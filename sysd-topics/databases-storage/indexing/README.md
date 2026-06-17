# Indexing

**Track:** Building Blocks
**Category:** Databases & Storage

## What It Is

Database index ek auxiliary data structure (usually B-tree ya hash) hota hai jo ek table ki specific column(s) pe lookups ko full-table scan se bachakar logarithmic ya constant time mein point/range queries serve karne deta hai, kuch extra storage aur slower writes ke cost pe.

## Real-World Analogy

Socho ek 1000-page textbook hai aur tumhe "consistent hashing" word dhoondhna hai. Ek tareeka: page 1 se shuru karo aur har page padhte jao jab tak word na mil jaaye — ye **full-table scan** hai, O(n), worst case poori book.

Doosra tareeka: book ke end mein jo **index** hota hai usko kholo. Wahan saare important words **alphabetically sorted** hain, aur har word ke saamne page numbers likhe hain. Tum "consistent hashing" ko sorted list mein turant locate kar lete ho (kyunki sorted hai, binary-search jaisa jump kar sakte ho), aur seedha page 814 pe chale jaate ho. Ye **index lookup** hai.

Do baatein yahan notice karo. Pehli: index khud extra paper (storage) leta hai — book thodi moti ho jaati hai. Doosri: agar publisher book mein ek naya paragraph add kare, to usse content page to update karna hi padega, plus **index bhi re-update** karna padega taaki page numbers sahi rahein — yaani har edit ab thoda mehenga ho gaya. Bilkul yahi tradeoff database index ka hai: fast reads, lekin extra space aur slower writes.

## How It Works

1. **Bina index ke baseline:** `SELECT * FROM users WHERE email = 'a@b.com'` agar `email` pe koi index nahi hai, to DB ko **full table scan** karna padta hai — har row check karo. 10 million rows pe ye sequential disk reads ka ek bada chunk hai, easily 100s of ms se seconds tak.

2. **B-tree index (the default):** Most relational DBs (Postgres, MySQL/InnoDB) by default ek **B+ tree** banate hain index column pe. Ye ek balanced tree hai jisme keys **sorted** rehti hain, har node mein kai keys hoti hain (high fan-out, jaise 100s of keys per node), to tree **shallow** rehta hai — 10 million rows ko bhi typically ~3-4 levels mein cover kar leta hai. Lookup `O(log n)`: root se shuru karo, sahi child pointer follow karo, leaf tak pahuncho. 3-4 node reads, har ek page cache ya ek disk seek — total kuch hi ms.

3. **Leaf level aur range scans:** B+ tree mein actual data pointers (ya clustered index mein data khud) sirf **leaf nodes** pe hote hain, aur leaves ek **linked list** ki tarah sorted order mein chained hote hain. Isi wajah se `WHERE age BETWEEN 25 AND 30` jaisi **range query** efficient hai: start key dhoondho, phir leaves ke through sequentially scan karte jao jab tak range khatam na ho. Sorted order `ORDER BY` aur range dono ko free deta hai.

4. **Hash index:** Kuch engines hash index support karte hain — column ko hash karke ek bucket pe map karte hain. Equality lookup (`WHERE id = 42`) ke liye ye `O(1)` average, B-tree se bhi fast. **Lekin** hash index range ya sorting support nahi karta (hashing order ko destroy kar deti hai), isliye `BETWEEN`, `<`, `ORDER BY` pe useless hai.

5. **Clustered vs secondary index:** **Clustered index** table ki rows ko physically index key ke order mein store karta hai — to leaf hi actual row data hota hai (InnoDB primary key clustered hota hai). Ek table mein sirf **ek** clustered index ho sakta hai. **Secondary (non-clustered) index** alag structure hota hai jiske leaf mein key + ek pointer (primary key ya row-id) hota hai; row fetch karne ke liye ek **extra lookup** (back to clustered index) lagta hai.

6. **Composite index aur covering index:** Index ek se zyada columns pe ho sakta hai, jaise `(last_name, first_name)` — ye **leftmost-prefix** order mein kaam karta hai. Agar query ko zaroori saare columns index mein hi mil jaayein (`SELECT email FROM users WHERE id = 5` aur index `(id, email)` hai), to DB ko table touch karne ki zaroorat hi nahi — ye **covering index** / index-only scan hai, fastest.

7. **Write cost:** Har `INSERT`/`UPDATE`/`DELETE` ko table ke saath-saath **har affected index** ko bhi maintain karna padta hai (tree mein sahi jagah insert, possibly node splits). Isiliye 5 indexes wali table pe writes ek index wali se kaafi slower hoti hain.

## Tradeoffs & Variants

- **Read speed vs write speed vs storage:** Index reads ko `O(n)` → `O(log n)` karta hai, lekin har index extra disk space leta hai aur har write ko slower karta hai (sab indexes update hone chahiye). Interviewer yahi probe karta hai: "kya hum har column pe index laga dein?" — nahi, write-heavy tables pe over-indexing throughput kill kar deta hai.

