# Leader Election

**Track:** Building Blocks
**Category:** Consistency & Coordination

## What It Is

Leader election ek aisa coordination mechanism hai jisme ek group of nodes mutually agree karte hain ki kaunsa single node "leader" hoga jo special coordination kaam (writes order karna, work assign karna, decisions lena) handle karega, aur agar wo leader fail ho jaaye to baaki nodes automatically ek naya leader chun lete hain.

## Real-World Analogy

Socho ek cricket team hai jisme 5 players hain, aur kisi ek ko **captain** banana hai — toss kaun karega, field placement kaun decide karega, ye ek hi banda decide kare to confusion nahi hoti. Saare players ek transparent rule pe agree karte hain, jaise "jiski jersey number sabse choti hai wahi captain" (deterministic tie-break). Sab captain ko follow karte hain.

Ab captain ground se bahar chala jaata hai (injury / node crash). Players thodi der wait karte hain — "shayad pani peene gaya hai" — aur jab kaafi der tak captain instructions nahi deta (heartbeat timeout), tab baaki players ek nayi election karte hain aur agla sabse senior banda captain ban jaata hai. Khel rukta nahi, bas leadership handoff ho jaati hai.

Ek critical twist: agar do players ek saath "main captain hoon" bol dein (network partition mein dono ko laga purana captain mar gaya), to **do captains conflicting decisions** de denge — yahi "split-brain" disaster hai, aur leader election ka asli kaam isi ko rokna hai.

## How It Works

1. **Why a leader at all:** Distributed systems mein agar har node independently decide kare ki "main is write ko commit karta hoon", to conflicts aur inconsistency aati hai. Ek single leader ko coordinator bana do — saare writes uske through serialize ho jaate hain, ordering clean rehti hai. Followers leader se replicate karte hain.

2. **Term / epoch number:** Election ek monotonically increasing number ke saath hoti hai — Raft isko **term** kehta hai, Paxos **ballot/proposal number**, ZooKeeper **epoch**. Har nayi election ke saath ye number badhta hai (term 5 → term 6). Ye number stale leaders ko detect karne ka core trick hai: agar koi message purane term ka aaye, usko reject kar do.

3. **Voting & quorum:** Ek candidate khud ko nominate karta hai aur baaki nodes se vote maangta hai. Leader banne ke liye usko **majority quorum** chahiye — yaani 5 nodes ke cluster mein kam se kam 3 votes. Quorum is liye zaroori hai kyunki do alag majorities ek hi term mein possible nahi (3 + 3 > 5), to ek term mein sirf ek hi leader ban sakta hai. Har node ek term mein sirf ek baar vote deta hai.

4. **Heartbeats / leases:** Leader ban-ne ke baad wo periodically heartbeat bhejta hai followers ko — typically har **50–150 ms**. Followers ek randomized **election timeout** (jaise 150–300 ms) rakhte hain. Jab tak heartbeat aata rahe, koi nayi election nahi. Heartbeat interval << election timeout hona chahiye (jaise 50 ms heartbeat vs 300 ms timeout) taaki normal network jitter false election trigger na kare.

5. **Failure detection → re-election:** Agar ek follower apne election timeout (jaise 300 ms) tak koi heartbeat nahi sunta, to wo maan leta hai leader mar gaya, term ko increment karta hai (term 6 → 7), khud candidate banta hai, aur votes maangta hai. Randomized timeouts (har node ka alag, jaise 150–300 ms range se random) is liye use hote hain taaki saare followers ek saath candidate na ban jaayein — warna votes split ho jaate hain aur koi majority nahi banti (split vote).

6. **Fencing the old leader:** Maan lo purana leader actually mara nahi tha, bas slow / partitioned tha. Naya leader (higher term) ban gaya. Jab purana leader wapas aata hai aur koi command bhejta hai (lower term), to peers usko stale dekh ke reject kar dete hain, aur purana leader demote ho ke follower ban jaata hai. Storage-level pe iske liye **fencing token** (monotonic number) bhi use hota hai taaki stale leader ka write reject ho.

7. **Typical scale numbers:** Production coordination clusters (ZooKeeper / etcd) usually **3 ya 5 nodes** ke hote hain (odd number, taaki quorum clean rahe). Leader failure se naya leader elect hone ka typical convergence time **sub-second se kuch seconds** hota hai, jo heartbeat + election timeout config pe depend karta hai.

## Tradeoffs & Variants

- **Cluster size — odd kyun, aur quorum cost:** 3 nodes ek failure tolerate karte hain (quorum = 2), 5 nodes do failures (quorum = 3). 4 nodes ka quorum bhi 3 hai par wo bhi sirf 1 failure tolerate karta hai — to 4 nodes ka cost zyada par fault-tolerance 3 jaisa hi. Isiliye **odd number** prefer hota hai. Bada cluster → zyada fault tolerance par har write ko zyada nodes se ack chahiye → higher write latency.

