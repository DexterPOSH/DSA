# Number of 1 Bits

**Category:** Bit Manipulation
**Difficulty:** easy

## Problem Statement

Given an unsigned integer `n`, return the number of `1` bits it has in its binary representation (also called the **Hamming weight** / popcount).

```
11        ->  3      # binary 1011 has three 1s
128       ->  1      # binary 10000000 has one 1
4294967293 -> 31     # binary is 31 ones and one 0
```

## Real-World Analogy

**What Azure Service Bus is:** Azure Service Bus is Azure's managed messaging service for reliable queues and publish/subscribe topics. It lets systems exchange messages without both sides being online at the same time, while Azure handles brokered delivery and access control.

**What a Shared Access Policy permission mask is, and why it's used:** A Service Bus Shared Access Policy defines SAS authorization rights such as Listen, Send, and Manage. Those rights can be modeled as a compact permission mask where each 1 bit means a specific right is enabled. The mask exists so permission checks and audits are fast: inspect bit positions instead of parsing a longer permissions structure every time.

**The mapping:** Counting 1 bits is like auditing how many Service Bus rights are enabled in one policy mask. A simple loop checks every possible flag slot, while Brian Kernighan's `n & (n - 1)` clears exactly the lowest enabled right each pass. The key insight is that the optimized loop runs once per enabled permission, not once per possible permission slot.

## Approach

**Approach 1 — har bit check karo (simple, fixed 32 loops):**

```python
def hamming_weight(n):
    count = 0
    for _ in range(32):
        count += n & 1   # last bit 1 hai?
        n >>= 1           # right shift, agla bit aage le aao
    return count
```

**Approach 2 — Brian Kernighan's trick (sirf set-bits jitni baar):**

Key insight: `n & (n - 1)` har baar **sabse rightmost set bit ko clear** kar deta hai. `n - 1` us rightmost 1 ko 0 banata aur uske aage ke sare 0 ko 1 — phir `&` lene se woh bit aur uske neeche sab wipe ho jaate. Loop tab tak chalao jab tak `n` zero na ho:

```python
def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1     # lowest set bit hatao
        count += 1
    return count
```

Yeh sirf utni baar loop karta jitne 1 bits hain — sparse numbers pe bahut tez.

> Why `n & (n-1)` works, ek example: `n = 12 = 1100`. `n-1 = 1011`. `1100 & 1011 = 1000` — rightmost set bit (position 2) gaya. Repeat: `1000 & 0111 = 0000`. Do steps → do set bits. 

## Complexity

- **Time:** O(1) effectively — fixed 32-bit integer, max 32 iterations (Kernighan: O(set-bits) ≤ 32).
- **Space:** O(1) — bas ek counter.

## Common Pitfalls

- **Signed shift ka jhol (Java/C):** in languages me `>>` sign-extend karta — leading 1s aate rahenge, infinite loop. Wahan `>>>` (unsigned shift) use karo ya mask lagao. Python me integers arbitrary-precision hain, koi issue nahi.
- **Brian Kernighan ka exact form bhulna** — `n & (n - 1)` (clear lowest set bit) vs `n & -n` (isolate lowest set bit) — dono alag hain. Counting ke liye pehla wala.
- **`for` me condition `n` daalna par shift na karna** — infinite loop. Har iteration me `n >>= 1` ya `n &= n-1` zaroori.
- **Built-in pe reliance** — `bin(n).count('1')` ya `n.bit_count()` chalega, par interview me trick samjhana expected hai.

## When to Use This Pattern

Jab **set bits ginnne / toggle / clear** karna ho → `n & (n-1)` (clear lowest), `n & -n` (isolate lowest), `n & 1` + shift (read bits) ka toolkit yaad rakho. Cue: "Hamming weight", "popcount", "count bits", "is power of two" (`n & (n-1) == 0`).

## NeetCode Link

https://neetcode.io/problems/number-of-one-bits
