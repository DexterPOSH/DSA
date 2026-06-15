# Design Twitter / News Feed — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-twitter-feed --quiz-score N/M` -->

## Q1 (warm-up — requirements & scoping)
Tum Twitter ka home timeline design kar rahe ho. Functional aur non-functional requirements gather karne ke liye tum interviewer se kaunse clarifying questions poochoge, aur is system ki defining characteristic kya hai jo poore design ko drive karti hai?

**Ideal answer:**
- Clarifying questions: chronological vs ML-ranked feed? media support? expected DAU/scale? eventual consistency acceptable? likes/retweets in scope?
- Functional: post tweet, follow/unfollow, home timeline (followed users, newest-first), user timeline.
- Non-functional: high availability, low read latency (~200ms p99), eventual consistency OK, horizontal scalability.
- **Defining characteristic: read-heavy** (read:write ~100:1). Ye poore design ka driver hai — read path ko optimize/precompute karna padta hai, isliye fan-out-on-write aur caching aate hain.

## Q2 (core — capacity estimate)
Maan lo 200M DAU hain aur average 2 tweets/user/day. Write QPS aur read QPS estimate karo, aur explain karo ki ye numbers architecture ka kaunsa decision force karte hain.

**Ideal answer:**
- Writes/day = 200M × 2 = 400M. Avg write QPS = 400M / 86,400 ≈ **~4,600/sec**; peak (~2-3×) ≈ **~12,000/sec**.
- Read:write ~100:1 → read QPS ≈ 4,600 × 100 ≈ **~460,000/sec**; peak ≈ **~1M reads/sec**.
- Implication: 1M read QPS pe har read pe timeline compute karna (followed users ki tweets fetch + merge live) feasible nahi → **precompute the timeline (fan-out on write) + cache it in Redis**. Reads cheap, writes mein extra work — read-heavy ke liye correct tradeoff.
- Bonus: storage ~1 KB/tweet × 400M/day × 365 ≈ ~146 TB/year metadata; media → object store + CDN.

## Q3 (data-model / API choice)
Tweets aur social graph store karne ke liye SQL chunoge ya NoSQL? Justify karo. Aur home timeline read karne ke liye pagination kaise karoge — offset ya cursor — aur kyun?

**Ideal answer:**
- **NoSQL** (wide-column like Cassandra / key-value like DynamoDB): access patterns single-key lookups + append-heavy high-write-throughput hain, complex joins/multi-row ACID nahi chahiye, aur horizontal sharding (by user_id/tweet_id) chahiye. SQL joins is scale pe bottleneck.
- Tweet IDs: **Snowflake-style** (timestamp + machine + sequence) — globally unique + time-sortable, no single bottleneck.
- Follow graph: dono direction index chahiye — by follower_id (whom I follow) aur by followee_id (my followers, fan-out ke liye).
- **Cursor-based pagination** (opaque cursor = last tweet_id/timestamp), NOT offset. Offset pe feed continuously badalne se duplicates/skips aate hain; cursor stable + efficient hota hai (index seek vs scan).

## Q4 (key deep-dive tradeoff — fan-out on write vs read)
Fan-out-on-write (push) vs fan-out-on-read (pull) explain karo. Read-heavy Twitter ke liye default kaunsa hai, aur uska sabse bada problem kya hai aur tum use kaise solve karoge?

**Ideal answer:**
- **Push (fan-out on write):** tweet ko post hote hi sabhi followers ke precomputed timeline cache mein push. Reads super-fast (ready Redis list). Cost: write amplification (1 tweet × N followers). Read-heavy ke liye **default**.
- **Pull (fan-out on read):** tweet sirf author ke paas; read time pe followed users ki tweets query + merge. Cheap writes, expensive/slow reads.
- **Problem with pure push: celebrity fan-out** — ek celebrity (e.g. 50M followers) ka tweet 50M writes trigger karega (thundering herd), DB/cache choke + slow delivery.
- **Solution: hybrid** — normal users push; celebrities (followers > threshold) ke tweets push mat karo, read time pe **pull + merge** with follower ki pushed timeline. Plus inactive users ke liye lazy/pull compute.

## Q5 (applied — scaling bottleneck + mitigation)
System scale karte waqt do major bottlenecks naam batao (celebrity ke alawa) aur har ke liye concrete mitigation do.

**Ideal answer (koi do solid, with mitigation):**
- **Hot keys / hot partitions** (viral tweet ya celebrity profile ek partition pe hot) → dedicated hot-tweet cache, replication, request coalescing.
- **Redis memory pressure** (200M users × ~800 tweet_ids) → capped lists, inactive users evict/lazy-compute, sharded Redis cluster (consistent hashing).
- **Thundering herd on cache miss/expiry** → single-flight / request coalescing, staggered TTLs.
- **Write/fan-out spikes** → decouple write from fan-out via **Kafka** async consumers, back-pressure + retries, horizontally scale consumers.
- **Consistency vs latency tradeoff** noted: async push = 1-2s eventual delivery, accepted for availability + low read latency.
