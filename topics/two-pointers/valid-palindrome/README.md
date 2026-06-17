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

Socho do log ek hi sentence ko padh rahe hain — ek **shuruaat se** (left), ek
**aakhir se** (right). Dono ek-ek letter aage badhte hain aur beech me milte hain.
Har step pe wo apna-apna letter compare karte hain: agar kabhi bhi do letters
match nahi karte, to sentence palindrome nahi hai — bas wahi ruk jao. Lekin ek
twist hai: dono readers spaces, commas aur capital/small ka farak ignore karte
hain — sirf "real" letters aur digits matter karte hain. Isiliye agar koi pointer
pe junk character (space, punctuation) aaye, to wo bina compare kiye usse skip
kar deta hai.

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
