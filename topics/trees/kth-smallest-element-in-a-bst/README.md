# Kth Smallest Element in a BST

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Given the `root` of a binary search tree and an integer `k`, return the **kth smallest** value (1-indexed) among all nodes.

```
        5
       / \
      3   6        k = 3   ->  4
     / \
    2   4
   /
  1

  inorder = [1, 2, 3, 4, 5, 6]  ->  3rd smallest = 4
```

## Real-World Analogy

Socho ek **library** hai jaha books ek BST ki tarah arranged hain — har shelf ke left me chhote call-numbers, right me bade. Tumhe "3rd smallest book" chahiye. Tum sabse left wali deepest book se shuru karte ho (smallest), phir agla, phir agla… ek-ek karke ginte jaate ho. Jaise hi count `k` pe pahunchta hai, wahi tumhari answer book hai. Yeh left → root → right wala disciplined walk hi **inorder traversal** hai, jo BST ko **sorted order** me deta hai.

## Approach

**Key fact:** BST ka **inorder traversal** (left → node → right) values ko **ascending sorted order** me visit karta hai. To kth smallest = inorder me kth visited node.

Poori sorted list banane ki zaroorat nahi — bas **count karte jao aur k pe ruk jao**.

```python
def kth_smallest(root, k):
    stack = []
    cur = root
    while stack or cur:
        while cur:                  # left ki deepest tak jao
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()           # smallest unvisited node
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right             # ab uske right subtree me jao
```

Pattern: **iterative inorder traversal with a stack** + early exit. Recursive bhi chalega (ek counter rakho, k==0 pe answer capture karo), par iterative me jaldi ruk sakte ho without unwinding poori recursion.

## Complexity

- **Time:** O(h + k) — pehle leftmost tak utarne me h steps, phir k nodes pop. Worst case O(n) jab k = n ya tree skewed.
- **Space:** O(h) — stack me ek time pe ek root-to-node path hi hota hai. Balanced me O(log n).

## Common Pitfalls

- **Poora inorder array bana ke fir indexing** — kaam karta hai par O(n) space aur jaldi ruk nahi sakte. `k` pe stop karna efficient hai.
- **1-indexed vs 0-indexed** — k 1-based hai. `k -= 1` pehle, fir `k == 0` check — yeh kth node ko exactly pakadta hai.
- **`cur = cur.right` bhulna** — pop ke baad right subtree me na gaye to traversal galat ho jaata.
- **Follow-up: frequent inserts/deletes** — agar tree baar-baar modify hota aur k baar-baar puchha jaata, to har node me **subtree size** store karo; tab kth O(h) me mil jaata bina full inorder ke.

## When to Use This Pattern

Jab BST me **order-statistics** chahiye ("kth smallest/largest", "median", "rank of a value", "count in range") → socho **inorder traversal = sorted sequence**. Cue: "BST + sorted/ordered/kth" → left-root-right walk.

## Visual

Open [visual.html](visual.html) for an interactive inorder walk that counts down to the kth node.

## NeetCode Link

https://neetcode.io/problems/kth-smallest-integer-in-a-bst
