# HTTP & HTTPS

**Track:** Building Blocks
**Category:** Fundamentals & Networking

## What It Is

HTTP ek stateless, text-based request/response application-layer protocol hai jisse clients (browsers, apps) servers se resources maangte hain, aur HTTPS wahi HTTP hai lekin ek TLS encryption layer ke neeche chalta hua, jo confidentiality, integrity aur server authentication deta hai.

## Real-World Analogy

Socho HTTP ek postcard bhejne jaisa hai. Tum apna message (request) likhte ho, address (URL) daalte ho, aur postman (the network — routers, ISPs, proxies) usse destination tak le jaata hai. Problem ye hai ki raaste mein har postman, har sorting office us postcard ko padh sakta hai, aur theoretically badal bhi sakta hai — kyunki sab kuch plain text mein khula pada hai.

HTTPS us postcard ko ek **sealed, tamper-evident envelope** mein daal dena hai jiski chaabi sirf tumhare aur asli receiver ke paas hai. Beech mein koi postman lifaafa kholega to padh nahi paayega (confidentiality), aur agar koi chhed-chhaad karega to receiver ko turant pata chal jaayega (integrity). Aur sabse important: jab tum envelope seal karte ho, tum pehle receiver ka **ID card (certificate)** check karte ho — taaki koi imposter bich mein khada hoke "main hi tumhara bank hoon" bol ke tumhari chitthi na chura le (authentication). Yahi TLS handshake ka kaam hai.

## How It Works

**HTTP request/response cycle:**

1. **Request line + headers:** Client ek request bhejta hai jisme ek **method** (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`, `OPTIONS`), ek path (`/api/users/42`), HTTP version, aur **headers** (key-value metadata jaise `Host`, `Authorization`, `Content-Type`, `Accept`) hote hain. `POST`/`PUT` ke saath ek body bhi hoti hai.

2. **Response:** Server ek **status code** ke saath jawaab deta hai — `2xx` success (`200 OK`, `201 Created`, `204 No Content`), `3xx` redirect (`301` permanent, `302`/`307` temporary, `304 Not Modified`), `4xx` client error (`400`, `401 Unauthorized`, `403 Forbidden`, `404`, `429 Too Many Requests`), `5xx` server error (`500`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`) — plus response headers aur body.

3. **Stateless:** Har request apne aap mein complete hoti hai; server do requests ko by default link nahi karta. State (login, cart) cookies, tokens ya session IDs se carry hoti hai.

**Transport ke neeche TCP:** HTTP/1.1 aur HTTP/2 ek TCP connection ke upar chalte hain. TCP connection khulne mein ek 3-way handshake lagta hai — yaani ek extra round-trip (1 RTT) overhead, jo same-region mein ~1-5 ms aur cross-continent mein ~100-150 ms tak ho sakta hai.

**HTTPS = HTTP + TLS handshake:** Plain TCP connect ke baad TLS handshake hota hai:

1. Client `ClientHello` bhejta hai (supported TLS versions, cipher suites, ek random nonce).
2. Server `ServerHello` + apna **certificate** (public key + CA signature) bhejta hai. Client certificate chain ko ek trusted **CA** tak verify karta hai — yahi server authentication hai.
3. Dono ek **session key** (symmetric) establish karte hain (modern TLS 1.3 mein ECDHE key exchange se, forward secrecy ke saath).
4. Iske baad saara application data us fast **symmetric key** se encrypt hota hai (AES-GCM type), kyunki asymmetric crypto slow hai aur sirf handshake ke liye use hota hai.

**Latency numbers:** TLS 1.2 handshake = 2 extra RTTs, **TLS 1.3 = sirf 1 RTT** (aur resumed connections pe **0-RTT** possible). To ek HTTPS connection cold-start: ~1 RTT TCP + 1 RTT TLS 1.3. Isi liye connection reuse (keep-alive) aur **HTTP/2 multiplexing** itne important hain — ek hi connection pe hazaaron requests bina dobara handshake kiye.

**Protocol versions ka evolution:**
- **HTTP/1.1:** Ek connection pe ek-ek request serially; "head-of-line blocking" — agli request pichli ke khatam hone ka wait karti hai. Browsers isiliye 6 parallel connections per host kholte hain.
- **HTTP/2:** Ek single TCP connection pe **multiplexed streams** + header compression (HPACK). Application-level HoL blocking khatam, par ek TCP packet loss poori connection ki saari streams ko stall kar deta hai (TCP-level HoL).
- **HTTP/3:** TCP ki jagah **QUIC over UDP** use karta hai — har stream independent, to ek packet loss sirf usi stream ko affect karta hai. TLS 1.3 built-in, aur 0/1-RTT connection setup. Google, Cloudflare, YouTube ye production mein use karte hain.

## Tradeoffs & Variants

