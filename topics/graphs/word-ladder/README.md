# Word Ladder

**Category:** Graphs
**Difficulty:** hard

## Problem Statement

Given a `beginWord`, an `endWord`, and a `wordList`, return the length of the **shortest transformation sequence** from `beginWord` to `endWord`, where:
- Each step changes **exactly one letter**.
- Every intermediate word must be in `wordList`.

Return `0` if no such sequence exists. The length counts **every word including begin and end**.

```
beginWord = "hit", endWord = "cog"
wordList  = ["hot","dot","dog","lot","log","cog"]
->  5      # hit -> hot -> dot -> dog -> cog   (5 words)
```

## Real-World Analogy

Socho ek **word-maze** hai. Har word ek room hai, aur do rooms ke beech darwaza tabhi hai jab wo words **sirf ek letter** me alag ho. Tumhe `beginWord` room se `endWord` room tak **sabse chhote raaste** se pahunchna hai. Maze me shortest path dhoondhne ka classic tareeka: **BFS — level by level fan out**, jaise paani ek jagah girao aur ripples sab directions me ek saath failte hain. Jo ripple sabse pehle `endWord` ko chhuye, wahi shortest path. DFS yahan galat hai — wo ek raasta poora andar tak jaata hai, shortest guarantee nahi.

## Approach — BFS shortest path

Unweighted graph me shortest path = **BFS**. Har word ek node, ek-letter-difference = ek edge.

**Trick — neighbors efficiently:** har word ke har position pe `'a'..'z'` try karke check karo ki wo word `wordList` (ek **set**, O(1) lookup) me hai. `L` length, 26 letters → har word ke `26·L` candidates, bina poori list scan kiye.

```python
from collections import deque

def ladder_length(beginWord, endWord, wordList):
    words = set(wordList)
    if endWord not in words:
        return 0
    q = deque([(beginWord, 1)])          # (word, distance-so-far)
    visited = {beginWord}
    while q:
        word, steps = q.popleft()
        if word == endWord:
            return steps
        for i in range(len(word)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nxt = word[:i] + c + word[i+1:]
                if nxt in words and nxt not in visited:
                    visited.add(nxt)     # mark on ENQUEUE, not dequeue
                    q.append((nxt, steps + 1))
    return 0
```

> **Why mark visited on enqueue:** BFS me jaise hi koi word queue me daalo, uska shortest distance fix ho jaata. Dobara enqueue karne ka koi fayda nahi — aur na karne se duplicates aur blow-up bachta hai.

> **Pro upgrade — bidirectional BFS:** dono ends se ek saath BFS chalao, beech me mil jao. Frontier exponentially chhota rehta — `O(b^(d/2))` vs `O(b^d)`. Interview me mention karna strong signal hai.

## Complexity

- **Time:** O(N · L² · 26) → effectively **O(N · L²)** — `N` words, har word ke liye `L` positions × 26 letters, aur har candidate banane/compare me O(L). (`N = len(wordList)`, `L = word length`.)
- **Space:** O(N · L) — queue + visited set + the word set.

## Common Pitfalls

- **`endWord` list me hai ya nahi pehle check na karna** — agar nahi hai to answer hamesha `0`; early return saves work.
- **DFS use karna** → shortest path guarantee nahi. Single-letter-change shortest = **BFS only**.
- **`wordList` ko list rakhna** → har neighbor check O(N). **Set** banao → O(1) membership.
- **Visited mark karna dequeue pe (popleft ke baad)** → same word multiple baar queue me, exponential blow-up. **Enqueue pe mark karo.**
- **Counting off-by-one** — length me begin aur end dono count hote hain. `hit→hot→dot→dog→cog` = **5**, not 4. Isliye distance `1` se shuru.
- **Neighbors banane ka O(N·L) approach** — har pair compare karna slow; better hai `26·L` pattern generation per word.

## When to Use This Pattern

"Shortest number of steps / minimum transformations / fewest moves" on an **unweighted** graph (har move equal cost) → **BFS**. Cue words: *shortest*, *minimum steps*, *fewest*, *least moves*, implicit graph jahan states edges define karte hain (Word Ladder, Open the Lock, Rotting Oranges, Knight moves). Weighted edges aaye to Dijkstra socho; yahan sab edges weight-1 hain to plain BFS optimal hai.

## Practice

- Visual: open `topics/graphs/word-ladder/visual.html`

## NeetCode Link

https://neetcode.io/problems/word-ladder
