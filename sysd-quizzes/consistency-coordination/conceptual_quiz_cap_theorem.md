# CAP Theorem — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update cap-theorem --quiz-score N/M` -->

## Q1 (warm-up)
In one or two sentences, what does the CAP theorem state? Define each of the three letters.

**Ideal answer:**
- CAP: ek distributed data system network partition ke dauraan Consistency aur Availability dono guarantee nahi kar sakta — sirf ek.
- **C (Consistency):** har read ko most recent successful write dikhe (linearizability / single-copy semantics).
- **A (Availability):** har request to a non-failing node ko ek non-error response mile (chahe stale ho).
- **P (Partition tolerance):** nodes ke beech messages drop/delay hone par bhi system operate karta rahe.
- Bonus: yeh recognize karna ki tension partition ke dauraan trigger hota hai.

## Q2 (core)
Most real distributed systems are described as either CP or AP — almost never "CA". Mechanically, why is that, and what actually happens inside a CP vs an AP system the moment a network partition splits the cluster?

**Ideal answer:**
- P is not optional — real networks drop/delay packets, so partitions WILL happen; tum P ko opt out nahi kar sakte.
- Isliye actual choice "C ya A **during a partition**" hai → systems CP ya AP ban jaate hain; "CA" sirf single-node / non-distributed mein theoretical.
- **CP behaviour:** partition ke dauraan minority/non-quorum side request ko reject/block karta hai (error ya timeout) taaki stale/wrong data na de — consistency safe, availability gayi us side.
- **AP behaviour:** har side request accept karke turant respond karta hai (local copy se), divergence allow karta hai; partition heal hone par reconcile karta hai (last-write-wins, version vectors, CRDTs, read-repair).
- Bonus: quorum example — `N=3, W=2, R=2` (`W+R>N`) CP-style; jis side `W` reach nahi hoti wo write reject karti hai.

## Q3 (tradeoff)
CAP only talks about behaviour during a partition. What does PACELC add, and why does it matter for system design even when the network is perfectly healthy?

**Ideal answer:**
- PACELC: **if Partition → choose A vs C; Else (normal operation) → choose Latency vs Consistency.**
- Matters because even without partitions, strong consistency requires cross-node coordination (quorum round trips) → higher latency / lower throughput.
- So tradeoff partition ke bina khatam nahi hota — wo Latency-vs-Consistency ban jaata hai.
- Examples: DynamoDB = PA/EL (available + low latency); Spanner / strongly-consistent stores = PC/EC.
- Bonus: concrete numbers — cross-region quorum read `p99` `~50-100ms` vs eventual `~5ms`.

## Q4 (gotcha)
A candidate says: "I'll design a CA system — consistent and available — since my datacenter network is reliable, I don't need partition tolerance." Also, the CAP 'C' is the same as ACID's 'C', right? Critique both claims.

**Ideal answer:**
- "CA in a distributed system" is a false framing — network partitions are inevitable, you cannot opt out of P; tum sirf partition ke time C ya A choose kar sakte ho. Reliable network bhi guarantee nahi hai.
- When there's NO partition, you genuinely get both C and A — so "CA" describes normal operation, not a design choice you make.
- CAP's C (linearizability / single-copy / replica consistency) is **not** ACID's C (transaction invariants/constraints like FK, balance ≥ 0). Conflate karna galat hai.
- Bonus: "AP means no consistency" bhi galat — AP eventually consistent ho sakta hai post-heal.

## Q5 (applied)
You're designing two services: (a) a payment/inventory system where stock counts must never be wrong, and (b) a social-feed "like counter" that must never go down even under huge write volume. For each, would you pick CP or AP, why, and name a real system you'd reach for?

**Ideal answer:**
- **(a) Payments/inventory → CP.** Stale/wrong stock ya double-spend unacceptable; correctness > uptime. Reject/block during partition is acceptable. Real systems: Spanner, etcd/ZooKeeper (locks/coordination), HBase, MongoDB (primary-based, CP-leaning), or an RDBMS with quorum.
- **(b) Like counter / feed → AP.** Downtime aur lost writes unacceptable; slightly stale/eventually-consistent count tolerable. Accept writes everywhere, reconcile later (CRDT counters ideal). Real systems: Cassandra, DynamoDB (eventual), Riak.
- Pattern recognition: "money/stock/lock/never wrong" → CP; "always up / massive writes / staleness OK" → AP.
- Bonus: mention tunable consistency (Cassandra `QUORUM` vs `ONE`, DynamoDB strongly-consistent read flag) and the normal-case latency cost (PACELC).
