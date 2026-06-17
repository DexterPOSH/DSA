# Longest Repeating Character Replacement

**Category:** Sliding Window
**Difficulty:** medium

## Problem Statement

Given a string `s` (uppercase letters) and an integer `k`, you may replace **at most
`k` characters** with any other uppercase letter. Return the length of the **longest
substring containing the same letter** you can get after doing those replacements.

```
s = "ABAB",   k = 2   ->  4    # replace 2 B's with A (or 2 A's with B) -> "AAAA"
s = "AABABBA", k = 1   ->  4    # window "ABBA": replace the lone A -> "BBBB"
```

## Real-World Analogy

Socho ek deewar pe tiles laggi hain alag-alag colors ki, aur tumhare paas sirf `k`
**repaint stickers** hain. Tum ek lagatar stretch (window) choose karte ho aur uske
andar **majority color** ko rehne dete ho, baaki tiles ko repaint kar dete ho — par
sirf tabhi jab repaint karne waali tiles `k` se zyada na ho. Tumhe sabse lambi aisi
stretch chahiye jise tum ek hi color me badal sako. Window me jitne tiles "majority
nahi" hain (`window_len - max_count`), utne repaints chahiye — wo `k` se zyada hue
to window ko chhota karo.

## Approach

**Sliding window + frequency count.** Window me har char ka count rakho. Window valid
hai jab `window_len - max_count <= k`, jahan `max_count` window me sabse frequent char
ki count hai. (`window_len - max_count` = jitne characters replace karne padenge.)

`right` se expand karo, count update karo. Agar window invalid ho gayi
(`window_len - max_count > k`), to `left` ko ek step aage karo aur uska count ghatao.

```python
def character_replacement(s, k):
    count = {}
    left = 0
    max_count = 0          # window me sabse frequent char ki frequency
    best = 0
    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_count = max(max_count, count[s[right]])
        # window invalid? -> ek char left se nikaalo
        if (right - left + 1) - max_count > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
```

> **Sneaky bit:** `max_count` ko kabhi *decrease* nahi karte jab window shrink hoti.
> Lagta hai bug hai, par nahi — answer sirf tabhi badhta jab koi *naya* zyada-frequent
> char milta hai, isliye stale (slightly high) `max_count` se window kabhi galat-bade
> nahi hoti; bas grow karti rehti hai. Yahi is problem ka famous trick hai.

## Complexity

- **Time:** O(n) — ek pass, `left` aur `right` dono monotonic. Count map fixed 26 size.
- **Space:** O(1) — count map me at most 26 uppercase letters.

## Common Pitfalls

- **`max_count` ko recompute / decrease karne ki koshish** — zaroorat nahi, aur karoge
  to har step pe O(26) lag kar code slow + over-complicated ho jaata. Stale max chalta hai.
- **Window ko `while` se shrink karna** — yahan single `if` kaafi hai kyunki hum window
  ko *kabhi chhota nahi karte*, sirf slide karte hain (right ke saath left bhi 1 badhta).
- **`window_len - max_count` ko galat samajhna** — yeh "replace karne waale" characters
  hain; yahi `k` se compare hota hai, na ki `max_count` directly.
- **Lowercase/mixed case assume karna** — problem uppercase deta; warna count size adjust karo.

## When to Use This Pattern

"Longest window jisme at most K changes/violations allowed ho" — jab aisa dikhe to
**sliding window with a 'cost = window_len - something' check** socho. Cousins:
"max consecutive ones III" (at most K zeros flip), "longest subarray with at most K
distinct". Cue: window valid rehne ke liye ek budget `k`.

## NeetCode Link

https://neetcode.io/problems/longest-repeating-substring-with-replacement
