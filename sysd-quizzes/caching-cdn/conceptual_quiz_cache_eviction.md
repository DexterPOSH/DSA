# Cache Eviction (LRU/LFU) — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update cache-eviction --quiz-score N/M` -->

## Q1 (warm-up)
Cache eviction kya hai, aur LRU vs LFU mein basic farak kya hai?

**Ideal answer:**
- Eviction = jab bounded/fixed-size cache full ho jaye, nayi entry ke liye jagah banane ke liye kisi purani entry ko hatana.
- LRU = **Least Recently Used** evict karta hai — recency (last access time) ke basis pe.
- LFU = **Least Frequently Used** evict karta hai — frequency (total access count) ke basis pe.
- Goal: cache hit ratio maximize karna taaki slow origin/DB hits (cache miss) minimize hon.

## Q2 (core)
LRU cache ko O(1) get aur put ke saath kaise implement karoge? Kaun se data structures aur kyun?

**Ideal answer:**
- Do structures: **hash map** (key → node) + **doubly linked list** (recency order).
- Hash map: key se node ka O(1) lookup.
- Doubly linked list: most-recently-used head pe, least-recently-used tail pe; node ko O(1) mein detach + re-insert kar sakte hain (prev/next pointers).
- **Get/hit:** node ko head pe move karo (mark most-recent).
- **Put/miss:** head pe insert; agar size > capacity, **tail** node evict karo aur hash map se uski key delete karo.
- Doubly (na ki singly) linked list isliye, kyunki arbitrary node ko O(1) mein detach karne ke liye prev pointer chahiye.

## Q3 (tradeoff)
LRU aur LFU mein se kab kaunsa behtar hai? Har ek ka weak point kya hai?

**Ideal answer:**
- **LRU** temporal locality acchi pakadta hai, par ek **scan/flood** (bada one-time sequential read, jaise full table scan) usko pollute kar deta hai — hot entries tail pe push hoke evict ho jaati hain.
- **LFU** scan-resistant hai (one-time reads ka count 1 rehta hai, evict ho jaate hain), par **stale/aging problem** hai — purani once-popular entry high count ki wajah se atak jaati hai chahe ab koi use na kare.
- LFU ka fix: **frequency decay/aging** ya **(W-)TinyLFU**.
- LFU thoda zyada memory (per-key counters + buckets) leta hai LRU se.
- Workload-dependent: shifting popularity → LRU adapt better; stable popularity + scans → LFU better.

## Q4 (gotcha)
Kya Redis exact LRU implement karta hai? Aur naive LFU O(1) hota hai kya?

**Ideal answer:**
- **Nahi**, Redis by default **approximate / sampled** LRU (aur LFU) karta hai — exact recency order maintain karna har key ke liye metadata + reordering maangta hai jo mehenga hai.
- Redis randomly **N keys sample** karta hai (`maxmemory-samples`, default ~5) aur unme se best victim evict karta hai; sample badhao to accuracy badhti hai par CPU cost bhi.
- **Naive LFU O(1) nahi hai** — lowest-count dhoondhna O(N) scan hai. O(1) LFU ke liye **frequency buckets (per-frequency doubly linked list) + minFreq pointer** chahiye; access pe entry ko freq→freq+1 bucket mein shift karo.
- Bonus: Linux page cache CLOCK/second-chance (reference bit) se LRU approximate karta hai.

## Q5 (applied)
Tum ek hot-key product catalog cache design kar rahe ho jahan kuch items extremely popular hain, par roz ek bada batch job poore catalog ko scan karta hai. Kaunsi eviction policy choose karoge aur kyun? Kahan deploy karoge?

**Ideal answer:**
- Pure LRU **bura** rahega kyunki daily full-catalog scan saari hot items ko evict kar dega (cache pollution).
- **LFU ya (W-)TinyLFU** behtar — scan ke one-time reads low frequency rakhte hain, popular items high frequency ki wajah se retained rehte hain (scan-resistant).
- Frequency **aging/decay** add karo taaki popularity shift hone pe purani entries gradually flush hon.
- Implementation choices: **Redis `allkeys-lfu`** with appropriate `maxmemory`, ya app-level **Caffeine (W-TinyLFU)** with admission control.
- Bonus signals: per-item **TTL** for freshness, hot-key handling, aur cache stampede protection (request coalescing) — eviction se separate concern.
