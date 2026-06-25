# Non Overlapping Intervals

**Category:** Intervals
**Difficulty:** medium

## Problem Statement

Given an array of `intervals`, return the **minimum number of intervals you need to
remove** to make the rest non-overlapping.

```
[[1,2],[2,3],[3,4],[1,3]]   ->  1    # remove [1,3]
[[1,2],[1,2],[1,2]]         ->  2    # keep one, remove two duplicates
[[1,2],[2,3]]               ->  0    # touching, no overlap
```

> Equivalent framing: find the **maximum set of non-overlapping intervals you can
> keep**; remove the rest. `answer = n - keep`.

## Real-World Analogy

**What Azure Batch is:** Azure Batch is Azure's service for scheduling compute-intensive jobs across a pool of VM nodes. When a pool slice is constrained, only one reservation can use that slice at a time, so overlapping reservations represent more promised capacity than the pool can actually provide.

**What a capacity reservation window is, and why it's used:** A capacity reservation window is an operational promise that a Batch pool slice will be available to a job for a specific start/end period. If too many requests overlap, the scheduler must reject some windows to keep the accepted plan feasible. Sorting by earliest end time is used because accepting the reservation that frees the pool first leaves the most remaining timeline for later Azure Batch jobs.

**The mapping:** Each interval is an Azure Batch reservation request for the same constrained pool slice. Sort requests by end time, accept a request only when its start is at or after the last accepted end, and count every overlapping request as one that must be removed. The key insight is that choosing the earliest-ending Azure reservation is the greedy move that maximizes kept windows, so rejected windows are the minimum removals.

## Approach

**Greedy by end time.** Sort by end, phir scan: jab tak agla interval pichhle "kept"
interval ke `end` ke baad (ya barabar) shuru hota hai, use rakho aur `end` update
karo; warna woh overlap kar raha → remove count badhao (use chhod do).

```python
def erase_overlap_intervals(intervals):
    intervals.sort(key=lambda x: x[1])    # END ke order me sort
    prev_end = float('-inf')
    removed = 0
    for start, end in intervals:
        if start >= prev_end:             # no overlap -> KEEP
            prev_end = end
        else:                             # overlap -> REMOVE this one
            removed += 1
    return removed
```

Key insight: **sort by end, not start.** Earliest-finishing interval ko keep karna
hamesha optimal hai (exchange argument) — yeh greedy globally best deta hai.

## Complexity

- **Time:** O(n log n) — sorting; phir O(n) single sweep.
- **Space:** O(1) extra (sort ke alawa).

## Common Pitfalls

- **Start pe sort karna** — galat. Earliest-**end** chahiye greedy ke liye. Start
  pe sort karoge to ek lambe early-start interval choose karke baaki kaat doge.
- **Touching ko overlap maan lena** — `[1,2]` aur `[2,3]` overlap nahi karte; isliye
  condition `start >= prev_end` (with `>=`), na ki `>`.
- **`prev_end` update kab** — sirf jab interval **keep** karo tab update karo. Removed
  interval ka end aage carry mat karo (use to phenk diya).
- **n - keep vs removed** — dono framing equivalent; yahan seedha `removed` count kar rahe, no need to subtract.

## When to Use This Pattern

"Maximum non-overlapping subset" / "minimum removals to de-conflict" / "ek resource
pe max activities" → **greedy sort-by-end (activity selection)**. Cue dikhe: single
resource, overlapping ranges, optimize count. Cousins: Meeting Rooms II, Maximum Length of Pair Chain.

## Practice

- Visual: open `topics/intervals/non-overlapping-intervals/visual.html`

## NeetCode Link

https://neetcode.io/problems/non-overlapping-intervals
