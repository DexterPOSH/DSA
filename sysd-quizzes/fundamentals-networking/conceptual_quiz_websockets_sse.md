# WebSockets & SSE — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update websockets-sse --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines, what is the core difference between WebSockets and Server-Sent Events (SSE)?

**Ideal answer:**
- WebSocket = full-duplex / bidirectional persistent connection — client aur server dono kabhi bhi message bhej sakte hain.
- SSE = unidirectional, server → client only — server client ko events push karta hai over a long-lived HTTP response.
- WebSocket apna own protocol (`ws://`/`wss://`) chalata hai after an HTTP Upgrade; SSE plain HTTP (`text/event-stream`) par hi rehta hai.
- Bonus: SSE built-in auto-reconnect deta hai; WebSocket nahi.

## Q2 (core)
Walk me through how a WebSocket connection gets established, and how it differs from a normal HTTP request after that.

**Ideal answer:**
- Starts as a normal HTTP/1.1 GET with headers `Upgrade: websocket`, `Connection: Upgrade`, and a random `Sec-WebSocket-Key`.
- Server replies `101 Switching Protocols` with `Sec-WebSocket-Accept` (SHA-1 of key + fixed GUID) to confirm.
- After the handshake, the same TCP connection stops speaking HTTP and switches to the WebSocket protocol.
- Data now flows as small bidirectional **frames** (header ~2–14 bytes), not request/response pairs — much lower per-message overhead than full HTTP headers.
- Connection is persistent; keep-alive via ping/pong frames.

## Q3 (tradeoff)
You only need the server to push live updates to clients (no client → server messages). Why might SSE be a better choice than WebSockets here, and what's one limitation of SSE you'd watch out for?

**Ideal answer:**
- SSE runs over plain HTTP — no protocol upgrade — so it works naturally with existing HTTP load balancers, proxies, auth middleware, and HTTP/2; less infra complexity.
- Built-in auto-reconnect with `Last-Event-ID` resume; with WebSocket you'd implement reconnect/backoff/replay yourself.
- WebSocket's full-duplex power is wasted for pure server-push, and stateful connections are more expensive/complex to scale.
- Limitations to watch: SSE is unidirectional (client can't send over it); text/UTF-8 only (binary needs base64); and the HTTP/1.1 ~6-connections-per-domain limit (mitigated by HTTP/2).

## Q4 (gotcha)
A candidate says "WebSockets are basically always the better choice because they're more powerful." What's wrong with that reasoning, and what scaling problem do both WebSockets and SSE share?

**Ideal answer:**
- "More powerful" ≠ "always better" — WebSocket adds cost/complexity: stateful persistent connections consume server memory + file descriptors, need protocol-upgrade-aware infra, and require you to build reconnect logic. For pure server-push, SSE is simpler, cheaper, and HTTP-native.
- Shared scaling problem: both hold **long-lived connections pinned to a specific server instance**. This forces sticky sessions / connection-aware routing.
- To broadcast a message to clients connected across multiple instances, you need a Pub/Sub fan-out layer (e.g., Redis Pub/Sub) so a message arriving on one server reaches clients on other servers.
- Also: idle connections get killed by proxy/LB timeouts, so you need ping/pong (WS) or heartbeat comment lines (SSE).

## Q5 (applied)
ChatGPT-style apps stream their answer token-by-token as it's generated. Would you pick WebSockets or SSE for that token stream, and why? When would you switch to the other?

**Ideal answer:**
- For token streaming, **SSE is a strong fit** — it's purely server → client, plays well with plain HTTP/HTTP-2, and gives auto-reconnect; OpenAI's streaming API uses the SSE `text/event-stream` format. The initial prompt is just a normal HTTP request; the response is the SSE stream.
- Lower infra overhead than WebSocket for a one-directional stream; no need for full-duplex.
- Switch to **WebSocket** when you need frequent low-latency client → server messages on the same channel — e.g., interactive/collaborative sessions, live multiplayer, chat with typing indicators, or bidirectional voice/data where the client constantly sends too.
- Reasonable to mention that either can work; the deciding factor is whether the client needs to push frequently over the same connection.
</content>
