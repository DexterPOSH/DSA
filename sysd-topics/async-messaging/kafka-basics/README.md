# Kafka Basics

**Track:** Building Blocks
**Category:** Async & Messaging

## What It Is

Apache Kafka ek distributed, append-only commit log hai jisme producers events ko partitioned, replicated topics mein likhte hain aur consumers unhe apni speed pe (pull-based) padhte hain, taaki systems durably aur asynchronously decouple ho sakein.

## Real-World Analogy

Socho ek bada newspaper distribution system hai. **Topic** ek newspaper hai, jaise "Times of India". Lekin ek hi printing press se poora desh handle nahi hota, isliye us newspaper ki kai **partitions** (regional editions) hoti hain — Mumbai edition, Delhi edition, Chennai edition.

Har edition ek **append-only log** hai: aaj ka issue #5001, kal ka #5002 — naye issues sirf end mein add hote hain, purane kabhi edit nahi hote. Har issue ka ek fixed number hota hai jo kabhi change nahi hota — yahi **offset** hai.

**Producers** wo reporters hain jo stories likhke kisi specific edition mein daalte hain. Agar story pe "city = Mumbai" likha hai (the **key**), to wo hamesha Mumbai edition mein hi jaati hai — taaki ek city ki saari khabrein order mein ek hi jagah milein.

**Consumers** subscribers hain. Yahan twist hai: Kafka khabar padhne ke baad delete nahi karta. Newspaper ka pura backlog shelf pe pada rehta hai (**retention**, jaise 7 din). Har subscriber apna bookmark rakhta hai — "main issue #4990 tak padh chuka hoon" (the **consumer offset**). Ek hi edition ko 5 alag subscribers (analytics, billing, search-indexer) apne-apne bookmark se padh sakte hain, ek dusre ko disturb kiye bina. Yahi Kafka ka asli kamaal hai: ek baar likha, kai baar independently padha gaya.

## How It Works

1. **Topic aur partitions:** Ek topic ko hum N partitions mein todte hain (jaise 12 partitions). Har partition ek ordered, immutable, append-only sequence of records hai. **Ordering guarantee sirf ek partition ke andar hoti hai, poore topic mein nahi.** Zyada partitions = zyada parallelism, kyunki har partition independently consume ho sakti hai.

2. **Producer write path:** Producer ek record bhejta hai. Agar record ka **key** hai, to partition = `hash(key) % numPartitions` (default murmur2 hash) — same key hamesha same partition mein, isliye per-key ordering milti hai. Key na ho to records partitions pe round-robin / sticky-batching se spread hote hain. Producer records ko batch karta hai (default `linger.ms` thoda wait karke) — ek single produce request mein hazaaron records, jisse throughput millions of events/sec tak pahunch sakta hai.

3. **Offset:** Har record ko us partition ke andar ek monotonically increasing 64-bit number milta hai — offset 0, 1, 2, .... Ye partition ke andar globally unique aur permanent hai. Consumer ki poori bookkeeping bas "is partition ka konsa offset tak main padh chuka" — yahi hai.

4. **Storage aur retention:** Partition disk pe segment files ke roop mein store hoti hai. Kafka sequential disk writes aur OS page cache + zero-copy (`sendfile`) use karta hai, isliye disk-based hone ke bawajood latency single-digit milliseconds mein rehti hai. Records consume hone par delete nahi hote — wo retention policy pe expire hote hain (time-based jaise `retention.ms = 7 days`, ya size-based).

5. **Replication aka durability:** Har partition ka ek **leader** broker hota hai aur kuch **follower** replicas (replication factor, typically 3). Saare reads/writes leader pe jaate hain; followers leader se data copy karte hain. Jo replicas leader ke saath caught-up hain wo **ISR (In-Sync Replicas)** kehlaate hain. Leader mar jaaye to ek in-sync follower naya leader ban jaata hai — koi data loss nahi.

6. **Producer acks:** `acks=0` (fire and forget, fastest, lossy), `acks=1` (sirf leader ne likha — leader crash ho to thoda data loss possible), `acks=all` (leader + saari ISR ne likha — strongest durability, thodi zyada latency). Production durability ke liye `acks=all` + `min.insync.replicas=2` standard combo hai.

7. **Consumer groups — scaling:** Consumers ek **group** banate hain. Ek partition group ke andar sirf ek consumer ko assign hoti hai. To agar topic mein 12 partitions hain aur group mein 4 consumers, to har consumer ~3 partitions handle karta hai — kaam parallel ho jaata hai. **Isiliye max parallelism = partition count.** 12 partitions hain to 13th consumer idle baithega.

8. **Multiple groups, same data:** Alag consumer groups same topic ko independently padhte hain, har group ka apna offset. Group-A (real-time fraud) aur Group-B (data warehouse ETL) dono saari events dekhte hain — ye pub/sub fan-out deta hai.

9. **Offset commit:** Consumer periodically apna processed offset commit karta hai (internal `__consumer_offsets` topic mein). Restart/rebalance ke baad wahin se resume hota hai.

## Tradeoffs & Variants

- **Partition count — ulta nahi hota easily:** Zyada partitions → zyada parallelism aur throughput, lekin har partition broker pe file handles, memory, aur replication overhead leti hai; rebalances slow ho jaate hain aur end-to-end latency badh sakti hai. Bड़ी baat: **partitions sirf badhaye ja sakte hain, ghataye nahi**, aur partitions badhane se keyed records ki future placement badal jaati hai (per-key ordering toot sakti hai). Isliye capacity upfront soch ke decide karo.

