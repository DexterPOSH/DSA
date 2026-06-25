# Two Sum

**Category:** Arrays & Hashing
**Difficulty:** easy

## Problem Statement

Given an array of integers `nums` and an integer `target`, return the **indices** of the two numbers that add up to `target`. Exactly one valid pair exists, and you can't use the same element twice.

```
nums = [2, 7, 11, 15], target = 9   ->  [0, 1]   # 2 + 7 == 9
nums = [3, 2, 4],       target = 6   ->  [1, 2]   # 2 + 4 == 6
```

## Real-World Analogy

**What Azure Cache for Redis is:** Azure Cache for Redis is Azure's managed Redis service for low-latency key-value lookups. Services put small pieces of data in Redis when they need to answer "do we already have this exact key?" in milliseconds. In Two Sum, the useful key is a number we've already passed in the stream.

**What key-value GET/SET lookup is, and why it's used:** Redis `GET` retrieves the value stored for an exact key, and `SET` records a key for future requests. That model exists so callers can jump straight to the record they need instead of scanning every previous record. Storing `number -> index` in Azure Cache for Redis would let a telemetry processor instantly ask whether the complement it needs has already arrived.

**The mapping:** For each value `x`, compute `target - x` and do a Redis-style lookup for that complement. If it exists, the stored value is the earlier index and the pair is complete; otherwise store `x -> current index` so a later number can find it. The key insight is to cache the past in a hash map, so each new number needs one Azure-style lookup instead of comparing against everything before it.
## Approach

**Brute force** — try every pair (O(n²)):

```python
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
```

**Optimal — hash map (one pass)** (O(n)):

The idea is simple — for each number `n`, we need `target - n` (the complement). As we scan the array, maintain a dictionary `seen` that maps *value -> index*. For each number, first check whether its complement is already in `seen`; if it is, we found the pair, so return the indices. Otherwise, store the current number in `seen` and keep going.

```python
def two_sum(nums, target):
    seen = {}                      # value -> index
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []                      # problem guarantees a pair, par safe rahna
```

Pattern: **hash map for complement lookup** — one pass, with each lookup taking O(1).

## Complexity

- **Time:** O(n) — scan the array once, with each dictionary lookup/insert taking O(1) on average.
- **Space:** O(n) — in the worst case, the entire array is stored in `seen` before the pair is found.

## Common Pitfalls

- **Using the same element twice** — you must check `complement in seen` **before** adding the current number. That prevents pairing a number with itself (e.g. `target = 2*n`).
- **Values vs indices** — the problem asks for indices, not values. Store value -> index in the dictionary, not the reverse.
- **Duplicate values** — if `nums` contains the same value twice (such as `[3, 3]`, target `6`), the value -> index map still works because the complement matches a previously seen index.
- **Sorting with two pointers** — this works and gives O(1) extra space, but sorting loses the original indices unless you track them separately. When indices are required, a hash map is cleaner.

## When to Use This Pattern

When you see *"find two (or k) elements whose relation/sum/difference equals a target"* — immediately think **hash map of complements**. "Pair that sums to X", "two numbers have difference k", and "does some `a` exist such that `target - a` is present" can all be solved with one-pass hash lookups in O(n), without an O(n²) nested loop.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the one-pass hash map approach.

## NeetCode Link

https://neetcode.io/problems/two-integer-sum
