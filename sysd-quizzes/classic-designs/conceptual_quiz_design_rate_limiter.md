# Design a Rate Limiter — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-rate-limiter --quiz-score N/M` -->

## Q1 (warm-up — requirements/scoping)

A "design a rate limiter" prompt mein interview shuru hone par tum kaun se clarifying questions poochoge, aur kaun se non-functional requirements isme sabse zyada important hote hain?

**Ideal answer:** Clarifying questions: (1) client-side vs server-side limiter (server-side, kyunki client untrusted) (2) limit kis dimension par — user ID / IP / API key / endpoint, ya rule-based combination (3) single DC vs distributed/multi-DC (distributed = asli challenge) (4) limit exceed par hard reject (`429`) vs throttle/queue. Key non-functional requirements: **low latency** (limiter har request ke path mein hai, sub-ms decision chahiye, khud bottleneck na bane), **high availability** (limiter down ho to main service na ruke → fail-open vs fail-closed tradeoff), aur **accuracy vs scalability** tradeoff (distributed mein perfect accuracy + low latency dono mushkil, thodi slack tolerate karni padti hai).

## Q2 (core — capacity estimate)

100M DAU aur average 50 requests/user/day maan ke, average aur peak QPS estimate karo. Counter store ki memory roughly kitni chahiye, aur asli scaling pressure storage par hai ya kahin aur?

**Ideal answer:** Total daily = `100M * 50 = 5B requests/day`. Average QPS = `5B / 86,400 ≈ 58K QPS`. Peak (~3x) = `~175K QPS`. Memory: ~10M active keys * ~50 bytes/counter = `~500 MB` — ek Redis instance/chhote cluster mein fit. Key insight: counters **ephemeral** hain (TTL = window size), isliye storage chhota rehta hai; asli pressure **QPS aur per-request latency** par hai, isliye in-memory store (Redis) + edge distribution chahiye, na ki bada durable store.

## Q3 (tradeoff — data-model / API choice)

Counters ke liye Redis (NoSQL in-memory) aur rules ke liye SQL kyun? Dono ke alag store choices ko justify karo.

**Ideal answer:** **Counters → Redis**: ultra-low-latency atomic increments + native TTL, millions writes/sec par; durability matter nahi karti kyunki counter window ke baad waise bhi expire ho jaata hai (`INCR`, `EXPIRE`, Lua atomicity). SQL yahan write-throughput aur latency par fail karega. **Rules → SQL**: low-volume, strongly-consistent, relational/queryable (admin dashboards, audits); rules rarely change hote hain aur har box par cache ho jaate hain, isliye SQL ka latency hot path mein nahi aata. Correct answer dono ke access pattern (high-throughput ephemeral vs low-volume durable) ko store choice se connect karta hai.

## Q4 (gotcha — key deep-dive tradeoff)

Fixed window counter ka "boundary burst" problem kya hai, aur token bucket vs sliding window counter mein kya tradeoff hai? Tum default kya choose karoge?

**Ideal answer:** **Boundary burst:** fixed window mein "100/min" limit ke saath, window ke last second mein 100 + agle window ke first second mein 100 → 1 second mein effectively 200 requests pass ho jaate hain, limit cross karte hue. **Sliding window log:** har timestamp store karke accurate, par per-key memory/compute high. **Sliding window counter:** current+previous window ka weighted average — accuracy aur cost ka sweet spot, burst smooth ho jaata hai. **Token bucket:** tokens steady rate par refill, bucket capacity tak bursts allow karta hai par steady-state rate cap karta hai; sirf 2 values (token count + last refill ts) store karne padte hain, memory-efficient. Default: **token bucket** — burst-friendly, memory-efficient, Redis Lua mein atomic implement ho jaata hai. (Bonus: race condition se bachne ke liye check-and-decrement atomic Lua script mein hona chahiye.)

## Q5 (applied — scaling bottleneck + mitigation)

Distributed setup mein ek single Redis "hot key" bottleneck kab banta hai, aur isko kaise mitigate karoge? Saath mein, Redis down ho jaaye to limiter ka behaviour kya hona chahiye?

**Ideal answer:** **Hot key:** ek bahut popular key (viral endpoint / single high-traffic user) ek hi Redis shard ko hammer karti hai → hot shard, kyunki ek key hamesha ek hi shard par hash hoti hai. Mitigations: (1) key ko multiple sub-counters mein split karo (`key:bucket_0..N`), har request random bucket increment kare, decision ke liye sum lo (2) per-box **local + periodic sync (sloppy counters)** — low latency, thodi over-limit slack accept karke central store load kam. **Redis down:** zyadatar systems **fail-open** karte hain (allow requests) taaki limiter ki unavailability se main service na ruke — availability > strict correctness; lekin security-critical limits (login/fraud) ke liye **fail-closed** valid choice hai. Acha answer tradeoff (latency vs accuracy, availability vs correctness) explicitly name karta hai.
