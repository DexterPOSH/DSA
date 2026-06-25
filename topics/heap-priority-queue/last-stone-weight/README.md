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

**What Azure Batch is:** Azure Batch is Azure's service for running many compute tasks across a managed pool of machines. You can think of it as maintaining a pool of pending work items and repeatedly dispatching the most important work according to a scheduling policy. In this analogy, the "weight" of a stone is the amount of demand or backlog a work item represents.

**What priority-based workload dispatch is, and why it's used:** Priority-based dispatch always selects the largest or most urgent pending work first so the scheduler focuses on the biggest bottlenecks. After two large workloads interact, they may cancel each other out completely, or the larger one may leave a smaller remainder that still needs future processing. Requeueing that remainder is essential because the pool changes dynamically after every dispatch.

**The mapping:** The max-heap is the Azure Batch-style priority queue of pending workload weights. Each loop pops the two heaviest items, just like a scheduler pulling the two largest current demands; equal weights disappear, and an unequal pair pushes `y - x` back as leftover demand. The key insight is that every step depends on the current two extremes, so a heap gives exactly the operation the simulation needs: pop top two, then reinsert any remainder.

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
