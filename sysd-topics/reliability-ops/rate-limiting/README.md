# Rate Limiting

**Track:** Building Blocks
**Category:** Reliability & Ops

## What It Is

Rate limiting ek technique hai jisme ek client (ya user/IP/API key) ko ek fixed time window mein sirf ek limited number of requests allow kiye jaate hain, taaki system ko overload, abuse, aur runaway cost se bachaya ja sake.

## Real-World Analogy

Socho ek popular nightclub ke gate pe ek bouncer khada hai jiska rule hai: "Har minute maximum 60 log andar." Matlab average ek banda per second. Ab agar ek hi second mein 200 log ekdum se gate pe aa jaayein, to bouncer sabko andar nahi ghusne dega — kuch ko wait karaayega ya wapas bhej dega (reject), bhale hi club ke andar abhi jagah ho.

Yahi rate limiting ka core idea hai: capacity available ho ya na ho, hum jaan-bujhke ek rate cap lagate hain taaki backend systems (DB, downstream services) ko ek predictable, controlled flow mile aur koi ek aggressive client poore club ka maza kharab na kare. Token bucket waale variant mein bouncer thoda flexible hota hai — agar pichhle kuch minute khaali gaye the, to wo thodi "saved up" capacity use karke ek chhota burst andar aane de sakta hai.

## How It Works

Rate limiting ka kaam: har incoming request pe ek fast decision lena — **allow** ya **reject (HTTP 429 Too Many Requests)**. Ye decision microseconds mein hona chahiye, warna limiter khud ek bottleneck ban jaata hai. Char common algorithms hain:

1. **Fixed Window Counter:** Time ko fixed windows mein baant do, jaise har 1 minute. Har key (e.g. `user:42`) ke liye ek counter rakho. Limit `100 req/min` hai to 10:00:00–10:00:59 ke beech counter 100 tak badhao, 101st request ko reject. Window khatam hone pe counter `0` reset. Bahut simple aur memory-light (ek integer per key), lekin **boundary burst problem** hai: agar client 10:00:59 pe 100 requests aur 10:01:00 pe 100 aur bhej de, to 1 second ke andar 200 requests pass ho gayin — limit ka double.

2. **Sliding Window Log:** Har request ka exact timestamp ek sorted log/set mein store karo (e.g. Redis sorted set). Har naye request pe, current time se `window` (jaise 60s) se purane timestamps hata do, phir count check karo. Bilkul accurate (koi boundary burst nahi), lekin memory heavy — `100 req/min` limit matlab per key up to 100 timestamps store; millions of users pe ye bahut RAM kha jaata hai.

3. **Sliding Window Counter:** Fixed window aur sliding log ke beech ka practical middle ground. Current aur previous window ke counters ko weighted average se combine karta hai. Example: limit 100/min, current window mein abhi tak 40s beete (40% beet gaya), previous window ka count 90 tha, current ka 20 hai → estimate = `90 * (1 - 0.4) + 20 = 74`. 74 < 100 to allow. Approximate hai par accuracy achhi aur memory bas do counters per key — isiliye production mein (Cloudflare-style) common.

4. **Token Bucket:** Ek bucket mein max `B` tokens (capacity), aur refill rate `r` tokens/sec. Har request ek token consume karta hai; token ho to allow, na ho to reject. Bucket steadily `r` rate se refill hota hai. Example: `B = 100`, `r = 10/sec` → average 10 req/sec sustain, lekin agar bucket full ho to ek instant mein 100 ka burst absorb ho sakta hai. **Bursts allow karta hai** controlled tarike se — yahi iski USP hai. (Leaky Bucket iska cousin hai jo output ko ekdum smooth constant rate pe nikaalta hai, no burst.)

**Distributed setup:** Single server pe in-memory counter chalega, par real systems mein 100s of API gateway nodes hote hain. Sabko ek shared, consistent view chahiye, isliye counters ek central fast store mein rakhe jaate hain — typically **Redis** (sub-millisecond latency, atomic `INCR`/Lua scripts for race-free check-and-update). Limiter ka added latency ~1-2ms target hota hai. Per-node local cache + periodic sync se Redis load kam karte hain (thodi accuracy trade karke).

## Tradeoffs & Variants

- **Accuracy vs memory/cost:** Sliding Window Log = perfectly accurate par memory heavy. Fixed Window = cheap par boundary bursts allow karta hai. Sliding Window Counter = approximate but both-worlds sweet spot. Interviewer aksar poochta hai "kaun sa choose karoge aur kyun" — answer scale aur accuracy requirement pe depend karta hai.

