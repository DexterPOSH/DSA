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

Socho tum ek **family tree ko aaine (mirror) me dekh rahe ho**. Har person abhi bhi wahi hai, but "left wala beta" ab "right wala beta" ban gaya aur ulta bhi. Mirror sirf top node pe lagao to kaafi nahi — har level pe, har node ke do bachche aapas me jagah badal lete hain. Aur jab tum kisi node pe pahunchte ho, to usse neeche ka poora subtree bhi already flip ho chuka hota hai. Bas yahi recursion hai: "mera left aur right swap karo, phir dono ko bolo apne aap ko flip kar lo."

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
