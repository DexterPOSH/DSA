# CAP Theorem

**Track:** Building Blocks
**Category:** Consistency & Coordination

## What It Is

CAP theorem kehta hai ki ek distributed data system network partition ke dauraan Consistency (har read latest write dekhe) aur Availability (har request bina error ke respond kare) — in dono mein se sirf ek hi de sakta hai, dono ek saath nahi.

## Real-World Analogy

Socho do shops hain — ek Mumbai mein, ek Delhi mein — aur dono ek hi shared price list bechte hain. Normally jab bhi Mumbai wali shop price change karti hai, wo turant phone karke Delhi wali shop ko bata deti hai, taaki dono ki list same rahe.

Ab ek din beech ka phone line kat jaata hai (yeh hai **network partition**). Ab Delhi wali shop ke saamne ek customer khada hai jo price poochh raha hai. Do hi options hain:

- **Option A (Consistency choose karo):** Delhi shop kehti hai "bhai abhi main confirm nahi kar sakti ki Mumbai ne price badla ya nahi, isliye main aapko serve hi nahi karungi" — yaani wo customer ko reject kar deti hai taaki kabhi galat (stale) price na de. Yeh **CP** behaviour hai: consistency bachayi, availability sacrifice ki.
- **Option B (Availability choose karo):** Delhi shop kehti hai "main aapko apni purani list se price de deti hoon, chahe wo thodi outdated ho" — customer ko serve to kiya, par price stale ho sakta hai. Yeh **AP** behaviour hai: availability bachayi, consistency sacrifice ki.

Phone line theek hone ke baad (partition heal) dono shops apni lists reconcile kar leti hain. Point yeh hai: **jab tak line zinda hai (no partition), tum dono — consistency aur availability — comfortably de sakte ho.** CAP ka tension sirf partition ke dauraan trigger hota hai.

## How It Works

1. **Teen properties define karo:**
   - **Consistency (C):** Yahan "C" linearizability ko refer karta hai — har read ko sabse recent successful write dikhe, jaise pure system mein ek hi copy ho. (Note: yeh ACID ka "C" nahi hai, woh alag concept hai.)
   - **Availability (A):** Non-failing node pe aane wali har request ko ek non-error response milna chahiye — bhale hi response thoda stale ho.
   - **Partition tolerance (P):** System tab bhi kaam karta rahe jab nodes ke beech messages drop ya delay ho jaayein.

2. **P optional nahi hai — woh given hai:** Real distributed systems mein network kabhi-na-kabhi packets drop karega ya nodes ko split karega. Isliye partition tolerance ek choice nahi, ek reality hai. Matlab practical choice "CA vs CP vs AP" nahi hai — practical choice **"partition aane par C chodoge ya A?"** hai. Isiliye real systems effectively **CP ya AP** hote hain; pure "CA" sirf single-node ya non-distributed setup mein theoretical hai.

3. **Partition ke dauraan decision:** Maan lo ek 3-node cluster hai aur network do groups mein bant gaya: ek side pe 2 nodes (majority), doosri side pe 1 node (minority). Ab minority side pe ek write aata hai:
   - **CP system:** Minority side write ya read ko reject/block kar deta hai (kyunki wo quorum confirm nahi kar sakta). Client ko error ya timeout milta hai — typically request `500ms` quorum-wait ke baad fail. Consistency safe, par us side availability gayi.
   - **AP system:** Minority node bhi write accept kar leta hai apne local copy mein, aur turant `~5ms` mein respond karta hai. Baad mein jab partition heal hota hai, conflicting writes ko reconcile karna padta hai (e.g. last-write-wins via timestamps, ya version vectors / CRDTs).

4. **Quorum math (CP ka common mechanism):** N replicas mein agar write quorum `W` aur read quorum `R` aise chuno ki `W + R > N`, to har read kam-se-kam ek aisi replica chhuti hai jisne latest write dekha — yeh strong consistency deta hai. Example: `N=3, W=2, R=2` → `2+2 > 3`. Partition mein agar koi side `W=2` nodes reach nahi kar sakta, wo write reject karega (CP). Agar tum `W=1, R=1` rakho (`1+1 = 2 ≤ 3`), to writes hamesha succeed honge even on minority side → high availability, but stale reads possible (AP-leaning).

5. **Heal ke baad reconciliation:** AP systems ko convergence chahiye — anti-entropy (Merkle tree comparison), read-repair, ya hinted handoff jaise mechanisms se divergent replicas eventually same state pe aate hain. Yahi "eventual consistency" hai.

