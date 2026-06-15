# PACELC

**Track:** Building Blocks
**Category:** Consistency & Coordination

## What It Is

PACELC theorem CAP ka extension hai jo kehta hai: agar network **P**artition hota hai to system ko **A**vailability aur **C**onsistency mein se choose karna padta hai, lekin **E**lse (jab system normally chal raha hai, no partition) tab bhi ek tradeoff hai — **L**atency vs **C**onsistency ke beech.

## Real-World Analogy

Socho aap ek bank ke do branches chalate ho — ek Mumbai mein, ek Delhi mein — aur dono ki passbook (data) same honi chahiye.

Ab do situations hain. Pehli: Mumbai aur Delhi ke beech ki phone line kat gayi (network **partition**). Ab customer Delhi branch pe paisa nikaalne aaya. Aapke paas do hi choices hain — ya to "sorry, line down hai, abhi service nahi de sakte" bol do (consistency choose ki, par **availability** gayi), ya phir withdrawal allow kar do bina Mumbai se confirm kiye (available rahe, par dono branches ka balance ab mismatch — **consistency** gayi). Yahi CAP wala "PAC" hissa hai.

Doosri situation, jo zyada important hai: phone line **bilkul theek hai**, koi partition nahi. Customer Delhi pe paisa nikaalta hai. Ab bhi sawaal hai — kya har transaction se pehle Delhi branch Mumbai ko call karke "confirm karo balance" pooche (yaani strong **consistency**, par har request mein extra round-trip ki **latency**)? Ya phir Delhi apni local copy se turant paisa de de aur baad mein Mumbai ko sync kar le (fast, low **latency**, par thodi der ke liye stale/eventually-consistent data)? Yahi hai PACELC ka "ELC" hissa — partition na hone par bhi aapko latency aur consistency mein trade karna padta hai. CAP ye normal-operation wala tradeoff miss kar deta hai, PACELC use highlight karta hai.

## How It Works

PACELC ka formula yaad rakhne ka tarika: **if (P) then (A or C), else (L or C)**.

1. **Do alag conditions:** PACELC system ko do states mein dekhता hai. **P** = network partition ho raha hai. **E** (Else) = partition nahi hai, normal steady-state operation chal raha hai. Ek distributed system apni zindagi ka 99%+ time "E" state mein hi spend karta hai — partitions rare events hain. Isiliye ELC wala tradeoff practically zyada relevant hota hai.

2. **Partition branch (PA / PC):** Jab partition hota hai, system ya to **PA** (partition ke time availability prefer kare, requests serve karta rahe, consistency baad mein reconcile) ya **PC** (consistency prefer kare, partition ke dauraan kuch nodes requests reject karein taaki divergent data na bane).

3. **Else branch (EL / EC):** Jab sab normal hai, system ya to **EL** (latency prefer kare — ek replica se hi turant respond kar do, ~1-5 ms local read, baaki replicas ko async update karo) ya **EC** (consistency prefer kare — read/write ko quorum ya sabhi replicas se confirm karao, isme cross-node ya cross-region round-trips add hote hain, jaise same-DC mein ~10-30 ms aur cross-region quorum mein 50-150 ms tak).

4. **System ko classify karna:** Har system ko ek 2-letter combination milta hai partition branch se + 2-letter ELC branch se. Common classifications:
   - **PA/EL** — partition par available, normal par low-latency. Maximally "AP-flavoured." Example: Cassandra, DynamoDB (default tunable settings), Riak.
   - **PC/EC** — partition par consistent, normal par bhi consistent (latency ki keemat pe). Maximally "CP-flavoured." Example: HBase, BigTable, traditional fully-consistent stores, etcd/ZooKeeper (linearizable reads).
   - **PA/EC** aur **PC/EL** — mixed, kam common but exist karte hain.

5. **Tunable knob:** Real systems mein ye choice often per-request configurable hota hai. Jaise Cassandra mein consistency level `ONE` (EL — fast, ek replica) vs `QUORUM`/`ALL` (EC — slow but consistent). To ek hi cluster different requests ke liye alag PACELC behaviour de sakta hai.

## Tradeoffs & Variants

