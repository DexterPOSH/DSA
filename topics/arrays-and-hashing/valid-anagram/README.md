# Valid Anagram

**Category:** Arrays & Hashing
**Difficulty:** easy

## Problem Statement

Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise. An anagram uses the exact same letters with the exact same frequencies, just rearranged.

## Real-World Analogy

**What Azure Cache for Redis is:** Azure Cache for Redis is Azure's managed in-memory Redis service, commonly used for fast shared state such as counters, session data, rate limits, and caches. It is useful when many tiny updates need to be recorded quickly without rewriting a whole document. For an anagram check, the shared state is a compact inventory of characters.

**What a Redis hash counter is, and why it's used:** A Redis hash stores many small fields under one key, like `letter -> count`. `HINCRBY` atomically increments or decrements one field, so a client can update a single counter without fetching, editing, and saving the whole hash. Azure apps use this kind of counter when the exact balance matters, because it prevents lost updates and keeps the inventory cheap to maintain.

**The mapping:** The first string increments the Redis-style counter for every character; the second string decrements the same counters. If the strings are true anagrams, every field returns to zero, meaning the character inventory matches even though the order changed. The key insight is that anagrams are not about sequence — they are about balanced counts, just like a Redis hash whose per-letter counters all net out.
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
