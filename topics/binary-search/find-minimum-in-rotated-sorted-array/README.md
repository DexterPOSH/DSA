# Find Minimum in Rotated Sorted Array

**Category:** Binary Search
**Difficulty:** medium

## Problem Statement

A sorted (ascending, distinct) array has been **rotated** between `1` and `n` times. E.g. `[0,1,2,4,5,6,7]` rotated 4 times becomes `[4,5,6,7,0,1,2]`. Given such an array, return the **minimum element** in `O(log n)` time.

```
[3, 4, 5, 1, 2]       ->  1
[4, 5, 6, 7, 0, 1, 2] ->  0
[11, 13, 15, 17]      ->  11   (rotated n times = back to sorted)
```

## Real-World Analogy

Socho ek **ghadi (clock face)** pe numbers 1→12 likhe hain, phir kisi ne dial ko thoda ghuma diya. Ab ek hi "**cliff**" (giraav) hai jahan bada number ke turant baad sabse chhota aata hai — jaise `7` ke baad `0`. Woh cliff ka bottom hi minimum hai. Tumhe pure circle pe ghoomne ki zaroorat nahi: beech me dekho aur poochho — "kya mai abhi cliff ke pehle wale (oonche) part me hoon, ya baad wale (neeche) part me?" Jis taraf cliff hai, usi taraf jao. Har step me aadha kaat do.

## Approach

Pattern: **binary search using the "which half is sorted" invariant**. Rotated array do sorted halves me bata hota hai. Trick: `nums[mid]` ko **`nums[hi]`** (right end) se compare karo — `lo` se nahi.

- Agar `nums[mid] > nums[hi]` → minimum `mid` ke **right** me hai (cliff aage hai). `lo = mid + 1`.
- Agar `nums[mid] <= nums[hi]` → `mid` se `hi` tak portion sorted hai, to minimum `mid` *par ya uske left* me hai. `hi = mid` (mid ko discard mat karo — woh khud min ho sakta).

```python
def find_min(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1        # min strictly to the right of mid
        else:
            hi = mid            # min at mid or to its left
    return nums[lo]             # lo == hi == index of minimum
```

> **`nums[hi]` se compare kyun, `nums[lo]` se nahi?** Right end hamesha reliable signal deta. Agar fully-sorted (no rotation), `nums[mid] <= nums[hi]` har baar true → `hi` ghatega → `lo` index 0 (first element) pe land karega = correct min. `nums[lo]` se compare karne me yeh edge case extra handling maangta.

## Complexity

- **Time:** O(log n) — har comparison me search space half. Single pass.
- **Space:** O(1) — do pointers, koi extra memory nahi.

## Common Pitfalls

- **`nums[mid]` ko `nums[lo]` se compare karna** — fully-sorted aur kuch rotations me galat branch. `nums[hi]` reliable hai; usi se compare karo.
- **`lo <= hi` (with `=`) use karna** — yeh boundary-find loop hai; `lo < hi` chahiye, warna `hi = mid` ke saath infinite loop (window shrink hi nahi hoga jab `lo == hi`).
- **`hi = mid - 1` likh dena** — `mid` khud minimum ho sakta, usse skip kar diya to answer miss. Boundary search me `hi = mid`.
- **`>=` vs `>`** — distinct elements assume hain. `nums[mid] > nums[hi]` (strict) sahi. Duplicates wali variant ("II") alag handling maangti.

## When to Use This Pattern

Cue: **"rotated sorted array"** ya "sorted array jisme ek discontinuity / pivot hai" + `O(log n)`. Jab array piecewise-sorted ho, har step me **"konsa half clean (sorted) hai"** decide karke wahi half discard/keep karo. Cousins: Search in Rotated Sorted Array, Find Peak Element — sab "modified binary search on a non-trivially-monotonic structure".

## NeetCode Link

https://neetcode.io/problems/find-minimum-in-rotated-sorted-array
