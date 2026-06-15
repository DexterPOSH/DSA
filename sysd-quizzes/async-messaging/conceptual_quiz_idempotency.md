# Idempotency — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update idempotency --quiz-score N/M` -->

## Q1 (warm-up)
Idempotency ko ek line mein define karo. Ek example do ek operation ka jo naturally idempotent hai, aur ek jo nahi hai.

**Ideal answer:** Idempotency = ek operation ko 1 baar ya N baar perform karne ka end state same rehta hai (duplicate calls extra side-effect nahi daaltin). Naturally idempotent: `SET balance = 500` (absolute set), `PUT /user/42`, `DELETE /order/9`, `GET`. Non-idempotent: `balance += 100`, `INSERT new row`, "send email / charge card" — har call ek naya side-effect. Bonus: idempotent ≠ "no state change" (DELETE state badalta hai par net effect same).

## Q2 (core)
Ek payment API duplicate charges se kaise bachti hai jab client retry karta hai? Idempotency key flow ko first-request aur duplicate-request dono ke liye describe karo.

**Ideal answer:** (1) Client ek unique idempotency key generate karta hai *retry se pehle* aur retry pe **same** key reuse karta hai (header mein bhejta hai). (2) Server ek dedup store (Redis/DB) mein key lookup karta hai. (3) First request → cache miss → key insert (atomic, e.g. `SET NX` ya `INSERT ON CONFLICT`), operation execute (charge), full response key ke against save, response return. (4) Duplicate → cache hit (status done) → operation dobara NAHI chalata, saved response wapas bhejta hai → no double charge. Key points grader checks: client-generated key reused on retry, atomic insert, response stored & replayed, operation not re-executed.

## Q3 (tradeoff)
Dedup store ke liye Redis vs ek DB unique constraint — tradeoffs kya hain? Kab kya choose karoge?

**Ideal answer:** Redis: bahut fast (~0.2–0.5 ms), TTL easy, par non-durable — agar persistence off/relaxed ho to crash pe key loss → duplicate slip through ho sakta hai; high-throughput, less-critical dedup ke liye accha. DB unique constraint (`INSERT ... ON CONFLICT`): durable, transactional, same DB transaction mein side-effect ke saath atomic ho sakta hai — par har request pe extra row/write, throughput cost. Choice: payments / correctness-critical → DB (ya Redis + DB). Pure high-throughput dedup jahan rare miss tolerable → Redis. Bonus: TTL/retention tradeoff (forever store nahi kar sakte, ~24h–7d window).

## Q4 (gotcha)
Bahut log kehte hain "PUT/DELETE idempotent hain, POST nahi." Iss statement mein kya nuance / galat-fehmi hai? Aur "check-then-act race condition" kya hai?

**Ideal answer:** (a) PUT/DELETE idempotent "hone chahiye" ye HTTP *spec semantics* hai, guarantee nahi — implementation galat ho to PUT bhi non-idempotent ban sakta hai, aur sahi-design kiya POST (idempotency key ke saath) idempotent ban sakta hai. Spec = guidance, not enforcement. Bonus: idempotent vs safe distinction (DELETE idempotent par safe nahi; GET dono). (b) Check-then-act race: "pehle SELECT karke dekho exist karta hai, phir INSERT" — do concurrent duplicates dono SELECT pe miss dekhte hain, dono INSERT/execute kar dete hain → double effect. Fix: atomic primitive — `INSERT ... ON CONFLICT DO NOTHING` ya `SET key NX`, taaki sirf ek "jeete."

## Q5 (applied)
Aap ek Kafka consumer bana rahe ho jo "OrderPlaced" events process karke orders create karta hai. Kafka at-least-once delivery deta hai. Aap exactly ek order per event kaise ensure karoge? Aur "idempotency se exactly-once delivery milti hai" — sahi ya galat?

**Ideal answer:** Kafka at-least-once = duplicates aayenge hi (rebalance, redelivery). Har event ka ek stable unique id ho (e.g. `event_id` / `order_id` in payload). Consumer processing ko idempotent banao: dedup store ya DB unique constraint on `event_id` (`INSERT order ... ON CONFLICT DO NOTHING`), ya order creation ko `order_id` ke against upsert karo. Offset commit & side-effect ka ordering bhi sambhaalo (process → persist with dedup → commit). Galat hai ki "idempotency exactly-once delivery deti hai" — delivery still at-least-once; idempotency duplicates ko harmless banakar **effectively-once / exactly-once effect** deti hai, delivery guarantee nahi. (Kafka's own "exactly-once" bhi idempotent producer + transactions pe based hai.)
