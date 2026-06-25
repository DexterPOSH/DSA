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

**What Azure Cosmos DB is:** Azure Cosmos DB is Azure's globally distributed NoSQL database for storing JSON-like documents with low-latency reads and writes. It scales by spreading data across partitions while still letting related items be found through a chosen key. For grouping anagrams, we want every word with the same letter inventory to route to the same group.

**What a partition key is, and why it's used:** A Cosmos DB partition key is a value taken from each item that determines its logical partition. Items with the same partition key live together logically, which makes targeted reads efficient and avoids expensive fan-out across many partitions. The key must be stable and meaningful, because it is the routing label Cosmos DB uses to decide where related data belongs.

**The mapping:** For each word, create a canonical signature — either sorted letters like `aet` or a 26-count tuple — and treat that signature like the Cosmos DB partition key. `eat`, `tea`, and `ate` all produce the same key, so the hash map appends them to the same list. The key insight is that the original word order can vary, but a canonical partition key makes equivalent anagrams land in one Azure-style bucket.
## Approach

For each word, build a **canonical key** that is the same for anagrams, then group words by that key in a hash map (`key -> list of words`).

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

Sorting each word costs `O(k log k)`. To avoid that, build the key from a **26-length count array** — one count per lowercase letter. Anagrams have identical count vectors. Convert it to a tuple so it can be used as a dictionary key (lists are not hashable).

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

Assume `n` = number of words and `k` = max word length.

- **Sorted key:** Time **O(n·k log k)** — each word must be sorted. Space **O(n·k)** for the map.
- **Count key (optimal):** Time **O(n·k)** — scan each word once to compute counts, with no sorting. Space **O(n·k)**.

## Common Pitfalls

- **Trying to use a list as a dictionary key** — lists are unhashable in Python, so convert the count array to `tuple(count)`.
- **Getting a `KeyError` with a plain `dict`** — `dict[key].append(...)` crashes the first time a key appears. Use `defaultdict(list)` or `setdefault`.
- **Treating the sorted form as the output** — `"aet"` is only an internal key; return the original words (`eat`, `tea`), not the sorted version.
- **Assuming lowercase-only input** — if uppercase or Unicode can appear, a 26-slot array is not enough; then `sorted()` or a general `Counter` key is safer.

## When to Use This Pattern

When you see *"split items into groups that become equal after a transform or normalization"* — think **canonical key + hash map of lists**. Anagrams, numbers with the same digits, and strings that match after rotation/normalization all use the same trick: build a signature that is identical for every member of a group, then bucket by that signature.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of building the canonical key and bucketing words.

## NeetCode Link

https://neetcode.io/problems/anagram-groups
