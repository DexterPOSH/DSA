# Sliding Window Maximum

**Category:** Sliding Window
**Difficulty:** hard

## Problem Statement

Given an array `nums` and a window size `k`, the window slides from left to right one
position at a time. Return an array of the **maximum value in each window**.

```
nums = [1, 3, -1, -3, 5, 3, 6, 7],  k = 3
windows:  [1  3 -1]              -> 3
             [3 -1 -3]           -> 3
                [-1 -3  5]       -> 5
                   [-3  5  3]    -> 5
                      [5  3  6]  -> 6
                         [3  6  7] -> 7
answer = [3, 3, 5, 5, 6, 7]
```

## Real-World Analogy

**What Azure Stream Analytics with Azure Event Hubs is:** Azure Event Hubs ingests telemetry streams, and Azure Stream Analytics can compute real-time aggregates over those streams. A query can ask for the maximum value seen in each sliding time window, such as peak CPU, latency, or queue depth over the last five minutes. Azure emits a new aggregate as the window moves, while old events eventually expire from the active state.

**What a sliding-window maximum aggregate is, and why it's used:** The `MAX` over a sliding window answers "what is the highest measurement still inside the current window?" It exists because operations teams care about recent peaks, but recomputing the maximum by scanning every event in every overlapping window would waste work. A monotonic candidate list is the data-structure version of that aggregate: keep only values that could still become the maximum, discard expired ones, and discard smaller ones dominated by a newer larger value.

**The mapping:** Each number is an Azure Event Hubs telemetry measurement, and each length-`k` slice is the active Azure Stream Analytics window. The deque front is the current Azure `MAX`; indices falling out of the window are expired from the front, and smaller values at the back are removed when a larger measurement arrives because they can never win any future overlapping window. After the first full window, output the front for each slide. The key insight is that by storing only decreasing candidates, each element is pushed and popped at most once, giving O(n) instead of rescanning every window.

## Approach

**Monotonic deque holding indices.** Deque me hum *indices* rakhte hain a, aise ki unki
values **decreasing** order me hon. Invariant:
- **Front** index hamesha current window ka maximum.
- Naya element aate waqt, deque ke **back** se saare chhote/barabar elements pop karo
  (ab wo kabhi max nahi ban sakte).
- **Front** ko pop karo agar wo index window se bahar nikal gaya (`< right - k + 1`).

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()          # indices, values decreasing
    out = []
    for i, n in enumerate(nums):
        # 1) back se chhote elements hatao
        while dq and nums[dq[-1]] <= n:
            dq.pop()
        dq.append(i)
        # 2) front window se bahar? hatao
        if dq[0] <= i - k:
            dq.popleft()
        # 3) pehla full window ban gaya -> max record karo
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```

Brute force har window pe max scan karta = O(n·k). Deque har element ko at most **ek
baar push aur ek baar pop** karta — isliye total O(n).

## Complexity

- **Time:** O(n) — har index ek baar deque me jaata aur ek baar nikalta (amortized O(1)
  per step). Heap-based solution O(n log k) deta, deque usse fast hai.
- **Space:** O(k) — deque me at most `k` indices, plus O(n) output.

## Common Pitfalls

- **Values store karna instead of indices** — window se bahar nikalne ka check
  (`dq[0] <= i - k`) index ke bina possible hi nahi. Hamesha **indices** rakho.
- **`<` vs `<=` back-pop me** — `<=` use karo taaki equal values bhi pop ho jaayein;
  warna stale duplicates front pe atak sakte hain (correctness vajah se aksar dono
  chalte, par `<=` deque chhoti rakhta).
- **Output ko jaldi start karna** — pehla max tabhi push karo jab `i >= k - 1`, warna
  incomplete windows ka galat answer aa jaayega.
- **Front expire check ka order** — pehle naya push karo, phir front-expire check; ya
  consistent order rakho — galat order pe ek window slip ho sakti.
- **`k > len(nums)` / `k == 0`** edge cases ko sochna.

## When to Use This Pattern

"Har sliding window me max/min chahiye" ya "running max/min jisme purane elements expire
hote hain" — jab aisa dikhe to **monotonic deque** socho. Cousins: "shortest subarray
with sum ≥ K" (deque of prefix sums), stock-span, "jump game with window". Cue:
window + extremum + need O(n), na ki O(n·k).

## NeetCode Link

https://neetcode.io/problems/sliding-window-maximum
