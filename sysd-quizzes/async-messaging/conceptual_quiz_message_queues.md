# Message Queues — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update message-queues --quiz-score N/M` -->

## Q1 (warm-up)
Message queue kya hai, aur ye producer aur consumer ke beech kya problem solve karta hai? One line definition do aur main benefit batao.

**Ideal answer:**
- Message queue ek intermediary buffer hai jisme producer messages enqueue karta hai aur consumer baad mein dequeue/process karta hai.
- Core benefit: **decoupling** — producer aur consumer ko time (async) aur speed mein alag kar deta hai; producer ko consumer ke ready hone ka wait nahi karna padta.
- Bonus points: buffering/load-leveling (bursts absorb), fault isolation (consumer down hone par producer affected nahi).

## Q2 (core)
"Competing consumers" model ke saath, jab ek consumer message process karta hai to ack–visibility timeout lifecycle kaise kaam karta hai? Batao ek message produce hone se delete hone tak ka path.

**Ideal answer:**
- Producer message ko queue/broker pe enqueue karta hai; broker use store karta hai (durable hone par disk pe persist).
- Consumer message receive/poll karta hai; broker us message ko temporarily **invisible** (visibility timeout / in-flight) kar deta hai taaki koi aur consumer use simultaneously na uthaye.
- Competing consumers: ek message **sirf ek** consumer ko jaata hai (kaam baant liya), broadcast nahi.
- Successful processing ke baad consumer **ack** bhejta hai → broker message ko delete karta hai.
- Agar consumer crash/ack nahi karta, visibility timeout expire hone par message wapas visible ho jaata hai aur redeliver hota hai (at-least-once).

## Q3 (tradeoff)
Traditional message queue (jaise RabbitMQ ya SQS) aur ek log-based system (jaise Kafka) ke beech key differences kya hain? Kab kaunsa choose karoge?

**Ideal answer:**
- Traditional queue: message ack hone par **delete** ho jaata hai; broker delivery track karta hai; per-message ack/retry/DLQ; competing consumers se simple work distribution.
- Kafka log: **append-only log**, messages retention period (jaise 7 days) tak rehte hain; consumers apna **offset** track karte hain; multiple consumer groups same data ko independently consume/**replay** kar sakte hain; partitions se high throughput.
- Choose queue (RabbitMQ/SQS): simple task distribution, per-message ack, DLQ, lower operational complexity.
- Choose Kafka: high throughput, event replay/reprocessing, multiple independent consumers same stream pe, event sourcing / streaming pipelines.
- Trade-off mention: Kafka mein ordering per-partition guaranteed; queue mein standard mode aksar best-effort ordering.

## Q4 (gotcha)
Ek interviewer kehta hai "main message queue use karunga taaki exactly-once delivery aur guaranteed ordering mile." Is statement mein kya galat hai, aur design mein iska kya implication hai?

**Ideal answer:**
- **Exactly-once misconception:** Most production queues **at-least-once** deti hain — ack kho sakta hai ya consumer crash kar sakta hai, to message **duplicate** ho sakta hai. True exactly-once distributed systems mein practically achievable nahi (best case "effectively once" via dedup/idempotency).
- Implication: consumers ko **idempotent** banao (jaise `order_id`/dedup key pe check), warna double charge/double email jaisa bug.
- **Ordering misconception:** Standard SQS aur multi-partition Kafka **global ordering guarantee nahi** karte. Strict order chahiye to FIFO queue / single partition / message group, jo **throughput cap** kar deta hai (serial processing).
- Bonus: visibility timeout < processing time ho to duplicates badhte hain; DLQ + max-retry se poison messages handle karo.

## Q5 (applied)
Ek flash-sale e-commerce system design kar rahe ho jahan peak pe 50,000 orders/min aate hain, par downstream order-processing DB sirf ~5,000 orders/min handle kar sakta hai. Message queue yahan kaise fit hota hai, aur kya design decisions loge?

**Ideal answer:**
- **Load leveling:** API layer order ko queue pe enqueue kare aur user ko turant ack de (order received). Queue 50k/min burst absorb karti hai jabki consumers steady ~5k/min (or jitna scale karein) drain karte hain — DB overload se bachta hai.
- **Decoupling:** Web tier aur order-processing tier alag scale; spike pe web tier crash nahi karta.
- **Scaling consumers:** Competing consumers / worker pool add karke throughput badhao; ideally consumers ko 50k/min tak scale karo taaki backlog drain ho (queue sustained imbalance ke liye nahi, sirf temporary burst ke liye).
- **Idempotency:** at-least-once delivery, isliye `order_id` pe dedup taaki duplicate order na bane.
- **DLQ + retries:** fail hone wale orders DLQ mein, manual replay/inspect.
- **Monitoring:** queue depth / backlog age monitor karo; agar permanently badh raha hai to consumers scale ya rate-limit producers (backpressure).
- Bonus: ordering agar zaroori (jaise per-user) to FIFO/message-group-key (user id) use karo, samajhte hue throughput trade-off.
