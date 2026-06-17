# Top K Frequent Elements

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given an integer array `nums` and an integer `k`, return the `k` most frequent
elements. The answer may be returned in any order.

Example: `nums = [1,1,1,2,2,3], k = 2` → `[1,2]` (1 appears 3×, 2 appears 2×).

## Real-World Analogy

A post office with PO boxes numbered by *how many letters arrived*. Box #3 holds
people who got 3 letters, Box #2 holds those who got 2, etc. To find the "top 2
busiest" you just read from the highest-numbered box downward until you have 2
names — no sorting needed, because the box number *is* the frequency. That's
bucket sort.

## Approach

1. **Frequency count** — build a `Counter`: `{1:3, 2:2, 3:1}`.
2. **Bucket by frequency** — make buckets indexed `0..n` (an element can appear at
   most `n` times). Place each number into `bucket[its_frequency]`:
   `bucket[3]=[1]`, `bucket[2]=[2]`, `bucket[1]=[3]`.
3. **Scan high → low** — walk buckets from highest frequency down, collecting
   numbers until `k` are gathered, then return.

```python
def topKFrequent(nums, k):
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)
    res = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            res.append(num)
            if len(res) == k:
                return res
```

## Complexity

- **Time:** O(n) — counting is O(n), bucket fill is O(n), scan is O(n). Beats the
  heap approach's O(n log k) because the bucket index replaces comparison sorting.
- **Space:** O(n) — the count map plus n+1 buckets.

## Common Pitfalls

- Bucket array must be size `len(nums) + 1` (frequency can reach `n`).
- Scan from high to low (`range(len-1, 0, -1)`), else you collect the least frequent.
- Early-return at `len(res) == k`; no need to scan all buckets.
- Heap alternative: maintain a size-k heap → O(n log k), valid but slower.

## When to Use

"Top K" / "K most frequent" / "K largest" problems, especially when counts are
bounded so bucket sort applies.

## Visual

Open `visual.html` in this directory for an interactive step-by-step walkthrough
(frequency map → buckets → high-to-low scan) with the PO-box analogy.

## NeetCode Link

https://neetcode.io/problems/top-k-elements