- **Single leader vs leaderless:** Single-leader (Raft, ZooKeeper) clean ordering deta hai par leader ek **write bottleneck** aur SPoF-ish point ban jaata hai (mitigated by fast re-election). Leaderless / multi-leader systems (Dynamo-style quorum reads/writes) write availability badhate hain par conflict resolution (vector clocks, last-write-wins) ka bojh dalte hain. Interviewer aksar poochta hai: "leader bottleneck ho raha hai, kya karoge?" → answer: sharding (per-partition leader, jaise Kafka).

- **Dedicated coordination service vs roll-your-own:** Apna consensus likhna (Raft from scratch) bahut error-prone hai. Practice mein log ek external coordination service use karte hain — **ZooKeeper, etcd, ya Consul** — jo leader election ko ek primitive ki tarah expose karte hain (ephemeral nodes / leases / locks). Tradeoff: ek aur dependency aur operational overhead, par battle-tested correctness.

- **Lease-based election:** Leader ek time-bound **lease** (jaise 10 s) leta hai. Lease ke andar wo confidently act karta hai bina har operation pe quorum check kiye; lease expire hone se pehle renew karna padta hai. Faster reads deta hai (no per-read quorum) par clock skew pe depend karta hai — agar leader ka clock galat chala to lease boundary par do leaders overlap kar sakte hain.

## When To Use It

- **Replicated databases / state machines:** Ek primary jo writes accept kare aur replicas ko order mein replicate kare — Raft (etcd, CockroachDB, TiKV), or primary election in PostgreSQL/MySQL HA setups.
- **Distributed locks & coordination:** ZooKeeper / etcd / Consul ke upar built leader election — jaise ek hi instance ko cron / scheduled job chalane do (taaki duplicate run na ho), ya ek single "controller".
- **Kafka:** Har partition ka ek **leader broker** hota hai jo us partition ke produce/consume requests handle karta hai; controller broker partition leaders assign karta hai. (Older Kafka ZooKeeper use karta tha; newer KRaft mode self-managed Raft-based hai.)
- **Kubernetes:** Controller-manager aur scheduler **leader election** (lease objects via the API server) use karte hain taaki HA deployment mein sirf ek active controller ho.
- **General rule:** Jab bhi "exactly one node should be doing X at a time" ya "writes must have a single ordering authority" — wahan leader election fits.

## Common Interview Gotchas

- **Split-brain — sabse bada trap:** Agar quorum/term mechanism na ho aur network partition ho jaaye, to dono sides apna-apna leader chun lete hain → **two leaders, conflicting writes, data corruption**. Quorum (majority) iski guarantee deta hai: 5-node cluster mein agar 3-2 split ho, sirf 3-side majority bana sakti hai, 2-side leader nahi ban sakta. **Concrete:** isiliye even-split-prone configs (jaise 2-node ya cross-DC 2+2) khatarnak hain. Interviewer poochega "do leaders kaise rokoge?" → quorum + term + fencing token.

- **Heartbeat timeout ≠ death:** Ek missed heartbeat ka matlab leader mar gaya — ye galat assumption hai. GC pause, network blip, ya slow disk se heartbeat late aa sakta hai. Isiliye timeout buffer rakhte hain aur **fencing tokens** use karte hain — agar "dead" maana gaya leader wapas aaya, uske stale writes higher-term/token check se reject ho jaayein. Naive "no heartbeat = dead → kill" se zombie/double-leader problem aati hai.

- **Quorum read/write ko bhool jaana:** Sirf leader elect kar lena kaafi nahi. Agar naya leader purane committed data ko overwrite kar de to consistency tut-ti hai. Raft mein leader ko apna log up-to-date prove karna padta hai (election restriction) tabhi vote milta hai — to leader hamesha latest committed entries rakhta hai. "Koi bhi node leader ban sakta hai" — galat; **most up-to-date node hi** ban sakta hai.

- **Even-numbered cluster:** Log 2 ya 4 nodes daal dete hain "redundancy ke liye". 2-node cluster mein quorum 2 hai → ek node down hone pe poora cluster write-unavailable. Hamesha **odd (3/5/7)** rakho.

- **Election storm / split vote:** Agar saare followers ek saath candidate ban jaayein (non-randomized timeouts), votes split ho jaate hain, koi majority nahi banti, aur repeated re-elections se cluster stall ho jaata hai. Fix: **randomized election timeouts** taaki ek node pehle candidate bane.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/consistency-coordination/conceptual_quiz_leader_election.md`](../../../sysd-quizzes/consistency-coordination/conceptual_quiz_leader_election.md) — `sysd-buddy quiz scaffold leader-election` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update leader-election --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — cluster of nodes, term/heartbeat flow, leader failure aur re-election with quorum voting ka interactive diagram.
