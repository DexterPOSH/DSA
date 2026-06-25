# Redundant Connection

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

You start with `n` nodes labelled `1..n` and a list of `edges`. The graph was a **tree** (n nodes, n-1 edges, no cycles) and then **exactly one extra edge** was added. Return that extra edge — the one that creates a cycle. If multiple answers exist, return the edge that appears **last** in the input.

```
edges = [[1,2], [1,3], [2,3]]   ->  [2,3]
# 1-2 and 1-3 are fine; adding 2-3 closes a cycle (1-2-3-1)
```

## Real-World Analogy

**What Azure Virtual Network is:** Azure Virtual Network (VNet) is Azure's private networking service for placing cloud workloads into subnets and connecting networks with peering, gateways, and routes. VNet peering links two VNets over Azure's backbone so resources can communicate privately. As peerings accumulate, the set of VNets and peering links forms a graph.

**What redundant VNet peering detection is, and why it's used:** A new peering is redundant for a tree-shaped topology if its two VNets are already connected through existing peerings. Detecting that matters when a team wants a controlled network graph with one managed path between segments, because an extra link creates a loop in the topology model and expands the paths traffic or dependencies may follow. The check should be done as links are added so the first edge that closes a cycle can be identified.

**The mapping:** Each node is an Azure VNet and each edge is a peering being added in order. Union-Find checks the root group of both endpoints before accepting the edge; different roots mean the peering connects two separate groups, while the same root means the two VNets were already connected. The key insight is that the redundant connection is exactly the first Azure peering whose endpoints already share a component root.


## Approach — Union-Find (Disjoint Set Union)

Ye classic **Union-Find** problem hai. Har edge ko ek-ek karke process karo:

1. `find(x)` — node `x` ka root mukhiya nikalo (path compression ke saath taaki agli baar fast ho).
2. Har edge `(u, v)` pe: agar `find(u) == find(v)` → dono pehle se same component me hain → **ye edge cycle banata hai → return it**.
3. Warna `union(u, v)` — dono components ko merge kar do.

Kyunki hum edges ko input order me process karte hain aur pehla cycle-banane wala edge return karte hain, wahi automatically "last in input" wala redundant edge hota hai (tree + 1 extra edge me sirf ek hi cycle hota hai).

```python
def find_redundant_connection(edges):
    parent = list(range(len(edges) + 1))   # 1-indexed; parent[i] = i

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path compression
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:                # already connected -> this edge closes a cycle
            return [u, v]
        parent[ru] = rv             # union
    return []
```

> **Union by rank** bhi add kar sakte ho (chhota tree bade ke neeche), but path compression akela hi practically kaafi fast hai is problem ke liye.

## Complexity

- **Time:** O(n · α(n)) ≈ **O(n)** — `α` inverse-Ackermann hai, effectively constant. Har edge pe do `find` + ek `union`.
- **Space:** O(n) — `parent` array.

## Common Pitfalls

- **1-indexing bhulna** — nodes `1..n` hain, isliye `parent` array ka size `n+1` rakho warna index error.
- **Path compression na karna** — kaam to karega, but bade inputs pe `find` slow ho jaata (skewed chain).
- **Cycle detect karne ke baad bhi union karte rehna** — jaise hi `find(u)==find(v)` mile, **turant return** karo; aage mat badho.
- **BFS/DFS se cycle dhoondhne ki koshish** — ho sakta hai, but har edge ke liye fresh traversal O(n²) ho jaata. Union-Find isi ke liye bana hai.
- **DSU ko directed graph maan lena** — yahan graph undirected hai; `union(u,v)` aur `union(v,u)` same baat.

## When to Use This Pattern

Jab bhi "dynamically edges add ho rahe hain aur poochna hai kya ye nodes already connected hain / kya cycle banega" — **Union-Find** socho. Cues: *connected components count*, *cycle detection in undirected graph*, *"are these two in the same group?"*, *Kruskal's MST*. Agar graph static ho aur ek hi baar traverse karna ho to DFS/BFS bhi chalega, but incremental merging me DSU king hai.

## Practice

- Visual: open `topics/graphs/redundant-connection/visual.html`

## NeetCode Link

https://neetcode.io/problems/redundant-connection
