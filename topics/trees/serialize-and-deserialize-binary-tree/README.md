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

**What Azure Resource Manager is:** Azure Resource Manager is Azure's control plane for deploying and organizing cloud resources. ARM templates and Bicep files sit on top of that control plane as infrastructure-as-code formats, capturing resources and relationships so an environment can be reviewed, versioned, and recreated. Exporting and redeploying is essentially turning a live Azure structure into text and then rebuilding it.

**What template serialization with null shape markers is, and why it's used:** When a hierarchy has optional child slots, values alone do not fully describe the shape. Explicit markers for missing children preserve where a branch is absent, just as infrastructure-as-code needs enough relationship data to recreate the same parent/child structure. Without those markers, different Azure-shaped trees could produce the same token stream and deserialize incorrectly.

**The mapping:** Serialization writes the tree like an Azure template export in preorder: current node, then left child, then right child, using a null token for empty slots. Deserialization consumes tokens in the same order, creating a node for each value and returning `None` for each null marker. The key insight is that values plus explicit missing-child markers make the stream self-describing enough to rebuild the exact tree.

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
