# Minimum Interval to Include Each Query

**Category:** Intervals
**Difficulty:** hard

## Problem Statement

You're given `intervals` where `intervals[i] = [left_i, right_i]` (inclusive), and an
array of `queries`. For each query `q`, find the **size of the smallest interval that
contains `q`** — where size of `[l, r]` is `r - l + 1`. If no interval contains `q`,
the answer is `-1`. Return an array of answers, one per query.

```
intervals = [[1,4],[2,4],[3,6],[4,4]],  queries = [2,3,4,5]
   ->  [3, 3, 1, 4]
   # q=2: smallest covering = [2,4] size 3
   # q=4: smallest covering = [4,4] size 1
   # q=5: smallest covering = [3,6] size 4
```

## Real-World Analogy

**What Azure Service Health is:** Azure Service Health is Azure's personalized health and advisory service for incidents, advisories, and planned maintenance that may affect your subscriptions and resources. It gives teams event timelines, impact details, and alerts so they can explain what was happening at a particular time.

**What planned-maintenance event matching is, and why it's used:** A planned-maintenance event has a start time, an end time, and an impact window duration. When many alert timestamps need explanations, matching each timestamp by scanning every event is slow; instead, sort timestamps and events, then keep only events that have started and have not yet ended. A min-heap keyed by duration surfaces the shortest active Azure maintenance window, which is usually the most specific explanation for that timestamp.

**The mapping:** Intervals are Azure Service Health planned-maintenance events, and queries are alert timestamps. Sweep timestamps in sorted order, push every event whose start is at or before the timestamp into a duration heap, lazily remove heap entries whose end is before the timestamp, and read the heap top as the smallest covering window. The key insight is that sorted offline processing plus lazy heap cleanup answers many Azure timestamp queries without rechecking every event each time.

## Approach

**Offline + sort + min-heap by interval size.** Intervals ko left ke order me sort,
queries ko value ke order me sort (par original index yaad rakho). Sweep:

```python
import heapq

def min_interval(intervals, queries):
    intervals.sort()                          # by left ascending
    heap = []                                 # (size, right) min-heap by size
    res = {}
    i = 0
    for q in sorted(queries):
        # add every interval whose left <= q (now reachable)
        while i < len(intervals) and intervals[i][0] <= q:
            l, r = intervals[i]
            heapq.heappush(heap, (r - l + 1, r))
            i += 1
        # drop intervals that already ended before q (right < q)
        while heap and heap[0][1] < q:
            heapq.heappop(heap)
        res[q] = heap[0][0] if heap else -1    # smallest still covering q
    return [res[q] for q in queries]
```

Key ideas:
1. **Sort queries** → ek hi forward pass me `i` pointer intervals ko monotonically add karta hai (har interval at most ek baar push).
2. **Min-heap by size** → top hamesha sabse chhota candidate.
3. **Lazy deletion** → invalid (`right < q`) intervals ko sirf tab nikaalo jab woh top pe aayein.

> `res` dict use kar rahe taaki duplicate queries bhi ek hi answer share karein,
> phir original order me reconstruct.

## Complexity

- **Time:** O(n log n + m log m + (n+m) log n) — intervals sort + queries sort +
  har interval ek push/pop. Effectively O((n + m) log(n + m)).
- **Space:** O(n) heap + O(m) result map.

## Common Pitfalls

- **Size formula** — inclusive intervals: size = `r - l + 1`, na ki `r - l`. q=4 in `[4,4]` ka answer 1 hona chahiye.
- **Queries ko sort kiye bina answer original order me dena** — sorted order me process karo, par output original query order me map karke do (isliye dict/index tracking).
- **Lazy deletion miss karna** — jab tak heap top ka `right < q`, pop karte raho;
  varna purana (already-ended) interval galat answer dega.
- **`<=` vs `<` add condition me** — interval reachable hai jab `left <= q` (q exactly left pe ho to bhi cover karta).
- **Duplicate queries** — agar same query baar baar aaye, dict caching se redundant kaam bach jaata.

## When to Use This Pattern

"Har query/point ke liye intervals me se kuch **optimize** (smallest/longest/etc.) chahiye" + bahut saari queries → **offline sort queries + min/max-heap sweep with lazy deletion**. Cue: "for each query find best covering interval", static intervals, many queries. Cousins: heap-based sweeps, The Skyline Problem.

## Practice

- Visual: open `topics/intervals/minimum-interval-to-include-each-query/visual.html`

## NeetCode Link

https://neetcode.io/problems/minimum-interval-including-query
