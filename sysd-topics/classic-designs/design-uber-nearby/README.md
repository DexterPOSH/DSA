# Design Uber / Nearby

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Ek ride-hailing system design karna hai jahan riders apni current location se nearby available drivers dhoondh sakein, ek ride request kar sakein, aur system real-time mein unhe ek matching driver ke saath match kar de — yaani "Nearby drivers" lookup + driver-rider matching at scale.

## Requirements & Scope

Pehle scope nail karo — interviewer ko dikhao ki aap requirements ko functional aur non-functional mein todte ho.

**Functional requirements:**
- Driver apni location har few seconds mein update kare (location heartbeat).
- Rider ek given location ke aas-paas (radius ya top-K) ke **nearby available drivers** dekh sake.
- Rider ek ride request kare; system use ek nearby available driver ke saath **match** kare.
- Match hone ke baad driver aur rider ek dusre ki **live location** track kar sakein (trip tracking).

**Non-functional requirements:**
- **Low latency:** nearby query aur matching p99 < 200-300 ms feel honi chahiye — varna UX kharaab.
- **High availability:** matching service down matlab koi ride nahi — paisa rukta hai. Read-heavy path par availability > strong consistency.
- **Scalability:** millions of concurrent drivers, har ek frequently location bhej raha hai (write-heavy ingest).
- **Geo-correctness:** lookup spatially sahi ho — galat shahar ke drivers na aayein.
- **Eventual consistency** location data ke liye theek hai (driver 2-4 sec purani location pe dikhe to chalega), lekin **double-booking nahi** honi chahiye (ek driver ek hi rider ko).

**Clarifying questions** jo interviewer se poochne chahiye:
- Sirf matching karna hai ya full trip lifecycle (pricing, payment, ETA) bhi? (Aam taur par scope ko nearby + matching tak rakho.)
- Read pattern: top-K nearest drivers chahiye ya fixed-radius ke saare?
- Global system hai ya single-region? (Geo-sharding ka decision yahin se aata hai.)
- Accuracy vs freshness: kitni purani location acceptable hai?

## Capacity Estimate

Back-of-the-envelope — arithmetic dikhana zaroori hai, sirf numbers nahi.

**Assumptions:**
- Active drivers (online at peak): **1,000,000** (1M).
- Riders DAU: **100,000,000** (100M); peak concurrent ride requests low compared to driver writes.

**Write QPS (location updates — the dominant load):**
- Har driver location bheje har **4 seconds**.
- Write QPS = `1,000,000 drivers / 4 s` = **250,000 writes/sec** (250K QPS). Yahi system ka asli bottleneck hai — location ingest write-heavy hai.

**Read QPS (nearby + matching):**
- Maan lo peak par **1M ride requests/hour**.
- Read QPS = `1,000,000 / 3600 s` ≈ **278 req/sec** base; har request ke peeche kuch internal nearby lookups + retries, to round up to **~1-2K QPS**. Note: reads << writes here.

**Storage:**
- Active "current location" state: per driver ~`driverId(8B) + lat(8B) + lng(8B) + ts(8B) + status(4B)` ≈ **40 bytes**, round to ~100 B with overhead.
- Live state = `1M × 100 B` = **100 MB** — chhota, isliye in-memory store (Redis) mein comfortably fit ho jaata hai.
- Trip history / location trail (for analytics, persisted): `250K writes/sec × 100 B × 86400 s` ≈ **2.16 TB/day** ≈ **~788 TB/year** raw. Isko cheap object store / time-series DB mein archive karo, hot path mein nahi.

**Bandwidth (ingest):**
- `250,000 writes/sec × 100 B` = **25 MB/sec** ≈ **200 Mbps** of location ingest. Manageable, lekin connection overhead (TLS, headers) isse kaafi badha deta hai — isliye persistent connections / batching matter karta hai.

Takeaway: **write-heavy ingest (250K QPS)** is the headline number; live state is tiny (100 MB) so it lives in memory; persisted trail is huge (TB/year) so it goes to cold storage.

## API Design

Key endpoints (REST-style; production mein gRPC + persistent connection for the driver heartbeat):

