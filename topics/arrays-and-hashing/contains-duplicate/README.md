# Contains Duplicate

**Category:** Arrays & Hashing
**Difficulty:** easy

## Problem Statement

Given an integer array `nums`, return `True` if any value appears at least twice in the array, and `False` if every element is distinct.

## Real-World Analogy

Imagine you're a **bouncer at a club with a guest list**. As each person walks in, you check if you've already seen their name tonight. You could scan the entire list every time (slow), or you could keep a set of names you've already checked off — one glance tells you "seen this one before." That set of checked-off names is a **hash set**.

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
