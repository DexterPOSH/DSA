# Binary Tree Right Side View

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Imagine standing on the **right side** of a binary tree. Return the values of the nodes you can see, **ordered top to bottom** — i.e. the **last node of each level** (the rightmost one).

```
        1            <- see 1
       / \
      2   3          <- see 3 (rightmost of its level)
       \   \
        5   4        <- see 4

binary-tree-right-side-view(root)  ->  [1, 3, 4]
```

Note: it's not always the literal right-edge chain. If the right subtree is shallow and the left subtree goes deeper, a deeper level's rightmost node may come from the **left** side.

## Real-World Analogy

**What Azure Portal's Resource Manager tree is:** The Azure portal visualizes Resource Manager scopes as a navigable hierarchy so operators can browse Management Groups, Subscriptions, Resource Groups, and Resources. The underlying parent/child relationships do not depend on screen position, but the UI still renders siblings in a visible left-to-right order. That display order lets us talk about what would be visible from one side of the tree.

**What right-edge visibility is, and why it's used:** A right-side view is like a compact Azure portal summary that keeps only the rightmost visible scope at each depth. Instead of listing every resource at a tier, it records the item that would not be hidden by siblings when looking from the right edge. This kind of per-level representative is useful when the shape matters but the full tier list is more detail than you need.

**The mapping:** BFS processes one Azure tier at a time from left to right. For each level, keep overwriting the visible candidate as nodes are popped, or simply record the last node processed for that level. The key insight is that the queue already groups nodes by depth, so the final item in each level is exactly the right-side view.

## Approach

Yeh **level order traversal (BFS)** ka chhota twist hai: har level process karte waqt, us level ka **last node** answer me daal do.

```python
from collections import deque

def right_side_view(root):
    if not root:
        return []
    res, q = [], deque([root])
    while q:
        n = len(q)
        for i in range(n):              # process one full level
            node = q.popleft()
            if i == n - 1:              # last node of this level = rightmost
                res.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
    return res
```

`i == n - 1` wala check hi poora kaam karta hai — left-se-right enqueue hone ki wajah se level ka aakhri pop hamesha rightmost hota hai.

> **DFS alternative:** root-right-left order me DFS karo, aur har **depth pe sabse pehli baar** jo node mile usse record karo (`if depth == len(res): res.append(node.val)`). Right ko pehle visit karne se wahi rightmost-per-level milta hai. O(n) time, O(h) space.

Pattern: **BFS level scan, pick the last of each level** (ya DFS right-first, first-seen-per-depth).

## Complexity

- **Time:** O(n) — har node ek baar enqueue/dequeue.
- **Space:** O(n) — BFS me queue ek poori level (worst case ~n/2 nodes) hold kar sakti hai.

## Common Pitfalls

- **"Bas right child ki chain follow kar lo" maan lena** — galat. Agar kisi level pe rightmost node left-subtree se aata hai (right subtree chhota hai), to plain right-pointer chain usse miss kar degi. Hamesha poora level scan karo.
- **`i == n - 1` ki jagah `i == 0` (leftmost) le lena** — yeh "left side view" ban jaayega. Right side = last node.
- **Empty tree** — `[]` return karo.
- **DFS me left-first karna** — DFS approach me agar left ko pehle visit kiya, to har depth pe leftmost record hoga; right-first visit karna zaroori hai.

## When to Use This Pattern

"Har level se ek representative node chahiye" (rightmost / leftmost / max / average) → **BFS level traversal + per-level pick**. Cousins: Level Order Traversal, Largest Value in Each Row, Average of Levels. Cue: "ek side se dikhne wale / per-layer ek element" → level scan karke chuno.

## NeetCode Link

https://neetcode.io/problems/binary-tree-right-side-view
