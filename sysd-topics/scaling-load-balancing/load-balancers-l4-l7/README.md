# Load Balancers (L4 vs L7)

**Track:** Building Blocks
**Category:** Scaling & Load Balancing

## What It Is

Load balancer ek aisa component hai jo incoming traffic ko multiple backend servers ke beech distribute karta hai — aur ye distribution ya to transport layer (L4: TCP/UDP, sirf IP+port dekh ke) pe hota hai, ya application layer (L7: HTTP, jahan URL/headers/cookies tak dekha jaata hai) pe.

## Real-World Analogy

Socho ek bade airport ka entry gate hai jahan hazaaron passengers (requests) aa rahe hain.

Ek **L4 load balancer** us security guard jaisa hai jo sirf passenger ke boarding pass pe likha gate number (IP + port) dekhta hai aur usko bina kuch aur pooche seedha us counter pe bhej deta hai. Wo fast hai kyunki usko passenger ke bag ke andar jhaank ke nahi dekhna — bas "ye terminal 3 ka hai, udhar jao." Ek baar passenger ek counter pe assign ho gaya, to uski poori conversation us hi counter ke saath chalti rehti hai (connection sticky).

Ek **L7 load balancer** us smart concierge jaisa hai jo passenger se actually baat karta hai: "aap kahan jaa rahe ho? Business class ho? Wheelchair chahiye?" — yaani request ka content (URL path `/api/video`, header `Accept-Language: hi`, cookie) padh ke decide karta hai ki kaunsa specialized counter best rahega. Ye zyada intelligent hai, par har passenger se baat karne mein thoda zyada time aur effort lagta hai.

Difference clear hai: L4 sirf "envelope" pe likha address dekhta hai, L7 "letter khol ke" content padhta hai.

## How It Works

**L4 (Transport layer) load balancing:**

1. Client ek TCP connection open karta hai LB ke virtual IP (VIP) pe. LB transport-layer info — source IP, source port, destination IP, destination port, protocol (the 5-tuple) — dekh ke ek backend choose karta hai.
2. Backend choose karne ke baad LB usually packets ko **forward** kar deta hai (NAT ya Direct Server Return ke through), without parsing the payload. Connection ka pura lifetime ek hi backend pe pinned rehta hai (connection-level stickiness).
3. Kyunki TCP/TLS payload ko decrypt ya parse nahi karna padta, ye extremely fast hai — modern L4 LBs (jaise hardware ya kernel-bypass software) **millions of packets/sec** handle kar sakte hain with **sub-millisecond (microseconds-level)** added latency.
4. TLS yahan **pass-through** hota hai — encrypted bytes seedhe backend tak jaate hain, LB unhe decrypt nahi karta.

**L7 (Application layer) load balancing:**

1. Client LB ke saath ek full TLS handshake aur HTTP connection establish karta hai. LB **TLS terminate** karta hai (decrypt), phir HTTP request ko parse karta hai — method, path, headers, cookies sab readable ho jaate hain.
2. Ab LB content-based routing kar sakta hai: `/api/*` ek service pool ko, `/static/*` doosre ko, `Host: video.example.com` teesre ko. Sticky sessions cookie ke through (request-level, na ki sirf connection-level).
3. LB phir ek **naya connection** (often pooled/keep-alive) backend ke saath banata hai aur request forward karta hai. Ek hi client connection se aane wali alag-alag requests alag-alag backends pe jaa sakti hain.
4. Parsing + TLS termination ki wajah se added latency typically **single-digit milliseconds (~1-5 ms)** range mein hoti hai — L4 se zyada, par bohot capable hardware/software pe abhi bhi tens-to-hundreds of thousands of requests/sec realistic hai.

Mental model: ek typical setup mein client → L7 LB (HTTP routing, TLS termination, request retries) → backend pools. Ya cloud mein, ek global L4 LB (jaise NLB) traffic ko regional L7 LBs (jaise ALB / Envoy) pe spread karta hai — dono layers ek saath bhi use hote hain.

## Tradeoffs & Variants

