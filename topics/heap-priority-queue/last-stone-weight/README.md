# Last Stone Weight

**Category:** Heap / Priority Queue
**Difficulty:** easy

## Problem Statement

Tumhare paas stones hain, har ek ka ek `weight`. Har turn me **do sabse heavy stones** uthao (`x <= y`) aur smash karo:
- agar `x == y`: dono destroy ho jaate hain.
- agar `x != y`: chhota destroy, bada ek naye stone `y - x` me badal jaata hai.

Last me jo ek stone bacha (ya 0 agar kuch nahi bacha) uska weight return karo.

```
[2, 7, 4, 1, 8, 1]
smash 8,7 -> 1   => [2,4,1,1,1]
smash 4,2 -> 2   => [2,1,1,1]
smash 2,1 -> 1   => [1,1,1]
smash 1,1 -> 0   => [1]
-> 1
```

## Real-World Analogy

Socho ek **gladiator arena** hai. Har round me hum do **sabse strong** baache hue gladiators ko aamne-saamne khada karte hain. Equal strength wale? Dono mar jaate hain. Warna chhota mar jaata hai aur bada thak ke `(bada - chhota)` strength ke saath bach jaata hai aur wapas pool me daal diya jaata hai. Hum baar-baar **top-2 strongest** chahte hain — yahi **max-heap** ka kaam hai: har baar sabse bada turant nikaalo.

## Approach

Har turn me "do sabse bade" chahiye. Naive: har baar array sort karo — O(n log n) per turn, total O(n² log n). Better: **max-heap** se top-2 har baar O(log n) me nikaalo.

Python ka `heapq` sirf min-heap deta, isliye **values negate** kar do — negative ka min = original ka max.

```python
import heapq

def last_stone_weight(stones):
    heap = [-s for s in stones]        # negate -> max-heap trick
    heapq.heapify(heap)
    while len(heap) > 1:
        y = -heapq.heappop(heap)        # heaviest
        x = -heapq.heappop(heap)        # 2nd heaviest
        if y != x:
            heapq.heappush(heap, -(y - x))   # remnant back in
    return -heap[0] if heap else 0
```

Pattern: **max-heap se repeatedly top-2 nikaalo, process karo, result wapas push karo.**

## Complexity

- **Time:** O(n log n). Har smash ek-do heap ops (log n), aur kul O(n) smashes — har smash pool ka size kam se kam 1 ghatata hai.
- **Space:** O(n) for the heap.

## Common Pitfalls

- **Negate karna bhulna** — `heapq` min-heap hai. Bina negate kiye tum sabse *chhote* stones smash karoge, galat answer.
- **Push wapas karna bhulna** — `y != x` case me `y - x` ko heap me wapas daalna zaroori hai, warna stones gayab.
- **Empty heap pe `heap[0]`** — agar saare stones cancel ho gaye to heap empty; `return 0` handle karo.
- **`x` aur `y` ka order ulta** — pop order me pehla wala bada (`y`), doosra chhota (`x`). `y - x` hamesha `>= 0`.

## When to Use This Pattern

"Repeatedly **largest/smallest do (ya k) elements** uthao, combine karo, result wapas daalo" → max-heap (ya min-heap) simulation. Cue: greedy "always take the extreme right now" + dynamic pool. Cousins: merge K lists, task scheduler, minimum cost to connect ropes.

## NeetCode Link

https://neetcode.io/problems/last-stone-weight
