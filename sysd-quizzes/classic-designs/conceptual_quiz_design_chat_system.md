# Design a Chat System (WhatsApp) — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update design-chat-system --quiz-score N/M` -->

## Q1 (warm-up — requirements/scoping)
Aapko "design WhatsApp" diya gaya hai. Kaam shuru karne se pehle aap kaunse clarifying questions poochoge, aur is system ke functional vs non-functional requirements kya honge? Kya scope mein NAHI rakhoge?

**Ideal answer:**
- **Clarifying questions:** 1:1 only ya group bhi (aur group max size)? Text only ya media? E2EE in scope? Delivery + read receipts chahiye? Presence/last-seen? Multi-device sync? History retention?
- **Functional:** 1:1 + group messaging, real-time delivery, offline store-and-forward, delivery + read receipts, online/last-seen presence, media attachments.
- **Non-functional:** low latency (sub-second), high availability, durability (no message ever lost even if recipient offline), scale (50M+ DAU), per-conversation ordering (global total order zaroori nahi), availability preferred over strong consistency.
- **Out of scope:** video calling, payments, stories — explicitly bol dena taaki time bache.
- Bonus: scoping ko narrow rakhna — interviewer ko impress karta hai jab aap pehle scope cut karte ho.

## Q2 (core — capacity estimate)
50M DAU aur average 40 messages per user per day maan ke, write QPS aur ek saal ka text-storage estimate nikaalo. Arithmetic dikhao, aur batao media ko alag kyun handle karoge.

**Ideal answer:**
- **Writes/day** = 50M × 40 = **2 billion/day**.
- **Avg write QPS** = 2×10^9 / 86,400 ≈ **~23,000/sec**; peak ≈ 2× ≈ **~46,000/sec**.
- **Storage:** ~300 bytes/message → 2×10^9 × 300 B = **600 GB/day** → × 365 ≈ **~219 TB/year** (text/metadata only).
- **Media:** blobs orders-of-magnitude bigger; isiliye S3-style blob store + CDN pe offload, chat servers se nahi — text path ka bandwidth/storage chhota aur predictable rehta hai.
- Grader checks: assumptions clearly stated, arithmetic shown, peak vs avg distinction, media separation reasoning. (Exact numbers se zyada method matter karta hai.)

## Q3 (data-model / API choice)
Messages store karne ke liye SQL chunoge ya NoSQL? Apna partition key aur clustering key batao, aur justify karo ki "last 50 messages of a conversation" query efficient kyun hogi.

**Ideal answer:**
- **NoSQL wide-column (Cassandra/HBase-style)** preferred: workload write-heavy + append-only + naturally per-conversation time-series; horizontal scale + tunable consistency chahiye; global joins/ACID transactions ki zaroorat nahi.
- **Partition key = conversationId** (ek thread = ek partition), **clustering key = messageId/timestamp (DESC, time-sortable like Snowflake/ULID)**.
- "Last 50 messages" ek **single-partition, already-sorted range read** ban jaata hai → fast, no scatter-gather.
- Mention: separate **per-user mailbox/inbox table** (partition key = userId) offline delivery ke liye; group membership/metadata SQL ya KV me (consistency for membership), presence/session in Redis.
- Grader checks: explicit choice + justification tied to access pattern, correct partition/clustering keys, single-partition read insight.

## Q4 (key deep-dive tradeoff — connection routing)
Sender ka WebSocket Server A pe hai, recipient ka Server B pe. Message A se B tak kaise pahुंchega? Aur recipient offline ho to message lost hone se kaise bachoge?

**Ideal answer:**
- **Session/Presence map in Redis** (`userId → chatServerId`): Server A lookup karke recipient ka server (B) find karta hai, phir internal message bus/RPC (e.g. Kafka) ke through forward karta hai → B push karta hai client ko.
- Chat servers **stateful** (sockets in memory) → sticky load balancing, aur server failure pe client reconnect + Session map update.
- **Offline → store-and-forward:** Session map "not connected" batata hai → message recipient ke **mailbox/inbox partition** me persist hota hai + Notification Service push (APNs/FCM) bhejti hai. Reconnect pe Chat Server mailbox drain karke deliver karta hai.
- **Durability via acks:** at-least-once delivery; ack na aaye to message pending rehta hai aur retry hota hai; `clientMsgId` se client-side de-dup → effectively-once.
- Grader checks: Session Service routing concept, stateful-server implication, mailbox-based store-and-forward, ack/retry for no-loss guarantee.

## Q5 (applied — scaling bottleneck + mitigation)
Aapke system me 1000+ member groups bahut active hain aur message delivery lag karne lagi. Kaun-kaun se bottlenecks ho sakte hain, aur har ek ka mitigation kya hai?

**Ideal answer:**
- **Group fan-out / write amplification:** ek message N copies + N push notifications → spike. Mitigation: async fan-out via Kafka queue; very large groups ke liye **fan-out-on-read** consider karo; hot-partition ke liye partitioning strategy revisit.
- **Read receipts cost:** har read receipt khud ek message → traffic doubles; large groups me per-member receipts mehenga. Mitigation: aggregate/limit read receipts for big groups.
- **Presence/heartbeat load:** 10M concurrent × frequent heartbeats = huge write load. Mitigation: heartbeat interval badhao (5–10s), presence eventually-consistent + approximate last-seen.
- **Stateful server reconnect storms (thundering herd):** server crash pe saare clients ek saath reconnect. Mitigation: jittered exponential backoff, capacity headroom, fast Session map updates.
- Grader checks: identifies at least 2-3 distinct bottlenecks specific to chat-at-scale AND gives a concrete mitigation for each (not just "add more servers").
