# Backpressure — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update backpressure --quiz-score N/M` -->

## Q1 (warm-up)
In one or two sentences, what is backpressure, and what core problem does it solve?

**Ideal answer:** Backpressure is a flow-control mechanism where a slow consumer signals its upstream producer to slow down so the producer's rate matches the consumer's processing capacity. Key points the grader checks: (1) it's about producer/consumer rate mismatch; (2) the signal flows upstream (consumer -> producer), not downstream; (3) the problem it solves is unbounded buffering leading to memory exhaustion / OOM, latency blowup, or data loss; (4) the goal is to keep the system stable rather than letting the queue grow forever.

## Q2 (core)
Walk through the main strategies a system can use to apply backpressure when the consumer can't keep up. Name at least three.

**Ideal answer:** Should describe several of: (1) **Block/pause** — block the producer's `send()` when the bounded buffer is full (e.g. `BlockingQueue.put()`); lossless but stalls producer. (2) **Pull-based / demand signaling** — consumer requests `n` items and producer sends only that many (Reactive Streams `request(n)`, gRPC streaming flow control). (3) **Credit / sliding-window** — receiver advertises a window of how much it will accept (TCP receive window). (4) **Drop / load shedding** — discard new or old events when full (metrics, live video). Bonus: mention bounded buffer with high/low watermarks to trigger slow-down/resume, and that pressure propagates end-to-end through a chain of queues/services. Grader checks at least three distinct strategies with a correct one-line mechanic each.

## Q3 (tradeoff)
A fast service is receiving external traffic you cannot slow down, but it calls a slow downstream dependency. You can't block the inbound producer. What are your options and their tradeoffs?

**Ideal answer:** Since blocking the external producer isn't possible, the realistic responses are: (1) **Bounded buffer/queue** — absorb bursts, but it will fill if the net rate stays negative, adding latency (Little's Law) and eventually hitting its bound. (2) **Load shedding / drop** — reject or drop excess requests once the buffer is full (e.g. return HTTP 429), trading data loss for system stability and bounded latency. (3) **Rate-limit / reject at the edge** rather than blocking internally (internal blocking risks thread-pool exhaustion / cascading stall / deadlock). Mention lossless vs lossy choice depends on whether the data is critical (orders) vs droppable (telemetry). Grader checks: recognition that you must buffer-then-shed (not buffer forever), edge rejection over internal blocking, and the loss-vs-stability tradeoff.

## Q4 (gotcha)
A teammate says "we don't need backpressure, we'll just use a really big buffer." Why is this wrong, and how is backpressure different from rate limiting?

**Ideal answer:** A bigger (or unbounded) buffer only delays the problem: if the producer rate exceeds the consumer rate, the net fill rate is positive, so the buffer eventually fills regardless of size, causing OOM, and meanwhile latency keeps climbing (deeper queue = longer wait, Little's Law). The real fix is a bounded buffer plus an explicit upstream signal (or load shedding). On the second part: **rate limiting** is static/proactive — a fixed cap (e.g. 1000 req/sec) regardless of whether the consumer is idle or saturated; **backpressure** is dynamic/reactive — the signal is driven by actual consumer saturation. They're complementary, not the same. Grader checks: "big buffer just delays + still OOMs," latency growth, and the static-vs-dynamic distinction between rate limiting and backpressure.

## Q5 (applied)
Give a concrete system where backpressure is built in or essential, and explain how the signal propagates through it.

**Ideal answer:** Any valid real example with correct mechanics, e.g.: (1) **Kafka** — consumers are pull-based (`max.poll.records`, fetch sizing), so a slow consumer naturally fetches less; lag grows on the broker (durable) instead of crashing the consumer. (2) **Reactive Streams / Project Reactor / RxJava / Akka Streams** — `request(n)` demand signaling from subscriber to publisher. (3) **TCP flow control** — receiver's advertised receive window throttles the sender. (4) **Flink** — backpressure propagates operator-to-operator upstream to the source and is an observable metric. (5) **RabbitMQ** — consumer prefetch (`basic.qos`) limits unacked messages per worker. Grader checks: a real system named, the correct backpressure mechanism for it, and an explanation that the signal flows from the slow/downstream point back upstream toward the source (e.g. DB slow -> service slow -> queue fills -> upstream service throttled -> producer slows).
</content>
