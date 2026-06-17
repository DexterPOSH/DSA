# Sharding & Partitioning

**Track:** Building Blocks
**Category:** Data Distribution

## What It Is

Sharding ek technique hai jisme ek bade dataset ko chhote independent chunks (shards/partitions) mein todkar alag-alag nodes pe rakha jaata hai, taaki ek single machine ki storage aur throughput limits ko cross karke system horizontally scale kar sake.

## Real-World Analogy

Socho ek city ki ek hi giant library hai jisme 10 crore books hain, aur ek hi building, ek hi entry gate. Jaise-jaise books badhti hain, building chhoti pad jaati hai aur entry gate pe log lambi line mein khade rehte hain — ek hi librarian sab handle nahi kar sakta. Ye hamara single overloaded database hai.

Ab city decide karti hai ki ek hi mega-library ki jagah, alag-alag branches banayenge: branch A mein authors A-G, branch B mein H-N, branch C mein O-Z. Har branch ka apna building, apna librarian, apna gate. Ye **range partitioning** hai. Problem: agar ek author (jaise "Harry Potter" series) super popular hai, to uski branch pe bheed lag jaati hai — baaki branches khaali. Ye **hot shard** hai.

Iska fix: book ke title ka ek hash nikaalo aur usse decide karo kaunsi branch — to popular aur unpopular books evenly bikhar jaati hain. Ye **hash partitioning** hai. Lekin ab "saari A-author ki books" ek saath dhoondhna mushkil ho gaya kyunki wo kai branches mein scatter hain. Yahi sharding ka core trade-hai: load distribute karo, par "ek hi jagah related data" ki convenience kho do.

## How It Works

1. **Partition key (shard key) chuno:** Pehla aur sabse critical step — kaunsa column/field decide karega ki ek row kis shard pe jaayegi? Jaise `user_id`, `tenant_id`, ya `order_id`. Yahi key system ki scalability aur hotspots dono ko define karti hai. Galat key = poora system re-design.

2. **Partitioning strategy lagao:** Shard key se shard number nikaalne ke teen common tareeke:
   - **Range-based:** Key ranges shards pe map. Jaise `user_id 1–1M → shard 0`, `1M–2M → shard 1`. Range queries (`BETWEEN`) fast, lekin sequential keys (auto-increment IDs, timestamps) latest shard pe pile up karte hain → hotspot.
   - **Hash-based:** `shard = hash(key) % N`. Distribution uniform, par range queries scatter ho jaati hain. Aur plain `% N` mein agar `N` badla (shard add/remove), to ~saara data remap hota hai — isiliye production mein **consistent hashing** use hoti hai jahan sirf ~K/N keys move hon.
   - **Directory-based:** Ek lookup table (`key → shard`) maintain karo. Maximum flexibility (kisi bhi key ko kahin bhi rakh sakte ho, rebalance easy), par lookup service ek extra hop aur single point of failure ban sakta hai.

3. **Route the request:** Application ya ek proxy/router layer (jaise Vitess for MySQL, or a coordinator) shard key dekhkar query ko sahi shard pe bhejti hai. Ek single-shard point lookup typically sub-millisecond se 1-2 ms routing overhead add karta hai — bahut kam.

4. **Scale numbers ka feel:** Maan lo ek node comfortably ~5,000 writes/sec aur ~1 TB data handle karta hai. Aapko 50,000 writes/sec aur 10 TB chahiye → ~10 shards lagao, har shard apne slice (~5K wps, ~1 TB) ko handle kare. Sharding throughput aur storage dono ko linearly (ideally) badhata hai.

5. **Cross-shard operations:** Agar ek query ka data ek hi shard pe ho (single-shard query), to fast. Lekin agar query multiple shards ko touch kare (jaise "saare users count karo", ya do users ka data jo alag shards pe hain), to **scatter-gather** karna padta hai — har shard pe query bhejo, results merge karo. Ye slow hota hai aur tail latency badhata hai (jitne shards, utna zyada chance ki ek slow ho).

6. **Rebalancing:** Jaise data badhta hai ya hotspot banta hai, shards ko split/move karna padta hai. Consistent hashing ya fixed-number-of-virtual-partitions (jaise pehle se 1024 logical partitions banao, baad mein unhe physical nodes pe redistribute karo — ye "shard splitting" approach Kafka/Dynamo-style systems use karte hain) is migration ko predictable banate hain.

## Tradeoffs & Variants

