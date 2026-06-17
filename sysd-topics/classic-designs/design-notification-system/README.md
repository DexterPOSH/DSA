# Design a Notification System

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Ek aisa system jo multiple services se trigger events leta hai aur unko millions of users tak teen channels — Push (APNs/FCM), SMS, aur Email — pe reliably, at-scale, aur near-real-time deliver karta hai.

## Requirements & Scope

Interview mein sabse pehle scope nail karna zaroori hai, warna aap galat system bana doge. Pehle clarifying questions, phir requirements.

**Clarifying questions (jo interviewer se poochne chahiye):**
- Kaun se channels support karne hain? (Push only, ya SMS + Email + Push + in-app?)
- Notifications transactional hain (OTP, password reset) ya promotional/bulk (marketing campaigns)? Dono ke SLA bahut different hote hain.
- Delivery guarantee kya chahiye — at-least-once ya exactly-once? (Real answer: at-least-once + idempotency, kyunki exactly-once distributed systems mein practically impossible/expensive hai.)
- Ordering matter karta hai? (Usually per-user soft ordering theek hai, strict global ordering nahi.)
- User preferences / opt-out aur rate limiting chahiye? (Almost always haan — spam aur compliance ke liye.)
- Scale kya hai — kitne DAU, peak QPS?

**Functional requirements:**
- Multiple sender services events bhej sakein ek single notification API ke through.
- Teen channels: Push, SMS, Email (third-party providers ke saath integrate).
- User preferences honi chahiye — channel-level opt-in/opt-out aur Do-Not-Disturb (DND).
- Templating support (personalized content with variables).
- Rate limiting per user (taaki ek user ko 50 notifications na chali jaayein).
- Deduplication — same event do baar aaye to ek hi notification jaaye.

**Non-functional requirements:**
- **High availability** — notification drop nahi hona chahiye (especially OTP jaise transactional).
- **Reliability / durability** — agar downstream provider down hai to message kho na jaaye; retry hona chahiye.
- **Low latency** transactional ke liye (OTP < few seconds), bulk ke liye eventual theek hai.
- **Scalability** — millions of notifications/day, traffic spikes (sale events) handle karna.
- **Decoupling** — sender services ko provider downtime se shielded rehna chahiye.

## Capacity Estimate

Back-of-the-envelope. Assume karte hain:

- **DAU = 10 million** users.
- Average **5 notifications per user per day** (push + email mix).
- Total notifications/day = `10M * 5 = 50M/day`.

**Write QPS (notification ingestion):**
- `50M / 86400 sec ≈ 580 QPS` average.
- Peak factor ~5x (sale/event spikes) → **~2,900 QPS peak**. Round to ~3K QPS write.

**Read QPS (preferences/template lookups):**
- Har notification ke liye ek user-preference lookup + template fetch. Average ~580 QPS, peak ~3K QPS reads — lekin ye cache se serve honge (Redis), DB hit nahi.

**Storage estimate (notification logs, 1 year retention):**
- Per notification record ≈ `500 bytes` (id, user_id, channel, status, timestamps, template_id, metadata).
- Per day = `50M * 500 bytes = 25 GB/day`.
- Per year = `25 GB * 365 ≈ 9.1 TB/year`. Replication 3x → **~27 TB**. Ye easily NoSQL (Cassandra) pe shard ho jaata hai.

**Bandwidth:**
- Write ingestion: `3K QPS * 500 bytes ≈ 1.5 MB/s` — trivial.
- Real bandwidth provider egress pe hai (email bodies, push payloads), jo per-channel third-party handle karte hain.

**Takeaway:** Ye system write-heavy + fan-out-heavy hai. Bottleneck DB nahi, balki **downstream provider throughput aur queue depth** hai. Isiliye message queue + worker fleet design ka core hai.

## API Design

Single ingestion endpoint, internally event-driven.

```
POST /v1/notifications
Authorization: Bearer <service-token>
Body:
{
  "user_id": "u_123",
  "event_type": "order_shipped",        // maps to a template
  "channels": ["push", "email"],          // optional; else use user prefs
  "template_data": { "order_id": "A42", "eta": "Jun 18" },
  "priority": "transactional",            // transactional | bulk
  "dedup_key": "order_shipped:A42:u_123"  // idempotency key
}
→ 202 Accepted { "notification_id": "n_789", "status": "queued" }
```

Preference management:
```
GET  /v1/users/{user_id}/preferences
PUT  /v1/users/{user_id}/preferences
   { "push": true, "email": true, "sms": false, "dnd": {"start":"22:00","end":"08:00"} }
```

Status / observability:
```
GET  /v1/notifications/{notification_id}   → { status: sent|delivered|failed|bounced }
```

Note: ingestion **202 Accepted** return karta hai (sync nahi). Actual delivery async hoti hai queue ke through — ye decoupling ka core hai.

## High-Level Architecture

Request flow components:

1. **Notification Service (API gateway)** — sender services se request leta hai, basic validation (auth, schema) karta hai, dedup_key check karta hai, aur event ko message queue pe daal deta hai. Phir turant 202 return karta hai.
2. **Message Queue (Kafka)** — buffer + decoupling layer. Sender ko provider downtime se isolate karta hai aur traffic spikes ko absorb karta hai. Priority ke hisaab se alag topics (transactional vs bulk) taaki OTP marketing ke peeche stuck na ho.
3. **Workers / Consumers (per channel)** — queue se consume karte hain. Har worker:
   - **Preference & DND check** — user ne is channel pe opt-out to nahi kiya, DND window mein to nahi.
   - **Rate limiter check** — per-user token bucket (Redis).
   - **Template rendering** — template + `template_data` se final content banata hai.
   - **Provider call** — channel-specific adapter (APNs/FCM, Twilio/SNS, SES) ko call karta hai.
