# Design TinyURL

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

TinyURL ek URL shortening service hai jo ek lambe URL ko ek chhote unique alias (jaise `tinyurl.com/abc123`) mein convert karti hai, aur us short alias pe hit aane pe user ko original long URL pe redirect kar deti hai.

## Requirements & Scope

Pehle scope clarify karna important hai, warna aap galat cheez design kar doge. Functional aur non-functional dono lock karo.

**Functional requirements:**
- Ek long URL do, service ek short URL return kare (`shorten(longUrl) -> shortUrl`).
- Short URL pe GET aane pe original long URL pe HTTP redirect ho jaaye.
- Optionally user ek custom alias (`tinyurl.com/my-brand`) choose kar sake.
- Optionally links ka ek expiry / TTL ho (kuch saal baad ya custom date pe).

**Non-functional requirements:**
- **High availability** — service barely down honi chahiye, kyunki agar redirect fail hua to saari published links toot jaayengi.
- **Low latency** — redirect ek hot path hai, p99 single-digit milliseconds hona chahiye.
- **Read-heavy** — read:write ratio bohot skewed hai (~100:1), kyunki ek banaya gaya link kai baar click hota hai.
- **Short, unpredictable keys** — alias chhota ho aur easily guessable / enumerable na ho (security).
- **Scalability** — kai saal ke links store hone chahiye (billions of rows).

**Clarifying questions interviewer se poochne layak:**
- Traffic scale kya hai — kitne new URLs per day aur kitne redirects per day?
- Short link kitne characters tak ka ho — length constraint?
- Custom alias support karna hai ya sirf auto-generated?
- Links expire hote hain ya forever live rehte hain?
- Analytics chahiye (click counts, geo, referrer)? Ye scope ko kaafi badha deta hai.

## Capacity Estimate

Back-of-the-envelope numbers interviewer ko dikhane ke liye — assumptions clearly state karo.

**Assumptions:**
- New URLs (writes): **100 million per day** (1e8).
- Read:write ratio **100:1**, to redirects (reads): **10 billion per day** (1e10).

**QPS (queries per second):** 1 din mein roughly `86,400` seconds (~1e5).
- Write QPS = `1e8 / 1e5` = **~1,000 writes/sec**.
- Read QPS = `1e10 / 1e5` = **~100,000 reads/sec**.
- Peak ke liye ~2x maan lo: write peak ~2K/sec, read peak ~200K/sec.

**Storage (5 years):**
- 5 saal mein total URLs = `100M/day * 365 * 5` ≈ **182 billion** (~1.8e11) records.
- Per record size estimate: short key (7 bytes) + long URL (~500 bytes) + metadata (creation time, expiry, owner ~100 bytes) ≈ **~600 bytes/record**.
- Total storage = `1.8e11 * 600 bytes` ≈ **~110 TB** over 5 years. Single machine pe fit nahi hoga — sharding chahiye.

**Bandwidth:**
- Write ingress = `1,000/sec * 600 bytes` ≈ **600 KB/sec** — trivial.
- Read egress = `100,000/sec * 600 bytes` ≈ **60 MB/sec** — manageable, par read QPS hi asli challenge hai.

**Key space:** Base62 (`a-z`, `A-Z`, `0-9` = 62 chars). `62^7` ≈ **3.5 trillion** combinations — 7 characters 1.8e11 URLs ke liye comfortably enough hai. 6 chars `62^6` ≈ 56 billion deta hai jo 5-year estimate ke liye thoda kam pad sakta hai, isliye **length 7** safe choice hai.

## API Design

REST endpoints simple rakhe ja sakte hain:

```
POST /api/v1/shorten
  Body: { "longUrl": "https://...", "customAlias": "optional", "expiryDate": "optional" }
  Returns: { "shortUrl": "https://tinyurl.com/abc1234" }   (201 Created)

GET /{shortKey}
  -> HTTP 301 (permanent) or 302 (temporary) redirect to longUrl
     (Location header = original long URL)

DELETE /api/v1/{shortKey}    (optional, owner-authenticated)
  -> removes the mapping
```

**301 vs 302 ka choice ek classic gotcha hai:** `301 Permanent Redirect` browser/proxy ko cache karne deta hai, to subsequent clicks aapke server pe aate hi nahi — load kam, par aap click analytics aur per-click control kho dete ho. `302 Found (temporary)` har click ko server pe laata hai, to analytics aur kill-switch milta hai, par read load zyada. Analytics chahiye to **302** chuno.

## High-Level Architecture

Request flow components:

1. **Client / Browser** — short URL hit karta hai ya naya URL submit karta hai.
2. **Load Balancer** — incoming traffic ko stateless app servers pe distribute karta hai.
3. **Application servers (stateless)** — do logical paths: write path (shorten) aur read path (redirect). Stateless hone se horizontally scale karna easy hai.
4. **Key Generation Service (KGS)** — unique short keys produce karta hai (neeche deep dive).
5. **Cache (Redis / Memcached)** — `shortKey -> longUrl` mapping ka hot cache; reads yahin se serve hote hain.
6. **Database (sharded NoSQL/KV store)** — source of truth for mappings.

**Read path (redirect — hot path):** `GET /{shortKey}` -> LB -> app server -> cache lookup. Cache hit pe seedha 301/302 redirect. Cache miss pe DB se fetch, cache mein populate (LRU), phir redirect.

**Write path (shorten):** `POST /shorten` -> LB -> app server -> KGS se ek unique key le ya generate kar -> DB mein `(shortKey, longUrl, metadata)` insert -> short URL return. Cache ko aksar write pe populate nahi karte (write-around), kyunki naya link turant click ho ye zaroori nahi.

