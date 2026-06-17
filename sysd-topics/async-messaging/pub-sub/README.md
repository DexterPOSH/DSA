# Pub/Sub

**Track:** Building Blocks
**Category:** Async & Messaging

## What It Is

Pub/Sub ek messaging pattern hai jisme publishers messages ko ek named channel (topic) pe bhejte hain bina ye jaane ki kaun consume karega, aur subscribers us topic se messages receive karte hain — yaani sender aur receiver ek broker ke through fully decoupled rehte hain.

## Real-World Analogy

Socho ek YouTube channel hai. Creator (publisher) ek naya video upload karta hai — usko ye nahi pata ki kaun-kaun log dekhenge, kitne log dekhenge, ya kab dekhenge. Wo bas video "publish" kar deta hai us channel (topic) pe.

Dusri taraf, jitne bhi log us channel ko "subscribe" kiye hue hain (subscribers), sabko notification mil jaati hai aur sab apni-apni marzi se, apne time pe video dekh lete hain. Ek subscriber video dekhe ya na dekhe, isse baaki subscribers ya creator ko koi farak nahi padta. Naya subscriber kal aata hai to wo bhi same channel se future videos paa lega.

Yahi Pub/Sub ka core idea hai: creator (publisher) aur viewers (subscribers) ek-dusre ko directly nahi jaante — beech mein YouTube (the broker/topic) sab handle karta hai. Ek se zyada viewer same video paate hain (fan-out), aur dono sides independently scale karte hain.

## How It Works

1. **Topic banana:** Sabse pehle ek **topic** (ya channel) define hota hai, jaise `order.placed` ya `user.signup`. Ye ek named logical channel hai jiske through messages flow karte hain. Topic ko aksar partitions mein divide kiya jaata hai parallelism ke liye (jaise Kafka mein ek topic ke 12 partitions).

2. **Publisher message bhejta hai:** Producer ek message (typically chhota payload, ~1 KB se kuch KB tak) us topic pe publish karta hai broker ko. Publisher ko sirf topic ka naam pata hota hai — kaun subscribe kiya hua hai, kitne subscribers hain, ye bilkul nahi pata. Ek modern broker (Kafka) ek single cluster pe millions of messages/sec sustain kar sakta hai, aur publish-side p99 latency typically single-digit se low double-digit ms hoti hai.

3. **Broker store/route karta hai:** Broker (Kafka, Google Pub/Sub, AWS SNS/SQS, RabbitMQ) message ko receive karta hai. Log-based brokers (Kafka) message ko ek **append-only commit log** (partition) mein durably likh dete hain aur usko retention period tak rakhte hain (default jaise 7 days, ya size-based jaise 1 TB per partition). Queue/push-based brokers (RabbitMQ, SNS) message ko subscribers tak deliver hote hi (ya ack ke baad) discard kar dete hain.

4. **Fan-out to subscribers:** Ek hi message multiple independent subscribers tak pahunchta hai. Agar 3 alag services us topic ko subscribe kiye hain (jaise email-service, analytics-service, inventory-service), to teeno ko message ki **apni-apni copy** milti hai. Ye Pub/Sub ka defining feature hai — ek publish, multiple deliveries.

5. **Delivery model — push vs pull:**
   - **Pull (Kafka):** Subscriber broker se messages khud poll karta hai aur apna **offset** (last read position) track karta hai. Isse subscriber apni speed pe consume karta hai (backpressure naturally handle).
   - **Push (SNS, webhooks):** Broker message ko subscriber ke endpoint pe actively deliver karta hai.

6. **Consumer groups & scaling:** Ek logical subscriber ko kai instances mein scale karte hain ek **consumer group** se. Kafka mein topic ke partitions group ke consumers ke beech baant diye jaate hain — jaise 12 partitions + 4 consumers = har consumer ko 3 partitions. Iska matlab ek consumer group ka parallelism partition count se bounded hota hai (12 partitions = max 12 useful consumers in that group).

7. **Acknowledgement & offset commit:** Subscriber message process karne ke baad broker ko **ack** bhejta hai (ya offset commit karta hai). Agar ack nahi aaya (consumer crash), broker message redeliver karta hai — yahi at-least-once delivery ki neenv hai.

## Tradeoffs & Variants

- **Pub/Sub vs Point-to-Point Queue:** Ek plain queue mein har message ko **exactly ek** consumer process karta hai (work distribution / load balancing). Pub/Sub mein har message **saare** interested subscribers ko jaata hai (fan-out / broadcast). Interviewer aksar yahi clarify karwaata hai: "do you want each message handled once, or by everyone?" Kafka dono kar sakta hai — single consumer group = queue-like, multiple groups = pub/sub-like.

