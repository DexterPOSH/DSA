# ACID vs BASE

**Track:** Building Blocks
**Category:** Databases & Storage

## What It Is

ACID aur BASE do opposite consistency philosophies hain: ACID (Atomicity, Consistency, Isolation, Durability) har transaction ko strict aur immediately-consistent rakhta hai, jabki BASE (Basically Available, Soft state, Eventually consistent) availability aur scale ke liye strong consistency ko thoda loosen karke "data thodi der baad sahi ho jaayega" wala model deta hai.

## Real-World Analogy

Socho ek bank ki branch hai vs ek WhatsApp group chat.

**ACID = bank transfer.** Jab aap A account se B account mein 5000 rupees transfer karte ho, to ya to poora transfer hota hai (A se kate AUR B mein jude), ya bilkul nahi hota — beech ka koi state allowed nahi (5000 A se kat gaye par B mein nahi pahunche, ye kabhi nahi hona chahiye). Aur jaise hi transfer "done" dikhta hai, har teller, har ATM turant updated balance dikhayega. Yahan bank thoda slow ho sakta hai (lock lagega, double-check hoga), par galti ki gunjaish zero hai.

**BASE = WhatsApp group.** Aapne message bheja, aapko turant "sent" dikh gaya — system available rehta hai chaahe kuch members offline hon. Par har member ke phone pe message thodi-thodi der ke gap se pahunchta hai (kisi ko 1 second, kisi ko 5 second). Kuch second ke liye different log alag-alag "version" dekh rahe hote hain (soft state), par **eventually** sabke paas same messages same order mein aa jaate hain. Yahan goal hai "kabhi block mat karo, fast raho" — perfect instant agreement se zyada important hai ki system chalta rahe.

Bank ko BASE pe nahi chala sakte (paisa gayab ho jaayega), aur WhatsApp ko har message pe global lock laga ke ACID nahi bana sakte (1 billion users pe ye crawl kar jaayega). Right tool, right job.

## How It Works

**ACID — strong consistency machinery:**

1. **Atomicity** — Ek transaction ek all-or-nothing unit hai. Database ek write-ahead log (WAL) maintain karta hai: changes pehle log mein likhe jaate hain, phir apply hote hain. Agar beech mein crash ho gaya, to recovery ke time incomplete transaction ko rollback kar diya jaata hai. To partial update kabhi visible nahi hota.

2. **Consistency** — Transaction database ko ek valid state se doosre valid state mein le jaata hai, saare constraints (foreign keys, unique, CHECK, balance >= 0) respect karte hue. Constraint violate hua to poora transaction abort.

3. **Isolation** — Concurrent transactions aise chalte hain jaise wo serial (ek-ke-baad-ek) chale ho. Ye usually locks (2-phase locking) ya MVCC (multi-version concurrency control, jaise PostgreSQL) se hota hai. Isolation levels — Read Committed, Repeatable Read, Serializable — define karte hain kitna strict isolation hai. Serializable sabse strong par sabse slow.

4. **Durability** — Commit ho gaya matlab data disk pe (ya replicated) safe hai, power chali jaaye tab bhi. WAL ko `fsync` karke ye guarantee milti hai.

Cost: ye sab coordination latency add karta hai. Ek single-node ACID commit typically ~1-10ms (fsync ke saath), aur distributed ACID (2-phase commit across nodes) mein har commit pe cross-node round-trips — easily 10-100ms+, aur ek node down hone pe poora commit block ho sakta hai.

**BASE — availability-first machinery:**

1. **Basically Available** — System har request ka response deta hai, chaahe wo thoda stale data ho. Reads/writes block nahi hote even if some replicas down hain.

2. **Soft state** — System ka state time ke saath change ho sakta hai bina kisi naye input ke, kyunki replicas background mein converge ho rahe hote hain (anti-entropy, read-repair).

3. **Eventually consistent** — Agar naye writes ruk jaayein, to thodi der baad saare replicas same value pe pahunch jaate hain. Ye "thodi der" usually milliseconds se seconds hoti hai (e.g., DynamoDB cross-region replication typically sub-second se ~1-2s), par guarantee sirf "eventually" ki hai.

Mechanics: writes ko multiple replicas pe async push kiya jaata hai. Quorum systems (jaise Dynamo-style) mein N replicas, W write-quorum, R read-quorum tune hota hai. Agar W + R > N, to strong-ish consistency; agar W + R <= N, to pure eventual consistency par max availability/throughput (often 100K+ QPS easily scale karta hai horizontally).

