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

Socho ek **mobile hanging sculpture** (chhat se latki hui, dono taraf weights). Balanced tabhi rahega jab har joint pe dono taraf ki "lambai" lagभग barabar ho — koi ek taraf bahut zyada lamba latak gaya to poora tedha ho jaata. Important baat: sirf top joint dekh kar nahi keh sakte balanced hai ya nahi — **har joint** pe check karna padta hai. Ek bhi joint imbalanced (ek side 2+ level zyada gehri) to poori sculpture "unbalanced". Aur jaise sculpture ko neeche se assemble karte ho, waise hi hum neeche se heights compute karke upar check karte jaate hain.

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