- **Log-based (Kafka) vs Push-based (RabbitMQ/SNS):** Log-based broker messages ko retain karta hai → naya subscriber **history se replay** kar sakta hai, aur offset-based consumption deterministic hota hai. Cost: storage, aur consumer ko apna offset manage karna padta hai. Push/queue-based broker simpler hai, message consume hote hi gayab — replay nahi, lekin lightweight aur low retention overhead.

- **Delivery guarantees:** **At-most-once** (fire-and-forget, fast par message drop ho sakta hai), **at-least-once** (default in most systems, par duplicates possible → consumers ko **idempotent** banana padta hai), **exactly-once** (Kafka transactions/idempotent producer se achievable but mehnga aur scope-limited). Interviewer ka classic probe: "at-least-once means you WILL get duplicates — how do you dedupe?"

- **Ordering:** Global ordering across a topic generally guarantee nahi hoti. Kafka **per-partition** ordering deta hai. Agar tumhe related events in-order chahiye (jaise ek hi user ke events), to **same partition key** use karo (jaise `userId`) taaki wo ek partition pe land karein. Tradeoff: strong ordering = limited parallelism.

- **Retention & replay vs storage cost:** Lambi retention (jaise 30 days) powerful hai — reprocessing, new consumers, debugging — par disk cost badhta hai. Short retention sasta par message jaldi gayab.

## When To Use It

- **Event-driven microservices:** Jab ek event pe kai downstream services ko react karna ho — `order.placed` → payment, inventory, email, analytics — sab independently. (LinkedIn, Uber, Netflix sab Kafka-heavy hain.)
- **Decoupling producers from consumers:** Jab tum nahi chahte ki producer downstream consumers ke availability/speed pe block ho. Producer publish karke aage badh jaata hai.
- **Fan-out / broadcast:** Ek event ko N subscribers tak pahunchana (notifications, cache invalidation across services).
- **Stream processing & data pipelines:** Kafka + Flink/Spark Streaming — clickstreams, logs, metrics ingest karke real-time process karna.
- **Buffering / load leveling:** Spike absorb karne ke liye — producer burst kare to broker buffer kare, consumer steady rate pe drain kare.
- **Real systems:** Apache Kafka (LinkedIn-origin), Google Cloud Pub/Sub, AWS SNS+SQS, Azure Event Hubs/Service Bus, RabbitMQ, Redis Pub/Sub (ephemeral, no persistence).

## Common Interview Gotchas

- **Pub/Sub ≠ guaranteed delivery by default:** Plain Redis Pub/Sub fire-and-forget hai — agar subscriber offline hai to message **kho jaata hai**, koi persistence nahi. Log mat lagao ki har Pub/Sub durable hai. Durability chahiye to Kafka jaisa persistent log-based broker chahiye. Ye distinction interview mein clearly batao.

- **"Exactly-once" ka myth:** Network ke paar true exactly-once delivery practically impossible hai (two generals problem). Jo systems "exactly-once" claim karte hain wo aksar at-least-once delivery + idempotent processing / dedup ka combo hote hain. Safe answer: "main at-least-once use karunga aur consumers ko idempotent banaunga (dedup via message-id / idempotency key)."

- **Ordering across topic assume karna:** Common mistake — ye maan lena ki saare messages global order mein aayenge. Reality: ordering sirf **partition ke andar** guaranteed hai. Cross-partition / cross-topic ordering nahi. Agar order matters, partition key design karo.

- **Consumer parallelism ≠ unlimited:** Ye sochna ki ek consumer group mein jitne chaaho utne consumers add karke speed badha lenge — galat. Ek group ka parallelism **partition count se capped** hai. 12 partitions hain to 13th consumer idle baithega. Scale karne ke liye partition count badhana padta hai (jo apni complexity laata hai — re-partitioning, ordering reshuffle).

- **Backpressure ignore karna:** Agar consumer producer se slow hai aur retention chhoti hai, to messages retention window se baahar nikal kar **drop / lag** ho jaayenge. Slow consumer ki monitoring (consumer lag metric) zaroori hai. Push-based systems mein slow consumer broker pe buffer build kar sakta hai.

- **Broker ko "just a queue" samajhna:** Kafka ek distributed, replicated commit log hai — replication factor (jaise 3), leader/follower, ISR (in-sync replicas) sab durability aur availability ke liye matter karte hain. Single broker = single point of failure; production mein replicated cluster chahiye.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/async-messaging/conceptual_quiz_pub_sub.md`](../../../sysd-quizzes/async-messaging/conceptual_quiz_pub_sub.md) — `sysd-buddy quiz scaffold pub-sub` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update pub-sub --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — publisher → topic (with partitions) → broker → multiple subscribers / consumer groups ka fan-out diagram.