- **Bursts allow karne hain ya nahi:** Token Bucket controlled bursts allow karta hai (good for bursty-but-okay traffic jaise user batch actions). Leaky Bucket strictly smooth output deta hai (good jab downstream ekdum constant rate hi handle kar sake). Ye ek key design fork hai.

- **Local vs distributed (centralized) state:** Local in-memory counters fast (zero network hop) par har node apni limit alag track karta hai → effective global limit `N_nodes × limit` ho jaata hai (over-permissive). Centralized Redis accurate global limit deta hai par har request pe ek network round-trip aur Redis ek single point of failure/bottleneck ban sakta hai. Hybrid (local cache + async sync) bich ka raasta hai.

- **Fail-open vs fail-closed:** Agar Redis/limiter down ho jaaye, to requests allow karein (fail-open, availability-first) ya block karein (fail-closed, protection-first)? Zyaadatar public APIs fail-open jaate hain taaki limiter outage poora service down na kar de — par security-sensitive endpoints (login) fail-closed.

- **Granularity / key choice:** Limit kis dimension pe — per user ID, per IP, per API key, per endpoint, ya combination? IP-based easy hai par NAT/proxy ke peeche kai users share karte hain (collateral blocking) aur attacker IP rotate kar sakta hai. API-key based zyada precise.

## When To Use It

- **Public APIs:** Stripe, GitHub, Twitter/X jaise APIs har key pe limits lagate hain (e.g. GitHub `5000 req/hour`) — `429` response + `Retry-After` aur `X-RateLimit-Remaining` headers ke saath.
- **Brute-force / abuse protection:** Login aur OTP endpoints pe per-account/per-IP limits taaki credential stuffing aur password guessing rok sakein.
- **Cost & capacity control:** Expensive downstream (LLM inference, payment gateways, third-party paid APIs) ke aage limiter laga ke runaway cost aur quota exhaustion se bachna.
- **Fairness / multi-tenant:** Ek tenant ka traffic spike baaki tenants ko starve na kare — "noisy neighbour" problem. API gateways (Kong, Envoy, AWS API Gateway, NGINX) built-in rate limiting offer karte hain.
- **DDoS mitigation (layer):** Cloudflare/Akamai edge pe rate limiting use karte hain (often Sliding Window Counter) as one defense layer.

## Common Interview Gotchas

- **Fixed Window ki boundary burst:** Sabse classic gotcha. Limit `100/min` ke saath client 10:00:59 pe 100 + 10:01:00 pe 100 = ek hi second mein 200 requests nikaal sakta hai — limit ka effectively 2x. Agar koi candidate "Fixed Window se exact rate guarantee milti hai" bole to galat hai. Sliding window isi ko fix karta hai.

- **Distributed mein race condition:** Multiple nodes simultaneously same key pe `read counter → check → increment` karein bina atomicity ke, to do requests dono "99 < 100" dekh ke pass ho jaayengi (lost update). Isiliye Redis atomic `INCR` ya Lua script (single round-trip check-and-set) zaruri hai. "Bas `GET` phir `SET` kar denge" galat answer hai.

- **Token Bucket ≠ Leaky Bucket:** Log inhe interchangeably bol dete hain. Token Bucket **bursts allow** karta hai (tokens jama ho sakte hain), Leaky Bucket output ko **constant rate** pe smooth karta hai (no burst). Interviewer ye distinction specifically probe karta hai.

- **Rate limiting vs Throttling vs Load shedding:** Rate limiting = per-client quota enforce karna. Throttling = aksar same cheez ya slow-down. Load shedding = system overload pe requests drop karna regardless of client quota (server-health driven, client-quota driven nahi). Inhe mix karna common galti hai.

- **Clock skew & window boundaries:** Distributed nodes ke clocks slightly alag ho sakte hain; window calculations server time pe depend karein to inconsistency aati hai. Centralized store (Redis) ka time use karna ya logical windows isse handle karta hai.

- **`429` ke saath `Retry-After` dena:** Sirf reject kar dena adhura hai — well-behaved API client ko batana chahiye kab retry kare (`Retry-After` header) aur kitna budget bacha hai (`X-RateLimit-Remaining`), warna clients tight retry loop mein aur load badha denge.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/reliability-ops/conceptual_quiz_rate_limiting.md`](../../../sysd-quizzes/reliability-ops/conceptual_quiz_rate_limiting.md) — `sysd-buddy quiz scaffold rate-limiting` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update rate-limiting --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — token bucket refill, fixed vs sliding window, aur allow/reject decision flow ka interactive diagram.
