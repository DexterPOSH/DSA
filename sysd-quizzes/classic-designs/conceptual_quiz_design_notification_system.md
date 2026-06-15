# Design a Notification System — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-notification-system --quiz-score N/M` -->

## Q1 (warm-up)
You're asked to "design a notification system." Before drawing any boxes, what clarifying questions do you ask, and what are the key functional vs non-functional requirements you'd lock down?

**Ideal answer:**
- Clarifying questions: which channels (push/SMS/email/in-app)? transactional vs promotional/bulk? delivery guarantee (at-least-once vs exactly-once)? ordering needed? opt-out/preferences & rate limiting? expected scale (DAU, peak QPS)?
- Functional: single ingestion API for sender services, multi-channel (push/SMS/email), user preferences + DND/opt-out, templating, rate limiting, deduplication.
- Non-functional: high availability + durability (no drops, especially OTP), low latency for transactional / eventual for bulk, scalability for spikes, decoupling of senders from providers.
- Bonus signal: noting transactional and bulk have very different SLAs and should be handled differently.

## Q2 (core)
Walk me through a back-of-the-envelope capacity estimate for 10M DAU. Compute write QPS, yearly storage for notification logs, and tell me where the real bottleneck is.

**Ideal answer:**
- Assumptions stated: 10M DAU, ~5 notifications/user/day → 50M/day.
- Write QPS: 50M / 86400 ≈ 580 QPS average; with ~5x peak factor → ~3K QPS peak.
- Storage: ~500 bytes/record × 50M/day = 25 GB/day; × 365 ≈ ~9 TB/year; ×3 replication ≈ ~27 TB.
- Reads (prefs/templates) mostly served from cache, not DB.
- Key insight: the bottleneck is NOT the DB — it's downstream provider throughput + queue depth / fan-out. That's why the design centers on a queue + worker fleet.

## Q3 (data-model / API)
For the data layer you propose SQL for user preferences but NoSQL (Cassandra) for the notification log. Justify each choice based on access patterns. Also: why does the ingestion API return 202 Accepted instead of doing the work synchronously?

**Ideal answer:**
- Preferences = SQL: low write volume, strong consistency (opt-out is compliance-binding), relational queries, small dataset. Consistency > raw throughput here.
- Notification log = NoSQL wide-column (Cassandra): write-heavy (50M/day, append-only, never updated), time-series access (partition by user_id, cluster by created_at), needs horizontal write scale that single-node SQL can't give.
- Principle: choice is access-pattern-driven, not a blanket preference.
- 202 Accepted: ingestion just validates + enqueues to the message queue and returns immediately; actual delivery is async via workers. This decouples senders from provider latency/downtime and absorbs spikes — synchronous provider calls would block/cascade-fail under load.

## Q4 (tradeoff)
Why put a message queue (Kafka) between the notification service and the providers at all? And given you can't realistically get exactly-once delivery, what guarantee do you choose and how do you stop users from getting duplicate notifications?

**Ideal answer:**
- Queue rationale: decouples producer from consumer → (a) absorbs traffic spikes (queue depth grows, nothing dropped), (b) enables retries (re-enqueue failed messages), (c) priority isolation via separate topics (transactional vs bulk) so OTP isn't stuck behind marketing.
- Guarantee: at-least-once (never lose a message, tolerate duplicates) — exactly-once is impractical/expensive in distributed delivery.
- Dedup: idempotency via a dedup_key checked in Redis (SETNX with TTL) before the provider call; if already seen, skip. Mention DLQ for poison messages and retry with exponential backoff.
- Trade-off awareness: dedup TTL too long = memory cost, too short = late duplicate slips through.

## Q5 (applied — scaling bottleneck + mitigation)
At scale, name the dominant bottlenecks of this system and how you'd mitigate each. Specifically address a flaky third-party provider and a broadcast/celebrity fan-out that must notify millions at once.

**Ideal answer:**
- Provider bottleneck: APNs/SES have their own rate limits & downtime. Mitigations: queue buffering, per-provider rate limiting, circuit breaker (open on error spike, hold traffic, half-open recovery), and multi-provider failover (primary + fallback).
- Broadcast/celebrity fan-out: a single event notifying millions causes a write/fan-out storm. Mitigations: a dedicated bulk pipeline with batching on separate low-priority topics so transactional latency isn't degraded.
- Other valid points: queue backpressure → autoscale consumers, shed/deprioritize bulk first, alert on consumer lag; preference staleness from caching → invalidate cache on opt-out + short TTL to avoid compliance violations; hot partitions handled via partitioning strategy.
