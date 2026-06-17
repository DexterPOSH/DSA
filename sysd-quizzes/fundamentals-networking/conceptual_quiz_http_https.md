# HTTP & HTTPS — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update http-https --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines: what is HTTP, and what exactly does HTTPS add on top of it?

**Ideal answer:**
- HTTP = stateless, application-layer request/response protocol between client and server; uses methods (GET/POST/etc.), headers, and status codes.
- HTTPS = HTTP running over a **TLS** layer.
- TLS adds three guarantees: **confidentiality** (encryption), **integrity** (tamper detection), and **server authentication** (via certificates). Mentioning all three, not just "encryption," is the key signal.

## Q2 (core)
Walk through what happens during a TLS handshake when a browser connects to `https://bank.com`. Why isn't the actual page data encrypted with the certificate's key?

**Ideal answer:**
- ClientHello (TLS versions, cipher suites, random nonce) → ServerHello + server **certificate** (public key + CA signature).
- Client verifies the cert chain up to a trusted **CA** — this is the authentication / anti-MITM step.
- Both sides derive a shared **symmetric session key** (TLS 1.3 uses ECDHE key exchange, gives forward secrecy).
- Application data is encrypted with the fast **symmetric** key (e.g. AES-GCM), NOT the certificate's asymmetric key.
- Reason: asymmetric crypto is slow; it's used only for the handshake (auth + key exchange), then symmetric crypto handles bulk data.
- Bonus: TLS 1.3 handshake is 1 RTT (0-RTT on resumption); TLS 1.2 was 2 RTTs.

## Q3 (tradeoff)
Compare HTTP/1.1, HTTP/2, and HTTP/3. When would HTTP/3 actually beat HTTP/2, and what's the catch?

**Ideal answer:**
- HTTP/1.1: one request at a time per connection → application-level head-of-line (HoL) blocking; browsers open ~6 parallel connections per host to compensate.
- HTTP/2: **multiplexed streams** over a single TCP connection + header compression (HPACK); fixes app-level HoL. But a single TCP packet loss stalls ALL streams (TCP-level HoL blocking).
- HTTP/3: runs over **QUIC (UDP)**; streams are independent, so a lost packet affects only its own stream. TLS 1.3 built in, 0/1-RTT setup.
- HTTP/3 wins on **lossy / high-latency networks** (mobile, global users) where TCP HoL hurts.
- Catch: QUIC is UDP-based, so some firewalls/middleboxes block it → must fall back to HTTP/2.

## Q4 (gotcha)
"HTTP is stateless, so how does staying logged in work?" Also: a candidate says `POST` and `PUT` are interchangeable. Are they?

**Ideal answer:**
- Statelessness: the **server** treats each request independently; state isn't stored implicitly across requests. Login state is carried by the **client** via cookies / tokens (e.g. session ID or JWT) sent on every request; server looks it up (Redis session store) or reconstructs it (stateless JWT). This is what makes horizontal scaling easy.
- POST vs PUT: NOT interchangeable. **POST is non-idempotent** (repeating it can create multiple resources); **PUT is idempotent** (replaces a resource at a known URI; repeating yields the same state). PUT can also create if the client picks the ID. Idempotency drives safe retry logic.

## Q5 (applied)
You're designing a public-facing API plus internal microservices. Where do you terminate TLS, and would you ever use mTLS? Justify.

**Ideal answer:**
- Public edge: terminate TLS at a **load balancer / reverse proxy** (NGINX, Envoy, ALB) — centralizes cert management, offloads encryption CPU; internal hop can be plain HTTP for simplicity/efficiency within a trusted network.
- HTTPS is mandatory for all public traffic (privacy, integrity against ISP/ad injection, auth; browsers flag plain HTTP; HTTP/2-3 effectively require it).
- **mTLS** (mutual TLS — both client and server present/verify certs) for **service-to-service** internal comms in a **zero-trust** model — common in service meshes (Istio, Linkerd). Tradeoff: stronger security but operationally heavier (cert issuance/rotation).
- Strong answers note end-to-end vs edge-termination tradeoff and that mTLS adds the client-authentication leg that normal HTTPS lacks.
</content>
