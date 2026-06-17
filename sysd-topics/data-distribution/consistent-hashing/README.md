# Consistent Hashing

**Track:** Building Blocks
**Category:** Data Distribution

## What It Is

Consistent hashing ek aisi technique hai jisme keys aur nodes dono ko ek circular hash space (the "ring") pe map kiya jaata hai, taaki jab koi node add ya remove ho to sirf ~K/N keys hi remap hon, almost saari nahi.

## Real-World Analogy

Socho ek round dining table hai jiske around clockwise positions pe kuch waiters (nodes) khade hain. Har dish (key) table pe ek fixed spot pe rakhi jaati hai, aur usko serve karne ki zimmedaari us waiter ki hoti hai jo clockwise direction mein us dish ke just baad khada hai — yaani "next waiter clockwise."

Ab agar ek waiter chala jaata hai (node removed), to sirf uske saamne wali dishes ko handle karne ki responsibility uske clockwise wale next waiter ko shift hoti hai. Baaki poore table ko rearrange nahi karna padta. Aur agar naya waiter aata hai (node added), to wo bas apni position pe khada ho jaata hai aur usse just pehle wali kuch hi dishes uske paas aa jaati hain — table ka baaki sab kuch waisa ka waisa rehta hai. Yahi consistent hashing ka core kamaal hai: change ka blast radius chhota rehta hai.

## How It Works

1. **The ring:** Ek hash function (jaise MD5/SHA, ya MurmurHash) ka output space ek bade range ka hota hai, jaise `0` se `2^32 - 1`. Is range ko hum ek circle maan lete hain — `2^32 - 1` ke baad wapas `0` aa jaata hai. Yahi hamara hash ring hai.

2. **Nodes ki placement:** Har node (server) ka ek identifier (jaise IP ya hostname) hash karke ring pe ek point pe rakh dete hain. To 4 nodes ring pe 4 alag positions pe baith jaate hain.

3. **Keys ki placement:** Har key (jaise `user:42` ya ek cache key) ko bhi usi hash function se hash karke ring pe ek point milta hai.

4. **Clockwise assignment:** Ek key kis node ko belong karti hai? Key ke position se clockwise chalte jao, aur jo **pehla node** milta hai wahi us key ka owner hai. (Convention clockwise/anti-clockwise koi bhi ho sakta hai, bas consistent honi chahiye.)

5. **Node add/remove:** Jab naya node ring pe add hota hai, to wo apne aur apne predecessor node ke beech wali keys "steal" kar leta hai — sirf utni hi keys move hoti hain. Jab koi node hata, to uski saari keys uske clockwise successor ko transfer ho jaati hain. Dono case mein baaki nodes untouched rehte hain.

6. **Virtual nodes (vnodes) — load balance ka asli trick:** Problem ye hai ki agar har physical node ko ring pe sirf ek hi point pe rakhein, to positions random hone ki wajah se kisi node ko ring ka bada arc mil sakta hai aur kisi ko chhota — yaani uneven load (hot spots). Solution: har physical node ko ring pe **kai points** pe rakho. Matlab node `A` ko `A#1`, `A#2`, ... `A#150` ke roop mein 150 alag hashed positions pe scatter kar do. Ye 150 points "virtual nodes" hain. Zyada points hone se ring pe har physical node ka total arc statistically balance ho jaata hai (law of large numbers), aur load distribution smooth ho jaata hai. Bonus: jab ek node hata, to uski keys ek single successor pe nahi girtin — wo kai successors ke beech bant jaati hain.

## Tradeoffs & Variants

- **vs naive `hash(key) % N`:** Modulo scheme mein assignment poori tarah `N` (node count) pe depend karta hai. Jaise hi `N` badalta hai (node add/remove), `hash(key) % N` ki value almost har key ke liye change ho jaati hai, to ~poora dataset remap hota hai — distributed cache mein ye ek massive cache stampede / DB overload trigger kar deta hai. Consistent hashing mein `N` change hone pe sirf ~K/N keys move hoti hain.

- **vnode count ka tradeoff:** Zyada vnodes (jaise per node 100-200+) → behtar load balance aur node removal pe smoother redistribution. Lekin har vnode ko ring metadata mein track karna padta hai, to memory aur lookup/routing table bada hota hai. Kam vnodes → halka metadata, par zyada imbalance risk. Practice mein ~100-256 vnodes per node ek common sweet spot hai.

- **Weighted nodes:** Agar kuch servers zyada powerful hain (zyada RAM/CPU), to unko proportionally **zyada vnodes** de do. Jaise ek 2x-capacity node ko 2x vnodes — to ring ka double arc usko milta hai aur wo proportionally zyada keys handle karta hai. Ye heterogeneous clusters ke liye clean way hai capacity skew handle karne ka.

## When To Use It

- **Sharding / data partitioning:** Keys ko nodes ke beech distribute karna jahan node count time ke saath badalta rehta hai.
- **Distributed caches:** Ek ring of cache servers (jaise Memcached fleet, ya Redis cluster-style setups) — taaki ek cache node add/remove karne pe poora cache invalidate na ho.
- **Load balancers:** Requests ko backend servers pe map karna with sticky behaviour, bina poora mapping reshuffle kiye jab servers aate-jaate hain.
- **Databases:** Cassandra aur Amazon DynamoDB partitioning ke liye consistent hashing (with vnodes) use karte hain — keys ko ring pe place karke replicas ko clockwise successors pe rakhna.

## Common Interview Gotchas

- **"Sirf K/N keys move hoti hain" — aur WHY:** Ye sabse important point hai. `K` = total keys, `N` = nodes (add ke baad). Jab naya node ring pe aata hai, wo sirf apne arc segment ki keys leta hai — jo statistically `K/N` ke aas-paas hoti hain. Concrete: **1000 keys across 4 nodes; ek 5th node add karo → average sirf ~200 keys (K/N = 1000/5) remap hoti hain**, baaki ~800 untouched. Modulo scheme hota to lagbhag saari 1000 keys ki position badal jaati. WHY: clockwise ownership sirf neighbour ke beech ke arc ko affect karta hai, global mapping ko nahi.

- **Hot spots without vnodes:** Agar bina vnodes ke plain consistent hashing use karein, to random node placement ki wajah se kisi node ko ring ka bada arc mil sakta hai → wo node overloaded (hot spot). Isiliye production mein hamesha vnodes use hote hain. Interviewer aksar poochta hai "without vnodes kya problem hogi?" — answer: load imbalance / hot spots.

- **Hash function choice:** Hash function uniform aur well-distributed hona chahiye (jaise MurmurHash), warna nodes/keys ring pe cluster ho jaayenge aur balance bigad jaayega. Cryptographic strength yahan goal nahi hai — distribution quality aur speed matter karte hain. Bad hash = clustered points = uneven arcs even with vnodes.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/data-distribution/conceptual_quiz_consistent_hashing.md`](../../../sysd-quizzes/data-distribution/conceptual_quiz_consistent_hashing.md) — `sysd-buddy quiz scaffold consistent-hashing` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update consistent-hashing --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — hash ring, key/node placement, aur clockwise assignment ka interactive diagram.
