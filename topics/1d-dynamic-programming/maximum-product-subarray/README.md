# Maximum Product Subarray

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, find the contiguous subarray (containing at least one number) that has the **largest product**, and return that product.

```
[2, 3, -2, 4]      ->  6    # subarray [2, 3]
[-2, 0, -1]        ->  0    # best is just [0]
[-2, 3, -4]        ->  24   # whole array: -2 * 3 * -4 = 24
```

## Real-World Analogy

Socho tum ek trader ho jo har din ka **multiplier** dekh raha hai — kuch din profit double karte hain (`>1`), kuch flat (`0`), aur kuch din loss me **negative** swing dete hain. Ab twist ye hai: do bure (negative) din ek saath aa jaayein to unka product **positive** ho jaata hai — do losses milke ek bada gain ban sakte hain!

Isliye tumhe sirf "abhi tak ka best" yaad rakhna kaafi nahi. Tumhe **sabse chhota (most negative) product bhi** yaad rakhna padega, kyunki agla negative number aaya to wahi chhota wala palat ke sabse bada ban sakta hai. Best aur worst — dono ko saath chalao.

## Approach

**Key insight:** ek single `max_so_far` chalana fail karta hai, kyunki negative number sabkuch ulta deta hai. Jab `nums[i]` negative ho, to abhi tak ka **maximum** product *minimum* ban jaata hai aur **minimum** *maximum* ban jaata hai. Isliye har position pe `cur_max` aur `cur_min` dono track karo.

Har element `n` pe teen candidates hain naye max ke liye:
- `n` akela (fresh start),
- `cur_max * n` (positive streak extend),
- `cur_min * n` (do negatives ka palatna).

```python
def max_product(nums):
    result = cur_max = cur_min = nums[0]
    for n in nums[1:]:
        # n negative hua to max/min swap ho jaayega — isliye teeno ka max/min
        candidates = (n, cur_max * n, cur_min * n)
        cur_max = max(candidates)
        cur_min = min(candidates)
        result = max(result, cur_max)
    return result
```

Pattern: **running DP** — `dp[i]` ko explicit array me store nahi karte, bas do rolling variables (`cur_max`, `cur_min`) chalate hain. Yahi Kadane's algorithm ka product-version hai.

## Complexity

- **Time:** O(n) — ek hi pass, har element pe constant kaam.
- **Space:** O(1) — sirf do running variables, koi dp array nahi.

## Common Pitfalls

- **Sirf `cur_max` track karna** — `cur_min` bhula to negative-flip wale cases (jaise `[-2, 3, -4]`) galat aayenge.
- **`max`/`min` ko sequentially update karna** — `cur_max` update karne ke baad agar usi line me `cur_min` me purana `cur_max` chahiye to bug. Pehle dono ke candidates compute karo, **fir** assign karo (ya temp use karo).
- **Zero handling** — `0` pe dono `cur_max` aur `cur_min` `0` ho jaate hain, jo automatically streak reset kar deta hai. Alag se handle karne ki zaroorat nahi — teeno candidates me `n` (=0) include hai.
- **Empty array** — `nums[0]` se start kar rahe hain, to empty input pe guard chahiye.
- **`result` ko `0` se initialize karna** — agar saare numbers negative hue to `0` galat answer dega; `nums[0]` se init karo.

## When to Use This Pattern

Jab "contiguous subarray ka optimal kuch (max sum / max product)" maanga ho → **Kadane-style running DP** socho. Aur jab operation me sign-flip ka khel ho (multiplication, negatives), to ek single best kaafi nahi — **best aur worst dono** carry karo. Cue: "ek extreme dusre extreme ko feed kar sakta hai."

## NeetCode Link

https://neetcode.io/problems/maximum-product-subarray
