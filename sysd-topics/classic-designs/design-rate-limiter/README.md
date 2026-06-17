# Design a Rate Limiter

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Rate limiter ek aisa component hai jo ek client (user / IP / API key) ko ek time window mein kitni requests allowed hain ye enforce karta hai, aur limit cross hone par requests ko reject (HTTP `429 Too Many Requests`) ya throttle karta hai.

## Requirements & Scope

**Clarifying questions (interview ki shuruaat mein ye poochho):**

- Limiter client-side hai ya server-side? (Hum **server-side**, ek shared service maan rahe hain — client-side trust nahi kar sakte.)
- Limit kis dimension pe? Per user ID, per IP, per API key, ya per endpoint? (Hum flexible **rule-based** keys support karenge, jaise `{user_id}:{endpoint}`.)
- Single data-center hai ya **distributed / multi-DC**? (Hum distributed maanenge — yahi asli challenge hai.)
- Limit exceed hone par hard reject karna hai ya soft throttle/queue? (Default: reject with `429`.)

**Functional requirements:**

- Configurable rules: "100 requests per minute per user", "5 logins per IP per 15 min" jaise rules define ho saken.
- Limit exceed hone par request block ho aur client ko clear signal mile (`429` + `Retry-After` header).
- Multiple limiter ek hi key pe consistent decision den (distributed correctness).

**Non-functional requirements (ye zyada important hain interview mein):**

- **Low latency:** Limiter har request ke path mein baithta hai, isliye decision sub-millisecond hona chahiye. Limiter khud bottleneck nahi banna chahiye.
- **High availability:** Limiter down ho to bhi main service chalti rahe. Yahan **fail-open** (limiter down → request allow) vs **fail-closed** (reject) ka tradeoff hai — zyadatar systems availability ke liye fail-open chunte hain.
- **Accuracy vs scalability:** Distributed setup mein perfect accuracy aur low latency dono ek saath mushkil hain; thoda over/under count tolerate karna padta hai.

## Capacity Estimate

Maan lo ek API gateway behind ek bada product hai:

- **DAU:** 100M users.
- **Average requests per user per day:** 50 → total daily requests = `100M * 50 = 5B requests/day`.
- **Average QPS:** `5B / 86,400 sec ≈ 57,870 ≈ ~58K QPS`.
- **Peak QPS:** average ka ~3x maan lo → `~174K ≈ ~175K QPS` peak.

**Counter storage:** Har active key ke liye ek counter chahiye (key + count + window timestamp ≈ `~50 bytes`). Maan lo peak par ~10M unique active keys ek window mein:

- Memory = `10M * 50 bytes = 500 MB`. Ye easily ek Redis instance (ya chhota cluster) ki RAM mein fit ho jaata hai — counters short-lived hain (TTL = window size), isliye long-term storage minimal hai.

**Bandwidth:** Har request par limiter ko ek read-modify-write (≈ `~100 bytes` round trip). Peak `175K QPS * 100 bytes = 17.5 MB/s ≈ ~140 Mbps` limiter store ke aage. Ye manageable hai.

**Takeaway:** Storage chhota hai (counters ephemeral hain), asli pressure **QPS aur per-request latency** par hai — isliye in-memory store (Redis) aur edge-level distribution chahiye.

## API Design

Rate limiter aam taur par ek internal call hai (gateway/middleware se), public API nahi. Core signature:

```
allow_request(key: string, rule_id: string) -> Decision

Decision {
  allowed:      bool
  limit:        int     // total allowed in window
  remaining:    int     // requests left in current window
  retry_after:  int     // seconds until allowed again (jab blocked ho)
}
```

