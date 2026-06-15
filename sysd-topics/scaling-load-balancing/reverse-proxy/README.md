# Reverse Proxy

**Track:** Building Blocks
**Category:** Scaling & Load Balancing

## What It Is

Reverse proxy ek server hai jo clients aur ek ya zyada backend servers ke beech mein baithta hai — client request usi ke paas aati hai, aur wo request ko appropriate backend pe forward karke response wapas client ko bhej deta hai, taaki backends client se directly kabhi expose na hon.

## Real-World Analogy

Socho ek bade corporate office ka reception desk. Bahar se koi visitor aata hai aur kisi bhi employee ya department se milna chahta hai — wo seedha andar nahi ghus sakta. Reception pe ek receptionist baithi hai jo har visitor ko receive karti hai, unki identity check karti hai, aur phir andar ke correct person tak unhe route karti hai.

Visitor ko ye nahi pata ki andar kaun-kaun se employees hain, kaun aaj chhutti pe hai, ya kis floor pe kaun baithta hai — usse bas reception ka ek single address pata hai. Receptionist andar ki saari complexity hide kar leti hai: wo load balance karti hai (ek hi banda busy ho to doosre ko bhej do), security check karti hai, aur ek hi entry point se sab kuch control karti hai.

Reverse proxy bilkul yahi receptionist hai. Clients ko sirf proxy ka ek public address (jaise `api.example.com`) pata hota hai. Andar 50 backend servers ho sakte hain, kuch down ho sakte hain, naye add ho sakte hain — client ko kuch farak nahi padta. (Note: forward proxy ka kaam ulta hota hai — wo client ki taraf se baithta hai, jaise office ka ek banda jo bahar jaake baaki sabke liye kaam karwa ke laata hai.)

## How It Works

1. **Single entry point / DNS:** Client ek hostname resolve karta hai (jaise `api.example.com`) jo reverse proxy ke public IP pe point karta hai — actual backend IPs kabhi DNS mein expose nahi hote. Saara client traffic pehle proxy pe land karta hai.

2. **TLS termination:** Proxy aksar HTTPS connection ko apne paas hi terminate karta hai — yaani TLS handshake aur decryption proxy karta hai, backends ke saath usually plain HTTP ya ek lighter internal TLS pe baat karta hai. Ek TLS handshake roughly 1 extra RTT add karta hai; isse ek hi jagah handle karne se backends ka CPU bachta hai aur cert management central ho jaata hai.

3. **Routing / request matching:** Proxy incoming request ke `Host` header, URL path, ya headers dekh ke decide karta hai konsa backend pool isko handle karega — jaise `/api/*` ek service ko, `/static/*` doosri ko (path-based routing), ya `Host: shop.example.com` ek pool ko (host-based / virtual hosting).

4. **Load balancing + backend selection:** Pool ke andar proxy ek algorithm (round-robin, least-connections, weighted, ya hash-based sticky sessions) se ek healthy backend choose karta hai. Health checks (jaise har 2-5 sec ek `/healthz` ping) se unhealthy backends ko rotation se nikaal diya jaata hai.

5. **Connection handling:** Proxy client ke saath ek connection rakhta hai aur backend ke saath alag connection (often ek reused connection pool se). Ye connection pooling thousands of slow client connections ko absorb karke backends ko sirf kuch hundred warm connections de deta hai. Modern proxies tens of thousands concurrent connections per instance handle kar lete hain.

6. **Response path + caching:** Backend response proxy ko aata hai; proxy cacheable responses (jaise static assets, ya `Cache-Control` allow kare to API responses) ko cache kar sakta hai. Ek cache hit microseconds-to-low-ms mein serve hota hai bina backend ko hit kiye, jabki ek backend round-trip 10-100ms le sakta hai.

7. **Cross-cutting concerns:** Wapas bhejne se pehle proxy compression (gzip/brotli), rate limiting, request/response header rewriting, aur logging/metrics emission kar deta hai — ye sab ek hi central layer pe.

## Tradeoffs & Variants

- **Reverse proxy vs Load balancer:** Ye interviewer ka favourite confusion hai. Load balancing reverse proxy ka **ek feature** hai. L4 load balancer (jaise AWS NLB) sirf TCP/UDP packets ko forward karta hai — usse HTTP ka pata nahi hota, isliye fast but dumb. L7 reverse proxy (nginx, Envoy, HAProxy in HTTP mode) HTTP layer samajhta hai — path routing, TLS termination, caching, header rewriting sab kar sakta hai, but per-request overhead thoda zyada.

