# TCP vs UDP

**Track:** Building Blocks
**Category:** Fundamentals & Networking

## What It Is

TCP ek connection-oriented, reliable, ordered transport protocol hai jo handshake, acknowledgements aur retransmission se guaranteed delivery deta hai, jabki UDP ek connectionless, "fire-and-forget" transport hai jo minimal overhead pe packets bhejta hai bina delivery, order ya duplicate ki koi guarantee diye.

## Real-World Analogy

Socho TCP ek **registered courier (jaise Blue Dart with proof-of-delivery)** hai. Pehle courier wala call karke confirm karta hai ki aap ghar pe ho (handshake), phir har parcel deliver karne pe aapse signature leta hai (acknowledgement). Agar koi parcel kho jaaye, wo dobara bhejta hai (retransmission). Aur agar aapne 3 boxes order kiye to wo guarantee karta hai ki box 1, phir 2, phir 3 isi order mein milein (ordering). Reliable hai — par har step pe confirmation aur tracking ka overhead lagta hai, isliye thoda slow.

UDP ek aam **postcard / pamphlet drop** jaisa hai. Postman bas aapke letterbox mein daal ke chala jaata hai — na koi signature, na confirmation ki mila ki nahi, na ye guarantee ki 5 postcards usi order mein pahunchein. Agar ek kho gaya to kho gaya, koi resend nahi. Lekin kyunki koi tracking-overhead nahi, ye bahut fast aur lightweight hai. Live cricket commentary jaisa — agar ek second ka audio packet drop ho gaya to use dobara bhejne ka koi point nahi, tab tak to match aage badh chuka hoga.

## How It Works

### TCP — reliability ki machinery

1. **3-way handshake (connection setup):** Client `SYN` bhejta hai, server `SYN-ACK` se reply karta hai, client `ACK` se confirm karta hai. Iske baad hi data flow shuru hota hai. Isme ek full round-trip ka cost lagta hai — agar RTT (round-trip time) 50 ms hai, to actual data bhejne se pehle hi ~50 ms ka setup delay aa jaata hai.
2. **Sequence numbers + ACKs:** Har byte ka ek sequence number hota hai. Receiver bheje gaye data ke liye ACK wapas bhejta hai. Agar sender ko time pe ACK nahi milta (timeout, ya 3 duplicate ACKs), to wo us segment ko **retransmit** karta hai. Yahi reliability ka core hai.
3. **In-order delivery + head-of-line blocking:** Receiver bytes ko sequence number ke order mein hi application ko deliver karta hai. Agar segment 5 kho gaya par 6,7,8 aa gaye, to 6,7,8 buffer mein ruke rehte hain jab tak 5 retransmit hoke nahi aata — ise **head-of-line (HOL) blocking** kehte hain.
4. **Flow control (sliding window):** Receiver apni `receive window` advertise karta hai (kitna data wo buffer kar sakta hai). Sender us window se zyada un-ACKed data nahi bhejta — taaki slow receiver overwhelm na ho.
5. **Congestion control:** Algorithms jaise slow start, congestion avoidance, CUBIC (Linux default), ya BBR network ke load ke hisaab se sending rate adjust karte hain — packet loss ya delay dekh ke window shrink/grow karte hain. Ye Internet ko collapse hone se bachata hai.
6. **Connection teardown:** `FIN`/`ACK` exchange se connection clean-up hota hai.

**Header size:** TCP header minimum **20 bytes** (options ke saath zyada).

### UDP — minimalism

1. **No handshake:** Application bas `sendto()` call karke datagram bhej deti hai. Koi connection setup nahi, isliye zero setup RTT.
2. **No ACK, no retransmission, no ordering:** Packet bheja, bhool gaye. Reliability, ordering, dedup — ye sab agar chahiye to **application layer** pe khud build karna padta hai (jaise QUIC ne kiya).
3. **Header size sirf 8 bytes:** source port, destination port, length, checksum — bas. Per-packet overhead bahut kam.
4. **Message-oriented (datagram boundaries):** TCP ek byte-stream hai (boundaries nahi), par UDP har `sendto()` ko ek discrete datagram ki tarah preserve karta hai. Ek `recvfrom()` = ek datagram.

**Latency intuition:** Same-region servers ke beech ek extra round-trip ~1-5 ms add karta hai; cross-continent ~100-150 ms. TCP ka handshake yahi extra RTT(s) cost karta hai, jo UDP bachata hai.

## Tradeoffs & Variants

