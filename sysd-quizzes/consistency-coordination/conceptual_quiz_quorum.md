# Quorum (R+W>N) — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update quorum --quiz-score N/M` -->

## Q1 (warm-up)
In a quorum-based replication scheme, what do `N`, `W`, and `R` stand for, and what does the condition `R + W > N` buy you?

**Ideal answer:**
- `N` = number of replicas that store each piece of data.
- `W` = write quorum: a write is acknowledged as successful only after at least `W` replicas confirm it.
- `R` = read quorum: a read queries at least `R` replicas and returns the newest version among them.
- `R + W > N` guarantees the read set and the (latest) write set overlap in at least one replica, so any read sees the most recent successful write (latest-value visibility / strong-ish consistency).

## Q2 (core)
With `N = 3, W = 2, R = 2`, walk through exactly why a read is guaranteed to return the latest write. Mention the overlap math.

**Ideal answer:**
- The latest write landed on at least `W = 2` replicas.
- A read contacts at least `R = 2` replicas.
- Two subsets of size 2 each, drawn from only 3 replicas, must share at least `R + W - N = 2 + 2 - 3 = 1` replica (pigeonhole principle).
- That overlapping replica holds the latest version, so when the reader compares versions (timestamps / vector clocks) across the `R` responses, the newest one wins and is returned.
- Bonus: the write didn't need all 3 acks (only 2), so a slow/down 3rd replica doesn't block; the read still finds the latest value via the overlap.

## Q3 (tradeoff)
You have `N = 3`. Compare `W = 3, R = 1` vs `W = 1, R = 3` vs `W = 2, R = 2`. When would you pick each, and what's the cost?

**Ideal answer:**
- `W = 3, R = 1`: reads are fast (one replica) — good for read-heavy workloads; but writes must hit all 3 replicas, so a single down/slow replica blocks or slows every write (low write availability, high write tail latency).
- `W = 1, R = 3`: writes are fast and highly available (one ack) — good for write-heavy / ingest workloads; but reads must contact all 3, raising read latency and read fragility.
- `W = 2, R = 2`: majority on both sides (`N/2 + 1`); balanced consistency, tolerates one node down on either path; the common default.
- Key insight: all three satisfy `R + W > N` so all give the overlap guarantee; the choice just shifts the latency/availability cost between the read and write paths.

## Q4 (gotcha)
A candidate claims "`R + W > N` gives you full linearizable / perfectly consistent reads." Where is this wrong?

**Ideal answer:**
- The overlap only guarantees a read set intersects the latest write's replica set; it does NOT handle several real anomalies.
- Concurrent writes: quorum says how many replicas participate, not which value wins — you still need conflict resolution (last-write-wins via timestamps, or vector clocks + app-side merge). Quorum alone can lose or diverge data.
- Sloppy quorum (Dynamo-style): when home replicas are down, writes go to other healthy nodes with hints, which can temporarily break the strict `R + W > N` overlap and open a stale-read window.
- Reads during an in-progress/partial write can see old or mixed state.
- Conclusion: quorum is a practical approximation of strong consistency, not true linearizability; for that you need real consensus (Paxos/Raft). The Dynamo paper itself acknowledges this.

## Q5 (applied)
You're designing a leaderless, geo-distributed key-value store across 3 datacenters and need low-latency reads/writes without sacrificing too much consistency. How do you apply quorum here, and which real systems guide your choice?

**Ideal answer:**
- Use a tunable-quorum datastore (Cassandra, Riak, Dynamo, Voldemort) where `N`, `R`, `W` are configurable per request.
- To avoid cross-DC round trips on every operation, use a per-datacenter quorum like Cassandra's `LOCAL_QUORUM` — achieve quorum within the local DC for latency, replicate cross-DC asynchronously.
- Pick `N` per DC (e.g., 3) and `W = R = 2` locally for the overlap guarantee while tolerating one down node.
- Mention mechanisms that keep replicas converged: read repair (fix stale replicas on read), hinted handoff (hold writes for down nodes), and anti-entropy (Merkle-tree background sync).
- Acknowledge the trade-off: `LOCAL_QUORUM` gives strong consistency within a DC but only eventual consistency across DCs; if global strong consistency is required, you'd accept higher latency (`EACH_QUORUM` / cross-DC quorum) or move to a consensus-based system.
