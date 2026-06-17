# Circuit Breakers

**Track:** Building Blocks
**Category:** Reliability & Ops

## What It Is

Circuit breaker ek client-side resiliency pattern hai jo ek failing downstream dependency ke calls ko temporarily block kar deta hai (fail-fast) jab failures ek threshold cross kar jaate hain, taaki caller waste na ho aur dependency ko recover hone ka mauka mile.

## Real-World Analogy

Socho ghar ki electrical wiring mein lagi MCB (circuit breaker switch) ko. Normally current smoothly flow karta hai — switch "closed" hai, sab appliances chal rahe hain. Ab agar kahin short circuit ho jaaye ya overload aaye, to MCB turant "trip" ho jaata hai (open ho jaata hai) aur current ko cut kar deta hai. Wo intentionally circuit todta hai taaki wiring jale na aur ghar mein aag na lage.

Software ka circuit breaker bhi bilkul yahi karta hai. Tumhari service ek downstream API ko call kar rahi hai. Jab tak downstream healthy hai, switch "closed" hai aur calls jaate rehte hain. Par jaise hi downstream girne lagta hai (timeouts, errors bahut zyada), breaker "trip" karke open ho jaata hai — ab har naya call instantly fail hota hai, downstream ko call kiye bina. Thodi der baad breaker thoda sa "trial" current chhodta hai (half-open) — agar downstream theek ho gaya, switch wapas closed; agar abhi bhi kharaab hai, wapas open. MCB ki tarah ye dono ko bachata hai: caller ko hanging se aur downstream ko pile-on traffic se.

## How It Works

Circuit breaker ek finite state machine hai jiske 3 states hote hain: **Closed**, **Open**, aur **Half-Open**.

1. **Closed (normal operation):** Saare requests downstream tak normally jaate hain. Breaker har call ka outcome track karta hai — success ya failure (failure = error response, timeout, ya connection refused). Ek rolling window mein failures count/rate maintain hoti hai.

2. **Trip condition (Closed → Open):** Jab failures ek threshold cross karti hain, breaker trip karke **Open** ho jaata hai. Threshold do styles ka ho sakta hai:
   - **Count-based:** "last 20 calls mein se 10 fail" jaisa.
   - **Rate-based:** "rolling 10-second window mein agar error rate > 50%" — bashart minimum volume (jaise at least 20 requests) ho, taaki 1-out-of-2 jaisa noise breaker na trip kar de.

3. **Open (fail-fast):** Open state mein breaker downstream ko **bilkul call nahi karta**. Har incoming request immediately reject hoti hai (ya fallback serve hoti hai) — typically sub-millisecond, jabki ek hanging call 30s timeout tak latak sakti thi. Ye latency bachat hi asli point hai: 30s wait ke badle ~0.1ms fail. Breaker ek timer set karta hai, jaise **sleep window 30 seconds**, jiske dauraan wo Open rehta hai.

4. **Half-Open (cautious probe):** Sleep window khatam hone par breaker **Half-Open** mein jaata hai aur ek (ya kuch limited number, jaise 1-5) **trial requests** downstream ko bhejta hai:
   - Agar trial requests **succeed** karti hain → downstream recover ho gaya → breaker wapas **Closed**, full traffic resume.
   - Agar trial **fail** hoti hai → downstream abhi bhi sick → breaker wapas **Open**, aur ek aur sleep window (often exponential backoff ke saath) wait karta hai.

5. **Metrics & isolation:** Har downstream dependency ka apna alag breaker hota hai — Payment API ka breaker trip hone se Search API ke calls block nahi hone chahiye. Breaker state aur trip events ko metrics/alerts mein emit karna zaroori hai (e.g. "PaymentService breaker OPEN") taaki on-call ko pata chale.

**Concrete example:** Maano checkout service Payment API ko 500 QPS pe call karti hai, normal latency 40ms. Payment API down ho gaya — har call ab 30s timeout pe fail kar rahi hai, aur 500 QPS × 30s = thousands of threads block ho ke checkout service bhi hang. Breaker (50% error rate over 20+ requests) ek-do second mein trip karke Open ho jaata hai. Ab 500 QPS instantly ~0.1ms mein fail ya fallback ("Payment temporarily unavailable") serve hoti hai. Threads free, checkout service alive. 30s baad half-open probe — Payment recover hua to traffic resume.

## Tradeoffs & Variants

