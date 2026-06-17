# Stateless Services & Sessions — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update stateless-services-sessions --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines, what does it mean for a service to be "stateless"? Does stateless mean there is no state anywhere in the system?

**Ideal answer:**
- Stateless = a service instance does not keep any per-client state in its own local memory/RAM between requests; each request is self-contained (carries its own context, usually a token).
- It does NOT mean there is no state in the system — state still exists, but it is externalized (Redis/DB) or carried by the client (JWT/session token).
- Key consequence: any instance can serve any request, so instances are interchangeable.

## Q2 (core)
Walk through how a stateless web service handles an authenticated request such that any instance behind the load balancer can serve it. Where does the session state actually live?

**Ideal answer:**
- Client sends an identity proof on every request — typically a session token / JWT in the `Authorization` header.
- The instance does not store the user's session in local RAM; it either (a) looks the session up in a shared external store (Redis/Memcached), or (b) verifies a self-contained signed JWT (signature check, no network call).
- State lives in an external store (server-side sessions) or inside the token itself (JWT) — not in the instance.
- Because no local state is needed, the LB can route to any instance (round-robin/least-connections); failures and rolling deploys don't lose sessions.
- Bonus: external store lookups are fast (in-memory, ~sub-ms to ~1-2 ms same-AZ).

## Q3 (tradeoff)
Compare opaque server-side session IDs (backed by a store) versus self-contained JWTs. What do you gain and lose with each?

**Ideal answer:**
- Server-side session ID: server looks it up in Redis on each request. Gain: instant revocation (delete the key → session dead); small token. Lose: a store round-trip on every request; store becomes a critical dependency/SPOF that must be replicated.
- JWT: signed, self-contained claims; server verifies the signature locally (CPU only, no lookup). Gain: no store round-trip, very fast, fewer dependencies. Lose: hard to revoke before expiry; larger payload (~200 B–1 KB) sent on every request.
- Common resolution: short-lived access JWT (5–15 min) + long-lived, server-side-revocable refresh token to bound the revocation gap.

## Q4 (gotcha)
A candidate says: "I'll just use sticky sessions on the load balancer, so I don't need an external session store — that keeps things stateless and scalable." What's wrong with this reasoning?

**Ideal answer:**
- Sticky sessions are NOT stateless — they keep per-client state in one instance's local memory and use LB affinity (cookie/IP hash) as a routing crutch. This is a stateful design.
- Problems: uneven load (a hot instance keeps getting its pinned clients), and if that instance dies/restarts (or during a rolling deploy), all its in-memory sessions are lost — users get logged out.
- It also undermines autoscaling: new instances can't take over existing sessions.
- The correct stateless approach externalizes session state (Redis) or uses tokens (JWT) so any instance can serve any request.

## Q5 (applied)
You're designing the API tier for a service that must autoscale from ~10K to ~50K QPS during peak and run on Kubernetes with an HPA. How does a stateless design make this work, and what new dependency/risk does it introduce?

**Ideal answer:**
- Make instances share-nothing: no per-client state in pod memory; sessions in Redis or carried as JWTs. This makes pods interchangeable so the HPA can freely add/remove pods and the LB can route to any of them.
- Scale-out is trivial and fast: new pods have no local state to warm up; a dying pod just gets pulled from rotation and its user's session survives in the external store. Rolling deploys don't drop sessions.
- New risk: the external session store (Redis) becomes a critical dependency / potential SPOF and a per-request latency cost (~1 ms + network); it must be replicated (Sentinel/Cluster) and lookups optimized. JWTs can reduce store load by avoiding lookups, at the cost of harder revocation.
- Good mention of real patterns: ALB/ASG or K8s Deployment + HPA, Twelve-Factor "share-nothing" processes, serverless analog.
