# Design TinyURL — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-tinyurl --quiz-score N/M` -->

## Q1 (warm-up — requirements & scoping)
You are designing a URL shortener. Before writing any architecture, what functional and non-functional requirements would you lock down, and what clarifying questions would you ask the interviewer?

**Ideal answer:**
- **Functional:** `shorten(longUrl) -> shortUrl`; redirect on hit; optional custom alias; optional expiry/TTL.
- **Non-functional:** high availability (broken redirects = broken published links), low-latency redirects (p99 single-digit ms), read-heavy (~100:1 read:write), short + non-guessable keys, scalable to billions of rows.
- **Clarifying questions:** traffic scale (writes/day, reads/day)? max key length? custom aliases needed? do links expire? analytics required (this expands scope significantly)?
- Bonus: explicitly notes redirect is the hot path and reads dominate.

## Q2 (core — capacity estimate)
Assume 100 million new URLs per day and a 100:1 read:write ratio. Walk through the read/write QPS, the 5-year storage, and how many characters the short key needs.

**Ideal answer:**
- Writes/day = 1e8; reads/day = 100 × 1e8 = 1e10.
- ~1e5 seconds/day → **write QPS ≈ 1,000/sec**, **read QPS ≈ 100,000/sec** (peak ~2x).
- 5-year records = 1e8 × 365 × 5 ≈ **~180 billion (1.8e11)**.
- ~600 bytes/record → ~1.8e11 × 600 ≈ **~110 TB** → too big for one machine, needs sharding.
- Key length: Base62, `62^7 ≈ 3.5 trillion` comfortably covers 1.8e11; `62^6 ≈ 56B` is too tight → choose **length 7**.
- Bonus: states assumptions clearly; notes read QPS (not bandwidth) is the real challenge.

## Q3 (tradeoff — API / data-model choice)
Would you use a SQL or NoSQL store for the core mapping, and why? Separately, would your redirect return HTTP 301 or 302?

**Ideal answer:**
- **Store:** workload is a simple key-value lookup (no joins, no multi-row txns) at billions of rows / 110 TB → favors a **NoSQL KV / wide-column store** (DynamoDB/Cassandra) or a sharded relational DB; built-in partitioning, high write throughput, easy horizontal scale. ACID not needed; eventual consistency is fine for redirects.
- **301 vs 302:** 301 (permanent) lets browsers/proxies cache the redirect → lower server load but **loses per-click analytics and kill-switch**. 302 (temporary) sends every click to the server → enables analytics/control but **higher read load**. Choose 302 if analytics matter, 301 to minimize load.
- Bonus: notes mappings are immutable so caching/invalidation is trivial.

## Q4 (gotcha — key generation deep dive)
Compare hashing the long URL versus a counter-with-base62 scheme for generating short keys. What is a Key Generation Service (KGS) and why is it preferred?

**Ideal answer:**
- **Hashing (MD5/SHA, take first 6-7 chars):** risks **collisions** (different URLs → same prefix; same URL → same key), requiring check-and-retry on insert → extra reads.
- **Counter + Base62:** globally unique auto-incrementing counter, base62-encode the integer → **no collisions, no collision-check**. Needs a distributed counter (ZooKeeper range allocation or Snowflake-style IDs) to avoid a single-counter bottleneck/SPOF.
- **KGS:** a dedicated service that **pre-generates** base62 keys offline into used/unused tables and hands out ready keys on request. Benefits: removes key-gen from the latency-critical path, makes collisions structurally impossible. Must be **replicated** to avoid SPOF.
- Bonus: notes custom aliases break the counter scheme and need a unique-constraint insert.

## Q5 (applied — scaling bottleneck + mitigation)
At 100K+ read QPS, what is the primary bottleneck on the redirect path, and how do you mitigate it? Also address what happens to a single viral link.

**Ideal answer:**
- **Bottleneck:** the DB cannot serve 100K-200K read QPS directly. Primary mitigation is an **in-memory cache** (Redis/Memcached) holding hot `shortKey -> longUrl` mappings; the 80/20 access pattern gives a high hit ratio; LRU eviction; immutable mappings mean no stale-cache problem.
- **Cache failure risk:** if cache is cold/down, full load hits the DB → mitigate with cache replication, multiple cache nodes via consistent hashing, and DB read replicas.
- **Sharding:** 110 TB / 200K QPS needs hash-based (consistent hashing) partitioning on `shortKey` so node add/remove only remaps K/N keys; deterministic since the key is known at redirect time.
- **Viral / hot key:** one link can overwhelm a single cache/shard node → replicate that key across multiple cache nodes or push the redirect to a CDN edge cache.
- Bonus: mentions a single global counter as a write-path bottleneck (solved by KGS/distributed IDs).
