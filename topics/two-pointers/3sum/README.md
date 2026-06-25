# 3Sum

**Category:** Two Pointers
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, return **all unique triplets** `[a, b, c]` such
that `a + b + c == 0`. The solution set must **not contain duplicate triplets**
(order within/among triplets doesn't matter).

```
[-1, 0, 1, 2, -1, -4]  ->  [[-1, -1, 2], [-1, 0, 1]]
[0, 1, 1]              ->  []          # no triplet sums to 0
[0, 0, 0]              ->  [[0, 0, 0]]
```

## Real-World Analogy

**What Azure Data Explorer (Kusto) is:** Azure Data Explorer is Azure's fast analytics service for high-volume telemetry, logs, and time-series data, queried with KQL. Teams use it to investigate numeric deltas such as capacity changes, error-rate movement, or cost adjustments across huge datasets. Sorting or ordering a result set gives the query a structure that simple scans can exploit.

**What a sorted range scan is, and why it's used:** In a sorted Kusto-style scan, moving the left cursor increases the candidate value and moving the right cursor decreases it. For a balanced triplet, you can pin one telemetry delta as the anchor `a`, then search the remaining sorted range for two deltas whose sum is `-a`. Sorting exists here for two reasons: it makes the pointer movements predictable, and it places equal deltas next to each other so duplicate anchors and duplicate pairs can be skipped cleanly.

**The mapping:** The sorted `nums` array is an ordered Azure Data Explorer telemetry column, `i` is the fixed Kusto predicate/anchor, and `l`/`r` are the lower and upper range cursors searching for the complement. If the sum is too small, move `l` to a larger delta; if it is too large, move `r` to a smaller delta; on a match, record it and skip adjacent duplicates. The key insight is that sorting turns a cubic search into repeated linear complement scans while also making deduplication local.

## Approach

Pattern: **sort + fix one + two-pointer** (O(n²)). Sorting do cheezein deta hai —
two-pointer chal sakta hai, aur duplicates adjacent aa jaate hain (easy skip).

```python
def three_sum(nums):
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if nums[i] > 0:                       # sorted -> baaki sab positive, sum != 0
            break
        if i > 0 and nums[i] == nums[i - 1]:  # duplicate anchor skip
            continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:  # dup skip on left
                    l += 1
                while l < r and nums[r] == nums[r + 1]:  # dup skip on right
                    r -= 1
    return res
```

> **Brute force** teen nested loops = O(n³). Sort + two-pointer isse **O(n²)** tak
> le aata, aur duplicate handling sorting ke kaaran clean rehti.

## Complexity

- **Time:** O(n²) — outer loop O(n), andar two-pointer O(n). Sort O(n log n) chhota
  pad jaata.
- **Space:** O(1) extra (output ko chhod kar) — in-place sort, sirf pointers.

## Common Pitfalls

- **Duplicate triplets** — sabse bada trap. Anchor pe `nums[i] == nums[i-1]` skip,
  aur match ke baad dono pointers pe dup-skip — dono zaroori hain.
- **Set use karke dedupe karna** — kaam karta hai par slow aur memory-heavy;
  sorted-skip cleaner hai aur interviewer wahi chahta.
- **`nums[i] > 0` break miss karna** — sorted array me anchor positive ho gaya to
  aage kuch nahi milega; bina iske bhi correct hai par optimization chhoot jaata.
- **Pointer move karna bhulna match ke baad** — `l += 1; r -= 1` na karo to infinite
  loop / same triplet repeat.

## When to Use This Pattern

Jab "k numbers dhundo jinka sum = target" dikhe → **sort, fir (k-1) ko nested
two-pointer me reduce karo**. 3Sum = 1 fix + 2-pointer; 4Sum = 2 fix + 2-pointer.
Cue: "find triplets/quadruplets summing to X, no duplicates."

## NeetCode Link

https://neetcode.io/problems/three-integer-sum
