# Insert Interval

**Category:** Intervals
**Difficulty:** medium

## Problem Statement

You're given a list of **non-overlapping** intervals `intervals`, sorted by their
start time, and one `newInterval`. Insert `newInterval` into the list so that the
result is still **sorted and non-overlapping** (merge where needed).

```
intervals = [[1,3], [6,9]],  newInterval = [2,5]   ->  [[1,5], [6,9]]
intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
                                               ->  [[1,2],[3,10],[12,16]]
```

## Real-World Analogy

**What Azure Update Manager is:** Azure Update Manager is Azure's service for assessing, scheduling, and orchestrating OS updates across Azure VMs, on-prem machines, and multicloud servers connected through Azure Arc. Instead of patching whenever an update appears, operators define controlled maintenance periods so changes happen during approved windows with predictable impact.

**What a maintenance window is, and why it's used:** A maintenance window is a start/end block during which updates are allowed to run for a target set of machines. Keeping these windows sorted and non-overlapping gives operators a clean timeline: past windows stay untouched, overlapping approvals become one larger maintenance period, and future windows remain in order. This prevents the same fleet from being represented by duplicate patch windows and makes the schedule easy to reason about.

**The mapping:** The existing Azure Update Manager schedule is the sorted interval list, and the incoming approval is `newInterval`. Copy every window that ends before the new one starts, merge every window that overlaps it by taking the earliest start and latest end, then insert the merged block before the first future window. The key insight is that sorted, non-overlapping Azure maintenance windows make all conflicts with the new window contiguous, so one left-to-right pass is enough.

## Approach

List sorted hai, isliye **linear scan in three phases** — koi dobara sort nahi.

```python
def insert(intervals, newInterval):
    res = []
    i, n = 0, len(intervals)

    # Phase 1: sab intervals jo new se poori tarah pehle (end < new.start)
    while i < n and intervals[i][1] < newInterval[0]:
        res.append(intervals[i])
        i += 1

    # Phase 2: jo overlap karte hain unhe new me merge karo
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    res.append(newInterval)          # merged block daalo

    # Phase 3: sab bache hue (start > new.end)
    while i < n:
        res.append(intervals[i])
        i += 1

    return res
```

Pattern: **sorted-interval sweep**. Overlap ki condition: do intervals `a` aur `b`
overlap karte hain jab `a.start <= b.end` AND `b.start <= a.end`. Yahan ek side
phase-1 me already handle ho gaya, isliye phase-2 me sirf `start <= newEnd` check
bachta hai.

## Complexity

- **Time:** O(n) — har interval exactly ek baar visit hota hai, koi sort nahi (input already sorted tha).
- **Space:** O(n) — output list ke liye (in-place gin-na ho to O(1) extra).

## Common Pitfalls

- **Overlap condition galat lagana** — touching intervals (`[1,3]` aur `[3,5]`) ko
  overlap maano: use `<=`, na ki `<`. Warna `[1,3]+[3,5]` merge nahi honge.
- **newInterval ko mutate karna** — phase-2 me hum `newInterval` ko hi expand karte
  hain; agar caller ko original chahiye to copy bana lo.
- **Empty intervals** — `intervals = []` pe code ko sirf `[newInterval]` return karna chahiye (teeno loops skip ho jaate hain — kaam karta hai).
- **`new` sabse end me aata hai** — phase-1 sab consume kar le, phase-2/3 kuch na kare; `res.append(newInterval)` phir bhi sahi jagah daalta hai.

## When to Use This Pattern

Jab intervals **already sorted** ho aur ek single insertion/merge karna ho → poora
re-sort mat karo, **three-phase linear sweep** socho. Cue: "sorted non-overlapping
list + ek naya element fit karo". Cousins: Merge Intervals (jahan sort khud karna padta), Meeting Rooms.

## Practice

- Visual: open `topics/intervals/insert-interval/visual.html`

## NeetCode Link

https://neetcode.io/problems/insert-new-interval
