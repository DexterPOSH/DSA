# Cache Strategies

**Track:** Building Blocks
**Category:** Caching & CDN

## What It Is

Cache strategies wo patterns hain jo decide karte hain ki application, cache, aur backing store (DB) ke beech reads aur writes kaise route aur synchronize hon — jaise cache-aside, read-through, write-through, write-back, aur write-around.

## Real-World Analogy

Socho ek busy restaurant ka kitchen hai. Main store-room (database) door peeche hai aur slow hai — wahan tak jaana time leta hai. Cook ke paas saamne ek chhoti counter shelf (cache) hai jisme sabse zyada use hone wale ingredients rakhe rehte hain.

- **Cache-aside:** Cook ko jab tomato chahiye, wo pehle counter shelf dekhta hai. Mil gaya to use kar liya (cache hit). Nahi mila (cache miss) to peeche store-room jaata hai, tomato laata hai, ek copy counter shelf pe rakh deta hai, phir use karta hai. Yahan cook khud (application) shelf ko manage kar raha hai.
- **Write-through:** Jab nayi stock aati hai, cook ek saath counter shelf aur store-room dono mein rakhta hai — taaki dono hamesha match karein.
- **Write-back:** Cook jaldi-jaldi sirf counter shelf update karta hai aur store-room ko baad mein batch mein sync karta hai — fast, par agar shelf gir gayi (cache crash) to wo pending updates kho sakte hain.

Yahi tradeoff har strategy ka core hai: speed vs consistency vs data-loss risk.

## How It Works

Pehle ek baseline samjho: ek typical in-memory cache (Redis/Memcached) ka read latency **sub-millisecond se ~1 ms** hota hai, jabki ek disk-backed DB read **5-20 ms** le sakta hai. Isiliye agar hum 90% reads cache se serve kar pāyein (90% hit ratio), to average latency dramatically gir jaati hai aur DB pe load kam ho jaata hai.

**1. Cache-Aside (Lazy Loading) — sabse common:**
- Read: app cache se key maangta hai. Hit → return. Miss → app DB se padhta hai, cache mein `SET key value EX <ttl>` karke daalta hai, phir return karta hai.
- Write: app DB mein likhta hai, aur cache mein us key ko **invalidate (delete)** kar deta hai (update nahi — delete safer hai).
- App khud cache aur DB dono ko orchestrate karta hai; cache ko DB ka knowledge nahi hota.

**2. Read-Through:**
- App sirf cache se baat karta hai. Miss hone pe **cache library/provider khud** DB se load karke populate karta hai, phir app ko return karta hai. Logic cache layer mein chhupa hota hai, application code clean rehta hai.

**3. Write-Through:**
- Har write cache aur DB dono mein **synchronously** jaati hai — pehle cache (ya DB), phir doosra, dono confirm hone ke baad hi success. Cache hamesha DB ke saath consistent rehta hai, par write latency = cache write + DB write (dono ka sum), to writes thode slow hote hain.

**4. Write-Back (Write-Behind):**
- Write sirf cache mein jaati hai aur turant ack ho jaati hai (fast, ~1 ms). Cache un dirty entries ko **asynchronously batch** karke DB mein baad mein flush karta hai. Throughput aur write latency best, par cache crash hone pe un-flushed writes ka **data-loss risk**. DB write bursts ko absorb karne ke liye great (e.g. high-frequency counters, metrics).

**5. Write-Around:**
- Write seedha DB mein jaati hai, cache ko bypass karke. Cache sirf tab populate hota hai jab koi us key ko read kare (cache-aside ke saath pairs). Isse cache "write-once-read-never" data se polluted nahi hota. Tradeoff: recently-written data ka pehla read hamesha miss hoga.

**TTL aur eviction:** Har strategy ke saath entries ko ek **TTL** (e.g. 60s, 300s) dete hain taaki stale data bounded rahe, aur memory full hone pe ek eviction policy (typically **LRU**) purani/least-used entries hata deti hai.

## Tradeoffs & Variants

- **Cache-aside vs read-through:** Cache-aside flexible hai (app kuch bhi load logic likh sakta hai) par har caller ko sahi karna padta hai aur code duplicate hota hai. Read-through clean hai par caching provider/library pe dependency aur kam customization.
- **Write-through vs write-back:** Write-through = strong cache-DB consistency, slow writes, no data-loss. Write-back = blazing fast writes + write coalescing, par durability risk (cache crash = lost writes). Interviewer poochega: "kya aap stale ya lost data afford kar sakte ho?"
- **Invalidate vs update on write:** Write pe cache entry ko **delete** karna (invalidate) generally update se safer hai — kyunki concurrent writes mein update karne se cache ek stale value se overwrite ho sakta hai (race condition). Delete karne se next read fresh value load karega.
- **TTL length:** Chhota TTL → fresher data, lower hit ratio, zyada DB load. Bada TTL → high hit ratio, par zyada staleness. Ye knob consistency vs efficiency ka direct lever hai.

## When To Use It

- **Cache-aside:** Default choice for read-heavy workloads jaise user profiles, product catalogs, feed metadata. Facebook ka famous **Memcached + MySQL** setup essentially cache-aside hai.
- **Read-through:** Jab aap caching ko ek clean abstraction ke peeche rakhna chahte ho — e.g. **Netflix EVCache**, ya CDN-style edge caches.
- **Write-through:** Jab read-after-write consistency important ho aur write volume manageable ho — e.g. configuration data, session data.
- **Write-back:** High-throughput write absorption — metrics/counters, like-counts, analytics ingestion. DB-level pe Linux page cache aur SSD controllers internally write-back use karte hain.
- **Write-around:** Jab bahut data write hota hai par rarely read — logs, audit trails, bulk imports — taaki cache pollute na ho.

## Common Interview Gotchas

- **"Cache hamesha DB ke saath consistent rehta hai" — galat.** Sirf write-through (sync) hi tight consistency deta hai. Cache-aside aur write-back mein hamesha ek staleness/inconsistency window hota hai. Interview mein hamesha consistency model explicitly state karo.
- **Cache stampede / thundering herd:** Ek popular key expire hote hi hazaaron concurrent requests ek saath miss hokar DB ko hit kar dete hain (cache stampede). Mitigations: request **coalescing / single-flight** (ek hi request DB se load kare, baaki wait karein), **early/probabilistic expiration**, ya **locking** with a short lock TTL. Ye sabse common follow-up hai.
- **Thundering on cold start:** Empty cache pe sudden traffic = saare reads DB pe. Cache **warming** (pre-loading hot keys) se mitigate karo.
- **Invalidate vs update confusion:** Bahut log write pe cache ko naye value se "update" karna suggest karte hain — par concurrent writes mein ye stale-overwrite race create karta hai. Safer answer: **delete (invalidate)** on write.
- **Negative caching bhulna:** Agar DB mein key exist hi nahi karti, to har request miss hokar DB pe jaayegi. Solution: "not found" result ko bhi short TTL ke saath cache karo (negative caching), warna missing keys DB ko hammer karti hain.
- **Write-back ko durable maan lena:** Write-back fast hai par cache crash pe un-flushed data gone. Critical/financial data ke liye ise mat suggest karo.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/caching-cdn/conceptual_quiz_cache_strategies.md`](../../../sysd-quizzes/caching-cdn/conceptual_quiz_cache_strategies.md) — `sysd-buddy quiz scaffold cache-strategies` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update cache-strategies --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — cache-aside, write-through, aur write-back ke read/write flows ka interactive diagram.
