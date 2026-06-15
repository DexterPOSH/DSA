# B-Tree vs LSM-Tree

**Track:** Building Blocks
**Category:** Databases & Storage

## What It Is

B-Tree aur LSM-Tree do alag on-disk storage engine designs hain — B-Tree data ko sorted, in-place updatable pages mein rakhta hai (read-optimized), jabki LSM-Tree (Log-Structured Merge-Tree) writes ko pehle memory mein buffer karke sequentially disk pe flush karta hai aur baad mein background compaction se merge karta hai (write-optimized).

## Real-World Analogy

Socho aapke paas ek classroom register hai jisme students alphabetically sorted hone chahiye.

**B-Tree wala approach:** Aap ek hi proper register rakhte ho jisme har page pe naam sorted hain. Jab naya student "Karan" admission leta hai, aap us page pe jaate ho jahan "Ka..." aana chahiye aur usse wahin physically insert kar dete ho. Agar page bhar gaya to page ko do hisson mein split karte ho. Lookup super fast hai — kisi bhi naam ko alphabetically index follow karke seedha dhoondh lo. Lekin har insert mein aapko sahi jagah dhoondh kar wahin likhna padta hai (random write), aur kabhi-kabhi page split ka extra kaam.

**LSM-Tree wala approach:** Aap register pe seedha nahi likhte. Aapke paas desk pe ek chhoti notebook (memory buffer) hai — naya student aaya, bas usme jaldi se likh do, no sorting tension. Notebook bhar gayi to use ek baar mein sorted karke ek nayi clean sheet (immutable file) bana ke pile pe rakh do, aur fresh notebook le lo. Writing bohot fast hai kyunki aap hamesha aage badh rahe ho, kabhi peeche jaa ke kisi page ko edit nahi karte. **Catch:** ab "Karan" ko dhoondhne ke liye pehle desk notebook dekho, fir pile ki har sheet (newest se oldest) check karo — kyunki "Karan" ki latest entry kisi bhi sheet pe ho sakti hai. Isliye background mein ek peon (compaction) baar-baar in sheets ko merge karke duplicates hata ke bade sorted bundles banata rehta hai, taaki reads slow na hon.

Bas yahi core difference hai: B-Tree "likhte waqt mehnat" (write effort) karta hai, LSM-Tree "padhte waqt mehnat" (read effort) plus background cleanup.

## How It Works

### B-Tree

1. **Structure:** Ek balanced tree of fixed-size **pages** (typically `4 KB` or `8 KB` — Postgres default `8 KB`, MySQL InnoDB `16 KB`). Har page mein sorted keys hote hain plus child pointers. Tree ka branching factor (fan-out) bohot high hota hai (sometimes few hundred keys per page), isliye tree shallow rehta hai.

2. **Lookup:** Root page se start karo, binary-search within page, sahi child pointer follow karo, neeche descend karo. Ek typical large DB me `2^32` keys ko sirf **3-4 levels** mein store kiya ja sakta hai — yaani ek key dhoondhne ke liye max ~4 page reads. SSD pe ye sub-millisecond, disk-cache hit ho to microseconds.

3. **Write (update/insert):** Sahi leaf page dhoondho, usme value ko **in-place** update/insert karo. Page full ho gaya to **page split** — page ko do mein todo aur parent mein ek key promote karo. Ye split kabhi-kabhi upar tak propagate hota hai.

4. **Durability — WAL:** In-place writes risky hain (crash mid-write = corrupt page). Isliye har change pehle **Write-Ahead Log (WAL/redo log)** mein append hota hai, fir actual page modify hota hai. Crash hone pe WAL replay karke consistency restore hoti hai. Matlab ek logical write effectively do disk writes ban sakta hai (WAL + page).

5. **Random I/O nature:** Page jahan belong karta hai wahin likhna padta hai → **random writes** disk pe. SSD pe theek hai, par spinning disk pe ye slow tha (yahi LSM ki original motivation thi).

### LSM-Tree

