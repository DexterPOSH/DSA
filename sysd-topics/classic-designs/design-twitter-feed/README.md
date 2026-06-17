# Design Twitter / News Feed

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Ek social platform design karna hai jahan users tweets post karte hain aur dusron ko follow karke unka home timeline (news feed) dekhte hain — yaani followed users ki recent tweets ka reverse-chronological (ya ranked) merged stream.

## Requirements & Scope

Pehle clarifying questions poochho, taaki scope nail ho jaaye:
- Read-heavy ya write-heavy? (Twitter strongly **read-heavy** hai — log padhte zyada hain, likhte kam.)
- Timeline strictly chronological chahiye ya ML-ranked? (Hum core ke liye chronological lenge, ranking ko extension maanenge.)
- Media (images/video) support karna hai? (Haan, but blob storage + CDN se handle karenge, metadata DB mein.)
- Eventual consistency acceptable hai timeline ke liye? (Haan — feed mein tweet 1-2 sec late aana fine hai.)

**Functional requirements:**
- User tweet post kar sake (text + optional media, ~280 chars).
- User dusre users ko follow/unfollow kar sake.
- User apna **home timeline** dekh sake (followed logon ki tweets, newest first).
- User apna **user timeline** dekh sake (sirf apni tweets).
- Likes / retweets (basic) — optional extension.

**Non-functional requirements:**
- **High availability** — feed read kabhi down nahi hona chahiye (availability > consistency, AP-leaning).
- **Low latency** — home timeline load ~200ms ke andar (p99).
- **Eventual consistency** — naya tweet followers ke feed mein thodi der mein dikhe, ye acceptable hai.
- **Scalability** — hundreds of millions of users, billions of tweets.
- **Read-heavy optimization** — read:write ratio kareeb 100:1 maan ke design karo.

## Capacity Estimate

Maan lo numbers (interviewer ke saath confirm karke):
- **DAU = 200M** (daily active users).
- Har user average **2 tweets/day** post karta hai.

**Write QPS (tweets):**
- Tweets/day = 200M × 2 = **400M tweets/day**.
- Seconds/day ≈ 86,400 ≈ ~10^5.
- Avg write QPS = 400M / 86,400 ≈ **~4,600 writes/sec**.
- Peak ≈ 2-3× avg ≈ **~12,000 writes/sec**.

**Read QPS (timeline views):**
- Read:write ratio ~100:1 maan ke → avg read QPS ≈ 4,600 × 100 ≈ **~460,000 reads/sec**.
- Peak reads ≈ **~1M reads/sec**. (Yahi reason hai ki read path ko precompute/cache karna padta hai.)

**Storage (tweets/year):**
- Ek tweet ≈ 280 chars text (~300 bytes) + metadata (tweet_id, user_id, timestamp, counters) ≈ **~1 KB** (media ko alag blob store mein rakhenge, ye sirf metadata).
- Tweets/year = 400M/day × 365 ≈ **~1.46 × 10^11 tweets/year** (~146 billion).
- Storage/year = 146B × 1 KB ≈ **~146 TB/year** sirf tweet metadata. 5 saal → ~0.7 PB. Replication (×3) ke saath ~2 PB.
- Media: agar 10% tweets mein ~200 KB ka image hai → 40M/day × 200 KB ≈ **~8 TB/day** blob storage → CDN + object store (S3-style) chahiye.

**Bandwidth (read):**
- Peak read 1M req/sec, har feed response ~ list of tweet IDs + hydrated content. Agar ek feed page ~10 KB return kare → 1M × 10 KB ≈ **~10 GB/sec egress** at peak → CDN + caching mandatory.

In numbers ka punchline: read path massive hai (1M QPS), isliye home timeline ko har read pe compute karna feasible nahi — usko **precompute (fan-out)** karna padega.

## API Design

REST-style (internally gRPC ho sakta hai). Auth via token; `userId` token se nikalta hai.

