# WebSockets & SSE

**Track:** Building Blocks
**Category:** Fundamentals & Networking

## What It Is

WebSockets ek full-duplex, bidirectional persistent connection deta hai jahan client aur server dono kabhi bhi message bhej sakte hain, jabki Server-Sent Events (SSE) ek lightweight, unidirectional stream hai jisme server plain HTTP ke upar client ko continuously events push karta rehta hai.

## Real-World Analogy

Socho aap kisi se baat kar rahe ho.

**WebSocket ek phone call jaisa hai.** Ek baar call connect ho gaya (handshake), to dono log freely, kabhi bhi, ek dusre se bol sakte hain — koi baar baar dial nahi karta. Line khuli rehti hai jab tak koi hang up na kare. Ye bidirectional hai aur low-latency — jaise hi aap bolte ho, dusra turant sunta hai.

**SSE ek news radio channel jaisa hai.** Aapne radio tune kiya (ek HTTP request bheja), aur ab station continuously aapko updates broadcast karta rehta hai. Aap (client) sirf sun sakte ho — radio mein wapas bol nahi sakte. Agar aapko station ko kuch bhejna hai, to aapko alag se phone (ek normal HTTP request) karna padega. Aur agar signal kat jaaye, to aapka radio automatically dobara wahi station pakad leta hai (auto-reconnect) — yahi SSE ka built-in `Last-Event-ID` reconnect behaviour hai.

Toh rule of thumb: dono taraf se constant baat-cheet chahiye → phone call (WebSocket). Sirf server se ek-tarfa updates chahiye → radio (SSE).

## How It Works

### WebSocket

1. **HTTP Upgrade handshake:** Connection ek normal HTTP/1.1 GET request se shuru hota hai jisme special headers hote hain: `Upgrade: websocket`, `Connection: Upgrade`, aur ek random `Sec-WebSocket-Key`. Server agree karta hai to `101 Switching Protocols` return karta hai with `Sec-WebSocket-Accept` (jo key ka SHA-1 hash hota hai ek fixed GUID ke saath). Is point ke baad wahi TCP socket HTTP nahi, balki WebSocket protocol (`ws://` ya secure `wss://`) bolta hai.

2. **Frames, not requests:** Handshake ke baad data HTTP request-response mein nahi, balki chhote **frames** mein flow hota hai. Har frame ka overhead bahut chhota hota hai — typically **2 se 14 bytes** ka header (vs HTTP request ke saikdo bytes of headers). Isiliye high-frequency messaging mein WebSocket bahut efficient hai.

3. **Bidirectional, persistent:** Ek hi connection par dono direction mein messages async chal sakte hain. Latency ek round trip ke order mein hoti hai — same-region typically **single-digit se low double-digit milliseconds** — kyunki naya connection setup ya TCP/TLS handshake har message pe nahi karna padta.

4. **Keep-alive:** Connection zinda rakhne ke liye protocol-level **ping/pong** frames bheje jaate hain (jaise har 30s), taaki idle connections aur dead peers detect ho sakein, aur beech ke proxies/load balancers connection ko timeout pe na maar dein.

### SSE

1. **Ek long-lived HTTP response:** Client ek normal GET request bhejta hai with header `Accept: text/event-stream`. Server `Content-Type: text/event-stream` ke saath response **kabhi close nahi karta** — wo response body ko open rakh ke chunks mein events likhta rehta hai (HTTP chunked transfer).

2. **Text event format:** Har event simple `text/event-stream` format mein hota hai — lines jaise `data: hello\n\n`. Optional fields: `event:` (event type), `id:` (event ID), aur `retry:` (reconnect delay ms mein). Double newline (`\n\n`) ek event ko terminate karta hai.

3. **Browser API + auto-reconnect:** Browser mein `EventSource` API isko handle karti hai. Sabse bada feature: agar connection drop ho jaaye, browser **automatically reconnect** karta hai, aur last received `id:` ko `Last-Event-ID` request header mein bhejta hai — server wahin se resume kar sakta hai. WebSocket mein ye reconnect logic aapko khud likhna padta hai.

4. **Unidirectional:** Data sirf server → client flow hota hai. Client ko server ko kuch bhejna ho to alag se ek regular HTTP request karni padti hai. SSE text-only hai (UTF-8); binary bhejna ho to base64 encode karna padta hai.

## Tradeoffs & Variants

- **Directionality:** WebSocket = full-duplex (dono taraf). SSE = server → client only. Agar client se frequent uplink messages chahiye (jaise chat typing, multiplayer moves), WebSocket. Agar sirf server push chahiye (live feed, notifications, progress), SSE simpler hai.

