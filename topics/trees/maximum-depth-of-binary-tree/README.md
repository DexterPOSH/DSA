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

Socho ek **company ka org chart** hai — CEO top pe, neeche managers, unke neeche reports, aur aage. "Maximum depth" matlab sabse lambi reporting chain kitni gehri hai: CEO se le kar sabse junior intern tak kitne log. Tum CEO se nahi gin sakte directly — tumhe har branch neeche tak follow karni padti hai. Trick yeh hai: har manager bas apne **sabse gehre report ki depth + 1 (khud)** return karta hai. CEO ko dono taraf se jo bada number aaye, wahi answer.

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