1. **Memtable:** Saare writes pehle ek in-memory sorted structure (jaise a balanced tree / skip list) mein jaate hain — yahi **memtable**. Write super fast (`O(log n)` in RAM, microseconds). Crash safety ke liye write pehle ek on-disk **WAL** mein bhi append hota hai.

2. **Flush → SSTables:** Memtable ek size threshold (jaise few MB to tens of MB) cross kare to use **immutable** sorted file ke roop mein disk pe **sequentially** likh dete hain — ise **SSTable (Sorted String Table)** kehte hain. Sequential write hone ki wajah se ye throughput bohot high hota hai. Naya empty memtable start ho jaata hai.

3. **Reads:** Ek key dhoondhne ke liye: pehle memtable check karo, fir newest SSTable se oldest tak. Worst case, key kisi bhi level pe ho sakti hai. Isko fast karne ke liye:
   - **Bloom filters:** Har SSTable ke saath ek probabilistic filter jo bina disk read kiye bata deta hai "ye key is file mein definitely nahi hai" (no false negatives). Isse non-existent / missing-level reads almost free ho jaate hain.
   - **Sparse index + block cache:** SSTable ke andar sorted blocks aur ek in-memory sparse index se seedha relevant block tak jump.

4. **Compaction:** Background process jo multiple SSTables ko merge-sort karke naye, bigger, de-duplicated SSTables banata hai. Yahi purani/overwritten values aur tombstones (deletes) ko physically hatata hai. Do common strategies:
   - **Leveled compaction (RocksDB/LevelDB default-ish):** SSTables ko levels `L0, L1, L2...` mein organize karo, har level pehle se ~10x bada. Read amplification kam (ek key per level mostly ek hi file mein), par write amplification zyada.
   - **Size-tiered compaction (Cassandra default):** Similar-size SSTables ko ek saath merge karo. Write amplification kam, par read amplification zyada (ek key kai overlapping files mein ho sakti hai).

5. **Deletes — tombstones:** LSM immutable files ko edit nahi kar sakta, isliye delete ek special **tombstone** marker likhta hai. Actual data tab tak rehta hai jab tak compaction use clean na kare.

### The three "amplifications" (sabse important framing)

- **Write amplification:** 1 logical write multiple physical writes banta hai. B-Tree me WAL + in-place page (+ splits). LSM me WAL + initial flush + har compaction pass me dobara rewrite. LSM ki write amplification often higher hoti hai, par writes **sequential** hote hain.
- **Read amplification:** 1 logical read multiple physical reads. B-Tree me bounded (~tree height, 3-4 reads). LSM me potentially multiple SSTables (Bloom filters isse kaafi tame karte hain).
- **Space amplification:** Disk pe actual logical data se zyada storage. B-Tree me page fragmentation / half-empty pages. LSM me purani overwritten values + tombstones jab tak compaction na chale.

## Tradeoffs & Variants

- **Write-heavy vs Read-heavy:** Yahi central decision. Write-heavy / high-ingest workload (time-series, event logs, metrics, messaging) → **LSM** (sequential writes, high throughput). Read-heavy / point-lookup + range scan with latency predictability → **B-Tree** (bounded read amplification).

- **Sequential vs Random writes:** LSM writes sequential hote hain — ye spinning disks pe huge tha aur SSDs pe bhi friendly (kam write-induced wear, kam random IOPS). B-Tree random writes karta hai.

- **Read/space amplification ka cost:** LSM ki low write cost free nahi — aap read amplification (multiple SSTables) aur space amplification (un-compacted duplicates) mein pay karte ho, plus background compaction CPU/IO consume karta hai jo **read/write latency spikes** de sakta hai (compaction stalls).

- **Latency predictability:** B-Tree ki tail latency zyada predictable hoti hai (fixed tree height). LSM mein compaction kicks in hone pe p99/p999 latency spike kar sakti hai — ye production tuning ka bada topic hai.

- **Compaction strategy variant:** Leveled (low read amp, high write amp) vs Size-tiered (low write amp, high read amp). RocksDB ye dono offer karta hai; choice workload pe depend karti hai.

