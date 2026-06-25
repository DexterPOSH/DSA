# Word Search

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given an `m x n` grid of characters `board` and a string `word`, return `True`
if `word` exists in the grid. The word can be constructed from letters of
**sequentially adjacent** cells (horizontally or vertically neighboring). The
**same cell may not be used more than once** in a single word.

```
board = [["A","B","C","E"],
         ["S","F","C","S"],
         ["A","D","E","E"]]

word = "ABCCED"   ->  True     # A(0,0)->B(0,1)->C(0,2)->C(1,2)->E(2,2)->D(2,1)
word = "SEE"      ->  True
word = "ABCB"     ->  False    # 'B' at (0,1) can't be reused
```

## Real-World Analogy

**What Azure AI Search is:** Azure AI Search is a managed search service that ingests documents, analyzes text into tokens, and builds indexes so applications can query content quickly. Instead of scanning every document for every request, Azure AI Search uses its index to jump to likely matches and verify them. That makes it a good analogy for proving a specific sequence exists in a structured space.

**What token-position traversal is, and why it's used:** Search indexes can keep positional information about where tokens occur, which helps phrase or proximity queries verify that terms appear in the required order and closeness. This exists because a simple bag of matching tokens can produce false positives: the words may be present but not connected the way the query requires. A traversal abandons a candidate as soon as the next required token is missing, reused, or not in a valid neighboring position.

**The mapping:** Each board cell is an Azure AI Search token position, and each character in the word is the next query token to prove. DFS moves to an adjacent matching cell, marks it visited so the same position is not reused in the path, and backtracks by clearing the mark when the branch dead-ends. The key insight is to carry just enough path state to prevent illegal reuse, then undo that state so other query paths can be tested.

## Approach — grid DFS with backtracking

Har cell ko ek **potential starting point** maano. Jis cell ka letter
`word[0]` ke equal ho, wahan se DFS shuru karo. DFS me index `i` track karta hai
ki word ka kaunsa letter abhi match karna hai.

DFS at `(r, c, i)`:
1. Agar `i == len(word)` → poora word mil gaya, `True`.
2. Bounds ke bahar, ya `board[r][c] != word[i]`, ya cell already visited → `False`.
3. Current cell ko **mark visited** karo (in-place `#` se overwrite — clever trick,
   no extra visited set chahiye).
4. Chaaro directions me recurse karo `i+1` ke liye. Koi bhi `True` de to `True`.
5. **Backtrack:** cell ka original letter wapas restore karo (un-mark).

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, i):
        if i == len(word):
            return True
        if (r < 0 or c < 0 or r >= rows or c >= cols
                or board[r][c] != word[i]):
            return False
        board[r][c] = "#"                    # mark visited in-place
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1)
                 or dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        board[r][c] = word[i]                # BACKTRACK: restore
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
```

> **`#` overwrite trick:** alag `visited` set rakhne ke bajaye current path ke
> cell ko temporarily `#` bana dete ho (jo word me kabhi nahi hoga). Restore on
> the way out. Saves O(m·n) space aur lookups O(1) inline ho jaate hain.

## Complexity

- **Time:** O(m · n · 4^L) — har starting cell se, har step pe up to 4 choices,
  L = `len(word)` depth tak. Practically pruning (letter mismatch) bahut branches
  jaldi kaat deta.
- **Space:** O(L) recursion stack depth. In-place marking se koi extra grid nahi.

## Common Pitfalls

- **Backtrack restore bhulna** — `board[r][c] = word[i]` na karo to grid corrupt,
  aur ek hi cell future paths me galat se "used" reh jaata.
- **Visited check chhodna** — bina marking ke same cell ko word me dobara use kar
  loge (e.g. `"ABCB"` galat se `True` aa jayega).
- **Base case order** — `i == len(word)` ka success check, mismatch/bounds check
  se **pehle** hona chahiye, warna last letter match hone ke baad bhi out-of-bounds
  recurse kar ke `False` aa sakta.
- **Empty word / empty board** edge cases handle karo.
- **(Micro-opt)** agar `Counter(word)` ke kisi letter ka count grid me available
  count se zyada ho → turant `False`. Bonus pruning.

## When to Use This Pattern

Grid me "kya ek path/shape banta hai jo X satisfy kare" → **DFS + backtracking on
a grid**. Cue: 2D board, adjacency moves, ek hi cell reuse nahi. Cousins:
Number of Islands (DFS flood), Surrounded Regions, Path with constraints. Mantra:
choose a direction → recurse → un-choose (restore).

## NeetCode Link

https://neetcode.io/problems/search-for-word
