# Regular Expression Matching

**Category:** 2-D Dynamic Programming
**Difficulty:** hard

## Problem Statement

Given an input string `s` and a pattern `p`, implement matching that supports:

- `.` — matches **any single** character.
- `*` — matches **zero or more** of the *preceding* element.

The match must cover the **entire** string `s` (not a partial substring).

```
s = "aab", p = "c*a*b"   ->  True
# c* -> zero c's,  a* -> "aa",  b -> "b"   => whole string matched

s = "mississippi", p = "mis*is*p*."  ->  False
```

## Real-World Analogy

**What Azure Web Application Firewall is:** Azure Web Application Firewall protects web apps by inspecting HTTP requests at services such as Azure Application Gateway or Azure Front Door. It applies managed and custom rules before traffic reaches the application, blocking or allowing requests based on paths, headers, query strings, and other fields. In this analogy, the request path is checked against a regex-like custom policy.

**What regex-style custom rule matching is, and why it's used:** Custom WAF rules let teams express compact traffic policies instead of writing application code for every path variation. A wildcard-like `.` can accept any single character, while `*` means the previous token may repeat zero or more times. That flexibility is powerful but creates branches, because the matcher must consider both "use this repetition" and "skip it entirely."

**The mapping:** The Azure request path is `s`, the WAF-style policy is `p`, and `dp[i][j]` records whether the first `i` path characters match the first `j` pattern characters. A literal or `.` advances diagonally when the current character is accepted, while `*` checks zero occurrences from two pattern columns back or one more occurrence from the row above. The key insight is that regex matching is a grid of repeated text-pattern states, so caching each state avoids re-exploring the same WAF rule branch again and again.

## Approach

Pattern: **2-D DP** jahan `dp[i][j]` = `True` agar `s[:i]` (`s` ke pehle `i` chars)
`p[:j]` (`p` ke pehle `j` chars) ko fully match karta hai.

**Base case:** `dp[0][0] = True` (empty matches empty). Empty `s` vs pattern jaise
`a*b*c*` bhi true ho sakta hai — handle below.

**Transition for `dp[i][j]`** (pattern char `p[j-1]`):

1. **`p[j-1]` is a normal char or `.`** → match current char:
   `dp[i][j] = dp[i-1][j-1]` **and** `p[j-1] == s[i-1] or p[j-1] == '.'`.

2. **`p[j-1] == '*'`** → look at `p[j-2]` (the char before `*`):
   - **Zero occurrences:** drop the `x*` pair → `dp[i][j-2]`.
   - **One+ occurrences:** if `p[j-2]` matches `s[i-1]` (`==` or `.`),
     then `dp[i-1][j]` (consume one `s` char, keep the same `x*`).
   - Combine with **OR**.

```python
def is_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):                 # empty s vs patterns like a*b*
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '*':
                dp[i][j] = dp[i][j - 2]                       # zero of preceding
                if p[j - 2] == s[i - 1] or p[j - 2] == '.':
                    dp[i][j] = dp[i][j] or dp[i - 1][j]       # one more
            else:
                dp[i][j] = dp[i - 1][j - 1] and (
                    p[j - 1] == s[i - 1] or p[j - 1] == '.')
    return dp[m][n]
```

## Complexity

- **Time:** O(m·n) — har cell ek baar, constant work per cell.
- **Space:** O(m·n) for the table (rolling 1-D row tak optimize possible).

## Common Pitfalls

- **`*` ko apne aap match karna** — `*` kabhi akela kuch match nahi karta; yeh
  hamesha *pichle* element ko modify karta hai. Pair `(x, *)` ko ek unit samjho.
- **`dp[0][j]` (empty s) wali row bhulna** — `a*`, `a*b*` jaise patterns empty string
  match karte hain; yeh boundary set na ki to false negatives.
- **Zero-occurrence branch chhodna** — `dp[i][j-2]` (poora `x*` skip) miss kar diya
  to `c*a*b` jaise patterns toot jaayenge.
- **`p[j-2]` match check galat** — "one more" branch sirf tab valid jab preceding
  char current `s` char se match kare (`==` ya `.`).
- **Greedy/regex library use karna** — interview me manual DP chahiye, `re.match`
  nahi. Greedy backtracking bhi likha ja sakta hai but DP cleaner aur no TLE.

## When to Use This Pattern

Jab do sequences match karni ho with *wildcards / quantifiers* aur har position pe
multiple branches ban rahe ho → **2-D match DP** (`dp[i][j]` over prefixes). Cousins:
Wildcard Matching (`?` and `*`), Longest Common Subsequence, Interleaving String,
Distinct Subsequences. Cue: "string vs pattern with special chars, full match" →
think `dp[i][j]` and case-split on the pattern character.

## Practice

- Visual: open `topics/2d-dynamic-programming/regular-expression-matching/visual.html`

## NeetCode Link

https://neetcode.io/problems/regular-expression-matching
