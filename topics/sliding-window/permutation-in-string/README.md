# Permutation in String

**Category:** Sliding Window
**Difficulty:** medium

## Problem Statement

Given two strings `s1` and `s2`, return `True` if `s2` contains a **permutation of
`s1`** as a substring. In other words, does some contiguous window of `s2` have the
**exact same character counts** as `s1`?

```
s1 = "ab",  s2 = "eidbaooo"   ->  True    # "ba" is a permutation of "ab"
s1 = "ab",  s2 = "eidboaoo"   ->  False   # no window is an anagram of "ab"
```

## Real-World Analogy

Socho `s1` ek **recipe** hai jisme fixed quantities chahiye — jaise "2 onions, 1
tomato". Tum `s2` ki pantry pe ek **fixed-size basket** (window) slide karte ho jiska
size = recipe me total items. Har position pe poochte ho: "is basket me bilkul wahi
quantities hain jo recipe maangti hai?" Order matter nahi karta — sirf counts match
hone chahiye. Ek bhi position pe perfect match mil gaya, to answer `True`.

## Approach

**Fixed-size sliding window + frequency match.** Window ka size hamesha `len(s1)` hai.
`s1` ka frequency count banao. Phir `s2` pe ek window slide karo: har naya char andar
aaye, ek purana char bahar jaaye, aur poochte raho ki window ka count `s1` ke count
ke barabar hai ya nahi.

Naive: har window pe poora count compare (O(26) per step). Cleaner: ek `matches`
counter rakho jo track kare kitne characters (of 26) ka count exactly match karta hai.

```python
from collections import Counter

def check_inclusion(s1, s2):
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    window = Counter(s2[:len(s1)])      # pehla window
    if window == need:
        return True
    for i in range(len(s1), len(s2)):
        window[s2[i]] += 1              # right se add
        left_ch = s2[i - len(s1)]
        window[left_ch] -= 1           # left se remove
        if window[left_ch] == 0:
            del window[left_ch]        # zero counts hata do warna == fail karega
        if window == need:
            return True
    return False
```

Window slide hone pe sirf **do characters** badalte hain (ek add, ek remove) — isliye
har step O(1)-ish update, aur poora algorithm linear.

## Complexity

- **Time:** O(n) — `n = len(s2)`. Har slide pe constant work; `Counter` compare 26 keys
  tak, jo constant maana jaata.
- **Space:** O(1) — at most 26 letters dono counters me.

## Common Pitfalls

- **`len(s1) > len(s2)` check bhulna** — warna pehla window hi out of range / galat.
- **Zero-count keys delete na karna** — `Counter == Counter` me ek side pe `{'a':0}`
  ho to equality fail. Count 0 hone pe key `del` karo (ya fixed 26-array use karo).
- **Window size variable banana** — yahan window **fixed** hai (`len(s1)`); isko
  variable-window problems se mat confuse karo.
- **Har step pe poori string sort/compare karna** — O(n·m log m), bekaar slow. Incremental
  count update + ek `matches` counter rakhna best hai.
- **Subsequence ke saath confuse** — permutation **contiguous substring** hona chahiye.

## When to Use This Pattern

"Kya koi anagram / exact-multiset-match window exist karti hai" ya "fixed-length window
jisme kuch satisfy ho" — jab aisa dikhe to **fixed-size sliding window with frequency
counts** socho. Direct cousin: "Find All Anagrams in a String" (saare start indices
return karo).

## NeetCode Link

https://neetcode.io/problems/permutation-string