- **Speed vs intelligence:** L4 fast aur cheap (no payload parsing, microsecond latency), par dumb — sirf IP/port pe route kar sakta hai. L7 slower (ms-level, CPU for TLS+parsing) par smart — path/header/cookie based routing, retries, rewrites, content-aware load distribution.
- **TLS termination:** L7 ko TLS terminate karna padta hai routing decisions ke liye → LB pe cert management aur CPU cost, par backend se LB tak ka load uthata hai (TLS offload). L4 pass-through mein end-to-end encryption preserve hota hai, lekin LB content nahi dekh sakta.
- **Stickiness granularity:** L4 = connection-level stickiness (ek TCP connection ek backend pe). L7 = request-level routing + cookie-based session affinity, jo zyada flexible hai.
- **Protocol awareness:** L7 features jaise HTTP/2, gRPC routing, header-based canary, WAF (web application firewall) sirf application layer pe possible hain. L4 protocol-agnostic hai — TCP/UDP kuch bhi (databases, custom protocols, game servers) balance kar sakta hai jahan L7 ko protocol samajh hi nahi aata.
- **Failure detection:** L4 health check usually shallow (TCP connect succeed?). L7 deep health check kar sakta hai (HTTP `GET /health` → 200 expect karo), to ye actually broken-but-listening backends ko bhi detect kar leta hai.

## When To Use It

- **L4 use karo jab:** ultra-low latency / high throughput chahiye, non-HTTP protocols (TCP/UDP — databases, message brokers, gaming, VoIP) balance karne hain, ya end-to-end TLS preserve karna hai. Examples: AWS **Network Load Balancer (NLB)**, Google **Maglev**, **LVS/IPVS**.
- **L7 use karo jab:** content-based routing chahiye (path/host/header se microservices ke beech split), TLS offload, sticky sessions via cookie, A/B testing / canary, ya WAF. Examples: AWS **Application Load Balancer (ALB)**, **NGINX**, **HAProxy**, **Envoy** (service mesh ka data plane), GCP HTTPS LB.
- **Dono saath:** Bade systems mein typically ek L4 LB front pe (raw throughput + DDoS absorption) aur peeche L7 LBs (smart routing). Interviewer ko ye "layered" answer impress karta hai.

## Common Interview Gotchas

- **"L7 hamesha better hai" — galat:** L7 zyada features deta hai par latency aur CPU cost ke saath. Database connections ya gRPC streaming jaise cases mein L4 often better choice hai. Right answer is "depends on requirement," not "always L7."
- **L4 payload nahi dekh sakta, isliye URL-based routing impossible:** Bohot log keh dete hain "L4 se `/api` ko alag backend pe bhejo" — ye nahi ho sakta, kyunki L4 ko HTTP path dikhta hi nahi (wo encrypted/un-parsed payload hai). Path-based routing strictly L7 cheez hai.
- **TLS pass-through vs termination confusion:** L4 = pass-through (LB encrypted bytes forward karta hai, decrypt nahi karta). L7 = termination (LB decrypt karta hai). Agar L7 ko routing karni hai cookies/headers pe, to usko TLS terminate karna **hi** padega — encrypted content padha nahi jaa sakta.
- **OSI layer number rough hai:** Interview mein "L4 vs L7" ek practical distinction hai (transport vs application), strict academic OSI model nahi. TLS technically L5/6 pe baithta hai par practically L7 LB hi usko terminate karta hai — over-pedantic mat bano.
- **Stickiness aur load balance ka tension:** Sticky sessions (chahe L4 connection-level ho ya L7 cookie-based) ek server ko overload kar sakte hain agar ek client heavy ho — perfect even distribution aur stickiness dono ek saath fully achieve nahi hote. Ye tradeoff explicitly mention karo.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_load_balancers_l4_l7.md`](../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_load_balancers_l4_l7.md) — `sysd-buddy quiz scaffold load-balancers-l4-l7` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update load-balancers-l4-l7 --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — L4 vs L7 routing path, TLS termination, aur content-based routing ka interactive diagram.
