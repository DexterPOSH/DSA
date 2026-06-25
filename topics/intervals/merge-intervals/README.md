# Merge Intervals

**Category:** Intervals
**Difficulty:** medium

## Problem Statement

Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all
**overlapping** intervals and return the non-overlapping intervals that cover all
the input intervals.

```
[[1,3],[2,6],[8,10],[15,18]]   ->  [[1,6],[8,10],[15,18]]   # [1,3] & [2,6] overlap
[[1,4],[4,5]]                  ->  [[1,5]]                   # touching counts as overlap
```

## Real-World Analogy

**What Azure Update Manager is:** Azure Update Manager helps Azure operators coordinate update assessment and patch deployment across large fleets of machines. In real organizations, multiple teams may submit planned maintenance windows for the same application fleet, region, or dependency chain.

**What maintenance-window consolidation is, and why it's used:** Consolidation combines overlapping maintenance windows into the fewest continuous outage periods that need to be communicated and tracked. Sorting by start time brings overlapping windows next to each other, so operators can extend one active window instead of announcing several partially duplicated windows. This produces a cleaner Azure change calendar and avoids double-counting customer-impact periods.

**The mapping:** Each interval is a proposed Azure Update Manager maintenance window. Sort by start time, keep the last consolidated window, and if the next window starts before or at its end, extend the end to the later finish time; otherwise, finalize the current window and start a new one. The key insight is that once Azure maintenance windows are sorted, every overlap is local to the current merged window.

## Approach

Pehle **sort by start**, phir ek pass me merge — classic **sort + sweep**.

```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])      # start ke order me lao
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last = merged[-1]
        if start <= last[1]:                # overlap (touch bhi) -> stretch
            last[1] = max(last[1], end)
        else:                               # gap -> naya block
            merged.append([start, end])
    return merged
```

Sort ke baad ek interval sirf apne **immediately pehle wale** se overlap check karna
kaafi hai — agar us se overlap nahi to peeche kisi se bhi nahi (sab start chote hain
aur unka end aur bhi peeche).

## Complexity

- **Time:** O(n log n) — dominant cost sorting ka hai; sweep khud O(n).
- **Space:** O(n) output ke liye (sort in-place ho to O(log n) extra for the sort itself).

## Common Pitfalls

- **Sort bhulna** — bina sort, ye pure algorithm galat. Yehi step #1 hai.
- **Touching intervals** — `[1,4]` aur `[4,5]` ko merge karo (`<=`, na ki `<`),
  warna tumhare answer me extra split rah jaayega.
- **`max(last[1], end)` na lagana** — agar nested interval ho (`[1,10]` ke andar `[2,3]`), to seedha `last[1]=end` lagane se end **chhota** ho jaayega. Hamesha `max`.
- **Sort key galat** — start ke saath kabhi end pe sort mat karo; start ka order chahiye taaki left-to-right sweep valid rahe.

## When to Use This Pattern

Jab bhi "**overlapping ranges ko combine/clean up**" karna ho → pehle sort by start,
phir single sweep. Yeh poore intervals family ka foundation hai. Cue: "ranges,
overlap, merge/coverage". Cousins: Insert Interval, Meeting Rooms, Employee Free Time.

## Practice

- Visual: open `topics/intervals/merge-intervals/visual.html`

## NeetCode Link

https://neetcode.io/problems/merge-intervals
