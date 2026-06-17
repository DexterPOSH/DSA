# Valid Anagram

**Category:** Arrays & Hashing
**Difficulty:** easy

## Problem Statement

Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise. An anagram uses the exact same letters with the exact same frequencies, just rearranged.

## Real-World Analogy

Two bags of **Scrabble tiles**. Dump both bags on the table and count each letter. If bag A has three E's, one R, and one T — and bag B has the exact same counts — they're anagrams. You don't care about order, just that the inventory matches.

## Approach

**Sort approach** (O(n log n)):
```python
def is_anagram(s, t):
    return sorted(s) == sorted(t)
```

**Optimal — frequency map** (O(n)):
```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for c in s:
        count[c] = count.get(c, 0) + 1
    for c in t:
        count[c] = count.get(c, 0) - 1
        if count[c] < 0:
            return False
    return True
```

## Complexity

| Approach | Time | Space |
|----------|------|-------|
| Sort | O(n log n) | O(n) |
| **Hash map** | **O(n)** | **O(1)** — at most 26 keys |

## Common Pitfalls

- Forgetting the length check — if lengths differ, immediately False
- Using two separate counters instead of one with increment/decrement
- Confusing anagram with palindrome

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the frequency counter approach using s = "anagram" and t = "nagaram".

## NeetCode Link

https://neetcode.io/problems/is-anagram
