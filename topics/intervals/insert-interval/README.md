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

Socho ek **calendar** hai jisme meetings already pari hain, time ke order me, koi
overlap nahi. Ab boss ek nayi meeting de deta hai `[4,8]`. Tum upar se neeche scan
karte ho:

- Jo meetings naye block ke **poori tarah pehle** khatam ho jaati hain (`end < newStart`) → unhe waise hi rakh do, koi tension nahi.
- Jo meetings naye block ko **touch ya overlap** karti hain → unhe naye block ke
  saath **chipka do (merge)** — start ka minimum lo, end ka maximum.
- Jo meetings naye block ke **poori tarah baad** shuru hoti hain (`start > newEnd`) → bachi hui sab waise ki waise add kar do.

Ek hi pass, kyunki list already sorted hai.

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
