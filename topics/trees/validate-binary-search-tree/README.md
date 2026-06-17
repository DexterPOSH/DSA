# Validate Binary Search Tree

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Given the `root` of a binary tree, determine whether it is a **valid binary search tree (BST)**. A valid BST means:

- Every node in the **left** subtree of a node is **strictly less** than the node.
- Every node in the **right** subtree is **strictly greater** than the node.
- Both subtrees are themselves valid BSTs.

The catch: it's the *whole subtree*, not just the immediate children.

```
        5
       / \
      1   7        ->  True
         / \
        6   8

        5
       / \
      1   7        ->  False   (4 is in 7's right subtree but 4 < 5)
         / \
        6   4
```

## Real-World Analogy

Socho ek **office building** hai jisme har floor pe ek room-number range allot hai. Reception (root) bolta hai: "mere left wing me jo bhi rooms hain, sab mere number se chhote, aur right wing me sab bade." Lekin yeh rule **transitive** hai — left wing ke andar ka koi bhi room, building ke top-level "max allowed" se bhi neeche hona chahiye, sirf apne immediate parent se nahi. Har node ke paas ek `(min, max)` allowed range hoti hai jo upar se neeche narrow hoti jaati hai. Koi room apni range se bahar nikla → building invalid.

## Approach

**Naive galti:** sirf `node.left < node < node.right` check karna. Yeh fail hota hai kyunki ek deep left-subtree ka node apne grandparent ka rule tod sakta hai (upar wala `4` dekho).

**Optimal — min/max bounds propagate karo:** har node ko ek valid range `(low, high)` me hona chahiye. Root ka range `(-∞, +∞)`. Jab left jaate ho, `high` ko current node value se replace kar do (left me sab chhote hone chahiye). Right jaate ho to `low` ko current node value se replace kar do.

```python
def is_valid_bst(root):
    def valid(node, low, high):
        if not node:
            return True                      # empty subtree -> always valid
        if not (low < node.val < high):      # strict bounds
            return False
        return (valid(node.left,  low, node.val) and
                valid(node.right, node.val, high))
    return valid(root, float('-inf'), float('inf'))
```

Pattern: **DFS with propagated bounds**. Alternatively, an **inorder traversal of a BST yields strictly increasing values** — so you can inorder-walk and check each value is greater than the previous one.

## Complexity

- **Time:** O(n) — har node exactly ek baar visit hota hai.
- **Space:** O(h) — recursion stack, h = tree height. Balanced me O(log n), skewed me O(n).

## Common Pitfalls

- **Sirf immediate children check karna** — sabse common bug. Range propagate karna zaroori hai, warna deep violation miss ho jaata.
- **`<=` vs `<`** — BST me values usually **strictly** increasing hoti hain. `low <= node.val` likha to duplicate-equal value galat pass kar jayega. Default: strict.
- **Integer overflow (C++/Java me)** — `-∞/+∞` ke liye `INT_MIN/INT_MAX` use kiya aur node ki value wahi nikli to bound fail karega. Python me `float('inf')` se yeh problem nahi, par interview me mention karo (use `long` ya nullable bounds).
- **Inorder approach me previous value reset karna bhulna** ya use `None` se compare na karna.

## When to Use This Pattern

Jab koi tree property check karni ho jo **subtree-wide constraint** ho (sirf local nahi) — "is this a valid BST", "range sum", "node within bounds" — to socho: **DFS me upar se context (min/max, path-sum, depth) neeche propagate karo**. Cue: "valid hai ya nahi, har node ko poore subtree ke against verify karna hai."

## Visual

Open [visual.html](visual.html) for an interactive DFS walkthrough showing the `(low, high)` window narrowing at each node.

## NeetCode Link

https://neetcode.io/problems/valid-binary-search-tree
