# Cache Eviction (LRU/LFU)

**Track:** Building Blocks
**Category:** Caching & CDN

## What It Is

Cache eviction wo policy hai jo decide karti hai ki jab ek fixed-size cache bhar jaaye, to nayi entry ke liye jagah banane ke liye kaunsi purani entry nikaali (evict) jaaye — LRU least-recently-used ko nikaalta hai, LFU least-frequently-used ko.

## Real-World Analogy

Socho aapke study table pe sirf 10 books rakhne ki jagah hai (ye hamari cache capacity hai), aur poori library (DB / origin) door basement mein hai jahan se book laana slow hai.

**LRU wala banda** ye rule follow karta hai: "Jo book sabse lambe time se chhui hi nahi gayi, usko basement wapas bhej do." Aaj subah aapne jo book padhi, wo table pe rahegi; jo do hafte se untouched padi hai, wo sabse pehle jaayegi. Logic simple hai — recently use hui cheez aage bhi use hone ka chance zyada rakhti hai.

**LFU wala banda** count rakhta hai: "Har book pe ek tally mark lagao jab bhi padho. Jo book sabse kam baar padhi gayi (lowest count), usko nikaalo." Yahan timing nahi, total frequency matter karti hai. Ek dictionary jo aap 50 baar khol chuke ho wo bachi rahegi, chahe aaj na padhi ho; jo novel aapne sirf 1 baar dekha tha wo pehle jaayega.

Dono ka asli sangharsh table ki limited jagah aur basement ki slow trip ke beech hai — sahi book table pe rakho to basement trip (cache miss) bachti hai.

## How It Works

Cache ek bounded store hai, maan lo capacity `C = 1000` entries, hosted in RAM with ~1 ms (often sub-ms) lookup latency, jabki cache miss pe origin/DB se fetch 50-200 ms le sakta hai. Har `GET` request pe agar key present hai → **cache hit** (fast return), warna **cache miss** → origin se fetch, cache mein daalo, aur agar cache full hai to ek victim evict karo.

**LRU (Least Recently Used):**

1. Data structure: ek **hash map** (key → node) plus ek **doubly linked list** jo entries ko recency order mein rakhti hai — most-recently-used head pe, least-recently-used tail pe.
2. **On access (hit):** node ko list se detach karke head pe move kar do (mark as most-recent). Ye O(1) hota hai kyunki doubly linked list mein prev/next pointers se splice instant hai.
3. **On insert (miss):** naya node head pe add karo. Agar `size > C`, to **tail** wala node (least-recently-used) hata do aur hash map se uski key delete kar do.
4. Net effect: har operation O(1) time. 1000-entry cache pe ek eviction sirf 2-3 pointer updates hai — microseconds.

**LFU (Least Frequently Used):**

1. Har entry ke saath ek **frequency counter** rakho. Access pe counter `++`.
2. Eviction pe **lowest counter** wali entry nikaalo. Naive implementation O(N) scan karega — slow.
3. O(1) LFU: ek **frequency-bucket** structure — har distinct frequency ke liye ek doubly linked list of entries, aur ek `minFreq` pointer. Access pe entry ko `freq` bucket se `freq+1` bucket mein move karo; evict karte waqt `minFreq` bucket ke tail ko nikaalo. Naye entry ka freq `1` set hota hai aur `minFreq = 1`.
4. Tradeoff: LFU ko per-key extra counters + bucket bookkeeping chahiye, to memory overhead LRU se thoda zyada hota hai.

Real numbers ka feel: agar hit ratio 90% se 95% ho jaaye, to 1M QPS pe origin hits 100K/s se ghat ke 50K/s ho jaate hain — origin load aadha. Isiliye eviction policy ka choice tail latency aur backend cost dono pe seedha asar daalta hai.

## Tradeoffs & Variants

