# Quorum (R+W>N)

**Track:** Building Blocks
**Category:** Consistency & Coordination

## What It Is

Quorum ek aisi technique hai jisme data ke `N` replicas hone par har write ko kam se kam `W` replicas pe aur har read ko kam se kam `R` replicas se confirm karaaya jaata hai, aur jab `R + W > N` rakha jaaye to read aur write sets mein kam se kam ek replica zaroor overlap karta hai — isi overlap se latest write read tak guaranteed pohochti hai.

## Real-World Analogy

Socho ek classroom mein `N = 5` dost hain jo group project ka latest version apne-apne laptop pe rakhte hain. Koi update karta hai to use "save" tab maano hua jab kam se kam `W = 3` doston ne usko apne laptop pe copy kar liya (yaani teen ne "haan mere paas aa gaya" bol diya). Ab jab tumhe latest version chahiye to tum kisi ek dost se nahi poochte — tum kam se kam `R = 3` doston se poochte ho aur unke versions mein se sabse naya (highest version number wala) utha lete ho.

Yahan magic numbers ka hai: `R + W = 3 + 3 = 6`, jo `N = 5` se bada hai. Iska matlab — jin 3 doston ne latest copy save ki thi aur jin 3 doston se tumne poocha, in dono groups mein **kam se kam ek dost common zaroor hoga** (pigeonhole principle: 3 + 3 = 6 logon ki "slots" 5 doston mein fit nahi hoti bina overlap ke). Wahi common dost tumhe latest version de dega. Agar `W = 2` aur `R = 2` rakhte (`R + W = 4 < 5`), to ho sakta tha jin 2 ne save kiya aur jin 2 se tumne poocha wo bilkul alag log hon — phir tum purana version padh lete. Yahi quorum ka core idea hai: overlap force karke staleness rok do.

## How It Works

1. **N, W, R define karo:** `N` = total replicas per piece of data (jaise `N = 3`). `W` = write quorum, yaani ek write tab successful maana jaata hai jab kam se kam `W` replicas ne acknowledge kar diya. `R` = read quorum, yaani read ke time client kam se kam `R` replicas se value fetch karta hai. Typical setup: `N = 3, W = 2, R = 2`.

2. **Write path:** Client (ya coordinator node) write request ko parallel mein saare `N` replicas ko bhejta hai, har value ke saath ek version marker (jaise ek timestamp ya vector clock) attach karke. Coordinator tab tak wait karta hai jab tak `W` acknowledgements aa na jaayein. `N = 3, W = 2` mein, agar do replicas ~5 ms mein respond kar dein aur teesra slow (~40 ms) hai, to client ko 5 ms pe hi "write OK" mil jaata hai — teesre replica ka wait nahi karna padta. Isse tail latency control mein rehti hai.

3. **Read path:** Client `R` replicas se value maangta hai. Unme se jo version sabse naya hota hai (highest timestamp / dominating vector clock) wahi return hota hai. `R = 2` mein do replicas se padha, dono ke versions compare kiye, latest wala diya.

4. **Overlap guarantee (`R + W > N`):** Kyunki latest write `W` replicas pe gayi aur read `R` replicas se ho raha hai, aur `R + W > N`, to in do sets ka intersection non-empty hai — kam se kam ek replica aisa hoga jisne latest write dekha aur jisko read bhi chhoo raha hai. Isliye read mein latest value zaroor present hoti hai (badi version ke roop mein). Ye **strong consistency** (more precisely, read-your-writes / latest-value visibility) deta hai.

5. **Read repair:** Read ke time agar coordinator ko `R` replicas mein version mismatch dikhe (kisi ke paas purana data), to wo background mein stale replicas ko latest value se update kar deta hai. Isse divergence dheere-dheere heal hoti rehti hai.

6. **Anti-entropy / hinted handoff:** Jab koi replica down tha aur write miss kar gaya, to systems jaise Cassandra/Dynamo hinted handoff (temporary node us write ko hold karta hai) aur background Merkle-tree based anti-entropy se replicas ko eventually sync karte hain — quorum ke bahar wali consistency repair.

## Tradeoffs & Variants

- **Consistency vs latency/availability:** `R + W > N` strong-ish consistency deta hai but har request ko zyada replicas se response chahiye, to slowest-of-W (write) aur slowest-of-R (read) latency dominate karti hai. `R + W <= N` rakho to faster aur more available, par stale reads possible — yaani eventual consistency.

