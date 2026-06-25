# Product of Array Except Self

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, return an array `output` where `output[i]` is the **product of every element except `nums[i]`**. You must solve it **without using division**, and in **O(n)** time.

```
nums   = [1, 2, 3, 4]
output = [24, 12, 8, 6]
# output[0] = 2*3*4 = 24, output[1] = 1*3*4 = 12, output[2] = 1*2*4 = 8, output[3] = 1*2*3 = 6
```

## Real-World Analogy

**What Azure Data Factory/Synapse pipeline processing is:** Azure Data Factory orchestrates data movement and transformation pipelines, while Azure Synapse runs large-scale analytics jobs over ordered datasets. Together, they are often used to process rows in a defined order and write derived columns for downstream consumers. For this problem, each row needs context from everything before it and everything after it, but not from itself.

**What an ordered aggregate pass is, and why it's used:** An ordered aggregate pass walks a partition in sequence and carries a running value, such as a cumulative total or product, from one row to the next. Pipelines use this pattern when a row's output depends on neighboring history without needing an expensive self-join for every row. Running one pass forward and one pass backward also avoids division, which matters when zeros make division-based shortcuts unsafe.

**The mapping:** The forward Azure-style pass writes the product of all numbers to the left of each index; the backward pass multiplies in the product of all numbers to the right. Since the current row is skipped in both carried values, its own number never contaminates its answer. The key insight is to split "everything except me" into two ordered aggregates — prefix and suffix — then combine them in place.
## Approach

In brute force, for each `i` you multiply every other element = O(n²). You might think of using division with total product / nums[i] — but that **breaks when zeros are present**, and the problem forbids division.

**Optimal — prefix × suffix products** (O(n) time, O(1) extra space):

Each `output[i]` = (product of everything before `i`) × (product of everything after `i`). Use two passes:

1. **Left-to-right:** store the running product of everything to the **left** of `i` in `output[i]`.
2. **Right-to-left:** keep a `suffix` variable, multiply `output[i]` by that suffix, then update the suffix.

```python
def product_except_self(nums):
    n = len(nums)
    output = [1] * n

    prefix = 1                       # i ke left ka product
    for i in range(n):
        output[i] = prefix
        prefix *= nums[i]

    suffix = 1                       # i ke right ka product
    for i in range(n - 1, -1, -1):
        output[i] *= suffix
        suffix *= nums[i]

    return output
```

Reuse the output array to store prefixes, so extra space is O(1) (the output array does not count). Pattern: **prefix/suffix accumulation**.

## Complexity

- **Time:** O(n) — just two linear passes, with no nested loop.
- **Space:** O(1) extra — only two scalar variables (`prefix`, `suffix`) besides the output array. (The output array does not count.)

## Common Pitfalls

- **Using division** — it is explicitly banned, and if the array contains **zero**, division breaks or gives the wrong result. The prefix/suffix approach handles zeros naturally.
- **Resetting output during the suffix pass** — in the second pass, use `output[i] *= suffix` (multiply), not `=`; otherwise, you erase the prefix from the first pass.
- **Not starting prefix/suffix at 1** — the multiplicative identity is `1`. If you start at `0`, everything becomes zero.
- **Building extra prefix/suffix arrays** — it works, but costs O(n) space; reusing the output array keeps extra space at O(1).
- **Using an array instead of a single suffix variable** — beginners often build two full arrays, but one running scalar is enough.

## When to Use This Pattern

When each index needs **"the aggregate of everything except this index"** or **"some left-side information combined with some right-side information"** — think **prefix + suffix scan**. Range products/sums, running totals from both ends, and before-and-after information at each position all become O(n) with two directional passes.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the prefix and suffix passes.

## NeetCode Link

https://neetcode.io/problems/products-of-array-discluding-self