```
# Driver bhejta hai — high frequency
POST /v1/drivers/{driverId}/location
  body: { lat, lng, ts, status }   # status: AVAILABLE | ON_TRIP | OFFLINE
  -> 200 OK (ack only)

# Rider nearby drivers dekhta hai
GET  /v1/drivers/nearby?lat={lat}&lng={lng}&radiusKm={r}&limit={k}
  -> 200 { drivers: [{ driverId, lat, lng, etaSec, distanceM }] }

# Rider ride request karta hai (matching trigger)
POST /v1/rides
  body: { riderId, pickupLat, pickupLng, dropLat, dropLng }
  -> 202 { rideId, status: "MATCHING" }   # async; result via push/poll

# Match status / live trip tracking
GET  /v1/rides/{rideId}
  -> 200 { rideId, status, driverId?, driverLat?, driverLng?, etaSec? }
```

Note: location update **ack-only** rakho (no heavy response) kyunki ye 250K QPS hit karta hai. Matching ko **async (202 Accepted)** rakho — synchronous block mat karo, kyunki match karne mein nearby search + lock + confirm involved hai.

## High-Level Architecture

Components aur request flow:

1. **API Gateway / Load Balancer** — driver heartbeats aur rider requests ko geo-region ke hisaab se route karta hai.
2. **Location Ingest Service** — driver location writes (250K QPS) accept karta hai, lightweight rakha jaata hai. Ye write ko do jagah bhejta hai:
   - **Location Store (Redis with geospatial index)** — current location, hot path read ke liye.
   - **Kafka (location-updates topic)** — durable async stream; isse downstream consumers (trip history persist, analytics, ETA models) feed hote hain bina ingest ko slow kiye.
3. **Geo / Nearby Service** — rider ke `(lat, lng)` ke around nearby available drivers query karta hai (geo-index ke against), distance/ETA compute karta hai, top-K return karta hai.
4. **Matching Service** — ride request leta hai → Nearby Service se candidates → ek driver ko **lock/claim** karta hai (taaki double-booking na ho) → driver ko offer bhejta hai → accept hone par ride confirm.
5. **Trip Service** — confirmed trip ki live location relay karta hai rider aur driver ke beech (often via WebSocket/long-poll).
6. **Notification / Push** — driver ko ride offer, rider ko "driver assigned" push.

**Read flow:** Rider → Gateway → Nearby Service → Location Store (geo-query) → top-K drivers back.
**Write flow:** Driver → Gateway → Location Ingest → (Redis geo-index + Kafka).
**Match flow:** Rider → Matching Service → Nearby candidates → atomic claim → confirm → notify both.

## Data Model

Do alag stores, do alag access patterns:

**1. Live driver location — Redis (in-memory, NoSQL).**

| Field | Type | Note |
|---|---|---|
| driverId | string | key |
| lat, lng | float | current position |
| status | enum | AVAILABLE / ON_TRIP / OFFLINE |
| updatedAt | epoch ms | freshness / TTL |

Redis `GEOADD` / `GEOSEARCH` (internally a sorted set keyed by **geohash score**) deta hai `O(log N)` radius queries directly. Per-region key (e.g. `geo:drivers:{cityShard}`) rakho. TTL ~10-15 sec set karo taaki stale/disconnected drivers index se apne aap nikal jaayein.

**Why NoSQL/in-memory here:** location data **high-write, ephemeral, eventually-consistent** hai aur strong relational guarantees ki zaroorat nahi. A relational DB 250K writes/sec sustain karke per-row update karega to it becomes the bottleneck. Redis geo-index gives spatial query + speed.

**2. Rides / trips — relational (SQL, e.g. Postgres) + history in object store.**

| Field | Note |
|---|---|
| rideId (PK) | |
| riderId, driverId | FKs |
| status | MATCHING / CONFIRMED / ON_TRIP / DONE / CANCELLED |
| pickup/drop lat,lng | |
| createdAt, confirmedAt | |

**Why SQL here:** ride/booking ek **transactional entity** hai — ek driver ko ek rider ke saath atomically claim karna, state transitions, billing — yeh sab ACID maangte hain. Double-booking avoid karne ke liye transactional guarantee chahiye. Raw location trail (TB/year) ko Postgres mein nahi, **time-series / object store** (S3, Cassandra) mein archive karo.

## Deep Dives

### 1. Geospatial indexing — Geohash vs Quadtree vs S2

