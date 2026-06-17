# Group Anagrams

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given an array of strings `strs`, group together the strings that are **anagrams** of each other. Two words are anagrams if one is a rearrangement of the other's letters (same letters, same counts). Return the groups in any order.

```
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
->  [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
```

## Real-World Analogy

Socho tum ek library me kaam karte ho aur tumhare paas Scrabble tiles ke bag pade hain. Har bag me kuch letters hain. Tumhe sare bags ko aise groups me daalna hai ki ek group ke saare bags me **bilkul same letters same count me** hon. Kaise pehchanoge? Har bag ke tiles ko **alphabet order me laga do** — `eat`, `tea`, `ate` teeno sort karne pe `aet` ban jaate hain. Yeh sorted form ek **fingerprint** hai: jin bags ki fingerprint same, woh ek group. Tum ek shelf banate ho jiska label `"aet"` hai aur usme `eat`, `tea`, `ate` rakh dete ho. Yeh shelf-by-fingerprint system hi hamara **hash map (key -> list)** hai.

## Approach

Har word ke liye ek **canonical key** banao jo anagrams ke liye same ho, phir us key pe words ko group karo (hash map me `key -> list of words`).

**Approach 1 — sorted string as key** (simple, O(n·k log k)):

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))   # "eat" -> "aet"
        groups[key].append(s)
    return list(groups.values())
```

**Approach 2 — char-count tuple as key** (optimal, O(n·k)):

Sorting har word pe `O(k log k)` lagta hai. Usse bachne ke liye key ko **26-length count array** se banao — har lowercase letter ka count. Same anagrams ka count vector identical hoga. Tuple banao taaki wo dictionary key ban sake (lists hashable nahi hoti).

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for ch in s:
            count[ord(ch) - ord('a')] += 1
        groups[tuple(count)].append(s)   # tuple is hashable
    return list(groups.values())
```

Pattern: **hash map keyed by a canonical signature**.

## Complexity

Maan lo `n` = number of words, `k` = max word length.

- **Sorted key:** Time **O(n·k log k)** — har word ko sort karna padta hai. Space **O(n·k)** map ke liye.
- **Count key (optimal):** Time **O(n·k)** — har word ko ek baar scan karke count nikalte hain, sorting nahi. Space **O(n·k)**.

## Common Pitfalls

- **List ko dictionary key banane ki koshish** — Python me list unhashable hai, isliye count array ko `tuple(count)` me convert karo.
- **`dict` use karke `KeyError`** — plain `dict[key].append(...)` crash karega agar key pehli baar aa rahi hai. `defaultdict(list)` ya `setdefault` use karo.
- **Sorted form ko output samajhna** — `"aet"` sirf ek internal key hai; output me original words (`eat`, `tea`) return karne hain, sorted version nahi.
- **Case / non-lowercase assume** — agar uppercase ya unicode aa sakti hai to 26-size array kaafi nahi; tab `sorted()` ya general `Counter` key zyada safe hai.

## When to Use This Pattern

Jab dikhe *"items ko un groups me baanto jo kisi transform/normalization ke baad equal ho jaate hain"* — socho **canonical key + hash map of lists**. Anagrams, "same digits ke numbers", "rotation/normalization ke baad equal strings" — sabme trick yahi hai: ek aisa signature banao jo group ke saare members ke liye identical ho, aur us signature pe bucket kar do.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of building the canonical key and bucketing words.

## NeetCode Link

https://neetcode.io/problems/anagram-groups
