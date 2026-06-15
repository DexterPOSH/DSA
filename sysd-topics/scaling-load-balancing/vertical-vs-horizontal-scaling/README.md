# Vertical vs Horizontal Scaling

**Track:** Building Blocks
**Category:** Scaling & Load Balancing

## What It Is

Vertical scaling (scale up) ka matlab hai ek single machine ko aur powerful banana (zyada CPU, RAM, disk), jabki horizontal scaling (scale out) ka matlab hai zyada machines add karke load ko unke beech baant dena.

## Real-World Analogy

Socho aapka ek dhaba hai jahan ek hi cook khana banata hai. Customers badhne lage. Ab aapke paas do raaste hain.

**Vertical scaling:** Aap usi ek cook ko ek bada chulha, tez gas, aur teen burners de do — taaki wahi banda zyada tezi se zyada plates nikaal sake. Simple hai, kitchen waisi ki waisi hai, ek hi banda sab sambhaal raha hai. Lekin ek dikkat: cook to ek hi hai. Agar usko chhutti chahiye, ya wo beemar pad gaya, to poora dhaba band. Aur ek banda chahe kitna bhi powerful chulha de do, ek limit ke baad zyada plates nahi nikaal sakta.

**Horizontal scaling:** Aap teen aur cooks hire kar lo, sabke apne chulhe, aur ek waiter (load balancer) orders ko inn cooks ke beech distribute kare. Ab agar ek cook beemar pad gaya, baaki teen kaam chalu rakhte hain — koi ek single point of failure nahi. Aur capacity badhani ho to bas ek aur cook add kar do. Dikkat ye hai ki ab aapko coordination chahiye: order kis cook ke paas jaaye, sab cooks ek hi recipe (consistent data) follow karein, aur kitchen thodi complex ho jaati hai.

Yahi vertical bhi-versus-horizontal ka core tradeoff hai: ek powerful banda (simple par ceiling aur single point of failure), versus kai normal bande (resilient aur elastic par coordination ka kharcha).

## How It Works

1. **Vertical scaling (scale up):** Aap apni existing machine ka instance type upgrade karte ho. Jaise cloud pe ek VM ko `4 vCPU / 16 GB RAM` se `16 vCPU / 64 GB RAM` pe le jaana. Application code waisa ka waisa rehta hai — usko bas zyada resources mil jaate hain. Ek single-node Postgres jo `2000 QPS` pe choke kar raha tha, bigger instance pe `8000 QPS` handle kar sakta hai. Catch: ye upgrade aksar reboot/downtime maangta hai (instance resize ke liye machine restart), aur har hardware tier ki ek physical ceiling hoti hai (jaise ek single box max `128 vCPU / 4 TB RAM`).

2. **Horizontal scaling (scale out):** Aap kai identical machines (replicas) chalate ho aur unke aage ek **load balancer** rakhte ho jo incoming requests ko inn machines pe distribute karta hai (round-robin, least-connections, ya consistent hashing se). Agar ek node `2000 QPS` serve karta hai, to `5` nodes theoretically `~10000 QPS` — but real mein thoda kam, kyunki coordination overhead lagta hai.

3. **Stateless tier scale-out:** Stateless services (jaise web/API servers jinke paas local session state nahi) scale out karna easy hai — bas ek aur replica add karo aur load balancer pool mein register kar do. Naya capacity seconds-to-minutes mein available. Yahi cloud autoscaling ka basic premise hai: CPU `70%` cross kare to ek instance add, `30%` se neeche jaaye to ek hata do.

4. **Stateful tier scale-out (mushkil part):** Databases jaise stateful systems ko horizontally scale karna tricky hai kyunki data ko machines ke beech baantna padta hai. Do common patterns:
   - **Replication:** Ek primary (writes) + kai read replicas (reads). Read-heavy workload scale ho jaata hai, par writes still ek primary pe (ya phir multi-primary with conflict handling).
   - **Sharding/partitioning:** Data ko key ke basis pe tukdon (shards) mein baant do — jaise `user_id % N`, ya consistent hashing se. Har shard ek alag machine pe. Ab writes bhi parallel scale hote hain, par cross-shard queries aur joins painful ho jaate hain.

5. **Latency angle:** Vertical scaling per-request latency ko aksar kam karta hai (faster CPU, zyada RAM = kam disk I/O, bada cache). Horizontal scaling throughput badhata hai par ek extra network hop (load balancer + possibly cross-node coordination) add kar sakta hai, jisse single-request latency thodi badh sakti hai (jaise `+1-2 ms` LB hop).

## Tradeoffs & Variants

- **Ceiling:** Vertical scaling ki ek hard physical limit hai — duniya ki sabse badi machine bhi ek finite size ki hai. Horizontal scaling theoretically "infinite" hai (aur machines add karte raho), jab tak coordination cost manage ho.

- **Availability / SPOF:** Single vertically-scaled box ek **single point of failure** hai — wo gira to service down. Horizontal setup mein redundancy built-in hai: ek node mare to baaki serve karte rehte hain (with proper health checks aur LB).

