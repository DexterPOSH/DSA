# Idempotency

**Track:** Building Blocks
**Category:** Async & Messaging

## What It Is

Idempotency ek aisi property hai jisme ek hi operation ko ek baar ya multiple baar perform karne ka end state same rehta hai — yaani duplicate retries system pe extra side-effect nahi daalti.

## Real-World Analogy

Socho ek lift (elevator) ka call button. Aap up-button dabate ho, lift already bula li gayi. Ab agar aap nervous hokar usi button ko 5 aur baar daba do, to bhi lift sirf ek hi baar aayegi — multiple presses ka net effect single press jaisa hi hai. Button "idempotent" hai.

Iske ulat socho ek vending machine jisme har "Coke" button press pe ek alag can nikalti hai aur ₹50 katte hain. Agar network laggy ho aur aap button do baar daba do, to do cans aur ₹100 — duplicate action ka duplicate side-effect. Ye non-idempotent operation hai.

Distributed systems mein network kabhi reliable nahi hota: request bheji, response time pe nahi aaya, to client retry karta hai — par ho sakta hai original request server tak pahunch gayi thi aur sirf response kho gaya. Idempotency hamara "lift button" banata hai har critical operation ko, taaki retry safe rahe aur "Coke do baar nikal gayi" jaisa double-charge na ho.

## How It Works

1. **Problem ka root:** "At-least-once" delivery. Kafka, SQS, gRPC retries, payment gateways — sab at-least-once guarantee dete hain, exactly-once nahi (kyunki network mein response loss ko request loss se distinguish karna impossible hai). To duplicate aayenge hi. Idempotency consumer ki zimmedaari hai ki duplicate ko safely absorb kare.

2. **Idempotency key:** Client har "mutating" request ke saath ek unique key bhejta hai — ek UUID jaisa `Idempotency-Key: 7f3a-...`. Important: ye key client generate karta hai *retry se pehle* aur retry pe **same** key reuse karta hai. Agar key har retry pe nayi banegi to dedup hoga hi nahi.

3. **Server-side dedup store:** Server ek fast store (jaise Redis ya ek DB table) mein dekhta hai: "kya is key ko maine pehle process kiya?" Lookup typically sub-millisecond (Redis ~0.2-0.5 ms) hota hai.
   - **Pehli baar (cache miss):** key store karo (status = `in-progress`), operation execute karo (e.g. charge ₹500), result store karo (status = `done`, saved response), client ko response bhejo.
   - **Duplicate (cache hit, status `done`):** operation dobara mat chalao — store kiya hua saved response wapas bhej do. Charge dobara nahi hota.

4. **Atomicity of the check-and-act:** Naive "pehle check karo, phir insert karo" mein race condition hai — do concurrent duplicates dono ko miss dikhega aur dono charge kar denge. Isliye atomic primitive use hota hai: DB mein `INSERT ... ON CONFLICT DO NOTHING` (unique constraint on idempotency key), ya Redis `SET key val NX`. Jiska insert "jeeta" wahi process karta hai, doosra hara hua duplicate wait/return karta hai.

5. **TTL / retention:** Keys forever store nahi kar sakte (storage badhega). Common practice: idempotency keys ko 24h–7 days TTL ke saath rakho — itna window kaafi hai realistic retries (client retry, gateway retry) cover karne ke liye. Stripe jaise systems 24h tak idempotency keys honor karte hain.

6. **Concrete flow example:** Client `POST /charge` with `Idempotency-Key: K1`, amount ₹500 bhejta hai. Server K1 ko `NX` se insert karta hai → success → Stripe pe charge karta hai (~300 ms) → response `{charge_id: ch_99}` ko K1 ke against save karta hai → client ko bhejta hai. Ab response client tak network glitch se nahi pahuncha. Client 2 sec baad **same K1** se retry karta hai → server K1 already `done` dekhta hai → bina dobara charge kiye saved `{charge_id: ch_99}` lauta deta hai. Net effect: ek hi ₹500 charge.

## Tradeoffs & Variants

- **Naturally idempotent vs explicit dedup:** Kuch operations design se hi idempotent hote hain — jaise `SET balance = 500` (absolute set), ya `PUT /user/42 {name: "A"}` (full replace), ya `DELETE /order/9`. Inko dedup store ki zaroorat nahi. Problem `INSERT`, `balance += 100`, "send email" jaise *relative / side-effectful* operations mein hai — inke liye idempotency key + dedup store chahiye. Interviewer aksar poochta hai "is operation ko naturally idempotent bana sakte ho?" — ye pehla, sasta option hai.

