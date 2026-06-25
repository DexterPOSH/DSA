# Count Good Nodes in Binary Tree

**Category:** Trees
**Difficulty:** medium

## Problem Statement

A node `X` in a binary tree is called **good** if, on the path from the **root down to X**, there is **no node with a value greater than X**. In other words, `X` is at least as large as every ancestor on its path. Return the number of good nodes. (The root is always good — its path is just itself.)

```
        3
       / \
      1   4
     /   / \
    3   1   5

Good nodes: 3(root), 4, 5, and the lower 3.   ->  4

  - 3 (root): good (always).
  - 1: ancestor 3 is bigger -> NOT good.
  - 3 (under 1): max on path is 3, 3 >= 3 -> good.
  - 4: path max before it is 3, 4 >= 3 -> good.
  - 1 (under 4): path has 4 -> NOT good.
  - 5: path max is 4, 5 >= 4 -> good.
```

## Real-World Analogy

**What Azure Defender for Cloud is:** Azure Defender for Cloud, now Microsoft Defender for Cloud, helps assess and improve the security posture of Azure resources and subscriptions. It surfaces recommendations, alerts, and secure-score-style signals so teams can see which parts of an estate are strongest or weakest. In this analogy, every scope in the Azure hierarchy has a security score.

**What Secure Score path tracking is, and why it's used:** As governance flows from a Management Group down to Subscriptions, Resource Groups, and Resources, a child is often judged in the context of what has already been seen on its inherited path. Carrying the best score so far creates a high-water mark: a scope is notable when it matches or exceeds every ancestor before it. This avoids comparing a node to unrelated branches that do not govern it.

**The mapping:** DFS carries the current Azure high-water score from parent to child. When `node.val >= max_so_far`, count the node as good, then pass `max(max_so_far, node.val)` into both children. The key insight is that each node only needs one piece of path state — the maximum ancestor value — not the full route back to the root.

## Approach

**DFS, path ke saath running max carry karo.** Har node pe: agar `node.val >= max_so_far` → good (count karo). Phir bachchon me `max(max_so_far, node.val)` paas karo.

```python
def good_nodes(root):
    def dfs(node, max_so_far):
        if not node:
            return 0
        good = 1 if node.val >= max_so_far else 0
        new_max = max(max_so_far, node.val)
        good += dfs(node.left, new_max)
        good += dfs(node.right, new_max)
        return good

    return dfs(root, float('-inf'))
```

Root ko `-inf` ke saath start karte hain taaki wo hamesha good ginaa jaaye. Har subtree apne good nodes ka count laut-ता hai, jise hum jod dete hain.

Pattern: **DFS with a downward-accumulated parameter (running max)**. State neeche bahti hai (max), aur count upar return hota hai.

## Complexity

- **Time:** O(n) — har node exactly ek baar visit hota hai, har visit pe O(1) kaam.
- **Space:** O(h) — recursion stack tree ki height jitna. Balanced me O(log n), skewed me O(n).

## Common Pitfalls

- **`>` use karna `>=` ki jagah** — "good" ki definition me ancestor ka value node se **bada** nahi hona chahiye; barabar chalta hai. `>=` se ties ko good count karo, warna valid good nodes miss honge.
- **Max ko upar-ki-taraf return/share karna** — running max **neeche** flow karta hai (parameter), koi shared mutable state nahi. Galat se ek global `max` update karoge to siblings ek doosre ko pollute karenge.
- **Root ko good na ginna** — root ka path sirf khud hai, wo hamesha good hai. `-inf` initial max isse automatically handle karta hai.
- **`new_max` compute karna bhulna** — child ko purana max paas kar diya to deeper nodes galat tarah good gine jaa sakte hain.

## When to Use This Pattern

Jab har node ka faisla **root-se-uss-node tak ke path ki property** pe depend kare (max, min, sum, count-along-path) → **DFS me wo property ko parameter ki tarah neeche le jao**. Cousins: Path Sum, Max Path Through Root, Sum of Root-to-Leaf Numbers. Cue: "node ka answer uske ancestors pe depend karta hai" → top-down DFS with accumulated state.

## NeetCode Link

https://neetcode.io/problems/count-good-nodes-in-binary-tree