- **L vs C concrete cost:** EL waala system local replica se serve karke ~1-5 ms latency deta hai par stale read ka risk. EC waala system quorum chahta hai — agar replicas 3 regions mein hain to ek quorum write/read 50-150 ms le sakta hai. Interviewer pooch sakta hai "kitni latency add hoti hai EC mein?" — answer: extra network round-trip(s) to other replicas/regions.
- **PACELC ≠ sirf CAP + ek aur letter:** Key insight ye hai ki latency-vs-consistency tradeoff **hamesha** present hai, partition ho ya na ho. CAP sirf failure case dekhta hai; PACELC steady-state ko bhi cover karta hai jo 99% time hota hai.
- **Per-operation tunability:** Modern systems static PA/EL ya PC/EC nahi hain — wo tunable consistency dete hain (Cassandra consistency levels, DynamoDB ki strongly-consistent vs eventually-consistent reads). To "ye system kya hai" ka jawaab often "depends on configured consistency level" hota hai.
- **Default vs configured:** Classification often default config par based hoti hai. DynamoDB default eventually-consistent reads (EL) deta hai, par aap strongly-consistent read flag laga sakte ho (EC, ~2x read cost). Isliye blanket label dene se pehle config samajhna zaroori hai.

## When To Use It

PACELC ek **analysis/vocabulary framework** hai — ise design discussion mein datastore choose karte waqt reasoning ke liye use karo:

- **Datastore selection justify karna:** "Hum Cassandra (PA/EL) le rahe hain kyunki low write latency aur high availability chahiye, aur thodi eventual consistency acceptable hai (e.g., social feed, activity log)."
- **Strong consistency wale use cases:** Financial ledgers, inventory counts, locking/coordination — yahan PC/EC systems (Spanner with TrueTime, etcd, ZooKeeper, HBase) justify karo, latency ki keemat acceptable hai kyunki correctness paramount hai.
- **Real systems vocabulary:** Cassandra/DynamoDB/Riak = PA/EL. HBase/BigTable = PC/EC. Google Spanner = PC/EC (TrueTime se external consistency, geo-replicated commit latency accept karta hai). MongoDB = configurable, default majority-write leaning PC/EC-ish but tunable. Ye naam interview mein bolne se aapki depth dikhti hai.
- **Tradeoff articulate karna:** Jab interviewer "consistency ya availability?" pooche, PACELC use karke better answer do — "partition par main X chununga, aur normal operation par main latency ke liye Y trade karunga."

## Common Interview Gotchas

- **"PACELC sirf CAP ka rename hai" — galat:** Sabse bada misconception. CAP sirf partition (failure) scenario address karta hai. PACELC ka asli contribution **ELC** hai — wo batata hai ki bina kisi failure ke, normal din mein bhi, har distributed datastore latency aur consistency ke beech choose kar raha hai. Ye distinction bolna interviewer ko impress karta hai.

- **CAP ka "CA" wala confusion:** Log sochte hain ek system "CA" (partition tolerance chhod do) ho sakta hai. Distributed system mein network partitions inevitable hain — aap P ko opt-out nahi kar sakte. PACELC isiliye "P" ko ek **condition** maanta hai (jab hota hai), na ki ek choice. Aap partition hone par PA ya PC chunte ho, "no partition tolerance" koi real option nahi hai.

- **EL ka matlab "no consistency" nahi:** EL latency prefer karta hai, par iska matlab data corrupt nahi — usually eventual consistency hoti hai (replicas aakhir mein converge ho jaate hain). EL = "abhi fast respond, sync baad mein," not "consistency bilkul nahi."

- **Classification absolute samajhna:** "Cassandra PA/EL hai" bolna theek hai default ke liye, par actual behaviour consistency level config par depend karta hai (ONE vs QUORUM vs ALL). Tunable systems ek single fixed label mein fit nahi hote — ye nuance batao.

- **Latency aur consistency ka relationship galat batana:** Strong consistency ke liye aapko zyada replicas se confirm karwana padta hai (quorum/all), jisme network round-trips add hote hain → higher latency. Ye tradeoff fundamental hai (speed-of-light limit cross-region). Kabhi mat bolo "strong consistency bhi fast ho sakti hai bina cost ke."

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/consistency-coordination/conceptual_quiz_pacelc.md`](../../../sysd-quizzes/consistency-coordination/conceptual_quiz_pacelc.md) — `sysd-buddy quiz scaffold pacelc` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update pacelc --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — PACELC decision tree (if P → A/C, else → L/C) aur common datastores ki classification ka interactive diagram.
