# Longest Consecutive Sequence

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given an unsorted integer array `nums`, return the length of the **longest run of consecutive integers** (e.g. `4, 5, 6, 7`). The numbers can appear in any order in the array. You must do it in **O(n)** time.

```
nums = [100, 4, 200, 1, 3, 2]   ->  4    # the run 1,2,3,4 has length 4
nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]  ->  9   # 0..8
```

## Real-World Analogy

**What Azure Resource Graph is:** Azure Resource Graph is Azure's service for querying resource inventory across subscriptions at scale. Instead of calling each VM, NIC, or virtual network one by one, teams can run a Kusto-style query and get a current view of resources and properties. For IP analysis, that means collecting the private addresses currently allocated to NICs in a VNet.

**What a resource inventory query is, and why it's used:** A Resource Graph query turns scattered Azure resources into a searchable set of records, such as all allocated private IP addresses. This exists because cloud estates are too large to inspect manually or by repeated per-resource API calls. Once the addresses are in a set, range detection becomes a membership problem: "does the previous or next address exist?"

**The mapping:** Put every number into a hash set just like collecting every allocated IP from Azure Resource Graph. Only start counting from a number whose predecessor is missing, because that number is the beginning of a consecutive range; then keep checking `num + 1`, `num + 2`, and so on until lookup fails. The key insight is that by walking only from true range starts, each value belongs to one scan, so fast membership checks keep the work linear.
## Approach

Naive: sort and compare adjacent values → O(n log n). We want O(n).

**Optimal — hash set + start-of-run detection** (O(n)):

1. Put all numbers into a `set` → O(1) membership checks.
2. For each number `n`, check whether `n - 1` is **not** in the set. If it is not, then `n` is the **start** of a run.
3. Count forward only from starts: `n, n+1, n+2…` as long as each value exists in the `set`. Track the length and update the maximum.

```python
def longest_consecutive(nums):
    num_set = set(nums)
    longest = 0

    for n in num_set:
        if n - 1 not in num_set:          # n is the start of a run
            length = 1
            while n + length in num_set:  # walk the run forward
                length += 1
            longest = max(longest, length)
    return longest
```

Crucial: the inner `while` loop runs only when `n` is a start. That means each full chain is walked only once overall — O(n), not n². Pattern: **hash set + only-extend-from-boundaries**.

## Complexity

- **Time:** O(n) — building the set is O(n); each `n-1` check is O(1); and across all starts, the inner while loop touches each element at most once.
- **Space:** O(n) — all numbers are stored in the set.

## Common Pitfalls

- **Skipping the start check** — if you count forward from every number without the start check, the inner loop repeatedly walks overlapping chains → **O(n²)**. `if n - 1 not in set` is what makes it O(n).
- **Sorting** — it gives the correct answer, but it is O(n log n); interviewers often explicitly ask for O(n).
- **Duplicates** — `set` automatically deduplicates values, so duplicates do not inflate the length. (Using a list can cause bugs.)
- **Empty array** — start with `longest = 0` so empty input returns `0`.
- **Confusing index vs value in `while n + length in num_set`** — here, `n + length` is the *value* you are looking for in the set, not an array index.

## When to Use This Pattern

When you need to find the **"longest consecutive / contiguous run"** in unsorted data, or determine whether elements form a continuous range without sorting, think **hash set + extend-only-from-boundaries**. The trick is to put values in a set for O(1) membership, then start work only from boundaries (run starts) so each element is processed once.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough that finds run-starts and walks each chain forward.

## NeetCode Link

https://neetcode.io/problems/longest-consecutive-sequence
