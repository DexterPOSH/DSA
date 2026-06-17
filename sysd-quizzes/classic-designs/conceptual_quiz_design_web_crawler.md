# Design a Web Crawler — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-web-crawler --quiz-score N/M` -->

## Q1 (warm-up — requirements & scoping)
You're asked to "design a web crawler." Before drawing any boxes, what clarifying questions do you ask, and what are the core functional vs non-functional requirements you'd lock down?

**Ideal answer:**
- **Clarifying questions:** scale + time window (e.g. how many pages, by when?), content types (HTML only vs images/PDF/video), freshness needs (one-shot vs continuous re-crawl), whether text storage is needed or just the link graph, average page size assumption.
- **Functional:** fetch pages from seed URLs, extract + follow outlinks, deduplicate URLs, store content, respect `robots.txt`, support re-crawl for freshness.
- **Non-functional:** scalability (billions of pages, horizontally scalable), politeness/robustness (handle malformed HTML, slow servers, redirect loops, spider traps), fault tolerance (resumable frontier state), extensibility (new content types).
- Explicitly **scopes out** things like search ranking/indexing and JS rendering to keep the design focused.

## Q2 (core — capacity estimate)
Assume the target is 1 billion pages per month at an average 500 KB per page. Estimate the average crawl QPS, the sustained inbound bandwidth, and the monthly storage. Show the arithmetic.

**Ideal answer:**
- **QPS:** seconds/month ≈ 30·24·3600 = 2.592M s. 1e9 / 2.592e6 ≈ **~400 pages/sec** average; peak (2-3x) ≈ ~1,000/sec.
- **Bandwidth:** 400 · 500 KB = 200 MB/sec = 200·8 ≈ **~1.6 Gbps** sustained inbound.
- **Storage:** 1e9 · 500 KB = 5e14 B = **500 TB/month** raw; with ~5x compression ≈ **100 TB/month** (≈ 1.2 PB/year).
- Key takeaway: bandwidth + storage dominate → fetchers must scale horizontally and content must live in distributed blob storage. Bonus if they note seen-set lookups ≈ outlinks · QPS (≈ 10·400 = 4,000/sec).

## Q3 (data-model / store choice)
Would you store URL metadata and page content in a SQL database or NoSQL? Justify the choice, and describe the schema/keys you'd use.

**Ideal answer:**
- Picks **NoSQL** for both, with reasons: scale (billions of rows won't fit one relational box; shard by `url_hash`), simple key-based access pattern (lookup/upsert by url_hash, no complex joins/transactions), write-heavy ingest favoring wide-column stores (Cassandra/Bigtable).
- **Content:** object/blob store (S3/HDFS), **content-addressed** by `contentHash` (SHA-256) → gives automatic page-level dedup; raw bytes compressed.
- **URL metadata:** wide-column/KV with `url_hash` as PK/shard key, fields like `url`, `status` (PENDING/FETCHED/FAILED/BLOCKED), `last_crawled_at`, `content_hash`, `fetch_count`, `priority`.
- Notes that SQL's ACID/joins strength is wasted here and would become the scaling bottleneck.

## Q4 (tradeoff / gotcha — the URL Frontier)
The URL Frontier must satisfy two conflicting goals: prioritization and politeness. Explain the tension and how a two-tier (Mercator-style) frontier resolves it.

**Ideal answer:**
- **Tension:** prioritization wants to fetch the most important/fresh URLs first; politeness requires never hammering a single host (one connection at a time + delay between requests + `robots.txt`). Pure priority ordering could send many requests to the same hot host at once → impolite/banned.
- **Back queues for politeness:** each back queue maps to a single host; all of a host's URLs route to the same queue, and one worker drains it serially → per-host serialization + delay. A heap tracks each host's next-ready/next-fetch time.
- **Front queues for prioritization:** front queues represent priority levels; a biased router pulls higher-priority URLs more often and routes them into the back queues.
- Bonus: mentions `robots.txt` caching and DNS caching as part of politeness/throughput, and that the two-tier split decouples "what to fetch next" from "who to be polite to."

## Q5 (applied — scaling bottleneck + mitigation)
At scale, name two things that break in this design and how you'd mitigate each. Include the dedup strategy.

**Ideal answer:**
- **Frontier as SPOF/hotspot:** a single centralized frontier caps throughput and is a single point of failure. **Mitigation:** shard the frontier by host/domain hash — a host always maps to one shard, preserving per-host serialization while throughput scales linearly.
- **Dedup at scale:** exact seen-set for billions of URLs won't fit in RAM. **Mitigation:** a **Bloom filter** (~10 bits/elem, ~1% FP) gives "definitely new" / "maybe seen"; only "maybe" hits the backing KV store. Plus **content-level dedup** via content-hash (content-addressed store) for mirror/session-id duplicates, and URL normalization to maximize hits. Should note the Bloom FP tradeoff: false positives drop some new URLs (coverage loss), tunable via bits/element.
- Other acceptable breaks: **spider traps** (mitigate with depth/URL budget limits + blacklists), **politeness vs throughput** (keep frontier host-diverse so aggregate throughput stays high), **freshness vs cost** (adaptive re-crawl by change rate).
