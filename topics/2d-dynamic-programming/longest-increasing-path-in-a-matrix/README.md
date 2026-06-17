# Longest Increasing Path in a Matrix

**Category:** 2-D Dynamic Programming
**Difficulty:** hard

## Problem Statement

Given an `m x n` integer matrix, return the length of the **longest strictly
increasing path**. From any cell you may move **up, down, left, or right** (no
diagonals, no wrapping). You may start and end anywhere.

```
matrix = [[9, 9, 4],
          [6, 6, 8],
          [2, 1, 1]]            ->  4    # path 1 -> 2 -> 6 -> 9
```

## Real-World Analogy

Socho ye grid ek **terrain ka height-map** hai — har cell ki value uski altitude.
Tum ek hiker ho jo hamesha **upar ki taraf hi chalta hai** (strictly increasing
altitude), aur sirf 4 padosi cells me ja sakta hai. Sawaal: sabse lambi uphill trail
kitni lambi ho sakti hai? Ab key insight: kisi bhi ek cell se shuru karke "yahaan se
aage sabse lambi uphill trail kitni lambi hai" ka jawab **fixed** hai — wo cell ke
neighbours pe depend karta hai, aur koi cycle possible nahi (kyunki altitude strictly
badhti hai, tum kabhi wapas usi cell pe nahi aa sakte). To har cell ka answer ek baar
compute karke **yaad rakh lo (memo)** — dobara mat chalo.

## Approach

Ye DAG pe longest path hai (strictly-increasing edges → no cycle). Plain DFS har cell
se exponential hota; isliye **DFS + memoization** — har cell ke liye `memo[r][c]` =
"is cell se shuru hone wali longest increasing path ki length".

```python
def longest_increasing_path(matrix):
    if not matrix:
        return 0
    rows, cols = len(matrix), len(matrix[0])
    memo = {}                                      # (r, c) -> longest path from here

    def dfs(r, c):
        if (r, c) in memo:
            return memo[(r, c)]
        best = 1                                    # the cell itself
        for dr, dc in ((1,0), (-1,0), (0,1), (0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + dfs(nr, nc))   # extend into a higher neighbor
        memo[(r, c)] = best
        return best

    return max(dfs(r, c) for r in range(rows) for c in range(cols))
```

Pattern: **DFS + memo on a grid (top-down DP over a DAG).** No `visited` set needed —
the strict-increase condition itself prevents revisiting (you can never loop back to an
equal-or-lower cell). The memo turns repeated subproblems into O(1) lookups.

## Complexity

- **Time:** O(m · n) — har cell ek hi baar fully compute hota (memo ki wajah se), aur
  har cell se constant (4) neighbours check hote. Bina memo ke worst case exponential.
- **Space:** O(m · n) memo + O(m · n) recursion depth worst case (ek lambi snake path).

## Common Pitfalls

- **`visited` set use karna** — yahan zaroorat nahi aur galat bhi ho sakta hai. Strict
  increase guarantee karta hai no cycle; `visited` add karne se valid revisits (alag
  path se) block ho sakte hain. Bas `>` condition kaafi hai.
- **`>=` vs `>`** — path **strictly** increasing hona chahiye. `>=` lagaya to equal
  cells pe move hoga aur infinite/wrong length aayega.
- **Sirf ek cell se DFS** — answer kisi bhi cell se shuru ho sakta hai, isliye **har**
  cell se `dfs` lo aur `max` lo. Sirf `[0][0]` se start galat.
- **Memo na lagana** — bina memo TLE pakka. Yehi DP ka asli point hai.
- **Base length `0` rakhna** — `best` ko `1` se init karo (cell khud length 1 hai),
  `0` se nahi.

## When to Use This Pattern

"Grid/graph pe **longest path** with a monotonic edge rule (strictly increasing/
decreasing)" → DFS + memo, kyunki monotonicity DAG banati hai (no cycle). Cue:
"har cell ka answer uske neighbours se derive hota aur subproblems repeat hote" →
top-down memo. Cousins: course schedule longest chain, word ladder length variants,
any DAG longest-path.

## NeetCode Link

https://neetcode.io/problems/longest-increasing-path-in-matrix