- **LRU vs LFU — recency vs frequency:** LRU temporal locality pakadta hai (abhi-abhi use hui cheez), LFU long-term popularity pakadta hai. LRU ek **scan/flood** se bigad jaata hai — ek baar ka bada sequential read (jaise full table scan) saari hot entries ko tail tak push karke evict kar deta hai (cache pollution). LFU is scan ko resist karta hai kyunki one-time reads ka count `1` rehta hai.
- **LFU ka "stale/aging" problem:** Purani entry jo kabhi bahut popular thi (high count) wo high frequency ki wajah se cache mein atki reh sakti hai chahe ab koi use na kare. Fix: **frequency decay / aging** (counts ko time ke saath halve karna) ya **LFU with dynamic aging** / **TinyLFU/W-TinyLFU** jaise schemes.
- **Approximations for cost:** True LRU ko per-access pointer updates chahiye, jo high-concurrency mein lock contention deta hai. Isiliye real systems aksar **approximate** karte hain: Redis ka **`allkeys-lru`** ek **sampling** approach use karta hai (`maxmemory-samples`, default 5) — exact LRU ke bajaye randomly N keys sample karke unme se oldest evict karta hai. Linux page cache **CLOCK / second-chance** algorithm use karta hai (ek reference bit) jo LRU ko approximate karta hai bina full linked list maintain kiye.
- **Admission vs eviction:** Modern caches (Caffeine, jo **W-TinyLFU** use karta hai) eviction ke saath **admission control** bhi karte hain — naye item ko tabhi admit karte hain jab wo evict-hone-wale victim se "zyada valuable" lage (frequency sketch se estimate). Ye hit ratio LRU se kaafi behtar deta hai.
- **TTL aur size-awareness:** Pure LRU/LFU "value freshness" ya "object size" ignore karte hain. Real systems eviction ko **TTL** (expiry) aur kabhi **size-aware** (bade objects pehle nikalo) ke saath combine karte hain.

## When To Use It

- **In-memory caches:** Redis aur Memcached — Redis explicitly `maxmemory-policy` deta hai: `allkeys-lru`, `allkeys-lfu`, `volatile-lru`, `allkeys-random`, etc. Default eviction tab kick karta hai jab `maxmemory` hit ho.
- **Application-level caches:** Java mein **Caffeine** (W-TinyLFU) aur **Guava Cache** (LRU-ish), Go/Python LRU dicts (Python ka `functools.lru_cache`).
- **OS / DB internals:** Linux page cache (CLOCK), database buffer pools (PostgreSQL clock-sweep, MySQL InnoDB ek LRU variant jo scan-resistance ke liye list ko young/old sublists mein todta hai).
- **CDN edge caches:** Akamai/Cloudflare/CloudFront edge nodes popular content cache karte hain aur eviction se decide karte hain kya rakhein — yahan size-aware + frequency-aware policies common hain.
- **Interview signal:** Jab "design a cache", "design Redis", "rate limiter ke saath hot-key cache", ya "design a CDN/news feed" aaye — bounded memory + reuse pattern ka zikr ho to eviction policy explicitly discuss karo.

## Common Interview Gotchas

- **"LRU O(1) kaise?" — sirf hash map bolna galat hai.** O(1) ke liye **hash map + doubly linked list dono** chahiye. Hash map se key → node lookup O(1), aur doubly linked list se recency reorder + tail eviction O(1). Singly linked list se detach O(N) ho jaata, isiliye **doubly** linked list zaroori hai. Ye combo classic LeetCode "LRU Cache" (146) ka core hai.
- **LRU vs LFU ko interchange kar dena:** LRU = recency (kab last access hua), LFU = frequency (kitni baar access hua). Ye alag hain — ek scan workload pe LRU bura, LFU accha; ek shifting-popularity workload pe LFU stale entries pe atak jaata hai, LRU better adapt karta hai.
- **"Naive LFU bhi O(1) hai" maan lena:** Lowest-count dhoondhna naive mein O(N) scan hai. O(1) LFU ke liye **frequency buckets + minFreq pointer** chahiye — ye detail interviewers specifically probe karte hain.
- **Sochna ki Redis exact LRU karta hai:** Redis by default **approximate (sampled) LRU/LFU** karta hai memory bachane ke liye — exact recency order maintain nahi karta. `maxmemory-samples` badhane se accuracy badhti hai par CPU cost bhi.
- **Thread-safety bhool jaana:** Concurrent access mein linked list reorders ko synchronize karna padta hai; warna race conditions cache corrupt kar dete hain. Real systems sharded locks / lock-free structures / sampling se contention kam karte hain.
- **Cache stampede ko eviction se confuse karna:** Eviction (jagah banana) aur stampede/thundering-herd (ek hot key expire/evict hone pe sab requests ek saath origin ko hit karna) alag problems hain — stampede ka fix request coalescing / locks, eviction ka fix policy choice hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/caching-cdn/conceptual_quiz_cache_eviction.md`](../../../sysd-quizzes/caching-cdn/conceptual_quiz_cache_eviction.md) — `sysd-buddy quiz scaffold cache-eviction` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update cache-eviction --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — LRU doubly-linked-list + hash map, access/reorder, aur tail eviction ka interactive diagram.
