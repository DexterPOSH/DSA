# Design YouTube / Video Streaming

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

YouTube jaisa system design karna hai jahan users video **upload** kar saken, system unhe transcode karke multiple resolutions mein store kare, aur baaki users unhe globally, low-latency pe, adaptive quality ke saath **stream/watch** kar saken.

## Requirements & Scope

**Functional requirements:**
- User video **upload** kare (large files, GBs tak).
- Uploaded video ko multiple resolutions/formats mein **transcode** karna (240p, 480p, 720p, 1080p, 4K) aur HLS/DASH ke liye chunks banana.
- User video **watch/stream** kare — adaptive bitrate ke saath, kahin se bhi (global), low buffering.
- View counts, likes, comments jaisi metadata operations.
- Search aur recommendation (yeh hum out-of-scope rakhenge, sirf mention karenge).

**Non-functional requirements (NFRs):**
- **High availability** > strong consistency — video stream na ruke yeh zyada important hai bajaye iske ki view count exactly real-time ho. View count thoda eventually consistent ho to chalega.
- **Low latency** streaming globally — isliye CDN zaroori hai.
- **Durability** — uploaded video kabhi lose nahi hona chahiye (11 nines wala object storage).
- **Read-heavy** system — watch:upload ratio bahut skewed hai (hum ~1000:1 maan rahe hain).
- **Scalability** — billions of videos, billions of daily watches.

**Clarifying questions jo interview mein poochne chahiye:**
- Kitne DAU aur watch:upload ratio kya hai?
- Max video size aur length? (upload pipeline aur storage estimate isi pe depend karta hai)
- Kya live streaming bhi scope mein hai, ya sirf VOD (video-on-demand)? (live ka pipeline alag hota hai — RTMP ingest, low-latency HLS — hum VOD pe focus kar rahe hain.)
- Kaunse devices/regions support karne hain? (codecs aur CDN footprint isse decide hota hai.)
- Recommendation/search in-scope hai ya nahi?

## Capacity Estimate

Maan lo numbers (interview mein assumptions clearly state karo):

- **DAU = 100M**, har user average **5 videos/day** watch karta hai.
- **Watches/day** = 100M × 5 = **500M watches/day**.
- **Read QPS (avg)** = 500M / 86,400 s ≈ **5,800 watch-starts/sec**. Peak ~2-3x → **~15K QPS**. (Yeh stream *start* requests hain; actual byte-serving CDN handle karta hai, origin nahi.)
- **Watch:upload ratio ~1000:1**, to **uploads/day** = 500M / 1000 = **500K uploads/day** ≈ **~6 uploads/sec** avg, peak ~15-20/sec. Yeh confirm karta hai ki system **read-heavy** hai.

**Storage estimate (yearly):**
- Avg uploaded video raw ≈ **5 min @ ~50 MB** maan lo. Lekin transcoding ke baad hum multiple renditions store karte hain (240p se 1080p tak), to per-source total ≈ **5x raw ≈ 250 MB** stored (including all resolutions + chunks).
- Per day = 500K × 250 MB = 125M MB = **~125 TB/day**.
- Per year = 125 TB × 365 ≈ **~45 PB/year**. (Replication/erasure-coding ke saath effective footprint aur bada — easily 100+ PB/year. Isi liye object storage + tiering chahiye.)

**Bandwidth (egress) estimate:**
- Avg watch ≈ 5 min @ **2 Mbps** (720p) maan lo → ek watch ≈ 5 × 60 × 2 Mbit = 600 Mbit ≈ **75 MB delivered**.
- Per day = 500M × 75 MB = **~37.5 PB/day egress**.
- Avg egress = 37.5 PB/day / 86,400 ≈ **~3.5 Tbps**, peak iska 2-3x. **Yeh bandwidth origin se serve karna impossible hai → CDN absolutely mandatory hai**, jo edge se serve karke origin ko sirf cache-miss pe hit kare.

## API Design

Streaming khud **HLS/DASH manifest + chunk GETs** ke through hota hai (CDN se), application APIs metadata aur upload orchestration ke liye hain.

