# Replication — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update replication --quiz-score N/M` -->

## Q1 (warm-up)
What is replication, and how is it different from sharding (partitioning)?

**Ideal answer:**
- Replication = keeping multiple *copies of the same data* on different nodes.
- Goals: high availability / fault tolerance, read scaling, and lower latency via locality.
- Sharding/partitioning = splitting *different* data across nodes (write & storage scaling); each node holds only a subset.
- Key distinction: replication copies the same data; sharding divides distinct data. Real systems often do both — partition the data, then replicate each partition.

## Q2 (core)
Explain how single-leader replication works, and the difference between synchronous and asynchronous replication.

**Ideal answer:**
- All writes go to one **leader**; the leader records changes to a replication log (binlog / WAL) and streams them to **followers**, which apply them to their copies.
- Reads can be served from followers → read scaling. Writes funnel through the leader.
- **Synchronous:** leader acks the client only after a follower confirms the write — durable (no loss if leader dies), but adds a round-trip of latency and can stall writes if the follower is slow/down.
- **Asynchronous:** leader acks immediately and propagates later — fast and available, but writes not yet replicated can be lost if the leader crashes.
- Bonus: semi-synchronous (one follower sync, rest async) as the practical middle ground.

## Q3 (tradeoff)
In a leaderless / quorum system with N replicas, W write acks, and R read replicas, what does the condition W + R > N buy you, and what are its limits?

**Ideal answer:**
- `W + R > N` forces the write set and read set to **overlap by at least one replica**, so a read is guaranteed to touch at least one node that has the latest acked write → avoids fully stale reads.
- Example: `N=3, W=2, R=2`. Tuning the knob: higher W/R = stronger consistency but slower/less available; `W=1,R=1` = fastest but stale reads likely.
- Limits: it is **not linearizability** — concurrent writes, sloppy quorums / hinted handoff, and read-repair timing can still surface stale or conflicting values. Conflict resolution (versions/CRDTs) may still be needed.

## Q4 (gotcha)
A service uses asynchronous replication and tells users "your write succeeded." Why might a user still read stale data right after, and what real data-loss risk exists?

**Ideal answer:**
- **Replication lag:** followers trail the leader (ms to seconds under load). If the follow-up read hits a lagging follower, the user sees old data — the read-your-own-writes problem.
- Mitigations: read-your-writes (read from leader after a write), monotonic reads (don't go backwards in time for a user), sticky/lag-aware routing.
- **Data-loss risk:** with async, if the leader crashes before propagating recently-acked writes, those writes are *permanently lost* despite the client receiving `OK`. Failover can also cause split-brain / silently discarded writes — so "we replicate, so we never lose data" is false unless writes are synchronous/quorum-durable.

## Q5 (applied)
You're designing a read-heavy global app (read:write ≈ 100:1) with users across regions. How would you use replication, and what would change if writes also needed to be fast in every region?

**Ideal answer:**
- Read-heavy → **single-leader with multiple read replicas**; scale reads by adding followers, route reads to the nearest/least-lagged replica. Accept async lag and add read-your-writes/monotonic-reads where correctness matters.
- HA/DR: keep cross-region replicas so a region failure is survivable; plan explicit failover (election, fencing to avoid split-brain).
- If *writes* must be fast in every region → single-leader's cross-region write latency hurts; move to **multi-leader (leader per region)** or **leaderless quorums**, accepting write-conflict resolution (LWW, version vectors, CRDTs) / eventual consistency.
- Mention real systems: MySQL/Postgres read replicas, MongoDB replica sets, Cassandra/DynamoDB quorums, Kafka ISR. Note replication usually combines with sharding for write/storage scale.
</content>
