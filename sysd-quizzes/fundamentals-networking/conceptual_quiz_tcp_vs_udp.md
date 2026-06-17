# TCP vs UDP — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update tcp-vs-udp --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines, define TCP and UDP and name the single biggest difference between them.

**Ideal answer:**
- TCP = connection-oriented, reliable, ordered, byte-stream transport (handshake + ACKs + retransmission).
- UDP = connectionless, "fire-and-forget" datagram transport with no delivery/order/dedup guarantees.
- Biggest difference: TCP guarantees reliable, in-order delivery (at the cost of overhead/latency); UDP does not (but is lightweight and fast).

## Q2 (core)
Walk through what happens before and during a TCP data transfer that makes it "reliable." Why does UDP not pay these costs?

**Ideal answer:**
- 3-way handshake (SYN → SYN-ACK → ACK) sets up the connection — costs ~1 RTT before any data.
- Sequence numbers per byte; receiver sends ACKs; sender retransmits on timeout or 3 duplicate ACKs.
- In-order delivery to the application (buffering out-of-order segments).
- Flow control (sliding receive window) and congestion control (slow start / CUBIC / BBR) adjust send rate.
- UDP skips all of this: no handshake, no ACK, no retransmission, no ordering — just `sendto()` an 8-byte-header datagram. That's why it's lower overhead/latency but unreliable.

## Q3 (tradeoff)
Explain head-of-line (HOL) blocking in TCP and why it makes plain TCP a poor fit for real-time audio/video. How does QUIC address it?

**Ideal answer:**
- TCP delivers bytes strictly in order, so if one segment is lost, later segments that already arrived are held in the buffer until the lost one is retransmitted — that stall is HOL blocking.
- For real-time media this is bad: retransmitting stale audio/video data is useless (the moment has passed), and the stall adds latency; dropping/skipping a frame is better than waiting.
- QUIC runs over UDP and implements reliability per-stream, so a loss in one stream doesn't block other streams; it also has faster (0-RTT/1-RTT) setup. (Bonus: HTTP/3 = QUIC; this is why HTTP/2-over-TCP still suffered TCP-level HOL blocking.)

## Q4 (gotcha)
A candidate says: "TCP guarantees that each message I send arrives as a separate, ordered message, and UDP has no checksum so it can't detect corruption." What's wrong with both claims?

**Ideal answer:**
- TCP is a byte-stream, not message-oriented — it preserves byte order but NOT message boundaries. Two `send()` calls can arrive in one `recv()` (or be split); the app must do its own framing (length-prefix/delimiter). UDP is the one that preserves datagram boundaries.
- UDP DOES have a checksum (optional on IPv4, mandatory on IPv6). It detects corruption — corrupt datagrams are dropped — but it does not recover/retransmit. So "UDP can't detect corruption" is false; "UDP can't repair corruption" would be correct.

## Q5 (applied)
You're designing the transport for (a) a DNS resolver, (b) a multiplayer game's player-position updates, and (c) a banking REST API. Pick TCP or UDP for each and justify.

**Ideal answer:**
- (a) DNS → mostly UDP: tiny stateless request/response, low latency, server scales to many clients without per-connection state; falls back to TCP for large responses / zone transfers.
- (b) Game position updates → UDP: only the latest position matters, stale updates are worthless, and HOL blocking / retransmission would add harmful latency; the app sends frequent updates so loss is tolerable.
- (c) Banking REST API → TCP: correctness is non-negotiable, every byte must arrive in order, and it runs over TLS-on-TCP (or HTTP/3/QUIC); reliability + ordering outweigh the handshake/overhead cost.
- Strong answers note the general rule: TCP when correctness > speed; UDP when freshness/latency > perfect delivery or when the app builds its own reliability (e.g., QUIC).
