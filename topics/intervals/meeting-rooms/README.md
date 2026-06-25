# Meeting Rooms

**Category:** Intervals
**Difficulty:** easy

## Problem Statement

Given an array of meeting time `intervals` where `intervals[i] = [start_i, end_i]`,
determine if a person could attend **all** meetings — i.e. return `True` if **no two
meetings overlap**, else `False`.

```
[[0,30],[5,10],[15,20]]   ->  False   # [0,30] overlaps [5,10]
[[7,10],[2,4]]            ->  True     # disjoint
[[1,5],[5,8]]             ->  True     # touching is fine
```

## Real-World Analogy

**What Azure Update Manager is:** Azure Update Manager is Azure's centralized way to manage OS update compliance and scheduled patching for machines. For a single Azure VM, only one maintenance operation should own the machine at a time; overlapping patch windows create confusing ownership, noisy alerts, and avoidable downtime risk.

**What maintenance-window conflict checking is, and why it's used:** Conflict checking validates a proposed set of maintenance windows before they are accepted for the same VM or fleet. Sorting by start time is used because once windows are chronological, any double-booking must appear between neighboring windows; a later window cannot hide a conflict behind an earlier non-overlapping one. This avoids expensive pair-by-pair comparisons while still catching every overlap.

**The mapping:** Each meeting interval is an Azure Update Manager maintenance window for the same VM. Sort the windows by start time, then compare each window's start with the previous window's end; if `start < previous_end`, the VM would be double-booked and the schedule is invalid. The key insight is that sorting turns a global Azure scheduling question into a simple adjacent-window check.

## Approach

**Sort by start, phir adjacent overlap check.**

```python
def can_attend_meetings(intervals):
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:   # starts before prev ends
            return False
    return True
```

Sort ke baad agar koi overlap hai to woh **consecutive** intervals me hi dikhega —
isliye sirf neighbours compare karna kaafi. First clash milte hi `False`.

## Complexity

- **Time:** O(n log n) — sorting dominant; scan O(n).
- **Space:** O(1) extra (sort ke alawa).

## Common Pitfalls

- **Sort bhulna** — bina sort adjacent-check meaningless hai.
- **Touching ko clash maan lena** — `[1,5]` aur `[5,8]` clash nahi (ek khatam, doosri
  shuru). Condition `start < prev_end` (strict `<`); `<=` galat `False` dega.
- **Har pair compare karna (O(n²))** — zaroorat nahi; sort ke baad sirf adjacent.
- **Single ya empty list** — loop chalta hi nahi, seedha `True` (sahi).

## When to Use This Pattern

"Kya saare ranges ek single resource pe bina clash fit ho sakte hain?" → sort by
start + adjacent overlap check. Yeh Meeting Rooms II ka warm-up hai (jahan **kitne**
rooms chahiye woh poochte hain). Cue: single timeline, "any overlap exists?".

## Practice

- Visual: open `topics/intervals/meeting-rooms/visual.html`

## NeetCode Link

https://neetcode.io/problems/meeting-schedule
