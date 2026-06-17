# Binary Tree Maximum Path Sum

**Category:** Trees
**Difficulty:** hard

## Problem Statement

A **path** in a binary tree is a sequence of nodes where each adjacent pair is connected by an edge. A node appears at most once, and the path **need not pass through the root**. Return the maximum **sum** of node values along any such path.

```
        -10
        /  \
       9    20
            / \
           15  7

  best path: 15 -> 20 -> 7  =  42
```

Note: a path can also be a single node, and it can "turn" at one node (go up the left child, through the node, down the right child).

## Real-World Analogy

Socho ek **trekking trail network** hai pahaadon me, jaha har point pe ek altitude-score (positive ya negative) hai. Tumhe ek aisa continuous trail chahiye jisme **total score maximum** ho. Har junction (node) pe do choice hai: us junction se **ek hi taraf** neeche jaake aage ek bade trail ka hissa ban-na (taaki parent tumhe use kar sake), **ya** us junction pe hi left aur right dono dips ko jod ke ek "peak path" complete kar dena. Negative-score wale detour ko skip karo — usse `0` maan lo, kyunki usme jaane ka koi faayda nahi. Best peak har junction pe yaad rakho.

## Approach

Har node pe do alag cheezein hoti hain:

1. **Gain a node can "pass up" to its parent:** node ki value + uske ek (sirf ek) child ki best downward gain. Parent isse ek straight line ke roop me use kar sakta hai.
2. **Best path that "peaks" at this node:** node.val + left gain + right gain — yeh path yahi turn karta hai, parent ke kaam ka nahi, par overall answer ka candidate hai.

Trick: **negative child-gain ko `0` se clamp** karo (`max(0, childGain)`) — negative branch lena nuksaan hai.

```python
def max_path_sum(root):
    best = float('-inf')

    def gain(node):
        nonlocal best
        if not node:
            return 0
        left  = max(gain(node.left),  0)   # negative -> skip (clamp to 0)
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)   # path peaking here
        return node.val + max(left, right)          # gain passed UP (one side)

    gain(root)
    return best
```

Pattern: **postorder DFS returning a "partial" value, updating a global "complete" answer.** The function returns one thing (upward gain) but tracks another (best full path) on the side.

## Complexity

- **Time:** O(n) — har node ek baar visit.
- **Space:** O(h) — recursion stack, h = height.

## Common Pitfalls

- **Return value aur global answer me confusion** — function `node.val + max(left, right)` return karta (ek side only), par `best` me `left + right` dono jodte. Inhe alag rakhna **the** key insight hai.
- **Negative ko clamp na karna** — `max(0, gain)` bhulne se negative subtrees answer kharab kar dete.
- **`best` ko 0 se initialize karna** — agar saare nodes negative ho (e.g. `[-3]`), answer `-3` hona chahiye, `0` nahi. `-inf` se start karo.
- **Returning `left + right` upar** — galat! Parent ek node se sirf ek straight line ho ke nikal sakta hai, dono branches lekar nahi.

## When to Use This Pattern

Jab tree me koi quantity chahiye jo **kisi bhi node pe turn kar sakti** ho (diameter, max path sum, longest univalue path) → socho: **DFS jo child se ek "straight" value return kare, par node pe "left+right" combine karke global best update kare**. Cue: "path/chain anywhere in the tree, not necessarily through root."

## Visual

Open [visual.html](visual.html) for an interactive postorder walkthrough showing upward-gain vs the best peaking-path at each node.

## NeetCode Link

https://neetcode.io/problems/binary-tree-maximum-path-sum