```
# --- Upload (resumable, large file) ---
POST   /api/v1/videos
       body: { title, description, visibility }
       -> { videoId, uploadUrl }        # pre-signed S3 multipart upload URL

PUT    <uploadUrl>                       # client raw bytes ko directly object store pe daalta hai
                                         # (origin server bypass — backend load se bachne ke liye)

POST   /api/v1/videos/{videoId}/complete # upload done; transcoding pipeline trigger karta hai

# --- Watch / playback ---
GET    /api/v1/videos/{videoId}          # metadata + CDN manifest URL deta hai
GET    <cdnUrl>/{videoId}/master.m3u8    # HLS master manifest (renditions list)
GET    <cdnUrl>/{videoId}/720p/seg_003.ts# ek media chunk (CDN se serve hota hai)

# --- Engagement ---
POST   /api/v1/videos/{videoId}/view     # async view event (fire-and-forget, queue mein)
POST   /api/v1/videos/{videoId}/like
GET    /api/v1/videos/{videoId}/comments
```

Key idea: **upload aur download dono object store/CDN se directly hote hain pre-signed URLs ke through**, app servers ke through bytes nahi jaate — sirf control-plane (metadata, orchestration) app servers handle karte hain.

## High-Level Architecture

**Components:**
- **API / Metadata service** — upload init, complete, metadata reads/writes, pre-signed URL issue karna.
- **Blob/Object store (S3/GCS)** — raw uploads aur transcoded renditions/chunks ke liye durable storage.
- **Message queue (Kafka/SQS)** — `upload.complete` events ko transcoding workers tak pahunchana (decoupling + backpressure).
- **Transcoding pipeline (worker fleet)** — raw video ko ffmpeg se multiple resolutions mein convert karna, HLS/DASH ke liye segment karna, thumbnails generate karna.
- **Metadata DB** — video metadata, status, owner, view counts.
- **CDN** — edge pe chunks serve karna (global low latency).
- **Cache (Redis)** — hot metadata aur counts.

**Upload flow:**
1. Client `POST /videos` → metadata service video row banata hai (`status=UPLOADING`) aur pre-signed multipart URL return karta hai.
2. Client raw bytes **directly object store** pe upload karta hai (resumable).
3. Client `complete` call karta hai → metadata service ek event Kafka pe publish karta hai (`status=PROCESSING`).
4. Transcoding workers event consume karte hain, raw video fetch karke **multiple renditions + HLS segments** banate hain, unhe object store pe likhte hain.
5. Done hone pe worker metadata DB update karta hai (`status=READY`) aur CDN pre-warm/origin pointer set ho jaata hai.

**Watch flow:**
1. Client `GET /videos/{id}` → metadata + CDN manifest URL milta hai (cache se serve, mostly).
2. Player **master manifest** fetch karta hai CDN se → available renditions dekhta hai.
3. Player network conditions ke hisaab se **adaptive bitrate** se rendition choose karke chunks sequentially CDN se fetch karta hai. CDN miss hone pe origin (object store) se pull karke cache karta hai.
4. View event async queue pe jaata hai → count batch/stream-process hota hai.

## Data Model

**Choice: metadata ke liye SQL+NoSQL mix, video bytes ke liye object store (DB mein kabhi nahi).**

`videos` table — **NoSQL (e.g. Cassandra/DynamoDB)** kyunki yeh massive scale pe partition-by-`video_id` se linear scale karta hai aur access mostly key-based hai (point lookup by `video_id`). Strong relational joins ki zaroorat nahi.

```
videos        (NoSQL, partition key = video_id)
  video_id (PK), owner_id, title, description, visibility,
  status (UPLOADING|PROCESSING|READY|FAILED),
  duration_sec, created_at, thumbnail_url

renditions    (per video, can be embedded ya separate)
  video_id, resolution (240p..4k), codec, manifest_path, size_bytes

view_counts   (NoSQL counter / separate analytics store)
  video_id, count            # eventually consistent, async aggregated

comments      (NoSQL, partition key = video_id, sort key = created_at)
  video_id, comment_id, user_id, text, created_at
```