## Tradeoffs & Variants

- **CAP connection** — Network partition (P) ke time aapko choose karna padta hai: ACID systems usually CP (consistency choose karte hain, partition mein unavailable ho jaate hain), BASE systems usually AP (available rehte hain, temporary inconsistency accept karte hain). Interviewer aksar yahin probe karta hai.

- **Latency vs correctness** — ACID = predictable correctness par higher write latency aur lower write throughput, kyunki coordination/locks lagte hain. BASE = low latency, massive horizontal scale, par application ko stale reads aur conflict resolution handle karna padta hai.

- **Distributed ACID ka cost** — Single-node ACID sasta hai. Multi-node ACID (2-phase commit, ya Spanner-style with TrueTime) coordination overhead laata hai. Google Spanner ACID + horizontal scale dono deta hai par atomic clocks/GPS (TrueTime) ki infra cost pe.

- **Tunable consistency** — Cassandra aur DynamoDB per-query consistency tune karne dete hain: ek hi DB mein critical read ke liye strong (quorum) aur cheap read ke liye eventual choose kar sakte ho. To "ACID vs BASE" hamesha binary nahi — ek spectrum hai.

- **NewSQL middle ground** — CockroachDB, Spanner, YugabyteDB ACID guarantees ko distributed scale pe laate hain, ye purana "ACID = doesn't scale" assumption todte hain.

## When To Use It

**ACID choose karo jab:**
- Financial / payment systems — bank ledgers, Stripe-style payments, inventory deduction. Money aur stock kabhi double-count ya lose nahi hone chahiye.
- Booking systems jahan double-booking unacceptable hai (seat reservation, ticketing).
- Examples: PostgreSQL, MySQL (InnoDB), Oracle, Google Spanner, CockroachDB.

**BASE choose karo jab:**
- High-scale, high-availability systems jahan thoda stale data acceptable hai — social feeds, like/view counters, product catalogs, session stores, shopping carts (Amazon ka famous example).
- Globally distributed, write-heavy workloads jahan low latency aur "always on" critical hai.
- Examples: Amazon DynamoDB, Cassandra, Riak, MongoDB (default tunable), Couchbase.

Pattern recognition: agar interview prompt mein "billions of users", "global", "high write throughput", "feed/timeline", "always available" aaye → BASE/eventual ki taraf socho. Agar "transaction", "balance", "payment", "must not lose/double-count" aaye → ACID.

## Common Interview Gotchas

- **"NoSQL = BASE, SQL = ACID" — ye galat hai.** Ye properties consistency model ke baare mein hain, data model ke baare mein nahi. MongoDB (NoSQL) multi-document ACID transactions support karta hai. Spanner aur CockroachDB distributed hain par fully ACID. To NoSQL hone se BASE automatic nahi ho jaata.

- **"BASE means data is wrong / can be lost" — nahi.** Eventually consistent ka matlab durability loss nahi hai. Writes durably store hote hain (multiple replicas pe), bas saare replicas pe ek hi waqt par visible nahi hote. Eventual ka matlab "temporarily different across replicas", "lost" nahi.

- **Consistency word ka double meaning** — ACID ka "C" (constraints valid rakhna, app-level integrity) aur CAP/eventual consistency ka "consistency" (saare replicas same value dikhaayen) DO ALAG cheezein hain. Interviewer specifically isse trap karta hai. ACID's C = data integrity rules; CAP's C = replica agreement (linearizability).

- **"ACID can't scale" — outdated.** Spanner, CockroachDB, YugabyteDB prove karte hain ki ACID + horizontal scale possible hai, bas coordination cost (TrueTime/consensus) ke saath.

- **Eventual consistency conflicts ignore karna** — BASE mein concurrent writes conflict kar sakte hain. Aapko conflict resolution strategy chahiye: last-write-wins (timestamp based, par data lose kar sakta hai), version vectors, ya CRDTs. "Eventually consistent" bol dena kaafi nahi — kaise converge hoga ye explain karna padta hai.

- **Soft state ko durability se confuse karna** — Soft state ka matlab replicas background mein converge ho rahe hain, na ki data volatile/non-durable hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/databases-storage/conceptual_quiz_acid_vs_base.md`](../../../sysd-quizzes/databases-storage/conceptual_quiz_acid_vs_base.md) — `sysd-buddy quiz scaffold acid-vs-base` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update acid-vs-base --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — ACID transaction flow vs BASE replica-convergence ka side-by-side interactive diagram.
