# Retries, Timeouts & Backoff

**Track:** Building Blocks
**Category:** Reliability & Ops

## What It Is

Retries, timeouts, aur backoff teen related reliability patterns hain jo transient failures ko gracefully handle karte hain: timeout ek slow call ko bound karta hai, retry usko dobara attempt karta hai, aur backoff (with jitter) retries ke beech ka wait badhata hai taaki ek struggling downstream service ko overwhelm na karein.

## Real-World Analogy

Socho aap ek dost ko call kar rahe ho aur line busy aa rahi hai. **Timeout** ye decide karta hai ki phone kitni der ring karega before aap maan lo "ye nahi uthayega" aur cut kar do — endlessly hold karke nahi baithte.

**Retry** matlab cut karke aap dobara try karte ho, kyunki ho sakta hai abhi network glitch tha.

Ab **backoff** ka asli kamaal: agar aap busy tone ke turant baad baar-baar redial maaroge, to aap aur baaki saare callers milke us bande ke phone ko aur jaam kar doge. Samajhdaar tareeka ye hai — pehli baar 1 second ruko, phir 2 second, phir 4 second (exponential backoff). Aur **jitter** matlab thoda random wait add karna, taaki gaon ke saare log exactly ek hi time pe redial na karein (warna sab ek saath dobara line jaam kar denge — yahi "thundering herd" hai). Backoff plus jitter ka combo ye ensure karta hai ki retries calm aur spread-out rahein, aur recovering service ko saans lene ka mauka mile.

## How It Works

1. **Timeout sabse pehle:** Har remote call (RPC, HTTP, DB query) pe ek deadline lagao. Bina timeout ke ek slow/hung dependency aapke caller ke threads/connections ko block kar deti hai aur failure cascade ho jaata hai. Typical numbers: ek fast internal RPC ka p99 maybe 20ms hai, to timeout ~100-200ms set karte hain (headroom ke saath), na ki default 30s. Rule of thumb: timeout = upstream ke p99 latency se thoda upar, na bahut tight (false failures) na bahut loose (slow leak).

2. **Retry on transient errors only:** Failure aane par decide karo retry karna hai ya nahi. Retry sirf transient/idempotent-safe errors pe — jaise timeout, connection reset, HTTP 503 (Service Unavailable), 429 (Too Many Requests). **Non-retryable** errors pe NEVER retry: HTTP 400 (bad request), 401/403 (auth), 404 — ye dobara try karne se bhi waise hi fail honge, bas load badhega.

3. **Backoff between attempts:** Har retry ke beech wait karo, aur wait ko progressively badhao. Common formula exponential backoff: `wait = base * 2^attempt`. Example with base = 100ms → attempt 1 ke baad 100ms, fir 200ms, 400ms, 800ms wait. Isse retries spread ho jaate hain aur downstream ko recover hone ka time milta hai.

4. **Jitter add karo:** Pure exponential backoff mein bhi, agar 1000 clients ek saath fail hue, to sab exactly 100ms, fir 200ms pe synchronized retry karenge — yeh retry spikes (thundering herd) banata hai. Jitter randomness add karta hai. Sabse common "full jitter": `wait = random(0, base * 2^attempt)`. Isse retries time pe smoothly spread ho jaate hain instead of sharp bursts.

5. **Cap the retries:** Ek max attempt limit rakho (jaise 3 attempts total) aur ek overall deadline. Infinite retry kabhi nahi — warna jab downstream sach mein down hai, aap usko aur DDoS kar doge apne hi traffic se. 3 retries with full jitter usually enough hota hai transient blips ke liye.

6. **Combine with circuit breaker:** Jab failures sustained hon (transient nahi), retries cheez bigaadte hain. Circuit breaker downstream ke failure rate ko track karta hai; threshold cross hote hi circuit "open" ho jaata hai aur calls turant fail-fast hoti hain (retry kiye bina), giving downstream room to recover. Ye retry storms ko rokta hai.

## Tradeoffs & Variants

- **Retries availability badhate hain par load bhi:** Har retry effectively extra request hai. Agar har client 3 retries karta hai, to ek partial outage mein aapka downstream traffic 3x-4x spike kar sakta hai — exactly jab wo already struggling hai. Isiliye retries ko backoff + jitter + cap + circuit breaker ke saath hi deploy karo.

