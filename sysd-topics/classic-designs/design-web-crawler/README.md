# Design a Web Crawler

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Ek web crawler ek aisa distributed system hai jo seed URLs se shuru hoke web pages ko systematically fetch karta hai, unme se naye links extract karta hai, aur un links ko follow karke web ka ek bada portion download + process kar leta hai (jaise search engine indexing, web archiving, ya ML training corpus ke liye).

## Requirements & Scope

Pehle hamesha scope clarify karo — interviewer dekhna chahta hai ki tum problem ko narrow kar sakte ho.

**Functional requirements:**
- Seed URLs ke set se shuru karke web pages ko **fetch** (HTTP GET) karna.
- Har page se naye **URLs extract** karke crawl frontier mein add karna.
- Already-seen URLs ko skip karna (**deduplication**), taaki same page baar-baar crawl na ho.
- Fetched content ko downstream ke liye **store** karna (raw HTML / parsed text), aur metadata persist karna.
- **Politeness** maintain karna — kisi single host ko hammer mat karo, `robots.txt` rules follow karo.
- **Freshness** — pages ko periodically re-crawl karna kyunki content change hota rehta hai.

**Non-functional requirements:**
- **Scalability** — billions of pages handle karna, horizontally scalable hona chahiye.
- **Politeness/Robustness** — malformed HTML, slow servers, redirect loops, spider traps ko gracefully handle karna.
- **Fault tolerance** — crawler crash ho to frontier state lost nahi hona chahiye; resumable hona chahiye.
- **Extensibility** — naye content types (images, PDFs) plug-in style add ho saken.

**Clarifying questions jo poochne chahiye:**
- Kitne pages crawl karne hain aur kitne time mein? (e.g. 1 billion pages / month)
- Sirf HTML chahiye ya images/PDF/video bhi?
- Freshness kitni important hai — ek baar crawl ya continuous re-crawl?
- Crawl ko text storage chahiye ya sirf links graph?
- Estimated average page size kya assume karein?

**Out of scope (is design ke liye):** actual search ranking/indexing, JavaScript rendering (assume mostly static HTML), aur duplicate-content (near-dup) detection — inko mention karke side rakh do.

## Capacity Estimate

