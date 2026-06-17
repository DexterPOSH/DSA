# Design a Chat System (WhatsApp)

**Track:** Design Problems
**Category:** Classic Designs

## What It Is

Ek 1:1 aur group messaging system design karna jahan messages real-time deliver hon, offline users ko reliably store-and-forward ho, aur delivery/read receipts (single tick, double tick, blue tick) aur online/last-seen presence dikhe — billions of users ke scale pe.

## Requirements & Scope

Pehle scope nail karna zaroori hai — warna aap pura Slack/Teams build karne lag jaoge. Clarifying questions interviewer se:

- 1:1 chat + group chat dono? Group ka max size kya (WhatsApp ~1024)?
- Sirf text, ya media (images/video/voice) bhi? End-to-end encryption (E2EE) in scope?
- Delivery + read receipts chahiye? Presence (online/last-seen)?
- Message history kitne time retain karni hai — forever ya devices tak?
- Multi-device sync chahiye?

**Functional requirements (scope ke andar):**
- 1:1 aur group messaging, real-time delivery jab dono online ho.
- Offline users ke liye store-and-forward — jab wapas online aaye to pending messages mile.
- Delivery receipt (server received + recipient delivered) aur read receipt.
- Online/last-seen presence.
- Media attachments (image/video/voice) via blob store.

**Non-functional requirements:**
- **Low latency** — message delivery sub-second feel honi chahiye.
- **High availability** — chat down nahi ho sakta; but availability over strong consistency (ek message thoda late aana acceptable hai, lost nahi).
- **Reliability/durability** — koi message kabhi drop nahi hona chahiye, even agar recipient offline ho.
- **Scale** — 50M+ DAU, billions of messages/day.
- **Consistency** — ek single chat thread ke andar message ordering preserve honi chahiye (causal/per-conversation ordering), global total order zaroori nahi.

**Explicitly out of scope** (interview time bachane ke liye bol do): video calling, payments, stories. E2EE ko optional mention rakho — agar interviewer chahe to deep-dive.

## Capacity Estimate

Back-of-the-envelope. Assumptions clearly bol kar number nikalo:

- **DAU = 50 million**, har user average **40 messages/day** bhejta hai.
- **Writes/day** = 50M × 40 = **2 billion messages/day**.
- **Write QPS (avg)** = 2 × 10^9 / 86,400 s ≈ **23,000 writes/sec**. Peak ≈ 2× avg ≈ **~46,000 writes/sec**.
- **Read QPS** — ek message average ~1.5 recipients tak deliver hota hai (mostly 1:1, kuch group fan-out), plus receipts. Read fan-out roughly 2× writes → **~46,000 reads/sec avg**, peak **~90,000/sec**.

**Storage:**
- Average message payload (text + metadata: ids, timestamps, sender, status) ≈ **300 bytes**.
- Per day = 2 × 10^9 × 300 B = **600 GB/day**.
- Per year = 600 GB × 365 ≈ **219 TB/year** (text only). Media blobs alag S3-style store mein jaate hain, aur woh isse kahin bada hota hai — but text metadata yeh raha.

**Bandwidth:**
- Incoming write bandwidth = 23,000 msg/s × 300 B ≈ **6.9 MB/s** (text only). Media uploads is se orders-of-magnitude zyada, isiliye media ko CDN/blob path pe offload karte hain, chat servers se nahi.

**Connections:**
- 50M DAU me se assume karo ~10M concurrently connected. Ek server agent ~100K persistent connections handle kar sakta hai (tuned) → **~100+ connection (chat) servers** sirf live sockets ke liye.

## API Design

WebSocket (ya WhatsApp jaisa MQTT) for the real-time bidirectional channel; HTTP/REST for non-realtime ops (history, group mgmt, media presign). Sketch:

```
# Real-time channel (persistent WebSocket)
connect(authToken)                          # client → chat server, opens socket
send(conversationId, clientMsgId, content)  # client → server; server returns serverMsgId + ts
recvMessage(message)                        # server → client push
ack(messageId, status)                      # delivered/read receipts, both directions
presence(userId, status, lastSeen)          # server → client push

# REST (non-realtime)
POST /v1/conversations                       {participantIds[]} -> conversationId
GET  /v1/conversations/{id}/messages?before=<ts>&limit=50   # history pagination
POST /v1/groups/{id}/members                 {userId}
POST /v1/media:presign                        {mimeType,size} -> {uploadUrl, mediaId}
```

`clientMsgId` (client-generated UUID) idempotency ke liye critical hai — retries pe duplicate message create na ho.

## High-Level Architecture

Components:

- **Client** — persistent WebSocket connection ek **Chat (WebSocket) Server** se.
- **Connection/Session Service** — tracks "user X kis chat server pe connected hai" (a `userId → chatServerId` map in Redis). Routing ke liye essential.
- **Chat Servers** — stateful, persistent connections hold karte hain; messages receive/forward karte hain.
- **Message Service + Message Store** — persistence (write to DB) aur store-and-forward for offline users.
- **Presence Service** — heartbeat se online/last-seen track karta hai, Redis me.
- **Group Service** — group membership/metadata.
- **Notification Service** — APNs/FCM push jab recipient offline ho.
- **Media/Blob Store + CDN** — images/video/voice.

