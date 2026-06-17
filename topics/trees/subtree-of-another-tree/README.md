# Subtree of Another Tree

**Category:** Trees
**Difficulty:** easy

## Problem Statement

Given the roots of two binary trees `root` and `subRoot`, return `True` if there is a subtree of `root` with the **same structure and node values** as `subRoot`, and `False` otherwise. A subtree of `root` is a node in `root` **plus all of its descendants** — you can't match a partial slice in the middle of a tree.

```
root =                subRoot =
      3                    4
     / \                  / \
    4   5                1   2
   / \
  1   2

subtree-of-another-tree(root, subRoot)  ->  True   # the left child (4,1,2) matches exactly

root =                subRoot =
      3                    4
     / \                  / \
    4   5                1   2
   / \                          \
  1   2                          0   <- extra node

result  ->  False  # structure differs, the 0 has no counterpart
```

## Real-World Analogy

Socho tumhare paas ek bada **family tree** hai aur ek chhota family tree — kisi cousin ka. Tum check karna chahte ho ki kya wo chhota tree, bade tree me **exactly waise hi** kahin baitha hai: same log, same parent-child rishta, bilkul wahi shape. Tum bade tree ke har person pe rukte ho aur poochte ho: "agar main yahin se neeche poora dekhun, to kya yeh hu-ba-hu wahi chhota tree banta hai?" Agar kisi ek bhi jagah perfect match mil gaya — done. Bas dhyaan rakhna: match ka matlab hai **us node se neeche ka poora peड़**, beech me se aadha-adhura nahi.

## Approach

Do cheezein chahiye: (1) "in dono trees ka shape + values bilkul same hai?" check karne wala helper `sameTree`, aur (2) `root` ke har node pe ye check chalana.

**Helper — `sameTree(a, b)`:** dono `None` → `True`. Ek `None` doosra nahi → `False`. Values alag → `False`. Warna left subtrees same **aur** right subtrees same.

```python
def is_subtree(root, sub_root):
    def same(a, b):
        if not a and not b:
            return True
        if not a or not b or a.val != b.val:
            return False
        return same(a.left, b.left) and same(a.right, b.right)

    if not sub_root:        # empty tree is a subtree of everything
        return True
    if not root:            # ran out of nodes, sub_root non-empty
        return False
    if same(root, sub_root):
        return True
    return is_subtree(root.left, sub_root) or is_subtree(root.right, sub_root)
```

Pattern: **DFS traversal + per-node same-tree comparison**. Har candidate node pe ek poora `same` check — isliye nested traversal.

> **Optimization mention (follow-up):** har subtree ko ek serialized string (e.g. preorder with `#` for nulls) me badal do, phir "kya `subRoot` ka string, `root` ke string ka substring hai?" — ek KMP/string-match me O(n + m). Yeh interviewer ko impress karta hai, but pehle clean recursive answer do.

## Complexity

- **Time:** O(n · m) — har node (n total) pe up to O(m) ka `same` comparison chal sakta hai, jahan m = `subRoot` ka size. Practically `same` jaldi-jaldi false return hota hai, but worst case yahi hai.
- **Space:** O(n) — recursion stack, skewed tree me tree ki height tak (worst case n).

## Common Pitfalls

- **`val` check ke pehle `None` checks bhulna** — agar pehle `a.val != b.val` likh diya aur `a` `None` hai, to crash. Hamesha pehle dono-null aur one-null handle karo.
- **"Same value mil gaya, done" maan lena** — sirf root value match karne se subtree match nahi hota; poora structure recurse karke verify karo.
- **Partial match accept karna** — subtree ka matlab node + **saare descendants**. `subRoot` ke leaf ke neeche `root` me extra nodes ho to bhi match nahi (`same` me one-null → False isse pakad leta hai).
- **Empty `subRoot` edge case** — convention se empty tree har tree ka subtree hai → `True` jaldi return.

## When to Use This Pattern

Jab "kya pattern-tree X bade-tree Y me kahin embedded hai (exact match)?" type sawaal aaye → **DFS over candidates + structural equality check**. Cousins: Same Tree, Symmetric Tree, Leaf-Similar Trees. Cue: "exact structural match somewhere" → har node ko ek possible starting point maano.

## NeetCode Link

https://neetcode.io/problems/subtree-of-a-binary-tree
