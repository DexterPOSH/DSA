# SQL vs NoSQL

**Track:** Building Blocks
**Category:** Databases & Storage

## What It Is

SQL databases relational, schema-on-write stores hain jo strong consistency aur ACID transactions dete hain via ek fixed table schema, jabki NoSQL ek umbrella term hai un non-relational stores ke liye (key-value, document, wide-column, graph) jo flexible schema aur horizontal scalability ke liye aksar strong consistency ko trade karte hain.

## Real-World Analogy

Socho SQL database ek government office ka form hai — har column pehle se defined hai (Name, DOB, Aadhaar number), har field ka type fixed hai, aur agar ek bhi mandatory field khaali ya galat type ki hai to form reject ho jaata hai. Sab kuch neat rows aur columns mein, aur agar do clerks ek hi record ko ek saath update karein to ek lock lag jaata hai taaki data corrupt na ho. Ye discipline reliable hai par rigid — naya column add karna matlab poora form template change karna.

NoSQL ko socho ek notebook / diary jaisa jahan har page (document) pe tum jo chaaho likh sakte ho. Ek page pe sirf naam aur phone, agle page pe naam, address, 3 emails aur ek nested list of orders — koi nahi rok raha. Ye super flexible hai aur tum jaldi-jaldi pages add kar sakte ho (horizontal scale), par koi central rule nahi enforce karta ki har page ka format same ho, to consistency ki guarantee tumhe khud application mein sambhalni padti hai. SQL = strict structured form; NoSQL = flexible free-form diary.

## How It Works

1. **Schema-on-write vs schema-on-read:** SQL mein table ka schema pehle define hota hai (`CREATE TABLE users (id INT, email VARCHAR(255) UNIQUE ...)`). Write ke time DB validate karta hai ki data schema follow karta hai — isliye "schema-on-write". NoSQL document/KV stores mein aksar schema enforce nahi hota write pe; structure ko application read ke time interpret karti hai — "schema-on-read". Yahi flexibility ka source hai aur yahi data-quality risk ka bhi.

2. **ACID vs BASE:** SQL engines (Postgres, MySQL/InnoDB) ACID dete hain — Atomicity, Consistency, Isolation, Durability — via transactions, write-ahead logs aur locks/MVCC. Classic NoSQL aksar BASE model follow karta hai — Basically Available, Soft state, Eventually consistent — yaani replicas thodi der ke liye diverge ho sakte hain par eventually converge ho jaate hain. (Note: modern NoSQL jaise DynamoDB, MongoDB ab tunable consistency aur multi-document transactions bhi dete hain.)

3. **Scaling model:** SQL traditionally **vertical scaling** (ek bade box pe — zyada CPU/RAM) ke liye design hua, kyunki cross-shard JOINs aur distributed transactions mehnge hain. NoSQL **horizontal scaling** (sharding across many commodity nodes) ke liye built hai — data ko partition key pe baant ke 100s of nodes pe spread karo. Concrete: ek well-tuned single Postgres node aksar single-digit-thousand se ~low-tens-of-thousands writes/sec handle karta hai; Cassandra/DynamoDB jaise stores ko nodes add karke linearly scale karke millions of ops/sec tak le jaaya jaata hai.

4. **Data models (NoSQL flavors):**
   - **Key-value** (Redis, DynamoDB core): `O(1)` lookup by key, ~sub-millisecond latency in-memory (Redis aksar < 1 ms), value opaque blob.
   - **Document** (MongoDB, Couchbase): JSON/BSON documents, nested fields pe query/index kar sakte ho.
   - **Wide-column** (Cassandra, HBase, Bigtable): rows with dynamic columns, partition key + clustering key pe optimized, write-heavy time-series ke liye great.
   - **Graph** (Neo4j): nodes + edges, multi-hop relationship traversal jahan SQL ko recursive JOINs lagte.

5. **Query path:** SQL ek declarative query planner deta hai — tum `SELECT ... JOIN ... WHERE` likhte ho aur engine indexes use karke optimal plan choose karta hai; ad-hoc queries aur multi-table JOINs first-class hain. NoSQL mein aksar tumhe **query-driven data modeling** karni padti hai — access patterns pehle decide karo, fir data ko us shape mein store karo (often denormalized/duplicated), kyunki cross-partition JOINs ya to allowed nahi ya bahut slow hote hain.

## Tradeoffs & Variants

- **Consistency vs availability (CAP):** Network partition ke time SQL (single-node ya synchronous-replica) typically CP-leaning hota hai — consistency choose karke availability sacrifice. Classic NoSQL (Dynamo-style) aksar AP-leaning — available rehta hai par stale read de sakta hai. Interviewer yahaan probe karta hai: "agar do datacenters ke beech link toot jaaye, tum stale data serve karoge ya error?"

