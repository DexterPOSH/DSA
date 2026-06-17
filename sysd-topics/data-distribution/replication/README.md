# Replication

**Track:** Building Blocks
**Category:** Data Distribution

## What It Is

Replication ka matlab hai same data ki multiple copies ko alag-alag nodes (machines / data centers) pe rakhna, taaki system ko higher availability, better read throughput, aur fault tolerance mile.

## Real-World Analogy

Socho ek popular library hai jismein ek hi famous book ki bahut demand hai. Agar sirf ek hi copy ho (single node), to ek time pe ek hi insaan padh sakta hai, aur agar wo copy kho jaaye ya phat jaaye to book hi gayi — total data loss.

Ab library 5 copies bana ke alag-alag branches mein rakh deti hai. Faayde:
- **Read scale:** 5 log ek saath padh sakte hain, kyunki har branch apni local copy se serve karti hai.
- **Fault tolerance:** Ek branch jal bhi jaaye to book baaki 4 branches mein safe hai.
- **Locality:** Delhi wala banda Delhi branch se padhega, Mumbai wala Mumbai se — low latency.

Lekin ek nayi headache aa gayi: agar author book ka naya edition release kare (a write/update), to saari 5 copies ko update karna padega. Jab tak sab copies sync nahi hoti, alag-alag branch ke log **alag version** padh rahe honge. Yahi replication ka central dard hai — "copies banana easy hai, unko consistent rakhna mushkil."

## How It Works

Core idea: ek logical dataset, multiple physical replicas. Writes ko sab replicas tak propagate karna padta hai; reads kisi bhi replica se serve ho sakti hain. Architecture mukhyatah teen tarah ki hoti hai:

1. **Single-leader (master-slave / primary-replica):**
   - Ek node **leader** hota hai. Saari writes pehle leader pe jaati hain.
   - Leader change ko ek **replication log** (jaise MySQL binlog, Postgres WAL) mein likhta hai aur followers ko stream karta hai.
   - **Followers** is log ko apply karke apni copy update karte hain. Reads followers se bhi serve ho sakti hain → read scaling.
   - Ye sabse common pattern hai (MySQL, PostgreSQL, MongoDB default, Redis).

2. **Replication kaise propagate hota hai (sync vs async):**
   - **Synchronous:** Leader client ko `OK` tabhi bolta hai jab kam se kam ek (ya N) follower ne write confirm kar di. Durable, par har write mein extra round-trip — agar follower 5 ms door hai to wo 5 ms har write pe add ho jaata hai. Follower slow/down hua to leader block ho sakta hai.
   - **Asynchronous:** Leader local commit karke turant `OK` de deta hai, followers baad mein catch up karte hain. Fast (sub-millisecond ack), par leader crash hua aur log abhi tak followers tak nahi pahuncha to **un-replicated writes lost** ho sakti hain.
   - Practical middle ground: **semi-synchronous** — ek follower sync, baaki async.

3. **Replication lag:** Async setups mein followers leader se kuch peeche hote hain — typically few ms se lekar, overloaded system mein, several seconds tak. Lag ki wajah se ek user apni hi likhi cheez turant agle read mein na dekhe (read-your-own-writes problem).

4. **Multi-leader:** Multiple nodes writes accept karte hain (aksar ek leader per data center), aur ek dusre ko async replicate karte hain. Cross-region write latency kam hoti hai, par do leaders pe same row simultaneously edit ho jaaye to **write conflict** aata hai jise resolve karna padta hai.

5. **Leaderless (Dynamo-style):** Koi fixed leader nahi. Client (ya coordinator) write ko `N` replicas pe bhejta hai aur kam se kam `W` se ack ka wait karta hai; read `R` replicas se hoti hai. Agar `W + R > N`, to read aur write quorums overlap karte hain → latest value milne ki guarantee. Example: `N=3, W=2, R=2`. Cassandra, DynamoDB, Riak isi family se hain.

## Tradeoffs & Variants

- **Sync vs async (durability vs latency):** Sync = no data loss on leader failure, par higher write latency aur availability risk (follower down → writes stall). Async = fast aur available, par failover pe data loss possible. Interviewer aksar yahi probe karta hai — "leader crash hua, kitna data lose ho sakta hai?"

