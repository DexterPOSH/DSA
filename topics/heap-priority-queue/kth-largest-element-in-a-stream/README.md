# Kth Largest Element in a Stream

**Category:** Heap / Priority Queue
**Difficulty:** easy

## Problem Statement

Design a class `KthLargest` that, for a fixed `k`, returns the **kth largest** element seen so far each time a new number arrives. Note: it's the kth largest in *sorted order* (duplicates count), not the kth distinct value.

```
KthLargest(k=3, nums=[4, 5, 8, 2])
add(3)  -> 4      # stream sorted desc: [8,5,4,3,2] -> 3rd largest = 4
add(5)  -> 5      # [8,5,5,4,3,2] -> 3rd = 5
add(10) -> 5      # [10,8,5,5,4,3,2] -> 3rd = 5
add(9)  -> 8      # [10,9,8,5,5,4,3,2] -> 3rd = 8
add(4)  -> 8
```

## Real-World Analogy

**What Azure Stream Analytics is:** Azure Stream Analytics is Azure's real-time stream-processing service for turning continuous telemetry into dashboards, alerts, and downstream outputs. In this analogy, Azure Monitor supplies live resource metrics such as VM CPU, request counts, latency, and error rates, while Stream Analytics represents the processor that updates results as each metric arrives. Together, they model a stream where every new value may change a "top k" view immediately.

**What a streaming top-k boundary is, and why it's used:** A streaming top-k dashboard only needs the largest k values seen so far, not a sorted history of every metric ever received. Keeping a bounded min-heap of size k makes the smallest value inside that top-k set instantly visible; that value is the cutoff for whether a new metric matters. This exists to keep per-event work small and memory bounded while still updating the kth-largest answer after every arrival.

**The mapping:** The constructor loads the initial Azure Monitor-style metric samples into a min-heap and trims it to k values. Each `add(val)` is a new telemetry point: push it, evict the smallest if the heap grew too large, and then read `heap[0]`. The key insight is that the root is not the largest value; it is the weakest value that still qualifies for the top-k, which is exactly the kth largest so far.

## Approach

Naive: har `add` pe poora array sort karo aur `arr[k-1]` lo — O(n log n) per add. Bekaar for a stream.

**Optimal — min-heap of size k.** Heap me sirf top-k largest elements rakho. Heap ka root (minimum) hamesha kth largest hai. Naya element aaye to push karo; agar heap k se bada ho gaya to pop karo (sabse chhota nikal do). Root return.

```python
import heapq

class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums[:]            # min-heap
        heapq.heapify(self.heap)
        while len(self.heap) > k:      # trim down to top-k
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)   # evict the smallest
        return self.heap[0]            # root = kth largest
```

Python ka `heapq` default min-heap hai — yahi humein chahiye. Root (`heap[0]`) hamesha smallest of the k = kth largest overall.

## Complexity

- **Time:** `add` → O(log k). Sirf push + maybe pop, dono log k (heap size capped at k, n nahi).
- **Space:** O(k). Heap me kabhi bhi sirf k elements.

## Common Pitfalls

- **Max-heap use karna** — agar saare n elements ek max-heap me rakhoge to har add pe k baar pop karna padega aur heap O(n) space leta. Min-heap of size k cleaner aur faster hai.
- **kth distinct samajh lena** — yeh kth largest *with duplicates* hai. `[5,5,5]`, k=2 ka answer 5 hai, not "no 2nd distinct".
- **Constructor me trim bhulna** — agar `nums` me k se zyada elements hain to init pe extra pop karke heap ko size k pe laana zaroori hai.
- **`heap[0]` ko peek karne ke bajaye pop kar dena** — root sirf padhna hai, nikalna nahi.

## When to Use This Pattern

"Top-k / kth largest / kth smallest **from a stream** (ya bade dataset)" dikhe to min-heap (kth largest ke liye) ya max-heap (kth smallest ke liye) of size k socho. Cue: tumhe poora data sort nahi karna, sirf k boundary maintain karni hai. Cousins: K Closest Points, Kth Largest in Array, Top K Frequent.

## NeetCode Link

https://neetcode.io/problems/kth-largest-element-in-a-stream
