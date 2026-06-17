# Unique Paths

**Category:** 2-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

A robot sits at the **top-left** corner of an `m x n` grid. It can only move **right** or **down**. How many distinct paths reach the **bottom-right** corner?

```
m = 3, n = 7   ->  28
m = 3, n = 2   ->  3
```

## Real-World Analogy

Socho ek city ka grid hai — sirf **right ya down** chal sakte ho (one-way streets). Tumhe top-left se bottom-right pahunchna hai. Ab kisi bhi intersection pe khade ho ke socho: "is corner tak main kitne tareeke se aa sakta hoon?" Jawaab simple hai — main yahan ya to **upar wale block se neeche aaya**, ya **left wale block se right aaya**. Aur koi raasta hai hi nahi. To is corner ke paths = (upar wale corner ke paths) + (left wale corner ke paths). Bas yahi recurrence hai. Har cell apne **do padosiyon** (top + left) ka sum hai.

## Approach

Har cell `dp[i][j]` = us cell tak pahunchne ke tareeke. Ek cell tak sirf upar se (`dp[i-1][j]`) ya left se (`dp[i][j-1]`) aa sakte ho, to:

```
dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

**Base case:** pehli row aur pehli column me sab cells = `1` — kyunki ek hi seedha raasta hai (sirf right, ya sirf down).

**Full 2-D table (clearest to reason about):**
```python
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]      # row 0 and col 0 already = 1
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]
```

**Space-optimized (1-D row):** humein sirf upar wali row aur current row chahiye, to ek hi row roll kar sakte hain:

```python
def unique_paths(m, n):
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j-1]            # row[j]=top, row[j-1]=left (already updated)
    return row[-1]
```

> Pattern: **2-D DP table** jahan har cell apne ek-do padosiyon se banta hai. Yeh "count the ways to reach a cell" family ka prototype hai.

## Complexity

- **Time:** O(m·n) — har cell exactly ek baar fill hoti hai.
- **Space:** O(m·n) full table; **O(n)** with the rolling-row trick (sirf ek row store karte hain).

> Math shortcut: answer `C(m+n-2, m-1)` bhi hai (total m-1 downs + n-1 rights ko arrange karna). Interview me DP zyada safe — combinatorics galti se overflow/off-by-one kara deta.

## Common Pitfalls

- **Base row/col ko 1 set karna bhoolna** — agar 0 se shuru kiya to poori table 0 reh jaayegi.
- **`m` aur `n` ulta lagana** — rows = `m`, cols = `n`. Grid dimensions confuse mat karo.
- **Rolling-row me update order** — left-to-right hi chalo, taaki `row[j-1]` already-updated (current row ka left) ho aur `row[j]` abhi purana (upar wala) ho. Yeh order hi dono neighbors deta hai.
- **Combinatorics overflow** — bade `m,n` pe `(m+n-2)!` huge ho jaata; DP ya `math.comb` use karo.

## When to Use This Pattern

"Grid me top-left se bottom-right tak count/min/max paths" ya "har cell ek-do padosiyon (top/left/diagonal) se banti hai" — jab aisa dikhe to **2-D DP table** socho. Cousins: Unique Paths II (obstacles), Minimum Path Sum, Longest Common Subsequence, Edit Distance. Cue: cell ka jawaab uske neighbor cells ke jawaabon ka simple combination hai.

## Practice

- Visual: open `topics/2d-dynamic-programming/unique-paths/visual.html`

## NeetCode Link

https://neetcode.io/problems/count-paths