- **Threshold tuning (sensitivity vs stability):** Bahut aggressive threshold (jaise 2 failures pe trip) → breaker transient blips pe bhi trip karke unnecessarily traffic block karega (false positives). Bahut loose (jaise 95% error rate chahiye) → breaker tab tripega jab pehle hi system tabaah ho chuka. Plus **minimum request volume** chahiye warna low traffic pe 1 failure = 100% error rate dikh ke false trip ho jaayega.

- **Sleep window length:** Chhota window → faster recovery detection par downstream ko recover hone ka time kam, aur baar-baar probe se thrashing. Lamba window → downstream ko breathing room, par recover hone ke baad bhi traffic late resume hota hai. Common pattern: exponential backoff on repeated Open.

- **Fallback strategy:** Open hone par kya serve karein? Options: cached/stale data, default value, degraded response, ya simply fast error. "Fail-fast error" sabse simple hai; "cached fallback" best UX par staleness aur cache-availability pe depend.

- **Half-open concurrency:** Half-open mein kitni trial requests allow karein? Agar saari waiting traffic ek saath chhod di, to ek hi probe burst recovering downstream ko dobara gira sakta hai. Isliye half-open mein usually 1 ya kuch limited concurrent probes hi allow hote hain.

- **Circuit breaker vs retries vs bulkheads:** Ye complementary patterns hain. Retries transient failures handle karte hain; bulkheads ek dependency ke failure ko thread/connection pool isolate karke contain karte hain; circuit breaker repeated failures pe fail-fast karta hai. **Important:** retries + breaker ko saath tune karna padta hai — aggressive retries breaker ke failure count ko inflate karke usko jaldi trip karwa sakte hain (jo kabhi-kabhi accha bhi hai).

## When To Use It

- **Synchronous service-to-service calls** over network — REST/gRPC calls to a downstream microservice, especially jab caller ki request latency-sensitive hai.
- **Slow/failing dependency se cascading failure rokna:** Jab ek slow downstream caller ke threads/connections ko exhaust karke poore system ko gira sakta hai (cascading failure / "retry storm").
- **Real systems:** Netflix **Hystrix** (the pattern ko popular karne wala library), **Resilience4j** (Java ka modern successor), **Polly** (.NET), aur service meshes jaise **Envoy / Istio** mein built-in outlier detection + circuit breaking. AWS App Mesh aur most API gateways bhi support karte hain.
- **Mat use karo** jab call already async/queued ho (queue khud backpressure de raha hai), ya jab dependency local/in-process ho (network failure ka concept hi nahi).

## Common Interview Gotchas

- **"Circuit breaker downstream ko theek karta hai" — NO.** Breaker downstream ko repair nahi karta; wo sirf **caller ko protect** karta hai (fail-fast, thread/resource bachaana) aur downstream ko **load se relief** deta hai recover hone ke liye. Recovery downstream khud karta hai.

- **Breaker vs retry ko confuse karna:** Retry _same_ request ko dobara try karta hai (transient errors ke liye). Breaker _future_ requests ko block karta hai (sustained failure ke liye). Ek "wapas koshish karo" hai, doosra "abhi koshish mat karo." Dono milke chalte hain par alag jobs hain.

- **Half-open state ko bhul jaana:** Bahut log sirf Open/Closed bolte hain. Half-open ke bina breaker ko kabhi pata nahi chalega ki downstream recover hua ya nahi — wo ya to hamesha Open rahega ya manually reset karna padega. Half-open hi automatic recovery enable karta hai.

- **Per-dependency isolation miss karna:** Ek hi global breaker rakhne se ek dependency ka failure unrelated dependencies ke calls bhi block kar deta hai. Har downstream ka apna breaker hona chahiye.

- **Minimum volume / false trips:** Low-traffic services mein, agar threshold sirf error _rate_ pe ho bina minimum request count ke, to 1-2 failures bhi "100% error rate" dikha ke breaker trip kar denge. Hamesha minimum volume threshold rakho.

- **Timeout zaroori hai:** Breaker tabhi kaam karta hai jab failures detect ho — par bina per-call **timeout** ke, ek hanging call kabhi "failure" count hi nahi hoga, aur breaker trip nahi karega. Timeout + breaker saath chahiye.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/reliability-ops/conceptual_quiz_circuit_breakers.md`](../../../sysd-quizzes/reliability-ops/conceptual_quiz_circuit_breakers.md) — `sysd-buddy quiz scaffold circuit-breakers` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update circuit-breakers --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — Closed → Open → Half-Open state machine aur trip/recovery flow ka interactive diagram.
