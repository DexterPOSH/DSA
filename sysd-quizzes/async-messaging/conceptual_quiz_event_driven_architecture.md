# Event-Driven Architecture — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update event-driven-architecture --quiz-score N/M` -->

## Q1 (warm-up)
What is Event-Driven Architecture, and how does an "event" differ from a "command"?

**Ideal answer:**
- EDA: services communicate by producing/consuming **events** via a message broker instead of calling each other directly; interaction is **asynchronous** and **loosely coupled** — producer doesn't know who the consumers are.
- An **event** is an immutable **fact about something that already happened** (past tense, e.g. `OrderPlaced`); the producer just announces it.
- A **command** is an **instruction telling a specific service to do something** (e.g. `PlaceOrder`), directed at a known recipient.
- Key distinction: events = "this happened, react if you care" (no expectation of a specific action); commands = "you, do this".

## Q2 (core)
Walk through what happens from an event being produced to being processed in a log-based broker like Kafka. Mention partitions, consumer groups, and offsets.

**Ideal answer:**
- Producer **publishes** an event to a **topic**; the topic is split into **partitions** (an append-only, ordered log on disk), and the **partition key** decides which partition the event lands in.
- Broker **durably persists** the event; it stays available even if consumers are down (backlog builds up, producer is not blocked).
- Consumers subscribe via **consumer groups**: different groups each get their own copy of the stream (**pub/sub fan-out**); within one group, partitions are divided among members so each event is processed by **one** consumer in that group (work-queue).
- Each consumer tracks its position with an **offset** that it commits; after a crash it **resumes from the last committed offset**.
- Parallelism is bounded by partition count — N partitions ⇒ at most N active consumers per group.
- Bonus: ack/offset-commit is the basis of **at-least-once** delivery (uncommitted ⇒ redelivered).

## Q3 (tradeoff)
What delivery guarantee do most event systems give by default, and what does that force you to do in your consumers? Contrast with exactly-once.

**Ideal answer:**
- Default real-world guarantee is **at-least-once**: retries (after network failures/timeouts) can cause **duplicate** delivery.
- Therefore consumers must be **idempotent** — processing the same event twice must not corrupt state (e.g. dedup by `eventId`/idempotency key, upserts instead of blind increments).
- **Exactly-once** is achievable (Kafka idempotent producer + transactions, or dedup-based effective-once) but adds latency, complexity, and overhead.
- Practical interview stance: assume at-least-once + design idempotent consumers, rather than relying on exactly-once.
- Bonus: also mention **DLQ** for poison messages and **retries with backoff**.

## Q4 (gotcha)
A candidate claims their event system "guarantees that all events for a user are processed in order." Why is this often wrong, and how would you actually achieve per-entity ordering?

**Ideal answer:**
- Log-based brokers only guarantee ordering **per partition**, not globally across the topic.
- If a user's events get spread across **different partitions**, they can be processed **out of order** (different consumers, different rates).
- Fix: use the entity's id (e.g. `userId`) as the **partition key** so all of that user's events route to the **same partition**, preserving order for that user.
- Trade-off to mention: a skewed/high-traffic key can create a **hot partition** (uneven load); also adding partitions later changes key→partition mapping.
- Misconception named: ordering is not free or global.

## Q5 (applied)
You're designing the checkout flow for an e-commerce site. When would you choose EDA, when would you NOT, and how would you handle a consumer that keeps failing on certain messages?

**Ideal answer:**
- **Use EDA** for the post-order fan-out: one `OrderPlaced` event drives inventory, email/notification, analytics, fraud-check, loyalty — each reacts independently; new consumers can be added without changing the order service. Also good for absorbing **bursty load** (broker as buffer / load leveling) and **decoupling teams**.
- **Don't use EDA** for synchronous, immediate-response needs — e.g. "is this payment authorized right now?" or "is this username available?" — where the caller needs an answer before proceeding and **read-after-write/strong consistency** matters; use synchronous REST/gRPC there.
- Acknowledge EDA implies **eventual consistency** (downstream updates lag by seconds).
- Failing consumer handling: **retry with exponential backoff**; after max retries route the message to a **Dead Letter Queue (DLQ)** so the pipeline isn't blocked; **monitor consumer lag** and alert; investigate/replay DLQ messages later.
- Bonus: mention choreography vs orchestration (e.g. a **Saga** with orchestrator) for the multi-step transactional flow and compensating actions on failure.