- **B-tree vs hash:** B-tree general-purpose (equality + range + sort), thoda slower equality. Hash sirf equality, par tez. Interview mein "kab hash index?" ka answer: pure point-lookup workload jahan range/order ki zaroorat hi nahi.

- **B-tree vs LSM-tree:** B-tree **read-optimized**, in-place updates karta hai (random writes). **LSM-tree** (Log-Structured Merge tree — Cassandra, RocksDB, LevelDB, ScyllaDB) **write-optimized**: writes ko ek in-memory memtable + append-only sequential disk segments (SSTables) mein batch karta hai, phir background mein compaction. Sequential writes hone se write throughput bahut high, lekin reads ko kai SSTables check karne pad sakte hain (Bloom filters isko mitigate karte hain). Decision: write-heavy / time-series → LSM; read-heavy OLTP → B-tree.

- **Clustered vs secondary:** Clustered index range scans aur primary-key lookups ko super fast karta hai (data leaf pe hi hai), par sirf ek per table aur inserts ko sahi physical position pe rakhna padta hai. Secondary indexes flexible hain par ek extra pointer-chase add karte hain — unless covering.

- **Composite column order matters:** `(a, b)` index `WHERE a = ?` aur `WHERE a = ? AND b = ?` ke liye kaam karta hai, par akele `WHERE b = ?` ke liye nahi (leftmost-prefix rule). Galat order = useless index.

- **Specialized indexes:** Range/sort ke liye B-tree; full-text search ke liye inverted index; geospatial ke liye R-tree / GiST; JSON/array membership ke liye GIN (Postgres).

## When To Use It

- **High-selectivity filter/lookup columns:** Jin columns pe tum `WHERE`, `JOIN`, ya foreign-key lookups karte ho aur jo bahut distinct values rakhte hain (jaise `email`, `user_id`) — wahan index high payoff deta hai.
- **Range queries aur sorting:** `ORDER BY created_at`, `WHERE price BETWEEN ...` — B-tree index in queries ko sorted leaf chain se serve karta hai.
- **Real systems:** Postgres aur MySQL/InnoDB default B+ tree indexes use karte hain; **Cassandra/ScyllaDB/RocksDB/LevelDB** LSM-tree storage pe bane hain; **Elasticsearch/Lucene** full-text ke liye **inverted index** use karta hai; **MongoDB** B-tree indexes deta hai.
- **Avoid indexing when:** Bahut low-selectivity columns (jaise `boolean is_active` jahan 90% rows ek hi value) — planner waise bhi seq scan choose kar sakta hai; ya bahut write-heavy tables jahan har extra index throughput ko hurt karta hai.

## Common Interview Gotchas

- **"Index har query ko fast karta hai" — galat:** Index sirf un queries ko help karta hai jo us column ko `WHERE`/`JOIN`/`ORDER BY` mein use karein, aur jahan **selectivity high** ho. Low-selectivity column (e.g. gender) pe index ko query planner ignore kar dega kyunki seq scan saste padta hai — random index lookups bahut saari rows ke liye sequential scan se mehenge ho jaate hain.

- **Leftmost-prefix rule bhula dena:** `(a, b, c)` composite index `WHERE b = ?` ya `WHERE c = ?` (bina `a` ke) ke liye use **nahi** hota. Sirf prefixes — `a`, `(a,b)`, `(a,b,c)` — kaam karte hain. Bahut log assume kar lete hain ki composite index har contained column pe kaam karega.

- **Function/expression query index ko maar deta hai:** `WHERE UPPER(email) = 'X'` ya `WHERE col + 0 = 5` mein plain `email` index use nahi hoga, kyunki column wrap ho gaya — DB ko har row pe function evaluate karna padta hai. Fix: expression/functional index banao ya query ko sargable rakho.

- **Hash index pe range maang lena:** Hash index `WHERE id = 5` pe great hai par `WHERE id > 5` ya `ORDER BY id` pe bilkul bekaar — hashing sorted order destroy kar deti hai. Interview mein ye distinction asking points hai.

- **Over-indexing write cost ko ignore karna:** "Saare columns pe index laga do" wrong hai — har index ko har insert/update pe maintain karna padta hai, plus storage. Write-heavy systems mein ye throughput aur latency dono ko hurt karta hai.

- **B-tree vs LSM ulta bolna:** Yaad rakho — **B-tree read-optimized**, **LSM-tree write-optimized**. LSM sequential append + compaction se writes tez karta hai; reads ke liye multiple SSTables + Bloom filters. Ye interview mein commonly swap kar diya jaata hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/databases-storage/conceptual_quiz_indexing.md`](../../../sysd-quizzes/databases-storage/conceptual_quiz_indexing.md) — `sysd-buddy quiz scaffold indexing` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update indexing --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — B+ tree structure, leaf-level linked list, aur index lookup vs full-table scan ka interactive diagram.
