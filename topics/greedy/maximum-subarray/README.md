# Maximum Subarray

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, find the **contiguous subarray** (containing at least one number) with the **largest sum**, and return that sum.

```
[-2, 1, -3, 4, -1, 2, 1, -5, 4]   ->   6     # subarray [4, -1, 2, 1]
[5, 4, -1, 7, 8]                  ->   23    # whole array
[-3, -1, -2]                      ->   -1    # best is the single element -1
```

> "Contiguous" matters — you cannot skip elements. The answer is one unbroken slice.

## Real-World Analogy

**What Azure Cost Management plus Azure Monitor is:** Azure Cost Management helps teams understand spending, budgets, and cost trends across Azure resources, while Azure Monitor adds operational signals such as errors, latency, and resource health. Together they can describe a workload's hourly net value: useful business output or savings as positives, waste and incidents as negatives. The goal is to find the strongest continuous operating window, not scattered good hours.

**What rolling net-value windowing is, and why it's used:** A rolling window lets Azure operators compare contiguous periods of workload behavior, such as "which uninterrupted run of hours produced the best net value?" If the current window's total becomes negative, carrying that loss into future hours can only make any future window worse. Dropping the loss-making prefix immediately keeps the analysis focused on windows that can still become optimal.

**The mapping:** Each number is an Azure hour's net value, `cur` is the best continuous window ending at the current hour, and `best` is the strongest window seen anywhere on the dashboard. For each hour, Kadane's choice is either extend the existing window or restart at the current hour if the previous total is baggage. The key insight is that a negative prefix is never worth preserving, so one pass can keep the best contiguous value without checking every window.
## Approach

**Brute force** — har possible subarray ka sum (O(n²)): har start `i` se har end `j` tak loop. Slow.

**Optimal — Kadane's algorithm** (O(n), greedy/DP):

Do running values rakho:
- `cur` = sabse bada subarray-sum jo **abhi current index pe khatam** hota hai.
- `best` = ab tak dekha gaya overall maximum.

Har element pe ek greedy choice: kya is element ko pichle `cur` ke saath jodu, ya isi element se naya subarray shuru karu?

```python
def max_subarray(nums):
    cur = best = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)   # extend ya fresh start — greedy decision
        best = max(best, cur)   # overall best ko update karte raho
    return best
```

`cur = max(x, cur + x)` hi poora khel hai. Agar `cur + x < x`, matlab pichla `cur` negative tha aur bojh ban raha tha → drop it, `x` se fresh start. `best` ko side me track karte raho kyunki maximum kahin beech me bhi aa sakta hai (end pe nahi).

## Complexity

- **Time:** O(n) — ek hi pass, har element pe constant work.
- **Space:** O(1) — sirf do scalar variables, koi extra array nahi.

## Common Pitfalls

- **`best = 0` se initialize karna** — agar saare numbers negative ho (`[-3, -1, -2]`), to galat `0` return karoge. Hamesha `nums[0]` se init karo, kyunki subarray me kam se kam ek element hona hi chahiye.
- **`cur` ko negative jaane dena aur carry karna** — `max(x, cur + x)` ka pehla argument (`x`) hi yeh reset handle karta hai. Bhuloge to running sum me purana loss ghiste rahega.
- **`best` ko sirf end pe check karna** — maximum subarray beech me khatam ho sakta hai, isliye `best` ko har iteration pe update karo, na ki loop ke baad ek baar.
- **Indices return karne ki demand** — agar interviewer start/end index bhi maange, to jis index pe `cur` reset hua (fresh start) use `tempStart` me yaad rakho, aur jab `best` update ho tab `start, end` commit karo.

## When to Use This Pattern

Jab dikhe **"contiguous subarray / substring ka maximum (ya minimum) kuch find karo"** — sum, product, length — to running-value greedy/DP socho. Cue: "har position pe ek choice — pichle accumulated result ko extend karu ya yahin se naya shuru?" Kadane's iska canonical example hai. Cousins: Maximum Product Subarray, Best Time to Buy/Sell Stock, Maximum Circular Subarray.

## Visual

Open [visual.html](visual.html) in your browser for an interactive Prev/Next walkthrough of Kadane's running totals.

## NeetCode Link

https://neetcode.io/problems/maximum-subarray
