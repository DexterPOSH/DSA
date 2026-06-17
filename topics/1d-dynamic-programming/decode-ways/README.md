# Decode Ways

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

A message of digits is encoded with the mapping `'A' -> "1"`, `'B' -> "2"`, ..., `'Z' -> "26"`. Given a string `s` of digits, return the **number of ways** to decode it back into letters.

```
"12"    ->  2     ("AB" = 1,2   or  "L" = 12)
"226"   ->  3     ("BZ"=2,26  "VF"=22,6  "BBF"=2,2,6)
"06"    ->  0     (leading zero — "06" is invalid, and "6" alone can't pair)
```

## Real-World Analogy

Socho ek lambi sadak hai jisme har step pe tum **ya to 1 ghar aage jaa sakte ho ya 2 ghar** (jaise climbing stairs). Lekin ek twist: kuch jumps **blocked** hain. 

- Ek single digit tabhi valid hai jab wo `1-9` ho (`'0'` akela koi letter nahi banta).
- Do digits ka jump tabhi valid hai jab wo `"10"-"26"` ke beech ho (`"27"` ya `"05"` invalid).

Tumhe sadak ke end tak pahunchne ke total raaste ginne hain. Kisi position pe pahunchne ke raaste = pichhli position se aane wale raaste (agar single-step valid) + uss-se-pehli position se aane wale raaste (agar two-step valid). Yeh **Fibonacci-jaisa** recurrence hai, bas validity checks ke saath.

## Approach

**Pattern: 1-D DP (Climbing-Stairs cousin).** Let `dp[i]` = number of ways to decode the first `i` characters (`s[:i]`). Answer is `dp[n]`.

- `dp[0] = 1` — empty string ka ek (khaali) decoding hai. Base case.
- `dp[1] = 1` if `s[0] != '0'` else `0`.
- For each `i` from 2 to n:
  - **One-digit jump:** agar `s[i-1] != '0'`, to `dp[i] += dp[i-1]` (current digit ek letter).
  - **Two-digit jump:** agar `"10" <= s[i-2:i] <= "26"`, to `dp[i] += dp[i-2]` (last two digits milke ek letter).

```python
def numDecodings(s: str) -> int:
    if not s or s[0] == '0':
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1                       # empty + first valid char

    for i in range(2, n + 1):
        one = s[i-1]                        # last single digit
        two = s[i-2:i]                      # last two digits
        if one != '0':
            dp[i] += dp[i-1]                # single-digit decode
        if '10' <= two <= '26':
            dp[i] += dp[i-2]                # two-digit decode
    return dp[n]
```

**Space-optimized (O(1)):** sirf `dp[i-1]` aur `dp[i-2]` chahiye hote hain — do variables se kaam ban jaata hai, poora array zaroori nahi.

```python
def numDecodings(s: str) -> int:
    if not s or s[0] == '0':
        return 0
    prev2, prev1 = 1, 1                     # dp[i-2], dp[i-1]
    for i in range(1, len(s)):
        cur = 0
        if s[i] != '0':
            cur += prev1
        if '10' <= s[i-1:i+1] <= '26':
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1
```

## Complexity

- **Time:** O(n) — single pass, har position pe O(1) constant work (do checks).
- **Space:** O(n) for the dp array, ya **O(1)** with the two-variable rolling version.

## Common Pitfalls

- **Zero handling** — `'0'` akela invalid hai. `"30"` invalid (`3` ke baad `0` na single na valid pair `"30">26`). `"10"` aur `"20"` valid (sirf two-digit decode). Yeh edge cases sabse zyada bugs deti hain.
- **Two-digit range string-compare** — `'10' <= two <= '26'` Python me string comparison hai jo yahan lexicographically sahi kaam karta (same length). Lekin clarity ke liye `10 <= int(two) <= 26` bhi theek.
- **dp[0] = 1 ka matlab** — empty prefix ka "ek khaali decoding" — yeh base case zaroori hai warna two-digit decodes ka count off ho jaata.
- **Leading zero early return** — `s[0] == '0'` to seedha `0` return, warna `dp[1]` galat init hota.
- **Off-by-one in indexing** — `dp[i]` `s[:i]` ko represent karta (1-indexed prefix length), `s[i-1]` current char. Yeh mapping consistent rakho.

## When to Use This Pattern

"Number of ways to ... where each step has 1 or 2 choices" → **1-D DP, Fibonacci-style recurrence** (`dp[i] = dp[i-1] + dp[i-2]` with validity gates). Cousins: **Climbing Stairs**, **Min Cost Climbing Stairs**, **House Robber**. Cue: sequential decision jahan har position ka answer pichhle 1-2 positions pe depend karta hai.

## NeetCode Link

https://neetcode.io/problems/decode-ways