## Tradeoffs & Variants

- **C vs A under partition:** Yeh core decision hai. CP choose karo agar stale ya wrong data unacceptable hai (paisa, inventory, locks). AP choose karo agar downtime unacceptable hai aur thodi staleness chalegi (likes, feeds, shopping cart).

- **PACELC — CAP ka zaroori extension:** CAP sirf partition (P) case batata hai. PACELC kehta hai: **if Partition → choose between A and C; Else (normal operation) → choose between Latency and Consistency.** Yeh important hai kyunki normally bhi strong consistency ke liye nodes ko coordinate karna padta hai jisse latency badhti hai. Jaise: DynamoDB = **PA/EL** (partition mein available, normally low-latency). Fully strongly-consistent systems = **PC/EC**. Interviewer aksar "but what about latency when there's NO partition?" poochta hai — yahi PACELC cover karta hai.

- **Consistency ek spectrum hai, binary nahi:** "C ya not-C" se zyada nuance hai. Strong/linearizable → causal → read-your-writes → monotonic reads → eventual. Bahut systems tunable hote hain (Cassandra mein per-query `ONE` / `QUORUM` / `ALL` consistency level; DynamoDB mein eventual vs strongly-consistent read flag).

- **Cost angle:** Strong consistency = zyada cross-node round trips = higher latency (`p99` jump from `~5ms` to `~50-100ms` for cross-region quorum) aur lower throughput. Availability/eventual = low latency par application ko conflict-handling logic likhna padta hai.

## When To Use It

- **CP systems (consistency wins):** Banking/payments, inventory with strict stock counts, distributed locks, leader election, configuration/metadata stores. Real examples: **etcd, ZooKeeper, Consul** (sab Raft/Paxos-based, quorum CP), **HBase**, **Google Spanner** (CP, TrueTime se globally consistent), MongoDB default (primary-based, CP-leaning).

- **AP systems (availability wins):** Shopping carts, social feeds, user sessions, like/view counters, DNS, CDN edge data. Real examples: **Amazon DynamoDB** (default eventual), **Apache Cassandra**, **Riak**, **CouchDB**. Amazon ka classic justification: cart kabhi unavailable nahi hona chahiye, beshak kabhi-kabhi reconcile karna pade.

- **Interview pattern recognition:** Jab requirement mein "must never show wrong/stale value" ya "money/stock/lock" aaye → CP. Jab "must always be up / can't tolerate downtime / huge write volume" aaye aur staleness tolerable ho → AP. Aur jab interviewer normal-case latency poochhe → PACELC frame use karo.

## Common Interview Gotchas

- **"CAP mein se koi 2 pick karo" — galat framing:** Sabse common mistake. Tum partition ko opt-out nahi kar sakte (network unreliable hai), isliye real choice "C ya A" hai **only during a partition**. "CA system" jaisa kuch practically distributed world mein exist nahi karta. Mat kaho "main CA choose karunga."

- **Partition ke bina koi tradeoff nahi:** Jab network healthy hai, ek system strong consistency AUR high availability dono de sakta hai. CAP tradeoff sirf partition window mein active hota hai. Isiliye PACELC ka "Else Latency-vs-Consistency" wala part zaroori hai — normal-time tradeoff latency ka hai, availability ka nahi.

- **CAP ka "C" ≠ ACID ka "C":** CAP ka C = linearizability/single-copy semantics (replicas ke beech consistency). ACID ka C = transaction database constraints/invariants (jaise foreign keys, balance ≥ 0) ko preserve karna. Inko mat mix karo.

- **"AP means no consistency" — galat:** AP ka matlab "kabhi consistent nahi" nahi hai; matlab strong consistency partition mein guarantee nahi. Heal ke baad system eventually consistent ho jaata hai (read-repair, anti-entropy, CRDTs).

- **Availability ki strict definition:** CAP ki availability = har request to a **non-failing** node ka response. Yeh "99.99% uptime" wali operational availability se alag, ek formal theoretical definition hai. Inko interview mein conflate mat karo.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/consistency-coordination/conceptual_quiz_cap_theorem.md`](../../../sysd-quizzes/consistency-coordination/conceptual_quiz_cap_theorem.md) — `sysd-buddy quiz scaffold cap-theorem` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update cap-theorem --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — partition ke dauraan CP vs AP decision, quorum split, aur reconciliation ka interactive diagram.
