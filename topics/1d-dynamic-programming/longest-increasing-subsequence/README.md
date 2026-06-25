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

**What Azure Stream Analytics is:** Azure Stream Analytics is a real-time analytics service for processing event streams from sources such as Event Hubs, IoT Hub, and Blob Storage. It runs SQL-like queries over incoming events and writes results to downstream sinks. That makes it useful for detecting trends in telemetry as data arrives.

**What stateful trend aggregation is, and why it's used:** A streaming job can keep state about the best trend ending at earlier events instead of storing and reprocessing the whole stream for every new event. This state exists because real-time systems need low latency: when a new metric arrives, the job should reuse prior aggregates that are already known. For an increasing trend, only earlier lower values can extend into the current event.

**The mapping:** Event `i` is `nums[i]`, and `dp[i]` is the longest strictly increasing trend that ends at that event. Azure Stream Analytics would look back at prior events `j` with lower metric values and reuse their cached lengths, setting `dp[i] = max(dp[j] + 1)`. The key insight is that each subsequence is anchored by its last event, so the best answer ending here is built from the best valid answer ending earlier.

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
