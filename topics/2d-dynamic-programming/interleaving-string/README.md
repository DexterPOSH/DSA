# Interleaving String

**Category:** 2-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given strings `s1`, `s2`, and `s3`, return `True` if `s3` is formed by an
**interleaving** of `s1` and `s2`. An interleaving keeps the **relative order** of
characters from each string but lets you weave them together in any way.

```
s1 = "abc", s2 = "aed", s3 = "aabecd"           ->  True    # a(s2) a(s1) b(s1) e(s2) c(s1) d(s2)
s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"   ->  False
```

A necessary first check: `len(s1) + len(s2)` must equal `len(s3)`.

## Real-World Analogy

Socho do log ek hi document type kar rahe hain ek shared screen pe — ek bole `s1` ke
letters apne order me, dusra `s2` ke letters apne order me. Beech-beech me jo combined
text screen pe banta hai wo `s3` hai. Tumhe verify karna hai: kya `s3` exactly in dono
ki **typing ko interleave** karke ban sakta hai? Har position pe tum dekhte ho — agla
`s3` letter kis typist ne maara? Agar wo `s1` ke current letter se match karta hai to
`s1` aage badha do; agar `s2` se match karta hai to `s2` aage. **Dono se match kar sakta
hai** to confusion — yahi pe DP zaroori hai, kyunki ek galat choice baad me dead-end de
sakti hai aur tumhe dono raaste explore karne padte hain bina dobara kaam kiye.

## Approach

State: `dp[i][j]` = kya `s3`'s first `i+j` chars ko `s1[:i]` aur `s2[:j]` se interleave
kar sakte hain? Position `i+j` me `s3[i+j-1]` ya to `s1[i-1]` se aaya ya `s2[j-1]` se:

- Agar `s1[i-1] == s3[i+j-1]` aur `dp[i-1][j]` True → `dp[i][j]` True (last char `s1` se).
- Agar `s2[j-1] == s3[i+j-1]` aur `dp[i][j-1]` True → `dp[i][j]` True (last char `s2` se).

```python
def is_interleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(m + 1):
        for j in range(n + 1):
            k = i + j - 1                      # index into s3
            if i > 0 and s1[i-1] == s3[k] and dp[i-1][j]:
                dp[i][j] = True
            if j > 0 and s2[j-1] == s3[k] and dp[i][j-1]:
                dp[i][j] = True
    return dp[m][n]
```

Pattern: **2-D boolean DP over two-string prefixes** — har cell ye keh raha hai "kya yahan
tak pohoncha ja sakta hai". Top (`s1` se aaya) ya left (`s2` se aaya), char match hone pe.

## Complexity

- **Time:** O(m · n) — har cell ek baar, constant work. Greedy/DFS bina memo ke
  exponential ho jaata kyunki same `(i, j)` baar-baar visit hota.
- **Space:** O(m · n) table; ek row at a time rakh ke O(n) tak optimize kar sakte ho.

## Common Pitfalls

- **Length check bhulna** — agar `m + n != len(s3)` to turant `False`. Iske bina
  indexing galat ho jaati aur logic tut-ta hai.
- **`s3` index galti** — `s3[i+j-1]`, not `s3[i]` ya `s3[j]`. Total consumed chars `i+j`
  hain, last char index `i+j-1`.
- **Greedy lalach** — "jo match kare wahi le lo" galat hai jab dono match karein. Dono
  branches DP me explore hone chahiye; greedy ek tarph commit karke dead-end pe phasega.
- **Base row/column** — `dp[0][0]=True`. First row/column tabhi True jab prefix exactly
  ek string se ban sake (loop ye automatically handle karta `i==0`/`j==0` guards se).

## When to Use This Pattern

"Do sequences ko **merge / interleave / align** karke ek teesra banana, relative order
preserve karte hue" → 2-D DP over prefixes of both. Cue: ek string ke do prefixes ka
combination → table jiske axes do strings hain. Cousins: Edit Distance, LCS, Distinct
Subsequences — sab two-string grid DP.

## NeetCode Link

https://neetcode.io/problems/interleaving-string
