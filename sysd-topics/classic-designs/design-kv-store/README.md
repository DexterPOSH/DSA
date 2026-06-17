# Design a Distributed Key-Value Store

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Ek distributed key-value store design karna hai jo simple `get(key)` / `put(key, value)` operations expose karta hai, lekin data ko multiple machines pe partition aur replicate karke high availability, horizontal scalability, aur low latency deliver karta hai (jaise DynamoDB, Cassandra, ya Redis Cluster).

## Requirements & Scope

**Functional requirements:**

- `get(key)` aur `put(key, value)` — core API. Value ek opaque blob hai (store usko interpret nahi karta).
- `delete(key)` support karna.
- Values relatively chhoti (typically `< 1 MB`); ye object store nahi hai.
- Data multiple nodes pe distributed ho aur cluster horizontally scale kare (nodes add karne se capacity badhe).

**Non-functional requirements:**

- **High availability** — writes aur reads hamesha succeed hone chahiye, even jab kuch nodes down hon. Ye "always writable" property (jaise shopping cart) often consistency se zyada important hoti hai.
- **Low latency** — single-digit millisecond `p99` reads/writes.
- **Scalability** — incremental scaling, bina poore cluster ko rehash kiye.
- **Tunable consistency** — strong nahi, balki configurable: caller decide kare strong vs eventual chahiye.
- **Partition tolerance** — network split hone pe bhi system kaam karta rahe.
- **Durability** — acknowledged write data loss na ho (within replication guarantees).

**Clarifying questions interviewer se poochne layak:**

- Consistency model kya chahiye — strong, eventual, ya tunable? (Ye sabse bada design driver hai.)
- Read-heavy hai ya write-heavy? Read:write ratio kya hai?
- Average aur max value size? Total dataset size aur growth rate?
- Single data center ya multi-region / geo-replication?
- Range queries / secondary indexes chahiye, ya sirf point lookups? (Hum sirf point lookups assume kar rahe hain.)
- Latency SLA aur durability guarantee (kitne replica acknowledge karein)?

## Capacity Estimate

Maan lo ye ek large-scale store hai. Back-of-the-envelope:

- **DAU:** ~100 million daily active users.
- **Requests per user per day:** ~50 KV operations average.
- **Total ops/day:** `100M * 50 = 5 billion ops/day`.
- **Average QPS:** `5e9 / 86,400 s ≈ 57,870 ≈ 58K QPS` average. Peak ko `2x` maano → **~116K QPS peak**.
- **Read:write ratio:** maan lo `4:1` (read-heavy). To read QPS `≈ 46K`, write QPS `≈ 12K` (average).

**Storage:**

- Items: maano `10 billion` keys stored.
- Per item: key `~50 bytes` + value `~1 KB` + metadata (version/vector clock, TTL) `~100 bytes` ≈ `~1.15 KB`.
- Raw data: `10e9 * 1.15 KB ≈ 11.5 TB`.
- **Replication factor `N = 3`** → `11.5 TB * 3 ≈ 34.5 TB` ka usable footprint.
- Overhead (compaction, indexes, headroom) ke liye `~1.5x` → **~50 TB provisioned**.
- Yearly growth: agar `20%` keys/year add hon → `~2 billion` new keys → `~2.3 TB raw`, `~7 TB` after replication+overhead per year.

**Bandwidth:**

- Write ingress: `12K writes/s * 1.15 KB ≈ 13.8 MB/s` client-facing. Replication ke liye har write `N=3` baar travel karta hai internally → `~41 MB/s` intra-cluster write traffic.
- Read egress: `46K reads/s * 1.15 KB ≈ 53 MB/s` client-facing.
- Total network comfortably ek modern cluster ke andar fit ho jaata hai; storage aur QPS scaling main constraint hain.

**Node sizing:** agar ek node `~5 TB` SSD + `~10K QPS` handle kare, to `~50 TB / 5 TB = 10` nodes storage ke liye, par QPS+replication+headroom ke liye realistically **~20-30 nodes** chahiye. Ye sanity-check hai ki problem genuinely distributed hai.

## API Design

Client-facing API simple rehti hai; consistency knobs parameters mein expose hote hain:

```
put(key: string, value: bytes, opts?: { W?: int, ttl_seconds?: int }) -> { version }
get(key: string, opts?: { R?: int }) -> { value: bytes, version } | NotFound
delete(key: string, opts?: { W?: int }) -> { version }   // tombstone write
```

- `R` = read quorum (kitne replicas se read confirm karna hai), `W` = write quorum. Defaults cluster-level set hote hain (jaise `N=3, R=2, W=2`).
- `version` = vector clock ya version-stamp, jo client ko conflict reconciliation ke liye wapas milta hai (read-modify-write ke liye context).
- Internally nodes ek replication/membership API bhi expose karte hain (gossip, hinted handoff, read-repair), par interview ke liye client API yahi teen hain.

## High-Level Architecture

Ye ek **decentralized, peer-to-peer (Dynamo-style)** architecture hai — koi single master nahi, har node same role nibha sakta hai. Components:

1. **Coordinator node** — jis node pe client request aati hai wahi us request ka coordinator ban jaata hai. (Client smart ho to seedha responsible node ko hit karta hai; warna koi bhi node forward kar deta hai.)
2. **Partitioner (consistent hashing ring)** — `hash(key)` se ring pe position nikaalti hai; key ka owner = clockwise next node, aur uske baad ke `N-1` nodes replicas ban'te hain.
3. **Storage engine** — har node pe local persistence: typically ek **LSM-tree** (commit log + memtable + SSTables) write-heavy throughput ke liye.
4. **Replication + anti-entropy layer** — hinted handoff, read-repair, aur Merkle-tree based background sync.
5. **Membership & failure detection** — **gossip protocol** se nodes ek-doosre ka liveness aur ring topology share karte hain.

