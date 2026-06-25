# Construct Binary Tree from Preorder and Inorder Traversal

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Given two arrays `preorder` and `inorder` representing the preorder and inorder traversals of a binary tree (with **unique** values), reconstruct and return the tree.

```
preorder = [3, 9, 20, 15, 7]
inorder  = [9, 3, 15, 20, 7]

reconstructs:
        3
       / \
      9   20
         /  \
        15   7
```

## Real-World Analogy

**What Azure Resource Manager inventory is:** Azure Resource Manager stores the parent/child structure of an Azure estate: Management Groups contain Subscriptions, Subscriptions contain Resource Groups, and Resource Groups contain Resources. Inventory exports or queries describe those scopes so the hierarchy can be audited, compared, or rebuilt in another environment. The same tree can be described in different deterministic orders.

**What paired hierarchy export metadata is, and why it's used:** A preorder-style export is useful because it names the parent scope before the scopes it owns, so the next unread item identifies the root of the current slice. An inorder-style export is useful because, once that root is known, it separates which scopes belong on the left side versus the right side of that root. Together, the two views remove ambiguity that either order alone would leave.

**The mapping:** Rebuilding the tree is like reconstructing an Azure hierarchy from those two inventory views. Take the next preorder value as the current root, find it in the inorder list, and use that index to split the remaining scopes into left and right subtrees. The key insight is that preorder chooses the root, while inorder gives the exact boundary for recursively rebuilding each child branch.

## Approach

Two facts ka combo:
1. **Preorder ka pehla element hamesha root hai.**
2. **Inorder me us root ki position se array do parts me bant-ta hai** — left = left subtree, right = right subtree. Left subtree ka size se pata chalta hai preorder me left subtree kaha tak hai.

Naive me har baar inorder me root dhoondhne se O(n²). Optimal: ek **hashmap `value -> inorder index`** bana lo (O(1) lookup), aur preorder ko ek moving pointer se consume karo.

```python
def build_tree(preorder, inorder):
    idx = {v: i for i, v in enumerate(inorder)}   # value -> inorder position
    self_pre = iter(preorder)                      # consume preorder left-to-right

    def build(lo, hi):                  # inorder window [lo, hi]
        if lo > hi:
            return None
        val = next(self_pre)            # next root in preorder order
        node = TreeNode(val)
        mid = idx[val]                  # split point in inorder
        node.left  = build(lo, mid - 1) # build left FIRST (preorder = root,L,R)
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(inorder) - 1)
```

Pattern: **divide and conquer / recursive partition** using one traversal to find roots and the other to find boundaries. **Left ko pehle build karna critical hai** — preorder root ke baad poora left subtree deta hai.

## Complexity

- **Time:** O(n) — har node ek baar banta, inorder index lookup O(1) hashmap se.
- **Space:** O(n) — hashmap + O(h) recursion stack.

## Common Pitfalls

- **Right ko pehle build karna** — preorder pointer galat node consume karega. Order **left, then right** strict hai.
- **Har baar inorder me linear search** — O(n²) bana deta. Hashmap se index O(1).
- **Window boundaries galat** (`mid-1`, `mid+1` off-by-one) — dry-run karke verify karo.
- **Duplicate values** — yeh algorithm unique values assume karta. Duplicates ho to inorder split ambiguous, problem hi ill-defined ho jaati.
- **Preorder pointer ko shared/mutable rakhna bhulna** — har recursive call ko *same* moving pointer dekhna chahiye (yaha `iter` se handle kiya).

## When to Use This Pattern

Jab "do traversals se tree reconstruct karo" type dikhe → socho **ek traversal root identify karta hai, doosra left/right boundary**. Preorder+Inorder ya Postorder+Inorder dono work karte (postorder me root *last* hota, to right pehle build karo). Cue: "given traversals, rebuild the structure" → recursive partition.

## Visual

Open [visual.html](visual.html) for an interactive walkthrough showing how each preorder root splits the inorder array into left/right subtrees.

## NeetCode Link

https://neetcode.io/problems/construct-binary-tree-from-preorder-and-inorder-traversal