**Request flow (1:1, recipient online):**
1. Sender apne Chat Server A ko message bhejta hai (WebSocket).
2. Chat Server A message ko **Message Store** me persist karta hai, `serverMsgId` + timestamp assign karta hai, sender ko **delivery (server-received) ack** bhejta hai → single tick.
3. Server A, Session Service se poochta hai "recipient kis server pe hai?" → Chat Server B.
4. Message Server B ko route hota hai (internal message bus/RPC), B recipient ko push karta hai.
5. Recipient ka client **delivered ack** bhejta hai → sender ko double tick. Read karne pe **read ack** → blue tick.

**Recipient offline:** Step 3 pe Session Service "not connected" batata hai. Message Store me message **pending/undelivered** mark hota hai, aur Notification Service push notification bhejti hai. Jab recipient reconnect kare, Chat Server uske pending messages Message Store se pull karke deliver karta hai (store-and-forward).

## Data Model

NoSQL (wide-column, Cassandra/HBase-style) yahan SQL se behtar fit hai. Kyun: messages ek **append-heavy, write-dominant** workload hai (46K writes/sec), data naturally **per-conversation time-series** hai, aur hume single-thread ke andar ordering chahiye — global joins/transactions nahi. Wide-column store horizontal scale + tunable consistency + sorted clustering by time deta hai, jo exactly hamara access pattern hai. ACID transactions ki yahan zaroorat nahi.

**Messages table** (partition key = `conversationId`, clustering key = `messageId`/timestamp DESC):

| Field | Notes |
|---|---|
| `conversationId` | partition key — ek thread ek partition |
| `messageId` | time-sortable ID (Snowflake/ULID) → ordering aur clustering |
| `senderId` | |
| `content` / `mediaId` | text inline, media pointer to blob store |
| `createdAt` | |
| `status` | sent / delivered / read |

Is design me "GET last 50 messages of conversation X" ek single-partition sorted read ban jaata hai — fast.

**Per-user inbox / mailbox table** (offline delivery ke liye): partition key = `userId`, undelivered messages queue. Reconnect pe yahi drain hota hai.

**Group membership** + **conversation metadata** chhota, low-write data hai — ise relational/SQL ya simple KV me rakhna theek hai (consistency matters for membership).

**Presence + session map** RAM-speed chahiye → **Redis** (`userId → {status, lastSeen}`, `userId → chatServerId`), short TTLs ke saath.

## Deep Dives

**1) Connection routing + the Session Service.**
Asli challenge yeh hai ki sender ka socket Server A pe hai, recipient ka Server B pe — beech me message kaise jaaye? Solution: ek **Session/Presence map in Redis** jo `userId → chatServerId` rakhta hai. Server A is map me lookup karke Server B ko ek internal message bus (Kafka/RPC) ke through forward karta hai. Yeh "service discovery for live users" hai. Chat servers ko **stateful** rakhna padta hai (sockets in memory), to load balancing sticky honi chahiye aur server failure pe clients ko reconnect + Session Service update karna padta hai.

**2) Store-and-forward via per-user mailbox (the durability core).**
Offline users hi asli design problem hain. Har undelivered message recipient ke **mailbox/inbox partition** me persist hota hai. Reconnect pe Chat Server mailbox drain karta hai aur deliver karta hai, phir delivered ack aane pe entry clear/mark karta hai. Ack-based design ensure karta hai koi message lost na ho — agar ack nahi aaya, message pending rehta hai aur retry hota hai (at-least-once delivery; `clientMsgId` se client de-dup karta hai → effectively once).

**3) Message ordering with Snowflake/ULID IDs.**
Per-conversation ordering chahiye, global total order nahi. Har message ko ek **time-sortable ID** (Snowflake: timestamp + machine + sequence) milta hai. Same partition (conversation) ke andar clustering-by-ID se messages sorted aate hain. Distributed clock skew ka problem global ordering me hota — but kyunki hum sirf per-conversation order chahte hain (jo mostly ek hi region/partition se serialize hota hai), yeh manageable rehta hai. Receivers client-side bhi reorder kar sakte hain via timestamp/sequence.

## Bottlenecks & Tradeoffs

- **Group fan-out / hot partitions:** Bade group (1000+ members) me ek message N copies ko fan-out karta hai → write amplification aur Notification Service spike. Mitigation: fan-out ko async queue (Kafka) pe daalo, aur very large groups ke liye fan-out-on-read consider karo. Ek super-active group ek hot partition bhi ban sakta hai — large groups ke liye partitioning strategy revisit karo.
- **Stateful chat servers + reconnect storms:** Server crash hone pe usske saare clients ek saath reconnect karte hain → thundering herd. Mitigation: jittered exponential backoff on reconnect, capacity headroom, aur fast Session Service updates.
- **Presence at scale:** Har user ka frequent heartbeat × 10M concurrent = massive write load on presence store. Mitigation: heartbeat interval badhao (5–10s), presence ko eventually-consistent rakho, aur "last-seen" ko approximate karo — exact precision yahan zaroori nahi.
- **Availability vs consistency:** Hum availability choose karte hain — ek message thoda out-of-order ya late aa sakta hai, but kabhi lost nahi. Strong global ordering ki cost (latency/coordination) is workload ke liye worth nahi.
- **Read receipts cost:** Har read receipt khud ek message hai → effectively traffic double. Bade groups me per-member read receipts mehenga hai; isiliye WhatsApp groups me read receipt aggregate/limited hota hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/classic-designs/conceptual_quiz_design_chat_system.md`](../../../sysd-quizzes/classic-designs/conceptual_quiz_design_chat_system.md) — `sysd-buddy quiz scaffold design-chat-system` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update design-chat-system --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — chat servers, Session Service routing, aur store-and-forward flow ka interactive diagram.
