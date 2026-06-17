# Leader Election — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update leader-election --quiz-score N/M` -->

## Q1 (warm-up)
Leader election kya hai, aur ek distributed system mein hume ek single leader ki zaroorat hi kyun padti hai? One-line definition do, phir purpose explain karo.

**Ideal answer:**
- Definition: leader election ek coordination mechanism hai jisme nodes mutually agree karte hain ki ek single node "leader" hoga, aur agar wo fail ho to automatically naya leader chun lete hain.
- Purpose: ek single coordinator writes/decisions ko serialize karta hai → clean ordering aur consistency; har node independently decide kare to conflicts aate hain.
- Bonus: leader fail hone pe automatic failover hota hai, system available rehta hai.

## Q2 (core)
Raft jaise systems mein, ek follower kaise decide karta hai ki leader mar gaya hai aur election trigger karta hai? Term/epoch, heartbeat, aur election timeout ka role explain karo.

**Ideal answer:**
- Leader periodically heartbeats bhejta hai (e.g. har 50–150 ms).
- Har follower ek randomized election timeout rakhta hai (e.g. 150–300 ms); heartbeat aate rehne se timer reset hota rehta hai.
- Agar timeout tak koi heartbeat nahi aaya → follower maan leta hai leader dead, term ko increment karta hai, candidate banta hai, aur votes maangta hai.
- Leader banne ke liye majority quorum (e.g. 5 mein se 3) votes chahiye; har node ek term mein ek hi vote deta hai.
- Term = monotonically increasing number jo stale leaders detect karne mein use hota hai.
- Heartbeat interval << election timeout hona chahiye taaki false elections na hon.

## Q3 (tradeoff)
Coordination cluster ke liye log usually 3 ya 5 nodes (odd) kyun rakhte hain, 2 ya 4 nhi kyun? Cluster size ka fault-tolerance aur latency pe kya tradeoff hai?

**Ideal answer:**
- Quorum = majority. 3 nodes → quorum 2 → 1 failure tolerate. 5 nodes → quorum 3 → 2 failures tolerate.
- 4 nodes ka quorum bhi 3 hai par sirf 1 failure tolerate karta hai (4-1=3 still ≥ quorum, but 4-2=2 < 3) — yaani 4 nodes ka extra cost bina extra fault-tolerance ke. Isiliye odd numbers prefer hote hain.
- 2-node cluster: quorum 2, ek node down = poora cluster write-unavailable → bad.
- Tradeoff: bada cluster = zyada fault tolerance par har write ko zyada acks chahiye → higher write latency.

## Q4 (gotcha)
"Split-brain" kya hai aur leader election protocols isko kaise rokte hain? Ek concrete partition scenario do.

**Ideal answer:**
- Split-brain = ek network partition ke dono sides apna-apna leader chun lete hain → two leaders, conflicting writes, data corruption.
- Prevention: majority quorum. Concrete: 5-node cluster 3-2 split ho to sirf 3-side majority bana sakti hai; 2-side leader nahi ban sakta (2 < 3). Ek term mein do majorities impossible.
- Additional safeguards: monotonic term/epoch number (stale leader ke lower-term messages reject), aur fencing tokens (stale leader ke writes storage level pe reject).
- Misconception to avoid: ek missed heartbeat ≠ leader dead (GC pause / network blip); isiliye fencing zaroori hai jab "dead" leader wapas aaye.

## Q5 (applied)
Tumhe ek HA system design karna hai jisme ek scheduled job (jaise daily report generator) ka exactly ek hi instance run kare, chahe service ke 10 replicas chal rahe hon. Leader election kaise apply karoge? Kaunse real systems/tools use karoge?

**Ideal answer:**
- Pattern recognition: "exactly one node should do X at a time" → leader election fits.
- Approach: ek external coordination service (ZooKeeper ephemeral node / etcd lease / Consul session / Kubernetes lease object) se leader elect karo; sirf leader hi job chalaye.
- Lease/heartbeat: leader periodically lease renew kare; agar wo crash kar jaaye to lease expire hone pe doosra replica leader ban ke job le le.
- Fencing/idempotency: stale leader ke late writes ko fencing token se reject karo, aur job ko idempotent banao taaki failover window mein double-run bhi safe ho.
- Real examples: Kubernetes controller-manager/scheduler leader election via leases; Kafka partition leaders; etcd/ZooKeeper-based locks.
- Avoid: apna consensus from scratch likhna (error-prone) — battle-tested service use karo.