```
POST   /v1/tweets
       body: { text, mediaIds[] }
       → { tweetId, createdAt }

GET    /v1/timeline/home?cursor=<opaque>&limit=20
       → { tweets[], nextCursor }      # followed users ka merged feed

GET    /v1/timeline/user/{userId}?cursor=<opaque>&limit=20
       → { tweets[], nextCursor }      # ek user ki apni tweets

POST   /v1/follows        body: { followeeId }   → 200
DELETE /v1/follows/{followeeId}                  → 200

POST   /v1/tweets/{tweetId}/like                 → 200
```

Key design points:
- **Cursor-based pagination** (opaque cursor = last seen tweet_id/timestamp), NOT offset-based — kyunki feed continuously badalta hai aur offset pe duplicates/skips aate hain. Cursor stable hota hai.
- `limit` capped (e.g. max 50) taaki ek call se zyada load na ho.

## High-Level Architecture

Components aur request flow:

- **Load Balancer + API Gateway** — incoming requests, auth, rate-limiting.
- **Tweet Write Service** — POST /tweets handle karta hai: tweet ko DB mein persist karta hai, phir ek event publish karta hai.
- **Fan-out Service (async, queue-driven)** — naye tweet ka event consume karke writer ke followers ke **home timeline cache** mein tweet_id push karta hai.
- **Timeline Read Service** — GET /timeline/home: pehle precomputed timeline cache (Redis) se tweet_id list nikalta hai, phir tweet content **hydrate** karta hai (Tweet Cache/DB se).
- **Message Queue (Kafka)** — write path aur fan-out ke beech decoupling; fan-out async chalta hai taaki write latency low rahe.
- **Data stores:** Tweet store (NoSQL), Graph/Follow store, Timeline cache (Redis), User/profile store, Object store + CDN for media.

**Write flow:** Client → LB → Tweet Write Service → persist tweet in Tweet store → publish `TweetCreated` to Kafka → Fan-out Service consumers → har follower ki Redis timeline list mein `LPUSH tweet_id` (capped to ~800 entries).

**Read flow:** Client → LB → Timeline Read Service → Redis se follower ka timeline list (tweet_ids) → batch hydrate tweet content from Tweet Cache (fallback Tweet store) → merge with celebrity tweets (pull) → return page.

## Data Model

Ye system **NoSQL-leaning** hai (wide-column / key-value), kyunki access pattern simple key lookups aur append-heavy writes hain, strong cross-row transactions ki zaroorat nahi, aur horizontal scale chahiye. SQL relational joins is scale pe (1M read QPS, 146B tweets) bottleneck banenge.

**Tweets** (wide-column, e.g. Cassandra; partition by `tweet_id`):
| field | notes |
|---|---|
| tweet_id (PK) | Snowflake-style 64-bit ID — time-sortable + globally unique |
| user_id | author |
| text | up to 280 chars |
| media_ids | pointer to object store |
| created_at | timestamp (Snowflake mein already embedded) |
| like_count, retweet_count | denormalized counters |

**Follows / Social graph** (partition by `follower_id`):
| field | notes |
|---|---|
| follower_id (PK) | who follows |
| followee_id | who is followed |
| created_at | |
- Reverse index bhi (`partition by followee_id`) chahiye — fan-out ke liye "is user ke followers kaun hain?" fast nikalna padta hai.

**Home Timeline Cache** (Redis): `timeline:{user_id}` → list of tweet_ids (capped LIST, ~800 latest). Ye precomputed feed hai.

**Users/Profiles** (key-value): `user_id` → name, handle, follower_count, etc.

**Media:** object store (S3-style) + CDN; DB sirf media_id/URL rakhta hai.

**SQL vs NoSQL — why NoSQL:** access patterns single-key lookups + high write throughput + horizontal sharding by user_id/tweet_id maangte hain. No complex joins/ACID multi-row txns. NoSQL (Cassandra/DynamoDB-style) tunable consistency aur linear scale-out deta hai. Counters (likes) ke liye eventual-consistent counter columns ya Redis sufficient hain.

## Deep Dives

