# Counting Bits

**Category:** Bit Manipulation
**Difficulty:** easy

## Problem Statement

Given an integer `n`, return an array `ans` of length `n + 1` where `ans[i]` is the **number of 1 bits** in the binary representation of `i`, for every `i` from `0` to `n`. Aim for **O(n)** total time (one popcount per number is O(n log n)).

```
n = 5  ->  [0, 1, 1, 2, 1, 2]
            #  0=0   ->0
            #  1=1   ->1
            #  2=10  ->1
            #  3=11  ->2
            #  4=100 ->1
            #  5=101 ->2
```

## Real-World Analogy

Socho tum ek **building me har flat ki "ON lights" gin rahe ho**, flat number 0 se n tak. Har flat ko zero se ginna boring hai. Lekin ek shortcut hai: kisi bhi flat `i` ko dekho — agar tum uska **sabse right wala set bit hata do** (`i & (i-1)`), to jo chhota number `i'` bachta hai uske bulbs tum **pehle hi gin chuke ho**! To `i` ke bulbs = `i'` ke bulbs **+ 1**. Purana kaam dobara mat karo — bas table se uthao. Yeh hai **DP**: pehle ka answer reuse karo.

## Approach

**Naive:** har number pe popcount chalao → O(n log n). Chalta hai, par DP O(n) deta.

**DP recurrence (Brian Kernighan based) — `dp[i] = dp[i & (i-1)] + 1`:**

`i & (i - 1)` `i` ka lowest set bit clear karta — result hamesha `i` se chhota, to woh **already computed** hai. Usme +1 (jo bit humne abhi hataya).

```python
def count_bits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i & (i - 1)] + 1
    return dp
```

**Alternative DP — right shift / `dp[i] = dp[i >> 1] + (i & 1)`:**

`i >> 1` matlab `i` ko aadha karo (last bit gira do). Uske bits same as `i` except woh gira hua last bit — to add `i & 1`:

```python
def count_bits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

Dono O(n). Choose whichever clicks — `i >> 1` wala intuition aksar zyada natural lagta hai (har number ka half pehle aata hai).

## Complexity

- **Time:** O(n) — har `i` constant work (ek table lookup + 1 add). Total n+1 numbers.
- **Space:** O(n) for the output array (output ko extra space nahi ginte to O(1) auxiliary).

## Common Pitfalls

- **Loop `0` se shuru karke `dp[i & (i-1)]` access karna** with `i=0` → `0 & -1`... edge mess. Start from `i = 1`; `dp[0]` already `0`.
- **`i >> 1` vs `i / 2`** — Python me `/` float deta (`2.0`), index ke liye `//` ya `>>` use karo. `>>` clean hai.
- **Naive popcount ko O(n) samajh lena** — har popcount O(log i) hai, total O(n log n). DP isliye better.
- **Operator precedence** — `dp[i >> 1] + (i & 1)` me `i & 1` ko bracket me rakho; `+` ki precedence `&` se zyada hai, warna `dp[i>>1] + i` evaluate hoke phir `& 1` ho jaayega — galat.

## When to Use This Pattern

Jab **ek range [0..n] ke li` har number ka koi bit-property** chahiye aur tum chote subproblems reuse kar sakte ho → **bit DP**. Cue: "for every i from 0 to n compute ...", aur har `i` ka answer kisi chote `i'` (`i>>1` ya `i&(i-1)`) se derive hota ho. Yeh DP + bit-manipulation ka pyaara crossover hai.

## NeetCode Link

https://neetcode.io/problems/counting-bits
