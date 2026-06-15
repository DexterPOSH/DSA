# REST vs RPC vs GraphQL — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update rest-rpc-graphql --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines each, define REST, RPC, and GraphQL — and call out the core mental model that distinguishes them (what is the "unit" you talk to the server in)?

**Ideal answer:**
- **REST** = resource-oriented; you act on nouns (URLs like `/users/42`) using standard HTTP verbs (`GET/POST/PUT/DELETE`). Stateless.
- **RPC** = action/verb-oriented; you call a remote function like a local one (`getUser(42)`); modern form is gRPC over HTTP/2 with Protobuf.
- **GraphQL** = single endpoint + a query language; client asks for exactly the fields it wants and gets that shape back.
- Key distinction: REST talks in **resources/nouns**, RPC in **functions/verbs**, GraphQL in **declarative queries** over a typed schema.

## Q2 (core)
Walk through what physically happens when a gRPC call is made versus a GraphQL query. Mention the transport, the wire format, and one capability each unlocks.

**Ideal answer:**
- **gRPC:** client calls a generated stub → args serialized via **Protocol Buffers (binary)** → sent over **HTTP/2** (multiplexed streams on one TCP connection) → server stub deserializes, runs method, returns. Unlocks **bidirectional streaming** and compact/fast payloads (binary, ~30-60% smaller than JSON); contract is a `.proto` with codegen + compile-time type safety.
- **GraphQL:** client `POST`s a query to a single `/graphql` endpoint → server **parses + validates** against the schema → builds an execution tree → runs a **resolver** per field (data can come from DB/other services) → assembles response in the exact query shape. Unlocks **no over/under-fetching** and fetching nested/related data in one round-trip.
- Bonus: gRPC binary/HTTP-2 vs GraphQL JSON/HTTP-1.1-or-2; resolvers are per-field functions.

## Q3 (tradeoff)
A mobile dashboard needs a user's profile, their last 5 orders, and product recommendations. Compare how REST, gRPC, and GraphQL would each serve this, and which you'd pick for a bandwidth-constrained mobile client.

**Ideal answer:**
- **REST:** typically **3 round-trips** (`/users/42`, `/users/42/orders`, `/recommendations?user=42`) → under-fetching, more latency on mobile (~50-150 ms each); or a fat custom endpoint that over-fetches bytes.
- **gRPC:** you'd design an **aggregate method** (e.g. `GetDashboard`) returning a combined Protobuf message — compact and fast, but you hand-build the aggregation and browsers need gRPC-Web.
- **GraphQL:** **one query** returns exactly profile + 5 orders + recommendations in one round-trip, only the requested fields → minimal payload.
- For bandwidth-constrained mobile, **GraphQL** usually wins (one round-trip, no over-fetch). Caveat: watch the N+1 resolver problem and caching cost. (gRPC is the better answer for internal service-to-service, not browser/mobile-facing.)

## Q4 (gotcha)
"GraphQL is always faster than REST, and REST just means JSON over HTTP." Both halves are flawed — correct them.

**Ideal answer:**
- **"GraphQL always faster" is wrong:** GraphQL saves round-trips and trims payloads, but for a single simple lookup REST is often simpler and CDN-cacheable. Naive GraphQL resolvers cause the **N+1 problem** (one query → hundreds of DB hits) unless you add **DataLoader** batching. GraphQL also makes HTTP/CDN caching harder (POST queries, variable shapes).
- **"REST = JSON over HTTP" is wrong:** REST is an **architectural style** — resources, statelessness, uniform interface, HTTP verbs, (and ideally HATEOAS/hypermedia). JSON is just a common convention; the format isn't what makes it REST. "JSON over HTTP" alone is RPC-ish, not necessarily RESTful.
- Bonus: mention GraphQL query-depth/complexity DoS risk and that REST's strength is built-in HTTP caching (`ETag`, `Cache-Control`).

## Q5 (applied)
You're designing a system with many internal microservices plus public web and mobile clients. Which protocol(s) would you use at which layer, and name a real system that matches each choice.

**Ideal answer:**
- **Internal service-to-service (east-west):** **gRPC** — low latency, high throughput, Protobuf + codegen for polyglot services, streaming. Real: Google internally, service meshes (Envoy/Istio), Netflix/Uber backends.
- **Public-facing API:** **REST** when CRUD-heavy, broad client compatibility, and HTTP caching matter. Real: Stripe, GitHub v3.
- **Aggregation/BFF layer for web + mobile:** **GraphQL** to let each screen request its own data shape and aggregate multiple backends in one round-trip. Real: Facebook (originator), GitHub v4, Shopify, Netflix BFF.
- Key insight: these are **not mutually exclusive** — a common pattern is gRPC internally with a gateway/BFF exposing REST or GraphQL externally. Mentioning trade-offs (caching, browser support via gRPC-Web, N+1) earns full marks.
