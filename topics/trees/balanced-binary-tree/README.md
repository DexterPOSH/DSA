# Balanced Binary Tree

**Category:** Trees
**Difficulty:** easy

## Problem Statement

Given the `root` of a binary tree, return `True` if it is **height-balanced**. A tree is height-balanced jab **har node** ke left aur right subtree ki heights ka difference **at most 1** ho.

```
        3                          1
       / \                          \
      9   20      -> True            2     -> False
         /  \                         \
        15   7                         3   (right side 2 levels deeper than empty left)
```

## Real-World Analogy

**What Azure Resource Manager's management hierarchy is:** Azure Resource Manager (ARM) is Azure's control plane for creating, organizing, and governing cloud resources. Its scopes form a tree: tenant/root Management Group, child Management Groups, Subscriptions, Resource Groups, and finally Resources. That hierarchy lets governance decisions and rollups travel from children back to parents.

**What bottom-up health rollup is, and why it's used:** In a large Azure estate, a parent scope should not recompute every descendant from scratch when it only needs a compact summary like maximum depth, compliance state, or health. Each child can report a small result upward, and a special failure signal can stop unnecessary work once a bad branch is found. For a balance check, the useful summary is branch height; the failure signal is "this subtree is already unbalanced."

**The mapping:** The recursive function acts like an ARM scope rollup. Each node asks its left and right child scopes for their heights, returns `max(left, right) + 1` when they differ by at most one, and returns `-1` when the local scope is unbalanced. The key insight is that height and validity can be computed in the same postorder pass, with `-1` carrying the bad-news signal all the way to the root.

## Approach

Naive: har node pe `height(left)` aur `height(right)` nikalo, difference check karo, recurse — but yeh O(n²) (heights baar-baar recompute).

**Optimal (O(n)):** ek hi bottom-up DFS jo har node ke liye **height return** kare, lekin agar kahin imbalance mile to ek sentinel (`-1`) propagate kar de. `-1` milte hi short-circuit — neeche kahin unbalanced tha matlab poora tree unbalanced.

```python
def is_balanced(root):
    def height(node):
        if not node:
            return 0
        left = height(node.left)
        if left == -1:
            return -1                    # left subtree already unbalanced
        right = height(node.right)
        if right == -1:
            return -1                    # right subtree already unbalanced
        if abs(left - right) > 1:
            return -1                    # THIS node is unbalanced
        return 1 + max(left, right)      # balanced -> return real height

    return height(root) != -1
```

`-1` ko "balanced nahi hai" ka flag samjho. Jaise hi koi subtree ya node fail karta, `-1` upar tak chala jaata aur baaki kaam skip ho jaata.

## Complexity

- **Time:** O(n) — har node ek baar; height recursion ke andar hi reuse hoti hai (recompute nahi).
- **Space:** O(h) recursion stack, h = height. Worst case O(n).

## Common Pitfalls

- **O(n²) naive solution** — har node pe alag se `height()` call karna har baar subtree re-traverse karta. `-1` sentinel trick se ek hi pass me karo.
- **Sirf root pe check karna** — balanced ka matlab **har** node balanced ho. Recursion zaroori.
- **`abs()` bhulna** — `left - right > 1` likha to negative case (right gehra) miss ho jaata. `abs(left - right) > 1`.
- **`-1` ko height samajh lena** — jaise hi `-1` mile, short-circuit karo; usse `1 + max(...)` me mat ghuso warna garbage.
- **Off-by-one in diff** — difference `> 1` unbalanced; difference `== 1` ya `0` balanced.

## When to Use This Pattern

"Har node pe ek property satisfy honi chahiye, aur subtree ki computed value bhi chahiye" → **bottom-up DFS jisme ek special value (jaise `-1`) failure ka signal de**. Yeh "compute + validate in one pass with short-circuit" trick max-depth, diameter, aur BST-validation jaise problems me bhi kaam aata.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough showing heights computed bottom-up and the `-1` imbalance signal propagating.

## NeetCode Link

https://neetcode.io/problems/balanced-binary-tree
