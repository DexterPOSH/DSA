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

**What Azure Cosmos DB is:** Azure Cosmos DB is a distributed NoSQL database that partitions data for scale while indexing items inside each partition for fast lookup. A query often has two levels of narrowing: route to the relevant partition key range, then use the local index to find the item. That keeps a lookup from becoming a scan across every partition and every document.

**What a two-level index seek is, and why it's used:** A two-level seek means the router first uses ordered partition-range metadata to choose the right shard of data, then the storage engine uses that shard's index to seek to the position inside it. It exists because distributed databases need both global routing and local lookup efficiency. When each partition range starts after the previous one ends, the ranges form one globally ordered view even though the data is physically grouped.

**The mapping:** Each matrix row is an Azure Cosmos DB partition range, each column position is an offset inside that range, and the row-major rule makes all cells one virtual sorted index. Binary search probes a flat `mid`, decodes it with `row = mid // n` and `col = mid % n`, then compares `matrix[row][col]` with the target. The key insight is that you do not need to flatten the matrix; index arithmetic gives the same ordered seek while letting each comparison discard half of the virtual index.
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