- **Schema flexibility ka hidden cost:** Flexible schema fast iteration deta hai, par koi enforcement na hone se "schema drift" ho jaata hai — alag-alag documents alag shapes, aur application mein har edge case handle karna padta hai. SQL ka rigid schema upfront friction deta hai par data integrity (foreign keys, unique constraints, NOT NULL) guarantee karta hai.

- **JOINs vs denormalization:** SQL normalize karke duplication avoid karta hai aur JOIN-time pe data jodta hai. NoSQL denormalize karke read fast banata hai, par ek logical entity multiple jagah duplicate hone se updates ko fan-out karna padta hai aur write-side complexity badhti hai.

- **Strong vs eventual vs tunable:** Modern stores ka middle ground important hai. DynamoDB per-request "strongly consistent read" allow karta hai (extra latency/cost ke saath); Cassandra per-query consistency level (`ONE`, `QUORUM`, `ALL`) tune karne deta hai. To "NoSQL = always eventual" ek outdated claim hai.

- **NewSQL middle path:** Spanner, CockroachDB, TiDB, Vitess — ye horizontal scale + SQL interface + (often) strong consistency dene ki koshish karte hain (Spanner TrueTime ke saath external consistency). To SQL-vs-NoSQL ek strict binary nahi, ek spectrum hai.

## When To Use It

**SQL choose karo jab:**
- Data highly relational hai aur strong consistency / ACID critical hai — **financial/banking ledgers, payments, inventory, orders** (paisa double-spend nahi hona chahiye).
- Complex ad-hoc queries, reporting, multi-table JOINs aur transactional integrity chahiye.
- Real systems: PostgreSQL, MySQL — banks, e-commerce order systems, ERP.

**NoSQL choose karo jab:**
- **Massive horizontal scale + high write throughput** chahiye aur eventual consistency acceptable hai — feeds, activity logs, metrics, time-series.
- Schema rapidly evolve hota hai ya highly variable hai — product catalogs, user profiles, CMS content (document stores like MongoDB).
- Simple, predictable access patterns by key with very low latency — sessions, caching, leaderboards (Redis / DynamoDB).
- Real systems: **Cassandra** (Netflix viewing history, Instagram), **DynamoDB** (Amazon cart/shopping), **Redis** (session/cache), **Neo4j / graph** (LinkedIn-style "people you may know", fraud rings), **Bigtable** (Google Search index).

Interview pattern: jab requirement mein "billions of rows, write-heavy, geo-distributed, flexible schema" dikhe → NoSQL signal. Jab "transactions, money, complex JOINs, strong consistency" dikhe → SQL signal. Real designs aksar **polyglot persistence** use karte hain — Postgres for orders + Redis for cache + Elasticsearch for search.

## Common Interview Gotchas

- **"NoSQL means no schema" — galat.** Schema hota hai, bas wo application code mein implicit hota hai (schema-on-read) instead of DB mein enforced. Bina discipline ke ye schema drift aur silent data-quality bugs banata hai. Better framing: "schema-on-write vs schema-on-read", not "schema vs no-schema".

- **"NoSQL is always faster / always scales better" — galat.** NoSQL specific access patterns ke liye fast hai jinke around tumne data model kiya. Galat partition key chuno to **hot partitions** ban jaate hain aur throughput collapse ho jaata hai. Aur ek unindexed cross-partition scan SQL JOIN se bhi slow ho sakta hai. Scale ka faayda free nahi — wo query-driven modeling ki cost pe aata hai.

- **"NoSQL = no transactions / no consistency" — outdated.** MongoDB (4.0+) multi-document ACID transactions deta hai; DynamoDB transactions aur strongly-consistent reads support karta hai; Cassandra tunable consistency deta hai. Blanket "no ACID" bolna red flag hai.

- **"SQL scale nahi karta" — overstated.** SQL bahut door tak vertical scaling + read replicas + sharding (Vitess) + caching se scale karta hai. Bahut companies billions of rows Postgres/MySQL pe chalaati hain. Bottleneck aksar write throughput aur cross-shard transactions pe aata hai, na ki turant.

- **CAP ko galat samajhna:** CAP sirf network **partition** ke time relevant hai — normal operation mein consistency aur availability dono mil sakte hain. "NoSQL ne availability ke liye consistency choose kiya" ko nuance ke saath bolo: ye sirf partition scenario ka tradeoff hai, aur ab aksar tunable hai.

- **JOINs ko nazar-andaaz karna:** NoSQL pe denormalize karoge to read fast par writes (fan-out updates) complex. Interviewer poochega "agar ek user apna naam change kare jo 50 documents mein duplicate hai, tum kaise consistent rakhoge?" — ready raho.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/databases-storage/conceptual_quiz_sql_vs_nosql.md`](../../../sysd-quizzes/databases-storage/conceptual_quiz_sql_vs_nosql.md) — `sysd-buddy quiz scaffold sql-vs-nosql` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update sql-vs-nosql --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — SQL table schema vs NoSQL document/key-value/wide-column models ka side-by-side diagram, aur ACID vs BASE / scaling axes ka illustration.
