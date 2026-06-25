# Number of Connected Components in an Undirected Graph

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

You have `n` nodes labelled `0..n-1` and a list of undirected `edges`. Return the number of **connected components** — groups of nodes where every node can reach every other node in its group (and is isolated from other groups).

```
n = 5, edges = [[0,1], [1,2], [3,4]]   ->  2
# component A: {0,1,2}, component B: {3,4}
```

```
n = 5, edges = [[0,1], [1,2], [2,3], [3,4]]   ->  1
# all chained together
```

## Real-World Analogy

**What Azure Resource Graph is:** Azure Resource Graph is Azure's service for querying resource inventory across subscriptions and management groups. It can surface VNets, subnets, NICs, peerings, and other resources that together form a connectivity graph. That graph is useful for spotting whether an environment is one connected topology or several disconnected groups.

**What Union-Find connectivity grouping is, and why it's used:** Connectivity grouping starts with every Azure resource as its own group, then merges groups whenever a network or dependency edge connects them. Union-Find is used because it answers “are these already in the same group?” quickly while processing many edges. This avoids repeatedly traversing the whole graph as each new peering or dependency relationship is discovered.

**The mapping:** Each node is an Azure resource and each undirected edge is a connection between two resources. For every edge, Union-Find compares the endpoints' roots; different roots mean two topology groups should merge, while the same root means the edge stays inside an existing group. The key insight is that the final number of roots is the number of disconnected Azure topology components.


## Approach — Union-Find with a component counter

Same Union-Find machinery, but ab hum **count** track karte hain:

1. `count = n` se shuru karo (sab alag).
2. Har edge `(u, v)` pe: agar `find(u) != find(v)` → do alag components mile → **union karo aur `count -= 1`**.
3. Agar `find(u) == find(v)` → already same component → kuch mat karo.
4. End me `count` return karo.

```python
def count_components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path compression
            x = parent[x]
        return x

    count = n
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv     # union two distinct components
            count -= 1          # one fewer component
    return count
```

> **Alternative — DFS/BFS:** adjacency list banao, har unvisited node se ek traversal chalao, har traversal = ek component, count++. Bhi O(V+E) hai aur theek hai. Union-Find tab better jab edges streaming aa rahe ho ya cycle-detection bhi chahiye.

## Complexity

- **Time:** O(E · α(n)) ≈ **O(E)** — har edge pe do `find` + maybe ek `union`. (DFS version O(V + E).)
- **Space:** O(n) — `parent` array. (DFS version O(V + E) for adjacency list + recursion.)

## Common Pitfalls

- **Counter ko galat jagah decrement karna** — `count -= 1` sirf tab jab `find(u) != find(v)` (real merge). Har edge pe blindly decrement karoge to galat answer.
- **0-indexed vs 1-indexed** — yahan nodes `0..n-1` hain (Redundant Connection 1-indexed tha). `parent = list(range(n))`.
- **Isolated nodes bhulna** — jin nodes pe koi edge nahi, wo apne aap ek-ek component hain. `count = n` se shuru karne se ye automatically handle ho jaata.
- **DFS me visited set na rakhna** → infinite loop on cycles, ya same component double-count.
- **Path compression skip karna** → kaam karega but worst-case slow.

## When to Use This Pattern

"Kitne separate groups / islands / clusters hain" ya "in dono nodes ka ek hi network hai kya" → **Union-Find** (ya DFS/BFS flood-fill). Cousins: Number of Islands, Friend Circles / Provinces, Accounts Merge, Graph Valid Tree. Cue: *grouping + connectivity*. Agar saath me cycle ya incremental edges bhi ho, DSU clearly jeet-ta hai.

## Practice

- Visual: open `topics/graphs/number-of-connected-components-in-an-undirected-graph/visual.html`

## NeetCode Link

https://neetcode.io/problems/count-connected-components