- **Reliability vs latency:** TCP reliable hai par handshake + retransmission + in-order delivery ki wajah se tail latency zyada ho sakti hai. UDP fast aur low-overhead hai par delivery aapki problem hai.
- **Head-of-line blocking:** TCP mein ek lost packet poore stream ko block kar deta hai. Ye real-time media ke liye disaster hai. UDP mein har datagram independent hai — ek drop hone se baaki affect nahi hote.
- **Connection state:** TCP per-connection state rakhta hai (sequence numbers, windows, buffers) — server pe memory aur C10K-type scaling concerns aate hain. UDP stateless hai, isliye ek server lakhon clients ko sasta serve kar sakta hai (DNS isi wajah se UDP use karta hai).
- **QUIC (the modern hybrid):** QUIC UDP ke upar bana hai (HTTP/3 ka transport). Wo UDP ke datagram model pe khud reliability, ordering, congestion control, aur encryption (TLS 1.3 built-in) implement karta hai — par per-stream, taaki ek stream ka loss doosri streams ko block na kare (TCP ka HOL-blocking problem solve karta hai). Plus 0-RTT/1-RTT connection setup se handshake bhi tez.
- **Multicast/broadcast:** UDP one-to-many (multicast) support karta hai; TCP strictly point-to-point hai.

## When To Use It

**TCP choose karo jab correctness > speed:**
- Web (HTTP/1.1, HTTP/2), REST/gRPC APIs, file transfer, database connections (Postgres/MySQL wire protocols), email (SMTP), SSH — yahan ek byte bhi kho jaaye to kaam bigad jaata hai.

**UDP choose karo jab speed/freshness > perfect delivery, ya jab app khud reliability handle karti hai:**
- **DNS** — chhota request/response, fast, stateless (largely UDP; bade responses ke liye TCP fallback).
- **Real-time media** — VoIP, video calls (Zoom, WebRTC/RTP), live streaming. Purana data resend karna useless hai; ek dropped audio frame ko skip karna better hai.
- **Online gaming** — player position updates; latest position matter karta hai, stale one nahi.
- **Telemetry/metrics** — high-volume fire-and-forget (jaise StatsD).
- **QUIC / HTTP/3** — Google, Cloudflare, YouTube isi pe chal rahe hain: UDP ki flexibility + apni reliability layer.

## Common Interview Gotchas

- **"UDP unreliable hai isliye hamesha kharaab" — galat:** UDP intentionally minimal hai. Real-time apps ke liye "unreliable but fast" exactly chahiye hota hai. Aur QUIC dikhata hai ki UDP ke upar TCP-grade reliability bhi build ho sakti hai, with better control.
- **"TCP packets ki ordering guarantee deta hai" — precise raho:** TCP **byte-stream** ko in-order deliver karta hai; ye message boundaries preserve nahi karta. Agar aapne 2 alag `send()` kiye, receiver ek hi `recv()` mein dono ka mix dekh sakta hai. Boundaries chahiye to khud framing (length-prefix/delimiter) lagao. UDP datagram boundaries preserve karta hai.
- **Head-of-line blocking ka source samjho:** TCP-level HOL blocking ek lost segment ki wajah se hota hai. HTTP/2 ne multiple streams ek TCP connection pe daale, par TCP-level HOL blocking still hit karta hai — isiliye HTTP/3 (QUIC over UDP) per-stream reliability deta hai.
- **Handshake cost ko underestimate mat karo:** "Bas ek connection" lagta hai, par high-RTT links (mobile, cross-continent) pe TCP 3-way handshake + TLS handshake milke 2-3 RTTs = 300+ ms add kar sakte hain pehle byte se pehle. Isiliye QUIC ka 0-RTT/1-RTT ek bada deal hai.
- **"UDP mein checksum nahi hota" — galat:** UDP header mein checksum hota hai (IPv4 pe optional, IPv6 pe mandatory). Wo corruption **detect** karta hai (corrupt datagram drop ho jaata hai), par recover/retransmit nahi karta.
- **Reliability ≠ security:** TCP reliable delivery deta hai, encryption nahi. Encryption TLS (TCP) ya QUIC's built-in TLS 1.3 se aata hai. Inko alag rakho.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_tcp_vs_udp.md`](../../../sysd-quizzes/fundamentals-networking/conceptual_quiz_tcp_vs_udp.md) — `sysd-buddy quiz scaffold tcp-vs-udp` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update tcp-vs-udp --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — TCP 3-way handshake, ACK/retransmission flow, aur TCP vs UDP header/overhead ka side-by-side diagram.
