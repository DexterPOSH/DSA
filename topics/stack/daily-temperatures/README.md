# Daily Temperatures

**Category:** Stack (Monotonic Stack)
**Difficulty:** medium

## Problem Statement

Given an array `temperatures` of daily temperatures, return an array `answer` such
that `answer[i]` is the **number of days you have to wait** after day `i` to get a
warmer temperature. If there is no future day that is warmer, `answer[i] = 0`.

```
temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
answer        = [ 1,  1,  4,  2,  1,  1,  0,  0]
```

Day 0 (73) → next warmer is day 1 (74), wait 1 day.
Day 2 (75) → next warmer is day 6 (76), wait 4 days.
Day 6 (76) → no later day is warmer → 0.

## Real-World Analogy

**What Azure Monitor autoscale is:** Azure Monitor collects metrics and logs from Azure resources, and its autoscale feature uses those metrics to adjust capacity for services such as Virtual Machine Scale Sets and App Service plans. Instead of guessing capacity manually, you define rules like "if CPU stays high, add instances" or "if load drops, remove instances." The service keeps watching the metric stream and reacts when future samples prove a rule should fire.

**What threshold evaluation is, and why it's used:** An autoscale rule compares metric samples, often aggregated over a time window, against a configured threshold. The threshold exists to turn a noisy time series into a clear operational decision: do not scale on every random blip, but do scale when a later sample/window crosses the line. In this analogy, each earlier temperature is a pending threshold asking, "when will a future Azure metric sample be higher than me?"

**The mapping:** Each day is one Azure Monitor metric sample, and the answer array is the wait time until that sample is exceeded. The monotonic stack stores unresolved sample indices in decreasing temperature order, so cooler pending samples sit on top. When a warmer sample arrives, it pops every cooler sample it surpasses and records `current_index - previous_index`; anything left on the stack never saw a higher future metric, so it stays `0`. The key insight is that each sample waits on the stack exactly until the first later sample that beats it.

## Approach

Store **indices** in the stack (not values) so we can compute the distance `i - prev`.
Maintain the stack in **strictly decreasing temperature** order.

Understand the brute force first to appreciate the optimal solution: for each `i`,
scan forward with `j` until you find the first warmer day → O(n²).

**Optimal — monotonic decreasing stack** (O(n)):

```python
def daily_temperatures(temperatures):
    answer = [0] * len(temperatures)
    stack = []                       # holds indices; temps at these indices are decreasing
    for i, temp in enumerate(temperatures):
        # current temp warmer hai stack-top wale din se? -> uska answer mil gaya
        while stack and temp > temperatures[stack[-1]]:
            prev = stack.pop()
            answer[prev] = i - prev  # kitne din wait karna pada
        stack.append(i)
    return answer
```

Push each day onto the stack. When a new day arrives and is **warmer** than the
day at the stack top, that older day's wait is over — pop it and write the
distance `i - prev`. Days still left on the stack at the end never found a warmer
future day, so their answer remains `0` (already initialized).

## Complexity

| Approach | Time | Space | Why |
|----------|------|-------|-----|
| Brute force | O(n²) | O(1) | Each day scans everything ahead of it |
| **Monotonic stack** | **O(n)** | **O(n)** | Each index is pushed **exactly once** and popped once |

- **Time:** O(n) — even though there is a `while` loop, each index is pushed once
  and popped once during its lifetime. The amortized total work is linear.
- **Space:** O(n) — in the worst case (strictly decreasing temperatures, such as
  `[80,70,60]`), all indices sit on the stack at the same time.

## Common Pitfalls

- **Pushing values instead of indices** — you need the index to compute the distance
  `i - prev`. If you store only values, you cannot calculate "how many days."
- **`>=` vs `>`** — the problem asks for strictly warmer days, so use
  `temp > temperatures[stack[-1]]`. If you use `>=`, you incorrectly treat equal
  temperatures as "warmer."
- **Using `if` instead of `while`** — one new warmer day can answer **many** previous
  days on the stack. `if` pops only the top one → incorrect answers.
- **Forgetting to leave remaining stack indices as zero** — if `answer` is not
  initialized with `0`, leftover days will keep garbage values.

## When to Use This Pattern

"For each element, find the **next greater / next smaller / previous greater** element
(or its distance)" → this is a classic **monotonic stack** signal. When brute force
looks like O(n²) and you are searching for a "next bigger thing to the right"
relationship, keep the elements whose answer is still pending on the stack. Cousins:
Next Greater Element, Stock Span, Largest Rectangle in Histogram.

## Practice

- Visual: open `topics/stack/daily-temperatures/visual.html`

## NeetCode Link

https://neetcode.io/problems/daily-temperatures
