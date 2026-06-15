# Event-Driven Architecture

**Track:** Building Blocks
**Category:** Async & Messaging

## What It Is

Event-Driven Architecture (EDA) ek design style hai jisme services aapas mein direct call karne ke bajaye **events** (facts about something that already happened, jaise `OrderPlaced`) ko ek message broker pe emit karte hain, aur interested services un events ko asynchronously consume karke react karti hain — producer ko ye pata bhi nahi hota ki consumer kaun hai ya kitne hain.

## Real-World Analogy

Socho ek shaadi hai aur dulhe ke ghar pe baaja-band wale aa gaye. Jab band bajna shuru hota hai (the **event**: "baraat nikli"), to band wale kisi ek specific aadmi ko phone karke "tum aao" nahi bolte. Wo bas dhol bajaate hain — aur jisko bhi sunai deta hai, wo apne hisaab se react karta hai: koi naachne lagta hai, koi camera nikaal leta hai, koi paise lutaane lagta hai, aur halwai gulab jamun garam karne chala jaata hai.

Yahan band wale (**producer**) ko ye jaanne ki zaroorat hi nahi ki kitne log naachenge ya halwai kaun hai. Event "broadcast" ho gaya, aur har **consumer** ne apni zimmedaari independently nibha li. Agar kal ek naya cameraman (naya consumer) add ho jaaye, to band wale ko apna kaam badalna nahi padta — wo bhi bas dhol sunke kaam shuru kar dega. Yahi EDA ka core hai: **loose coupling** — producer aur consumer ek doosre ko jaane bina kaam karte hain, ek shared event ke through.

## How It Works

1. **Event produce hota hai:** Koi service jab kuch meaningful karti hai (jaise payment confirm hua), to wo ek **event** ek broker (Kafka, RabbitMQ, AWS SNS/SQS, ya Pulsar) pe publish karti hai. Event ek immutable fact hota hai — "ye ho chuka hai", command nahi ("ye karo"). Typical event payload chhota hota hai, ~200 bytes se 2 KB tak, with fields jaise `eventId`, `eventType`, `timestamp`, aur business data.

2. **Broker durably store karta hai:** Broker event ko disk pe persist karta hai aur consumers tak deliver karta hai. Kafka jaisa log-based broker events ko ek **partitioned append-only log** mein rakhta hai aur high throughput deta hai — ek well-tuned cluster easily **hundreds of thousands se millions of events/sec** handle kar leta hai, with produce latency typically **single-digit se ~10 ms** (acks=all ke saath thoda zyada).

3. **Consumers subscribe karte hain:** Ek ya zyada consumer services us event ko padhti hain. Do broad delivery models hote hain — **pub/sub** (har subscriber ko event ki apni copy milti hai, fan-out) aur **queue/work-queue** (ek group of workers load baant lete hain, ek message ek hi consumer process karta hai). Kafka mein dono ek saath: alag **consumer groups** fan-out dete hain, aur ek group ke andar partitions workers mein bant jaate hain.

4. **Async processing aur retries:** Consumer event ko apne pace pe process karta hai. Agar consumer down hai ya slow hai, to events broker mein wait karte hain (backlog/lag), producer block nahi hota. Fail hone pe consumer **retry** karta hai; baar-baar fail karne wale "poison" messages ek **Dead Letter Queue (DLQ)** mein bhej diye jaate hain taaki pipeline aage badhe.

5. **Offset / ack se progress track hota hai:** Kafka mein har consumer apna **offset** commit karta hai (kahaan tak padh liya). Crash ke baad wo wahin se resume karta hai. Queue-based brokers mein consumer message ko explicitly **ack** karta hai; bina ack ke message redeliver ho jaata hai — yahi at-least-once delivery ki foundation hai.

6. **Scale:** Throughput badhana ho to **partitions/consumers add karo**. Ek topic ke jitne partitions, utne parallel consumers ek group mein kaam kar sakte hain. 12 partitions matlab max 12 active consumers parallel — isse zyada consumers idle baith jaayenge.

## Tradeoffs & Variants

- **Loose coupling vs debugging pain:** EDA decoupling deta hai — services independently deploy/scale hoti hain. Lekin flow distributed ho jaata hai, to ek request ka end-to-end path follow karna mushkil hota hai. Iske liye **distributed tracing** (correlation IDs har event mein) almost mandatory hai.

- **Delivery semantics — at-least-once vs exactly-once:** Default real-world guarantee **at-least-once** hai (duplicates possible — network retry ke baad event do baar deliver ho sakta hai). Isliye consumers ko **idempotent** hona chahiye (same event do baar process karne pe result na bigde, jaise dedup via `eventId`). "Exactly-once" achievable hai (Kafka transactions / idempotent producer) par overhead aur complexity zyada — interview mein default assume karo at-least-once + idempotency.

