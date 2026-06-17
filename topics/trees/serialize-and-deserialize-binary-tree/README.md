# Serialize and Deserialize Binary Tree

**Category:** Trees
**Difficulty:** hard

## Problem Statement

Design two functions:

- `serialize(root)` — convert a binary tree into a single string.
- `deserialize(data)` — convert that string back into the **exact same** tree.

The tree can contain any structure (not a BST). Round-trip must be lossless: `deserialize(serialize(root))` ka result original tree ke barabar hona chahiye.

```
        1
       / \
      2   3
         / \
        4   5

  serialize ->  "1,2,#,#,3,4,#,#,5,#,#"
  deserialize back to the same tree
```

(`#` = null marker)

## Real-World Analogy

Socho ek **origami structure** hai jo tumhe courier se bhejni hai. Tum usse ek specific order me **fold karke ek flat strip** bana dete ho (serialize), aur saath me clear instructions: "yaha child hai", "yaha khaali hai (`#`)". Doosri taraf jo banda strip kholega, agar wo **bilkul same order** me fold-instructions follow kare, to exactly wahi structure wapas ban jaata. Null markers (`#`) critical hain — unke bina pata hi nahi chalega ki ek node ke kitne children the aur shape kya thi.

## Approach

Sabse clean: **preorder DFS with explicit null markers.** Har node ki value likho; null ke liye `#` likho. Deserialize me **same preorder order** me tokens consume karo — pehla token root, fir recursively left subtree build karo (jo apne aap saare tokens utha legi), fir right.

```python
def serialize(root):
    out = []
    def dfs(node):
        if not node:
            out.append('#')
            return
        out.append(str(node.val))
        dfs(node.left)
        dfs(node.right)
    dfs(root)
    return ','.join(out)

def deserialize(data):
    tokens = iter(data.split(','))
    def build():
        val = next(tokens)
        if val == '#':
            return None
        node = TreeNode(int(val))
        node.left  = build()     # consume left subtree's tokens
        node.right = build()     # then right
        return node
    return build()
```

Pattern: **preorder traversal + null sentinels.** Null markers se shape unambiguous ho jaati — yahi reconstruction ko deterministic banata. (BFS/level-order with `#` bhi valid alternative hai.)

## Complexity

- **Time:** O(n) serialize aur O(n) deserialize — har node + har null marker ek baar.
- **Space:** O(n) output string + O(h) recursion stack.

## Common Pitfalls

- **Null markers chhodna** — `#` ke bina shape recover nahi ho sakti. `[1,2]` vs `[1,#,2]` same string ban jate. Markers must.
- **Deserialize me token order galat** — serialize preorder me hai to deserialize bhi **left pehle, then right** consume kare. Order mismatch = galat tree.
- **Iterator/pointer share na karna** — saare recursive calls ko *ek hi* moving token stream dekhna chahiye (yaha `iter` use kiya). Naya split har call me banaya to tut jaayega.
- **Negative / multi-digit values** — comma se split karo, single chars assume mat karo. `-12` ek token hai.
- **Empty tree** — `root = None` → `"#"` serialize, wapas `None` deserialize. Edge case handle karo.

## When to Use This Pattern

Jab tree (ya graph) ko **persist / transmit / round-trip** karna ho — caching, sending over network, storing in DB → socho **traversal + null sentinels** (preorder DFS ya level-order BFS). Cue: "encode a tree to a string and back losslessly."

## Visual

Open [visual.html](visual.html) for an interactive walkthrough of preorder serialization producing tokens, then rebuilding the tree token-by-token.

## NeetCode Link

https://neetcode.io/problems/serialize-and-deserialize-binary-tree
