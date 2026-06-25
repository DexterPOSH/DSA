# Spiral Matrix

**Category:** Math & Geometry
**Difficulty:** medium

## Problem Statement

Given an `m x n` matrix, return **all elements in spiral order** — start at the top-left, go right across the top, down the right side, left across the bottom, up the left side, then spiral inward.

```
[[1, 2, 3],
 [4, 5, 6],     ->  [1, 2, 3, 6, 9, 8, 7, 4, 5]
 [7, 8, 9]]
```

## Real-World Analogy

**What Azure AI Vision is:** Azure AI Vision is Azure's image-understanding service, and Azure Machine Learning commonly prepares image tensors before model inference or training. Large tensors are often processed through views or windows so a pipeline can read the needed pixels without copying the whole image. Spiral traversal is a boundary-window way to consume that matrix.

**What a shrinking crop window is, and why it's used:** A crop window tracks top, bottom, left, and right bounds around the active part of an Azure image tensor. After a boundary is processed, the window shrinks inward so the next pass works only on unvisited pixels. This exists to stream structured data in a predictable order while keeping just a few pieces of metadata instead of a visited set.

**The mapping:** The matrix is the Azure image tensor and the four variables are the crop-window metadata. Read the top row left-to-right, the right column top-to-bottom, the bottom row right-to-left if it still exists, and the left column bottom-to-top if it still exists; then tighten the bounds. The key insight is that moving boundaries encode what remains, so each cell is emitted once without extra storage.

## Approach

Char boundaries maintain karo: `top`, `bottom`, `left`, `right`. Har spiral layer ke liye chaar directions me traverse karo, aur har direction ke baad us boundary ko **andar khींch lo**:

1. **Left → right** along `top`, phir `top += 1`.
2. **Top → bottom** along `right`, phir `right -= 1`.
3. **Right → left** along `bottom` (agar `top <= bottom` abhi bhi valid hai), phir `bottom -= 1`.
4. **Bottom → top** along `left` (agar `left <= right`), phir `left += 1`.

Loop chalta rahe jab tak `top <= bottom` aur `left <= right`.

```python
def spiral_order(matrix):
    res = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):      # top row, L->R
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):      # right col, T->B
            res.append(matrix[r][right])
        right -= 1
        if top <= bottom:                     # bottom row, R->L
            for c in range(right, left - 1, -1):
                res.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:                     # left col, B->T
            for r in range(bottom, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    return res
```

## Complexity

- **Time:** O(m·n) — har cell exactly ek baar visit hota hai.
- **Space:** O(1) extra (output list ko chhodke) — sirf char boundary pointers.

## Common Pitfalls

- **Bottom-row aur left-column ke `if` checks chhodna** — non-square ya single-row/column matrices me top/right boundaries cross ho jaane ke baad bhi tum dobara same row/column traverse kar dete ho → duplicate values. Yeh sabse common bug hai.
- **Boundaries update karna bhulna** — direction cover karne ke baad boundary ko shrink na karo to infinite loop.
- **Range ke `+1 / -1` galat karna** — backward loops me `range(right, left - 1, -1)` chahiye taaki `left` bhi include ho.
- **Empty matrix / empty row** handle na karna — `matrix[0]` access se pehle empty check.

## When to Use This Pattern

Jab "traverse / fill a matrix in a layered, boundary-following order" dikhe — spiral, diagonal, ya ring-by-ring — to **shrinking boundary pointers** (`top/bottom/left/right`) socho. Same idea reverse me: Spiral Matrix II (1..n² ko spiral me bharna). Cue: "process the outer ring, then recurse/loop inward."

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough that traces the spiral path and shrinks the boundaries.

## NeetCode Link

https://neetcode.io/problems/spiral-matrix
