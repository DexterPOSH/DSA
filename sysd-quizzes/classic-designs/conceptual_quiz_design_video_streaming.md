# Design YouTube / Video Streaming — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-video-streaming --quiz-score N/M` -->

## Q1 (warm-up)
You're asked to "design YouTube." Before drawing any boxes, what scoping/clarifying questions would you ask, and which functional vs non-functional requirements would you lock down first?

**Ideal answer:**
- **Clarifying questions:** DAU and watch:upload ratio; max video size/length; VOD only or live streaming too (live = different RTMP-ingest / low-latency-HLS pipeline); target devices/regions (drives codecs + CDN footprint); is search/recommendation in scope.
- **Functional:** upload, transcode into multiple resolutions (240p–4K) + HLS/DASH chunking, watch/stream with adaptive bitrate, engagement (views/likes/comments).
- **Non-functional:** read-heavy (watches >> uploads), high availability favored over strong consistency (stream must not stall; view count can be eventually consistent), low global latency (CDN), high durability of uploads, horizontal scalability.
- Bonus: explicitly narrows scope to VOD and defers recommendation/search.

## Q2 (core / capacity)
Assume 100M DAU, 5 watches/user/day, a ~1000:1 watch-to-upload ratio, ~5-min videos at ~2 Mbps. Estimate read QPS, uploads/sec, yearly storage, and egress bandwidth — and state the single biggest conclusion these numbers force.

**Ideal answer:**
- **Watches/day** = 100M × 5 = 500M → **read QPS ≈ 500M / 86,400 ≈ 5.8K/s**, peak ~15K/s (these are stream-*start* requests, not byte serving).
- **Uploads** = 500M / 1000 = 500K/day ≈ **~6/sec** avg → confirms system is read-heavy.
- **Storage:** raw ~50MB but ~5x with all renditions ≈ 250MB/video → 500K × 250MB ≈ **~125 TB/day → ~45 PB/year** (more with replication).
- **Egress:** 5 min @ 2 Mbps ≈ 75 MB/watch → 500M × 75MB ≈ **~37.5 PB/day ≈ ~3.5 Tbps avg**, peak higher.
- **Biggest conclusion:** ~3.5 Tbps cannot be served from origin → **CDN is mandatory**; the design must be read-heavy/CDN-first.
- Bonus: candidate states assumptions explicitly and does order-of-magnitude math, not false precision.

## Q3 (data-model / API choice)
Where do you store the actual video bytes vs. the metadata, and why would you pick NoSQL over SQL for the video catalog? How does upload/download avoid melting your app servers?

**Ideal answer:**
- **Bytes never in the DB** — raw + transcoded `.ts`/`.mp4` segments and manifests live in **object store (S3/GCS)**: durable (11 nines), cheap, infinitely scalable; DB stores only the **path/URL**.
- **Video catalog in NoSQL** (Cassandra/DynamoDB): billions of rows, access is point-lookup by `video_id`, partition-by-`video_id` scales horizontally with high write throughput; no need for relational joins. View counts → high-write counters, eventual consistency fine.
- **SQL** kept for low-volume transactional data (accounts/billing/subscriptions) where ACID + joins matter.
- **App servers bypassed for bytes:** client uploads directly to object store via **pre-signed (multipart, resumable) URLs**, and downloads come from **CDN**; app servers only handle control-plane (metadata, orchestration). This is the key to not melting backend bandwidth.

## Q4 (deep-dive tradeoff)
Why is transcoding done asynchronously off the upload request path, and how would you make a single long video transcode faster? What correctness concerns does the async/queue design introduce?

**Ideal answer:**
- **Why async:** transcoding is CPU-heavy and slow (minutes); keeping it synchronous would block the upload request and couple latency to a worker fleet. Decouple via **queue (Kafka/SQS)**: `upload.complete` event → worker fleet that **autoscales on queue lag**, with backpressure.
- **Faster long video:** **split into segments and transcode chunks in parallel** (DAG: split → fan-out transcode per chunk per resolution → merge/manifest), so turnaround drops from O(length) toward O(longest chunk).
- **Correctness concerns:** need **idempotency + retries** (worker crash → event reprocessed → must not produce duplicate/corrupt output); at-least-once delivery means dedup on `video_id`/segment; track `status` (PROCESSING→READY/FAILED) so partial output isn't served.
- Bonus: priority queues so short videos aren't starved behind long ones.

## Q5 (scaling bottleneck + mitigation)
A new video suddenly goes viral. Walk through what breaks across the read path and how you mitigate each failure — including how you keep view counts from killing your database.

**Ideal answer:**
- **CDN cold-start / cache-miss storm:** first request misses on every edge → origin overload. Mitigate with **origin shielding (mid-tier cache)** and **pre-warm/push** of popular content; high edge hit-ratio absorbs the bulk of ~3.5 Tbps.
- **Hot partition on metadata:** one `video_id` hammered → CDN absorbs most reads; for metadata use **Redis cache-aside + read replicas**.
- **View-count write storm:** writing a counter per view explodes DB throughput → **fire view events to a queue, batch/stream-aggregate (Kafka + stream processor), materialize counts periodically** → makes counts **eventually consistent**, which the NFRs allow.
- **Transcoding spike** (if it's a fresh upload): workers autoscale on lag + per-segment parallelism + priority queue.
- Bonus: names the explicit tradeoff — chose **availability + eventual consistency** over strong consistency so the stream never stalls.
