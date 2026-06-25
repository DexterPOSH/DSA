# Diameter of Binary Tree

**Category:** Trees
**Difficulty:** easy

## Problem Statement

Given the `root` of a binary tree, return its **diameter** — the length of the **longest path between any two nodes**, measured in **edges**. Yeh path root se guzarna zaroori nahi.

```
        1
       / \
      2   3        ->   diameter = 3   (path: 4 -> 2 -> 1 -> 3,  or 5 -> 2 -> 1 -> 3)
     / \
    4   5
```

Path `4 -> 2 -> 5` ka length 2 hai, but `4 -> 2 -> 1 -> 3` ka length 3 — wahi maximum.

## Real-World Analogy

**What Azure Resource Manager's management hierarchy is:** Azure Resource Manager organizes Azure estates into a parent/child scope tree: Management Groups, Subscriptions, Resource Groups, and Resources. Any two leaf resources are connected by walking up from one leaf to a shared parent scope and then down to the other leaf. That makes the hierarchy a good analogy for measuring the longest relationship path.

**What cross-scope path analysis is, and why it's used:** Operators sometimes need to understand the widest distance across an estate, such as the longest chain between resources under different subscriptions. The path can bend at the nearest shared Management Group or Subscription, so looking only at root-to-leaf depth misses the true maximum. Each scope needs to know its deepest child branch, while the estate-wide answer checks every possible bend point.

**The mapping:** The DFS returns one Azure branch height upward because a parent can extend a path through only one child. At each node, we compute `left_height + right_height` as the path that bends through that scope and update a global diameter. The key insight is that height is the value returned to the parent, while diameter is the best two-branch path observed anywhere.

## Approach

Yeh problem ka twist: har node pe do alag cheezein chahiye —
1. **Height** (apne parent ko return karne ke liye): `1 + max(left, right)`.
2. **Diameter through this node** (global answer update karne ke liye): `left_height + right_height`.

Trick: ek hi DFS me height return karo, aur side-effect ki tarah ek global `max` diameter update karte raho. Naive approach (har node pe alag se height nikalna) O(n²) ho jaata — isliye height ko recursion ke andar hi compute karke reuse karo.

```python
def diameter_of_binary_tree(root):
    diameter = 0

    def height(node):
        nonlocal diameter
        if not node:
            return 0
        left = height(node.left)
        right = height(node.right)
        diameter = max(diameter, left + right)   # path through this node (edges)
        return 1 + max(left, right)              # height back to parent

    height(root)
    return diameter
```

`height` leaves se `1` return karta (ya `None` se `0`), aur jaise-jaise upar jaata hai, har node pe `left + right` edges wala path consider karta hai. Final answer global `diameter` me hota hai.

## Complexity

- **Time:** O(n) — single DFS, har node ek baar. (Naive "recompute height" approach O(n²) hota.)
- **Space:** O(h) recursion stack, h = height. Worst case (skewed) O(n).

## Common Pitfalls

- **Diameter = height(root) maan lena** — galat. Longest path root se guzarna zaroori nahi.
- **Edges vs nodes** — yeh problem **edges** count karti hai. `left + right` heights jodo (nodes count nahi). Agar nodes chahiye hote to `+1` lagta.
- **O(n²) trap** — har node pe `height()` ko separately call karna har baar re-traverse karta. Ek hi DFS me height return karo aur diameter ko side me track karo.
- **`nonlocal` bhulna** (Python) — andar wali function se bahar ki `diameter` update karne ke liye `nonlocal` chahiye, warna naya local ban jaata.
- **Return value confusion** — recursion `height` return karta hai, but function `diameter` return karta hai. Inhe mix mat karo.

## When to Use This Pattern

Jab node pe **do cheezein chahiye** — ek "parent ko kya return karun" aur doosri "global best update karun" — to **DFS with a global accumulator** pattern lagao. Max-path-sum, longest-univalue-path, balanced-tree-check — sab isi shape ke hain: recursion ek value return karta, aur ek side-channel se global answer build hota.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough showing heights bubbling up and the diameter updating at each node.

## NeetCode Link

https://neetcode.io/problems/binary-tree-diameter