- **Sharding vs Replication (interviewer yahan clarity test karta hai):** Replication = **same** data ki copies multiple nodes pe (read scaling + availability). Sharding = **different** data ke pieces alag nodes pe (write + storage scaling). Ye complementary hain — real systems dono karte hain: har shard ko replicate bhi karte hain. Inhe mat confuse karo.

- **Range vs Hash vs Directory:** Range → range/scan queries fast par hotspots ka risk (monotonic keys). Hash → even distribution par range queries scatter ho jaati hain. Directory → flexible aur easy rebalance par extra lookup hop + SPOF risk.

- **Shard key choice — high cardinality + even access:** Key ki cardinality high honi chahiye (taaki enough distinct values ho to spread kar sakein) aur access pattern even hona chahiye. Low-cardinality key (jaise `country` jahan 80% traffic ek country se) → kuch shards hot, baaki idle.

- **Physical vs Logical sharding:** Logical shards (jaise 1024 partitions) ko initially kam physical nodes pe pack karo, phir grow hone pe unhe spread karo. Ye over-provisioning ke bina future rebalancing ko cheap banata hai.

- **Distributed transactions ka cost:** Multi-shard atomic write chahiye to 2-phase commit / saga patterns lagte hain — slow aur complex. Best practice: shard key aise chuno ki ek logical transaction ek hi shard pe rahe (jaise sab data of one `tenant_id` ek shard pe).

## When To Use It

- **Jab single node ki write throughput ya storage limit hit ho jaaye** — read replicas se kaam nahi banta (wo sirf reads scale karte hain), to writes/data distribute karne ke liye sharding chahiye.
- **Multi-tenant SaaS:** `tenant_id` pe shard karo — har tenant ka data ek shard pe, clean isolation aur cross-tenant queries rare.
- **Real systems:** Instagram aur Notion Postgres ko `user_id`/`workspace_id` pe shard karte hain. Vitess MySQL ko shard karta hai (YouTube, Slack). MongoDB/Cassandra/DynamoDB built-in sharding (partition key) dete hain. Discord messages ko `channel_id` pe Cassandra mein shard karta hai.
- **Mat use karo jab:** Data single beefy node + read replicas mein comfortably fit ho. Sharding heavy operational complexity laata hai (cross-shard joins, rebalancing, distributed transactions) — premature sharding ek classic over-engineering mistake hai.

## Common Interview Gotchas

- **"Sharding aur replication same hain" — NO.** Sabse common confusion. Replication = copies of same data (read scale + HA). Sharding = split of different data (write + storage scale). Interviewer specifically isko probe karta hai. Real design mein dono saath chalte hain.

- **Auto-increment / timestamp ko shard key banana:** Range-based sharding mein monotonically increasing key (auto-increment ID, `created_at`) hamesha **latest shard** pe writes daalti hai → ek shard hot, baaki idle. Fix: hash the key, ya ek high-cardinality dimension pe shard karo.

- **Cross-shard query ka cost underestimate karna:** "Saare users ko name se search karo" jaisi query agar shard key pe nahi hai, to har shard pe scatter-gather chalega — slow aur tail-latency heavy. Aksar iska answer ek alag denormalized index (jaise Elasticsearch) ya secondary index hota hai, naki sharded primary DB pe scan.

- **Naive `hash(key) % N` aur resharding pain:** `% N` simple lagta hai, par jab `N` badlega (capacity add karne pe), to almost saara data remap hoga → massive migration / downtime. Isiliye consistent hashing ya fixed logical-partition count use karte hain.

- **Resharding ko free maan lena:** Live system ko reshard karna ek bada operational project hai — dual writes, backfill, cutover, verification. Interview mein "main shard kar dunga" bolna easy hai; "kaise migrate karunga without downtime" wahan depth dikhti hai.

- **Hotspot sirf data size ka nahi, access ka bhi hota hai:** Ek "celebrity" user (millions of followers) ek single shard ko overload kar sakta hai even agar data evenly bata ho. Solution: us key ko further split karna ya cache lagana.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/data-distribution/conceptual_quiz_sharding_partitioning.md`](../../../sysd-quizzes/data-distribution/conceptual_quiz_sharding_partitioning.md) — `sysd-buddy quiz scaffold sharding-partitioning` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update sharding-partitioning --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — partition strategies (range/hash/directory), shard routing, aur hotspot vs balanced distribution ka interactive diagram.
