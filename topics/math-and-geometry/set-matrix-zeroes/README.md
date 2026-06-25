# Set Matrix Zeroes

**Category:** Math & Geometry
**Difficulty:** medium

## Problem Statement

Given an `m x n` matrix, if any element is `0`, set its **entire row and entire column** to `0`. Do it **in place**.

```
[[1, 1, 1],          [[1, 0, 1],
 [1, 0, 1],    ->     [0, 0, 0],
 [1, 1, 1]]           [1, 0, 1]]
```

The single `0` at `(1,1)` zeroes out row 1 and column 1.

## Real-World Analogy

**What Azure Resource Graph is:** Azure Resource Graph is Azure's service for querying resource inventory and configuration across subscriptions at scale. Teams can turn those query results into health matrices, such as availability zones by dependency type, to see where infrastructure problems are concentrated. The service helps reason over many resources without manually inspecting each one.

**What in-place fault marking is, and why it's used:** In a health matrix built from Azure Resource Graph data, a failed cell may imply that an entire zone row and dependency column should be flagged for action. But if you zero the row and column immediately, newly written zeroes look like original failures and create a false cascade. Marker storage exists to separate discovery from mutation: record which rows and columns are affected first, then clear them later.

**The mapping:** Each original `0` is an Azure health fault. The first row and first column become the marker storage for which rows and columns must be zeroed, while two booleans remember whether those marker lines were originally faulty themselves. After marking, the second pass clears marked cells, then handles the marker row and column, and the key insight is to reuse the matrix's own edge metadata to avoid extra space while preventing derived zeroes from triggering more zeroes.

## Approach

**Naive (O(m·n) space):** zeroes ke positions ko ek set me store karo, phir apply. Kaam karta hai par interviewer better maangega.

**Better (O(m+n) space):** do arrays — `zero_rows`, `zero_cols` — me mark karo, phir apply.

**Optimal (O(1) space) — matrix ki apni first row/column ko markers banao:**

1. Pehle check karo kya **first row** aur **first column** me khud koi 0 hai (do boolean flags me yaad rakho).
2. Baaki matrix scan karo; agar `matrix[i][j] == 0`, to uska marker set karo: `matrix[i][0] = 0` aur `matrix[0][j] = 0`.
3. Dobara inner matrix scan karo; agar `matrix[i][0] == 0` **ya** `matrix[0][j] == 0`, to `matrix[i][j] = 0`.
4. Aakhir me, un do flags ke hisaab se first row / first column ko zero karo.

```python
def set_zeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    first_row = any(matrix[0][j] == 0 for j in range(n))
    first_col = any(matrix[i][0] == 0 for i in range(m))

    for i in range(1, m):                 # mark using row0 / col0
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0

    for i in range(1, m):                 # apply markers
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0

    if first_row:
        for j in range(n): matrix[0][j] = 0
    if first_col:
        for i in range(m): matrix[i][0] = 0
```

First row aur column ko **alag se** isliye handle karte hain kyunki woh dono khud markers hain — agar unko inline zero kar diya to apne hi markers corrupt ho jaate.

## Complexity

- **Time:** O(m·n) — matrix ke do passes.
- **Space:** O(1) — first row/column ko markers ki tarah reuse kiya; sirf do boolean flags.

## Common Pitfalls

- **Pehle pass me hi zero karna** — naya 0 likhoge to second pass usko "original" samajh ke aur cells wipe kar dega. Hamesha mark karo, phir apply.
- **First row/column flags ko handle na karna** — woh dono markers hain, isliye unka apna zero-status alag se yaad rakhna padta hai.
- **First row/column ko galat order me zero karna** — markers padhne se pehle unko clear kar dिया to baaki cells galat ho jaayenge. Inko sabse last me karo.
- **`(0,0)` cell ka overlap** — `matrix[0][0]` row0 aur col0 dono ke liye marker ban sakta hai; isiliye do **alag** flags chahiye, ek shared cell pe bharosa mat karo.

## When to Use This Pattern

Jab "in-place matrix modification where writes can interfere with future reads" dikhe — to socho: kya input ke kisi hisse ko hi **scratch / marker storage** bana sakte hain? Yeh "use the matrix itself as O(1) auxiliary state" trick game of life, image rotation, aur in-place DP me bhi aata hai. Cue: "modify in place + O(1) space + ek cell ka decision doosri cells pe depend karta hai."

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the O(1)-space marker approach.

## NeetCode Link

https://neetcode.io/problems/set-zeroes-in-matrix
