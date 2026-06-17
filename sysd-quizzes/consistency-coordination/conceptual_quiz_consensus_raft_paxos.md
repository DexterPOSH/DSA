# Consensus (Raft/Paxos Overview) — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update consensus-raft-paxos --quiz-score N/M` -->

## Q1 (warm-up)
Consensus protocol kya solve karta hai? One sentence mein batao, aur ye kyun non-trivial hai jab nodes crash ho sakti hain ya network unreliable ho.

**Ideal answer:**
- Consensus = multiple unreliable nodes ko ek single agreed value / ordered sequence of operations pe agree karwaata hai.
- Goal: replicated state machine — same commands, same order, har replica pe → identical consistent state.
- Non-trivial isliye kyunki nodes crash ho sakti hain aur messages drop/delay/reorder ho sakte hain, fir bhi safety (no two conflicting decisions) hold karni chahiye.
- Bonus: agreement under faults achieve karna hai bina single point of failure ke.

## Q2 (core)
Raft mein ek client write committed kaise hoti hai — leader election se le ke commit tak ke steps batao. Quorum ka role kya hai aur `2f+1` ka kya matlab hai?

**Ideal answer:**
- Ek leader hota hai (randomized election timeout ~150-300 ms ke baad chuna jaata, majority votes se, term number badha ke).
- Client request leader ke log mein entry (index + term) ban ke append hoti hai.
- Leader `AppendEntries` RPC se entry followers ko replicate karta hai.
- Jab entry **majority** (quorum = floor(N/2)+1) nodes pe durably likh jaati → committed.
- Committed entry state machine pe log order mein apply hoti, fir client ko ack.
- `2f+1` nodes se `f` failures tolerate (3 nodes → 1 failure, quorum 2; 5 → 2 failures, quorum 3).
- Term = monotonic logical clock; higher term dikhe to node follower ban jaata.

## Q3 (tradeoff)
3-node vs 5-node Raft cluster ka tradeoff samjhao. Aur even number of nodes (jaise 4) kyun avoid karte hain?

**Ideal answer:**
- 3 nodes: 1 failure tolerate, quorum sirf 2 acks → lower write latency, lower cost.
- 5 nodes: 2 failures tolerate, quorum 3 acks → zyada durability/availability par thodi zyada latency + cost.
- 7+ rarely: quorum bada → write latency badhti, fault-tolerance gain diminishing.
- Even number useless extra: 4 nodes bhi quorum 3 → sirf 1 failure tolerate (3 jaisa hi), bas ek machine ka extra cost.
- Hamesha odd (3/5/7) choose karo.
- Bonus: cross-region replication round-trip latency (50-100+ ms) write cost badhata hai → sharding to scale.

## Q4 (gotcha)
Kaafi log consensus ko 2-phase commit (2PC) samajh lete hain. Dono mein kya farak hai? Aur "quorum overlap" safety kaise guarantee karta hai?

**Ideal answer:**
- 2PC blocking hai: coordinator crash → participants stuck (uncertain), aage nahi badh sakte.
- Consensus (Raft/Paxos) non-blocking: leader crash → naya leader chun ke continue.
- 2PC = atomic commit across multiple resources; consensus = replicated agreement + availability under failures.
- Quorum overlap: koi bhi do majorities (floor(N/2)+1) at least ek node share karti hain.
- Is overlap ki wajah se do conflicting values simultaneously commit nahi ho sakte → safety.
- Bonus: CAP mein consensus = CP; minority side (no quorum) writes reject karega → unavailable, but never inconsistent.

## Q5 (applied)
Ek system design interview mein tum kab consensus (etcd/ZooKeeper/Raft-based store) reach karoge, aur kab nahi? 2-3 concrete real systems ke saath justify karo.

**Ideal answer:**
- USE jab strong consistency / single source of truth / linearizability non-negotiable ho:
  - Coordination & metadata: etcd, Consul (Raft), ZooKeeper (ZAB) — leader election, config, service discovery, distributed locks. Kubernetes control-plane state = etcd.
  - Strongly-consistent DBs: Google Spanner (Paxos per shard), CockroachDB / TiKV-TiDB (Raft per range).
  - Distributed lock / exactly-one leader as a primitive.
- AVOID jab high-throughput, latency-sensitive, ya geo-distributed writes ho aur eventual consistency acceptable ho (shopping cart, feed counts, likes) → Dynamo-style quorum / CRDTs saste & faster.
- Justification: consensus har write pe coordination cost (round-trip to majority) leta hai; sirf wahan jahan correctness chahiye.
- Bonus: scale ke liye keyspace shard karo, har shard ka apna Raft group (Spanner/CockroachDB pattern).