- **HTTP vs HTTPS overhead:** HTTPS ek handshake RTT + thoda CPU (encryption) add karta hai. Aaj ke hardware pe ye overhead negligible hai (AES hardware-accelerated), aur browsers ab plain HTTP ko "Not Secure" mark karte hain — so practically HTTPS is non-negotiable. Interviewer agar "kyun HTTPS everywhere" poochhe to answer: privacy, integrity (no ISP injection/ad-tampering), authentication, aur HTTP/2-3 effectively HTTPS hi maangte hain.

- **HTTP/1.1 vs HTTP/2 vs HTTP/3:** /2 multiplexing se latency-sensitive, many-small-assets workloads (web pages with 100s of resources) fast hote hain. Par lossy networks (mobile) pe /2 ka TCP HoL blocking hurt karta hai — wahaan **/3 (QUIC)** clearly better. Tradeoff: QUIC UDP-based hai, to kuch corporate firewalls/middleboxes UDP block kar dete hain → fallback to /2.

- **TLS termination kahan ho:** Aksar TLS load balancer / reverse proxy (NGINX, Envoy, ALB) pe terminate hota hai, fir internal hop plain HTTP — simple aur CPU-efficient. Alternative: **end-to-end TLS / mTLS** (mutual TLS, dono side certs verify karein) — zero-trust / service mesh (Istio) mein common, par operationally heavier (cert rotation, etc.).

- **Idempotency:** `GET`, `PUT`, `DELETE`, `HEAD` idempotent hain (retry safe — same effect), `POST` nahi. Ye retry logic aur safe caching ke design ko drive karta hai.

- **Statelessness ka cost:** Stateless hone se servers horizontally scale karna easy hai (koi bhi server koi bhi request le sakta hai), par state ko har request mein carry karna padta hai (tokens/cookies), jo payload aur auth complexity badhata hai.

## When To Use It

- **Har request/response API:** REST APIs, web pages, mobile backends — sab HTTP/HTTPS pe. Default choice for client-server communication over the internet.
- **HTTPS hamesha** public-facing traffic ke liye — koi exception nahi. Login, payments, ya koi bhi PII handle karne wali service ke liye to mandatory.
- **HTTP/2** typical web frontends ke liye jahan ek page pe bahut saare resources load hote hain (multiplexing wins).
- **HTTP/3 / QUIC** mobile-heavy, high-latency ya lossy networks ke liye — jaise video streaming (YouTube), CDNs (Cloudflare), ya global apps.
- **mTLS** internal service-to-service communication mein jahan zero-trust security chahiye — service meshes (Istio, Linkerd), microservices.
- **Jab real-time bidirectional chahiye** (chat, live updates), HTTP request/response model fit nahi baithta — wahaan **WebSockets** ya **SSE** use hota hai (jo initial handshake HTTP se hi karte hain).

## Common Interview Gotchas

- **"HTTPS = encryption only" — galat:** HTTPS teen cheezein deta hai: **confidentiality** (encryption), **integrity** (tampering detect), aur **authentication** (server wahi hai jo claim kar raha). Authentication wala part log bhool jaate hain — yahi MITM attacks rokta hai via certificates + CA trust chain.

- **"HTTPS slow hai" — mostly myth:** TLS 1.3 sirf 1 RTT add karta hai (resumed pe 0-RTT), aur encryption hardware-accelerated hai. Connection reuse ke saath per-request overhead ~zero. Interviewer ye misconception probe karta hai.

- **`POST` vs `PUT` confusion:** `POST` non-idempotent (do baar chalao → do resources ban sakte hain), `PUT` idempotent (same resource ko replace, repeat safe). `PUT` create bhi kar sakta hai agar client resource ID decide kare. Ye galat batana red flag hai.

- **`301` vs `302`:** `301` permanent redirect — browsers/clients ise cache karte hain, future requests directly nayi URL pe. `302`/`307` temporary — cache nahi hota. Galti se `301` use kar diya to clients lambe time tak stale redirect cache rakh lenge.

- **Cookies aur statelessness:** "HTTP stateless hai par login kaise kaam karta hai?" — server stateless rehta hai; state client-side cookie/token mein store hokar har request ke saath wapas aati hai. Server session store (Redis) ya stateless JWT se reconstruct karta hai.

- **HTTP/2 multiplexing ≠ multiple TCP connections:** /2 ek hi TCP connection pe logical streams banata hai, naye connections nahi. Log isse 6-connection HTTP/1.1 trick se confuse karte hain.

- **TLS handshake mein "data encrypt karne ke liye certificate use hota hai" — galat:** Certificate ka asymmetric key sirf **handshake** (server authenticate + session key exchange) ke liye hai. Actual data ek tez **symmetric** session key se encrypt hota hai. Asymmetric crypto har byte pe use karna bahut slow hoga.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_http_https.md`](../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_http_https.md) — `sysd-buddy quiz scaffold http-https` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update http-https --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — request/response cycle, TLS handshake steps, aur HTTP/1.1 vs /2 vs /3 ka interactive diagram.
</content>
</invoke>