- **Ordering:** Global ordering guarantee karna mehenga hai. Kafka sirf **per-partition** ordering deta hai. Agar ek user ke saare events order mein chahiye, to us user ke `userId` ko **partition key** banao taaki wo events ek hi partition mein jaayein. Trade: high-cardinality key se hot partitions ban sakte hain.

- **Choreography vs Orchestration:** **Choreography** mein har service event sunke khud react karti hai (no central brain) — maximum decoupling par overall workflow samajhna tough. **Orchestration** mein ek central orchestrator (jaise a Saga orchestrator, Temporal, AWS Step Functions) steps coordinate karta hai — clearer flow, par central dependency. Interviewer aksar poochta hai "kab kaunsa?".

- **Event payload — thin vs fat events:** **Thin event** sirf `orderId` bhejta hai (consumer phir details fetch karta hai) — chhota event, par extra read load aur coupling. **Fat event** poora order snapshot carry karta hai — self-contained par bada aur stale ho sakta hai. **Event-Carried State Transfer** fat events ka pattern hai.

- **Eventual consistency:** Async hone ki wajah se system **eventually consistent** hota hai, immediately consistent nahi. User ko "order placed" dikh gaya par downstream inventory update hone mein kuch seconds lag sakte hain.

## When To Use It

- **High fan-out / multiple reactions to one fact:** Jaise e-commerce mein `OrderPlaced` → inventory, email, analytics, fraud-check, loyalty points — sab parallel react karein bina order-service ko har naye consumer ke liye change kiye.
- **Decoupling teams/services:** Microservices jahan independent deploy aur scale chahiye. Real systems: **Uber** (trip events), **LinkedIn** (Kafka ka origin — activity/feed events), **Netflix** (Kafka-based pipelines), **DoorDash**.
- **Spiky / bursty load absorb karna:** Broker buffer banta hai — Black Friday traffic spike async queue mein absorb ho jaata hai, downstream apne pace pe drain karta hai (load leveling).
- **Stream processing & analytics:** Real-time clickstream, metrics, ETL pipelines (Kafka + Flink/Spark Streaming).
- **Audit log / event sourcing:** Append-only event log hi source of truth banta hai; state ko events replay karke rebuild kar sakte ho.
- **Kab AVOID karo:** Simple request/response jahan caller ko immediate answer chahiye (jaise "is this username available?") — wahan synchronous REST/gRPC behtar hai, EDA over-engineering hoga.

## Common Interview Gotchas

- **"Event" ≠ "Command":** Event ek fact hai jo ho chuka — `OrderPlaced` (past tense). Command ek instruction hai kisi ke liye — `PlaceOrder`. EDA events pe based hai; producer kisi ko order nahi deta, bas announce karta hai. Naming past-tense rakhna decoupling reinforce karta hai.

- **At-least-once ko exactly-once samajh lena:** Sabse common galti. Default delivery duplicate de sakti hai. Agar consumer idempotent nahi hai (jaise har event pe blindly "balance += 100"), to duplicate event se double charge ho jaayega. **Hamesha mention karo: consumers idempotent hone chahiye (dedup via eventId / idempotency key).**

- **Ordering free maan lena:** Log-based broker mein ordering sirf **per-partition** hoti hai, global nahi. Agar related events alag partitions mein chale gaye to out-of-order process ho sakte hain. Fix: meaningful partition key.

- **Broker ko "fire and forget, kabhi fail nahi hoga" maan lena:** Consumers fail karte hain, lag build hota hai, poison messages aate hain. **DLQ, retries with backoff, aur consumer lag monitoring** mention karna maturity dikhata hai. Lag = (latest offset − committed offset); growing lag = consumers can't keep up.

- **Synchronous mindset:** "Producer ne event bheja matlab kaam ho gaya" — nahi. EDA async hai, system **eventually consistent** hai. Agar interviewer immediate read-after-write consistency maange, to pure EDA wahan fit nahi.

- **Backpressure ignore karna:** Agar producer broker se bahut tez events daale aur consumers slow hon, to unbounded backlog ya memory pressure ban sakta hai. Bounded queues, consumer autoscaling, ya producer throttling ka zikr karo.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/async-messaging/conceptual_quiz_event_driven_architecture.md`](../../../sysd-quizzes/async-messaging/conceptual_quiz_event_driven_architecture.md) — `sysd-buddy quiz scaffold event-driven-architecture` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update event-driven-architecture --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — producer → broker → multiple consumers ka fan-out flow, partitions/offsets, aur DLQ ka interactive diagram.
