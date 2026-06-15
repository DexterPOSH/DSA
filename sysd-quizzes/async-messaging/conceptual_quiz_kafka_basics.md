# Kafka Basics — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update kafka-basics --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines, what is Kafka and how is it fundamentally different from a traditional message queue like RabbitMQ or SQS?

**Ideal answer:**
- Kafka is a distributed, durable, append-only commit log — events are written to partitioned, replicated topics and consumed by pull-based consumers.
- Key difference: in a traditional queue, a message is deleted/removed once acknowledged by a consumer; in Kafka the record is NOT deleted on consumption — it stays until the retention window expires.
- Consequence: Kafka supports replay, multiple independent consumer groups reading the same data, and time-travel; a plain queue does not. Consumers track their own offset rather than messages being destroyed.

## Q2 (core)
A topic has a key on each record. Walk through what happens from the moment a producer sends a record to the moment a consumer in a group reads it. Mention partitions, keys, offsets, and consumer groups.

**Ideal answer:**
- Producer picks a partition: with a key, `partition = hash(key) % numPartitions` (murmur2 by default), so the same key always lands in the same partition → per-key ordering. Without a key, records are spread round-robin / sticky.
- The record is appended to that partition's append-only log and assigned a monotonically increasing offset (0,1,2,...) unique and permanent within that partition.
- Durability: write goes to the partition leader broker; followers (replicas) copy it; with `acks=all` the leader waits for all in-sync replicas (ISR) before acknowledging.
- Consumption: each partition is assigned to exactly one consumer within a consumer group; the consumer pulls records and periodically commits its processed offset (to `__consumer_offsets`) so it can resume after restart/rebalance.
- Bonus: a different consumer group reads the same partitions independently with its own offsets (fan-out / pub-sub).

## Q3 (tradeoff)
Your team is choosing the number of partitions for a new topic and the producer `acks` setting. What are the tradeoffs on each, and what would you generally recommend for a high-durability, high-throughput system?

**Ideal answer:**
- Partition count: more partitions → more parallelism (max consumers in a group = partition count) and throughput, BUT more broker file handles/memory, slower rebalances, and potentially higher end-to-end latency. Partitions can only be increased, not decreased, and increasing them changes future keyed-record placement (can break per-key ordering). So plan capacity upfront.
- `acks`: `acks=0` fire-and-forget (fastest, lossy), `acks=1` leader-only (leader crash → possible loss), `acks=all` leader + all ISR (strongest durability, higher latency).
- Recommendation: `acks=all` with `min.insync.replicas=2` (and replication factor 3) for durability; pick partition count from target throughput / desired consumer parallelism, erring on a reasonable number rather than blindly huge.
- Should articulate the core durability-vs-latency and parallelism-vs-overhead tradeoffs.

## Q4 (gotcha)
A candidate claims: "Kafka guarantees global ordering of all messages in a topic, and if I add more consumers to my group I'll always get more throughput." What's wrong with both statements?

**Ideal answer:**
- Ordering is guaranteed ONLY within a single partition, not across the whole topic. Global ordering requires a single partition, which kills parallelism. The practical approach is to partition by key so related events (same user/order) stay ordered.
- Adding consumers helps only up to the partition count: within a consumer group, each partition is assigned to exactly one consumer. With 12 partitions and 20 consumers, 8 consumers sit idle. Max useful parallelism = number of partitions.
- Strong answers also note: to scale beyond partition count you must add partitions (which has its own caveats), not just consumers.

## Q5 (applied)
You're designing an e-commerce checkout system. When an order is placed, billing, email notifications, inventory updates, and an analytics warehouse all need to react. Would you use Kafka here, and how would you set it up? Also call out one delivery-semantics concern.

**Ideal answer:**
- Yes, Kafka is a strong fit: it decouples the checkout producer from many independent downstream consumers, lets each scale/deploy independently, absorbs traffic spikes as a buffer, and is durable/replayable.
- Design: an `orders` topic; producer keys records by `order_id` (or `user_id`) so all events for one order stay ordered in one partition. Multiple partitions for parallelism.
- Each downstream concern is its own consumer group (billing group, email group, inventory group, analytics group) — all read the full stream independently with their own offsets (fan-out).
- Delivery-semantics concern: Kafka is at-least-once by default, so records can be processed more than once (e.g., consumer crashes before committing offset). Consumers must be idempotent — e.g., dedup on `order_id` / use an idempotency key — so billing doesn't charge twice or emails aren't sent twice. (Bonus: mention exactly-once is possible via idempotent producer + transactions but adds overhead, especially with external side-effects.)
