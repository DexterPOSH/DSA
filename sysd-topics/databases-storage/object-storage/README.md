# Blob / Object Storage

**Track:** Building Blocks
**Category:** Databases & Storage

## What It Is

Object storage ek storage system hai jisme data ko immutable "objects" (blob + metadata + ek unique key) ke roop mein ek flat namespace ("bucket") mein rakha jaata hai aur HTTP API ke through access kiya jaata hai, na ki file paths ya disk blocks ke through.

## Real-World Analogy

Socho ek bahut bada cloakroom (object storage) hai. Tum apna bag (the object — data + metadata) counter pe doge, aur badle mein ek token slip milti hai jis pe ek unique number likha hota hai (the key). Ab tumhe ye nahi pata ki tumhara bag andar kis shelf, kis room, ya kitni copies mein rakha gaya — wo cloakroom ka internal kaam hai. Jab chahiye ho, bas wahi token number do (`GET key`) aur poora bag wapas mil jaata hai.

Do important baatein yahan se click hoti hain. Ek: tum bag ke andar haath daal ke sirf ek shirt nahi badal sakte — pura bag wapas le ke, naya pack karke, dobara jama karna padta hai (objects immutable hote hain, in-place edit nahi). Do: cloakroom chahe lakhon bag rakh le, tumhara experience same rehta hai — bas token do aur le jao (flat namespace, infinite-feeling scale). Yahi object storage ka core mental model hai: token-in, blob-out, no folders, no in-place editing.

## How It Works

1. **Bucket aur key:** Sabse pehle ek **bucket** banta hai (ek global-ish naam, jaise `my-app-uploads`). Bucket ke andar har object ka ek **key** hota hai — ek plain string jaise `users/42/avatar.png`. Yaad rakho: slashes sirf naam ka hissa hain, real directories nahi hote — namespace **flat** hai. "Folder" feel sirf key prefix listing se aata hai (`prefix=users/42/`).

2. **Object = blob + metadata:** Har object teen cheezein store karta hai — actual bytes (the blob, few bytes se le ke **5 TB** tak single object, e.g. S3 limit), system metadata (size, content-type, etag, last-modified), aur optional user metadata (custom key-value tags).

3. **Write path (PUT):** Client ek HTTP `PUT /bucket/key` bhejta hai. Gateway request ko authenticate karta hai (signature, e.g. AWS SigV4), object ko chunks mein todta hai, **replicate ya erasure-code** karke multiple disks/nodes/AZs pe likhta hai, aur ek **key → location** mapping metadata store (ek separate, highly-available index) mein daal deta hai. Tabhi success return hota hai — yahi **durability** ka guarantee deta hai (e.g. S3 ka "11 nines", 99.999999999% — yaani 10 million objects pe ~1 object loss har 10,000 saal mein).

4. **Read path (GET):** `GET /bucket/key` aata hai → metadata index se object ki location lookup hoti hai → bytes fetch ho ke stream ho jaate hain. Hot objects ke liye aage ek **CDN** (CloudFront/Akamai) lagta hai jo edge pe cache karta hai, taaki origin latency (typically tens-of-ms range) user tak na pahunche.

5. **Immutability aur overwrite:** Object ko in-place edit nahi karte. "Update" ka matlab hai usi key pe **naya object PUT karna** jo purane ko replace kar de. Isiliye object stores **versioning** offer karte hain — har overwrite ek nayi version-id banata hai, purani version recover ho sakti hai.

6. **Large uploads — multipart:** Bade objects (e.g. >100 MB) ke liye **multipart upload** hota hai — file ko parts (har part typically ≥5 MB) mein todo, parts ko parallel mein upload karo, retry sirf failed part ka karo, aur end mein ek "complete" call se server unhe ek single object mein assemble kar deta hai. Ye throughput aur reliability dono badhata hai.

7. **Consistency:** Aaj ke major object stores (S3 since Dec 2020, GCS) **strong read-after-write consistency** dete hain — PUT ke turant baad GET latest data deta hai. (Pehle S3 eventually consistent tha, ye ab purani baat hai — interview mein dhyan rakhna.)

## Tradeoffs & Variants

- **Object vs Block vs File storage:** Object = HTTP API, flat namespace, immutable objects, infinite scale, par **high per-op latency** aur **no partial in-place writes** — random-access/transactional workloads (databases ka data dir) ke liye galat. Block storage (EBS, raw volumes) = low-latency random read/write, databases ke liye. File storage (NFS/EFS) = POSIX paths + hierarchy + partial writes, shared file systems ke liye. Interviewer aksar yahi distinction probe karta hai.

