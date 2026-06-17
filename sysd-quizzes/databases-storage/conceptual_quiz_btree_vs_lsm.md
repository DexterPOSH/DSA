# B-Tree vs LSM-Tree — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update btree-vs-lsm --quiz-score N/M` -->

## Q1 (warm-up)
In one or two sentences, define a B-Tree and an LSM-Tree as storage engines, and state which one is read-optimized and which is write-optimized.

**Ideal answer:**
- B-Tree: balanced tree of fixed-size sorted pages, data updated **in-place** in its sorted position; **read-optimized**.
- LSM-Tree (Log-Structured Merge-Tree): writes buffered in an in-memory **memtable**, flushed **sequentially** to immutable on-disk **SSTables**, merged later by **compaction**; **write-optimized**.
- Bonus: mentions that B-Tree does work at write time, LSM defers/batches it.

## Q2 (core)
Walk through what happens, step by step, when an LSM-Tree handles (a) a write and (b) a read of a single key. Mention how reads are kept fast.

**Ideal answer:**
- Write: append to on-disk **WAL** (durability) → insert into in-memory sorted **memtable**; when memtable hits a size threshold it is flushed as an **immutable, sequentially-written SSTable**; a fresh memtable starts.
- Read: check **memtable** first, then SSTables from **newest to oldest** (latest value wins).
- Fast reads via: **Bloom filters** per SSTable (skip files that definitely lack the key — no false negatives), **sparse index + block cache** to jump to the right block.
- **Compaction** runs in the background, merge-sorting SSTables to remove duplicates/tombstones and bound the number of files to search.

## Q3 (tradeoff)
B-Trees and LSM-Trees differ fundamentally in the I/O pattern of their writes. Explain the difference and why it historically mattered. Then explain the read-amplification trade-off that LSM pays in return.

**Ideal answer:**
- B-Tree writes are **random I/O** — data must be written where it belongs in sorted order (find leaf page, update in place, possibly split). LSM writes are **sequential I/O** — always append (WAL + sequential SSTable flush), sorting deferred to compaction.
- Why it mattered: sequential writes are dramatically faster on **spinning disks** (no seek), and on **SSDs** are friendlier for IOPS and wear. This was the original motivation for LSM.
- The trade-off: LSM pays **read amplification** — a key may live in any of several SSTables, so a lookup can touch multiple files (mitigated, not eliminated, by Bloom filters). It also pays **space amplification** (un-compacted duplicates/tombstones). B-Tree read amplification is bounded by tree height (~3-4 page reads).
- Strong answer also notes B-Tree gives more **predictable tail latency**, while LSM can spike on compaction.

## Q4 (gotcha)
A candidate claims: "LSM-Trees are strictly better because they have lower write amplification and are always faster." What's wrong with this statement?

**Ideal answer:**
- "Always faster" is false: LSM only optimizes the **write** path; reads can be **slower** (multiple SSTables), while B-Tree reads are bounded and often faster — so it's workload-dependent.
- "Lower write amplification" is often **backwards**: LSM frequently has **higher** write amplification because **compaction rewrites data repeatedly**. LSM's real advantage is that writes are **sequential and batched** (high throughput, low write latency), not that fewer bytes are written.
- Additional correct points: LSM **deletes are tombstones** (a delete is itself a write; space is reclaimed only at compaction), and **compaction is a hidden cost** (CPU/IO, p99/p999 latency spikes). Both engines use a WAL, so durability isn't a differentiator.

## Q5 (applied)
You're designing storage for two services: (1) a metrics/time-series ingestion pipeline taking millions of writes per second, and (2) an OLTP user-profile store with frequent point lookups, updates, and range queries needing predictable low latency. Which engine for each, and why? Name a real database for each.

**Ideal answer:**
- (1) Metrics/time-series → **LSM-Tree**: write-heavy, append-style, high ingest; sequential writes give the throughput; read latency variability is acceptable. Real systems: **Cassandra, RocksDB, ScyllaDB, HBase, InfluxDB, Bigtable**.
- (2) OLTP profile store → **B-Tree**: read-heavy/balanced, needs **bounded, predictable read latency**, strong point lookups + range scans, in-place updates. Real systems: **PostgreSQL, MySQL/InnoDB, Oracle, SQL Server, SQLite**.
- Strong answer justifies via amplification trade-offs (write vs read/space amplification, sequential vs random I/O, compaction-induced tail-latency risk) rather than just naming engines, and recognizes the pattern keywords ("millions of writes/sec" → LSM; "predictable low-latency reads + updates + range queries" → B-Tree).
