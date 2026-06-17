# Design a Distributed Key-Value Store — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-kv-store --quiz-score N/M` -->

## Q1 (warm-up)
You're asked to "design a distributed key-value store." Before drawing anything, what are the most important clarifying questions you'd ask, and which functional vs non-functional requirements would you lock down?

**Ideal answer:**
- Clarifying questions: consistency model (strong / eventual / tunable), read:write ratio, value size + total dataset size + growth, single-DC vs multi-region, point lookups only vs range/secondary indexes, latency SLA and durability (how many replicas must ack).
- Functional: `get` / `put` / `delete`, opaque values (< ~1 MB), data partitioned across many nodes, horizontal/incremental scaling.
- Non-functional: high availability ("always writable"), low latency (single-digit ms p99), scalability without full rehash, tunable consistency, partition tolerance, durability of acked writes.
- Strong signal: candidate explicitly notes that the consistency requirement is the biggest design driver and that availability is often prioritized over strong consistency for this class of system.

## Q2 (core)
Walk through the capacity estimate for ~100M DAU doing ~50 KV ops/day each, with ~10B stored items at ~1 KB value and replication factor 3. Show the arithmetic for QPS and storage.

**Ideal answer:**
- Ops/day: `100M * 50 = 5B ops/day`.
- Average QPS: `5e9 / 86,400 ≈ 58K QPS`; peak ≈ `2x ≈ ~116K QPS`.
- Split by ratio (e.g. 4:1 read:write): ~46K read QPS, ~12K write QPS average.
- Storage raw: per item ≈ key 50B + value ~1KB + metadata ~100B ≈ ~1.15 KB; `10e9 * 1.15KB ≈ 11.5 TB` raw.
- With `N=3` replication: `~34.5 TB`; with compaction/index/headroom overhead (~1.5x): `~50 TB` provisioned.
- Bonus: write replication multiplies intra-cluster bandwidth by N; rough node count sanity check (~20-30 nodes) shows the problem is genuinely distributed.

## Q3 (tradeoff)
Why use consistent hashing for partitioning instead of `hash(key) % N`? What problem do virtual nodes solve?

**Ideal answer:**
- `hash(key) % N` ties the assignment to node count; adding/removing a node changes the modulus so ~all keys remap → massive data movement (and cache stampede in a cache context).
- Consistent hashing maps keys and nodes onto a ring; a node change only remaps ~K/N keys (only the affected arc), rest untouched.
- Without virtual nodes, random placement gives uneven arcs → load imbalance / hot spots, and a removed node dumps all its keys onto a single successor.
- Virtual nodes (each physical node placed at ~100-256 ring points) smooth out load (law of large numbers), spread a failed node's keys across many successors, and let you give powerful nodes more vnodes for heterogeneous capacity.

## Q4 (gotcha)
Explain the N/R/W quorum knobs. What does `R + W > N` give you, and what's the catch that trips people up about "strong consistency" here?

**Ideal answer:**
- `N` = replicas per key, `W` = nodes that must ack a write, `R` = nodes that must respond to a read.
- `R + W > N` forces the read quorum and write quorum to overlap by at least one node, so a read is guaranteed to see the latest acked write → strong-ish (read-your-writes-ish) consistency. Example: `N=3, R=2, W=2` (`2+2 > 3`).
- `W=1` = fast writes but weak durability; `R=1` = fast reads but possible staleness.
- Gotcha: quorum overlap guarantees you read a node that *has* the latest write, but you still need versioning (vector clocks / version stamps) to identify which returned value is latest and to reconcile concurrent writes. Also, during a network partition you cannot have both full availability and strong consistency (CAP) — this is an AP-leaning system, so lowering R/W for availability reintroduces stale reads.
- Mentioning read-repair / hinted handoff as how replicas converge afterward is a plus.

## Q5 (applied)
At scale, name two concrete bottlenecks this design hits and how you'd mitigate each.

**Ideal answer:** (any two solid pairs)
- Hot keys / hot partitions: a single popular key overloads its replica-set → add a caching layer, key-splitting/suffix sharding, or request coalescing.
- LSM compaction & write amplification: background compaction causes I/O spikes hurting p99 → throttle compaction, tune leveled vs size-tiered strategy.
- Replication lag → stale reads under eventual consistency → read-repair, higher R, or sticky routing for read-your-writes.
- Tombstone buildup: deletes kept as tombstones (with GC grace period) to avoid resurrecting deleted data on lagging replicas → costs disk/read until compaction.
- Cluster rebalancing on node add/remove saturates the network → throttled, incremental streaming.
- Strong signal: candidate ties each bottleneck back to a specific component (storage engine, consistent-hashing ring, replication layer) rather than listing generic fixes.