- **Concurrency / locking:** B-Tree updates ko page-level latches/locks chahiye (in-place mutation). LSM ke immutable SSTables lock-free reads enable karte hain (no reader-writer contention on files), MVCC-friendly.

## When To Use It

**B-Tree chuno jab:**
- Read-heavy ya balanced OLTP workload ho, predictable low read latency chahiye.
- Strong range scans + point lookups dono chahiye with stable performance.
- Real systems: **PostgreSQL, MySQL/InnoDB, Oracle, SQL Server, MongoDB (WiredTiger B-Tree mode), SQLite, lmdb.** Most traditional relational DBs default B-Tree pe hain.

**LSM-Tree chuno jab:**
- Write-heavy / high-ingest workload — time-series, logs, metrics, IoT, messaging, write-amplified analytics ingestion.
- Sequential write throughput aur write cost prioritize karna ho, read latency thoda variable chal jaaye.
- Real systems: **Cassandra, RocksDB, LevelDB, ScyllaDB, HBase, Bigtable, InfluxDB, CockroachDB (RocksDB/Pebble pe), TiDB, MongoDB (WiredTiger LSM option).**

**Interview pattern recognition:** "We ingest millions of events/sec" ya "append-heavy time-series" sune to LSM bolo. "OLTP, low-latency reads, frequent updates with range queries" sune to B-Tree. Hamesha amplification trade-offs ke saath justify karo, just naam mat lo.

## Common Interview Gotchas

- **"LSM is always faster" — galat:** LSM sirf **write** path optimize karta hai. Reads (especially without good Bloom filters / on missing keys) multiple SSTables hit kar sakte hain. B-Tree reads bounded aur often faster hote hain. Blanket "LSM faster" bolna red flag hai.

- **"B-Tree writes random, LSM writes sequential" — yahi asli core insight:** Bohot log ye miss kar dete hain. B-Tree ko data wahin likhna padta hai jahan wo sorted-order me belong karta hai (random I/O). LSM hamesha aage append karta hai (sequential I/O) aur sorting baad mein compaction se hoti hai. Ye HDD pe game-changer tha aur SSD pe bhi wear/IOPS friendly hai.

- **Write amplification ko backwards samajhna:** Counter-intuitively, LSM ki **write amplification often B-Tree se zyada** hoti hai (compaction baar-baar data rewrite karta hai). LSM ka fayda raw write amplification kam hona nahi hai — fayda ye hai ki writes **sequential aur batched** hote hain, jisse effective throughput high aur latency low rehti hai. Interviewer specifically ye nuance probe karta hai.

- **Bloom filters ka role:** Agar koi LSM reads explain kare bina Bloom filters mention kiye, to wo aadhi picture hai. Bloom filters hi LSM ke read amplification ko practical banate hain — non-existent keys aur wrong SSTables ko skip karke. (No false negatives, small false-positive rate.)

- **Deletes free nahi hain (tombstones):** LSM me delete actually ek write hai (tombstone). Data turant nahi jaata; space tab tak occupied jab tak compaction na chale. High-churn / TTL-heavy workloads me tombstone buildup reads ko slow kar sakta hai (Cassandra ka classic "tombstone hell").

- **Compaction = hidden cost:** Log compaction ko "free background magic" maan lete hain. Reality: ye CPU + disk IO consume karta hai aur foreground read/write latency pe spikes (p99/p999) daal sakta hai. Production me ye tuning ka major axis hai.

- **WAL dono me hota hai:** Common misconception ki WAL sirf ek design ka feature hai. Durability ke liye **dono** B-Tree aur LSM WAL/commit-log use karte hain — yeh distinguishing factor nahi hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/databases-storage/conceptual_quiz_btree_vs_lsm.md`](../../../sysd-quizzes/databases-storage/conceptual_quiz_btree_vs_lsm.md) — `sysd-buddy quiz scaffold btree-vs-lsm` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update btree-vs-lsm --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — B-Tree page structure vs LSM memtable→SSTable→compaction flow ka side-by-side interactive diagram.
