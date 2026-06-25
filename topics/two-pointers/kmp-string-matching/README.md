# KMP — Knuth–Morris–Pratt String Matching

**Category:** Strings / Pattern Matching (two-pointer family)
**Full form:** Knuth–Morris–Pratt (Donald **K**nuth, James **M**orris, Vaughan **P**ratt, 1977)
**Difficulty:** medium–hard (concept), used as a *follow-up* to naive string search
**Status:** reference / follow-up — NOT on the LinkedIn CA1 list, but the "correct
O(n+m)" answer when an interviewer pushes on String Replacement / substring search.

## What it is

Substring search in **O(n + m)** instead of naive O(n·m). Core idea: on a
mismatch, **don't restart from scratch** — reuse the characters you already
matched.

(n = len(text), m = len(pattern))

## Real-World Analogy

**What Azure Web Application Firewall is:** Azure Web Application Firewall (WAF) protects web apps running behind services such as Azure Application Gateway and Azure Front Door. It inspects HTTP requests for common attack patterns like SQL injection, cross-site scripting, and protocol anomalies before traffic reaches the app. Because this happens on live request paths, scanning must be fast and avoid unnecessary rewinds.

**What signature-based request scanning is, and why it's used:** WAF rules often look for malicious signatures across URLs, headers, cookies, and request bodies. Conceptually, when a partial signature matches and the next character fails, an efficient scanner should not restart the request body from the beginning; it should reuse the part of the signature that could still be a valid prefix. KMP's LPS table is that reusable fallback knowledge: it preserves security coverage while keeping request inspection linear instead of repeatedly rescanning the same bytes.

**The mapping:** The Azure WAF request payload is the `text`, the malicious signature is the `pattern`, and the LPS array is the rule-engine-style fallback table. Pointer `i` over the payload never moves backward; pointer `j` over the signature either advances on matches or jumps to `lps[j - 1]` on mismatches. The key insight is to shift the pattern using what was already matched, so every request byte is processed a constant number of times.

## The LPS array (failure function) — the engine

For the pattern, build: **`lps[i]` = length of the longest *proper* prefix of
`pattern[0..i]` that is also a *suffix*** ("proper" = not the whole string).

Example `P = "ABABC"`:
```
index:  0   1   2   3   4
char:   A   B   A   B   C
lps:    0   0   1   2   0
```
- `"ABA"` → prefix `"A"` == suffix `"A"` → 1
- `"ABAB"` → `"AB"` == `"AB"` → 2

`lps[j-1]` tells you: on a mismatch, where to send the *pattern* pointer back to
(NOT to 0, but to `lps[j-1]`).

### Build LPS — O(m)

```python
def build_lps(P):
    lps = [0] * len(P)
    length = 0          # current longest prefix-suffix
    i = 1
    while i < len(P):
        if P[i] == P[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length > 0:
            length = lps[length - 1]   # fallback (same trick, recursive)
        else:
            lps[i] = 0
            i += 1
    return lps
```

## Search — O(n)

Two pointers: `i` over text, `j` over pattern. **`i` never moves backward** →
that's why it's linear.

```python
def kmp_search(text, pattern):
    if not pattern:
        return 0
    lps = build_lps(pattern)
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                return i - j          # match start index
                # for ALL matches: record (i - j), then j = lps[j-1]; continue
        elif j > 0:
            j = lps[j - 1]            # reuse matched prefix, don't rescan text
        else:
            i += 1
    return -1
```

## Complexity

- **Time:** O(n + m) — build LPS O(m), search O(n). `i` is monotonic.
- **Space:** O(m) for the LPS array.

## Why it beats naive (and fixes the buggy single-pass)

Naive re-scan is O(n·m). A hand-rolled single-pass that resets to 0 on every
mismatch is O(n) but **silently wrong** on adjacent (`"abab"`/`"ab"`) and
overlapping-prefix (`"aaab"`/`"aab"`) patterns. The LPS array is exactly the
bookkeeping that makes the single pass correct.

## How to Learn It (roadmap)

1. **Build LPS by hand** for 4–5 patterns until it's intuitive:
   `"AAAA"`, `"ABCDABD"`, `"AABAACAABAA"`, `"AAACAAAA"`.
2. Trace the search loop on a text by hand.
3. Watch an animation (see `visual.html`) — clicks fastest visually.
4. Then grind the practice problems below.

## Practice Problems (the pointers — do these to learn KMP)

| Problem | LeetCode | What it drills |
|---|---|---|
| Find Index of First Occurrence (strStr) | **LC 28** | Direct KMP search |
| Repeated Substring Pattern | **LC 459** | Clever LPS use |
| Longest Happy Prefix | **LC 1392** | Pure LPS array |
| Shortest Palindrome | **LC 214** | KMP on `s + '#' + reverse(s)` |
| Implement strStr / Rabin-Karp compare | LC 28 (alt) | Hashing vs KMP tradeoff |

> Order: **28 → 1392 → 459 → 214** (easy build-up to the trickier LPS tricks).

## When to Use

Any "find a pattern inside a string in linear time" need, or when naive search
TLEs. Cousins: Z-algorithm, Rabin-Karp (rolling hash), Aho-Corasick (multi-pattern).

## Related

- [[string-replacement]] — naive O(n·m) scan; KMP is its O(n+m) upgrade.
- Visual: open `topics/two-pointers/kmp-string-matching/visual.html`
