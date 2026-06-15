# Distributed Locks

**Track:** Building Blocks
**Category:** Consistency & Coordination

## What It Is

Distributed lock ek coordination mechanism hai jisse multiple processes (alag-alag machines pe chal rahe) ek shared resource ya critical section ko ek time pe sirf ek hi process ke through access karne dete hain — mutual exclusion across a network.

## Real-World Analogy

Socho ek bade office mein ek hi conference room hai aur uske bahar ek single physical key reception pe rakhi hai. Jis bhi team ko meeting karni hai, usko pehle reception jaake key leni padti hai. Jab tak ek team ke paas key hai, baaki sab teams wait karti hain — chahe wo kitni bhi powerful ya senior ho. Meeting khatam, key wapas reception pe — ab agli team le sakti hai.

Ab twist: agar key lene wali team meeting ke beech mein hi building chhod ke chali jaaye (process crash) aur key apni jeb mein leke chali jaaye, to room hamesha ke liye block ho jaayega — koi aur kabhi use nahi kar paayega (deadlock). Isiliye real distributed locks mein har key pe ek **time limit (lease / TTL)** lagaya jaata hai: "ye key max 30 second ke liye valid hai, uske baad apne aap reception pe wapas aa jaayegi." Yahi lease-based locking ka core idea hai — crash hone par bhi system khud-ba-khud recover ho jaata hai.

## How It Works

1. **Acquire (lock lena):** Client lock manager ko bolta hai "mujhe key `order:123` chahiye." Ye operation atomic hona chahiye — typical implementation Redis mein `SET order:123 <random-token> NX PX 30000` hai. `NX` = sirf tabhi set karo jab key exist na karti ho (yani lock free ho), `PX 30000` = 30000 ms (30s) ka TTL. Agar `SET` success return karta hai, lock mil gaya; nahi to kisi aur ke paas hai.

2. **Unique fencing token / owner ID:** Lock ke saath ek unique random value (jaise UUID) store hota hai jo sirf is client ko pata hai. Ye critical hai release ke time — taaki client galti se kisi aur ka lock na release kar de.

3. **Critical section:** Lock milne ke baad client apna kaam karta hai (jaise inventory decrement, payment process) — ye guaranteed single-writer window hai (theory mein).

4. **Release (lock chhodna):** Client lock delete karta hai, par sirf tab jab token match kare. Ye check-and-delete atomic hona chahiye, isliye Redis mein ek Lua script use hota hai: `if redis.call("get", KEYS[1]) == ARGV[1] then return redis.call("del", KEYS[1]) end`. Plain `GET` phir `DEL` race condition kholta hai.

5. **Lease expiry (safety net):** Agar client crash kar gaya release se pehle, to TTL (30s) ke baad lock apne aap expire ho jaata hai aur agla client le sakta hai. Bina TTL ke ek crashed client poore system ko permanently block kar deta. Tradeoff: TTL bahut chhota (jaise 1s) rakha to slow client ka lock beech mein expire ho sakta hai; bahut bada (jaise 5 min) rakha to crash ke baad recovery slow hoti hai.

6. **Renewal / lease extension:** Agar kaam TTL se zyada lag sakta hai, client ek background "watchdog" thread chalata hai jo periodically (jaise har 10s pe, jab TTL 30s ho) lock ko extend karta hai — taaki kaam ke beech mein lease expire na ho.

Latency intuition: ek single Redis lock acquire round-trip typically sub-millisecond se ~1-2 ms (same datacenter) hota hai, to high-throughput services aasani se hazaaron lock ops/sec kar sakti hain. ZooKeeper/etcd based locks consensus (quorum write) ki wajah se thoda heavy hote hain — typically single-digit to low double-digit ms per acquire.

## Tradeoffs & Variants

- **Redis (single instance) vs Redlock (multi-instance):** Single Redis node simple aur fast hai, par wo ek single point of failure hai — agar wo node fail ho aur replica abhi tak lock replicate na hua ho, to do clients ek saath lock le sakte hain. Redlock algorithm N (jaise 5) independent Redis nodes pe lock leta hai aur majority (3/5) milne par lock granted maanta hai. Ye availability badhata hai par complex hai aur Martin Kleppmann ne famously argue kiya ki ye GC pause / clock skew ke under bhi correctness guarantee nahi deta.

