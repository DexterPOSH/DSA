# Reverse Proxy — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update reverse-proxy --quiz-score N/M` -->

## Q1 (warm-up)
In one or two sentences, what is a reverse proxy, and where does it sit relative to clients and backend servers?

**Ideal answer:**
- A reverse proxy is a server that sits *in front of* one or more backend servers, between the clients and those backends.
- Clients send requests to the proxy (a single public entry point); the proxy forwards each request to an appropriate backend and returns the response.
- Key effect: backends are never directly exposed to clients — clients only know the proxy's address.

## Q2 (core)
Walk through what a reverse proxy actually does to a typical inbound HTTPS request, from the moment it arrives to the moment a response goes back. Name at least four distinct responsibilities.

**Ideal answer:**
- **TLS termination:** decrypts the HTTPS connection at the proxy (handles the handshake/certs centrally), often talking plain HTTP or internal mTLS to backends.
- **Routing:** inspects `Host` header / URL path / headers to pick the right backend pool (path-based or host-based routing).
- **Load balancing + health checks:** selects a healthy backend within the pool via round-robin / least-connections / weighted / hash, removing failed backends via health checks.
- **Connection pooling:** keeps separate client and backend connections, reusing a warm backend pool so many slow clients map to few backend connections.
- Bonus credit: caching cacheable responses, compression (gzip/brotli), rate limiting, header rewriting (e.g. adding `X-Forwarded-For`), logging/metrics — all at one central layer.

## Q3 (tradeoff)
A reverse proxy concentrates all traffic through one layer. What are the main downsides of that, and how do you mitigate them?

**Ideal answer:**
- **Single point of failure:** everything flows through the proxy, so if it dies the whole service is down. Mitigate with multiple redundant proxy instances behind a floating VIP / DNS failover / Anycast.
- **Extra network hop / added latency:** every request takes an additional hop (usually sub-ms intra-DC but real); the payoff is centralization of cross-cutting concerns.
- **Operational complexity:** another tier to deploy, scale, monitor, and patch.
- Good answers may also mention caching staleness risk and the cost/complexity of the TLS-terminate vs passthrough decision (L7 features vs end-to-end encryption).

## Q4 (gotcha)
Many candidates conflate a reverse proxy with a forward proxy, and a reverse proxy with a load balancer. Clear up both distinctions.

**Ideal answer:**
- **Reverse vs forward proxy:** a reverse proxy sits in front of *servers* and hides the backends from clients (clients don't know which server served them). A forward proxy sits in front of *clients* and hides the clients from servers (e.g. a corporate egress proxy / VPN); the destination server doesn't see the real client.
- **Reverse proxy vs load balancer:** load balancing is *one feature* of a reverse proxy, not its identity. A reverse proxy can be useful with a single backend (e.g. just for TLS termination or caching). Also: an L4 load balancer forwards TCP/UDP without understanding HTTP, whereas an L7 reverse proxy understands HTTP and can do path routing, caching, header rewriting, etc.

## Q5 (applied)
You're putting a reverse proxy in front of a fleet of stateful application servers that keep user session data in local memory. What problems arise, and how would you handle client IP and session affinity correctly?

**Ideal answer:**
- **Lost client IP:** backends see the proxy's IP, not the real client. The proxy must add `X-Forwarded-For` / `Forwarded`, and backends must trust it *only* when it comes from the trusted proxy (it can be spoofed otherwise). Any client-IP-based logic (rate limiting, geo, logging) depends on this.
- **Session affinity problem:** with local in-memory session state, plain round-robin breaks — a user's next request may hit a different backend and appear logged out. Fix by either (a) sticky sessions / session affinity (route a user consistently to the same backend, e.g. via cookie or IP hash), or (b) better: externalize session state to a shared store (e.g. Redis) so backends are stateless and any backend can serve any request.
- Strong answers note that (b) is generally preferred because stickiness undermines even load distribution and complicates scaling/failover.
