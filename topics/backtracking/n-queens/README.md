# N Queens

**Category:** Backtracking
**Difficulty:** hard

## Problem Statement

The **n-queens** puzzle: place `n` queens on an `n x n` chessboard so that **no
two queens attack each other**. A queen attacks along its row, column, and both
diagonals. Return all distinct board configurations (each as a list of strings
with `'Q'` and `'.'`).

```
n = 4  ->  two solutions:

  . Q . .        . . Q .
  . . . Q        Q . . .
  Q . . .        . . . Q
  . . . Q        . Q . .
  (".Q..","...Q","Q...","..Q.")   and its mirror
```

> `n = 2` aur `n = 3` ke **koi solution nahi** hote. `n = 1` trivially 1.

## Real-World Analogy

Socho tum ek **seating arrangement** bana rahe ho jahan har row me exactly ek
"diva" guest baithegi, lekin koi do divas ek doosre ko **direct line-of-sight**
(same column ya same diagonal) me nahi dekh sakti — warna drama ho jaata. Tum
row-by-row chalte ho: row 0 me koi safe column chuno, fir row 1 me aisa column jo
pichli divas se clash na kare, aur aage. Agar kisi row me **koi safe column nahi
bacha**, to seating dead-end hai — **pichli diva ko utha ke (backtrack)** dusri
seat pe baithao aur dobara try karo. Saari rows fill ho gayin → ek valid
arrangement mila.

## Approach — row-by-row placement with O(1) attack checks

Ek baar me ek **row** par ek queen rakho (har row me exactly ek queen, isliye
row-conflict automatically gone). Har row ke liye har column try karo jo **safe**
ho. Safety ko teen sets se O(1) me check karo:

- `cols` — kaun se columns already occupied.
- `diag` — `r - c` constant rehta hai ek `↘` diagonal pe.
- `anti` — `r + c` constant rehta hai ek `↙` (anti) diagonal pe.

```python
def solve_n_queens(n):
    res, board = [], [["."] * n for _ in range(n)]
    cols, diag, anti = set(), set(), set()

    def dfs(r):
        if r == n:
            res.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue                       # attacked -> prune
            cols.add(c); diag.add(r - c); anti.add(r + c)
            board[r][c] = "Q"
            dfs(r + 1)
            board[r][c] = "."                  # BACKTRACK
            cols.discard(c); diag.discard(r - c); anti.discard(r + c)

    dfs(0)
    return res
```

> **Diagonal identity yaad rakho:** cells on a `↘` diagonal share `r - c`; cells
> on a `↙` anti-diagonal share `r + c`. Yeh O(1) checks ka core trick hai — bina
> iske har placement pe O(n) scan lagta.

## Complexity

- **Time:** O(n!) worst case — row 0 me n choices, row 1 me ~(n-1) safe, etc.
  Diagonal/column pruning isse practically bahut chhota kar deta, par upper bound
  factorial hi rehta.
- **Space:** O(n) recursion depth + O(n) har set + O(n²) board (output alag).

## Common Pitfalls

- **Diagonal formula galat** — `r - c` (main) vs `r + c` (anti) confuse karna.
  Ek galat to two queens same diagonal pe aa jaayengi.
- **Backtrack me sab teen sets clean karna** + board cell restore — koi ek miss
  kiya to state corrupt, duplicate ya missing solutions.
- **Negative `r - c`** — set me daalo, no problem (Python sets handle negatives).
  Agar array index use kar rahe ho to offset `+n` lagana padta.
- **Row-conflict** ki alag check nahi chahiye — kyunki har `dfs(r)` me exactly ek
  queen place karte ho, do queens kabhi same row me aa hi nahi sakti.
- **`n=2,3`** pe empty result return hona normal hai — galat mat samajhna.

## When to Use This Pattern

"Constraints ke saath placement / arrangement, **conflict-free**, all solutions"
→ backtracking with incremental constraint sets. Cue: grid/board, mutual-exclusion
rules, "place all without conflict". Cousins: Sudoku Solver, N-Queens II (just
count), graph coloring. Mantra: place → check constraints in O(1) → recurse →
remove (backtrack).

## NeetCode Link

https://neetcode.io/problems/n-queens