- **CP store (ZooKeeper / etcd) vs AP store (Redis):** ZooKeeper aur etcd consensus (ZAB / Raft) pe bante hain — ye linearizable, fault-tolerant locks dete hain (ephemeral znodes / lease keys), correctness ke liye behtar. Cost: zyada latency aur operational complexity. Redis fast hai par by default correctness over availability nahi chunta. Rule of thumb: **agar lock galat hone par data corruption ho (money, inventory) → CP store; agar lock sirf efficiency optimization hai (do logo ka same kaam do baar na ho) → Redis fine.**

- **Fencing tokens:** Sabse bada correctness lever. Lock manager har lock grant ke saath ek monotonically increasing number (fencing token) deta hai. Client jab shared resource (DB / storage) ko likhe, to wo token bhejta hai, aur resource purane (chhote) token wali writes ko reject kar deta hai. Ye GC pause / network delay wali "two clients think they hold the lock" problem ko safely handle karta hai — bina iske koi bhi lease-based lock theoretically unsafe hai.

- **TTL tuning:** Chhota TTL = fast crash recovery par false expiry ka risk; bada TTL = slow recovery. Watchdog renewal isko mitigate karta hai par complexity add karta hai.

- **Lock granularity:** Coarse lock (ek bada lock for poora resource) simple par low concurrency; fine-grained locks (per-key) zyada throughput par deadlock / overhead risk.

## When To Use It

- **Leader election:** Sirf ek instance ko ek scheduled job / cron chalana hai across a fleet — lock holder hi leader. (etcd/ZooKeeper iske liye classic choice — Kubernetes leader election etcd lease pe based hai.)
- **Preventing duplicate work:** Ek webhook / message do baar deliver ho jaye, to lock se sirf ek hi process usko handle kare.
- **Guarding a non-transactional resource:** Jab shared resource (external API, file in object storage, legacy system) khud transactions support nahi karta, to upar se mutual exclusion enforce karna.
- **Real systems:** Redis Redisson library (Java) distributed locks widely use hote hain; Google Chubby (ZooKeeper ka inspiration) GFS/Bigtable mein leader election ke liye; HashiCorp Consul/etcd session-based locks; Kubernetes `Lease` objects.
- **Important guidance:** Agar aapka shared resource ek database hai jo transactions support karta hai, to aksar DB ka apna row-level lock ya optimistic concurrency (version column) zyada simple aur safe hota hai — distributed lock tabhi reach karo jab coordination DB ke bahar chahiye.

## Common Interview Gotchas

- **"Redlock se safety guaranteed hai" — NO:** Ek client jo lock hold kar raha hai, agar uska process ek long GC pause (jaise 10s) ya network delay mein chala jaaye, to lease expire ho sakti hai aur dusra client wahi lock le leta hai — ab DO clients ek saath khud ko lock holder maante hain. Lease-based lock akele isse nahi rok sakta. Iska sahi fix **fencing tokens** hai, na ki zyada Redis nodes.

- **`GET` phir `DEL` race:** Naive release — pehle check karo "kya lock mera hai?" phir delete — beech me lock expire hokar kisi aur ko mil sakta hai, aur aap uska lock delete kar doge. Release hamesha **atomic compare-and-delete** (Lua script / transaction) hona chahiye, token match ke saath.

- **TTL bhool jaana:** Bina TTL ke agar lock holder crash kar gaya, lock hamesha ke liye held reh jaata hai → permanent deadlock. Har distributed lock ka lease/TTL hona MUST hai.

- **Clock skew assumption:** Redlock jaise algorithms machines ke clocks pe depend karte hain. Agar ek node ka clock jump kar jaye (NTP correction, VM pause), to lock expiry timing galat ho sakti hai. Robust designs ko clock pe correctness ke liye rely nahi karna chahiye.

- **Lock != transaction:** Distributed lock atomicity ya durability nahi deta — wo sirf mutual exclusion deta hai. Agar aapko all-or-nothing chahiye to wo alag concern hai.

- **Single Redis node SPOF:** Interview mein agar aap "Redis lock" bolo, interviewer poochega "agar Redis fail ho gaya to?" — answer: replication async hone se ek tiny window mein do holders possible; isiliye correctness-critical cases mein CP store ya fencing tokens.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/consistency-coordination/conceptual_quiz_distributed_locks.md`](../../../sysd-quizzes/consistency-coordination/conceptual_quiz_distributed_locks.md) — `sysd-buddy quiz scaffold distributed-locks` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update distributed-locks --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — lock acquire/release flow, lease expiry, aur fencing token sequence ka interactive diagram.
