# Word Search II

**Category:** Tries
**Difficulty:** hard

## Problem Statement

Given an `m x n` board of characters and a list of `words`, return **all words from
the list that can be formed** on the board. A word is built from sequentially
adjacent cells (up/down/left/right), and **the same cell may not be used twice** in
one word.

```
board = [["o","a","a","n"],
         ["e","t","a","e"],
         ["i","h","k","r"],
         ["i","f","l","v"]]
words = ["oath","pea","eat","rain"]

-> ["oath","eat"]
```

## Real-World Analogy

**What Azure AI Content Safety is:** Azure AI Content Safety is Azure's moderation service for detecting harmful or policy-violating content in text and images. In a real content pipeline, OCR can turn text inside an image into characters or tokens that need to be checked before the content is published. Azure can also use custom blocklists so teams can catch organization-specific prohibited terms, not just broad safety categories.

**What trie-backed blocklist scanning is, and why it's used:** A blocked-term dictionary stores every term the moderation pipeline must detect. If OCR text is arranged like a grid, checking each blocked word separately from each cell would repeat a huge amount of work, especially when terms share prefixes. A trie-backed scan reuses those prefixes: as Azure explores neighboring OCR cells, the current trie node tells whether the path is still a possible blocked term, and a missing child means that path can be pruned immediately.

**The mapping:** The `words` list is Azure's custom blocklist, and building the trie stores all blocked terms in one shared prefix structure. The `board` is the OCR grid; DFS starts from each cell, moves to neighboring cells, marks cells as visited so one OCR cell is not reused in the same term, and carries a trie pointer along the path. When a trie child is missing we stop early, and when an end marker is reached we report the word; the key insight is that trie prefix pruning lets one grid traversal find all target words instead of running a separate search for every word.

## Approach

**Step 1 — saare words ko trie me daalo.** Har word ke last node pe poora word store
kar do (`node.word = word`) — taaki match milte hi seedha word collect kar sako, char
jodne ki zaroorat na pade.

**Step 2 — har cell se DFS, trie ke saath move karte hue.** DFS me current trie node
pass karo. Board cell ka char trie node me hai → us child me utro; word mila → answer
me daalo. Visited cells ko temporarily mark karo (no reuse), backtrack pe wapas.

```python
def findWords(board, words):
    # build trie
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node['#'] = w                      # '#' marks end + stores the whole word

    rows, cols = len(board), len(board[0])
    res = []

    def dfs(r, c, node):
        ch = board[r][c]
        nxt = node.get(ch)
        if not nxt:                        # is char ka koi word-prefix nahi -> prune
            return
        if '#' in nxt:                     # poora word ban gaya
            res.append(nxt['#'])
            del nxt['#']                   # dedupe: same word dobara na aaye

        board[r][c] = '*'                  # mark visited
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '*':
                dfs(nr, nc, nxt)
        board[r][c] = ch                   # un-mark (backtrack)

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)
    return res
```

**Pattern:** trie (saare words ek saath) + grid backtracking (DFS with visited + undo).
Trie ki wajah se DFS sirf un raaston pe jaata hai jo kisi word ka actual prefix hain.

## Complexity

- **Time:** O(`W·L`) to build the trie (W words, L avg length) + DFS worst case
  **O(m·n·4·3^(L−1))** — har cell se start, fir har step pe 3 nayi directions (jahan
  se aaye wo chhod ke), max depth = longest word length L. Practically trie pruning
  isse bahut chhota kar deta.
- **Space:** O(`W·L`) trie ke liye + O(L) recursion depth. In-place visited marking
  se koi extra visited matrix nahi (board hi reuse).

## Common Pitfalls

- **Per-word alag DFS chalana** — yeh TLE ka classic reason. Saare words ek trie me
  daal ke ek hi DFS chalana hi is problem ka point hai.
- **Visited un-mark bhulna (backtrack)** — `board[r][c]` ko `'*'` set karke wapas
  original char na karna → baaki paths corrupt. Har DFS return se pehle restore karo.
- **Word ko char-by-char rebuild karna** — leaf pe poora word store karo (`'#': w`),
  warna har match pe string concatenation slow + buggy.
- **Duplicate results** — agar ek word board pe do alag jagah se ban sakta hai to wo
  do baar aa jaayega. `del nxt['#']` (ya ek `set`) se dedupe karo.
- **Edge guards bhulna** — out-of-bounds aur already-visited check har neighbor pe
  zaroori, warna index error / infinite loop.
- **Optional optimization chhodna** — leaf nodes ko trie se prune karna (jab koi word
  match ho jaaye) bade inputs pe DFS ko aur tej karta hai; mention-worthy in interview.

## When to Use This Pattern

Jab dikhe **"grid/board + ek lambi list of words/patterns ko search karna"** ya
**"bahut saare strings ek hi space me match karna jinke prefixes overlap karte
hain"** — trie + DFS socho. Cue: agar tum ek search ko N baar repeat karte feel karo
jahan N candidates same prefix share karte hain, trie un searches ko ek me merge kar
deta. Cousins: Implement Trie (base), Add-and-Search Words (wildcard DFS), Boggle
solvers, autocomplete-over-grid.

## NeetCode Link

https://neetcode.io/problems/search-for-word-ii
