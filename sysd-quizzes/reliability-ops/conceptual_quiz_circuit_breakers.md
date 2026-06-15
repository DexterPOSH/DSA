# Circuit Breakers — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update circuit-breakers --quiz-score N/M` -->

## Q1 (warm-up)
Circuit breaker pattern kya hai, aur ek line mein iska core purpose kya hai?

**Ideal answer:**
- Ek client-side resiliency pattern hai jo failing downstream dependency ke calls ko temporarily block (fail-fast) karta hai jab failures threshold cross kar jaayein.
- Core purpose dual hai: (1) caller ko protect karna — hanging calls par threads/resources waste hone se bachana; (2) struggling downstream ko load se relief dekar recover hone ka mauka dena.
- Analogy (electrical MCB jo overload pe trip ho jaata hai) bonus.

## Q2 (core)
Circuit breaker ke teen states kaun se hain, aur ek state se doosri mein transition kab hota hai?

**Ideal answer:**
- **Closed:** normal operation, saare calls downstream tak jaate hain, breaker failures/successes track karta hai.
- **Closed → Open:** jab failure threshold cross ho (count-based jaise 10/20 calls fail, ya rate-based jaise >50% error rate over a minimum volume window) breaker trip karke Open ho jaata hai.
- **Open:** fail-fast — koi call downstream tak nahi jaati, har request immediately reject/fallback; ek sleep window (e.g. 30s) ke liye Open rehta hai.
- **Open → Half-Open:** sleep window expire hone par breaker Half-Open mein jaata hai aur 1 ya kuch limited trial/probe requests bhejta hai.
- **Half-Open → Closed:** probe succeed → wapas Closed (full traffic). **Half-Open → Open:** probe fail → wapas Open (often exponential backoff).

## Q3 (tradeoff)
Failure threshold aur sleep window tune karne mein kya tradeoffs hain? Bahut aggressive ya bahut loose values ka kya nuksan hai?

**Ideal answer:**
- **Threshold too aggressive (e.g. 2 failures pe trip):** transient blips par bhi breaker trip → false positives, unnecessary traffic block / degraded availability.
- **Threshold too loose (e.g. 95% error chahiye):** breaker tab tripega jab system already tabaah → protection ka point hi chala jaata hai.
- **Minimum request volume** zaroori — bina iske low traffic pe 1-2 failures = "100% error rate" dikha ke false trip.
- **Sleep window chhota:** fast recovery detection par downstream ko recover hone ka kam time + probe thrashing risk. **Lamba:** downstream ko breathing room par recovery ke baad bhi traffic late resume. Exponential backoff common mitigation.

## Q4 (gotcha)
"Circuit breaker downstream dependency ko theek kar deta hai" — ye statement sahi hai ya galat? Aur circuit breaker retry se kaise alag hai?

**Ideal answer:**
- Statement **galat** hai. Breaker downstream ko repair nahi karta; wo caller ko protect karta hai (fail-fast) aur downstream se load hata ke usko khud recover hone deta hai. Actual recovery downstream khud karta hai.
- **Retry vs breaker:** retry _same_ request ko dobara try karta hai (transient errors handle karne ke liye, "wapas koshish karo"). Breaker _future_ requests ko block karta hai (sustained failure ke liye, "abhi koshish mat karo"). Complementary par alag jobs.
- Bonus: aggressive retries breaker ka failure count inflate kar sakte hain; dono ko saath tune karna padta hai. Per-call timeout bhi zaroori warna hanging call kabhi failure count hi nahi hogi.

## Q5 (applied)
Ek checkout service synchronously Payment API ko 500 QPS pe call karti hai. Payment API down ho jaata hai. Circuit breaker kaise cascading failure rokta hai, aur tum kya kya configure karoge?

**Ideal answer:**
- **Problem without breaker:** har call 30s timeout pe fail; 500 QPS × 30s → hzaaron threads/connections block → checkout service khud hang (cascading failure / thread exhaustion).
- **With breaker:** ~50% error rate over a minimum volume detect hone par breaker trip → Open. Ab 500 QPS instantly (~sub-ms) fail-fast ya fallback serve. Threads free, checkout alive.
- **Recovery:** sleep window (e.g. 30s) baad Half-Open → 1-few probe requests → Payment recover hua to Closed, traffic resume; nahi to wapas Open with backoff.
- **Config knobs:** per-call timeout (zaroori), per-dependency breaker isolation (Payment ka breaker Search ko block na kare), error-rate threshold + minimum volume, sleep window, fallback (cached/default/degraded response), half-open probe concurrency.
- Real tooling mention bonus: Hystrix / Resilience4j / Polly / Envoy outlier detection.
