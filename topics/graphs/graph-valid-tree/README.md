# Graph Valid Tree

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

Given `n` nodes labelled `0..n-1` and a list of undirected `edges`, return `True` if these edges form a **valid tree**.

A graph is a valid tree iff **both** hold:
1. It is **fully connected** — every node reachable (exactly one component).
2. It has **no cycles**.

```
n = 5, edges = [[0,1], [0,2], [0,3], [1,4]]   ->  True    # connected, no cycle
n = 5, edges = [[0,1], [1,2], [2,3], [1,3], [1,4]]  ->  False   # 1-2-3-1 cycle
n = 4, edges = [[0,1], [2,3]]   ->  False   # no cycle, but two components (disconnected)
```

## Real-World Analogy

**What Azure Virtual Network is:** Azure Virtual Network (VNet) is Azure's private network container for subnets, IP ranges, gateways, and connected workloads. VNets can be linked with VNet peering so resources in separate networks communicate over Azure's backbone. Looking at all VNets and peerings together gives you a topology graph.

**What VNet peering topology validation is, and why it's used:** A tree-shaped peering topology means every VNet is reachable, but there is exactly one simple path between any two VNets. Teams may enforce that shape for labs, controlled landing zones, or simplified governance because it rules out isolated VNets and redundant loops. The validation checks both requirements: `n - 1` peering links for `n` VNets, and no link that connects two VNets already connected through another path.

**The mapping:** Each graph node is an Azure VNet and each edge is a peering link. Union-Find processes peerings one by one: if two endpoints already share a root, adding that peering would create a cycle; otherwise it merges their components. The key insight is that a valid tree is exactly connected plus acyclic, and the `n - 1` edge count lets those two properties meet in one clean test.


## Approach — Union-Find (cycle + connectivity in one pass)

Dono conditions ek hi Union-Find pass me check ho jaati hain:

1. **Edge-count shortcut:** agar `len(edges) != n - 1` → turant `False`. (n-1 edges tree ke liye necessary hai.)
2. Har edge `(u, v)` pe `find`: agar `find(u) == find(v)` → dono already connected → **cycle mila → False**.
3. Warna `union`.
4. Loop ke baad: agar shortcut pass ho gaya tha (`edges == n-1`) **aur** koi cycle nahi mila, to graph automatically fully connected bhi hai → `True`.

```python
def valid_tree(n, edges):
    if len(edges) != n - 1:        # tree must have exactly n-1 edges
        return False
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path compression
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:               # cycle -> not a tree
            return False
        parent[ru] = rv            # union
    return True
```

> **Why the count check makes connectivity free:** `n` nodes with exactly `n-1` edges and **no cycle** is *forced* to be connected — har union ne `count` ko 1 ghatāya, aur `n-1` successful unions `n` components ko `1` me le aate hain. So no separate connectivity scan needed.

> **DFS/BFS alternative:** adjacency list banao, node `0` se traverse karo tracking visited + parent. Agar koi already-visited non-parent node mile → cycle. End me agar `len(visited) != n` → disconnected. Bhi O(V+E).

## Complexity

- **Time:** O(E · α(n)) ≈ **O(n)** — `E = n-1` after the shortcut. (DFS version O(V+E).)
- **Space:** O(n) — `parent` array. (DFS version O(V+E) adjacency + recursion.)

## Common Pitfalls

- **Edge-count check bhulna** — without it you'd need a separate connectivity check at the end (count components == 1). Saath me rakho.
- **Sirf cycle check karna, connectivity nahi** — `[[0,1],[2,3]]` me koi cycle nahi but ye tree nahi (2 components). Edge-count shortcut isse pakad leta hai.
- **Self-loop / duplicate edges** — `[0,0]` ya `[1,2]` do baar → cycle. `find(u)==find(v)` ye handle kar leta (duplicate me dusri baar same root milega).
- **0-indexed nodes** — `parent = list(range(n))`.
- **DFS me parent track na karna** → undirected edge ko hi "back edge" samajh ke false cycle report kar doge.

## When to Use This Pattern

"Kya ye graph ek tree hai" / "connected + acyclic verify karo" / "exactly one path between every pair of nodes" → **Union-Find** (cycle + connectivity) ya DFS. Cue words: *valid tree*, *spanning*, *acyclic connected*. Yahi DSU machinery Redundant Connection aur Number of Connected Components me bhi chalti hai — teeno ek family.

## Practice

- Visual: open `topics/graphs/graph-valid-tree/visual.html`

## NeetCode Link

https://neetcode.io/problems/valid-tree
