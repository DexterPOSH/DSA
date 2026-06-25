# Invert Binary Tree

**Category:** Trees
**Difficulty:** easy

## Problem Statement

Given the `root` of a binary tree, **invert** it (mirror it left-to-right) and return the new root. Har node ke left aur right children swap ho jaate hain, recursively poore tree me.

```
        4                    4
       / \                  / \
      2   7      ->        7   2
     / \ / \              / \ / \
    1  3 6  9            9  6 3  1
```

## Real-World Analogy

**What Azure Portal's hierarchy visualization is:** The Azure portal can display the Resource Manager hierarchy so users can browse Management Groups, Subscriptions, Resource Groups, and Resources. The true Azure ownership graph stays the same regardless of how sibling scopes are ordered on screen. A visualization can mirror left and right positions without changing which parent owns which child.

**What child-order mirroring is, and why it's used:** Mirroring a hierarchy view swaps the visual placement of each pair of child branches. It can be useful for alternate layouts, comparisons, or simply showing that left and right are presentation details rather than ownership details. To mirror the whole Azure tree, every nested scope must apply the same swap, not just the root.

**The mapping:** Inverting a binary tree is that recursive Azure rendering flip. At each node, swap `left` and `right`, then recurse into the children so every descendant branch is mirrored too. The key insight is that the parent/child structure remains intact; only each node's two child slots trade places.

## Approach

Yeh ek classic **recursive DFS** problem hai. Har node pe teen kaam:

1. Left aur right child ko swap karo.
2. Left subtree pe recurse karo (invert).
3. Right subtree pe recurse karo (invert).

Base case: `None` node aaye to kuch mat karo, wahi return kar do.

```python
def invert_tree(root):
    if not root:
        return None
    root.left, root.right = root.right, root.left   # swap
    invert_tree(root.left)
    invert_tree(root.right)
    return root
```

Order matter nahi karta — chahe pehle swap karo phir recurse, ya pehle recurse phir swap. Dono kaam karte hain kyunki har node apne neeche wale ko independently flip karta hai. Iterative version bhi simple hai — bas ek BFS/DFS queue ya stack use karke har node visit karte waqt children swap kar do.

```python
from collections import deque
def invert_tree_iter(root):
    q = deque([root])
    while q:
        node = q.popleft()
        if not node:
            continue
        node.left, node.right = node.right, node.left
        q.append(node.left)
        q.append(node.right)
    return root
```

## Complexity

- **Time:** O(n) — har node ko exactly ek baar visit karte hain, n = total nodes.
- **Space:** O(h) recursive — h = tree height, recursion stack ke liye. Balanced tree me O(log n), worst case (skewed tree) O(n).

## Common Pitfalls

- **Base case bhulna** — `if not root: return None` na likha to `None.left` pe crash.
- **Swap se pehle recurse karna aur galat variable use karna** — agar pehle recurse karo to make sure tum updated children pe recurse kar rahe ho ya original pe, dono fine hain but consistent raho. Tuple-swap (`a, b = b, a`) safest hai kyunki atomic hai.
- **Return value bhulna** — interviewer ko `root` return chahiye, `None` nahi.
- **Sirf top node swap karna** — yeh recursive problem hai, sirf root ke children swap karne se kaam nahi banta.

## When to Use This Pattern

Jab bhi problem me ho "tree ko transform karo / mirror / har node pe same operation apply karo" → **recursive tree DFS** socho: base case (`None`), node pe kaam, dono subtrees pe recurse. Yeh "do something at every node + combine children" template har second tree problem me dikhta hai.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the recursive swap.

## NeetCode Link

https://neetcode.io/problems/invert-a-binary-tree
