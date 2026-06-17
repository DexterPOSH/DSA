# Alien Dictionary

**Category:** Advanced Graphs
**Difficulty:** hard

## Problem Statement

There's an alien language using lowercase English letters, but with an **unknown order**. You're given a list of `words` that are sorted **lexicographically by the alien rules**. Derive a valid ordering of the letters (return any valid one). If the order is **invalid** (contradictory) return `""`. If multiple orders are possible, any is fine.

```
words = ["wrt","wrf","er","ett","rftt"]   ->  "wertf"
words = ["z","x"]                          ->  "zx"
words = ["z","x","z"]                      ->  ""      # invalid (cycle)
```

> Adjacent words give us **pairwise precedence** between letters. Building a graph of "letter A comes before letter B" and ordering it → **topological sort**.

## Real-World Analogy

Socho tumhe ek alien dictionary mila jisme shabd to dikh rahe hain par alphabet ka order nahi pata. Lekin shabd **sorted** hain, to do **lagatar (adjacent)** words ko compare karke ek clue milta hai. Jaise `"wrt"` phir `"wrf"`: dono `"wr"` tak same, phir `t` vs `f` — matlab is language me **`t` aata hai `f` se pehle**. Har aisa clue ek **arrow** `t → f` graph me banata hai.

Ab yeh ek "kaun pehle, kaun baad" wala dependency graph hai — bilkul course-prerequisites jaisa. **Topological sort** se ek valid linear order nikaal lo. Agar koi **cycle** ban gaya (A→B aur B→A type contradiction), to koi valid order possible hi nahi → `""`.

## Approach — build precedence graph + topological sort (Kahn's BFS)

1. Har letter ko graph me daalo (in-degree 0).
2. Har adjacent word pair `(w1, w2)` ke liye pehla differing character `c1 != c2` dhoondo → edge `c1 → c2`. **Edge case:** agar `w1` longer hai aur `w2` uska prefix hai (jaise `["abc","ab"]`), to **invalid** → `""`.
3. Kahn's algorithm: in-degree 0 wale letters se shuru, queue me daalo, process karte jao, neighbours ka in-degree ghataao.
4. Agar saare letters order me aa gaye → valid; warna cycle → `""`.

```python
from collections import defaultdict, deque

def alien_order(words):
    adj = {c: set() for w in words for c in w}
    indeg = {c: 0 for c in adj}

    for w1, w2 in zip(words, words[1:]):
        for c1, c2 in zip(w1, w2):
            if c1 != c2:
                if c2 not in adj[c1]:
                    adj[c1].add(c2)
                    indeg[c2] += 1
                break
        else:                                  # no diff found in the overlap
            if len(w1) > len(w2):
                return ""                      # prefix-longer-first = invalid

    queue = deque([c for c in indeg if indeg[c] == 0])
    order = []
    while queue:
        c = queue.popleft()
        order.append(c)
        for nxt in adj[c]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    return "".join(order) if len(order) == len(indeg) else ""   # cycle check
```

## Complexity

- **Time:** O(C) where C = total characters across all words — building edges scans adjacent pairs, topo sort is linear in nodes+edges (edges ≤ 26²).
- **Space:** O(1) effectively (at most 26 letters and 26² edges) → O(U + min(U², C)).

## Common Pitfalls

- **Prefix edge case** — `["abc","ab"]`: `"ab"` poora prefix hai but `"abc"` pehle aaya → invalid. `for…else` ka `else` branch (loop bina `break` ke khatam hua) yahi pakadta hai.
- **`break` after first diff** — sirf **pehla** differing char hi precedence deta; uske baad ke chars se koi info nahi. Break karna zaroori.
- **All distinct letters ko graph me daalna** — sirf edges wale nahi; har letter ko nodes me include karo warna woh answer se gayab ho jaayega.
- **Cycle detection** — `len(order) != total letters` → cycle → return `""`. Bhulna mat.
- **Duplicate edges** — same edge dobara add karne se in-degree galat badh jaata; `if c2 not in adj[c1]` se guard karo.

## When to Use This Pattern

"Pairwise ordering constraints se ek global order nikaalo" / "dependency / prerequisite resolution" → **topological sort** (Kahn's BFS ya DFS post-order). Cue: "valid ordering exists?", "course schedule", "build order", "sorted data se hidden order infer karo". Cycle = no valid order.

## NeetCode Link

https://neetcode.io/problems/foreign-dictionary