- **Protocol & infra:** SSE plain HTTP ke upar chalta hai — koi protocol upgrade nahi, to existing HTTP load balancers, proxies, auth middleware, aur HTTP/2 ke saath naturally kaam karta hai. WebSocket ko `Upgrade` handshake aur `wss://` ko support karne wale infra ki zaroorat hoti hai; kuch corporate proxies WebSocket ko block/break kar dete hain.

- **HTTP/1.1 connection limit (SSE ka classic gotcha):** HTTP/1.1 par browser ek domain ke liye max **6 concurrent connections** allow karta hai. SSE ek connection consume kar leta hai, to multiple tabs khulne par limit hit ho sakti hai. HTTP/2 (jahan SSE multiplexed streams par chalta hai) ye problem solve kar deta hai. WebSocket is 6-connection limit ke under nahi aata.

- **Auto-reconnect:** SSE built-in deta hai (`EventSource` + `Last-Event-ID`). WebSocket mein reconnect, backoff, aur message replay khud implement karna padta hai.

- **Binary support:** WebSocket text aur binary dono bhej sakta hai. SSE sirf UTF-8 text — binary ke liye base64 (overhead).

- **Long-polling (fallback variant):** Dono se purana approach — client request bhejta hai, server response hold karta hai jab tak data na ho, phir client turant naya request bhejta hai. Higher latency aur overhead, par sabse compatible. Aaj mostly fallback ke roop mein use hota hai jab WebSocket/SSE available na ho.

## When To Use It

- **WebSocket — bidirectional, low-latency, high-frequency:**
  - Chat / messaging (Slack, WhatsApp Web).
  - Multiplayer games aur collaborative editing (Figma, Google Docs cursors).
  - Live trading / order books jahan dono taraf fast updates chahiye.

- **SSE — server-push, unidirectional, simplicity matters:**
  - Live notifications, news feeds, sports scores, stock tickers (display-only).
  - Progress / status streams (build logs, deployment progress).
  - **LLM token streaming** — ChatGPT-style "type hote hue" responses aksar SSE par hote hain (OpenAI ki streaming API SSE format use karti hai), kyunki ye purely server → client token stream hai.

- **Pattern recognition (interview):** "Client ko server se actively kuch bhejna hai?" — agar haan, WebSocket. "Sirf server ko push karna hai aur simple/HTTP-friendly chahiye?" — SSE. "Polling kaam kar jaayega aur scale low hai?" — short/long polling theek hai.

## Common Interview Gotchas

- **"WebSocket hamesha better hai" — galat:** WebSocket zyada powerful hai, par stateful persistent connections server ko expensive padti hain (har connection memory + file descriptor consume karta hai), aur infra complexity (sticky sessions, scaling, reconnect) zyada hai. Sirf server-push use case ke liye SSE simpler, cheaper aur HTTP-native choice hai. Over-engineering se bacho.

- **SSE bidirectional nahi hai:** Common mistake — SSE par client server ko message nahi bhej sakta. Uplink ke liye alag HTTP request chahiye. Agar bidirectional chahiye, SSE wrong tool hai.

- **HTTP/1.1 ka 6-connection limit:** Bahut log bhool jaate hain ki ek domain par browser sirf ~6 SSE/HTTP-1.1 connections rakh sakta hai. Multiple tabs → limit exhaust. Fix: HTTP/2 multiplexing, ya ek shared connection (SharedWorker) sab tabs ke liye.

- **Stateful scaling problem (load balancing):** WebSocket aur SSE dono long-lived connections hain, to wo ek specific server instance se bandhi hoti hain. Aapko sticky sessions / connection-aware routing chahiye, aur cross-instance broadcast ke liye ek Pub/Sub layer (jaise Redis Pub/Sub) chahiye taaki ek server par aaya message dusre server se connected clients tak pahunche. "Ek WebSocket server scale kaise karoge?" ka jawaab yahi hai.

- **Load balancer / proxy timeouts:** Idle long-lived connections ko beech ke proxies/LBs maar sakte hain. Isiliye WebSocket ping/pong aur SSE heartbeat/comment lines (`: keepalive\n\n`) bhejna padta hai connection alive rakhne ke liye.

- **WebSocket reconnect khud likhna padta hai:** Log assume karte hain WebSocket bhi SSE jaisa auto-reconnect karta hai — nahi. Drop hone par reconnect + backoff + missed-message replay aapki responsibility hai.

- **`wss://` (TLS) prefer karo:** Plain `ws://` ko corporate proxies aksar todte hain; `wss://` (TLS-wrapped) zyada reliably proxies/firewalls ke through pass hota hai aur secure bhi hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_websockets_sse.md`](../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_websockets_sse.md) — `sysd-buddy quiz scaffold websockets-sse` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update websockets-sse --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — WebSocket handshake/frames vs SSE event-stream ka side-by-side interactive diagram.
</content>
</invoke>
