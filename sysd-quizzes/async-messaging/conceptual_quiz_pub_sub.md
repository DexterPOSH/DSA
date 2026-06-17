# Pub/Sub — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update pub-sub --quiz-score N/M` -->

## Q1 (warm-up)
Pub/Sub pattern kya hai? Ek-do line mein define karo, aur batao publisher aur subscriber ka relationship kaisa hota hai.

**Ideal answer:**
- Pub/Sub ek messaging pattern hai jisme publishers messages ko ek named **topic/channel** pe bhejte hain, aur subscribers us topic se messages receive karte hain.
- Key point: publisher aur subscriber **decoupled** hote hain — publisher ko nahi pata kaun/kitne subscribers hain.
- Ek **broker** beech mein routing/delivery handle karta hai.
- Bonus: many-to-many — ek publish multiple subscribers tak (fan-out).

## Q2 (core)
Kafka jaise log-based broker mein ek message publish hone se lekar multiple consumers tak pahunchne tak kya-kya hota hai? Partitions, offset, aur consumer groups ka role bhi batao.

**Ideal answer:**
- Publisher message ko topic pe bhejta hai; topic **partitions** mein divided hota hai (parallelism ke liye).
- Broker message ko ek **append-only commit log** (partition) mein durably persist karta hai, retention period tak rakhta hai.
- Har consumer apna **offset** (last read position) track karta hai — pull-based consumption.
- **Fan-out:** har independent subscriber (consumer group) ko message ki apni copy milti hai.
- **Consumer group:** ek group ke andar partitions consumers ke beech baant diye jaate hain → parallelism, but partition-count se bounded.
- Bonus: ack/offset-commit ke baad hi message "consumed" maana jaata hai; crash pe redelivery.

## Q3 (tradeoff)
Point-to-point queue aur Pub/Sub mein kya difference hai? Aur ek hi Kafka cluster dono behaviours kaise de sakta hai?

**Ideal answer:**
- **Queue (point-to-point):** har message **exactly ek** consumer process karta hai → work distribution / load balancing.
- **Pub/Sub:** har message **saare** interested subscribers ko jaata hai → broadcast / fan-out.
- Decision criteria: "message ko ek baar handle karna hai ya sabko?"
- Kafka: **single consumer group** = queue-like (partitions group ke andar bante hain, ek message ek consumer ko); **multiple consumer groups** = pub/sub-like (har group ko full copy).
- Bonus: log-based (replay possible) vs push/queue-based (consume hote hi gayab) ka mention.

## Q4 (gotcha)
"Pub/Sub hamesha exactly-once aur durable delivery deta hai" — is statement mein kya galat hai? Real systems mein delivery guarantees kaise kaam karte hain?

**Ideal answer:**
- **Durability myth:** sab Pub/Sub durable nahi — jaise Redis Pub/Sub fire-and-forget hai, subscriber offline = message kho gaya. Durability ke liye persistent log-based broker (Kafka) chahiye.
- **Exactly-once myth:** network ke paar true exactly-once practically impossible; most systems **at-least-once** dete hain.
- At-least-once = **duplicates possible** → consumers ko **idempotent** banao (dedup via message-id / idempotency key).
- "Exactly-once" jo claim hota hai wo aksar at-least-once + idempotent processing/dedup ka combo hai (Kafka transactions limited scope).
- Bonus: at-most-once (fast, drop possible) bhi ek option hai.

## Q5 (applied)
Tumhe ek e-commerce system design karna hai jahan ek `order.placed` event pe payment, inventory, email, aur analytics — chaaron services ko react karna hai. Tum Pub/Sub kaise use karoge? Ordering aur scaling ke kaunse decisions lene padenge?

**Ideal answer:**
- Ek `order.placed` **topic** banao; order-service publish kare. Chaaron services **alag consumer groups** ke roop mein subscribe karein → fan-out, har service ko apni copy.
- **Decoupling:** order-service downstream services ke availability/speed pe block nahi hoga.
- **Ordering:** agar per-order/per-user ordering chahiye, **partition key** = `orderId`/`userId` use karo taaki related events same partition pe land karein (Kafka per-partition ordering).
- **Scaling:** har service apne consumer group ko partition-count tak scale kar sakti hai; throughput ke liye partition count plan karo.
- **Delivery:** at-least-once maano → consumers idempotent (jaise payment double-charge na ho, dedup by orderId).
- Bonus: retention set karo replay/new-consumer ke liye; consumer **lag** monitor karo backpressure ke liye.
