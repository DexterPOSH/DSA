# Distributed Locks — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update distributed-locks --quiz-score N/M` -->

## Q1 (warm-up)
What is a distributed lock, and how is it different from a normal in-process mutex/lock that you'd use inside a single program?

**Ideal answer:**
- A distributed lock provides **mutual exclusion across multiple processes/machines** over a network — ensuring only one process accesses a shared resource or critical section at a time.
- A normal mutex lives inside one process's memory and only coordinates threads of that single process; it cannot coordinate across machines.
- A distributed lock needs an external shared store (Redis, ZooKeeper, etcd) as the source of truth, and must tolerate network failures, partial failures, and crashes — concerns a local mutex never faces.
- Bonus: because the holder can crash or get partitioned, distributed locks almost always need a **lease/TTL**, unlike a local mutex.

## Q2 (core)
Walk through how you'd implement a basic distributed lock with Redis. Why must both the acquire and the release be atomic, and what does the release look like?

**Ideal answer:**
- **Acquire:** a single atomic `SET <key> <unique-token> NX PX <ttl>` — `NX` sets only if the key doesn't exist (lock is free), `PX` sets a TTL so the lock auto-expires.
- Store a **unique random token (e.g., UUID)** as the value so the owner can be identified.
- **Release must be atomic compare-and-delete:** check that the stored token equals my token, and only then delete — done via a Lua script (`if get == mytoken then del`) or a transaction.
- Why atomic: a naive `GET` then `DEL` has a race — between the two calls the lock can expire and be re-acquired by someone else, and you'd delete *their* lock.
- The TTL is the safety net: if the holder crashes before releasing, the lock auto-expires so the system isn't permanently deadlocked.

## Q3 (tradeoff)
When would you choose a CP store like ZooKeeper/etcd for locking versus a single Redis instance? What are you trading off?

**Ideal answer:**
- **Redis (AP-leaning, single node):** fast (sub-ms to ~1-2 ms acquire), simple, high throughput — but a single point of failure, and with async replication a failover can create a window where two clients both hold the lock. Default posture favors availability over strict correctness.
- **ZooKeeper / etcd (CP):** built on consensus (ZAB / Raft), giving linearizable, fault-tolerant locks (ephemeral znodes / lease keys) — better correctness — at the cost of higher latency (single-digit to low double-digit ms) and operational complexity.
- **Decision rule:** if a wrong lock causes real data corruption (money, inventory) → CP store; if the lock is only an efficiency optimization (avoid doing the same work twice) → Redis is fine.
- Bonus: Redlock (multi-Redis-node majority) improves availability but is debated for correctness under GC/clock-skew.

## Q4 (gotcha)
A client acquires a 30-second lease, then suffers a 40-second GC pause. Meanwhile another client acquires the same lock. Now both think they hold it. Does adding more Redis nodes (Redlock) fix this? What actually fixes it?

**Ideal answer:**
- **No — more Redis nodes / Redlock does not fix this.** The problem is timing/process-pause based, not a quorum/availability problem. Any purely lease-based lock can be violated when the holder pauses (GC, VM freeze) or is network-delayed long enough for the lease to expire.
- The real fix is **fencing tokens:** the lock service hands out a monotonically increasing number with each grant. The client includes this token on every write to the protected resource, and the resource (DB/storage) **rejects writes carrying an older (smaller) token**.
- This makes the stale holder's late write harmless — even if two clients momentarily think they hold the lock, only the one with the newest token can mutate the resource.
- Key insight: locks/leases are about timing assumptions you can't fully trust; fencing pushes the correctness check to the resource itself.

## Q5 (applied)
You're running a fleet of 10 identical service instances and a scheduled job must run on exactly one instance every minute. How would you use a distributed lock here, and what should you watch out for?

**Ideal answer:**
- Use the lock for **leader election / single-runner:** all 10 instances try to acquire a lock (e.g., `cron:nightly-report`) with a TTL; whoever wins runs the job, the rest skip.
- A natural fit is etcd/ZooKeeper lease-based election (this is how Kubernetes leader election works via `Lease` objects), or a Redis lock if occasional double-runs are tolerable.
- **Watch out for:** set a TTL so a crashed leader's lock auto-releases and another instance can take over; use a **watchdog/renewal** if the job can run longer than the TTL so the lease doesn't expire mid-job.
- Consider whether double execution is actually harmful — if the job is **idempotent**, a brief overlap is harmless and you can favor a simpler/available lock; if not (e.g., sends emails, charges money), prefer a CP store and/or fencing/idempotency keys.
- Bonus: don't forget the release should be token-checked, and the lock should not become a hidden single point of failure for the whole schedule.
