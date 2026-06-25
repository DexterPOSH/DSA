# Contains Duplicate

**Category:** Arrays & Hashing
**Difficulty:** easy

## Problem Statement

Given an integer array `nums`, return `True` if any value appears at least twice in the array, and `False` if every element is distinct.

## Real-World Analogy

**What Azure Cache for Redis is:** Azure Cache for Redis is Azure's managed Redis service: an in-memory data store built for very fast key lookups, counters, and lightweight coordination. Apps use it when they need an answer like "have I seen this ID before?" without scanning a database table or list. Because Redis stores keys in hash-table-like structures, membership checks are effectively constant time for normal workloads.

**What SETNX is, and why it's used:** `SETNX` means "set this key only if it does not already exist." Redis performs that check-and-write atomically, so the first caller creates the key and every later caller can tell the key was already present. Azure workloads use this pattern for deduplication, idempotency tokens, and simple locks because it turns "is this new?" into one safe operation instead of a slow scan plus a race-prone insert.

**The mapping:** Each number in the array is like a VM instance ID being written as a Redis key. If `SETNX(num)` succeeds, the number is new, so the algorithm keeps going; if it fails, that key already exists, so we found a duplicate and return `true`. The key insight is that a hash set gives the same direct membership test as Azure Cache for Redis: remember what you've seen, then stop the instant a repeat appears.
## Approach

**Brute force** — compare every pair (O(n²)):
```python
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] == nums[j]:
            return True
```

**Optimal — hash set** (O(n)):
```python
def contains_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

Walk through the array once. For each number, ask "have I seen this before?" — set lookup is O(1).

## Complexity

| Approach | Time | Space | Why |
|----------|------|-------|-----|
| Brute force | O(n²) | O(1) | Every pair compared |
| Sort first | O(n log n) | O(1) | Duplicates become adjacent |
| **Hash set** | **O(n)** | **O(n)** | One pass, O(1) lookups |

## Common Pitfalls

- **Using a list instead of a set** — `if num in my_list` is O(n), making the overall approach O(n²)
- **Forgetting the sort approach** — if interviewer says "no extra space", sort then check adjacent elements
- **One-liner shortcut** — `return len(nums) != len(set(nums))` works but interviewer usually wants the explicit loop

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the hash set approach.

## NeetCode Link

https://neetcode.io/problems/duplicate-integer
