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

**What Azure Cosmos DB is:** Azure Cosmos DB is Azure's globally distributed NoSQL database service for low-latency reads and writes at scale. To answer queries efficiently, it maintains indexes over item properties instead of scanning every document. For ordered comparisons, those indexes can behave like sorted key structures.

**What a range index cursor is, and why it's used:** A range index keeps values in an order that supports operations such as range filters and ordered scans. Rather than materializing every key first, a query engine can advance a cursor through the sorted index stream until it has enough results. This saves work when you only need the kth item or the first page of ordered data.

**The mapping:** A BST's inorder traversal is the Azure Cosmos DB range-index scan in miniature: visit left keys, then the current key, then right keys. Decrement `k` each time a value is emitted, and stop when `k` reaches zero. The key insight is that the BST invariant turns inorder traversal into sorted order, so the kth visit is the kth smallest value.

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