- **Cost curve:** Vertical scaling ki cost super-linear ho jaati hai — ek `2x` powerful machine aksar `2x` se zyada mehngi padti hai (high-end hardware premium). Horizontal scaling commodity hardware use karta hai, to cost zyada linear aur predictable rehti hai. Lekin horizontal mein operational/coordination cost (orchestration, networking, monitoring) add hoti hai.

- **Complexity:** Vertical simple hai — koi distributed systems problem nahi (no consistency, no partition tolerance headaches). Horizontal aapko CAP-theorem ki duniya mein le jaata hai: data consistency, replication lag, partial failures, distributed transactions — sab handle karna padta hai.

- **Downtime to scale:** Vertical scaling aksar reboot maangti hai (downtime), unless aap live-migration support karne wala platform use karein. Horizontal scaling zero-downtime ho sakti hai — naye nodes add karo bina existing ko chhede.

- **Statelessness ka role:** Horizontal scaling tab smooth hoti hai jab tier stateless ho. State ko bahar push karo (shared cache like Redis, DB, ya object store) taaki koi bhi replica koi bhi request serve kar sake. Sticky sessions avoid karo agar ho sake.

## When To Use It

- **Vertical first, simple workloads:** Early-stage app ya jab traffic abhi chhota hai — ek bada box hi simplest answer hai. Premature distribution avoid karo. Single-node Postgres/MySQL ko upgrade karna often databases ke liye pehla step hota hai (sharding se pehle).

- **Stateful databases jab tak possible:** Relational DBs ko log aksar vertically scale karte hain pehle (bigger instance), phir read replicas, phir last resort mein sharding — kyunki sharding strong consistency aur joins ko tod deta hai.

- **Horizontal for stateless web/API tier:** Web servers, API gateways, microservices — ye almost hamesha horizontally scale karte hain behind a load balancer. Yahi internet-scale services (Google, Amazon, Netflix) ka default hai.

- **Horizontal for elastic / spiky traffic:** Jab load predictable nahi (jaise flash sale, viral spike), autoscaling groups jo horizontally instances add/remove karte hain best fit hain — pay only for what you use.

- **Real systems:** Cassandra aur DynamoDB horizontal scaling (sharding + replication) ke liye built hain. Google's Spanner aur CockroachDB horizontally-scalable SQL dene ki koshish karte hain. Vertical example: ek single large Postgres/Oracle box jo enterprise OLTP serve karta hai. Practice mein bade systems **dono** combine karte hain — har node decently powerful (vertical) aur kai nodes (horizontal).

## Common Interview Gotchas

- **"Horizontal scaling hamesha better hai" — galat oversimplification:** Horizontal coordination cost (consistency, replication lag, distributed transactions, operational complexity) add karti hai. Chhote ya stateful workloads ke liye vertical scaling aksar zyada pragmatic aur sasta hota hai. Interviewer dekhna chahta hai ki aap blindly "just add more servers" nahi bolte.

- **Stateless vs stateful distinction:** Sabse common miss. Stateless tier scale out karna trivial hai; stateful (DB) scale out karna asli challenge hai. Agar aap "bas servers add kar do" bolte ho bina ye soche ki database kaise scale hogi, to interviewer turant pakad lega. State ko bahar (Redis/DB/object store) move karna ek key technique hai.

- **Linear speedup ki galatfehmi:** `N` nodes ka matlab `N`x throughput nahi hota. Coordination overhead, load imbalance, aur shared bottlenecks (jaise ek hi DB) ki wajah se real speedup sublinear hota hai. Amdahl's law: jo hissa serial hai (jaise single primary pe writes), wo overall scaling ko cap kar deta hai.

- **"Infinite scaling" myth:** Horizontal bhi truly infinite nahi — ek point ke baad coordination cost, network saturation, ya ek shared component (single primary DB, central lock service) bottleneck ban jaata hai. Linear cost bhi tabhi milti hai jab architecture genuinely shared-nothing ho.

- **Downtime assumption:** Log maan lete hain vertical scaling zero-downtime hai — usually nahi, instance resize ke liye reboot chahiye. Aur ulta, log maan lete hain horizontal scaling free hai — par naye nodes ko warm-up (cache fill, connection pool), data rebalance, aur LB registration time lagta hai.

- **Scale up vs scale out terminology:** "Scale up" = vertical, "scale out" = horizontal. Inn terms ko confuse mat karo — interviewer precise vocabulary expect karta hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_vertical_vs_horizontal_scaling.md`](../../../sysd-quizzes/scaling-load-balancing/conceptual_quiz_vertical_vs_horizontal_scaling.md) — `sysd-buddy quiz scaffold vertical-vs-horizontal-scaling` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update vertical-vs-horizontal-scaling --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — vertical (ek box grow hota) versus horizontal (load balancer ke peeche kai nodes) ka side-by-side interactive diagram.
