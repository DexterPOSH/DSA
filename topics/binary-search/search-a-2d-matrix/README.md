# Search a 2D Matrix

**Category:** Binary Search
**Difficulty:** medium

## Problem Statement

Given an `m x n` matrix with two properties:
1. Each row is sorted left-to-right (ascending).
2. The **first integer of each row is greater than the last integer of the previous row**.

Return `True` if `target` is in the matrix, else `False`. Must run in `O(log(m·n))`.

```
matrix = [[1,  3,  5,  7],
          [10, 11, 16, 20],
          [23, 30, 34, 60]]
target = 16   ->  True
target = 13   ->  False
```

## Real-World Analogy

Dekho, woh do conditions ka matlab hai: agar tum matrix ki saari rows ko **end-to-end jod do, to ek single fully-sorted list** ban jaati hai — `[1,3,5,7,10,11,16,20,23,30,34,60]`. Yeh ek **library ki shelf** jaisa hai jahan books strictly serial-number order me lagi hain, bas alag-alag racks (rows) me. Tumhe pata hai book #16 kis rack me, kis position pe hogi — bina poora ghoome. Bas ek sorted list pe binary search, lekin index ko 2D coordinates me decode kar lena hai.

## Approach

Pattern: **binary search on a flattened virtual 1D array** — hum matrix ko physically flatten nahi karte (waste of space), bas index `mid` (0 se `m*n - 1`) ko on-the-fly row/col me convert karte hain:

- `row = mid // n`
- `col = mid % n`

```python
def search_matrix(matrix, target):
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = matrix[mid // n][mid % n]   # decode flat index -> 2D
        if val == target:
            return True
        elif val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
```

Bas yahi. Ek hi binary search, `O(log(m·n))`.

> **Alternative (do binary searches):** pehle column 0 pe binary search karke sahi *row* dhoondo (jahan `row[0] <= target <= row[-1]`), phir us row me dobara binary search. Same complexity `O(log m + log n) = O(log(mn))`, but flattened wala cleaner hai.

## Complexity

- **Time:** O(log(m·n)) — total `m*n` cells ek virtual sorted list hain, ek hi binary search pass.
- **Space:** O(1) — koi flatten copy nahi banaई, index arithmetic se decode.

## Common Pitfalls

- **`n` ki jagah `m` se divide/mod karna** — `row = mid // n` (cols count), `col = mid % n`. Agar `m` use kiya to galat cell. Yaad rakho: `n` = row ki width = number of columns.
- **`hi = m * n` (off by one)** — flat indices `0 … m*n - 1` hain, to `hi = m*n - 1`.
- **Empty matrix / empty row** — `matrix` ya `matrix[0]` empty ho to `len(matrix[0])` crash. Guard kar lo edge me.
- **Second property bhul jaana** — agar rows independently sorted hain but cross-row continuity nahi (e.g. har row ka first prev row ke last se chhota ho sakta), to yeh flatten trick fail. Tab "Search a 2D Matrix II" wala staircase approach chahiye.

## When to Use This Pattern

Jab grid/matrix **"fully sorted in row-major order"** ho aur `O(log)` search chahiye → "isko ek lambi 1D sorted list samjho" aur flat-index binary search lagao. Cue: 2D structure jisme global ordering ho, index encode/decode se 1D problem ban jaati hai.

## NeetCode Link

https://neetcode.io/problems/search-a-2d-matrix
