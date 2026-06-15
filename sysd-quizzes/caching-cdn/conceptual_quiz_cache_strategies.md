# Cache Strategies — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update cache-strategies --quiz-score N/M` -->

## Q1 (warm-up)
In a cache-aside (lazy loading) read pattern, what exactly does the application do on a cache miss?

**Ideal answer:**
- Application first checks the cache; on a miss it does NOT just fail — it reads from the backing store (DB).
- It then writes (populates) that value back into the cache, typically with a TTL (e.g. `SET key value EX 300`).
- Finally it returns the value to the caller. So the application itself orchestrates both cache and DB; the cache has no knowledge of the DB.
- Bonus: "lazy loading" because the cache is populated only on demand (on the first miss), not proactively.

## Q2 (core)
Explain the difference between write-through and write-back (write-behind) caching, including the latency and durability implications of each.

**Ideal answer:**
- Write-through: every write goes to both cache and DB synchronously; success is returned only after both complete. Cache stays consistent with the DB; write latency = cache write + DB write (slower writes); no data loss on cache crash.
- Write-back: write goes only to the cache and is acknowledged immediately (fast, ~1 ms); dirty entries are flushed to the DB asynchronously, often batched/coalesced.
- Tradeoff: write-back gives best write throughput/latency and absorbs write bursts, but un-flushed entries are lost if the cache crashes before the flush (durability/data-loss risk).
- Good answer names a fit: write-back for high-frequency counters/metrics; write-through for data needing read-after-write consistency.

## Q3 (tradeoff)
You set the TTL on cached entries. What are you actually trading off by choosing a short TTL versus a long TTL?

**Ideal answer:**
- Short TTL → fresher data (less staleness) but lower hit ratio, meaning more cache misses and therefore more load on the DB.
- Long TTL → higher hit ratio and less DB load, but data can be stale for longer (consistency window grows).
- TTL is the direct lever between consistency/freshness and efficiency/DB-offload.
- Strong answer mentions it depends on how tolerant the use case is to staleness, and that invalidation-on-write can complement TTL for correctness.

## Q4 (gotcha)
A single very popular key expires and thousands of concurrent requests miss at the same instant, all hammering the DB. What is this called and how do you mitigate it?

**Ideal answer:**
- This is a cache stampede (a.k.a. thundering herd / dogpile effect).
- Mitigations: request coalescing / single-flight (only one request loads from the DB while others wait and reuse the result); a short-lived lock around the recompute; probabilistic/early expiration (refresh slightly before TTL so it never all expires at once); and cache warming for known hot keys.
- Bonus: negative caching for missing keys, and staggering/jittering TTLs so many keys don't expire simultaneously.

## Q5 (applied)
You're designing the read path for a read-heavy user-profile service backed by a slow relational DB. Which caching strategy would you pick and why, and what's the one consistency issue you must call out?

**Ideal answer:**
- Pick cache-aside (lazy loading) with an in-memory cache (Redis/Memcached) in front of the DB — it's the standard choice for read-heavy workloads (e.g. Facebook's Memcached + MySQL).
- On read: check cache, on miss load from DB and populate with a TTL. On profile update (write): write to DB and invalidate/delete the cache key (delete rather than update, to avoid stale-overwrite races).
- Consistency issue to call out: cache-aside has a staleness window — between a DB write and the cache update/invalidation, reads can serve stale data; cache-aside is not strongly consistent. Mention TTL + invalidation to bound it.
- Bonus: handle cold-start/stampede (warming, single-flight) and negative caching for non-existent profiles.
