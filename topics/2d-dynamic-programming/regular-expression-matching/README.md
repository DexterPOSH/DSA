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

Socho ek **strict immigration officer** ek passport (`s`) ko ek rulebook (`p`) ke
against verify kar raha hai, character-by-character. `.` matlab "is slot pe koi bhi
ek character chalega". Aur `*` sabse tricky hai — yeh *pichle* rule pe lagta hai aur
kehta hai "yeh rule zero ya jitni baar bhi repeat ho sakta hai".

Officer har step pe do raaste explore kar sakta hai jab `*` aaye: **rule ko skip kar
do** (zero occurrences), ya **ek character consume karke wahi rule dobara** apply
karo. Yeh branching exactly DP table me cache hoti hai — taaki same `(s-position,
p-position)` baar-baar na solve karna pade.

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