4. **Third-party Adapters** — APNs/FCM (push), Twilio/SNS (SMS), SES/SendGrid (email). Each behind a retry + circuit-breaker wrapper.
5. **Notification Log / Status Store (Cassandra)** — har attempt aur final status persist hota hai (analytics, debugging, status API).
6. **Preference DB + Cache** — user preferences (source of truth in DB, hot path Redis cache se).

Flow ek line mein: `Sender → Notification Service → Kafka → Channel Worker → (pref/rate/template) → Provider → Status logged`.

## Data Model

Do mukhya stores, kyunki access patterns alag hain.

**1. User Preferences — relational (PostgreSQL/MySQL).** Low write volume, strong consistency chahiye (compliance/opt-out legally binding), relational queries. SQL yahan sahi choice hai.
```
user_preferences
  user_id        PK
  push_enabled   bool
  email_enabled  bool
  sms_enabled    bool
  email          string
  phone          string
  device_tokens  json    // APNs/FCM tokens
  dnd_start      time
  dnd_end        time
  updated_at     timestamp
```

**2. Notification Log — NoSQL wide-column (Cassandra).** Write-heavy (50M/day), append-only, time-series-ish, kabhi update nahi karte — sirf insert + point/range reads by user. SQL yahan choke karega (single-node write ceiling, expensive sharding). Cassandra ka partition-by-user + clustering-by-time model perfect fit hai.
```
notification_log
  PARTITION KEY  user_id
  CLUSTERING KEY created_at DESC, notification_id
  channel        string
  status         string   // queued|sent|delivered|failed|bounced
  template_id    string
  dedup_key      string
  provider_resp  text
```

**SQL vs NoSQL nichod:** Preferences = SQL (consistency, low volume, relational). Logs = NoSQL (massive write throughput, horizontal scale, time-series access). Ye access-pattern-driven split classic interview signal hai.

## Deep Dives

**1. Message Queue + decoupling (sabse important).** Notification Service synchronously providers ko call kare to ye anti-pattern hai — provider down hua to sender block ho jaayega, aur spike mein system gir jaayega. Kafka beech mein daal ke hum producer ko consumer se decouple kar dete hain. Benefits: (a) spikes absorb hote hain (queue depth badhta hai, drop nahi hota), (b) retries possible hain (failed message ko re-enqueue), (c) priority isolation (transactional topic alag se, high consumer count). Partitioning **by user_id** se per-user ordering bhi soft-maintain hoti hai.

**2. Reliability — at-least-once + idempotency/dedup.** Distributed delivery mein exactly-once practically nahi milta, isliye hum **at-least-once** chunte hain (message kabhi kho na, bhale duplicate aa jaaye) aur duplicates ko **dedup_key + Redis** se kill karte hain. Worker provider call se pehle `SETNX dedup_key` karta hai (TTL ke saath); already-set hai to skip. Failed providers ke liye **retry with exponential backoff**, aur jo baar-baar fail karein wo **Dead Letter Queue (DLQ)** mein jaate hain for manual inspection — taaki ek poison message poore consumer ko block na kare.

**3. Rate limiting + provider fan-out resilience.** Per-user **token bucket in Redis** spam rokta hai (e.g. max N notifications/hour). Provider side pe **circuit breaker** lagate hain — agar APNs error rate spike kare, to circuit open ho jaata hai aur hum traffic temporarily roak ke queue mein hold karte hain (cascading failure se bachne ke liye), phir half-open se recover karte hain. Caching: user preferences Redis mein cache hoti hain (read-heavy hot path), DB sirf miss/update pe hit hoti hai.

## Bottlenecks & Tradeoffs

- **Third-party provider as the real bottleneck.** APNs/SES ki apni rate limits aur downtime hoti hai. Mitigation: queue buffering, per-provider rate limiting, circuit breakers, aur multi-provider failover (e.g. primary SES, fallback SendGrid).
- **Hot partitions / celebrity fan-out.** Agar ek event se millions of users ko notify karna ho (broadcast), to fan-out write storm aa jaata hai. Mitigation: dedicated bulk pipeline with batching aur separate low-priority topics, taaki transactional latency na bigde.
- **Duplicate notifications.** At-least-once ka natural side-effect. Mitigation: dedup_key + idempotency store (Redis with TTL). Trade-off: dedup window TTL bada karoge to memory cost, chhota karoge to late duplicate ho sakta hai.
- **Queue backpressure.** Provider slow hua to queue depth badhta jaayega → memory/lag. Mitigation: autoscale consumers, drop/deprioritize bulk traffic first, monitoring + alerts on consumer lag.
- **Preference staleness.** Cache se serve karne pe ek user opt-out karega to thodi der purani preference cache se aa sakti hai → unwanted notification (compliance risk). Mitigation: opt-out pe cache invalidate karo immediately + short TTL.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_notification_system.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_notification_system.md) — grade hone ke baad score record karo with `sysd-buddy progress update design-notification-system --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — components, queue-based flow, aur channel fan-out ka interactive diagram.
