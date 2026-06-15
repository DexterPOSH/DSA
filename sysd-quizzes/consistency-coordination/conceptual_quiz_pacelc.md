# PACELC — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update pacelc --quiz-score N/M` -->

## Q1 (warm-up)
What does the PACELC theorem stand for, and how would you state it in one sentence?

**Ideal answer:**
- **P**artition, **A**vailability, **C**onsistency, **E**lse, **L**atency, **C**onsistency.
- Formulation: "if (**P**)artition, then choose (**A**)vailability or (**C**)onsistency; **E**lse (no partition / normal operation), choose (**L**)atency or (**C**)onsistency."
- It is an extension of the CAP theorem (proposed by Daniel Abadi).
- Core idea: even when there is no partition, there is still a tradeoff — between latency and consistency.

## Q2 (core)
PACELC has two separate branches. Explain what each branch describes and which one is active most of the time in a real system.

**Ideal answer:**
- The **PAC** branch describes behaviour **during a network partition** (a failure): the system must sacrifice either availability (reject requests) or consistency (serve possibly-divergent data).
- The **ELC** branch describes behaviour during **normal operation** (no partition): the system trades latency against consistency — strong consistency requires confirming with more replicas (quorum/all), which adds network round-trips and latency; favouring latency means serving from a local/single replica with possibly stale data.
- The **Else (ELC) branch is active the vast majority of the time** (~99%+) because partitions are rare events; the PAC branch only matters during the relatively infrequent partition windows.
- Bonus: this is precisely why PACELC adds value over CAP — it covers the common steady-state case CAP ignores.

## Q3 (tradeoff)
In the ELC branch, why does choosing stronger consistency increase latency? Give a concrete sense of the cost.

**Ideal answer:**
- Strong/linearizable consistency requires a read or write to be confirmed by **multiple replicas** (a quorum, or all replicas) before responding, instead of answering from a single local replica.
- That confirmation needs **extra network round-trips** to the other replicas, which may be in other racks, datacenters, or regions.
- Concrete numbers: a local single-replica read can be ~1-5 ms; a same-datacenter quorum adds ~10-30 ms; a cross-region quorum can be ~50-150 ms (bounded ultimately by speed-of-light propagation between regions).
- Favouring latency (EL) means responding immediately from one replica and syncing others asynchronously, accepting eventual consistency / possible stale reads.
- Key point: the tradeoff is fundamental — you cannot get strong cross-region consistency without paying the round-trip latency.

## Q4 (gotcha)
A candidate says "PACELC is just CAP with an extra letter — same thing." Why is that wrong? Also, can a distributed system simply be 'CA' and opt out of partition tolerance?

**Ideal answer:**
- It is wrong because CAP only addresses the **partition (failure) scenario**, whereas PACELC's real contribution is the **ELC** part: it shows that even with **no failure**, during normal operation, every distributed datastore is trading latency vs consistency. That steady-state tradeoff is what CAP misses.
- On 'CA': in a distributed system, network **partitions are inevitable** and cannot be opted out of, so "CA / no partition tolerance" is not a real choice. PACELC treats **P as a condition** (when it happens) rather than a selectable property — when a partition occurs you choose PA or PC.
- Bonus accuracy: EL does not mean "no consistency" — it favours latency now and typically reaches eventual consistency (replicas converge later).

## Q5 (applied)
You're designing two systems: (a) a social-media activity feed, and (b) a financial ledger / inventory counter. For each, what PACELC classification would you target, name a real datastore, and justify it.

**Ideal answer:**
- **(a) Social feed → PA/EL.** Favour availability during partitions and low latency normally; brief staleness/eventual consistency is acceptable (a like or post showing a moment late is fine). Real datastores: **Cassandra, DynamoDB (default eventually-consistent reads), Riak.** Justification: high write throughput, low latency, always-available UX matter more than immediate global consistency.
- **(b) Financial ledger / inventory → PC/EC.** Favour consistency in both branches — correctness is paramount (no double-spend, no oversell), and the added latency is acceptable. Real datastores: **Google Spanner (TrueTime, external consistency), HBase/BigTable, etcd/ZooKeeper for coordination, or a strongly-consistent SQL/Spanner setup.** Justification: must never serve divergent balances; willing to pay quorum/commit latency for correctness.
- Bonus: mention **tunability** — e.g., Cassandra consistency levels (ONE vs QUORUM/ALL) or DynamoDB strongly-consistent read flag let you shift a single store along the EL↔EC axis per request, so classification often depends on configured consistency level.
