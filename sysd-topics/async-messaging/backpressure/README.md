# Backpressure

**Track:** Building Blocks
**Category:** Async & Messaging

## What It Is

Backpressure ek flow-control mechanism hai jisme ek slow consumer apne upstream producer ko signal deta hai ki "thoda dheere bhej" — taaki producer ki rate consumer ki capacity se match ho jaaye aur system unbounded buffering ya memory crash se bach jaaye.

## Real-World Analogy

Socho ek restaurant ka kitchen hai. Waiters (producers) tezi se orders le aate hain aur ek single chef (consumer) un orders ko cook karta hai. Agar waiters 30 orders/min la rahe hain par chef sirf 10 orders/min bana sakta hai, to order tickets ka dher (queue) lagta jaayega. Do raaste hain: ya to tickets ka pile infinite badhta rahe (jab tak ticket-rail toot na jaaye — yaani memory blow up), ya chef bole "ruko, mera rail full hai, jab tak main 2-3 plate clear na karu naye order mat lao."

Ye dusra behaviour hi backpressure hai — consumer apni saturation ka signal upstream bhejta hai aur producer apne aap slow ho jaata hai. Agar waiter signal ignore kare aur tickets fekta rahe, to ya kitchen crash karega ya tickets floor pe gir ke lost ho jaayenge (data loss). Backpressure ka asli point yahi hai: pressure ko gracefully peeche tak propagate karna, na ki silently drop ya explode hone dena.

## How It Works

1. **Rate mismatch detect hota hai:** Producer `P` events generate kar raha hai, say 50,000 events/sec, aur consumer `C` sirf 10,000 events/sec process kar sakta hai (har event ~100ms downstream call leti hai with limited concurrency). Beech mein ek buffer/queue hai jiska size badhna shuru ho jaata hai — 40,000 events/sec ki net rate se queue fill ho rahi hai.

2. **Bounded buffer + watermark:** Buffer ko bounded rakha jaata hai, say capacity 100,000 events. High watermark (e.g. 80%) pe consumer ek "slow down" signal raise karta hai; low watermark (e.g. 30%) pe "resume" signal. Unbounded buffer ka matlab hota OOM crash, isliye bound hamesha hota hai.

3. **Signal upstream propagate hota hai — 4 common strategies:**
   - **Block / pause:** Producer ka `send()` block ho jaata hai jab buffer full hai (classic bounded `BlockingQueue.put()`). Synchronous backpressure — slowest path determine karta hai overall throughput.
   - **Pull-based (demand signaling):** Consumer batata hai "main `n=256` aur events le sakta hu," producer sirf utne hi bhejta hai. Reactive Streams (`request(n)`) aur gRPC streaming flow control isi pe based hain.
   - **TCP-style credit / sliding window:** Receiver advertises ek window (kitna data wo abhi accept karega). Sender window se zyada nahi bhejta jab tak ACK na aaye. Kafka consumer ka `max.poll.records` aur fetch sizing bhi conceptually pull + credit hai.
   - **Drop / shed:** Buffer full hone pe naye (ya purane) events drop kar do — load shedding. Latency-sensitive systems (metrics, live video) ismein old data drop karte hain kyunki stale data useless hai.

4. **Steady state:** Backpressure ke baad producer effectively `min(P_rate, C_rate)` = 10,000 events/sec pe settle ho jaata hai. Queue depth stable rehti hai (e.g. ~5,000-20,000), latency bounded rehti hai, aur memory flat rehti hai instead of monotonic growth.

5. **End-to-end propagation:** Real systems mein chain hoti hai — `P -> Q1 -> service A -> Q2 -> service B (DB)`. Agar DB slow hua, to B slow hota hai, Q2 bharti hai, A ko backpressure milti hai, A slow hota hai, Q1 bharti hai, aur pressure poora chain ke through producer tak pahuchti hai. Yahi "propagation" backpressure ka core hai.

## Tradeoffs & Variants

