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

Socho ek **Boggle board** hai aur tumhare paas ek lambi word-list. Naive tareeka:
har word ke liye poora board pe alag-alag DFS chalao — par agar 10,000 words hain
aur bahut saare same prefix se start hote hain (`"app"`, `"apple"`, `"apply"`), to
tum baar-baar wahi `a→p→p` raasta dobara explore karoge. **Bekaar mehnat.**

Ab socho saare words ko ek **single trie** me daal do. Ab board pe sirf **ek hi DFS**
chalao, par har step pe trie ko saath-saath neeche le jao. Board ka current letter
agar trie node ke children me hai tabhi aage badho — **warna turant ruk jao** (us
direction me koi word ban hi nahi sakta). Trie tumhara "saare words ek saath" wala
GPS ban jaata hai: ek traversal me poori word-list check ho jaati hai, aur dead
directions pehle hi kat jaate hain.

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
