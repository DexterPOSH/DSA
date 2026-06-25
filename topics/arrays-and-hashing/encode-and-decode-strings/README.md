# Encode and Decode Strings

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Design two functions: `encode(strs)` turns a list of strings into a **single string**, and `decode(s)` turns that single string back into the **original list**. The catch: the strings can contain **any** character — including the one you'd love to use as a separator. So you can't just `"#".join(strs)`, because a string itself might contain `#`.

```
encode(["neet", "code", "love", "you"])  ->  "4#neet4#code4#love3#you"
decode("4#neet4#code4#love3#you")        ->  ["neet", "code", "love", "you"]
```

## Real-World Analogy

**What Azure Event Hubs is:** Event Hubs is Azure's big-data streaming and event-ingestion service — think of it as a massive pipe that can swallow millions of events per second (telemetry, logs, clickstreams) and hand them to downstream consumers. Producers fire events in; the service durably buffers them; consumers read them back in order. To move all those events over a single TCP connection, it needs a way to pack many independent messages into one continuous byte stream — exactly our problem.

**What AMQP framing is, and why it's used:** Event Hubs speaks **AMQP 1.0** (Advanced Message Queuing Protocol), a binary wire protocol. AMQP never sends a raw message blob and hopes the receiver can find where it ends. Instead it wraps every message in a **frame**: a small fixed **header that begins with the frame's total size in bytes**, followed by the payload. The receiver's loop is dead simple — read the size field, then read *exactly* that many bytes, and you've got one complete message; repeat for the next frame. This **length-prefix framing** is used because a streamed payload can contain *any* byte, including bytes that look like a delimiter. If AMQP tried to mark message boundaries with a special separator byte, a payload that happened to contain that byte would corrupt the stream. Declaring the length up front makes each frame **self-delimiting** — the content is read by *count*, never by *scanning*, so it can hold arbitrary data safely. (TCP segments, protobuf, and HTTP's `Content-Length` all rely on this same trick.)

**The mapping:** Our `encode`/`decode` is a miniature AMQP framer. `len(s)` + `#` is the frame header (size + a tiny delimiter that only separates the *digits* from the *body*), and `s` is the payload. Decoding mirrors the AMQP receiver: read the length, then consume exactly that many characters — never search for the next `#`. That's precisely why a string containing `#` still round-trips correctly: just like an AMQP payload that contains header-looking bytes, the count tells you where it ends, so the delimiter inside the data is harmless.

## Approach

Naive idea — `"#".join(strs)` — fails because a string can contain `#` itself, making decoding ambiguous. Solution: **length-prefixing**.

**Encode:** for each string `s`, write `len(s)` + `"#"` + `s`. `#` only separates the length from the string; the length is what tells decode how much content to read, not the `#`.

**Decode:** walk with pointer `i`. First read digits until `#` — that is the length. Starting immediately after `#`, slice exactly that many characters (even if they contain `#`). Then move the pointer forward and repeat.

```python
def encode(strs):
    return "".join(f"{len(s)}#{s}" for s in strs)

def decode(s):
    res, i = [], 0
    while i < len(s):
        j = i
        while s[j] != '#':         # read the length digits
            j += 1
        length = int(s[i:j])
        word = s[j + 1 : j + 1 + length]   # exactly `length` chars
        res.append(word)
        i = j + 1 + length          # jump past this chunk
    return res
```

Pattern: **length-prefixed (self-delimiting) encoding** — the same idea used in TCP/protobuf-style wire protocols.

## Complexity

Assume the total number of characters across all strings is `N`.

- **Time:** O(N) for both encode and decode — each character is touched a constant number of times. (Length digits are small enough to ignore for this analysis.)
- **Space:** O(N) for the output (encoded string or decoded list). Extra working space is O(1) beyond the output.

## Common Pitfalls

- **Plain delimiter (`#`, `,`, space) join** — fails when a string itself contains that delimiter. Length-prefixing avoids this.
- **Reading multi-digit lengths incorrectly** — length `12` has two digits. Read **all** digits up to `#`, not just one character.
- **Treating `#` as part of the string boundary** — `#` separates the length from the content; the content slice is based on the length, not on the next `#`.
- **Empty strings** — encode `""` as `"0#"`. During decode, length `0` appends an empty word, so do not forget to handle it.
- **Pointer arithmetic off-by-one** — content starts at `j+1` (after `#`), and the next chunk starts at `j + 1 + length`.

## When to Use This Pattern

When you need to **serialize arbitrary data into one flat stream/string** and the content may contain any byte, think **length-prefixing**. This is the same technique used in network protocols, file formats, and message framing: "first state how much data is coming, then send exactly that much data." It is a clean way to avoid delimiter-escaping complexity.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of length-prefixed encoding and decoding.

## NeetCode Link

https://neetcode.io/problems/string-encode-and-decode