### 1. Fan-out on Write (push) vs Fan-out on Read (pull) — the core decision

- **Fan-out on write (push model):** Jab user tweet kare, tweet ko uske **saare followers** ke precomputed home-timeline cache mein turant push kar do. Read super-fast ho jaata hai (Redis se ready list mil jaati hai). Cost: write amplification — ek tweet × N followers = N writes. Read-heavy system ke liye yahi default choice hai (reads cheap karo, writes mein extra kaam OK).
- **Fan-out on read (pull model):** Tweet sirf author ke store mein rakho. Read pe, followed sab users ki latest tweets query karke **merge** karo. Write sasta, lekin read slow + har read pe heavy compute. High-fanout (celebrity) ke liye accha.
- **Hybrid (real answer):** Normal users → push. **Celebrities** (millions of followers, e.g. >10K-1M threshold) → push mat karo (warna ek tweet pe crore writes = "thundering herd"). Celebrity tweets ko read time pe **pull** karke follower ke pushed timeline ke saath merge karo. Ye Twitter ka actual approach hai. Yahi hybrid bottleneck #1 (celebrity fan-out) solve karta hai.

### 2. Caching the timeline (Redis)

- Home timeline ek **capped Redis list** (`timeline:{user_id}`) hota hai jisme sirf ~800 recent tweet_ids hote hain (puri history nahi). 1M read QPS isi cache se serve hota hai, DB ko bachata hai.
- Sirf tweet_ids store karo, full content nahi → memory bachti hai + content ek baar update ho to har copy update nahi karni padti. Content ko alag **Tweet Cache** se batch-hydrate karo.
- **Active vs inactive users:** Jo users weeks se login nahi kiye, unke liye timeline precompute karna waste hai. Inactive users ka feed lazily (pull) compute karo, active users ke liye hi push rakho.

### 3. Async fan-out via message queue (Kafka)

- Write request ko fan-out se **decouple** karo: tweet persist hote hi response return kar do, fan-out background mein async consumers (Kafka) karein. Isse write latency low rehti hai aur ek slow fan-out write path ko block nahi karta.
- Queue back-pressure aur retries deta hai — agar fan-out workers lag, tweets queue mein buffer ho jaate hain, lost nahi hote. Horizontal consumer scaling se peak (12K writes/sec → millions of fan-out ops/sec) handle hota hai.

## Bottlenecks & Tradeoffs

- **Celebrity fan-out (write amplification):** Ek celebrity (50M followers) ka tweet pure push model mein 50M Redis writes trigger karega — DB/cache ko ghutne pe la dega aur tweet sabko late dikhega. **Mitigation:** hybrid — celebrity tweets pull at read time + merge. Threshold-based switching.
- **Hot keys / hot partitions:** Bahut viral tweet ya celebrity profile ka data ek partition pe hot ho jaata hai. **Mitigation:** dedicated cache for hot tweets, replication, request coalescing.
- **Consistency vs latency:** Push async hai → naya tweet kisi follower ko 1-2 sec late dikh sakta hai (eventual consistency). Ye intentional tradeoff hai — availability + low read latency ke liye strong consistency chhodi.
- **Redis memory pressure:** 200M active users × ~800 tweet_ids × 8 bytes ≈ bahut RAM. **Mitigation:** capped lists, inactive users ko evict/lazy-compute, sharded Redis cluster (consistent hashing).
- **Thundering herd on cache miss:** Agar ek popular timeline entry expire ho jaaye to ek saath laakhon reads DB pe gir sakte hain. **Mitigation:** request coalescing / single-flight, staggered TTLs.
- **ID generation:** Globally unique + time-sortable tweet IDs chahiye bina single bottleneck ke → **Snowflake** (timestamp + machine_id + sequence) distributed ID generation.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_twitter_feed.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_twitter_feed.md) — grade hone ke baad score record karo with `sysd-buddy progress update design-twitter-feed --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — write fan-out flow, hybrid push/pull, aur timeline cache ka interactive diagram.
