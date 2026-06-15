# REST vs RPC vs GraphQL

**Track:** Building Blocks
**Category:** Fundamentals & Networking

## What It Is

REST, RPC, aur GraphQL teen alag-alag API styles hain client aur server ke beech data exchange karne ke: REST resources ko URLs + HTTP verbs se expose karta hai, RPC remote functions ko ek local call ki tarah invoke karta hai, aur GraphQL ek single endpoint deta hai jahan client ek query language se exactly woh fields maangta hai jo usko chahiye.

## Real-World Analogy

Socho ek restaurant hai aur teen tareeke hain khana order karne ke.

**REST** ek printed menu jaisa hai jahan har dish (resource) ka ek fixed naam aur number hai. Tum "table 5" ya "dish 12" jaise nouns ke saath baat karte ho, aur actions standard hain — `GET` matlab "dikhao", `POST` matlab "naya banao", `DELETE` matlab "hatao". Waiter har naye customer ke liye same predictable rules follow karta hai, isliye koi bhi waiter tumhara order samajh sakta hai. Lekin agar tumhe ek dish ke saath uska chef, uski calories, aur side-dishes bhi chahiye, to tumhe alag-alag teen baar waiter ko bulana pad sakta hai.

**RPC** aisa hai jaise tum kitchen ke andar ek personal cook ko seedha bolte ho "makeButterChicken(spicy=true)". Tum noun nahi, **verb/action** pe focus karte ho — ek specific function chalao. Bahut fast aur direct, kyunki tum aur cook ek private shorthand share karte ho. Problem: agar koi naya customer aaye jo us shorthand ko nahi jaanta, to wo confuse ho jaata hai — coupling tight hoti hai.

**GraphQL** aisa waiter hai jise tum ek single parchi (query) doge jisme likha hai "mujhe butter chicken chahiye, sirf uska naam, price, aur chef ka naam — aur uske side-dishes ke sirf naam." Waiter ek hi round-trip mein bilkul utna hi laata hai, na zyada na kam. Flexible aur efficient, lekin waiter ko ek smart brain (query planner) chahiye jo har custom parchi ko samajh ke kitchen se sahi cheezein efficiently nikaal sake.

## How It Works

### REST
1. Server resources ko URLs se model karta hai: `GET /users/42`, `GET /users/42/orders`. HTTP verbs (`GET/POST/PUT/PATCH/DELETE`) actions define karte hain.
2. Stateless: har request self-contained hoti hai, server client ka session memory mein hold nahi karta. Isse horizontal scaling easy hoti hai.
3. Responses aksar JSON hote hain, aur HTTP status codes semantics dete hain (`200 OK`, `201 Created`, `404 Not Found`, `429 Too Many Requests`).
4. Caching built-in HTTP layer pe milti hai — `GET` requests ko CDN/browser `Cache-Control` aur `ETag` headers se cache kar sakte ho, jo ek bada operational win hai.
5. Cost: ek dashboard jo user + uske orders + recommendations dikhata hai, often **3 separate round-trips** maangta hai (under-fetching), ya ek fat endpoint banao jo har client ko zyada data deta hai (over-fetching). Har round-trip pe mobile network pe ~50-150 ms latency add hoti hai.

### RPC (including gRPC)
1. Client ek stub call karta hai jo local function jaisa dikhta hai: `userService.GetUser(id=42)`. Stub arguments ko serialize karke network pe bhejta hai.
2. Modern RPC = **gRPC**, jo HTTP/2 pe chalta hai aur **Protocol Buffers** (binary, schema-driven) se messages encode karta hai. Binary payload JSON se kaafi compact hota hai — typical messages mein **30-60% chhota** payload aur faster parse.
3. HTTP/2 multiplexing ek single TCP connection pe kai concurrent streams allow karta hai, plus **bidirectional streaming** (client-stream, server-stream, dono). Internal service-to-service calls mein single-digit ms latencies common hain.
4. Contract `.proto` file hota hai; codegen client aur server dono ke liye strongly-typed stubs banata hai. Schema mismatch compile-time pe pakda jaata hai.
5. Cost: browsers gRPC ko natively nahi bol sakte (gRPC-Web proxy chahiye), aur HTTP caching infra ko leverage karna mushkil hai kyunki ye `POST`-style binary calls hain.

### GraphQL
1. Ek single endpoint, usually `POST /graphql`. Client ek query bhejta hai jo exact shape describe karti hai: `{ user(id:42){ name orders{ id total } } }`.
2. Server ke paas ek **schema** (types + fields) hota hai. Har field ek **resolver** function se backed hota hai jo us field ka data fetch karta hai (DB, doosri service, cache — kahin se bhi).
3. Server query ko parse + validate karke ek execution tree banata hai, resolvers run karta hai, aur response ko query ke exact shape mein assemble karta hai — **no over-fetching, no under-fetching**.
4. Ek hi round-trip mein nested/related data mil jaata hai — woh dashboard jo REST mein 3 calls leta tha, GraphQL mein **1 call** mein aa jaata hai.
5. Cost: HTTP caching tougher hai (most queries `POST`, aur shapes vary karte hain), aur naive resolvers **N+1 query problem** create karte hain — isliye **DataLoader**-style batching/caching almost mandatory hai.

## Tradeoffs & Variants