- **Read-heavy vs write-heavy tuning:** `N` fixed rakhke tum knobs adjust kar sakte ho. Read-heavy workload: `R = 1, W = N` (jaise `N = 3, W = 3, R = 1`) — reads super fast (ek hi replica), par writes slow aur fragile (ek bhi replica down to write block). Write-heavy: `W = 1, R = N` — writes fast par reads heavy. Balanced default `W = R = (N/2 + 1)` (majority), jaise `N = 3 → W = R = 2`, `N = 5 → W = R = 3`.

- **Sloppy quorum:** Strict quorum mein write ko exactly designated `N` replicas par hi jaana chahiye. Sloppy quorum (Dynamo-style) mein agar home replicas down hain to write kisi bhi `W` healthy nodes pe chala jaata hai (with a hint), taaki availability bani rahe — par ye temporarily `R + W > N` ka overlap guarantee tod sakta hai, yaani stale read window khul sakti hai.

- **Concurrent writes / conflict resolution:** Quorum sirf "kitne replicas" decide karta hai, "kaunsa value jeeta" nahi. Do concurrent writes alag-alag replicas pe pohonchein to conflict resolution chahiye — last-write-wins (timestamp based, data loss risk) ya vector clocks + application-side merge (jaise Dynamo ka shopping cart). Ye orthogonal but critical decision hai.

- **Latency outliers:** Bada `W`/`R` matlab zyada nodes ka wait — koi ek slow/GC-paused node tail latency badha deta hai. Isliye `N = 3, W = 2` jaisa setup popular hai: ek slow replica ignore ho jaata hai.

## When To Use It

- **Leaderless replicated datastores:** Amazon Dynamo, Cassandra, Riak, aur Voldemort — sab tunable quorum (`N`, `R`, `W` configurable per request) use karte hain taaki client consistency vs latency trade-off khud choose kar sake.
- **Strong-consistency-on-leaderless:** Jab tumhe single-leader ke bina bhi latest-value reads chahiye (no single point of write bottleneck) — `R + W > N` set karke quorum reads/writes.
- **Geo-distributed multi-DC setups:** Per-datacenter quorum (jaise Cassandra ka `LOCAL_QUORUM`) — latency kam rakhne ke liye local DC ke andar quorum, cross-DC round-trip avoid.
- **Consensus systems indirectly:** Raft/Paxos bhi majority quorum (`N/2 + 1`) pe chalte hain — leader election aur log commit ke liye majority of nodes ka agreement. Concept same hai: overlap of any two majorities guarantees a common node.

## Common Interview Gotchas

- **`R + W > N` "perfect" consistency nahi hai:** Ye sirf guarantee karta hai ki read set mein latest-written replica overlap karega. Par concurrent writes, sloppy quorum, ya read-during-incomplete-write jaisi situations mein anomalies aa sakti hain. Dynamo paper khud is point ko note karta hai — quorum strong consistency ka ek practical approximation hai, bullet-proof linearizability nahi (uske liye proper consensus chahiye). Interviewer aksar yahi probe karta hai.

- **`W = N` ko "best consistency" mat samajhna:** `W = N` likhne par har replica ko write success ke liye respond karna padta hai — ek bhi replica down to **writes completely block / fail** ho jaate hain. Availability gir jaati hai. Isiliye production majority (`N/2 + 1`) prefer karta hai, full `N` nahi.

- **Overlap ka WHY (pigeonhole):** Sirf "`R + W > N` se consistency milti hai" ratna kaafi nahi — reason batao: write `W` nodes pe, read `R` nodes pe; agar `R + W > N` to do subsets `N` nodes mein bina overlap fit nahi ho sakte, isliye kam se kam `R + W - N` replicas common honge. Concrete: `N = 3, W = 2, R = 2 → overlap >= 2 + 2 - 3 = 1`. Wahi 1 node latest value carry karta hai.

- **Quorum != ordering/conflict resolution:** Quorum batata hai kitne nodes participate karenge, par do concurrent writes mein "winner" kaun — ye separate mechanism (timestamps / vector clocks / LWW) decide karta hai. Inhe mix karke mat bolo.

- **Read repair latency ka effect nahi hai:** Read repair background mein hota hai (ya async), to wo read latency ko block nahi karta — par ye exam mein confuse ho jaata hai. Read overlap se latest value milta hai; repair sirf laggards ko theek karta hai future ke liye.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/consistency-coordination/conceptual_quiz_quorum.md`](../../../sysd-quizzes/consistency-coordination/conceptual_quiz_quorum.md) — `sysd-buddy quiz scaffold quorum` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update quorum --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — `N`/`W`/`R` sets, read-write overlap, aur `R + W > N` se latest-value guarantee ka interactive diagram.
