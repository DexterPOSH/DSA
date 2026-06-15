# SQL vs NoSQL — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update sql-vs-nosql --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines, what fundamentally distinguishes a SQL (relational) database from a NoSQL database? Name the four main families of NoSQL stores.

**Ideal answer:**
- SQL = relational, fixed/predefined table schema (schema-on-write), strong consistency via ACID transactions, query with SQL/JOINs.
- NoSQL = non-relational umbrella term, flexible schema (schema-on-read), built for horizontal scale, often trades strong consistency for availability/performance.
- Four families: **key-value** (Redis, DynamoDB), **document** (MongoDB), **wide-column** (Cassandra, Bigtable/HBase), **graph** (Neo4j).
- Bonus: mentions it's a spectrum, not a strict binary.

## Q2 (core)
Explain ACID vs BASE, and how it connects to the scaling model (vertical vs horizontal) of each. Why is horizontal scaling harder for traditional SQL?

**Ideal answer:**
- ACID = Atomicity, Consistency, Isolation, Durability — guaranteed by SQL via transactions, write-ahead logs, locks/MVCC.
- BASE = Basically Available, Soft state, Eventually consistent — replicas may diverge temporarily then converge.
- SQL → traditionally **vertical scaling** (bigger box) because cross-shard JOINs and distributed transactions are expensive/complex.
- NoSQL → **horizontal scaling** (sharding across many commodity nodes via a partition key), scaling out to millions of ops/sec.
- Horizontal scaling is hard for SQL because maintaining ACID + JOINs across shards requires costly distributed coordination (two-phase commit, distributed locks).
- Bonus: notes modern NewSQL (Spanner, CockroachDB) and Vitess close this gap.

## Q3 (tradeoff)
You're designing a system and must choose between a strongly-consistent SQL store and an eventually-consistent NoSQL store. Walk through the CAP-theorem tradeoff and the JOIN-vs-denormalization tradeoff that drive this decision.

**Ideal answer:**
- CAP applies during a network **partition**: must choose Consistency or Availability. SQL/single-leader → CP-leaning (may reject/error to stay consistent); Dynamo-style NoSQL → AP-leaning (stays available, may serve stale reads).
- Stresses CAP only matters during a partition; normally you can have both.
- JOINs vs denormalization: SQL normalizes (no duplication) and joins at read time — flexible ad-hoc queries but cross-shard JOINs costly. NoSQL denormalizes/duplicates for fast reads but pushes complexity to writes (fan-out updates) and requires query-driven modeling.
- Good answer: ties it to a concrete requirement (money/transactions → SQL/CP; high write throughput + tolerable staleness → NoSQL/AP).
- Bonus: mentions tunable consistency (Cassandra QUORUM, DynamoDB strongly-consistent reads).

## Q4 (gotcha)
A candidate says: "NoSQL means there's no schema, and it's always faster and scales better than SQL." What's wrong with this statement?

**Ideal answer:**
- "No schema" is wrong — there IS a schema, it's just implicit in application code (schema-on-read) rather than enforced by the DB (schema-on-write). Unmanaged, this causes schema drift and silent data-quality bugs.
- "Always faster" is wrong — NoSQL is fast only for the access patterns you modeled around. A bad partition key creates **hot partitions** and collapses throughput; an unindexed cross-partition scan can be slower than a SQL JOIN.
- "Always scales better" overstated — SQL scales far with vertical scaling, read replicas, sharding (Vitess), caching; many companies run billions of rows on Postgres/MySQL.
- Bonus: notes modern NoSQL DOES support transactions/strong consistency (MongoDB multi-doc ACID, DynamoDB transactions), so "no ACID" is also outdated.

## Q5 (applied)
Design the persistence layer for a large social app that has: (a) user accounts + payments, (b) a high-volume activity/news feed, (c) user sessions, and (d) a "people you may know" feature. Which store would you pick for each and why?

**Ideal answer:**
- (a) Accounts + payments → **SQL** (Postgres/MySQL): relational data, strong consistency + ACID for money, transactional integrity, no double-spend.
- (b) Activity/news feed → **wide-column NoSQL** (Cassandra) or document store: write-heavy, massive horizontal scale, time-ordered, eventual consistency acceptable.
- (c) Sessions → **key-value** (Redis): sub-millisecond `O(1)` lookups by key, ephemeral, TTL support.
- (d) People you may know → **graph DB** (Neo4j) or graph layer: efficient multi-hop relationship traversal that would need expensive recursive JOINs in SQL.
- Key insight: real systems use **polyglot persistence** — pick the right store per access pattern rather than forcing one DB.
- Bonus: mentions partition-key choice for the feed to avoid hot partitions, and a caching layer in front of SQL.
