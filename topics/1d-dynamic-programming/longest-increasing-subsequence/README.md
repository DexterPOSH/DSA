# Longest Increasing Subsequence

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, return the length of the **longest strictly increasing subsequence**. A subsequence keeps the original order but need not be contiguous.

```
[10, 9, 2, 5, 3, 7, 101, 18]  ->  4   # e.g. [2, 3, 7, 101] or [2, 5, 7, 18]
[0, 1, 0, 3, 2, 3]            ->  4   # [0, 1, 2, 3]
[7, 7, 7, 7]                  ->  1   # strictly increasing, so only one 7
```

## Real-World Analogy

Socho tum **stacking cups** kar rahe ho ek line me — har cup tabhi rakh sakte ho jab uska number pichhle rakhe cup se bada ho. Array me numbers ek-ek aate hain (order fixed), aur tum sabse lambi badhti hui chain banana chahte ho.

Har naye number pe poochte ho: "mere se chhote jitne bhi numbers pehle aaye, unme se sabse lambi chain kaunsi thi? Us chain ke peeche main lag jaata hoon, +1." Yani har position pe "yahan **khatam** hone wali sabse lambi increasing chain" yaad rakho. Aakhir me sabse lamba wala answer.

## Approach

**O(n²) DP (samajhne ke liye best):** `dp[i]` = "index `i` pe **khatam** hone wali longest increasing subsequence ki length". Har `i` ke liye, peeche ke har `j < i` dekho jahan `nums[j] < nums[i]` — un sabke `dp[j]` me se max lo, +1.

```python
def length_of_lis(nums):
    n = len(nums)
    dp = [1] * n                     # har element akela ek length-1 subseq
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:    # strictly increasing
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

**O(n log n) optimal (patience sorting):** ek `tails` array rakho jahan `tails[k]` = length-`(k+1)` increasing subsequence ka **sabse chhota possible last element**. Har number ko binary-search se sahi jagah place karo:

```python
from bisect import bisect_left

def length_of_lis(nums):
    tails = []
    for n in nums:
        i = bisect_left(tails, n)    # pehli position jahan tails[i] >= n
        if i == len(tails):
            tails.append(n)          # chain extend hui
        else:
            tails[i] = n             # chhota last element se replace
    return len(tails)
```

Pattern: **1-D DP** (ending-here ka classic) ya **patience sorting + binary search** for the speedup. Note: `tails` khud LIS nahi hai, par uski **length** sahi hai.

## Complexity

| Approach | Time | Space | Why |
|----------|------|-------|-----|
| DP | O(n²) | O(n) | Har `i` ke liye saare pichhle `j` scan |
| Patience + binary search | **O(n log n)** | O(n) | Har element pe ek `bisect` (log n) |

## Common Pitfalls

- **`>=` vs `>`** — "strictly increasing" chahiye to `nums[j] < nums[i]`. Agar duplicates allowed (non-decreasing) ho to `bisect_right` use hoga; warna `bisect_left`.
- **`tails` ko answer samajhna** — `tails` array final me actual LIS sequence nahi hota, sirf uski length sahi hai. Sequence reconstruct karna ho to parent-pointers chahiye.
- **`dp` ko `0` se init karna** — har element khud ek length-1 subsequence hai, isliye `dp = [1]*n`.
- **Empty array** — `max(dp)` empty pe crash karega; guard daalo (LIS of `[]` is 0).

## When to Use This Pattern

"Longest / count of subsequence satisfying an order constraint" → ending-here DP socho (`dp[i]` = best subsequence ending at `i`). Jab n bada ho aur tum log-factor chahte ho, **patience sorting + binary search**. Cue: "order matters, contiguous nahi, optimal chain length."

## NeetCode Link

https://neetcode.io/problems/longest-increasing-subsequence
