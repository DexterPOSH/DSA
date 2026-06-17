# Load Balancers (L4 vs L7) — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update load-balancers-l4-l7 --quiz-score N/M` -->

## Q1 (warm-up)
In one or two sentences, what is the core difference between an L4 and an L7 load balancer?

**Ideal answer:**
- L4 (transport layer) routes based only on the TCP/UDP 5-tuple — source/dest IP, source/dest port, protocol — without looking at the payload.
- L7 (application layer) parses the actual application data (HTTP method, URL path, headers, cookies) and routes based on content.
- One-liner framing: L4 looks at the "envelope" (IP/port), L7 reads the "letter" (request content).

## Q2 (core)
Walk through what an L7 load balancer does when an HTTPS request arrives that an L4 load balancer does NOT do. Why does this matter for latency?

**Ideal answer:**
- L7 terminates TLS (decrypts the connection) so it can read the plaintext HTTP request.
- It then parses HTTP (method/path/headers/cookies) and makes a content-based routing decision (e.g. `/api/*` → service A, `/static/*` → service B), often opening a separate pooled connection to the backend.
- L4 skips all of this: it just forwards packets based on the 5-tuple (NAT or DSR), TLS stays pass-through (encrypted bytes go straight to backend).
- Latency impact: L4 adds microsecond-level overhead and scales to millions of packets/sec; L7 adds single-digit-millisecond (~1-5 ms) overhead because of TLS termination + parsing + extra connection handling.

## Q3 (tradeoff)
An interviewer says "just always use L7, it's more powerful." How do you push back? Give concrete cases where L4 is the better choice.

**Ideal answer:**
- L7's power (content routing, retries, WAF, rewrites) comes at the cost of latency and CPU (TLS termination + parsing).
- L4 is better when: ultra-low latency / very high throughput is needed; the protocol is non-HTTP (raw TCP/UDP — databases, message brokers, gaming, VoIP) where L7 can't parse it; or end-to-end TLS must be preserved (L4 pass-through doesn't decrypt).
- Correct framing is "it depends on the requirement," not "always L7."
- Bonus: many large systems layer both — L4 in front for raw throughput/DDoS absorption, L7 behind for smart routing.

## Q4 (gotcha)
A candidate proposes: "We'll use an L4 load balancer and route `/api` requests to one backend pool and `/static` to another." What's wrong with this, and what would they actually need?

**Ideal answer:**
- Wrong because L4 only sees IP/port (the 5-tuple), not the HTTP path — for HTTPS the payload is encrypted and even for plaintext L4 doesn't parse it. So path-based routing is impossible at L4.
- Path/host/header/cookie-based routing is strictly an L7 capability.
- For L7 to route on path it must terminate TLS first (you can't read an encrypted request).
- So the fix is: use an L7 load balancer (ALB / NGINX / HAProxy / Envoy) that terminates TLS and routes on the URL path.

## Q5 (applied)
You're designing a system that fronts both a public REST API (HTTPS, microservices behind path-based routing) and a high-throughput real-time multiplayer game backend (custom UDP protocol). How would you use load balancers here, and why?

**Ideal answer:**
- Two different needs → two different LB choices.
- REST API: use an L7 LB (ALB / NGINX / Envoy) for TLS termination, path/host-based routing across microservices, sticky sessions via cookie, retries, and optionally a WAF.
- Game backend: use an L4 LB (NLB / LVS-IPVS / Maglev) because the traffic is UDP (L7 can't parse it), needs very low latency and high packet throughput, and benefits from connection/flow-level stickiness so a player's packets keep hitting the same server.
- Good answer also mentions: L4 health checks are shallow (can-connect), so consider deeper health checks; and you can layer an L4 LB in front of L7 LBs for the API tier if you need extreme scale or DDoS absorption.