- **Backoff variants:** (a) Fixed backoff — har baar same wait, simple par sync issues. (b) Exponential backoff — wait doubles, standard choice. (c) Exponential + full jitter (`random(0, cap)`) — AWS-recommended, best load smoothing. (d) Decorrelated jitter — `sleep = min(cap, random(base, prev*3))`, even smoother. Interview mein "exponential + jitter" default answer hai.

- **Retry budget vs per-call retries:** Naive approach: har call independently retry karti hai (har request ka apna budget). Better at scale: ek **retry budget** (jaise total retries ≤ 10% of requests, jaisa gRPC/Envoy karte hain) — taaki overall retry amplification bounded rahe even agar many calls simultaneously fail karein.

- **Timeout budget across a chain:** Agar A → B → C call karta hai, to har hop apna full timeout nahi le sakta. Total deadline ko hops mein divide karo (deadline propagation). Warna A ka client already give up kar chuka hoga jab tak C respond kare — wasted work.

- **Idempotency requirement:** Retries sirf safe hain agar operation idempotent ho. GET retry karna fine. Par "charge credit card" ko blindly retry karna double-charge kar sakta hai. Solution: idempotency keys, taaki server duplicate request detect kar sake.

## When To Use It

- **Har inter-service RPC/HTTP call:** Basically saare network calls pe timeout mandatory hai; retry+backoff transient failures ke liye. gRPC, Envoy/Istio service mesh, aur Finagle (Twitter) sab built-in retry+backoff+budget dete hain.

- **Cloud SDKs:** AWS SDK, Google Cloud client libraries — sabme exponential backoff with jitter default hai for throttling (429/503) responses. Ye pattern AWS Architecture Blog ("Exponential Backoff And Jitter") se popular hua.

- **Message consumers / job queues:** Kafka consumers, SQS, background workers — failed message ko retry karte hain with backoff, aur N attempts ke baad dead-letter queue (DLQ) mein bhejte hain.

- **Database / cache clients:** Connection retries, transaction retries on deadlock/serialization conflicts (jaise Postgres `40001`) — bounded retries with backoff.

- **NOT for user-facing sync paths jahan latency budget tight ho:** Agar user 200ms response chahiye, to aap 3 retries with 800ms backoff afford nahi kar sakte — fail fast karo ya async kar do.

## Common Interview Gotchas

- **"Retries hamesha reliability badhate hain" — galat:** Without backoff/jitter/cap, retries ek minor blip ko full outage mein convert kar dete hain via retry storms / thundering herd. Classic cascading failure: downstream slow hua → clients timeout+retry → load 3x → downstream aur slow → aur retries → collapse. Yeh "retry amplification" interviewer ka favourite trap hai.

- **Bina jitter ke synchronized retries:** Pure exponential backoff bhi insufficient hai agar saare clients ek hi instant pe fail hue — wo lock-step mein retry karenge (spikes at 100ms, 200ms, ...). Jitter is the fix. "Exponential backoff" bolna adhoora hai; "exponential backoff **with jitter**" bolo.

- **Non-idempotent operations ko retry karna:** Timeout aaya iska matlab nahi ki request fail hui — ho sakta hai server ne process kar di par response kho gaya. Blind retry → duplicate side-effect (double charge, double order). Idempotency key zaroori hai.

- **Retrying non-retryable errors:** 400/401/403/404 ko retry karna pure waste — ye deterministically fail honge. Sirf 5xx/429/timeouts/connection errors retry karo.

- **Timeout choose karna without looking at p99:** Bahut tight timeout → healthy calls falsely fail. Bahut loose → resource leak jab downstream hang ho. Timeout ko actual p99 latency + buffer pe base karo, guesswork pe nahi.

- **Nested retries = multiplicative amplification:** Agar layer A 3x retry kare aur har attempt mein layer B bhi 3x retry kare, to effective load 9x ho jaata hai. Retries ko ek layer pe centralize karo (ya retry budget use karo), har layer pe nahi.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/reliability-ops/conceptual_quiz_retries_timeouts_backoff.md`](../../../sysd-quizzes/reliability-ops/conceptual_quiz_retries_timeouts_backoff.md) — `sysd-buddy quiz scaffold retries-timeouts-backoff` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update retries-timeouts-backoff --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — timeout deadline, exponential backoff curve, aur jitter ke saath retry spread ka interactive diagram.
