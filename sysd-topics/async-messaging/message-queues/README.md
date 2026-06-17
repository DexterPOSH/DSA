# Message Queues

**Track:** Building Blocks
**Category:** Async & Messaging

## What It Is

Message queue ek aisa intermediary buffer hai jisme ek producer messages bhejta hai aur ek consumer unhe baad mein process karta hai, taaki dono components asynchronously aur decoupled rehkar apni-apni speed pe kaam kar sakein.

## Real-World Analogy

Socho ek busy restaurant ka kitchen hai. Waiter (producer) order leke seedha chef (consumer) ke paas khade hokar wait nahi karta jab tak dish ban na jaaye — wo order parchi ek **order rail / spike** (the queue) pe tang deta hai aur turant agle table pe chala jaata hai. Chef jab free hota hai, rail se agli parchi uthata hai aur cook karta hai.

Iska faayda: agar lunch rush mein orders chef ke cooking speed se zyada tezi se aate hain, to parchiyan rail pe jama hoti rehti hain (queue buffers the burst) — koi order kho nahi jaata, aur waiter blocked nahi hota. Agar ek chef beemar ho gaya, doosra chef usi rail se parchiyan uthana shuru kar deta hai (consumer replaceable hai). Aur ek parchi ko ek hi chef uthata hai taaki ek dish do baar na bane. Yahi message queue ka core kamaal hai: producer aur consumer ko time aur speed dono mein decouple kar dena.

## How It Works

1. **Produce (enqueue):** Producer ek message (jaise `{order_id: 8821, action: "send_email"}`) queue ko bhejta hai. Message typically ek broker (RabbitMQ, AWS SQS, ActiveMQ) pe store hota hai. Ek message chhota hota hai — usually kuch hundred bytes se kuch KB tak; SQS ka max single message 256 KB hai.

2. **Buffer & durability:** Broker message ko hold karta hai. Agar durable configure kiya hai to message disk pe persist hota hai taaki broker crash hone pe bhi na khoye. Ek queue mein backlog millions of messages tak ja sakta hai jab consumers slow hon — yahi "buffering the burst" hai.

3. **Consume (dequeue):** Consumer queue se message poll/receive karta hai aur process karta hai. Classic queue model **competing consumers** hai: agar 5 consumers ek hi queue se padh rahe hain, to har message **sirf ek** consumer ko jaata hai (kaam baant liya). Yahi horizontal scaling deta hai — consumers add karo to throughput badhta hai.

4. **Acknowledge (ack):** Message process hone ke baad consumer broker ko **ack** bhejta hai, tab broker us message ko queue se delete karta hai. Agar consumer crash ho gaya bina ack kiye, broker visibility timeout (jaise SQS mein default 30s) ke baad message ko wapas visible kar deta hai taaki koi aur consumer use uthaye — isse at-least-once delivery milti hai.

5. **Retry & Dead Letter Queue (DLQ):** Agar ek message baar-baar fail hota hai (jaise 5 attempts), broker use ek **dead letter queue** mein bhej deta hai taaki wo "poison message" baaki processing ko block na kare; baad mein use inspect/replay kar sakte ho.

Numbers ka feel: ek single SQS queue easily tens of thousands of messages/sec handle kar leti hai; processing latency end-to-end usually single-digit se low tens of milliseconds, par real point latency nahi — burst absorption aur decoupling hai.

## Tradeoffs & Variants

- **Queue vs Pub/Sub (point-to-point vs fan-out):** Pure queue mein ek message ek hi consumer ko jaata hai (work distribution). Pub/Sub topic (Kafka, SNS, Google Pub/Sub) mein ek message **saare** subscribers ko jaata hai (fan-out / event broadcast). Interviewer aksar poochega "queue ya topic?" — answer depends: task ko ek baar process karna hai → queue; ek event ko multiple independent systems ko notify karna hai → pub/sub.

- **Delivery guarantees:** *At-most-once* (fire and forget, message kho sakta hai, fastest), *at-least-once* (default for most queues — message kabhi-kabhi duplicate ho sakta hai, isliye consumer **idempotent** hona chahiye), *exactly-once* (mehnga aur often "effectively once" via dedup keys + idempotency, truly exactly-once distributed systems mein nearly impossible).

