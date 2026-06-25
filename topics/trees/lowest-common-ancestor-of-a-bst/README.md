# Lowest Common Ancestor of a BST

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Given a **Binary Search Tree (BST)** and two nodes `p` and `q` that both exist in it, return their **Lowest Common Ancestor (LCA)** — the deepest node that has both `p` and `q` as descendants (a node is allowed to be a descendant of itself).

```
        6
       / \
      2   8
     / \ / \
    0  4 7  9
      / \
     3   5

LCA(2, 8)  ->  6    # split point: 2 goes left, 8 goes right
LCA(2, 4)  ->  2    # 4 is in 2's subtree, and a node can be its own ancestor
LCA(3, 5)  ->  4
```

## Real-World Analogy

**What Azure Policy is:** Azure Policy is Azure's governance service for defining rules, auditing compliance, and enforcing standards across Azure resources. Policies can be assigned at different scopes such as Management Groups, Subscriptions, or Resource Groups. Child scopes inherit applicable governance from their nearest relevant ancestors.

**What policy scope inheritance is, and why it's used:** Inheritance lets Azure teams define a rule once at a shared scope instead of duplicating it on every resource. When two resources need a common governance context, the important scope is the lowest place in the hierarchy that still contains both of them. In a BST analogy, ordered values let us find that split point without searching both full paths blindly.

**The mapping:** Starting at the root, compare both target values to the current node. If both are smaller, the common Azure-like scope must be in the left branch; if both are larger, it must be in the right branch. The key insight is that the first node where the targets split — or one target equals the node — is the lowest common ancestor.

## Approach

BST ki ordering exploit karo — **poora tree traverse karne ki zaroorat nahi**. Root se chalo:

- `p.val` aur `q.val` **dono `node.val` se bade** → LCA right me, `node = node.right`.
- **dono chhote** → LCA left me, `node = node.left`.
- **warna** (ek chhota ek bada, ya koi ek `node` ke barabar) → yahi split point, `node` hi LCA hai.

```python
def lowest_common_ancestor(root, p, q):
    node = root
    while node:
        if p.val > node.val and q.val > node.val:
            node = node.right       # both bigger -> go right
        elif p.val < node.val and q.val < node.val:
            node = node.left        # both smaller -> go left
        else:
            return node             # split (or one equals node) -> LCA
```

Pattern: **BST guided descent**. Iterative loop O(1) space me chalti hai; recursion bhi same logic, but stack leta hai.

## Complexity

- **Time:** O(h) — h = tree ki height. Har step me ek level neeche jaate ho. Balanced BST me O(log n), skewed me O(n).
- **Space:** O(1) — iterative version sirf ek `node` pointer rakhti hai, koi recursion stack nahi.

## Common Pitfalls

- **General-tree wala LCA algorithm yaha use karna** — wo O(n) hai. BST me ordering ka faida lo, warna interviewer poochega "BST hone ka kya use kiya?"
- **Strict vs non-strict comparison** — "node khud apna ancestor ho sakta hai", isliye `>` aur `<` use karo (strict). Agar `>=` use kiya to jis node pe `p` ya `q` baitha hai usse aage nikal jaoge aur galat answer.
- **`p < q` assume karna** — input kisi bhi order me aa sakta hai; dono comparisons (`p` aur `q` dono) likho, sirf ek node pe rely mat karo.
- **Recursion me return bhulna** — recursive likh rahe ho to child call ka result `return` karna mat bhoolo.

## When to Use This Pattern

Jab BST ho aur "navigate / search / range / kth / LCA" maanga jaaye → **ordering se direction choose karke descent**. Cue: "BST" + "do nodes ke beech ka relationship" → values compare karke left/right decide karo, poora tree mat ghoomo. Non-BST general tree me yahi problem ek alag (O(n) postorder) approach maangti hai.

## NeetCode Link

https://neetcode.io/problems/lowest-common-ancestor-in-binary-search-tree
