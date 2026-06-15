# Consensus (Raft/Paxos Overview)

**Track:** Building Blocks
**Category:** Consistency & Coordination

## What It Is

Consensus ek protocol hai jisse multiple unreliable nodes ek replicated state machine ke liye ek single agreed-upon value (ya operations ki ordered sequence) pe agree kar paate hain, even jab kuch nodes crash ho jaayein ya network messages drop/delay ho jaayein.

## Real-World Analogy

Socho ek WhatsApp group hai 5 dosto ka, aur tum sab milke decide kar rahe ho ki Sunday ka plan kya hoga — movie ya trekking. Problem ye hai ki network flaky hai: kisi ka message late aata hai, kabhi koi offline ho jaata hai. Agar har koi apni alag final decision maan le to chaos ho jaayega — kuch log cinema pahunchenge, kuch pahaad pe.

Toh tum log ek rule banate ho: group ka ek "leader" hoga (jiski battery sabse zyada hai, mazaak), aur har plan-change usi leader ke through hi propose hoga. Leader bolta hai "trekking final?" aur jab tak group ke **majority** (5 mein se kam-se-kam 3 log) "haan" nahi bol dete, plan confirmed nahi hota. Majority isliye chahiye taaki do alag-alag majorities kabhi do alag plans confirm na kar payein — kyunki 5 mein se koi bhi 3 logon ka group doosre kisi 3 logon ke group se kam-se-kam 1 banda toh share karega hi (overlap guarantee).

Agar leader ka phone band ho gaya (crash), to baaki log timeout ke baad ek naya leader chun lete hain aur plan chalta rehta hai. Yahi consensus hai: leader election + majority agreement + crash ke baad recovery, taaki sab ek hi consistent story pe rahein.

## How It Works

Consensus ka aam use replicated state machine banana hai: same commands ko same order mein har replica pe apply karo, to sab replicas identical state pe pahunchte hain. Raft (jo Paxos se zyada understandable hone ke liye design hua) is flow ko 3 sub-problems mein todta hai:

1. **Cluster size aur quorum:** Typically odd number of nodes, jaise **3 ya 5**. Quorum = majority = `floor(N/2) + 1`. 3 nodes → quorum 2 (1 failure tolerate). 5 nodes → quorum 3 (2 failures tolerate). General rule: **`2f + 1` nodes se `f` failures** tolerate hoti hain. Even number (jaise 4) ka faida nahi — 4 nodes bhi sirf 1 failure hi tolerate karte hain, bas cost zyada.

2. **Leader election (Raft):** Har node ke paas ek randomized **election timeout** hota hai, usually **150-300 ms** range mein. Agar follower ko leader se heartbeat is window ke andar nahi milta, wo apne aap ko candidate declare karta hai, **term number** badha deta hai, aur baaki nodes se vote maangta hai. Jise majority votes mil jaayein wo leader ban jaata hai. Randomized timeout split-vote ko avoid karta hai (sab ek saath candidate na banein).

3. **Term:** Term ek monotonically increasing integer hai jo "logical clock" ki tarah kaam karta hai. Har term mein at most ek leader. Agar kisi node ko higher term dikh jaaye, wo turant follower ban jaata hai — ye stale leaders ko khatam karta hai.

4. **Log replication:** Client ki har request leader ke log mein ek **entry** ban ke append hoti hai (index + term ke saath). Leader ye entry `AppendEntries` RPC ke through followers ko bhejta hai. Jab entry **majority** nodes pe durably likh jaati hai, leader use **committed** maan leta hai, apni state machine pe apply karta hai, aur client ko ack deta hai.

5. **Commit aur apply:** Committed entries hi state machine pe apply hoti hain, strictly log order mein. Isse har replica same sequence execute karta hai → deterministic identical state. Heartbeats (empty AppendEntries) har **~50 ms** pe jaate hain leader-liveness signal ke liye.

6. **Latency intuition:** Ek commit ke liye kam se kam **1 round-trip leader→majority→leader** chahiye. Same-region cluster mein ye **~1-5 ms** hota hai; cross-region (multi-datacenter) mein replication round-trip **50-100+ ms** tak ja sakta hai — isliye geo-distributed consensus write latency ko hurt karta hai. Throughput typically thousands se low-tens-of-thousands writes/sec per Raft group, isliye bade systems data ko **shard** karke har shard ke liye apna Raft group rakhte hain.

7. **Paxos contrast:** Classic (single-decree) Paxos ek hi value pe agree karne ka protocol hai with two phases — **Prepare/Promise** (phase 1) aur **Accept/Accepted** (phase 2), proposers proposal numbers use karte hain. Real systems **Multi-Paxos** chalate hain: ek stable leader phase 1 ko amortize kar deta hai aur steady-state mein sirf phase 2 (1 round-trip) chalta hai — concept mein ye Raft ke log replication jaisa hi ho jaata hai.

## Tradeoffs & Variants