User/account aur subscription jaisa relational data **SQL (Postgres/MySQL)** mein rakh sakte hain — yahan ACID aur joins matter karte hain aur scale chhota hota hai. **Object store (S3/GCS)** mein actual `.ts`/`.mp4` segments aur manifests — durable, cheap, infinitely scalable; DB sirf un blobs ka **path/URL** store karta hai, bytes nahi.

**SQL vs NoSQL — why:** Video metadata catalog billions of rows tak jaata hai aur reads point-lookup-heavy hain → NoSQL ka horizontal partitioning + high write throughput better fit. View counts high-write counters hain jahan strong consistency ki zaroorat nahi → NoSQL/eventually-consistent aggregation. Accounts/billing jaisa low-volume, transactional data → SQL.

## Deep Dives

**1) Transcoding pipeline (async, queue-driven):**
Transcoding CPU-heavy aur slow hai (ek video pe minutes lag sakte hain), isliye yeh **upload request ke synchronous path se hata kar** Kafka/queue ke peeche async kiya jaata hai. Worker fleet horizontally scale karti hai aur queue lag pe autoscale karti hai. Ek bada optimization: video ko **segments mein todo aur har segment ko parallel transcode karo** (DAG-style: split → fan-out transcode per chunk per resolution → merge/manifest). Isse ek long video ka turnaround time drastically girta hai. Idempotency aur retries zaroori hain (worker crash ho to event reprocess ho, duplicate output na bane).

**2) CDN + adaptive bitrate streaming (the read-path heart):**
~3.5 Tbps egress origin se serve karna impossible hai. **CDN edge caching** ke bina yeh system exist hi nahi kar sakta. Video ko **small chunks (2-10s segments)** mein store karke HLS/DASH manifests serve karte hain. Player **adaptive bitrate (ABR)** se network ke hisaab se rendition switch karta hai — slow network pe 480p, fast pe 1080p — taaki buffering minimize ho. Popular videos edge pe cache rehte hain (high hit ratio), tail/cold videos origin se pull hote hain. Push (popular content pre-warm) vs pull (on first miss) CDN strategy ka tradeoff hota hai.

**3) Read-heavy scaling — caching + counts:**
Metadata read QPS bahut high hai. Hot video metadata **Redis** mein cache karte hain (cache-aside). View counts ko har request pe DB write karna throughput kill kar dega → **events queue pe daalo, batch/stream-aggregate karo** (Kafka + stream processor), phir periodically count materialize karo. Yeh view count ko thoda **eventually consistent** banata hai — jo NFR ke hisaab se acceptable hai.

## Bottlenecks & Tradeoffs

- **Transcoding queue backlog:** Viral upload spike pe queue lag badh sakta hai → workers autoscale + per-segment parallelism + priority queues (chhoti videos pehle).
- **CDN cache miss storm / cold start:** Naya viral video pehli baar har edge pe miss → origin overload. Mitigation: origin shielding (mid-tier cache), popular content pre-warm/push.
- **Hot video / hot partition:** Ek viral video ek partition/key ko hammer kare → CDN absorbs most reads; metadata layer pe Redis + replicas.
- **View count accuracy vs throughput:** Exact real-time count chaho to writes explode hote hain. Tradeoff: eventual consistency + batched aggregation chosen — accuracy thodi der lagti hai par system scale karta hai.
- **Storage cost:** Multiple renditions × replication = huge footprint. Mitigation: cold/unpopular videos ko cheaper storage tier (Glacier-style) pe move karo, on-demand re-transcode, ya kam-popular renditions purge.
- **Strong consistency chhoda gaya:** Availability ke liye AP-side choose kiya (PACELC/CAP) — stream chalna > metadata perfectly consistent hona.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_video_streaming.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_video_streaming.md) — `sysd-buddy quiz scaffold design-video-streaming` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update design-video-streaming --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — upload→transcode→store→CDN→watch ka end-to-end architecture flow diagram.
