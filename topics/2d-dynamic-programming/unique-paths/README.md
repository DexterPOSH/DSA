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

**What Azure Virtual WAN is:** Azure Virtual WAN is a managed networking service that connects branches, VNets, and cloud networks through Microsoft-managed hubs. It centralizes routing so teams can reason about large Azure network topologies without configuring every path manually. In this analogy, the topology is simplified into a rectangular grid of Azure regions and data centers.

**What compliance-constrained route planning is, and why it's used:** Network teams often restrict which regions traffic may traverse to satisfy data residency, security, or operational policies. Here, the allowed policy is intentionally simple: traffic may only move east or south, never back north or west. That one-way constraint prevents loops and means every route to a cell must enter from exactly one of two approved neighbors.

**The mapping:** Each grid cell is an Azure network location, moving right or down is an allowed Virtual WAN route hop, and the DP cell stores how many compliant routes reach that location. The first row and first column each have one path because traffic can only keep moving in a straight line, while every interior cell adds the cached counts from the north and west neighbors. The key insight is that a global route count emerges from local dependencies, so the bottom-right cell gives all valid end-to-end paths after each cell is computed once.

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
