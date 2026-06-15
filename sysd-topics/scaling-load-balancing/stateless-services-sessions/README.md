# Stateless Services & Sessions

**Track:** Building Blocks
**Category:** Scaling & Load Balancing

## What It Is

Ek stateless service wo hota hai jo kisi bhi request ko handle karne ke liye apni local memory mein client ka koi prior state nahi rakhta — har request self-contained hoti hai (ya state externally store hota hai), taaki koi bhi instance kisi bhi request ko serve kar sake.

## Real-World Analogy

Socho ek bank branch hai jisme do tarah ke counters hain.

**Stateful counter (purana tareeka):** Tum ek specific teller ke paas jaate ho jo tumhari poori case file apni desk drawer mein rakhta hai. Agar wo teller chhutti pe chala jaaye (server crash), ya tumhe baar-baar usi teller ke paas bhejna pade (sticky session), to system rigid ho jaata hai. Naya teller tumhari file ke bina tumhe serve nahi kar sakta.

**Stateless counter (modern tareeka):** Yahan har customer ke paas apni poori passbook + ID khud hoti hai. Tum kisi bhi free teller ke paas jao, passbook dikhao, kaam ho gaya. Teller ko bas tumhari passbook (the request payload + a token) padhni hai — usko tumhe yaad rakhne ki zaroorat hi nahi. Branch 5 tellers se 50 tellers kar de, koi farak nahi padta; jo bhi free hai wahi serve kar dega. Yahi stateless service ka asli faayda hai: koi bhi instance, koi bhi request, kabhi bhi.

## How It Works

1. **State ko request body / token mein le aao:** Client har request ke saath apni identity proof bhejta hai — typically ek session token ya JWT `Authorization: Bearer <token>` header mein. Server ko apni RAM mein "ye user logged in hai" yaad rakhne ki zaroorat nahi.

2. **Server local memory mein kuch persist nahi karta:** Request aayi, process hui, response gaya — instance apni heap/RAM mein us client ke baare mein kuch nahi rakhta. Iska matlab N identical instances behind ek load balancer, aur LB kisi bhi instance pe request bhej sakta hai (round-robin / least-connections), sticky routing ki zaroorat nahi.

3. **Session state ko externalize karo:** Jo state genuinely chahiye (cart contents, login session, rate-limit counters), usko ek shared external store mein daalo — jaise Redis ya Memcached. Ek typical session lookup Redis se sub-millisecond se ~1-2 ms mein aa jaati hai (same-AZ, in-memory). Yahi reason hai stateless design fast rehta hai: heavy state DB mein nahi, ek fast in-memory store mein.

4. **Token-based approach (JWT):** JWT mein claims (user id, roles, expiry) signed hote hain. Server token ki signature verify karta hai (HMAC ya RSA) — ye purely CPU work hai, koi network call nahi, microseconds mein ho jaata hai. To server ko session store se baat karne ki bhi zaroorat nahi pad sakti. Tradeoff: JWT typically 200 bytes - 1 KB ka hota hai aur har request pe travel karta hai.

5. **Scaling ka payoff:** Kyunki har instance interchangeable hai, autoscaling trivial ho jaati hai. Traffic 10K QPS se 50K QPS ja raha hai? Bas naye pods add kar do; warming up ki zaroorat nahi kyunki unke paas local state hai hi nahi. Ek instance mar gaya? LB use rotation se nikaal deta hai aur user ko pata bhi nahi chalta — uska session Redis mein safe hai.

6. **Deploys aur restarts smooth:** Rolling deploy mein instances ek-ek karke restart hote hain. Stateful hote to in-memory sessions gum ho jaate; stateless mein kuch lose nahi hota kyunki state already externalized hai.

## Tradeoffs & Variants

- **Sticky sessions (session affinity) vs true stateless:** Sticky sessions mein LB ek client ko hamesha usi instance pe bhejta hai (cookie ya IP hash se), taaki in-memory session reuse ho. Ye quick fix hai par scaling tod deta hai — uneven load, aur instance marne pe us instance ke saare sessions gum. Pure stateless (external store) zyada resilient hai par har request pe ek extra store lookup ka cost.

