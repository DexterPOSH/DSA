# Design Uber / Nearby — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-uber-nearby --quiz-score N/M` -->

## Q1 (warm-up — requirements/scoping)
You're asked to "design Uber." Before drawing anything, how do you scope this down to the Nearby + matching core? List the functional and non-functional requirements you'd commit to, and two clarifying questions you'd ask the interviewer.

**Ideal answer:**
- Functional: drivers send periodic location updates; riders query nearby available drivers (radius or top-K); riders request a ride and get matched to a driver; live trip location tracking after match.
- Non-functional: low latency for nearby/matching (p99 ~200-300 ms), high availability (matching down = lost revenue), scalability for millions of concurrent drivers (write-heavy ingest), eventual consistency acceptable for location but NO double-booking.
- Clarifying questions (any two): single-region vs global (drives geo-sharding); top-K vs fixed-radius reads; how stale can a displayed location be (freshness vs accuracy); full trip lifecycle/pricing/payment in scope or just nearby+matching.
- Bonus: explicitly de-scoping pricing/payment/ETA models to keep focus.

## Q2 (core — capacity estimate)
Estimate the dominant load on this system. Assume 1,000,000 drivers online at peak, each sending location every 4 seconds. What's the write QPS, the live-state storage, and why does this number drive your architecture?

**Ideal answer:**
- Write QPS = 1,000,000 / 4 s = **250,000 writes/sec** — this is the headline number; the system is write-heavy on location ingest.
- Live state per driver ~40-100 B (driverId, lat, lng, ts, status); 1M × 100 B ≈ **100 MB** — small enough to live in memory (Redis).
- Contrast with reads: ~1M ride requests/hour ≈ 278 QPS base (~1-2K with retries), so reads << writes.
- Implication: cannot push 250K row-updates/sec at a relational DB; need in-memory geo-store + decouple persistence (Kafka). Persisted location trail is huge (~TB/day) so it goes to cold/time-series storage, not the hot path.

## Q3 (data-model / API choice)
For the location endpoint vs the ride/booking entity, what storage would you pick for each and why? Also: why make the location-update API "ack-only" and the ride-request API asynchronous?

**Ideal answer:**
- Location: **in-memory NoSQL (Redis geo-index)** — high-write, ephemeral, eventually-consistent, needs spatial queries (GEOADD/GEOSEARCH, O(log N)); relational per-row updates at 250K/sec would choke. TTL evicts stale/disconnected drivers.
- Ride/booking: **relational/SQL (Postgres)** — transactional entity needing ACID for atomic driver claim, state transitions, and avoiding double-booking. Raw location trail archived to object/time-series store, not Postgres.
- Location API ack-only: it's hit at 250K QPS, so keep the response tiny (no heavy payload) to minimize work/bandwidth.
- Ride API async (202 Accepted): matching involves nearby search + lock + driver offer/accept, which can take time; blocking synchronously hurts latency and UX, so return a rideId and push the result.

## Q4 (deep-dive tradeoff — geospatial indexing)
Why can't you just run `WHERE distance(rider, driver) < r` over the driver table? Compare geohash vs quadtree vs S2/H3 for the nearby query, and name one concrete gotcha with geohash.

**Ideal answer:**
- Naive distance scan is O(N) over all drivers — dead at 1M drivers per query. Need a spatial index.
- Geohash: encodes lat/lng into a base-32 string where shared prefix = proximity; nearby = same/adjacent prefix buckets; what Redis GEOSEARCH uses; simplest production choice.
- Quadtree: recursively subdivides space into 4 quadrants, deeper in dense areas → adaptive to skew, but rebalance/maintenance cost.
- S2 (square cells) / H3 (hexagons): hierarchical cells on the sphere; Uber uses H3 because hexagon neighbours are equidistant (avoids square-corner distance distortion); production-grade.
- Geohash gotcha: cell-boundary problem — two nearby points can land in different prefix cells, so you must also query the **8 neighbouring cells** (center + ring), not just the rider's cell.

## Q5 (applied — scaling bottleneck + mitigation)
At scale, two problems bite: (a) the 250K QPS write firehose overwhelming a single store, and (b) two riders racing to book the same driver. How do you mitigate each?

**Ideal answer:**
- Write firehose: **geo-shard** the location store by city/region (Mumbai drivers on Mumbai shard, etc.) so each shard handles only its region's writes+reads and nearby queries resolve within a shard; **decouple persistence** via Kafka — Redis keeps only the latest location (overwrite semantics), durable history streams to Kafka for downstream consumers, keeping the ingest service thin. Also mention hot-region skew (downtown density) → adaptive indexing / dynamic sub-sharding.
- Double-booking race: **atomically claim** the driver before offering — Redis SETNX lock on driverId, or a conditional DB update (`UPDATE ... WHERE status='AVAILABLE'`) / row lock; only the winning request offers the ride. Release lock on decline/timeout and fall through to the next candidate. This is the consistency split: nearby reads can be eventual/AP-leaning, but the claim/booking must be strongly consistent.
