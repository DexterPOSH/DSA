# Distinct Subsequences

**Category:** 2-D Dynamic Programming
**Difficulty:** hard

## Problem Statement

Given strings `s` and `t`, return the **number of distinct subsequences** of `s`
that equal `t`. A subsequence keeps the original relative order but can delete any
characters (including none).

```
s = "rabbbit", t = "rabbit"   ->  3
# the three b's give three distinct ways to pick "rabbit":
#   ra[bb]b it , ra[b]b[b]it , rab[bb]it   (which b's are kept differs)
```

## Real-World Analogy

**What Azure Blob Storage versioning is:** Azure Blob Storage stores objects such as configuration files, manifests, and policy documents, and versioning can preserve previous versions whenever a blob is overwritten. That gives teams an audit trail and a recovery point instead of losing the old content. In this analogy, an audit job reads a long versioned configuration blob and asks how many ordered ways a shorter policy snippet appears inside it.

**What an ordered subsequence audit is, and why it's used:** The audit does not require the policy characters or tokens to be adjacent; it only requires them to appear in the same order. That is useful when a required policy pattern may be separated by comments, whitespace, or extra settings in a real Azure configuration blob. Counting all possible alignments exposes how repeated characters create overlapping evidence paths that a simple first-match scan would miss.

**The mapping:** The source string is the long Azure blob version, the target string is the policy snippet, and the 2-D table compares every source prefix with every target prefix. When the current characters match, the cell adds the count for using that source character from the diagonal and the count for skipping it from the row above; when they differ, only skipping is possible. The key insight is that once prefix lengths are fixed, the remaining choices no longer care how you got there, so repeated subsequence choices collapse into cached counts.

## Approach

State: `dp[i][j]` = `s[:i]` me `t[:j]` kitne distinct subsequences ki tarah banta hai.

- Agar `s[i-1] == t[j-1]`: do raaste add karo — current `s` char ko **use** karo
  (`dp[i-1][j-1]`) **ya skip** karo (`dp[i-1][j]`).
- Agar match nahi: sirf skip — `dp[i][j] = dp[i-1][j]`.

Base: `dp[i][0] = 1` (empty `t` ko banane ka exactly ek tareeka — kuch mat chuno).
`dp[0][j>0] = 0` (empty `s` se non-empty `t` impossible).

```python
def num_distinct(s, t):
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = 1                                # empty t: one way
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i-1][j]                    # skip s[i-1]
            if s[i-1] == t[j-1]:
                dp[i][j] += dp[i-1][j-1]            # also use s[i-1]
    return dp[m][n]
```

Pattern: **2-D counting DP over two-string prefixes** with a use/skip branch — same grid
family as LCS and Edit Distance, but cells hold **counts**, not booleans/lengths.

## Complexity

- **Time:** O(m · n) — har cell constant work. Naive recursion (try every subsequence)
  exponential hota; memo/table isse polynomial bana deta.
- **Space:** O(m · n) table; rolling do rows (ya reverse-iterated single row) se O(n).

## Common Pitfalls

- **Base case galti** — `dp[i][0] = 1` for **all** `i` (empty `t` ek tareeke se banta).
  Ise `0` rakhna poora count tod deta. Aur `dp[0][j>0] = 0`.
- **Match pe sirf diagonal lena** — match hone par tumhe **dono** `dp[i-1][j-1]` (use)
  AUR `dp[i-1][j]` (skip) add karne hain. Sirf diagonal lena duplicate-letter cases
  undercount karta — yahi `"rabbbit"` me 3 ko 1 bana deta.
- **No-match pe diagonal chhoona** — match nahi to current char use kar hi nahi sakte;
  sirf `dp[i-1][j]` (skip) lo. Diagonal yahan illegal hai.
- **`s`/`t` roles swap** — `t` target subsequence hai (columns), `s` source (rows).
  Ulta karoge to galat answer. (`t` longer than `s` → answer 0.)
- **Overflow** — counts bade ho sakte hain; Python me fine, par C++/Java me 64-bit lo.

## When to Use This Pattern

"Kitne tareeke hain ek sequence ke andar ek target pattern ko **subsequence ki tarah
banane** ke" → 2-D counting DP with use/skip branch on character match. Cue: do strings,
"number of ways" (count, not yes/no, not length), order-preserving selection → prefix
grid jisme cells counts store karte hain. Cousins: LCS (length), Edit Distance (cost),
Interleaving String (boolean).

## NeetCode Link

https://neetcode.io/problems/distinct-subsequences
