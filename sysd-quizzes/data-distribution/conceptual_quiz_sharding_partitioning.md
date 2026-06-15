# Sharding & Partitioning — Conceptual Quiz

<!-- Agent (sysd-quiz skill): grade the user conversationally against each
     "Ideal answer" outline, then record the score with:
     `sysd-buddy progress update sharding-partitioning --quiz-score N/M` -->

## Q1 (warm-up)
What is sharding (a.k.a. horizontal partitioning), and what core scaling problem does it solve that read replicas cannot?

**Ideal answer:** Sharding ek bade dataset ko chhote independent chunks (shards/partitions) mein todkar alag-alag nodes pe rakhna hai; har shard apna slice of data + traffic handle karta hai. Key points the grader checks: (1) it splits *different* data across nodes (not copies); (2) it scales **writes and storage** horizontally past a single node's limits; (3) read replicas only scale **reads** (they hold a full copy), so they don't help when write throughput or total data size is the bottleneck.

## Q2 (core)
Walk through the three common partitioning strategies — range-based, hash-based, and directory-based. For each, give the main advantage and the main drawback.

**Ideal answer:** (1) **Range-based:** key ranges map to shards (e.g. user_id 1–1M → shard 0). Advantage: range/scan queries (`BETWEEN`) are efficient since neighbors sit together. Drawback: monotonic keys (auto-increment, timestamps) hammer the newest shard → hotspot. (2) **Hash-based:** `shard = hash(key) % N`. Advantage: even/uniform distribution. Drawback: range queries scatter across all shards, and plain `% N` remaps almost everything when N changes (mitigated by consistent hashing). (3) **Directory-based:** a lookup table maps key → shard. Advantage: maximum flexibility, easy rebalance, place any key anywhere. Drawback: extra lookup hop + the directory can become a SPOF/bottleneck.

## Q3 (tradeoff)
What properties make a good shard key, and why is choosing it the most important decision in a sharded design?

**Ideal answer:** A good shard key has (1) **high cardinality** — enough distinct values to spread data across many shards; (2) **even access distribution** — no single value carries a disproportionate share of traffic (avoids hotspots); (3) ideally **co-locates data needed together** in one shard so most queries are single-shard and transactions stay local. It's the most important decision because it determines load balance, hotspot behavior, and which queries are cheap (single-shard) vs expensive (scatter-gather); a wrong choice (e.g. low-cardinality `country`, or a monotonic timestamp) forces a full re-design and a painful live migration. Bonus: mention that changing the shard key later is very costly.

## Q4 (gotcha)
Someone says "sharding and replication are basically the same thing — both put data on multiple machines." Why is this wrong, and how do the two relate in a real system?

**Ideal answer:** They are different and complementary. **Replication** keeps **copies of the same data** on multiple nodes — it scales **reads** and provides **high availability / failover**. **Sharding** splits **different pieces of data** across nodes — it scales **writes and storage**. They solve different problems, so real systems use **both together**: data is split into shards, and each shard is itself replicated (e.g. a primary + replicas per shard) for availability. Grader also credits noting that replication alone can't relieve a write/storage bottleneck because every replica still holds the full dataset and all writes.

## Q5 (applied)
You're designing the message store for a Discord/Slack-style chat app expecting billions of messages and very high write volume. How would you shard it, what shard key would you pick, and what query would become expensive as a result?

**Ideal answer:** Shard the messages table by **channel_id** (or conversation/room id) — a high-cardinality key that co-locates all messages of one channel on one shard, so the dominant query ("load recent messages for this channel") is a fast single-shard read, and writes spread across channels. Replicate each shard for availability. Acknowledge the trade-off: queries that **cross the shard key become expensive** — e.g. full-text search across all of a user's messages, or "all messages by user X across every channel," require **scatter-gather** across shards (slow, tail-latency heavy). The standard fix is a separate secondary/denormalized index (e.g. an Elasticsearch index or a per-user index) rather than scanning the sharded primary store. Bonus points: mention consistent hashing / fixed logical partitions for predictable rebalancing, and that a hugely active channel can still be a hotspot (split further or cache). Real reference: Discord shards messages by channel on Cassandra.