Client-facing response (jab `allowed == false`):

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1718450400
```

Rule config (admin API se manage hoti hai):

```
POST /rules
{ "rule_id": "login_per_ip", "dimension": "ip", "limit": 5, "window_sec": 900, "algorithm": "sliding_window" }
```

## High-Level Architecture

Components:

1. **Client → API Gateway / Middleware:** Har incoming request gateway se guzarti hai. Gateway mein ek **rate-limiter middleware** baitha hai.
2. **Rule store:** Rules ek config store (jaise ek DB + local cache) mein rakhe jaate hain; middleware inhe periodically refresh karta hai (kyunki rules rarely change hote hain).
3. **Counter store (in-memory):** Ek **Redis** (ya Redis cluster) jo har key ka counter aur window state rakhta hai. Yahi shared state distributed correctness deta hai.
4. **Limiter logic:** Algorithm (token bucket / sliding window) jo counter store par atomic operation chala kar allow/deny decide karta hai.

**Request flow:**

1. Request gateway pe aati hai → middleware key banata hai (e.g. `user:42:GET/feed`).
2. Middleware rule lookup karta hai (local cache se).
3. Middleware counter store par **atomic** read-modify-write karta hai (Redis Lua script ya `INCR` + `EXPIRE`).
4. Counter limit ke andar hai → request backend ko forward, response headers mein `remaining` set.
5. Limit cross → `429` return, backend ko hit hi nahi karte.

## Data Model

**Counter store (Redis — NoSQL / in-memory key-value):**

| Field | Example | Notes |
|---|---|---|
| key | `rl:user:42:GET/feed` | rule + dimension se bana key |
| value | `87` (token bucket: count + last_refill_ts) | algorithm-specific state |
| TTL | `60s` (= window size) | expire hone par counter khud reset |

**Rule store (SQL — relational):**

| rule_id | dimension | limit | window_sec | algorithm |
|---|---|---|---|---|
| `login_per_ip` | ip | 5 | 900 | sliding_window |
| `api_per_user` | user_id | 100 | 60 | token_bucket |

**SQL vs NoSQL choice:**

- **Counters → NoSQL in-memory (Redis):** Counters ko **ultra-low-latency atomic increments aur TTL** chahiye, millions of writes/sec par. Redis exactly yahi deta hai (`INCR`, `EXPIRE`, Lua scripts for atomicity). Durability yahan matter nahi karti — counter window ke baad waise bhi gayab ho jaata hai. SQL yahan latency aur write-throughput pe fail karega.
- **Rules → SQL:** Rules low-volume, strongly-consistent, aur relational/queryable hone chahiye (admin dashboards, audits). Inhe cache karke har box pe rakha jaata hai, isliye SQL ka latency hot path mein nahi aata.

## Deep Dives

Tin building blocks jo yahan sabse zyada matter karte hain:

### 1. Algorithm choice: Token Bucket vs Sliding Window

- **Fixed window counter:** Ek window (e.g. 1 min) ke liye ek counter, `INCR` + `EXPIRE`. Simple aur fast, par **boundary burst problem** hai: window ke last second mein 100 + agle window ke first second mein 100 → 1 sec mein effectively 200 requests, limit "100/min" hone ke bawajood.
- **Sliding window log:** Har request ka timestamp ek sorted set mein store karo, window ke bahar wale evict karo, count gino. Bilkul accurate, par memory aur compute **per-request high** — har key ke liye saare timestamps rakhne padte hain.
- **Sliding window counter:** Current + previous fixed window ko weighted-average karke approximate karo. Accuracy aur cost ke beech sweet spot — boundary burst problem ko largely smooth kar deta hai bina poora log rakhe.
- **Token bucket:** Ek bucket mein tokens steady rate (`r` tokens/sec) pe refill hote hain, max capacity `b`. Har request ek token consume karti hai; token nahi to reject. **Bursts allow karta hai** (bucket bhara ho to) lekin steady-state rate cap karta hai. Most production limiters (jaise Stripe, AWS) iska variant use karte hain.

**Interview answer:** Default **token bucket** suggest karo — burst-friendly, memory-efficient (sirf 2 values: token count + last refill ts), aur Redis Lua mein atomic implement ho jaata hai.

### 2. Atomicity in a distributed counter store

Multiple gateway boxes ek hi Redis key ko hit karte hain. Naive "read count → check → increment" mein **race condition** hai: do boxes ek saath read karke dono allow kar sakte hain, limit cross karwa ke. Solution: operation ko **atomic** banao —

- `INCR` khud atomic hai (fixed window ke liye kaafi), aur first increment par `EXPIRE` set karo.
- Token bucket ke liye **Redis Lua script** use karo: refill compute + token check + decrement ek single atomic server-side operation mein. Isse check-and-act ka race khatam ho jaata hai.

### 3. Distributed coordination & edge enforcement

Multi-DC / multi-node par har box ki apni Redis copy rakhne se limits leak hoti hain. Do common patterns:

- **Centralized store:** Sab boxes ek shared Redis cluster ko hit karein → accurate, par extra network hop (latency) aur store par load.
- **Local + sync (sloppy counters):** Har box locally count kare aur periodically central store se reconcile kare → low latency, par thodi over-limit slack. High-scale systems ye accept karte hain (eventual accuracy).

## Bottlenecks & Tradeoffs

- **Single Redis hot key:** Ek bahut popular key (jaise ek viral endpoint) ek hi Redis shard ko hammer karega → hot shard. Mitigation: key ko shard karo (`key:bucket_0..N` counters ko split, then sum) ya key ko consistent-hash karke spread karo.
- **Latency vs accuracy:** Centralized counter accurate par slow; local sloppy counters fast par approximate. Tradeoff explicitly state karo — zyadatar production thodi inaccuracy accept karta hai for latency.
- **Redis availability:** Redis down ho to limiter ko **fail-open** karo (allow requests) taaki main service na ruke — availability ko correctness se upar rakhte hain. Critical limits (jaise fraud/login) ke liye fail-closed bhi valid choice hai.
- **Synchronization overhead:** Sloppy counters ka sync interval ek tradeoff hai — chhota interval → behtar accuracy, zyada network chatter; bada interval → ulta.
- **Boundary bursts:** Fixed window use kiya to 2x burst possible (upar dekha). Mitigation: sliding window counter ya token bucket.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_rate_limiter.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_rate_limiter.md) — grade hone ke baad score record karo with `sysd-buddy progress update design-rate-limiter --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — request flow, token bucket refill, aur distributed counter ka interactive diagram.