- **Single point of failure:** Sab kuch proxy se hoke jaata hai, to agar proxy down to poori service down. Isliye production mein proxy hamesha redundant chalti hai (multiple instances + ek floating VIP / DNS failover / Anycast). Tradeoff: extra infra complexity vs availability.

- **Extra network hop / latency:** Har request ek additional hop leta hai (typically sub-millisecond intra-DC, but real). Iske badle aapko centralization milta hai. Latency-critical paths pe log isko weigh karte hain.

- **Caching aggressiveness:** Zyada caching → backends pe kam load aur fast responses, lekin stale data ka risk. Personalized/authenticated content ko cache karna khatarnak hai (galat user ko doosre ka data mil sakta hai) — isliye cache keys mein auth/vary headers carefully handle karne padte hain.

- **TLS termination vs passthrough:** Terminate karo to proxy plaintext dekh sakta hai (routing/caching/WAF possible) but proxy aur backend ke beech ka segment encrypt karna padega for compliance (mTLS). Passthrough (TLS ko backend tak le jao) end-to-end encryption deta hai but proxy L7 features lose kar deta hai.

- **Variants:** API Gateway (reverse proxy + auth + rate limit + API composition), CDN edge (geographically distributed reverse proxy + cache), aur sidecar proxy (Envoy in a service mesh — per-pod reverse proxy).

## When To Use It

- **Koi bhi multi-server web/API backend:** Jaise hi ek service ke peeche ek se zyada instance honge, ek reverse proxy chahiye routing + load balancing ke liye. Almost har system design answer mein ye client ke baad pehla box hota hai.
- **TLS termination centralize karni ho:** Saare certs ek jagah, backends ka CPU free.
- **Microservices ke aage API Gateway:** Ek single public endpoint jo dozens of internal services ko route kare (Netflix Zuul, Kong, AWS API Gateway).
- **Static + dynamic content split:** `/static/*` cache se, `/api/*` backend se.
- **Real systems:** **nginx** aur **HAProxy** classic reverse proxies hain; **Envoy** modern service mesh (Istio) aur edge mein; **Cloudflare** aur **AWS CloudFront** CDN-level reverse proxies; **AWS ALB** ek managed L7 reverse proxy/load balancer hai.

## Common Interview Gotchas

- **Forward proxy vs reverse proxy ulta bol dena:** Reverse proxy **server ke aage** baithta hai aur clients se backends ko hide karta hai (clients ko pata nahi konsa server). Forward proxy **client ke aage** baithta hai aur server se clients ko hide karta hai (server ko pata nahi asli client kaun — jaise corporate egress proxy / VPN). "Reverse" ka matlab hai direction of who-it-fronts ulta hai.

- **"Reverse proxy = load balancer" maan lena:** Load balancing ek feature hai, identity nahi. Ek reverse proxy bina multiple backends ke bhi useful hai (sirf TLS termination ya caching ke liye, ek hi backend ke saamne).

- **Single point of failure ignore karna:** Agar aap reverse proxy ko design mein ek single box ki tarah draw karte ho bina redundancy bataye, interviewer turant poochega "ye down ho gaya to?". Hamesha multiple instances + VIP/DNS failover mention karo.

- **Client IP kho jaana:** Backend ko har request proxy ke IP se aata dikhta hai, asli client IP nahi. Isliye proxy `X-Forwarded-For` (ya `Forwarded`) header add karta hai. Agar backend rate-limiting ya geo-logic client IP pe karta hai aur ye header trust/handle nahi karta, to logic toot jaata hai. (Aur ye header spoof bhi ho sakta hai — sirf trusted proxy se aaya ho tabhi trust karo.)

- **TLS termination ke baad internal traffic plaintext chhod dena:** Agar proxy TLS terminate karta hai aur backends ko plain HTTP bhejta hai ek untrusted network pe, to wo segment exposed hai. Zero-trust setups mein proxy-to-backend bhi mTLS hona chahiye.

- **Sticky sessions ka silent assumption:** Agar backends mein session state local rakha hai, to plain round-robin todega (user ka next request doosre backend pe jaakar logged-out dikhega). Ya to sticky sessions (session affinity) use karo, ya better — session state ko externalize karo (Redis), taaki backends stateless rahein.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_reverse_proxy.md`](../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_reverse_proxy.md) — `sysd-buddy quiz scaffold reverse-proxy` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update reverse-proxy --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — client → reverse proxy → backend pool ka flow, TLS termination, routing, aur caching ka interactive diagram.
