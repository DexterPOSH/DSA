# Maximum Depth of Binary Tree

**Category:** Trees
**Difficulty:** easy

## Problem Statement

Given the `root` of a binary tree, return its **maximum depth** — the number of nodes along the longest path from the root down to the farthest leaf.

```
        3
       / \
      9   20         ->   depth = 3   (path 3 -> 20 -> 15 or 3 -> 20 -> 7)
         /  \
        15   7
```

Empty tree (`root = None`) ka depth `0` hai.

## Real-World Analogy

**What Azure Resource Manager's management hierarchy is:** Azure Resource Manager gives Azure resources a nested governance structure: Management Group → Subscription → Resource Group → Resource. Large organizations may add multiple Management Group layers above subscriptions to model business units or environments. The number of scopes on the longest chain tells you how deep the estate goes.

**What hierarchy depth is, and why it's used:** Depth matters because policies, RBAC assignments, budgets, and operational ownership often flow through these Azure scopes. A shallow branch may end at a subscription quickly, while another branch may pass through several management-group layers before reaching a resource. Measuring maximum depth identifies the longest path that governance or inventory traversal must follow.

**The mapping:** Each recursive call asks an Azure child scope for its deepest descendant length. A leaf returns `1`, an empty child returns `0`, and a parent returns `1 + max(left_depth, right_depth)`. The key insight is that the deepest branch completely determines the maximum depth; shorter sibling branches do not affect the answer.

## Approach

Classic **recursive DFS**. Kisi node ka depth = `1 + max(left subtree ka depth, right subtree ka depth)`. Base case: `None` ka depth `0`.

```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

Bas itna. Har node apne dono bachchon se poochta hai "tum kitne gehre ho?", bade wale ko leta hai, aur khud ke liye `+1` karta hai. Recursion neeche tak jaati hai (leaves return `1`), phir values upar bubble-up hoti hain.

Iterative **BFS** (level-by-level) bhi natural fit hai — jitne levels process karoge, wahi depth:

```python
from collections import deque
def max_depth_bfs(root):
    if not root:
        return 0
    q, depth = deque([root]), 0
    while q:
        depth += 1
        for _ in range(len(q)):          # ek poora level process karo
            node = q.popleft()
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
    return depth
```

## Complexity

- **Time:** O(n) — har node ek baar visit hota hai.
- **Space:** O(h) recursive (recursion stack), h = height. BFS me O(w) jahan w = max width of any level (worst case ~n/2).

## Common Pitfalls

- **`max` ke jagah `+` ya `min` lagana** — depth = longest path, isliye `max` chahiye, dono subtrees ka sum nahi.
- **Base case `0` na karna** — `None` ka depth `0` hota hai, `1` nahi. Galat karoge to off-by-one.
- **Leaf vs node depth confusion** — yeh problem **nodes** count karti hai (depth 3), edges (depth 2) nahi. Question dhyaan se padho.
- **Height vs depth terms** — interview me dono interchangeably use hote hain is problem ke liye; clarify kar lo agar confusion ho.

## When to Use This Pattern

"Tree ke baare me koi number nikalo jo children ke results pe depend karta hai" (depth, count, sum, max value) → **bottom-up recursive DFS**: base case `None`, dono children se values lo, `combine` karke return. Diameter, balanced-check, max-path-sum — sab isi `1 + f(left, right)` shape ke variants hain.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the recursion bubbling depths up.

## NeetCode Link

https://neetcode.io/problems/depth-of-binary-tree
