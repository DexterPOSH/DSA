# CDN — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update cdn --quiz-score N/M` -->

## Q1 (warm-up)
In one or two sentences, what is a CDN and what core problem does it solve?

**Ideal answer:**
- A CDN is a geographically distributed network of edge servers (PoPs) that cache and serve content from a location close to the user.
- Core problems solved: (1) reduce latency by serving from a nearby edge instead of a faraway origin, and (2) offload the origin server by absorbing most read traffic at the edge.
- Bonus: also helps with availability, traffic-spike absorption, and DDoS mitigation.

## Q2 (core)
Walk through what happens, step by step, when a user requests an object the first time vs. a second time from the same region. Use the terms cache HIT, cache MISS, origin fetch, and TTL.

**Ideal answer:**
- Request is routed (via DNS/Anycast) to the nearest edge PoP.
- Edge computes a cache key (typically URL + relevant headers) and checks its cache.
- First request → cache MISS: edge does an origin fetch (often via a shield/mid-tier cache), stores the object, and returns it. This first user pays the full origin RTT.
- Object is cached with a freshness lifetime from TTL (e.g. `Cache-Control: max-age`).
- Second request (object still fresh) → cache HIT: served directly from edge in single-digit ms, origin not touched.
- After TTL expires, edge revalidates with origin (ETag / If-None-Match), getting a `304 Not Modified` if unchanged.

## Q3 (tradeoff)
You're choosing TTLs for two asset types: a versioned JS bundle (`app.a1b2c3.js`) and the site's HTML page. How would you set TTLs and why? What's the general long-vs-short TTL tradeoff?

**Ideal answer:**
- General tradeoff: long TTL → higher hit ratio and lower origin load, but higher staleness risk; short TTL → fresher content but more origin/revalidation traffic.
- Versioned/immutable assets (`app.a1b2c3.js`): very long TTL, ideally `immutable`, because the URL changes whenever content changes, so there's no staleness risk.
- HTML page: short TTL (or revalidate each time), because it changes frequently and points to the versioned assets.
- Mentions the pattern of decoupling: long-lived versioned assets + short-lived HTML entry point.

## Q4 (gotcha)
A user reports they're still seeing an old (wrong) price on a product page hours after it was fixed at the origin. The page had a 24-hour TTL. What's going on, and what's the difference between TTL expiry and purge/invalidation?

**Ideal answer:**
- The edge is serving a still-fresh cached copy; with a 24h TTL it won't revalidate until expiry, so the stale price persists.
- TTL expiry is passive: the object becomes stale on its own after the lifetime elapses.
- Purge/invalidation is active: you call the CDN's purge API to immediately evict the object from edges (propagates in seconds-to-minutes).
- Right fix is a combination: trigger a targeted purge now, and going forward use sensible TTLs and/or versioned URLs (and short TTL for frequently-changing pages) so correctness-critical content can be updated promptly.

## Q5 (applied)
You're designing a global news + live-video site. Where and how would you apply a CDN, and what would you NOT route through it? Name a metric you'd watch.

**Ideal answer:**
- Put static assets (JS/CSS/images) and video segments (HLS/DASH) behind the CDN — highly cacheable, globally distributed users benefit from edge proximity.
- Use the CDN to absorb traffic spikes (breaking news) and as a DDoS buffer in front of origin.
- For dynamic/personalized content (logged-in feed, account pages) either bypass the cache, use very short micro-caching, or use edge compute with a carefully designed cache key (avoid serving one user's personalized data to another).
- Don't route writes/transactions/source-of-truth through the cache — origin still owns those.
- Key metric: cache hit ratio (also origin offload %, p95 latency); mentions that a low hit ratio means the CDN is being bypassed and origin is still loaded.
