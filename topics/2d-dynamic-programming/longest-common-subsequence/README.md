# Longest Common Subsequence

**Category:** 2-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given two strings `text1` and `text2`, return the length of their **longest common subsequence** (LCS). A subsequence keeps characters in order but **need not be contiguous**. Return `0` if there is none.

```
text1 = "abcde", text2 = "ace"   ->  3    # "ace"
text1 = "abc",   text2 = "abc"   ->  3    # "abc"
text1 = "abc",   text2 = "def"   ->  0    # nothing common
```

## Real-World Analogy

**What Azure Cognitive Search is:** Azure Cognitive Search, now Azure AI Search, is a managed search service that indexes documents so applications can retrieve relevant content quickly. Its analyzers break text into tokens and the index can retain token positions for ordered queries such as phrase or proximity searches. In this analogy, two indexed documents are being compared to find the longest shared ordered trail of tokens.

**What ordered token comparison is, and why it's used:** Two Azure search documents may discuss the same workflow while adding extra words, sections, or metadata in different places. An ordered comparison preserves the sequence of shared evidence without requiring the tokens to be adjacent. That is useful when you care about common structure or narrative, not just whether the same words appear somewhere in both documents.

**The mapping:** Document A and document B are the two strings, and each DP cell compares one prefix of A with one prefix of B. When the current tokens match, the cell extends the diagonal subsequence by one; when they differ, it keeps the better cached result from dropping a token from A or dropping a token from B. The key insight is that LCS allows skips but never reorders, so the bottom-right cell gives the longest Azure-style ordered evidence trail shared by both indexed documents.

## Approach

`dp[i][j]` = LCS length of `text1[:i]` aur `text2[:j]` (yaani pehle `i` aur pehle `j` characters). Table `(m+1) x (n+1)` size ki — extra row/col empty-prefix ke liye (LCS = 0).

Recurrence — har cell do haalat me se ek:
- **Last chars match** (`text1[i-1] == text2[j-1]`): diagonal se aao, +1 → `dp[i][j] = dp[i-1][j-1] + 1`
- **Match nahi**: best of "skip `text1` ka char" (`dp[i-1][j]`) ya "skip `text2` ka char" (`dp[i][j-1]`) → `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`

```python
def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]    # row 0 / col 0 = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1       # match: diagonal + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

**Space-optimized (two rows):** sirf upar wali row chahiye, to `O(min(m,n))` me reduce kar sakte ho do rows roll karke.

> Pattern: **2-D DP on two sequences**. Grid ka har cell teen padosiyon se banta hai — diagonal (match), top, ya left (skip).

## Complexity

- **Time:** O(m·n) — har cell ek baar fill, har fill O(1).
- **Space:** O(m·n) full table; **O(min(m,n))** with two-row rolling.

## Common Pitfalls

- **Index off-by-one** — `dp[i][j]` me `text1[i-1]` aur `text2[j-1]` compare karte hain (1-indexed dp, 0-indexed string). Yeh sabse common bug hai.
- **Substring vs subsequence confuse karna** — subsequence me gaps allowed hain; agar contiguous chahiye to wo *longest common substring* hai (alag recurrence: mismatch pe `0`, aur answer table ka max hota hai, last cell nahi).
- **Base row/col init bhoolna** — empty prefix ke saath LCS hamesha `0`, to first row aur column zero rakho.
- **Match case me `max` lagana** — match pe seedha `dp[i-1][j-1]+1` lo, `max(... , dp[i-1][j-1]+1)` jaisa extra `max` redundant (aur kabhi-kabhi galat intuition).

## When to Use This Pattern

"Do strings/arrays ke beech alignment, common part, ya transform" dikhe to **2-D DP table (two sequences)** socho. Cousins: Edit Distance, Longest Common Substring, Shortest Common Supersequence, Distinct Subsequences, diff/merge tools. Cue: do sequences ko side-by-side rakh ke "match karo ya kisi ek ko aage badhao".

## Practice

- Visual: open `topics/2d-dynamic-programming/longest-common-subsequence/visual.html`

## NeetCode Link

https://neetcode.io/problems/longest-common-subsequence
