# Rotate Image

**Category:** Math & Geometry
**Difficulty:** medium

## Problem Statement

You are given an `n x n` 2D matrix representing an image. Rotate it **90 degrees clockwise, in place** — you must modify the input matrix directly, without allocating another `n x n` matrix.

```
[[1,2,3],          [[7,4,1],
 [4,5,6],    ->     [8,5,2],
 [7,8,9]]           [9,6,3]]
```

Notice the first **column** (1,4,7), read bottom-to-top, becomes the first **row** (7,4,1).

## Real-World Analogy

Socho ek photo frame deewar pe ulta-seedha tanga hai aur usko tumhe 90° clockwise ghumana hai — bina deewar pe doosri keel thoke (no extra matrix). Photo studio wala ek neat trick use karta hai: pehle photo ka **mirror diagonal pe fold** karta hai (rows aur columns swap — transpose), phir har row ko **horizontally flip** karta hai. Do simple foldings ka combination = perfect 90° rotation. Koi naya frame nahi chahiye, sab kuch usi frame ke andar ho jaata hai.

## Approach

Direct rotation formula yaad rakhna mushkil hai (`new[j][n-1-i] = old[i][j]`). Iske bajaye **do aasaan steps** me todo — yahi interview ka clean answer hai:

**Step 1 — Transpose** (diagonal pe flip): har `matrix[i][j]` ko `matrix[j][i]` se swap karo. Sirf upper triangle (`j > i`) pe loop chalao, warna har swap do baar ho jaayega aur tum wapas wahi matrix paaoge.

**Step 2 — Reverse each row** (horizontal flip): har row ko ulta kar do.

```python
def rotate(matrix):
    n = len(matrix)
    # Step 1: transpose (swap across main diagonal)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # Step 2: reverse each row
    for row in matrix:
        row.reverse()
```

Transpose ke baad `[[1,4,7],[2,5,8],[3,6,9]]` milta hai; har row reverse karne ke baad `[[7,4,1],[8,5,2],[9,6,3]]` — exactly clockwise rotated. (Anticlockwise chahiye? Reverse the rows first, then transpose — ya columns ko flip karo.)

## Complexity

- **Time:** O(n²) — har cell ko ek baar touch karna hi padega; n² cells hain.
- **Space:** O(1) — sab kuch in-place swaps se, koi extra matrix nahi.

## Common Pitfalls

- **Transpose me poora grid loop karna** (`j` ko `0` se chalana) — har pair do baar swap ho jaata aur matrix unchanged rehti. `j` ko `i+1` se start karo.
- **Reverse step bhulna** — sirf transpose karne se anti-diagonal mirror milta hai, rotation nahi.
- **Clockwise vs anticlockwise confuse karna** — clockwise = transpose + reverse rows; anticlockwise = transpose + reverse columns (ya rows reverse karke transpose).
- **Extra matrix bana lena** — kaam to karega par "in place" constraint fail. Interviewer specifically O(1) space dekhna chahta hai.
- **Non-square pe yeh trick** lagana — transpose+reverse sirf square `n x n` pe in-place 90° deta hai.

## When to Use This Pattern

Jab bhi "rotate / flip / transpose a matrix in place" dikhe — sochо ki kya kaam ko **multiple simple geometric ops** (transpose, row-reverse, column-reverse) me tod sakte ho. Index gymnastics yaad rakhne se kahin behtar hai do clean passes. Cousins: rotate by 180° (reverse rows + reverse columns), spiral traversal, diagonal traversal.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the transpose-then-reverse approach.

## NeetCode Link

https://neetcode.io/problems/rotate-matrix
