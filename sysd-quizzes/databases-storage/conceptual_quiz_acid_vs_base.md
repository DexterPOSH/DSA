# ACID vs BASE — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update acid-vs-base --quiz-score N/M` -->

## Q1 (warm-up)
ACID aur BASE ka full form kya hai, aur ek line mein dono ki core philosophy kya hai?

**Ideal answer:**
- ACID = **A**tomicity, **C**onsistency, **I**solation, **D**urability. Philosophy: strict, immediately-consistent transactions — correctness over availability.
- BASE = **B**asically Available, **S**oft state, **E**ventually consistent. Philosophy: availability and scale over strong consistency — system stays up, replicas converge later.
- Bonus credit: ye opposite ends of a consistency spectrum hain, binary choice nahi.

## Q2 (core)
ACID ke "Atomicity" aur "Durability" properties database mechanically kaise guarantee karta hai?

**Ideal answer:**
- **Atomicity**: all-or-nothing via a write-ahead log (WAL) — changes pehle log mein, phir apply; crash hone pe incomplete transaction rollback ho jaata hai. Partial state kabhi visible nahi.
- **Durability**: commit ke baad data persist (WAL ko `fsync` to disk, and/or replicated) — power loss / crash ke baad bhi data survive karta hai.
- Strong answer mentions: commit = log durably flushed; recovery replays/rolls back from the log.
- (Bonus: Isolation via locks/2PL or MVCC; Consistency via constraint enforcement.)

## Q3 (tradeoff)
ACID aur BASE ke beech choose karte waqt CAP theorem kaise relate karta hai, aur har choice ka latency/throughput pe kya asar padta hai?

**Ideal answer:**
- Network partition (P) ke during choose karna padta hai: ACID systems usually **CP** (consistency pick karte hain, partition mein unavailable ho jaate hain), BASE systems usually **AP** (available rehte hain, temporary inconsistency accept karte hain).
- ACID: higher write latency / lower throughput due to locks/coordination; distributed ACID (2-phase commit) adds cross-node round-trips (10-100ms+) aur ek node down → commit block.
- BASE: low latency, high horizontal throughput (async replication, quorum tuning W+R), par stale reads aur conflict resolution app ko handle karne padte hain.
- Bonus: tunable consistency (Cassandra/DynamoDB) — W+R > N for strong-ish, else eventual.

## Q4 (gotcha)
"NoSQL means BASE and SQL means ACID" — ye statement sahi hai ya galat? Aur ACID ka 'C' (Consistency) CAP/eventual-consistency wale 'consistency' se kaise alag hai?

**Ideal answer:**
- Statement **galat** hai. Consistency model data model se independent hai: MongoDB (NoSQL) multi-document ACID transactions deta hai; Spanner/CockroachDB distributed hote hue bhi fully ACID hain. NoSQL hone se BASE automatic nahi.
- ACID's **C** = data integrity / constraints valid rakhna (foreign keys, CHECK, balance >= 0) — ek transaction valid state se valid state mein le jaata hai.
- CAP/eventual **consistency** = saare replicas same value dikhaayen (linearizability / replica agreement).
- Ye DO alag concepts hain jinhe same word share karta hai — yahi common trap hai.
- Bonus: BASE != data loss; eventually consistent writes still durable, bas turant har replica pe visible nahi.

## Q5 (applied)
Aap ek system design kar rahe ho jisme (a) ek payment/wallet ledger hai aur (b) ek social feed ka like-counter hai. Har component ke liye ACID ya BASE choose karoge aur kyun? Real systems name karo.

**Ideal answer:**
- **Payment/wallet ledger → ACID.** Money double-count ya lose nahi hona chahiye; atomic debit+credit, isolation se race conditions avoid. Examples: PostgreSQL/MySQL(InnoDB), Spanner, CockroachDB.
- **Like-counter / feed → BASE.** Massive write throughput + always-available; thoda stale count acceptable hai (kisi ko 999 dikhe kisi ko 1000 for a second). Examples: DynamoDB, Cassandra, Redis.
- Strong answer: ek hi system mein dono coexist kar sakte hain (polyglot persistence) — critical path ACID, high-scale non-critical path BASE.
- Bonus: counter conflicts ke liye CRDTs / atomic counters mention karna; pattern recognition — "must not lose money" → ACID, "billions of users, always on" → BASE.
