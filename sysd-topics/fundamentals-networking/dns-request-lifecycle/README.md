# DNS & Request Lifecycle

**Track:** Building Blocks
**Category:** Fundamentals & Networking

## What It Is

DNS (Domain Name System) internet ka phonebook hai — `www.example.com` jaise
human-friendly naam ko machine-friendly IP address (`93.184.216.34`) me translate
karta hai; aur "request lifecycle" woh poori journey hai jo browser me URL type
karne se le kar page render hone tak chalti hai.

## Real-World Analogy

Socho tumhe kisi office ko phone karna hai but number yaad nahi. Pehle apni **phone
contacts** check karte ho (browser cache). Nahi mila to ek **dost** ko poochte ho
jo directories jaanta hai (recursive resolver). Dost ko bhi nahi pata to wo
**master directory** (root) se poochta hai "yeh `.com` waale numbers kaun rakhta
hai?", phir **city directory** (TLD `.com`) se exact office ka front desk number
leta hai (authoritative nameserver), aur front desk se actual **extension** (IP)
milta hai. Ek baar mil gaya to dost usse thodi der yaad rakhta hai (caching, TTL)
taaki agli baar dobara na poochna pade.

## How It Works

URL `https://www.example.com` type karke Enter dabaya — ab yeh hota hai:

1. **Browser cache** — kya IP pehle se cached hai? (TTL ke andar) → haan to seedha
   step 8 pe jump.
2. **OS cache + `/etc/hosts`** — OS ka apna resolver cache aur hosts file check.
3. **Recursive resolver** — usually ISP ka ya `8.8.8.8` (Google) / `1.1.1.1`
   (Cloudflare). Yeh saari mehnat karta hai client ke behalf pe.
4. **Root nameserver** → "`.com` kaun handle karta hai?" → TLD nameserver ka pata
   deta hai. (13 logical root server addresses, Anycast se globally replicated.)
5. **TLD nameserver (`.com`)** → "`example.com` ka authoritative server kaun hai?"
   → authoritative NS ka pata.
6. **Authoritative nameserver** → actual **A record** (IPv4) ya **AAAA** (IPv6)
   return karta hai → `93.184.216.34`.
7. **Resolver caches** the answer (TTL tak) aur client ko IP de deta hai.
8. **TCP handshake** — client ↔ server (port 443): `SYN → SYN-ACK → ACK`.
9. **TLS handshake** — `ClientHello / ServerHello / certificate / key exchange` →
   encrypted channel ban gaya (HTTPS).
10. **HTTP request** — `GET /` server ko (aksar CDN edge ya load balancer ke
    through) → server **HTTP response** bhejta hai.
11. **Browser render** — HTML parse, CSS/JS fetch (har asset apni request), paint.

**Latency intuition:** cached lookup ≈ 0ms. Cold lookup = multiple round trips
(root → TLD → authoritative), often **tens-to-hundreds of ms**. Isiliye caching
har layer pe hota hai.

## Tradeoffs & Variants

- **Record types:** `A` (IPv4), `AAAA` (IPv6), `CNAME` (alias → another name),
  `NS` (delegation), `MX` (mail), `TXT` (verification/SPF).
- **TTL tradeoff:** high TTL = fewer lookups, faster, but stale records linger
  on failover/migration. Low TTL = quick failover but more DNS traffic. Migration
  se pehle TTL ghata dete hain.
- **GeoDNS / latency-based routing:** authoritative server location/health ke
  hisaab se alag IP deta hai → user ko nearest datacenter/CDN edge.
- **Anycast:** ek hi IP multiple physical locations pe advertise — BGP nearest
  ko route karta hai. Root servers aur CDNs isi pe chalte hain.
- **Recursive vs iterative:** resolver iteratively root→TLD→auth poochta hai, par
  client ke liye ek recursive call jaisa dikhta hai.

## When To Use It

Har system design discussion ka **entry point**. Jab bhi "user request kaise
pohonchti hai service tak", multi-region routing, CDN, failover, ya "why is the
first request slow" jaise sawaal aaye → yeh lifecycle samajhna padta hai. Service
discovery aur load balancing isi ke upar baithta hai.

## Common Interview Gotchas

1. **DNS ≠ single server** — yeh ek distributed hierarchy hai (root → TLD → auth),
   har level alag entity manage karta hai.
2. **DNS mostly UDP port 53** (fast, single packet); response bada ho (DNSSEC,
   zone transfer) to **TCP** pe fallback.
3. **Caching everywhere** — browser, OS, resolver. "First request slow, baaki
   fast" ka reason yahi hai (warm cache).
4. **TTL ka role failover me** — low TTL na ho to clients purane (dead) IP pe
   request bhejte rehte hain.
5. **CNAME chains** extra lookups add karte hain (latency); apex/root domain pe
   CNAME allowed nahi (ALIAS/ANAME use hota hai).
6. **DNS load balancing weak hai** — round-robin DNS client caching ki wajah se
   uneven; real LB ek L4/L7 load balancer karta hai, DNS sirf entry point deta hai.

## Practice

- Quiz: `sysd-quizzes/fundamentals-networking/conceptual_quiz_dns_request_lifecycle.md`
- Run a quiz: invoke the **sysd-quiz** skill / `sysd-buddy quiz scaffold dns-request-lifecycle`
- Visual: open `sysd-topics/fundamentals-networking/dns-request-lifecycle/visual.html`