## Data Model

Core table sirf ek mapping hai:

```
url_mapping
  short_key     VARCHAR(7)    PRIMARY KEY     -- the base62 alias
  long_url      TEXT          NOT NULL
  creation_date TIMESTAMP
  expiry_date   TIMESTAMP     NULL
  user_id       BIGINT        NULL            -- owner, if auth'd
```

Optionally ek `users` table aur ek `analytics` event stream (Kafka -> data warehouse) agar click tracking chahiye.

**SQL vs NoSQL ka choice:** Ye workload ek **simple key-value lookup** hai — koi complex joins ya multi-row transactions nahi. Data volume billions of rows (110 TB) hai jo horizontal partitioning demand karta hai. Isliye ek **NoSQL key-value / wide-column store** (DynamoDB, Cassandra, ya sharded relational) better fit hai: built-in partitioning, high write throughput, aur easy horizontal scaling deta hai. ACID transactions ki yahan zaroorat nahi; eventual consistency redirect ke liye acceptable hai (ek naya link milliseconds late dikhe to chalta hai). Agar relational use karna ho to bhi `short_key` pe shard karke scale kiya ja sakta hai.

## Deep Dives

Yahan 3 building blocks sabse zyada matter karte hain.

### 1. Key Generation — unique short keys kaise banayein

Do main approaches:

- **Hashing approach:** Long URL ko hash karo (MD5/SHA-256) aur first 6-7 base62 characters lo. Problem: **collisions** — do different URLs ka same prefix aa sakta hai, aur same URL do baar bhejne pe same key milta hai. Collision handle karne ke liye insert pe check-and-retry (append/rehash) karna padta hai, jo extra reads add karta hai.

- **Counter + Base62 encoding (preferred):** Ek globally unique auto-incrementing counter rakho aur uske integer value ko **base62 encode** karke short key banao. Counter `125` -> base62 -> `"21"`. Ye guarantee karta hai keys unique honge, koi collision check nahi. Distributed counter ke liye ek central service jaise **ZooKeeper** ranges allocate karta hai, ya **Twitter Snowflake**-style IDs use karte hain.

- **Key Generation Service (KGS) — best practice:** Ek dedicated service offline hi base62 keys pre-generate karke ek "available keys" DB mein rakhta hai. App server ek key chahiye to KGS se ek pre-made key le leta hai aur use "used" mark kar deta hai. Fayde: key generation read/write path se hat jaata hai (low latency), collisions structurally impossible. KGS keys ko do tables (used / unused) mein rakhta hai aur ek block of keys memory mein load karta hai — single point of failure se bachne ke liye KGS ko replicate karo.

### 2. Caching — read latency aur DB load

Reads 100x writes hain (~100K-200K QPS), to DB ko direct hit karna mehenga hai. Ek **in-memory cache (Redis/Memcached)** layer `shortKey -> longUrl` hot mappings rakhta hai.
- **80/20 rule:** ~20% URLs ~80% traffic generate karte hain, to cache hit ratio high rehta hai.
- **Eviction:** LRU policy — kam click hone wale links cache se nikal jaate hain.
- **Cache miss:** DB se fetch karke cache populate karo, phir serve. Mappings immutable hain (short->long badalta nahi), isliye stale cache ka problem nahi — invalidation almost free hai.

### 3. Sharding / Partitioning — 110 TB ko distribute karna

Single DB 110 TB aur 200K QPS handle nahi karega, to data ko shards mein todna padega.
- **Range-based sharding** (e.g. key ke first char pe) uneven load deta hai — kuch ranges hot ho jaati hain.
- **Hash-based / consistent hashing:** `shortKey` ko hash karke shard choose karo. Ye load evenly distribute karta hai. Lookup deterministic hai: `shard = hash(shortKey) % N` (ya consistent hashing ring se), kyunki redirect ke time short key hi pata hai. **Consistent hashing** use karne se node add/remove pe sirf K/N keys remap hoti hain — poora reshuffle nahi.

## Bottlenecks & Tradeoffs

- **Read hot path latency:** Cache hi asli scaling lever hai. Cache fail/cold ho to DB pe 200K QPS gir sakta hai. Mitigation: cache replication, multiple cache nodes via consistent hashing, aur DB read replicas as fallback.
- **Single global counter bottleneck:** Agar key generation ek single auto-increment counter pe depend kare to wo write throughput cap kar deta hai aur SPOF ban jaata hai. Mitigation: KGS pre-generation + ranges distribute via ZooKeeper, ya Snowflake-style distributed IDs.
- **Custom aliases + counter:** Custom alias counter-based scheme ko break karta hai (uniqueness check zaroori). Mitigation: custom alias ke liye DB mein conditional insert (unique constraint) aur collision pe user ko error.
- **301 caching vs analytics:** 301 se read load ghat-ta hai par analytics chala jaata hai; 302 ulta. Business need ke hisaab se choose karo.
- **Storage growth + expiry:** Forever-live links se 110 TB+ grow hota rehta hai. Mitigation: TTL / expiry-based cleanup, ek lazy cleanup job jo expired rows hata ke keys ko KGS pool mein wapas daale.
- **Hot key (viral link):** Ek single viral short link ek shard/cache node ko overwhelm kar sakta hai. Mitigation: us key ko multiple cache nodes pe replicate karo ya CDN-level caching of the redirect.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_tinyurl.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_tinyurl.md) — `sysd-buddy quiz scaffold design-tinyurl` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update design-tinyurl --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — high-level architecture, read/write request flow, aur key generation + sharding ka interactive diagram.