- **Over/under-fetching:** REST over- ya under-fetch karta hai (fixed response shapes). GraphQL client ko exact fields choose karne deta hai, isliye payload tight rehta hai — mobile/low-bandwidth clients ke liye bada plus.
- **Round-trips:** REST nested data ke liye multiple round-trips maangta hai; GraphQL ek query mein related data graph fetch kar leta hai. RPC ke liye tumhe usually ek aggregate method design karna padta hai.
- **Payload + speed:** gRPC (Protobuf binary) sabse compact aur fast hai → high-throughput internal microservices ke liye best. REST/GraphQL JSON human-readable hai par heavier.
- **Caching:** REST sabse strong hai — standard HTTP caching, CDN, `ETag`. gRPC aur GraphQL mein caching application-level effort maangti hai.
- **Schema & typing:** gRPC aur GraphQL dono strongly-typed contracts dete hain (`.proto` / GraphQL SDL), jisse client-server drift compile/validate time pe pakda jaata hai. Plain REST untyped hota hai jab tak tum OpenAPI/Swagger na lagao.
- **Streaming:** gRPC native bidirectional streaming deta hai. REST streaming ke liye SSE/long-polling hacks. GraphQL real-time ke liye **Subscriptions** (usually WebSockets) deta hai.
- **Versioning:** REST aksar URL versioning use karta hai (`/v1/`, `/v2/`). GraphQL evolutionary hai — naye fields add karo, purane ko `@deprecated` mark karo, koi `/v2` nahi. gRPC Protobuf field numbers ke saath backward-compatible evolution allow karta hai.
- **Browser support:** REST aur GraphQL dono browser-native (plain HTTP). gRPC ko browser mein chalane ke liye gRPC-Web + proxy chahiye.

## When To Use It

- **REST:** Public-facing APIs, CRUD-heavy resources, jab broad client compatibility aur HTTP caching matter karein. Stripe, GitHub (v3), aur zyadatar SaaS APIs REST hain — simple, cacheable, universally understood.
- **gRPC/RPC:** **Internal east-west microservice-to-microservice** traffic jahan low latency aur high throughput chahiye. Google internally gRPC use karta hai; Netflix, Uber, aur most service meshes (Envoy/Istio) gRPC carry karte hain. Polyglot backends ke liye codegen bada win hai.
- **GraphQL:** Jab ek frontend (especially mobile) ko **kai backends se data aggregate** karna ho aur har screen ko alag-alag data shape chahiye — over-fetching kill karna ho. Facebook (originator), GitHub (v4 API), Shopify, aur Netflix's BFF/aggregation layers GraphQL use karte hain. Mobile pe ek-query-per-screen latency aur battery dono bachata hai.
- **Common production pattern:** gRPC internal services ke beech, aur ek API gateway/BFF jo bahar REST ya GraphQL expose karta hai. Teeno mutually exclusive nahi hain — ek hi system mein layer-wise coexist karte hain.

## Common Interview Gotchas

- **"GraphQL hamesha faster hai" — galat.** GraphQL round-trips bachata hai aur payload trim karta hai, par single simple lookup ke liye REST aksar simpler aur cacheable hota hai. Aur naive GraphQL resolvers **N+1 problem** se DB ko hammer karte hain — bina DataLoader batching ke ek query 100s of DB hits trigger kar sakti hai. GraphQL "smarter fetching" deta hai, free speed nahi.
- **"REST ka matlab JSON hai" — galat.** REST ek **architectural style** hai (resources, stateless, uniform interface, HTTP verbs), format nahi. JSON sirf common convention hai; REST XML ya kuch bhi return kar sakta hai. Bahut log "JSON over HTTP" ko hi REST samajh lete hain — strictly that's "RESTful-ish," true REST mein HATEOAS/hypermedia bhi aata hai.
- **"gRPC = HTTP/3 / always fastest everywhere" — careful.** gRPC HTTP/2 pe chalta hai (HTTP/3 nahi by default), aur browsers se directly bolne ke liye gRPC-Web proxy chahiye. Internal services mein fast hai, public browser-facing pe friction hai.
- **GraphQL caching ko underestimate karna:** Interviewer puchega "GraphQL mein CDN caching kaise?" — REST `GET`s CDN pe free cache hote hain, par GraphQL `POST` queries nahi. Answer: persisted queries, response-level/field-level caching (Apollo), ya CDN ke liye query hashing.
- **Security surface:** GraphQL mein ek malicious deeply-nested query server ko DoS kar sakti hai (query explosion). Mitigation: query depth/complexity limits, persisted queries, rate limiting. REST endpoints discrete hote hain isliye ye specific risk kam hai.
- **Over/under-fetching dono pakdo:** Sirf "REST over-fetch karta hai" bolna adhura hai. REST **dono** karta hai — ek thin endpoint under-fetch (extra calls), ek fat endpoint over-fetch (extra bytes). GraphQL is exact dono ko solve karta hai. Ye nuance interviewer ko impress karta hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_rest_rpc_graphql.md`](../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_rest_rpc_graphql.md) — `sysd-buddy quiz scaffold rest-rpc-graphql` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update rest-rpc-graphql --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — REST vs RPC vs GraphQL ke request/response flow, payload shapes, aur round-trip comparison ka interactive diagram.
