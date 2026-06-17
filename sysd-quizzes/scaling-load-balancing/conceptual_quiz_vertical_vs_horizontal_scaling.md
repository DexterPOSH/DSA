# Vertical vs Horizontal Scaling — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update vertical-vs-horizontal-scaling --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines each, define vertical scaling (scale up) and horizontal scaling (scale out).

**Ideal answer:**
- Vertical scaling = ek single machine ko zyada powerful banana (more CPU/RAM/disk on the same box). Also called "scale up."
- Horizontal scaling = zyada machines add karke load unke beech distribute karna. Also called "scale out."
- Bonus: vertical = grow one node; horizontal = add more nodes, usually behind a load balancer.

## Q2 (core)
When you horizontally scale a service, what extra component(s) do you need, and why is scaling a stateless web tier much easier than scaling a stateful database?

**Ideal answer:**
- Need a **load balancer** in front to distribute requests across the replicas (round-robin / least-connections / consistent hashing).
- **Stateless tier:** koi local state nahi, so any replica can serve any request — bas ek aur identical instance add karo aur LB pool mein register kar do. Near-instant, zero-downtime.
- **Stateful DB:** data ko machines ke beech baantna padta hai. Options: replication (primary + read replicas) and/or sharding/partitioning. Ye consistency, replication lag, cross-shard joins/transactions jaise hard problems introduce karta hai.
- Key insight: state ko bahar push karna (Redis/DB/object store) makes a tier stateless and easy to scale out.

## Q3 (tradeoff)
Compare vertical vs horizontal scaling on at least three axes (e.g. ceiling, availability, cost, complexity, downtime). Which is "simpler" and why?

**Ideal answer:**
- **Ceiling:** vertical has a hard physical limit (biggest box is finite); horizontal is effectively unbounded.
- **Availability/SPOF:** a single vertically-scaled box is a single point of failure; horizontal has built-in redundancy (one node dies, others serve).
- **Cost:** vertical cost is super-linear (2x power often costs more than 2x — high-end hardware premium); horizontal uses commodity hardware, more linear, but adds operational/coordination cost.
- **Complexity:** vertical is simpler — no distributed-systems problems (no consistency/partition headaches). Horizontal pulls you into CAP-theorem territory.
- **Downtime:** vertical resize usually needs a reboot (downtime); horizontal can add nodes with zero downtime.
- "Simpler" = vertical, because there is no coordination/consistency to manage.

## Q4 (gotcha)
A candidate says "horizontal scaling is always better, and N nodes give you N times the throughput." What's wrong with both halves of that statement?

**Ideal answer:**
- "Always better" is false: horizontal adds coordination cost (consistency, replication lag, distributed transactions, ops complexity). For small or stateful workloads, vertical is often simpler and cheaper. Don't distribute prematurely.
- "N nodes = N× throughput" is false: real speedup is **sublinear** due to coordination overhead, load imbalance, and shared bottlenecks (e.g. a single primary DB). Amdahl's law — the serial fraction (like writes to one primary) caps overall scaling.
- Bonus: even horizontal isn't truly infinite — a shared component (single primary, central lock service) or network saturation eventually bottlenecks; linear cost only holds for genuinely shared-nothing designs.

## Q5 (applied)
You run a read-heavy social app. The stateless API tier is fine, but the single Postgres database is maxing out. Walk through how you'd scale the database, and in what order.

**Ideal answer:**
- **Step 1 — vertical first:** upgrade the DB instance (bigger CPU/RAM) — simplest, no app changes, no distributed-systems complexity. Often buys a lot of headroom (e.g. 2000 → 8000 QPS).
- **Step 2 — read replicas:** since it's read-heavy, add read replicas; route reads to replicas, writes to the primary. Scales reads well. Mention replication lag → reads may be slightly stale (eventual consistency).
- **Step 3 — caching:** put a cache (Redis/Memcached) in front for hot reads to offload the DB further.
- **Step 4 — sharding (last resort):** if writes are the bottleneck, shard/partition by key (e.g. user_id) across machines. Accept the cost: cross-shard queries/joins and transactions become hard.
- Good answer recognizes: scale up before scale out for stateful DBs, exploit the read-heavy nature with replicas + cache, and treat sharding as the heavy last step.
