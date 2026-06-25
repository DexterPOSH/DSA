# Valid Palindrome

**Category:** Two Pointers
**Difficulty:** easy

## Problem Statement

Given a string `s`, return `True` if it is a **palindrome** after converting all
uppercase letters to lowercase and **removing all non-alphanumeric characters**.
Otherwise return `False`.

```
"A man, a plan, a canal: Panama"  ->  True   # "amanaplanacanalpanama"
"race a car"                      ->  False  # "raceacar"
" "                               ->  True   # empty string after cleaning
```

## Real-World Analogy

**What Azure Storage geo-redundant storage (GRS) is:** Azure Storage GRS keeps data durable by asynchronously replicating a storage account's data from a primary region to a paired secondary region. It is used for disaster recovery and regional resilience so blobs, metadata, and other storage data remain protected even if a region has problems. Conceptually, you can think of it as maintaining a faithful secondary copy of the primary blob's logical contents.

**What manifest mirror verification is, and why it's used:** A blob manifest or block list describes the logical pieces that make up a blob, while metadata and checksums help systems reason about integrity. In this analogy, a verifier canonicalizes the primary and mirrored manifests by ignoring separators, punctuation-like markers, and casing differences, then compares the meaningful tokens from the outside inward. The point of that verification is to catch the first real mismatch cheaply while ignoring formatting noise that does not change the stored data.

**The mapping:** The string is the Azure Storage manifest text, non-alphanumeric characters are manifest separators to skip, and `.lower()` is the normalization step before comparing tokens. Pointer `l` reads from the primary-side start, pointer `r` reads from the mirrored-side end, and every matching pair proves one more symmetric layer is consistent. The key insight is to canonicalize while scanning with two pointers, so you verify symmetry in O(1) extra space instead of building a cleaned copy first.

## Approach

Pattern: **two pointers converging from both ends**. Pura string clean karke alag
buffer banane ki zaroorat hi nahi — do pointers `l` aur `r` rakho aur in-place
hi kaam karo.

```python
def is_palindrome(s):
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum():   # left junk skip
            l += 1
        while l < r and not s[r].isalnum():   # right junk skip
            r -= 1
        if s[l].lower() != s[r].lower():      # case-insensitive compare
            return False
        l += 1
        r -= 1
    return True
```

Loop tab tak chalta hai jab tak `l < r`. Har baar pehle dono pointers ko
**alphanumeric** position tak khisko, fir compare karo. Mismatch mila → `False`.
Beech tak bina mismatch pahunch gaye → `True`.

> **One-liner alternative:** `t = [c.lower() for c in s if c.isalnum()]` aur fir
> `t == t[::-1]`. Lekh saaf hai par yeh **O(n) extra space** leta hai. Two-pointer
> version O(1) space me karta hai — interviewer usually yahi sunna chahta hai.

## Complexity

- **Time:** O(n) — har character ko at most ek baar dono pointer touch karte hain.
- **Space:** O(1) — koi extra buffer nahi, sirf do index variables.

## Common Pitfalls

- **Skip loops me `l < r` guard bhulna** — agar string pura punctuation hai (`",,,"`),
  to inner `while` bina guard ke pointer ko range se bahar le ja sakta hai.
- **`.lower()` lagana bhulna** — `"Aa"` palindrome hai case-insensitively, par
  raw compare me `A != a`.
- **`isalnum()` vs `isalpha()`** — digits bhi valid hain (`"0P0"` is `False`,
  `"0p0"`-style cleaning matters), `isalpha` use karoge to digits galti se drop
  ho jaayenge.
- **Empty / all-junk string** → cleaned string empty hoti hai, jo palindrome hai →
  `True`. Yeh edge case miss mat karo.

## When to Use This Pattern

Jab dikhe "string/array ko **symmetric** check karna hai" ya "dono ends se andar
ki taraf compare" → **two pointers from opposite ends**. Cousins: reverse string,
valid palindrome II (ek deletion allowed), two-sum on sorted array.

## NeetCode Link

https://neetcode.io/problems/is-palindrome
