# Validate Binary Search Tree

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Given the `root` of a binary tree, determine whether it is a **valid binary search tree (BST)**. A valid BST means:

- Every node in the **left** subtree of a node is **strictly less** than the node.
- Every node in the **right** subtree is **strictly greater** than the node.
- Both subtrees are themselves valid BSTs.

The catch: it's the *whole subtree*, not just the immediate children.

```
        5
       / \
      1   7        ->  True
         / \
        6   8

        5
       / \
      1   7        ->  False   (4 is in 7's right subtree but 4 < 5)
         / \
        6   4
```

## Real-World Analogy

**What Azure Cosmos DB and Azure Cognitive Search indexing is:** Azure Cosmos DB and Azure Cognitive Search are Azure services that use indexes to avoid scanning every stored item for ordered queries. Cosmos DB indexes document properties for filters and ranges, while Azure Cognitive Search builds searchable indexes over content and fields. In both cases, ordered index behavior depends on values staying within the correct ranges.

**What inherited range-bound validation is, and why it's used:** A local comparison is not enough for an ordered index, because a value can be less than its parent but still violate a higher ancestor's allowed range. Query engines rely on the guarantee that an entire left partition is below the current key and an entire right partition is above it. Passing inherited low/high bounds preserves that global Azure index invariant at every level.

**The mapping:** Validate the BST by carrying the allowed `(low, high)` range into each node. The left child receives `(low, node.val)`, the right child receives `(node.val, high)`, and any value outside its inherited range fails immediately. The key insight is that a BST is globally ordered, not just parent-child ordered, so every node must satisfy all ancestor constraints.

## Approach

**Naive galti:** sirf `node.left < node < node.right` check karna. Yeh fail hota hai kyunki ek deep left-subtree ka node apne grandparent ka rule tod sakta hai (upar wala `4` dekho).

**Optimal — min/max bounds propagate karo:** har node ko ek valid range `(low, high)` me hona chahiye. Root ka range `(-∞, +∞)`. Jab left jaate ho, `high` ko current node value se replace kar do (left me sab chhote hone chahiye). Right jaate ho to `low` ko current node value se replace kar do.

```python
def is_valid_bst(root):
    def valid(node, low, high):
        if not node:
            return True                      # empty subtree -> always valid
        if not (low < node.val < high):      # strict bounds
            return False
        return (valid(node.left,  low, node.val) and
                valid(node.right, node.val, high))
    return valid(root, float('-inf'), float('inf'))
```

Pattern: **DFS with propagated bounds**. Alternatively, an **inorder traversal of a BST yields strictly increasing values** — so you can inorder-walk and check each value is greater than the previous one.

## Complexity

- **Time:** O(n) — har node exactly ek baar visit hota hai.
- **Space:** O(h) — recursion stack, h = tree height. Balanced me O(log n), skewed me O(n).

## Common Pitfalls

- **Sirf immediate children check karna** — sabse common bug. Range propagate karna zaroori hai, warna deep violation miss ho jaata.
- **`<=` vs `<`** — BST me values usually **strictly** increasing hoti hain. `low <= node.val` likha to duplicate-equal value galat pass kar jayega. Default: strict.
- **Integer overflow (C++/Java me)** — `-∞/+∞` ke liye `INT_MIN/INT_MAX` use kiya aur node ki value wahi nikli to bound fail karega. Python me `float('inf')` se yeh problem nahi, par interview me mention karo (use `long` ya nullable bounds).
- **Inorder approach me previous value reset karna bhulna** ya use `None` se compare na karna.

## When to Use This Pattern

Jab koi tree property check karni ho jo **subtree-wide constraint** ho (sirf local nahi) — "is this a valid BST", "range sum", "node within bounds" — to socho: **DFS me upar se context (min/max, path-sum, depth) neeche propagate karo**. Cue: "valid hai ya nahi, har node ko poore subtree ke against verify karna hai."

## Visual

Open [visual.html](visual.html) for an interactive DFS walkthrough showing the `(low, high)` window narrowing at each node.

## NeetCode Link

https://neetcode.io/problems/valid-binary-search-tree
