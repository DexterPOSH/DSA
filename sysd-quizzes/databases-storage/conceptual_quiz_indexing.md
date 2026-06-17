# Indexing — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update indexing --quiz-score N/M` -->

## Q1 (warm-up)
What is a database index, and what is the core tradeoff you accept when you add one?

**Ideal answer:**
- An index is an auxiliary data structure (usually a B-tree / B+ tree, sometimes hash) built on one or more columns that lets the DB find rows without a full-table scan — turning lookups from `O(n)` into roughly `O(log n)` (or `O(1)` for hash).
- The tradeoff: faster reads, but at the cost of (a) extra storage and (b) slower writes — every `INSERT`/`UPDATE`/`DELETE` must also maintain each affected index.
- Bonus: indexes only help queries that filter/join/sort on the indexed column with high selectivity.

## Q2 (core)
Why is a B+ tree index able to find a row among 10 million in just a few page reads, and how does its leaf structure also make range queries like `WHERE age BETWEEN 25 AND 30` efficient?

**Ideal answer:**
- B+ tree is **balanced** with **high fan-out** (many keys per node), so even 10M rows fit in ~3-4 levels → a lookup is ~3-4 node reads, i.e. `O(log n)`, just a few page/disk accesses.
- Keys are kept **sorted**, so at each node you follow the correct child pointer toward the target.
- In a B+ tree, data/pointers live only at the **leaf level**, and leaves are **linked together in sorted order** (linked list).
- For a range query you locate the start key, then **scan sequentially across leaves** until the range ends — no re-traversal. Same property gives `ORDER BY` cheaply.

## Q3 (tradeoff)
Compare B-tree indexes with LSM-trees. Which workloads suit each, and why?

**Ideal answer:**
- **B-tree = read-optimized**, does in-place updates (random writes); great for read-heavy OLTP and point/range lookups. Used by Postgres, MySQL/InnoDB.
- **LSM-tree = write-optimized**: buffers writes in an in-memory memtable, flushes to append-only **sequential** on-disk segments (SSTables), and merges them via background **compaction**. Sequential writes → very high write throughput. Used by Cassandra, RocksDB, LevelDB, ScyllaDB.
- LSM read cost: a read may need to check multiple SSTables; **Bloom filters** mitigate by skipping SSTables that definitely lack the key.
- Decision: write-heavy / time-series / high ingest → LSM; read-heavy with range/point queries → B-tree.

## Q4 (gotcha)
You created an index on `(last_name, first_name)` but a query filtering only on `first_name` is still slow / doing a full scan. Why? And give one more common reason an existing index silently doesn't get used.

**Ideal answer:**
- **Leftmost-prefix rule:** a composite index `(a, b)` only serves queries that use a left prefix — `a`, or `(a, b)` — not `b` alone. `WHERE first_name = ?` can't use a `(last_name, first_name)` index because `last_name` (the leftmost column) isn't constrained.
- A second common reason (any one): (a) **wrapping the column in a function/expression** like `WHERE UPPER(email) = ...` or `col + 0 = ...` makes the query non-sargable, so the plain column index is skipped — need a functional/expression index; or (b) **low selectivity** — on a column where most rows share a value, the planner prefers a seq scan over many random index lookups.

## Q5 (applied)
You're designing the schema for a `users` table with columns `id` (PK), `email`, `is_active` (boolean), and `created_at`. The app does: login by email, "list newest signups" pages ordered by `created_at`, and occasional analytics filtering on `is_active`. Which indexes would you add (or not), and why? Mention covering/clustered if relevant.

**Ideal answer:**
- **`email`:** index it — login does `WHERE email = ?`, high selectivity (unique), exact equality → ideal B-tree (or unique) index; point lookup in a few ms vs full scan.
- **`created_at`:** index it — "list newest" does `ORDER BY created_at DESC` / range pagination; B-tree leaves are sorted + linked, so it serves ordering and range efficiently.
- **`is_active`:** **don't** index it standalone — boolean is **low selectivity** (likely most rows `true`), planner will favor a seq scan; an index here mostly adds write/storage cost.
- **`id`:** already the primary key, which in InnoDB is the **clustered index** (data stored in PK order); one per table.
- Bonus: if a hot query is `SELECT email FROM users WHERE id = ?`, a **covering** index `(id, email)` enables an index-only scan (no table fetch). Note the **write/storage cost** of each extra index — don't over-index a write-heavy table.
