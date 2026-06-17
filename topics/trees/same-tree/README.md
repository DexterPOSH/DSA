# Same Tree

**Category:** Trees
**Difficulty:** easy

## Problem Statement

Given the roots of two binary trees `p` and `q`, return `True` if they are **structurally identical AND have the same node values** at every position.

```
   1        1
  / \      / \         ->  True   (same shape, same values)
 2   3    2   3

   1        1
  /          \         ->  False  (2 is left in one, right in the other)
 2            2
```

## Real-World Analogy

Socho do logon ke paas **same blueprint hone ka claim hai do buildings ka**. Tum kaise verify karoge? Dono ke main gate pe khade ho jao: kya dono buildings hain (ya dono khali plot)? Agar ek building aur doosra khali plot — alag, done. Dono building hain to kya unka naam/number same hai? Phir bolo "left wing andar jao" — wahan bhi same check, aur "right wing andar jao" — wahan bhi. Jab tak har corresponding kamra exactly match na ho, blueprint same nahi. Ek bhi mismatch (ek jagah room hai, doosri jagah nahi, ya value alag) → poora "not same".

## Approach

**Recursive DFS, dono trees ko ek saath chalao (lockstep).** Har step pe `p` aur `q` ke corresponding nodes compare:

1. **Dono `None`** → yahan tak same, `True` return.
2. **Ek `None`, doosra nahi** (ya values alag) → structure/value mismatch, `False`.
3. **Dono present aur value same** → left subtrees same AND right subtrees same (recurse dono pe).

```python
def is_same_tree(p, q):
    if not p and not q:
        return True              # dono khatam -> match
    if not p or not q or p.val != q.val:
        return False             # ek missing ya values mismatch
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)
```

`and` short-circuit karta hai — left side mismatch mila to right check hi nahi hoga, turant `False`. Iterative version me ek queue/stack me `(p_node, q_node)` pairs rakho aur same teen checks lagao.

## Complexity

- **Time:** O(n) — n = min(nodes in p, nodes in q); mismatch pe pehle hi ruk jaate hain. Worst case dono identical → O(n) full traversal.
- **Space:** O(h) recursion stack, h = height. Worst case (skewed) O(n).

## Common Pitfalls

- **`None` cases galat order me** — pehle "dono None?" check karo, phir "ek None?". Ulta karoge to logic gal jaati.
- **Sirf values compare karna, structure nahi** — `p.left` aur `q.left` dono ka existence match hona chahiye, na sirf value.
- **`or` vs `and` galti** — return me `and` chahiye (dono subtrees same hone chahiye). `or` likha to ek subtree match karne se `True` aa jaata — galat.
- **Value comparison bhulna** — `p.val != q.val` check zaroori; sirf structure same hone se kaam nahi.
- **Mirror se confuse karna** — same tree me `left<->left`, `right<->right` compare hota; symmetric/mirror problem me `left<->right` hota. Mix mat karo.

## When to Use This Pattern

"Do trees (ya do structures) ko ek saath traverse karke compare karo" → **simultaneous/lockstep DFS**. Yeh same-tree, symmetric-tree, subtree-of-another-tree, aur merge-two-trees jaise problems ka core hai: dono pe ek saath chalo, har corresponding pair pe decision lo, recurse on matching children.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough comparing both trees node-by-node in lockstep.

## NeetCode Link

https://neetcode.io/problems/same-binary-tree
