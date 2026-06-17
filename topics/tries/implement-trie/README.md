# Implement Trie (Prefix Tree)

**Category:** Tries
**Difficulty:** medium

## Problem Statement

Implement a `Trie` (prefix tree) class supporting three operations:

- `insert(word)` — add `word` to the trie.
- `search(word)` — return `True` if `word` was inserted (exact, full word).
- `startsWith(prefix)` — return `True` if any inserted word starts with `prefix`.

```
trie = Trie()
trie.insert("apple")
trie.search("apple")     -> True
trie.search("app")       -> False   # "app" was never inserted as a whole word
trie.startsWith("app")   -> True    # but "apple" starts with "app"
trie.insert("app")
trie.search("app")       -> True
```

## Real-World Analogy

Socho ek **dictionary ka shelf-of-shelves** hai. Top shelf pe 26 dabbe — `a` se
`z`. Tum "apple" rakhne jaate ho: pehle `a` wala dabba kholo, uske andar phir 26
chhote dabbe, unme se `p` kholo, phir `p`, phir `l`, phir `e`. Jis dabbe pe word
khatam hua, uspe ek **chhota flag laga do — "yahan ek poora word khatam hota
hai"**.

Ab koi `startsWith("app")` puchhe to bas `a → p → p` ka raasta follow karo — agar
raasta exist karta hai, prefix mil gaya, chahe aage word khatam ho ya na ho. Aur
`search("app")` me wahi raasta follow karo **plus** end pe flag check karo — flag
laga hai tabhi `True`. Yahi difference hai prefix aur poore word me.

## Approach

Har trie node ke paas do cheezein hoti hain:

1. `children` — ek map/array jo next character ko agle node se jodta hai.
2. `is_end` — boolean flag, "kya yahan koi inserted word khatam hota hai?"

Teeno operations ek hi shape follow karte hain — root se start karo, character ke
hisaab se neeche utro:

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # char -> TrieNode
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()   # naya raasta banao
            node = node.children[ch]
        node.is_end = True                       # word khatam -> flag laga do

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end  # raasta + end flag dono chahiye

    def startsWith(self, prefix):
        return self._walk(prefix) is not None    # sirf raasta chahiye

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None                      # raasta toot gaya
            node = node.children[ch]
        return node
```

`search` aur `startsWith` ka pura logic same hai — bas `search` extra me `is_end`
check karta hai. Isiliye humne `_walk` helper nikal liya.

## Complexity

- **Time:** `insert`, `search`, `startsWith` sab O(L) — `L` = word/prefix ki
  length. Har char ek hash lookup, length se bilkul independent of kitne words
  store kiye.
- **Space:** O(total characters inserted) worst case — agar koi prefix share na
  ho. Shared prefixes (jaise "app" + "apple") node reuse karte hain, isiliye trie
  storage me efficient hai.

## Common Pitfalls

- **`search` me `is_end` check bhulna** — tab "app" inserted na hone pe bhi `True`
  aa jaayega (kyunki "apple" ne wo raasta bana diya). Yahi poora point hai is
  problem ka.
- **`is_end` ko children-empty se confuse karna** — "app" insert karne ke baad bhi
  uske children ho sakte hain ("apple" ki wajah se). Leaf hona ≠ word end hona.
  Hamesha explicit `is_end` flag rakho.
- **Array vs dict for children** — `[None]*26` (a–z assume) thoda fast/space-tight
  hota hai, par dict zyada flexible (unicode, lazy alloc). Interview me dict simple
  aur safe.
- **Root ko ek character ki tarah treat karna** — root empty/sentinel hai, koi char
  hold nahi karta. Pehla char root ke children me jaata hai.

## When to Use This Pattern

Jab bhi dikhe **"prefix", "autocomplete", "dictionary of words", "common prefix",
ya bahut saari string lookups same set pe"** — trie socho. Cue: ek hash set sirf
exact-match deta, par jab tumhe *prefix* relationships ya char-by-char traversal
(jaise wildcard matching ya grid word-search) chahiye, tab trie jeet jaata hai.
Cousins: Add-and-Search Words (wildcard `.`), Word Search II (trie + grid DFS).

## NeetCode Link

https://neetcode.io/problems/implement-prefix-tree
