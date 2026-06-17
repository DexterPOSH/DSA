# Binary Tree Level Order Traversal

**Category:** Trees
**Difficulty:** medium

## Problem Statement

Given the root of a binary tree, return its **level order traversal** — the node values grouped **level by level**, from left to right, top to bottom. Output is a list of lists, one inner list per depth level.

```
        3
       / \
      9   20
         /  \
        15   7

binary-tree-level-order-traversal(root)  ->  [[3], [9, 20], [15, 7]]
```

## Real-World Analogy

Socho ek building me **floor-by-floor** announcement karni hai. Tum ground floor (root) se start karte ho, uske saare logon ko bulate ho, phir unke jo bachche pehli floor pe hain unko ek **line (queue)** me lagate jaate ho. Jab ek floor poora ho jaata hai, tum agli floor pe jaate ho — usi order me jaise wo queue me aaye the (left-se-right). Tum kabhi neeche utar ke beech me se kisi ko nahi bulate; ek poora floor khatam, tabhi agla. Yahi **BFS** hai — ek queue, level dar level.

## Approach

**BFS with a queue**, aur har iteration me **current level ka size pehle se snapshot** le lo — taaki ek baar me bilkul utne hi nodes process karo jitne us level pe hain.

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    res, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):     # snapshot: exactly this level's nodes
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        res.append(level)
    return res
```

`len(q)` ko loop ke shuru me freeze karna **key trick** hai — loop ke andar `q` me agli level ke bachche add ho rahe hain, but hum sirf utne hi pop karte hain jitne is level ke the.

Pattern: **BFS level-by-level**. Queue me FIFO order automatically left-to-right maintain karta hai.

## Complexity

- **Time:** O(n) — har node exactly ek baar enqueue aur ek baar dequeue hota hai.
- **Space:** O(n) — worst case queue me ek poori level ho sakti hai; complete tree ki sabse neeche wali level me ~n/2 nodes hote hain.

## Common Pitfalls

- **`len(q)` ko loop ke andar inline use karna** — agar `for _ in range(len(q))` ki jagah baar-baar `while len(q)` jaisa kuch likha jisme size live update hota hai, to levels aapas me mix ho jaayenge. Size pehle snapshot karo.
- **Empty root handle na karna** — `root = None` pe `[]` return karo, warna `deque([None])` me crash/galat output.
- **`list` ko queue ki tarah use karna** — `list.pop(0)` O(n) hai; `collections.deque` ka `popleft()` O(1). Bade trees pe ye matter karta hai.
- **Null children enqueue kar dena** — sirf existing `left`/`right` push karo, warna queue me `None` aa ke `.val` pe crash karega.

## When to Use This Pattern

Jab tree/graph me "level", "depth", "shortest path (unweighted)", ya "har layer pe kuch karo" dikhe → **BFS with a queue**. Cousins: Right Side View, Average of Levels, Zigzag Traversal, Min Depth. Cue: "process by layers / nearest-first" → queue + per-level size snapshot.

## NeetCode Link

https://neetcode.io/problems/level-order-traversal-of-binary-tree
