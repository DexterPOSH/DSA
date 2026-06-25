# Design Add and Search Words Data Structure

**Category:** Tries
**Difficulty:** medium

## Problem Statement

Design a data structure `WordDictionary` that supports adding words and searching
words — where a search word may contain the wildcard character `.`, which matches
**any single letter**.

- `addWord(word)` — store `word`.
- `search(word)` — return `True` if any stored word matches `word`, where `.` is a
  wildcard matching exactly one character.

```
wd = WordDictionary()
wd.addWord("bad")
wd.addWord("dad")
wd.addWord("mad")
wd.search("pad")   -> False
wd.search("bad")   -> True
wd.search(".ad")   -> True    # ".ad" matches bad / dad / mad
wd.search("b..")   -> True    # "b.." matches bad
```

## Real-World Analogy

**What Azure Cognitive Search is:** Azure Cognitive Search is Azure's managed search engine for building indexes over application content and querying them with full-text, filtered, and pattern-based searches. Instead of reading every document at query time, Azure uses the index's term structure to jump directly to candidate terms. That makes it a good analogy for a word dictionary that must answer many searches after words are added.

**What wildcard query matching is, and why it's used:** Azure Cognitive Search supports wildcard-style term queries in its full Lucene query syntax, such as a single-character wildcard (`?`) when one character is unknown. Our problem uses `.` for that same idea: exactly one unknown letter, not zero or many. Wildcards exist because users often know a word's shape but not every character; the search engine can follow fixed letters narrowly and branch only where the unknown slot appears, pruning branches that cannot finish the pattern.

**The mapping:** `addWord(word)` builds the Azure-like term index as a trie. During `search`, a literal character is one exact child edge, while `.` is the wildcard slot that fans out to every child at that depth and runs DFS on each possibility. When the pattern is consumed, `is_end` confirms a stored word really ends there; the key insight is that wildcard search is normal trie traversal until an unknown character forces controlled branching.

## Approach

`addWord` bilkul normal trie insert hai. Saara maza `search` me hai — jab `.`
milta hai to single path ki jagah humein **har child pe recurse** karna padta hai.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):
        def dfs(node, i):
            if i == len(word):
                return node.is_end           # poora word khatam -> end flag chahiye
            ch = word[i]
            if ch == '.':
                # wildcard: kisi bhi child se aage match ho gaya to kaafi
                for child in node.children.values():
                    if dfs(child, i + 1):
                        return True
                return False
            else:
                # fixed char: bas wahi ek raasta
                nxt = node.children.get(ch)
                return dfs(nxt, i + 1) if nxt else False

        return dfs(self.root, 0)
```

`i` index track karta hai ki word me kahan tak pahunche. Har step pe:

- **Fixed char** → us char ka child dekho; nahi mila to `False`, mila to aage recurse.
- **`.`** → saare children pe try karo; koi bhi `True` dega to `True`.
- **End of word** → current node ka `is_end` return karo.

## Complexity

- **Time:** `addWord` → O(L). `search` worst case → **O(26^d · L)** type, par
  precisely: agar word me `m` dots hain to woh nodes pe branch karte hain. No-dot
  search O(L). All-dots search trie ke poore branching subtree ko explore kar sakta
  hai — bounded by number of trie nodes visited. (L = word length.)
- **Space:** O(total chars added) for the trie + O(L) recursion depth during search.

## Common Pitfalls

- **End-of-word pe `is_end` check bhulna** — `i == len(word)` pe agar tum bas `True`
  return kar do (node mila isliye), to `"ba"` search `"bad"` store hone pe galat
  `True` de dega. Hamesha `node.is_end` return karo.
- **`.` pe sirf pehla child try karna** — saare children pe loop karna zaroori hai;
  ek branch fail ho to next try karo, tabhi pura `for ... if dfs(): return True`.
- **`None` node pe recurse** — fixed char ka child missing ho sakta hai; pehle check
  `if nxt` warna `AttributeError`.
- **`.` ko literal samajhna** — `.` matches exactly **one** char, zero ya multiple
  nahi (yeh regex `.` jaisa hai, `.*` jaisa nahi). `"b."` length-2 words se hi match.
- **Iterative loop se start karna** — `.` ki wajah se search inherently recursive
  (branching) hai; pure loop se likhna painful ho jaata.

## When to Use This Pattern

Jab dikhe **"dictionary + wildcard / pattern match / partial query"** — trie banao
aur search ko **DFS** bana do jahan wildcard pe saari branches explore ho. Cue:
"exact lookup nahi, balki pattern (kuch chars unknown) match karna hai." Cousins:
Implement Trie (base), Word Search II (trie + grid DFS), regex-lite matchers.

## NeetCode Link

https://neetcode.io/problems/design-word-search-data-structure