- **Replication vs Erasure coding:** Replication (e.g. 3 copies) = simple, fast recovery, par **3x storage cost**. Erasure coding (e.g. Reed-Solomon 10+4: data ko 10 shards + 4 parity mein todo) = same durability at ~**1.4x overhead**, par CPU cost aur degraded-read mein reconstruction overhead. Cold/large data → erasure coding; hot/small → replication.

- **Storage classes / tiering:** Hot (S3 Standard) → frequent access, higher per-GB cost, low latency. Infrequent (S3 Standard-IA) → cheaper storage, retrieval fee. Archive (Glacier / Glacier Deep Archive) → bahut sasta (~$1/TB/month range) par retrieval mein **minutes se hours** lag sakte hain. Lifecycle policies se objects automatically tier-down hote hain (e.g. 30 din baad IA, 90 din baad Glacier).

- **Strong vs eventual consistency:** Modern stores strong consistency dete hain, par cross-region replication async (eventual) hota hai. Multi-region setup mein ye tradeoff samajhna zaroori hai.

- **Flat namespace ke side-effects:** "List by prefix" allowed hai par sorting/range scans heavy ho sakte hain; bahut saare objects ko ek hi key-prefix ke neeche rakhne se historically throttling/hot-partition issues aate the.

## When To Use It

- **Media aur static assets:** Images, videos, audio — jaise user uploads, thumbnails. Netflix apne video segments S3 pe rakhta hai, fir CDN se serve karta hai.
- **Backups, archives, logs:** Bade, write-once-read-rarely datasets — DB snapshots, raw event logs, compliance archives.
- **Data lake / analytics:** S3/GCS/Azure Blob raw data store ke roop mein; Spark, Presto, Athena seedha objects pe query karte hain. Parquet/ORC files yahin rehti hain.
- **Static website hosting + CDN origin:** HTML/JS/CSS bundles object store mein, CDN front mein.
- **ML training data:** Bade training datasets aur model checkpoints object storage pe.
- **Real systems:** AWS S3, Google Cloud Storage, Azure Blob Storage, MinIO (self-hosted, S3-compatible), Ceph RADOS Gateway.

**Kab NAHI use karna:** Transactional/OLTP databases, low-latency random access, ya jahan partial in-place updates chahiye — wahan block ya file storage chahiye.

## Common Interview Gotchas

- **"Objects ko edit kar lo" — galat:** Objects **immutable** hain. Ek byte badalne ke liye bhi pura object dobara PUT karna padta hai. Agar design mein frequent small in-place updates chahiye (e.g. counter, DB rows), object storage galat choice hai — interviewer yahin trap karta hai.

- **Durability ≠ Availability:** Ye do alag numbers hain. **Durability** (e.g. 11 nines) = data lose nahi hoga. **Availability** (e.g. S3 Standard ka 99.99%) = us moment pe data accessible hoga. Tum 11-nines durable ho sakte ho par phir bhi ek outage mein temporarily unavailable. Dono ko interchange mat karo.

- **Flat namespace, real folders nahi:** `a/b/c.png` mein `a/b/` koi directory nahi — ye sirf key string ka prefix hai. "Rename a folder" jaisa O(1) operation nahi hota; har object ko effectively copy+delete karna padta hai.

- **"S3 eventually consistent hai" — purani baat:** S3 ab (Dec 2020 se) strong read-after-write consistency deta hai. Agar tum interview mein "S3 eventually consistent hai isliye stale read aa sakta hai" bologe to wo outdated hai.

- **Latency expectations:** Object storage low-latency random-access ke liye nahi hai — single GET typically tens-of-ms order ka hota hai, na ki block storage jaisa sub-ms. High-QPS hot reads ke liye CDN ya cache (Redis) aage lagao, seedha origin ko mat hammer karo.

- **Cost model:** Sirf storage per-GB hi nahi — **request count** (PUT/GET ke per-1000 charges), **egress/data-transfer**, aur archive **retrieval fees** bhi cost hain. "Glacier sasta hai" sun ke bina retrieval cost/time soche use karna mehnga pad sakta hai.

- **Large file = multipart:** Bade objects ek single PUT mein bhejne ki koshish (timeout/retry-from-zero) galti hai — multipart upload mention karna expected hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/databases-storage/conceptual_quiz_object_storage.md`](../../../sysd-quizzes/databases-storage/conceptual_quiz_object_storage.md) — `sysd-buddy quiz scaffold object-storage` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update object-storage --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — bucket/key, write path (replicate/erasure-code + metadata index), read path with CDN, aur object-vs-block-vs-file comparison ka interactive diagram.
