# Meeting Rooms II

**Category:** Intervals
**Difficulty:** medium

## Problem Statement

Given an array of meeting time `intervals`, return the **minimum number of conference
rooms** required so that no two simultaneous meetings share a room.

```
[[0,30],[5,10],[15,20]]   ->  2    # [5,10] & [15,20] both clash with [0,30]
[[7,10],[2,4]]            ->  1    # disjoint, one room reused
[[1,5],[5,8]]             ->  1    # touching, second reuses the room
```

> The answer equals the **maximum number of meetings happening at the same instant**.

## Real-World Analogy

**What Azure Batch is:** Azure Batch is Azure's managed service for running large-scale parallel and high-performance computing workloads on pools of VM compute nodes. You submit jobs and tasks, and Batch places them onto available nodes, with pool size or autoscale settings determining how much capacity exists.

**What pool capacity planning is, and why it's used:** Pool capacity planning asks how many VM nodes are needed so timed reservations can run without waiting for a node to free up. A min-heap of reservation end times models reusable capacity: the top is the node that becomes available first, so it is the first candidate to reuse for the next reservation. This gives a tight capacity estimate instead of blindly provisioning one VM per job.

**The mapping:** Each meeting is an Azure Batch job reservation, and each room is a VM node in the pool. Process reservations by start time, pop the earliest-ending node if it is already free, then push the new end time because that node is now occupied until then. The key insight is that the heap size represents concurrent Azure Batch VM demand, so the peak/final heap size is the minimum pool capacity needed.

## Approach

**Sort by start + min-heap of end times.**

```python
import heapq

def min_meeting_rooms(intervals):
    intervals.sort(key=lambda x: x[0])      # start ke order me process
    heap = []                               # min-heap of end times
    for start, end in intervals:
        if heap and heap[0] <= start:       # earliest-ending room is free
            heapq.heappop(heap)             # reuse it
        heapq.heappush(heap, end)           # this meeting occupies a room
    return len(heap)                        # rooms in use at the peak
```

Min-heap hamesha **earliest-freeing room** O(log n) me deta hai. Heap me jitne end
times bachte hain utne concurrent rooms — aur kyunki hum start order me chal rahe,
heap ka final size hi peak concurrency hai.

> **Alternative — two sorted arrays (sweep line):** starts aur ends alag sort karke
> do pointers chalao. `start < end` → naya room (count++), warna ek free hua
> (count--, end pointer aage). `max(count)` = answer. Same O(n log n), no heap.

## Complexity

- **Time:** O(n log n) — sort + n heap operations (each O(log n)).
- **Space:** O(n) — heap me worst case saare end times (sab overlap karein to).

## Common Pitfalls

- **Heap ko pop karna jab room free nahi** — sirf tab pop karo jab `heap[0] <= start`.
  Warna count galat ho jaayega.
- **Touching meetings** — `[1,5]` aur `[5,8]`: room reuse hona chahiye. Condition
  `heap[0] <= start` (with `<=`), na ki `<`.
- **Start pe sort na karna** — meetings ko chronological order me process karna zaroori, warna "kaunsa room free hua" galat niklega.
- **`len(heap)` ke bajaye max-tracking** — kyunki hum har step pe at most ek pop aur exactly ek push karte hain, final `len(heap)` hi peak hai; alag max-counter ki zaroorat nahi.

## When to Use This Pattern

"**Kitne resources / max concurrency** chahiye overlapping intervals ke liye?" →
min-heap of end times (ya sweep-line on sorted starts/ends). Cue: "minimum rooms /
servers / CPUs", "maximum simultaneous". Cousins: Meeting Rooms (I), Car Pooling, Employee Free Time.

## Practice

- Visual: open `topics/intervals/meeting-rooms-ii/visual.html`

## NeetCode Link

https://neetcode.io/problems/meeting-schedule-ii