- **acks aur durability vs latency:** `acks=all` + `min.insync.replicas=2` safest hai par har write ko replicas pe land karne ka wait — zyada latency. `acks=1` fast par leader failure pe in-flight data loss. Ye classic interview tradeoff hai.

- **Delivery semantics:** Default **at-least-once** (record duplicate ho sakta hai agar consumer crash kare commit se pehle). **At-most-once** offsets ko process se pehle commit karke (loss possible). **Exactly-once (EOS)** idempotent producer + transactions se milti hai, par overhead aur complexity badhti hai — zyadatar systems at-least-once + idempotent consumers (dedup on a key) prefer karte hain.

- **Ordering vs parallelism:** Strict global ordering chahiye to single partition use karo — par tab parallelism 1 ho jaati hai (throughput bottleneck). Practice mein per-key ordering (partition by key) chuna jaata hai, jo 99% use-cases ke liye kaafi hai.

- **Pull vs push:** Kafka pull-based hai — consumer apni speed se fetch karta hai. Isse slow consumers overwhelm nahi hote (no backpressure problem jaise push systems mein), aur batching natural hoti hai. Tradeoff: idle consumers thoda poll-latency add karte hain.

- **Kafka vs traditional queue (RabbitMQ/SQS):** Kafka log-based, replayable, high-throughput streaming ke liye; messages padhne par delete nahi hote. RabbitMQ/SQS task-queue semantics (ack karo to message gone), per-message routing, aur complex delivery patterns ke liye behtar. Kafka mein "replay last 3 days" trivial hai, traditional queue mein impossible.

## When To Use It

- **Event streaming / event sourcing:** Jab events ka durable, replayable log chahiye — har state change ek event. Real systems: LinkedIn (Kafka yahin bana tha, activity stream ke liye), Uber (trip/dispatch events).
- **Decoupling microservices:** Producer aur consumers ko independently scale/deploy karna — checkout service event likhta hai, billing/email/analytics asynchronously consume karte hain.
- **Log/metrics aggregation:** Hazaaron servers ke logs ek jagah pipe karke downstream (Elasticsearch, S3) tak pahunchana.
- **Stream processing backbone:** Kafka Streams / Apache Flink / Spark Streaming ke liye source-of-truth. Netflix real-time monitoring, fraud detection isi pattern pe.
- **CDC (Change Data Capture):** Database changes (via Debezium) ko Kafka mein stream karke downstream sync rakhna.
- **Buffer for traffic spikes:** Spike absorb karne ka shock-absorber — producer burst likhe, consumer apni steady speed se drain kare.

Pattern recognition for interviews: jab bhi "high throughput", "replay", "multiple independent consumers of same data", "durable async decoupling", ya "ordered event log" sunai de — Kafka strong fit hai.

## Common Interview Gotchas

- **"Kafka ek message queue hai" — adhoora:** Kafka ek **distributed log** hai, traditional queue nahi. Message consume hone par delete nahi hota; consumer offset aage badhta hai. Isiliye replay, multiple independent consumer groups, aur time-travel possible hai — jo plain queue mein nahi.

- **Ordering global nahi hoti:** Sabse common galti. **Ordering sirf partition ke andar guaranteed hai.** Agar pure topic ka global order chahiye to single partition (= no parallelism) chahiye. Real answer: partition by key taaki related events (same user/order) ordered rahein.

- **Consumer count > partition count = waste:** Ek partition group ke andar sirf ek consumer ko jaati hai. 12 partitions, 20 consumers → 8 consumers idle. Max useful consumers = partition count. Interviewer aksar yahi poochta hai "scaling ki limit kya hai?".

- **Exactly-once ko galat samajhna:** Kafka default at-least-once hai, exactly-once magically nahi milta. EOS specific producer idempotence + transactions ke saath, ek hi Kafka-to-Kafka boundary pe milti hai — external side-effects (DB write, email) ke saath still careful idempotency chahiye.

- **`acks` ko replication factor samajh lena:** `acks` producer-side acknowledgment level hai (kitne replicas confirm karein), replication factor topic-level config hai (kitne replicas exist karte hain). `acks=all` ka matlab "all ISR", not "all replicas". `min.insync.replicas` decide karta hai durability floor.

- **Retention = consumption nahi:** Records retention window tak rehte hain chahe consume ho ya na ho. Slow consumer agar retention se peeche reh jaaye to data lose kar sakta hai (offset out of range) — ye "consumer lag" ka khatra hai, monitor karna zaroori.

- **Zyada partitions hamesha better nahi:** Bahut zyada partitions → broker memory pressure, lambe rebalances, aur badhi hui latency. Sweet spot capacity planning ka kaam hai, blind "1000 partitions daal do" nahi.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/async-messaging/conceptual_quiz_kafka_basics.md`](../../../sysd-quizzes/async-messaging/conceptual_quiz_kafka_basics.md) — `sysd-buddy quiz scaffold kafka-basics` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update kafka-basics --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — topic/partitions, offsets, producer-to-partition keying, aur consumer-group-to-partition assignment ka interactive diagram.
