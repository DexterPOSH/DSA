# Blob / Object Storage — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update object-storage --quiz-score N/M` -->

## Q1 (warm-up)
What is object storage, and how does its data model differ from a traditional file system?

**Ideal answer:**
- Object storage data ko immutable **objects** mein rakhta hai; har object = blob (bytes) + metadata + ek unique **key**.
- Objects ek **flat namespace** ("bucket") mein rehte hain — koi real directory hierarchy nahi (slashes sirf key string ka prefix hain).
- Access HTTP API (PUT/GET/DELETE) se hota hai, na ki file paths ya POSIX semantics se.
- File system ke विपरीत: no true folders, no partial in-place writes, no path-based traversal — bas key-in, object-out.

## Q2 (core)
Walk through what happens on the write (PUT) path and how the system achieves durability. Mention how a later GET finds the data.

**Ideal answer:**
- Client `PUT /bucket/key` bhejta hai; gateway request ko **authenticate** karta hai (e.g. signature).
- Object ko **replicate ya erasure-code** karke multiple disks/nodes/**AZs** pe likha jaata hai — yahi durability deta hai (e.g. S3 "11 nines").
- Ek **key → location** mapping ek separate **metadata/index store** mein likhi jaati hai; tabhi success return hota hai.
- GET pe: index se location lookup → bytes fetch/stream. Bonus: CDN edge cache for hot objects, strong read-after-write consistency.
- Bonus: large objects ke liye **multipart upload** (parts parallel mein, retry per-part).

## Q3 (tradeoff)
When would you choose object storage over block storage, and what's the tradeoff between replication and erasure coding for durability?

**Ideal answer:**
- **Object vs block:** Object = HTTP API, flat namespace, immutable, huge scale, par **high per-op latency** aur **no partial in-place writes** → media/backups/data-lake ke liye. Block = low-latency random read/write → databases/transactional workloads ke liye.
- **Replication** (e.g. 3 copies): simple, fast recovery, par **~3x storage cost**.
- **Erasure coding** (e.g. RS 10+4): same durability at ~**1.4x overhead**, par CPU cost aur degraded-read reconstruction overhead.
- Conclusion: cold/large data → erasure coding; hot/small → replication. Bonus: storage class tiering (Standard → IA → Glacier).

## Q4 (gotcha)
Your teammate says "let's store our app's user-profile rows as objects and just edit the object whenever a field changes." What's wrong with that, and what's the difference between durability and availability?

**Ideal answer:**
- Objects are **immutable** — ek field badalne ke liye bhi **pura object dobara PUT** karna padta hai (no partial in-place write). Frequent small updates → object storage galat choice; block/DB chahiye.
- Latency bhi galat fit hai: object GET tens-of-ms order, transactional row access ke liye nahi.
- **Durability ≠ availability:** Durability (e.g. 11 nines) = data lose nahi hoga. Availability (e.g. 99.99%) = us moment accessible hoga. Highly durable hote hue bhi ek outage mein temporarily unavailable ho sakta hai.

## Q5 (applied)
Design the storage layer for a photo/video-sharing service handling millions of uploads. Where do object storage, CDN, multipart upload, and tiering fit?

**Ideal answer:**
- **Object storage** (S3/GCS/Azure Blob) raw media ke liye — store original + processed renditions (thumbnails, transcodes) as separate keys.
- **Multipart upload** for large videos — parts parallel, per-part retry, better throughput/reliability.
- **CDN** (CloudFront/Akamai) origin ke aage — hot reads edge se serve, origin latency/load bachao; key/URL design with cache-friendly paths.
- **Versioning** for overwrites; metadata DB se key/ownership/permissions track (object store khud transactional index nahi).
- **Lifecycle/tiering:** purani/rarely-accessed media → IA/Glacier se cost bachao.
- Bonus: presigned URLs se client seedha upload/download kare (app servers bypass), strong read-after-write consistency.