- **Single-leader vs multi-leader vs leaderless:**
  - Single-leader: simple, no write conflicts, par leader ek single write bottleneck aur SPOF hai (failover needed).
  - Multi-leader: better write availability & geo-locality, lekin **conflict resolution** ki complexity (LWW, version vectors, CRDTs).
  - Leaderless: high availability aur tunable consistency via `W`/`R`, par read-repair / anti-entropy aur eventual consistency ke saath jeena padta hai.

- **Consistency tuning:** `W + R > N` strong-ish read consistency deta hai par har op slow; `W=1, R=1` fastest par stale reads likely. Ye knob system design ka favourite hai.

- **Failover correctness:** Async ke saath automatic failover risky hai — purana leader vaapas aa jaaye to **split-brain** (do leaders) ho sakta hai, aur un-replicated writes silently discard ho jaate hain. Isiliye fencing / single-writer guarantees chahiye.

## When To Use It

- **Read-heavy workloads:** Read replicas add karke read QPS scale karo bina leader ko choke kiye. Jaise ek social feed jahan reads:writes ratio 100:1 hai — followers se reads serve karo.
- **High availability / disaster recovery:** Ek replica down ho to dusre se serve karo; cross-region replica rakho taaki poora data center fail hone pe bhi survive karo.
- **Geo-distributed low latency:** User ke nearest region mein replica rakho — multi-leader ya per-region read replicas. (e.g., global apps using CockroachDB / Spanner-style geo-replication.)
- **Real systems:** MySQL/PostgreSQL read replicas, MongoDB replica sets (leader election via Raft-like protocol), Kafka partition replication (ISR — in-sync replicas), Cassandra/DynamoDB leaderless quorums.

Note: Replication data ki **copies** banata hai (har node pe poora dataset ya partition ka pura set). Ye **sharding/partitioning** se alag hai (jo dataset ko TUKDON mein baant ke alag nodes pe rakhta hai). Real systems aksar dono combine karte hain: partition karo, phir har partition ko replicate karo.

## Common Interview Gotchas

- **"Replication == sharding" — NAHI.** Replication = same data ki multiple full copies (availability + read scale). Sharding = different data on different nodes (write/storage scale). Inko mix mat karo; aksar dono saath chahiye hote hain.

- **Async replication mein data loss ko underestimate karna:** Agar leader async setup mein crash kare aur recently-acked writes abhi followers tak nahi pahunche, to wo writes **permanently lost** ho sakti hain even after client ko `OK` mil chuka tha. "We replicate, so we never lose data" — ye galat hai jab tak sync/quorum durable na ho.

- **Replication lag ke side-effects bhulna:** Async follower reads stale ho sakti hain. Classic bug: user profile update karta hai, page reload karta hai, aur purana data dikhta hai (read hit a lagging follower). Fixes: read-your-writes consistency (apni writes ke baad leader se padho), monotonic reads (same user ko hamesha aage-badhta hua data), ya sticky routing.

- **`W + R > N` ko silver bullet samajhna:** Quorum overlap guarantee karta hai ki read kam se kam ek up-to-date replica touch karegi, par ye **linearizability guarantee nahi** karta — concurrent writes, sloppy quorums / hinted handoff, aur read-repair timing ke chalte edge cases mein stale ya conflicting values aa sakte hain.

- **Failover = free assumption:** Leader failover instant aur lossless nahi hai. Failure detection timeout, new-leader election, aur clients ka reroute — sabme time lagta hai, aur split-brain ka risk hota hai. Interview mein failover ko explicitly address karo.

- **Sync replication ki availability cost ignore karna:** Fully synchronous setup mein agar ek required follower slow/down ho, to writes ruk jaati hain — yaani durability badhane ke chakkar mein availability gir jaati hai (CAP ka practical taste).

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/data-distribution/conceptual_quiz_replication.md`](../../../sysd-quizzes/data-distribution/conceptual_quiz_replication.md) — `sysd-buddy quiz scaffold replication` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update replication --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — single-leader / multi-leader / leaderless topologies, write propagation, aur replication lag ka interactive diagram.
</content>
</invoke>
