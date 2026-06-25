# Kth Largest Element in an Array

**Category:** Heap / Priority Queue
**Difficulty:** medium

## Problem Statement

Diye gaye array `nums` aur integer `k`. Sorted order me **kth largest** element return karo (kth distinct nahi — duplicates count hote hain).

```
nums = [3, 2, 1, 5, 6, 4], k = 2
sorted desc: [6, 5, 4, 3, 2, 1] -> 2nd largest = 5
-> 5

nums = [3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4  -> 4
```

## Real-World Analogy

**What Azure Monitor is:** Azure Monitor is Azure's observability service for collecting metrics, logs, and traces from cloud resources and applications. For example, it can hold a fixed batch of VM CPU samples from a time range that an operator wants to inspect. Sometimes the operator needs a rank boundary, like the kth busiest VM, rather than a complete sorted report.

**What bounded top-k metric selection is, and why it's used:** A bounded top-k query keeps only the k largest metric values encountered while scanning a batch. This is useful because sorting every VM sample is unnecessary when smaller values cannot affect the kth-largest answer once the current top-k boundary is known. A min-heap of size k makes that boundary cheap to check: the root is the smallest value still inside the current top-k.

**The mapping:** Each number in `nums` is an Azure Monitor CPU sample from the fixed query result. Heapify the first k samples, then scan the rest: if a sample is larger than `heap[0]`, replace the root; if it is smaller or equal, it cannot change the kth-largest boundary. After one pass, `heap[0]` is the kth largest. The key insight is that the answer is the boundary of the top-k set, so maintaining that boundary beats sorting the whole array.

## Approach

**Min-heap of size k — O(n log k):**

```python
import heapq

def find_kth_largest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)
    for n in nums[k:]:
        if n > heap[0]:               # bigger than the weakest in top-k
            heapq.heapreplace(heap, n)
    return heap[0]                    # root = kth largest
```

**Quickselect — O(n) average** (in-place, no extra heap). kth largest = index `len(nums)-k` in ascending order:

```python
import random

def find_kth_largest(nums, k):
    target = len(nums) - k            # ascending index we want
    def partition(lo, hi):
        p = random.randint(lo, hi)
        nums[p], nums[hi] = nums[hi], nums[p]
        pivot, i = nums[hi], lo
        for j in range(lo, hi):
            if nums[j] < pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1
        nums[i], nums[hi] = nums[hi], nums[i]
        return i
    lo, hi = 0, len(nums) - 1
    while True:
        p = partition(lo, hi)
        if p == target: return nums[p]
        elif p < target: lo = p + 1   # answer in right half
        else: hi = p - 1              # answer in left half
```

Heap simple aur predictable. Quickselect average-case fastest but worst-case O(n²) (random pivot se mitigate hota).

## Complexity

| Approach | Time | Space | Note |
|----------|------|-------|------|
| Sort | O(n log n) | O(1)/O(n) | Simplest to write |
| **Min-heap size k** | **O(n log k)** | O(k) | Great when k ≪ n |
| **Quickselect** | **O(n) avg**, O(n²) worst | O(1) | Random pivot avoids worst case |

## Common Pitfalls

- **Quickselect ka index off-by-one** — kth *largest* ascending sort me index `n - k` hai (zero-based). Yeh galat karna sabse common bug.
- **Worst-case pivot** — already-sorted input + fixed pivot → O(n²). Random pivot (ya median-of-3) use karo.
- **Heap me max vs min confusion** — kth *largest* ke liye *min*-heap of size k (root = kth largest). Pure max-heap of all n elements bhi chalega but O(n + k log n), zyada space.
- **`heapreplace` vs `heappush`+`heappop`** — `heapreplace` ek op me pop-then-push; size constant rakhta. Sirf push karoge to heap n tak grow kar jayega.

## When to Use This Pattern

"kth largest / kth smallest / top-k from an unsorted array" → min/max-heap of size k (simple, stable) ya quickselect (jab pure O(n) average aur in-place chahiye). Cue: poora sort overkill, sirf ek rank-boundary chahiye. Cousins: K Closest Points, Median of Stream, Top K Frequent.

## NeetCode Link

https://neetcode.io/problems/kth-largest-element-in-an-array
