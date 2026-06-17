# Find Median from Data Stream

**Category:** Heap / Priority Queue
**Difficulty:** hard

## Problem Statement

Design a data structure that supports a **stream** of integers and can return the **median** at any time.

- `addNum(num)` — add an integer from the stream.
- `findMedian()` — return the median of all numbers added so far.

Median = middle value of the sorted numbers. Even count → average of the two middle values.

```
addNum(1)            findMedian() -> 1.0
addNum(2)            findMedian() -> 1.5     # (1 + 2) / 2
addNum(3)            findMedian() -> 2.0
```

## Real-World Analogy

Socho ek **seesaw (balance scale)** hai. Left side pe **chhoti aadhi** numbers baithi hain, right side pe **badi aadhi**. Median hamesha bilkul **beech** me hota hai — yaani seesaw ke pivot pe.

Trick: left side ko aise rakho ki uska **sabse bada** element easily mile (uska top), aur right side ka **sabse chhota** element easily mile. Beech ke do candidates yahi hain. Har naya number aane par usse sahi side pe daalo, phir **dono sides ko balance** karo taaki size me 1 se zyada farak na ho. Median = ya to bhaari side ka top (odd total), ya dono tops ka average (even total).

"Left ka max chahiye" = **max-heap**. "Right ka min chahiye" = **min-heap**. Bas dono ko balanced rakhna hai.

## Approach — two heaps

Maintain do heaps:
- `small` — a **max-heap** holding the smaller half (Python me negatives se simulate).
- `large` — a **min-heap** holding the larger half.

Invariant: har element in `small` ≤ har element in `large`, aur sizes ka farak ≤ 1. Hum convention rakhte hain: jab total odd ho, extra element `small` me jaata hai.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.small = []   # max-heap (store negatives)
        self.large = []   # min-heap

    def addNum(self, num):
        # 1) push to small (max-heap)
        heapq.heappush(self.small, -num)
        # 2) ensure every small <= every large: move small's max over if needed
        if self.small and self.large and (-self.small[0] > self.large[0]):
            heapq.heappush(self.large, -heapq.heappop(self.small))
        # 3) rebalance sizes (small may hold the extra, diff at most 1)
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        elif len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]                      # odd total
        return (-self.small[0] + self.large[0]) / 2    # even total
```

Teen kaam har `addNum` pe: **(1)** push, **(2)** order fix (left ka max kabhi right ke min se bada na ho), **(3)** size balance. `findMedian` bas heaps ke tops dekh ke O(1) me answer de deta — koi sorting nahi.

## Complexity

- **addNum Time:** O(log n) — har heap push/pop log n. Constant number of ops per add.
- **findMedian Time:** O(1) — sirf heap tops padho.
- **Space:** O(n) — saare numbers dono heaps me distribute hote hain.

> Naive alternative: list me daalo aur `findMedian` pe sort karo → O(n log n) per query. Sorted list me binary-search insert → O(n) per add (shift). Two heaps best of both: O(log n) add, O(1) median.

## Common Pitfalls

- **Max-heap simulate karna** — Python `heapq` min-heap hai. `small` ke liye `-num` push karo aur padhte waqt `-self.small[0]` se wapas flip karo. Sign bhulna = sab kuch ulta.
- **Order step skip karna** — sirf size balance karna kaafi nahi. Naya number `small` me push hua par woh `large` ke min se bada nikla, to usse cross karna padega; warna invariant toot jaata aur median galat aata.
- **Even/odd median formula** — odd pe bhaari side (yahan `small`) ka top; even pe **dono tops ka average** (`/2`, integer division nahi — float chahiye).
- **Empty state** — pehla element add hone se pehle `findMedian` call undefined; guard ya assume at-least-one-add.
- **Consistent extra-side convention** — decide karo extra element `small` me jaata ya `large` me, aur findMedian ko usi ke hisaab se likho. Mixing the two conventions = off-by-one median.
- **Integer overflow (other languages)** — do tops ka sum lete waqt large ints me overflow ka dhyaan (Python me concern nahi, Java/C++ me hai).

## When to Use This Pattern

Jab dikhe **"running / streaming median"** ya **"do balanced halves maintain karni hain jahan ek ka max aur dusre ka min chahiye"** → **two heaps (max-heap + min-heap)**. Cousins: sliding-window median, IPO/scheduling with two priority queues, "k-th smallest so far". Cue: "middle element chahiye continuously without re-sorting".

## NeetCode Link

https://neetcode.io/problems/find-median-in-a-data-stream
