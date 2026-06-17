# Rate Limiting — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update rate-limiting --quiz-score N/M` -->

## Q1 (warm-up)
Rate limiting kya hai, aur ek system mein iski zarurat kyun padti hai? Jab ek client apni limit cross kar de to typically kaun sa HTTP status code return hota hai?

**Ideal answer:**
- Definition: ek client/user/IP/API-key ko ek fixed time window mein limited number of requests allow karna.
- Purpose (koi 2-3): overload/resource exhaustion se protection, abuse/brute-force rokna, cost control, fairness across tenants (noisy neighbour), DDoS defense layer.
- Limit exceed pe **HTTP 429 (Too Many Requests)** return hota hai; bonus: `Retry-After` aur `X-RateLimit-Remaining` headers ka mention.

## Q2 (core)
Token Bucket algorithm kaise kaam karta hai? Bucket capacity `B = 100` aur refill rate `r = 10 tokens/sec` ke saath ye kaisa traffic shape allow karega?

**Ideal answer:**
- Bucket mein max `B` tokens hote hain; refill steadily `r` tokens/sec rate se hota hai.
- Har request ek token consume karta hai — token available ho to allow, na ho to reject.
- `B=100, r=10/sec` → sustained average ~10 req/sec, lekin agar bucket full ho to ek instant mein up to 100 ka **burst** absorb ho sakta hai.
- Key insight: Token Bucket controlled bursts allow karta hai (unused capacity "saved up" hoti hai). Tokens cap `B` pe rukte hain, infinite jama nahi hote.

## Q3 (tradeoff)
Fixed Window Counter aur Sliding Window Log ke beech accuracy vs memory ka tradeoff samjhao. Sliding Window Counter in dono ke beech kaise balance karta hai?

**Ideal answer:**
- **Fixed Window:** ek integer counter per key — memory-cheap, par boundary burst se inaccurate (limit ka ~2x leak ho sakta hai window boundary pe).
- **Sliding Window Log:** har request ka timestamp store karta hai (sorted set) — perfectly accurate, koi boundary burst nahi, lekin memory heavy (up to `limit` timestamps per key), millions of keys pe expensive.
- **Sliding Window Counter:** current + previous window counters ka weighted/proportional estimate (sirf 2 counters per key) — approximate but accuracy achhi, memory light; production sweet spot (e.g. Cloudflare-style).
- Core tradeoff articulate: accuracy ↑ to memory/cost ↑.

## Q4 (gotcha)
"Fixed Window Counter limit ko exactly enforce karta hai" — ye statement sahi hai ya galat, aur kyun? Ek concrete example do. Distributed setup mein counter increment karte waqt kaun si race condition aati hai aur uska fix kya hai?

**Ideal answer:**
- Statement **galat** hai — boundary burst problem ke kaaran.
- Concrete example: limit `100/min`, client 10:00:59 pe 100 + 10:01:00 pe 100 bhejta hai → ek hi second (~window boundary) mein 200 requests pass, effective 2x limit.
- Distributed race condition: kai nodes same key pe non-atomic `read → check → increment` karte hain → dono "99 < 100" dekh ke pass ho jaate hain (lost update / over-admission).
- Fix: **atomic operation** — Redis `INCR` ya ek Lua script jo check-and-set ko single round-trip mein atomically kare. Plain `GET` phir `SET` galat hai.

## Q5 (applied)
Tum ek public API gateway design kar rahe ho jo 100s of stateless nodes pe chal raha hai aur per-API-key global limit enforce karna hai. State kahan rakhoge aur kyun? Agar wo central store down ho jaaye to allow karoge ya reject — kis basis pe decide karoge?

**Ideal answer:**
- Local in-memory counters fail karte hain kyunki har node alag count rakhega → effective limit `N_nodes × limit` (over-permissive). Global limit ke liye **shared/centralized state** chahiye.
- Typically **Redis** — sub-ms latency, atomic `INCR`/Lua for race-free updates; limiter added latency ~1-2ms target.
- Optimization: per-node local cache + async sync to cut Redis round-trips (thodi accuracy trade-off).
- Failure mode decision: **fail-open** (Redis down → allow, availability-first) vs **fail-closed** (reject, protection-first). Public APIs aksar fail-open taaki limiter outage poora service na giraaye; security-sensitive endpoints (login) fail-closed.
- Bonus: granularity choice (per API key vs IP), `429` + `Retry-After`/`X-RateLimit-Remaining` headers.
