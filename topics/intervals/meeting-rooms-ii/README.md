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

Socho tum ek office manager ho. Meetings start-time ke order me aati hain. Har nayi
meeting ke liye poochho: **kya koi room abhi free ho chuka hai?** — yaani kya pichhli
kisi meeting ka end time is nayi meeting ke start se pehle (ya barabar) hai? Iske liye
tum ek **min-heap of end times** rakhte ho — heap ki jad (root) hamesha woh meeting
hai jo **sabse pehle khatam** hogi.

- Nayi meeting aayi → heap ke sabse jaldi-khatam-hone-wale end ko dekho.
- Agar woh `<= nayi.start` → woh room free ho gaya, **pop** karo (reuse).
- Phir nayi meeting ka end heap me **push** karo.

Heap ka **maximum size** kabhi jo pahuncha — wahi rooms ka answer.

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