- **Buffering vs Blocking vs Dropping:** Teen fundamental responses hain jab consumer slow ho. **Buffer** karo (queue lagao) — latency badhti hai, memory consume hoti hai, par koi data loss nahi (jab tak bound hit na ho). **Block** karo producer ko — no loss, par producer stall hota hai aur ye upstream tak ripple kar sakta hai (head-of-line blocking). **Drop** karo — system responsive rehta hai, par data loss accept karna padta hai. Interviewer ye trade probe karta hai: "agar producer ko block nahi kar sakte (e.g. external traffic), to kya karoge?" — answer usually bounded buffer + load shedding.

- **Push vs Pull:** Push systems (producer apni marzi se bhejta hai) mein backpressure explicitly engineer karni padti hai. Pull systems (consumer demand karta hai — Kafka, Reactive Streams) mein backpressure naturally built-in hai kyunki consumer apni rate control karta hai. Pull simpler hai par har low-latency use case ke liye fit nahi.

- **Lossless vs Lossy backpressure:** Lossless (block/buffer) — financial transactions, orders, jahan har event critical hai. Lossy (drop/sample) — telemetry, metrics, live dashboards jahan freshness > completeness. Galat choice = ya to data loss ya to cascading stall.

- **Where to apply:** Backpressure ko system ke edge pe rate-limit / reject karna (e.g. HTTP 429, queue at the boundary) aksar internal blocking se behtar hota hai, kyunki internal blocking deadlock aur thread-pool exhaustion paida kar sakti hai.

## When To Use It

- **Streaming pipelines:** Kafka consumers, Flink, Spark Streaming — agar downstream slow hai to source se ingestion rate ko throttle karna. Flink mein backpressure ek first-class observable metric hai (operators ke beech).
- **Reactive systems:** Reactive Streams spec (Project Reactor, RxJava, Akka Streams) ka pura design backpressure ke around hai — `request(n)` demand signaling.
- **Network protocols:** TCP flow control (receive window) khud ek backpressure mechanism hai. gRPC/HTTP-2 streaming flow control bhi.
- **Message queues / async workers:** RabbitMQ consumer prefetch (`basic.qos`), SQS visibility + concurrency limits — taaki worker apni capacity se zyada na le.
- **Pattern recognition (interview):** Jab bhi "producer-consumer rate mismatch," "queue unbounded grow ho rahi," "OOM under load," ya "fast service calling slow downstream" jaisa cue mile — backpressure (+ bounded queue + load shedding) ka jawab banta hai.

## Common Interview Gotchas

- **"Bas ek bada buffer laga do" — galat:** Unbounded ya bahut bada buffer backpressure ka solution nahi hai; ye sirf problem ko delay karta hai. Buffer eventually fill hoga (kyunki net rate negative hai), latency badhti rahegi (Little's Law: queue jitni deep, wait utna zyada), aur phir OOM. Bounded buffer + explicit signal hi real fix hai.

- **Backpressure ≠ rate limiting:** Rate limiting producer ko ek fixed cap (e.g. 1000 req/sec) deta hai chahe consumer free ho ya busy — ye proactive aur static hai. Backpressure reactive aur dynamic hai: actual consumer saturation ke basis pe signal generate hota hai. Dono complementary hain, same cheez nahi.

- **Drop karna hamesha "failure" nahi hai:** Log/metrics/live-video jaise lossy domains mein old data drop karna correct design hai (load shedding), bug nahi. Galti ye hai ki silently aur unbounded buffer karte raho jab tak crash na ho.

- **Cascading failure / head-of-line blocking:** Agar backpressure ko blindly block karke propagate karo, to ek slow downstream pura upstream stall kar sakta hai aur thread pools exhaust ho sakte hain — ye ek cascading failure bn jaata hai. Isiliye timeouts, bounded queues, circuit breakers, aur edge pe load shedding backpressure ke saath jaate hain.

- **Synchronous "slowness" bhi backpressure hai:** Log interview mein sochte hain backpressure sirf explicit `request(n)` signal hai. Reality mein ek blocking synchronous call (jo slow downstream pe wait karti hai) bhi implicit backpressure hai — wo caller ki rate ko naturally throttle kar deti hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/async-messaging/conceptual_quiz_backpressure.md`](../../../sysd-quizzes/async-messaging/conceptual_quiz_backpressure.md) — `sysd-buddy quiz scaffold backpressure` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update backpressure --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — producer/consumer rate mismatch, bounded buffer + watermarks, aur signal propagation ka interactive diagram.
</content>
</invoke>