- **Dedup store ka choice:** Redis (fast, ~0.3 ms, par TTL ke baad evict; agar persistence off ho to crash pe key loss → duplicate slip through) vs DB unique constraint (durable, transactional, par har request pe ek extra write/row). High-throughput pe Redis, strong-correctness-critical (payments) pe DB ya dono.

- **Key kaun generate kare:** Client-generated key (best — original aur retry dono ko cover karta hai end-to-end) vs server-derived natural key (jaise `order_id + "charge"`) jab client cooperate nahi karta. Client key zyada robust hai.

- **Storing the response vs just a flag:** Sirf "processed" flag store karoge to duplicate pe client ko kya lautaoge? Best practice: pehli baar ka **full response** save karo, taaki duplicate ko exactly wahi result mile (same `charge_id`), na ki ek generic "already done."

- **Idempotency != exactly-once execution:** Ye sabse bada conceptual tradeoff. Hum exactly-once *delivery* guarantee nahi kar sakte; hum at-least-once delivery + idempotent processing = **effectively-once** *effect* achieve karte hain. Kafka ka "exactly-once" bhi internally idempotent producer + transactions se hi banta hai.

## When To Use It

- **Payment / billing APIs:** Stripe, PayPal, Razorpay sab `Idempotency-Key` header support karte hain taaki double-charge na ho on retry. Ye canonical use case hai.
- **Message queue consumers:** Kafka/SQS at-least-once dete hain, to consumer ko har message ko `message_id` se dedup karke idempotently process karna padta hai (e.g. "order placed" event ko do baar process karke do orders na ban jaayein).
- **Webhooks:** Provider (Stripe, GitHub) same webhook event ko retry karta hai agar aapka 200 time pe nahi mila. Receiver ko `event_id` pe dedup karna chahiye.
- **Distributed writes / sagas:** Multi-step workflows jahan ek step retry hoga — har step idempotent hona chahiye warna partial reruns corrupt state banayenge.
- **gRPC / HTTP with retries:** Koi bhi `POST`/`PATCH` jise client ya proxy automatically retry karta hai.

## Common Interview Gotchas

- **"PUT/DELETE idempotent hote hain, POST nahi" — half-truth:** HTTP spec ke according `GET/PUT/DELETE` idempotent maane jaate hain aur `POST` nahi. Par ye *protocol-level semantics* hai. Asli safety *implementation* pe depend karti hai — ek galat-likha `PUT handler` jo har call pe append kare wo idempotent nahi rahega, aur ek sahi-design kiya `POST` (idempotency key ke saath) idempotent ban sakta hai. Spec guidance hai, guarantee nahi.

- **Idempotent vs safe:** "Safe" = koi state change nahi (GET). "Idempotent" = multiple calls = single call ka effect, par state change ho sakta hai (DELETE same row ko phir delete kare to first call ke baad woh already gayab; net effect same). Inko mat mix karo — `GET` safe + idempotent dono, `DELETE` idempotent par safe nahi.

- **Same key, alag payload:** Agar client K1 se ₹500 bhejta hai phir K1 se ₹900 bhej de, server ko kya karna chahiye? Correct answer: reject karo (409/422) — same idempotency key alag request body ke saath ek client bug hai, aur usko silently honor karna data corruption hai. Stripe yahi karta hai. Naive implementations sirf key match karke purana response lauta dete hain — galat.

- **Check-then-act race:** "Pehle SELECT to dekh lo exist karta hai, phir INSERT" classic race condition hai do concurrent duplicates ke beech — dono SELECT pe miss, dono INSERT → double effect. Atomic `INSERT ... ON CONFLICT` ya `SET NX` chahiye. Interviewer specifically ye race poochta hai.

- **Retry pe nayi key generate karna:** Sabse common practical bug — client har attempt pe fresh UUID banata hai. Tab dedup kaam hi nahi karega kyunki server ko har baar naya key dikhega. Key retry boundary se *pehle* fix honi chahiye.

- **Idempotency se exactly-once delivery assume kar lena:** Idempotency duplicates ko *harmless* banata hai, unhe rokta nahi. Aap abhi bhi at-least-once duniya mein ho — "exactly-once" ek effect hai jo idempotency deta hai, ek delivery guarantee nahi.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/async-messaging/conceptual_quiz_idempotency.md`](../../../sysd-quizzes/async-messaging/conceptual_quiz_idempotency.md) — `sysd-buddy quiz scaffold idempotency` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update idempotency --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — idempotency key flow, dedup store hit/miss, aur retry-after-lost-response ka interactive diagram.
