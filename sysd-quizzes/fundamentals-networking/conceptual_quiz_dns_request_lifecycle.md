# DNS & Request Lifecycle — Conceptual Quiz

<!-- Agent (sysd-quiz skill): grade the user conversationally against each Ideal
     answer, then record the score with:
     `sysd-buddy progress update dns-request-lifecycle --quiz-score N/M` -->

## Q1 (warm-up)
What does DNS do, and walk me through the chain of servers a recursive resolver contacts to resolve `www.example.com` from cold.

**Ideal answer:** DNS maps a human-readable domain name to an IP address. Cold resolution: recursive resolver → **root** nameserver (returns the `.com` TLD nameserver) → **TLD** nameserver (returns the authoritative nameserver for example.com) → **authoritative** nameserver (returns the A/AAAA record = the IP). Resolver then caches the answer per TTL and returns the IP to the client. Three distinct levels, three distinct entities.

## Q2 (core)
After the resolver returns the IP, what still has to happen before the browser can render the page over HTTPS? List the steps in order.

**Ideal answer:** TCP handshake (SYN → SYN-ACK → ACK) to the server IP on port 443 → TLS handshake (ClientHello/ServerHello/certificate/key exchange) to establish the encrypted channel → HTTP request (GET) sent (often via CDN edge / load balancer) → HTTP response → browser parses HTML, fetches CSS/JS/assets (each its own request) and paints. Bonus: connection reuse (keep-alive / HTTP/2 multiplexing) avoids repeating TCP/TLS per asset.

## Q3 (tradeoff)
Explain the TTL tradeoff on DNS records. Why might you lower TTL before a planned migration?

**Ideal answer:** High TTL → fewer lookups, lower latency, less DNS traffic, but stale records linger (clients keep hitting the old IP after a change). Low TTL → faster propagation/failover but more DNS query volume. Before a migration or failover you lower TTL (e.g. to 60s) ahead of time so clients pick up the new IP quickly once you cut over; raise it again afterward.

## Q4 (gotcha)
A candidate says "we'll just use DNS round-robin to load-balance across our servers." What's wrong or weak about relying on DNS for load balancing?

**Ideal answer:** DNS round-robin is weak because (1) clients/resolvers **cache** the returned record per TTL, so distribution is uneven and sticky; (2) DNS has no health awareness — it can hand out a dead server's IP until TTL expires; (3) no per-request balancing or session affinity. DNS is fine as the **entry point** (often returning a load balancer's / CDN's IP, possibly via GeoDNS), but real balancing is done by an L4/L7 load balancer. Also: DNS is mostly UDP/53 (single packet, fast), falling back to TCP for large responses (DNSSEC, zone transfers).

## Q5 (applied)
Why is the first request to a site often noticeably slower than subsequent ones, and where does caching help across the lifecycle?

**Ideal answer:** The first (cold) request pays the full DNS walk (root→TLD→authoritative = multiple sequential round trips, tens-to-hundreds of ms) plus TCP + TLS handshakes. Subsequent requests are fast because caching happens at every layer: browser DNS cache, OS resolver cache (+ `/etc/hosts`), recursive resolver cache (all per TTL), plus connection reuse (keep-alive/HTTP/2) and TLS session resumption. So a warm cache skips the DNS walk (~0ms) and often the handshakes too. CDNs/edge caching further cut content latency by serving from a nearby PoP (GeoDNS/Anycast routing the user to the closest edge).