Nearby query ka core problem: "is point ke paas kaun se drivers hain?" Naive `WHERE dist(p, driver) < r` over all drivers = `O(N)` scan = dead at 1M drivers. Solution: **spatial index**.

- **Geohash:** lat/lng ko ek base-32 string mein encode karo jahan **shared prefix = spatial proximity**. Nearby = same/adjacent prefix buckets dekho. Redis `GEOSEARCH` internally geohash use karta hai — yahi simplest production choice. Gotcha: geohash cell boundary par do paas wale points alag prefix mein gir sakte hain, isliye **neighbouring cells** bhi query karo (8 surrounding + center).
- **Quadtree:** space ko recursively 4 quadrants mein todo; dense areas (downtown) deeper subdivide hote hain → adaptive density handling. In-memory tree, great for skewed distributions, lekin rebalance/maintenance cost.
- **S2 (Google) / H3 (Uber):** sphere ko hierarchical cells mein todte hain (S2 = square-ish, H3 = hexagons). Uber actually **H3** use karta hai — hexagons ke neighbours equidistant hote hain (squares ke corners issue avoid). Production-grade choice.

Interview default: **geohash + Redis** se start karo, phir density skew aaye to **H3/quadtree** pe upgrade discuss karo.

### 2. Handling the 250K QPS write firehose

Har driver har 4s location bhejta hai — yeh dominant load hai. Mitigations:
- **Decouple ingest from persistence** via Kafka: Redis ko sirf latest location se update karo (overwrite, no append), durable history Kafka → consumers handle karein. Ingest service stays thin.
- **Batch / coalesce:** ek driver ke multiple updates ke beech sirf latest matter karta hai (current location), isliye overwrite semantics — no need to store every point hot.
- **Geo-sharding:** location store ko **city/region ke hisaab se shard** karo. Mumbai ke drivers Mumbai shard pe, Delhi ke Delhi pe. Ek shard sirf apne region ka write+read handle karta hai → horizontal scale, aur nearby query bhi same shard ke andar resolve hoti hai (cross-shard usually not needed since rider+driver same city).

### 3. Matching without double-booking

Race condition: do riders ek hi driver ko simultaneously claim kar lein. Mitigation:
- Matching Service nearby candidates leke ek driver ko **atomically claim** kare — e.g. Redis `SETNX driver:lock:{driverId}` ya DB row-level lock / conditional update (`UPDATE ... WHERE status='AVAILABLE'`). Sirf jeetne wala request hi driver ko offer bhejta hai.
- Driver ke accept/decline ya timeout par lock release. Decline → next candidate. Ye ensures ek driver kabhi ek se zyada active offer/ride mein nahi.

## Bottlenecks & Tradeoffs

- **Write firehose (250K QPS):** single Redis instance choke karega. **Mitigation:** geo-sharding (per-city Redis), Kafka offload for persistence. Tradeoff: cross-region riders (rare) ko handle karne mein complexity.
- **Hot regions / skew:** downtown Manhattan par drivers density bahut zyada → ek shard overloaded jabki rural shard idle. **Mitigation:** adaptive indexing (quadtree/H3 cells split density se), ya dynamic sub-sharding hot cities ke liye. Tradeoff: more moving parts, rebalancing cost.
- **Stale locations:** eventual consistency ka matlab dikhaye gaye driver shayad ab move ho chuke. **Mitigation:** short TTL (10-15s) on geo-entries + ETA recompute at match time. Tradeoff: TTL bahut chhota → genuine drivers gir jaate hain index se; bahut bada → stale matches.
- **Geohash boundary problem:** cell edge par paas wale drivers miss ho sakte hain. **Mitigation:** center + 8 neighbour cells query karo (ya H3 ring). Tradeoff: thoda zyada read work per query.
- **Consistency vs availability:** ride matching path par availability prefer karo (AP-leaning) for nearby reads, lekin **booking/claim par strong consistency** (single source of truth + lock) — warna double-booking. Classic split: reads eventual, the claim transactional.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_uber_nearby.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_uber_nearby.md) — `sysd-buddy quiz scaffold design-uber-nearby` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update design-uber-nearby --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — geo-index ring, driver location ingest flow, aur nearby query + matching ka interactive diagram.
