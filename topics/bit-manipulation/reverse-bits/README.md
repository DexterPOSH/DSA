# Reverse Bits

**Category:** Bit Manipulation
**Difficulty:** easy

## Problem Statement

Reverse the bits of a given **32-bit unsigned integer**. The bit at position 0 goes to position 31, position 1 to position 30, and so on.

```
Input:  00000010100101000001111010011100   (43261596)
Output: 00111001011110000010100101000000   (964176192)
```

(Mirror the 32-bit string left-to-right.)

## Real-World Analogy

Socho ek **32 logon ki line hai** jo ek conveyor belt pe khade hain — har banda ek bit (0 ya 1). Tumhe poori line **ulti** karni hai: pehla banda last position pe, last banda first position pe. Tum ek-ek karke line ke **right wale banda** ko uthate ho aur use ek nayi khaali line ke **left** me daalte ho, phir nayi line ko ek kadam right shift kar dete ho jagah banane ke liye. 32 baar yeh karne ke baad nayi line ekdum mirror-image ban jaati hai.

## Approach

Ek `result = 0` lo. 32 baar: `n` ka **lowest bit nikalo** (`n & 1`), use `result` ke andar daalo, phir `result` ko **left shift** karke agle bit ke liye jagah banao, aur `n` ko **right shift** karke uska agla bit ready karo.

Trick: kyunki hum `result` ko har step **left** shift karte hain par `n` se bits **right** se nikalte hain, automatically positions reverse ho jaati hain — first-out bit sabse zyada left shifts khaata, to wo MSB ban jaata.

```python
def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)  # result me jagah banao, n ka last bit chipkao
        n >>= 1                            # n ka agla bit ready
    return result
```

Step-by-step ek chote 4-bit example pe (`1011` → reverse `1101`):
- start `result=0000`, take `1` → `result=0001`
- take `1` → `result=0011`
- take `0` → `result=0110`
- take `1` → `result=1101`  ✅

> **One-liner (Python):** `int(format(n, "032b")[::-1], 2)` — string ko 32-bit me pad karo, reverse karo, parse karo. Cute, par interview me bit-loop hi samjhao.

## Complexity

- **Time:** O(1) — exactly 32 iterations, input size pe depend nahi.
- **Space:** O(1) — bas `result` integer.

## Common Pitfalls

- **`<<` aur `>>` ko ulta lagana** — `result` ko **left** shift karna hai (jagah banane ke liye, MSB-direction me fill), `n` ko **right** (consume lowest bit). Swap karoge to bits idhar-udhar.
- **32 ke alawa loop count** — problem fixed 32-bit hai; kam/zyada iterations se positions galat.
- **Order: shift pehle ya OR pehle?** — `(result << 1) | (n & 1)` me **shift pehle**, phir OR. Agar pehle OR karoge to last placed bit double-shift ho jaayega.
- **Signed-int overflow (Java/C):** `result` 32-bit signed me overflow kar sakta — wahan `>>>` / unsigned / `& 0xFFFFFFFF` ka dhyaan. Python big-int me yeh problem nahi.
- **Leading zeros ko bhulna** — input ko poore 32 bits maano; `n` jaldi 0 ho jaaye to bhi loop 32 baar chalao, warna trailing zeros (jo result me leading nahi, balki shift count me matter karte) miss ho jaate.

## When to Use This Pattern

Jab **bit-by-bit construct/transform** karna ho — "build result by peeling bits off input and shoving into output" → `(result << 1) | (n & 1)` ka extract-and-place idiom. Cue: reverse bits, binary↔decimal conversions, serialization of flags, bit-reversal permutation (FFT). Fixed-width pe hamesha O(1).

## NeetCode Link

https://neetcode.io/problems/reverse-bits
