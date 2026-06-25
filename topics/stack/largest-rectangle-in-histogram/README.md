# Largest Rectangle in Histogram

**Category:** Stack (Monotonic Stack)
**Difficulty:** hard

## Problem Statement

Given an array `heights` representing the heights of bars in a histogram (each bar
width `1`), find the **area of the largest rectangle** that can be formed within
the histogram.

```
heights = [2, 1, 5, 6, 2, 3]
->  10        # bars at index 2 and 3 (heights 5 and 6) -> width 2 x height 5 = 10
```

## Real-World Analogy

**What Azure Monitor is:** Azure Monitor stores time-series metrics for Azure resources, including compute usage, request counts, and capacity-related signals used by autoscale. Each metric is sampled into time buckets and can be viewed or queried over a continuous time range. For an autoscale group, you can think of those buckets as a capacity chart: each bucket says how much safe capacity was available during that slice of time.

**What minimum aggregation over a time window is, and why it's used:** Azure Monitor supports aggregations such as minimum, maximum, average, and total over metric windows. The minimum matters when you need a conservative guarantee across a continuous interval: the whole interval can only promise as much capacity as its lowest bucket. This exists because one weak bucket limits the safety of the entire window, just like the shortest histogram bar limits the height of any rectangle spanning it.

**The mapping:** Each histogram bar is one Azure Monitor capacity bucket; a rectangle is a continuous Azure time window; its height is the minimum capacity in that window and its width is the number of buckets. The monotonic increasing stack holds buckets whose right boundary is not known yet. When a lower bucket arrives, it proves that any taller pending bucket cannot extend farther right, so we pop that bucket and compute the widest window where it was the limiting minimum. The key insight is that a bar's best rectangle is computed exactly when Azure's next lower capacity sample reveals its right boundary.

## Approach

Store **indices** in the stack, and maintain heights in **non-decreasing (increasing)**
order. When a new bar arrives that is **shorter** than the bar at the stack top, the
top bar has found its **right boundary** (it cannot extend farther). Pop it and compute
its rectangle area:

- popped bar's **height** = `heights[popped]`
- **right boundary** = current index `i` (the bar stops here)
- **left boundary** = new stack-top index + 1 (from there onward, this bar was the shortest)
- **width** = `i - stack[-1] - 1` (if the stack is empty, width `= i`)

```python
def largest_rectangle_area(heights):
    stack = []                    # indices with increasing heights
    max_area = 0
    for i, h in enumerate(heights):
        # current bar chhota hai top se -> top bar ka right boundary yahin
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i - stack[-1] - 1 if stack else i
            max_area = max(max_area, height * width)
        stack.append(i)
    # bache hue bars: inka right boundary = end (n)
    n = len(heights)
    while stack:
        height = heights[stack.pop()]
        width = n - stack[-1] - 1 if stack else n
        max_area = max(max_area, height * width)
    return max_area
```

> **Sentinel trick (cleaner):** append a `0` to the end of `heights` — this removes
> the need for the final flush loop because `0` forces all bars to pop.

## Complexity

- **Time:** O(n) — each index is pushed exactly once and popped exactly once. Despite
  the `while` loop, the amortized work is linear.
- **Space:** O(n) — in the worst case (fully increasing histogram), all indices are on the stack.

## Common Pitfalls

- **Wrong width formula** — the most common bug. After the pop, use
  `i - stack[-1] - 1` (left boundary = new top), and if the stack becomes empty, width
  `= i` (the rectangle extends all the way left). Off-by-one errors here produce wrong areas.
- **Forgetting to flush remaining bars at the end** — in an increasing histogram
  (`[1,2,3,4]`), nothing pops inside the loop; all the work happens in the final
  `while` loop. If you skip it, the answer is wrong.
- **`>` vs `>=`** — use `heights[stack[-1]] > h` (strictly greater pop). It is fine
  to leave equal heights on the stack; the width is correctly accounted for later
  through the popped bar. `>=` can also work, but boundaries shift slightly — keep
  `>` for consistency.
- **Indices vs values** — width requires indices; values cannot produce distances.

## When to Use This Pattern

"For each element, how far can it extend left and right while it remains the dominant
(min/max) value?" → monotonic stack. Cue: histogram / skyline / "largest rectangle
or span where one element is the limiting factor." This problem is a building block:
**Maximal Rectangle** (2D binary matrix) treats each row as a histogram and calls this
same routine. Cousins: Trapping Rain Water, Daily Temperatures, Stock Span.

## Practice

- Visual: open `topics/stack/largest-rectangle-in-histogram/visual.html`

## NeetCode Link

https://neetcode.io/problems/largest-rectangle-in-histogram
