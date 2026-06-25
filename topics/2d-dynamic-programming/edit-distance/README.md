# Edit Distance

**Category:** 2-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given two strings `word1` and `word2`, return the **minimum number of operations**
required to convert `word1` into `word2`. The allowed operations are:

- **Insert** a character
- **Delete** a character
- **Replace** a character

This minimum is called the **Levenshtein distance**.

```
word1 = "horse", word2 = "ros"   ->  3
# horse -> rorse (replace h->r) -> rose (delete r) -> ros (delete e)
```

## Real-World Analogy

**What Azure Blob Storage versioning is:** Azure Blob Storage can keep prior versions of a blob when a configuration file or deployment manifest is overwritten. That lets teams inspect, restore, or compare historical content instead of treating every upload as a total replacement. For a deployment review, imagine comparing an old Azure configuration blob with the new version about to be rolled out.

**What version-to-version diffing is, and why it's used:** Versioning preserves the two snapshots; a diffing step explains the smallest set of edits needed to turn one snapshot into the other. This is useful because reviewers care whether the change is a tiny setting update, a deletion, or a broad rewrite before they approve or roll back. Insert, delete, and replace are the basic edit operations that describe those changes at the character or token level.

**The mapping:** Rows represent prefixes of the old Azure blob, columns represent prefixes of the new blob, and each DP cell stores the cheapest transformation cost for that prefix pair. Matching characters carry the diagonal cost forward, while a mismatch tries one insert, one delete, or one replace from neighboring cached cells and takes the minimum. The key insight is that a global minimum edit script is built from local prefix comparisons, so the bottom-right cell answers the full diff without re-solving the same prefix pairs.

## Approach

Pattern: **2-D DP table** jahan `dp[i][j]` = `word1` ke pehle `i` chars ko `word2`
ke pehle `j` chars me convert karne ka min cost.

**Base cases (boundaries):**
- `dp[0][j] = j` → empty word1 ko `j`-length prefix banane ke liye `j` inserts.
- `dp[i][0] = i` → `i`-length word1 ko empty banane ke liye `i` deletes.

**Transition (har cell):**
- Agar `word1[i-1] == word2[j-1]` → last char already match, free pass:
  `dp[i][j] = dp[i-1][j-1]`.
- Warna 1 + (teeno options me se sabse sasta):
  - `dp[i-1][j-1]` → **replace**
  - `dp[i-1][j]`   → **delete** from word1
  - `dp[i][j-1]`   → **insert** into word1

```python
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i                      # delete all i chars
    for j in range(n + 1):
        dp[0][j] = j                      # insert all j chars
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1],   # replace
                                   dp[i - 1][j],        # delete
                                   dp[i][j - 1])        # insert
    return dp[m][n]
```

Answer bottom-right cell `dp[m][n]` me milta hai.

## Complexity

- **Time:** O(m·n) — har cell ek baar fill hota hai, constant work per cell.
- **Space:** O(m·n) for the table. Sirf previous row chahiye, isliye **O(min(m,n))**
  tak optimize kar sakte ho (rolling 1-D array).

## Common Pitfalls

- **Boundary rows/cols bhulna** — `dp[0][j] = j` aur `dp[i][0] = i` zaroori hain,
  warna empty-string cases galat aayenge.
- **Index off-by-one** — `dp` me row `i` matlab `word1[i-1]` (1-indexed dp, 0-indexed
  string). `word1[i]` likh diya to bug.
- **Teeno transitions me se galat ek miss karna** — replace = diagonal, delete = up,
  insert = left. Inhe mix mat karo.
- **`+1` sirf mismatch pe** — match hone par cost zero, diagonal value as-is leni hai.
- **Rolling array me diagonal kho dena** — 1-D optimize karte waqt `dp[i-1][j-1]`
  ko overwrite hone se pehle ek temp me sambhaal lo.

## When to Use This Pattern

Jab do sequences ko ek-doosre me transform / align / compare karna ho with per-edit
cost → **2-D string DP**. Cousins: Longest Common Subsequence, One Edit Distance,
Distinct Subsequences, sequence alignment (DNA matching, diff tools). Cue:
"do strings, minimum operations / longest common X" → `dp[i][j]` over prefixes.

## Practice

- Visual: open `topics/2d-dynamic-programming/edit-distance/visual.html`

## NeetCode Link

https://neetcode.io/problems/edit-distance