Back-of-the-envelope — assume target **1 billion pages per month** crawl karna hai, average page size **500 KB** (HTML + assets metadata; pure HTML ~100 KB but let's be safe).

**Write QPS (crawl rate):**
```
1,000,000,000 pages / month
seconds in a month ≈ 30 * 24 * 3600 = 2,592,000 s
QPS = 1e9 / 2.592e6 ≈ 386 pages/sec  (~400 pages/sec average)
Peak (2-3x) ≈ ~1,000 pages/sec
```

**Bandwidth (download):**
```
400 pages/sec * 500 KB/page = 200,000 KB/sec = 200 MB/sec
= 200 MB/sec * 8 bits ≈ 1.6 Gbps sustained inbound bandwidth
```

**Storage per month (raw content):**
```
1e9 pages * 500 KB = 5e14 bytes = 500 TB / month
With compression (HTML compresses ~5x with gzip/zstd): ≈ 100 TB / month compressed
Per year ≈ 1.2 PB compressed
```

**Frontier / URL metadata storage:**
```
Assume avg page has ~10 outlinks. After dedup, suppose we track ~5 billion unique URLs.
URL metadata ≈ 100 bytes/URL (URL string ~50 B + hash + status + timestamp)
= 5e9 * 100 B = 5e11 = 500 GB metadata  → fits in a sharded KV store / DB.
```

**Read QPS:** crawler khud "read-heavy" downstream nahi hai; reads mostly internal — frontier queue se URL nikalna (~same as write QPS, ~400/sec dequeue) aur dedup "seen?" check (~outlinks * write QPS ≈ 400 * 10 = 4,000 lookups/sec on the seen-set).

Conclusion: bandwidth aur storage dominate karte hain. ~1.6 Gbps inbound aur ~1.2 PB/year — yeh batata hai ki fetchers ko horizontally scale + distributed storage (blob store) chahiye.

## API Design

Crawler mostly ek internal pipeline hai, par components ke beech clean interfaces honi chahiye. Key signatures:

```
# Frontier service (URL queue)
addURL(url, priority, hostKey) -> bool        # enqueue if not already seen
getNextURL(workerId) -> {url, hostKey}        # dequeue respecting politeness
markCompleted(url, status, fetchedAt)         # update crawl state

# Dedup / seen-set service
isSeen(urlHash) -> bool
markSeen(urlHash)

# Fetcher
fetch(url) -> {statusCode, headers, body, finalUrl}   # handles redirects, timeouts

# Content store
putPage(url, contentHash, rawBytes) -> docId
getPage(docId) -> rawBytes

# robots.txt cache
isAllowed(host, path, userAgent) -> bool
```

Agar external "submit a seed" API expose karni ho: `POST /v1/seeds { "urls": [...], "priority": "high" }`.

## High-Level Architecture

Components aur unke beech ka flow:

1. **URL Frontier** — central queue(s) jisme crawl karne wale URLs pade hain. Yeh do cheezein manage karta hai: **prioritization** (important pages pehle) aur **politeness** (per-host rate limiting). Usually do-tier design: front queues (priority ke hisaab se) + back queues (per-host, taaki ek host ke URLs ek hi worker pe serialize hon).
2. **Fetcher workers** — frontier se URL nikaalte hain, `robots.txt` check karte hain, HTTP GET karte hain. Yeh horizontally scaled fleet hai (sabse zyada machines yahin).
3. **DNS resolver (cached)** — domain ko IP mein resolve karna. DNS lookup slow ho sakta hai, isliye dedicated cached resolver rakhte hain.
4. **Content parser / link extractor** — fetched HTML parse karke text + outlinks nikaalta hai.
5. **URL filter + dedup (seen-set)** — extracted URLs ko normalize karta hai, `robots`/blacklist filter lagata hai, aur seen-set se check karta hai ki yeh URL pehle dekha to nahi.
6. **Content store (blob storage)** — raw HTML/text ko store karta hai (S3/HDFS style), plus content-hash se duplicate-page detection.
7. **Metadata DB** — har URL ka crawl status, last-crawled timestamp, content-hash.

**Request flow:** Seed URLs → Frontier → Fetcher dequeues URL → DNS resolve → robots.txt check → HTTP GET → Content store mein save → Parser extracts links → har link normalize + dedup check → naye URLs Frontier mein wapas push → loop chalta rehta hai. Re-crawl scheduler periodically purane URLs ko frontier mein wapas inject karta hai (freshness ke liye).

## Data Model

Do tarah ka data: **bulk content** (huge, append-only) aur **URL metadata** (lookups + updates).

**Content store — blob/object storage (NoSQL-style):** S3 / HDFS / a blob store. Raw bytes key-value ke roop mein. Reason: pages immutable + huge; relational schema ki zaroorat nahi; sequential write + occasional read pattern blob store ke liye perfect.
```
content:  key = contentHash (SHA-256)  → value = compressed raw bytes
          (content-addressed → automatic page-level dedup)
```

**URL metadata — wide-column / KV store (NoSQL, e.g. Cassandra/Bigtable):**
```
url_metadata:
  url_hash (PK)     -- normalized URL ka hash, sharding key
  url               -- canonical URL string
  status            -- PENDING / FETCHED / FAILED / BLOCKED
  last_crawled_at   -- timestamp
  content_hash      -- store mein content ka pointer
  fetch_count       -- retries / re-crawl count
  priority          -- crawl priority
```

**Seen-set:** bohot high-throughput membership check chahiye (4k+ lookups/sec). Exact: sharded KV / RocksDB keyed by `url_hash`. Memory bachane ke liye approximate **Bloom filter** front mein laga sakte ho (fast "definitely not seen" / "maybe seen") aur "maybe" case mein hi DB hit karo.

**SQL vs NoSQL choice + why:** Yahaan **NoSQL** pick karte hain. Reasons: (1) scale — billions of URLs, single relational box pe nahi aayega; horizontal sharding by `url_hash` natural hai. (2) Access pattern simple key-based hai (lookup/upsert by url_hash), complex joins/transactions ki zaroorat nahi. (3) Write-heavy ingest (400+ writes/sec metadata, 4k+ seen-set ops/sec) — wide-column stores (Cassandra/Bigtable) isi ke liye optimized hain. SQL ki ACID transactions + joins ki strength yahaan waste hai, aur scaling bottleneck ban jaati.

## Deep Dives

Teen building blocks jo is design ke liye sabse zyada matter karte hain.

**1. URL Frontier — prioritization + politeness (Mercator-style two-tier queues):**
Yeh crawler ka dimaag hai. Do conflicting goals balance karne hote hain:
- **Politeness:** ek single host pe ek time pe sirf ek connection, aur consecutive requests ke beech delay (e.g. host ki response time ka multiple). Iske liye **back queues** — har back queue ek single host ko map hoti hai, aur ek host ke saare URLs usi queue mein jaate hain (mapping table se). Ek worker thread ek back queue se serially URLs leta hai → automatic per-host serialization. Ek heap/priority structure track karta hai ki kaunsi host kab "ready" hai (next-fetch time).
- **Prioritization:** **front queues** priority levels (e.g. 1..N) represent karti hain. PageRank-style importance ya freshness se URL ko ek priority milti hai; ek biased router front queue se URL utha ke appropriate back queue mein daalta hai. High-priority pages zyada frequently pick hote hain.

**2. Deduplication at scale — Bloom filter + content hashing:**
Do level ki dedup chahiye. (a) **URL-level:** kya yeh URL already frontier/crawled mein hai? Billions of URLs ke liye exact set RAM mein nahi aata. Solution: ek **Bloom filter** (probabilistic, ~10 bits/element → ~1% false-positive) jo bolta hai "definitely new" ya "maybe seen". "Maybe" pe hi backing KV store check karte hain. Yeh RAM ko ~5GB level pe rakhta hai instead of TBs. (b) **Content-level:** do alag URLs same content de sakte hain (mirrors, session-id'd URLs). Content ka **hash (SHA-256)** store mein content-addressed key hota hai — same hash → already stored, dobara save mat karo. URL normalization (lowercasing, removing fragments/tracking params, sorting query params) dedup ko aur effective banata hai.

**3. Politeness + robots.txt + DNS caching:**
- `robots.txt` ko **cache** karo (per host, TTL ke saath) — har page ke liye dobara fetch karna wasteful aur impolite hai.
- **DNS caching:** crawler millions of hosts hit karta hai; uncached DNS lookups crawler ko throttle kar dete hain (synchronous + slow). Dedicated cached resolver (with local cache) latency drop kar deta hai.
- **Rate limiting** per host (politeness delay) hammering rokta hai — warna tumhe block/banned kar denge aur tum unintentional DDoS kar doge.

## Bottlenecks & Tradeoffs

- **Frontier as single point / hotspot:** ek centralized frontier throughput ko cap kar deti hai aur SPOF banti hai. **Mitigation:** frontier ko **shard** karo (by host/domain hash) taaki ek shard ek subset of hosts handle kare — per-host serialization preserve rehta hai (kyunki ek host hamesha ek hi shard pe), aur throughput linearly scale hota hai.
- **Spider traps / infinite spaces:** calendar pages, dynamically generated infinite URLs crawler ko loop mein phasa dete hain. **Mitigation:** per-host URL budget / max crawl depth, URL length limits, aur traps ko blacklist karo.
- **Politeness vs throughput tension:** strict per-host politeness se ek bade site ka crawl slow ho jaata hai. **Mitigation:** crawl ko host-diverse rakho (frontier mein many hosts simultaneously active), taaki aggregate throughput high rahe bina kisi single host ko hammer kiye.
- **Dedup false positives:** Bloom filter false-positive ka matlab kuch new URLs "seen" maan ke skip ho jaayenge (coverage loss). **Mitigation:** bits/element tune karo (lower FP rate), ya exact backing store ke saath layer karo.
- **Freshness vs cost:** sab kuch frequently re-crawl karna mehenga hai. **Mitigation:** adaptive re-crawl — frequently-changing pages (news) ko zyada, static pages ko kam frequently re-crawl karo (change-rate estimation se).
- **Storage hot spots:** content store mein popular content-hashes pe skew. **Mitigation:** content-addressed sharding + replication.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_web_crawler.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_web_crawler.md) — `sysd-buddy quiz scaffold design-web-crawler` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update design-web-crawler --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — frontier two-tier queues, fetcher fleet, dedup, aur crawl loop ka interactive architecture diagram.