- **Server-side sessions (opaque token + store) vs JWT:** Opaque session ID → server Redis se lookup karta hai. Faayda: instant revocation (Redis se key delete kar do, session dead). Nuksaan: har request pe ek store round-trip. JWT → self-contained, no lookup, fast. Nuksaan: revocation mushkil — token expiry tak valid rehta hai (isiliye short TTL jaise 15 min + refresh token pattern use hota hai).

- **JWT size & expiry tradeoff:** Bada JWT (zyada claims) = har request pe zyada bytes over the wire. Long expiry = revocation gap (compromised token zyada der valid). Short expiry = zyada refresh calls. Sweet spot: short-lived access token (5-15 min) + long-lived refresh token jo server-side revocable ho.

- **External store ek naya single point of failure:** Stateless services apne aap mein resilient, par ab Redis/session store critical ho gaya. Isko replicate karna padta hai (Redis Sentinel/Cluster), warna store down = sab logged out. Yaani aapne state move kiya hai, eliminate nahi.

## When To Use It

- **Horizontally scaling web/API tiers:** Koi bhi service jise aapko load ke saath scale-out karna hai — yahi default design hona chahiye. Twelve-Factor App ka Factor VI ("processes are stateless and share-nothing") exactly isi cheez ki baat karta hai.

- **Behind a load balancer with autoscaling:** AWS ALB + Auto Scaling Groups, Kubernetes Deployments + HPA — ye sab maante hain ki pods interchangeable hain. Stateless design ke bina HPA properly kaam nahi karta.

- **Serverless / FaaS:** AWS Lambda, Cloud Functions inherently stateless hain — har invocation fresh, state DynamoDB/Redis mein. Agar aap serverless soch rahe ho, stateless mandatory hai.

- **Real systems:** Netflix ke API services stateless hain (sessions externalized), isliye wo thousands of instances ke beech freely route kar paate hain. Authentication providers (Auth0, Okta) JWT issue karte hain taaki resource servers stateless reh sakein. Shopping carts often Redis-backed session stores use karte hain.

## Common Interview Gotchas

- **"Stateless ka matlab state hai hi nahi" — galat:** Stateless ka matlab service instance apni local memory mein state nahi rakhti. State exist karta hai — bas wo externalized hai (Redis, DB, ya client ke token mein). Interviewer ye distinction sunna chahta hai. "Where does the state live?" ka jawab "Redis/external store" hona chahiye, "nowhere" nahi.

- **Sticky sessions ko "stateless" samajh lena:** Sticky sessions actually stateful design hai with a routing crutch. Agar koi keh de "main sticky sessions use karunga to scaling solve ho gayi" — ye red flag hai. Sticky sessions instance failure aur load imbalance ke problems la deta hai.

- **JWT revocation ko trivial samajhna:** Common mistake — "logout pe JWT invalidate kar denge." JWT self-contained hai, server use unilaterally kill nahi kar sakta jab tak ek blocklist (jo wapas ek store + lookup laata hai, stateless-ness tod deta hai) na ho. Isliye short TTL + refresh token pattern. Ye nuance batana strong signal hai.

- **External store ki latency aur failure ko ignore karna:** Har request pe Redis call free nahi hai (~1 ms + network). High-QPS pe ye add up hota hai, aur Redis down hone pe poora auth flow rukta hai. Mention karo ki store ko replicate karna padta hai aur lookups ko cache/optimize karna hota hai.

- **Stateless vs idempotent ko mix karna:** Stateless = no per-client memory in the instance. Idempotent = same request do baar bhejne pe same result. Ye alag concepts hain; interviewer dono confuse karte dekh ke note karta hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_stateless_services_sessions.md`](../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_stateless_services_sessions.md) — `sysd-buddy quiz scaffold stateless-services-sessions` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update stateless-services-sessions --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — stateful vs stateless request routing, load balancer fan-out, aur externalized session store ka interactive diagram.
