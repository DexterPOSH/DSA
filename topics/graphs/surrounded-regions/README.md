# Surrounded Regions

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

Given an `m x n` board of `'X'` and `'O'`, **capture** all regions that are **4-directionally surrounded** by `'X'`. A region of `'O'`s is captured (flipped to `'X'`) if it is **not connected to any `'O'` on the border**. Modify the board in-place.

```
X X X X            X X X X
X O O X     ->     X X X X
X X O X            X X X X
X O X X            X O X X
```

The middle `O`s are fully surrounded → flipped. The bottom-left `O` touches the border → survives.

## Real-World Analogy

Socho ek board game hai jisme tumhe woh `O` territories "capture" karni hain jo poori tarah `X` se gher li gayi hain. Catch: jo `O` board ke **kinaare (border)** ko chhoo raha hai, ya kinaare wale `O` se juda hai, woh **safe** hai — uske paas "bahar bhaagne ka raasta" hai, isliye capture nahi hoga. Smart trick: seedha surrounded `O`s dhoondhne ki jagah, **border se ulta socho** — saare border-touching `O`s ko flood-fill karke "safe" (temporary `#`) mark kar do. Jo bach gaye (still `O`) woh definitely surrounded hain → `X` kar do. Safe wale `#` ko wapas `O` kar do.

## Approach

Pattern: **flood-fill from the borders to find the "escapees"**, then a final sweep flips the rest. (Reverse thinking, just like Pacific Atlantic.)

1. Board ke chaaron border pe har `'O'` se DFS chalakr connected `'O'`s ko temporary `'#'` (safe) mark karo.
2. Poora board sweep karo: bacha hua `'O'` → `'X'` (surrounded, capture), `'#'` → `'O'` (safe, restore).

```python
def solve(board):
    if not board:
        return
    rows, cols = len(board), len(board[0])

    def guard(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != "O":
            return
        board[r][c] = "#"                       # mark border-connected as safe
        guard(r+1, c); guard(r-1, c); guard(r, c+1); guard(r, c-1)

    for r in range(rows):
        guard(r, 0); guard(r, cols-1)           # left & right borders
    for c in range(cols):
        guard(0, c); guard(rows-1, c)           # top & bottom borders

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == "O":
                board[r][c] = "X"               # surrounded -> capture
            elif board[r][c] == "#":
                board[r][c] = "O"               # safe -> restore
```

> Direct "is this region surrounded?" check har region ke liye mushkil hai (escape detection). Border-flood ulta-flip karke problem ko ek simple 2-pass me reduce kar deta hai.

## Complexity

- **Time:** O(m·n) — border flood har safe cell ko ek baar chhoota, fir ek full sweep.
- **Space:** O(m·n) worst case — DFS recursion stack.

## Common Pitfalls

- **Seedha surrounded region dhoondhne ki koshish** — escape-route detection ulajh jaata hai. Hamesha **border se safe-mark** karo, fir invert.
- **Temporary marker conflict** — `'#'` aisa char ho jo board me na ho. Phase 2 me `'#' -> 'O'` restore karna mat bhoolo.
- **Sirf corners flood karna** — poore border (top+bottom rows, left+right cols) se flood karo, sirf 4 corners se nahi.
- **In-place modify** — problem board ko jagah pe badalne ko kehta hai; naya board return mat karo (jab tak signature na maange).
- **Empty board / single row** — `not board` guard; single-row/col me har `O` border pe hai → kuch capture nahi hota.

## When to Use This Pattern

Jab "regions jo boundary tak nahi pahunchti unhe flip/capture/remove karo" dikhe → **border se flood-fill, safe mark karo, fir invert.** Cue: "enclosed/surrounded by ..." → directly enclosed find mat karo; reachable-from-border ko nikaalo aur complement lo. Cousins: Pacific Atlantic, Number of Enclaves.

## NeetCode Link

https://neetcode.io/problems/surrounded-regions