- **Ordering:** Standard queues (SQS standard) ordering **guarantee nahi** karti — best-effort. Strict FIFO chahiye to FIFO queue (SQS FIFO, ~3000 msg/s with batching) ya Kafka partition use karo, par ordering aksar throughput cap kar deti hai (per-partition / per-message-group serial processing).

- **Push vs pull:** Pull (SQS — consumer poll karta hai) backpressure-friendly hai (consumer apni speed se leta hai). Push (RabbitMQ broker consumer ko deliver karta hai) lower latency par consumer overload ka risk, isliye prefetch limits chahiye.

- **Queue (RabbitMQ/SQS) vs Log (Kafka):** Traditional queue message ack hone pe delete kar deti hai. Kafka ek **append-only log** hai — messages retention period (jaise 7 days) tak rehte hain, consumers apna **offset** track karte hain, multiple consumer groups same data ko independently replay kar sakte hain. Replay aur high throughput chahiye → Kafka; simple task distribution + per-message ack/DLQ → RabbitMQ/SQS.

## When To Use It

- **Decoupling slow/unreliable work:** User signup pe welcome email bhejna — API turant respond kare, email kaam queue pe daal do. Agar email service down hai, request fail nahi hoti.
- **Burst / spike absorption (load leveling):** Flash sale pe 50k orders/min aaye par DB sirf 5k/min handle kar sakta hai → queue backlog absorb karti hai, consumers steady rate pe drain karte hain.
- **Background / long-running jobs:** Video transcoding, PDF generation, image thumbnails — synchronous request mein nahi karna, queue + worker pool.
- **Fan-out workflows (pub/sub variant):** Ek order placed event → inventory service, shipping service, analytics, email — sab independently react karein.
- **Real systems:** Uber/Lyft ride events, Instagram fan-out, banking transaction pipelines. Tools: **AWS SQS/SNS, RabbitMQ, Kafka, Google Pub/Sub, ActiveMQ, Redis Streams**.

## Common Interview Gotchas

- **"Exactly-once delivery milti hai" — galat:** Most production queues **at-least-once** deti hain. Network mein ack kho sakta hai, consumer crash kar sakta hai → message redeliver hota hai. Iska matlab consumers ko **idempotent** banao (jaise `order_id` pe dedup), warna double charge / double email ho jaayega. Ye sabse common interview trap hai.

- **Ordering by default assume karna:** Standard SQS aur multi-partition Kafka mein global order **guaranteed nahi** hai. Agar ordering chahiye, explicitly FIFO queue ya single partition / message group bolo, aur samjho ki isse throughput girta hai. Mat assume karo ki messages waise hi order mein process honge jaise bheje.

- **Queue ko "infinite buffer" maan lena:** Agar producers consistently consumers se tez hain, to queue **permanently grow** karegi (unbounded backlog) — ye bug hai, feature nahi. Fix: consumers scale karo, ya backpressure / rate limiting lagao. Queue sirf **temporary** bursts ke liye buffer hai, sustained imbalance ke liye nahi.

- **Poison message backlog block kar deta hai:** Ek message jo hamesha fail karta hai, agar wo head pe atak gaya (especially FIFO mein) to poori queue ruk sakti hai. **DLQ + max-retry** config zaroori hai.

- **Queue vs Pub/Sub confuse karna:** Kai log dono ko ek bol dete hain. Yaad rakho: queue = ek message ek consumer (competing consumers); pub/sub = ek message saare subscribers (fan-out).

- **Visibility timeout galat tune karna:** Agar timeout processing time se chhota hai, message redeliver ho jaata hai jab original consumer abhi bhi kaam kar raha hota hai → duplicate work. Timeout ko worst-case processing time se thoda zyada rakho.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/async-messaging/conceptual_quiz_message_queues.md`](../../../sysd-quizzes/async-messaging/conceptual_quiz_message_queues.md) — `sysd-buddy quiz scaffold message-queues` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update message-queues --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — producer → queue → competing consumers, ack/retry, aur DLQ flow ka interactive diagram.