- **Raft vs Paxos:** Dono safety-equivalent hain (same fault tolerance, same `2f+1` math). Farak understandability aur structure ka hai. Raft strong-leader + explicit terms ke saath samajhne/implement karne mein aasaan; classic Paxos ka spec minimal hai par real Multi-Paxos systems building mein notoriously trappy. Interview mein default Raft mention karna safe hai.

- **3 vs 5 nodes:** 3 → ek failure tolerate, faster quorum (sirf 2 acks chahiye), lower cost. 5 → do failures tolerate, par har write ko 3 acks chahiye → thoda zyada latency aur cost. 7+ rarely use hota hai kyunki quorum bada hone se write latency badhti hai aur fault-tolerance benefit diminishing hota hai.

- **Latency vs durability:** Leader fsync-to-disk before ack karega to durability strong, par per-write latency badhti hai. Kuch systems group-commit / batching karte hain throughput badhane ke liye, ek hi round-trip mein kai entries.

- **Read consistency:** Default mein linearizable read ke liye leader ko bhi quorum confirm karna padta hai ki wo abhi bhi leader hai (warna stale read mil sakti hai ek partitioned old leader se). Optimizations: **leader leases** ya **ReadIndex** — taaki har read pe full round-trip na karna pade. Ye ek classic tradeoff: read latency vs strict linearizability.

- **Membership change:** Cluster mein node add/remove karna risky hai (do overlapping configs do leaders bana sakte hain). Raft **joint consensus** ya single-server-at-a-time change use karta hai is safety ko guarantee karne ke liye.

- **Sharding:** Ek single Raft group throughput-bound hai, isliye scale ke liye keyspace ko shards mein todo aur har shard ka apna independent Raft group (Spanner, CockroachDB, TiKV yahi karte hain).

## When To Use It

- **Strongly-consistent metadata / coordination store:** ZooKeeper (ZAB, Paxos-family), etcd aur Consul (Raft) — leader election, config, service discovery, distributed locks ke liye. Kubernetes ka control-plane state etcd (Raft) pe baithta hai.
- **Replicated databases jinhe linearizability chahiye:** Google Spanner (Paxos per shard), CockroachDB aur TiKV/TiDB (Raft per range/region) — har shard apne replicas pe consensus se ordered writes commit karta hai.
- **Distributed locks aur leader election as a primitive:** Jab tumhe exactly-one guarantee chahiye (ek hi node ek kaam kare), consensus-backed store use karo.
- **Kab AVOID karo:** High-throughput, latency-sensitive, ya geo-distributed writes jahan eventual consistency acceptable hai (jaise shopping cart, social feed counts). Wahan Dynamo-style quorum / CRDTs / eventual consistency saste aur faster hain. Consensus har write pe coordination ka cost leta hai — use it only jahan correctness (single source of truth) non-negotiable ho.

## Common Interview Gotchas

- **"Consensus = 2-phase commit (2PC)" — galat.** 2PC blocking hai: agar coordinator crash ho jaaye, participants stuck (uncertain) reh sakte hain. Raft/Paxos non-blocking hain — leader crash hone pe naya leader chun ke aage badh jaate hain. 2PC atomic commit across resources ke liye hai; consensus replicated agreement + availability under failures ke liye.

- **"Quorum lock guarantee" ko galat samajhna.** Safety isliye hoti hai kyunki **koi bhi do majorities at least ek node share karti hain** (`floor(N/2)+1` ka overlap). Isi overlap ki wajah se do conflicting values kabhi simultaneously commit nahi ho paate. Ye batao to interviewer impress hota hai.

- **Even number of nodes useless extra.** 4 nodes bhi sirf 1 failure tolerate karte hain (quorum 3), 3 ki tarah — bas ek extra machine ka cost. Hamesha odd number (3/5/7) choose karo.

- **"Consensus partition mein bhi available rehta hai" — nahi.** CAP ke terms mein consensus systems **CP** hain: agar leader minority side pe phans gaya (no quorum), wo writes accept nahi karega → us side pe unavailability. Availability ko consistency ke liye sacrifice karta hai.

- **Committed ≠ applied/visible turant.** Entry majority pe durable hone pe committed hoti hai, par client ko visibility tab milti hai jab state machine pe apply ho. Aur ek naya leader ko apne se pehle ki entries ko careful commit-rules ke saath hi commit-count karna hota hai (Raft sirf current-term entry ko directly commit karta hai, purani entries ko us ke saath piggyback karta hai) — ye ek subtle safety detail hai.

- **Split-brain / two leaders.** Term/proposal-number mechanism isiliye exist karta hai: agar do nodes khud ko leader samjhein, higher term wala jeetega aur purana automatically step down karega. Logs higher-term leader ke according reconcile hote hain.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/consistency-coordination/conceptual_quiz_consensus_raft_paxos.md`](../../../sysd-quizzes/consistency-coordination/conceptual_quiz_consensus_raft_paxos.md) — `sysd-buddy quiz scaffold consensus-raft-paxos` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update consensus-raft-paxos --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — leader election, term changes, aur log replication to a majority quorum ka interactive diagram.
