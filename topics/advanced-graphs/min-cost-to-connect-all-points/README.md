# Min Cost to Connect All Points

**Category:** Advanced Graphs
**Difficulty:** medium

## Problem Statement

You're given `points` on a 2-D plane where `points[i] = [xi, yi]`. The cost to connect two points is the **Manhattan distance** `|xi - xj| + |yi - yj|`. Return the **minimum total cost** to connect **all points** such that there is exactly one path between any two points (i.e. build a **Minimum Spanning Tree**).

```
points = [[0,0],[2,2],[3,10],[5,2],[7,0]]
  ->  20
```

> Every pair of points is connectable — it's a **complete weighted graph** of N nodes. We want the cheapest subset of edges that keeps everyone connected with no cycles → **MST**.

## Real-World Analogy

**What Azure ExpressRoute and VNet peering are:** Azure ExpressRoute provides private connectivity between customer networks and Microsoft cloud services, while VNet peering connects Azure virtual networks over Microsoft's backbone. Together, they are common building blocks for a private Azure network that spans regions and workloads. Every circuit or peering link has cost and operational overhead, so you usually want enough connectivity to reach everyone without buying every possible connection.

**What minimum-spanning connectivity is, and why it's used:** A spanning-tree-style backbone connects all regions while avoiding cycles that do not make any new region reachable. Redundant paths may be useful for resilience in real Azure architecture, but if the problem's goal is minimum total cost with exactly one path between any two locations, a cycle is wasted spend. The mechanism exists to choose the cheapest set of links that still keeps the whole network connected.

**The mapping:** Each point is an Azure region or VNet, and the Manhattan distance is the estimated cost of an ExpressRoute or peering link between two locations. Prim's algorithm keeps a visited set for the already-built backbone, uses the min-heap as the list of candidate boundary links, and repeatedly adds the cheapest link to an unconnected point. Stale heap entries are ignored because that region was already connected more cheaply; the key insight is to grow the network by the cheapest safe edge, not by globally buying all cheap-looking edges.

## Approach — Prim's MST with a min-heap

Ek `visited` set rakho. Heap me `(cost, point_index)` daalo, JFK ki tarah point 0 se shuru. Har baar heap se **sabse sasta** edge nikaalo jo ek naye (unvisited) point tak jaata hai; usse add karo, total me cost jodo, aur uske saare neighbours ke edges heap me push karo.

```python
import heapq

def min_cost_connect_points(points):
    n = len(points)
    visited = set()
    heap = [(0, 0)]              # (cost, point_index), start at point 0
    total = 0

    while len(visited) < n:
        cost, i = heapq.heappop(heap)
        if i in visited:
            continue            # stale edge, skip
        visited.add(i)
        total += cost
        for j in range(n):
            if j not in visited:
                d = abs(points[i][0]-points[j][0]) + abs(points[i][1]-points[j][1])
                heapq.heappush(heap, (d, j))
    return total
```

Heap se nikalte waqt agar point already visited hai to skip — kyunki hum same point ke liye kai (cost) push kar chuke ho sakte hain; sabse sasta wala pehle niklega, baaki stale ho jaate hain.

## Complexity

- **Time:** O(N² log N) — har point ke liye saare N neighbours push karte hain (complete graph), heap operations log par. Dense graph me yeh standard hai.
- **Space:** O(N²) heap worst case (saare edges), O(N) visited.

> Kruskal + Union-Find bhi kaam karta (sort all N² edges → O(N² log N)). Dense complete graph pe Prim's usually cleaner.

## Common Pitfalls

- **`visited` check skip karna** — heap me ek hi point ke multiple stale entries hote hain; pop ke baad `if i in visited: continue` zaroori, warna cost double-count.
- **Manhattan distance galat** — `|dx| + |dy|`, Euclidean (`sqrt`) nahi.
- **Cost ko visit ke baad add karna** — start node ka cost 0 push karna sahi rahta hai; saare points visit hone tak loop chalao, `len(visited) < n` se.
- **Disconnected ka darr** — yahaan complete graph hai, hamesha connected; general MST me agar edges kam ho to MST exist hi na kare.

## When to Use This Pattern

"Connect all nodes with minimum total edge weight, no cycles" → **MST (Prim's ya Kruskal's)**. Cue: "minimum cost to link everything", "build cheapest network", "har do node ke beech ek hi path". Complete/dense graph → Prim's with heap; sparse with edge list → Kruskal + Union-Find.

## NeetCode Link

https://neetcode.io/problems/min-cost-to-connect-points