**Request flow (write):** client → coordinator → coordinator `hash(key)` se top-`N` replica nodes nikaalta hai → parallel mein sab ko write bhejta hai → jaise hi `W` acknowledgements aa jaate hain, client ko success return → baaki replicas async converge ho jaate hain (ya hinted handoff via).

**Request flow (read):** client → coordinator → `N` replicas se value maangta hai → `R` responses aane par latest version (vector clock se decide) return → agar replicas mein staleness mile to **read-repair** background mein purane replica ko update kar deta hai.

## Data Model

- **Logical model:** ek flat map `key -> (value, version, metadata)`. Koi relational schema, joins, ya range scans by default nahi.
- **Per-item fields:** `key` (partition key), `value` (opaque bytes), `version` (vector clock / timestamp), `ttl` (optional expiry), `tombstone` flag (deletes ke liye).
- **On-disk:** LSM-tree. Writes pehle ek append-only **commit log** (durability) aur in-memory **memtable** mein jaati hain; memtable bhar jaane par immutable **SSTable** ke roop mein disk pe flush hoti hai; background **compaction** SSTables merge karke purani versions/tombstones clean karta hai. Reads memtable + relevant SSTables check karte hain (Bloom filters se non-existent keys jaldi skip ho jaati hain).

**SQL vs NoSQL choice:** Yahan **NoSQL (key-value)** hi sahi hai. Reasons: (a) access pattern sirf point lookup by key hai — joins/transactions/range scans nahi chahiye, to RDBMS ki ACID machinery overhead hai; (b) hume horizontal scaling aur high availability chahiye, jo single-master SQL me mushkil hai jabki consistent-hashed KV me natural hai; (c) schema flexible (opaque value) hai. Agar requirement strong multi-key transactions ya rich queries ki hoti, tab SQL / NewSQL consider karte.

## Deep Dives

**1. Partitioning via Consistent Hashing (with virtual nodes).**
Data ko nodes pe baantne ke liye `hash(key)` ko ek circular ring pe map karte hain; key ka owner clockwise next node hota hai. **Naive `hash % N` mat use karo** — node add/remove hone par almost saari keys remap ho jaati hain (massive data movement). Consistent hashing me node change par sirf `~K/N` keys move hoti hain. **Virtual nodes** (har physical node ko ring pe `~100-256` points pe rakhna) se load even hota hai (no hot spots) aur heterogeneous capacity handle hoti hai (powerful node ko zyada vnodes).

**2. Replication + Tunable Consistency (quorums, N/R/W).**
Har key ko top-`N` clockwise nodes pe replicate karte hain (cross-rack/cross-AZ for fault isolation). Consistency ko quorum se tune karte hain: agar `R + W > N` → strong-ish consistency (read aur write quorum overlap karte hain, to latest write zaroor dikhega). `W = 1` → fast writes, weak durability; `R = 1` → fast reads, possible staleness. Common balanced config: `N=3, R=2, W=2` (`2+2 > 3`). Ye CAP me **AP**-leaning system hai jab `R`/`W` ko availability ke liye low rakha jaata hai.

**3. Failure handling: Hinted Handoff, Read-Repair, Merkle Trees.**
- **Hinted handoff:** agar ek target replica temporarily down ho, to coordinator write ko kisi healthy node pe "hint" ke saath store kar deta hai; node wapas aane par hint deliver ho jaata hai → write availability bani rehti hai.
- **Read-repair:** read ke waqt jab replicas me version mismatch mile, latest version se stale replicas ko foreground/background me update kar dete hain.
- **Merkle trees (anti-entropy):** replicas periodically apne data ke hash trees compare karke sirf divergent ranges sync karte hain — poora data compare kiye bina efficient reconciliation.
- **Conflict resolution:** concurrent writes ke liye **vector clocks** se causality track hoti hai; jo automatically resolve na ho usko client ko (ya last-write-wins timestamp se) reconcile karte hain.

## Bottlenecks & Tradeoffs

- **Hot keys / hot partitions:** ek single popular key ya skewed access poore ek replica-set ko overload kar sakta hai. Mitigation: hot keys ke liye extra caching layer, key-splitting (suffix sharding), ya request coalescing.
- **Consistency vs availability (CAP):** network partition me strong consistency aur availability dono nahi mil sakte. Tunable `R`/`W` se trade-off application pe chhod dete hain; default AP rakhte hain availability ke liye, par stale reads accept karne padte hain.
- **Compaction & write amplification:** LSM-tree me background compaction CPU/disk I/O spikes deta hai aur write amplification badhata hai, jo `p99` latency hurt kar sakta hai. Mitigation: compaction throttling, leveled vs size-tiered strategy tuning.
- **Replication lag → stale reads:** eventual consistency me ek replica purana data return kar sakta hai. Mitigation: read-repair, higher `R`, ya read-your-writes ke liye sticky routing.
- **Tombstone buildup:** deletes turant remove nahi hote (tombstones), warna doosre replicas pe deleted data "resurrect" ho jaata. Tombstones ko compaction tak rakhna padta hai (GC grace period), jo disk aur read cost badhata hai.
- **Cluster rebalancing:** node add/remove pe data movement network saturate kar sakta hai; throttled, incremental streaming chahiye.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_kv_store.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_kv_store.md) — `sysd-buddy quiz scaffold design-kv-store` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update design-kv-store --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — consistent-hashing ring, top-`N` replica placement, aur quorum read/write flow ka interactive diagram.
