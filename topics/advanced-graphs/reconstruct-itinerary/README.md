# Reconstruct Itinerary

**Category:** Advanced Graphs
**Difficulty:** hard

## Problem Statement

You're given a list of airline tickets `[from, to]`. Reconstruct the itinerary in order so that **all tickets are used exactly once** and the trip **starts at `"JFK"`**. If multiple valid itineraries exist, return the one with the **smallest lexical order** when read as a single string (i.e. prefer the alphabetically smaller next airport).

It is guaranteed that at least one valid itinerary exists.

```
tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]
  ->  ["JFK","MUC","LHR","SFO","SJC"]

tickets = [["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]]
  ->  ["JFK","ATL","JFK","SFO","ATL","SFO"]   # ATL before SFO (lexical)
```

> This is an **Eulerian path** problem: a path that uses every *edge* exactly once. The trick is **Hierholzer's algorithm**.

## Real-World Analogy

**What Azure Network Watcher is:** Azure Network Watcher is Azure's network monitoring and troubleshooting service. It helps operators inspect topology, test connectivity, capture packets, analyze NSG flow logs, and understand next-hop behavior for Azure virtual networks. In practice, it is the tool you reach for when you need a clear, auditable view of how network resources are connected.

**What topology link auditing is, and why it's used:** When auditing VNet peerings or ExpressRoute circuit connections, every link should be checked exactly once so the report does not miss a connection or double-count one. A deterministic traversal order makes the audit reproducible; if several outbound links are available, choosing the alphabetically smallest region/name first is like a stable tie-breaker. The mechanism exists to turn many local links into one complete inspection trail.

**The mapping:** Airports are Azure hubs or regions, tickets are directed peering/circuit links, and the per-node min-heap stores the next unused link in lexical order. Hierholzer's DFS consumes outbound links until a hub has none left, then appends that dead-end during backtracking because it belongs near the end of the final audit trail. Reversing the post-order list gives one continuous route that uses every Azure network link exactly once; the key insight is that this is an edge-usage problem, not a node-visit problem.

## Approach — Hierholzer's algorithm (post-order DFS)

Pehle har airport ke liye uske destinations ko ek **min-heap** (ya sorted list) me rakho, taaki hum hamesha lexically smallest next airport pehle try karein. Phir DFS:

1. Current airport se sabse chhota available destination uthao (heap se pop).
2. Us edge ko "use" kar diya — recurse into that destination.
3. Jab kisi node ke saare outgoing tickets khatam ho jaayein (dead end), use **result me append** karo.
4. End me result ko **reverse** karo.

```python
from collections import defaultdict
import heapq

def find_itinerary(tickets):
    graph = defaultdict(list)
    for src, dst in tickets:
        heapq.heappush(graph[src], dst)   # min-heap per airport

    route = []
    def dfs(airport):
        while graph[airport]:
            nxt = heapq.heappop(graph[airport])  # smallest unused edge
            dfs(nxt)
        route.append(airport)                    # post-order: dead-end first

    dfs("JFK")
    return route[::-1]                            # reverse for final order
```

Why post-order + reverse? Agar tum pre-order me likho, to tum lexically chhote raaste me ghus ke phans sakte ho aur kuch tickets chhoot jaayengi. Post-order guarantee karta hai ki dead-end node hamesha route ke **baad** wale hisse me jaaye — reverse karne pe sab sahi jagah aa jaata hai.

## Complexity

- **Time:** O(E log E) — har edge ek baar process hoti hai; heap push/pop pe log factor (E = number of tickets).
- **Space:** O(E) — graph adjacency + recursion stack + result.

## Common Pitfalls

- **Lexical order bhulna** — agar plain dict-of-lists use karo bina sort/heap ke, to "smallest" itinerary guarantee nahi hota.
- **Pre-order me append karna** — classic bug. Greedy "chhota pehle" pre-order me ek wrong dead-end pe phasa deta hai jahaan abhi tickets bachi hain. Post-order + reverse hi sahi hai.
- **Heap pop ko peeche reverse na karna** — heap se already smallest nikalta hai; final `route` ko bhi reverse karna mat bhoolo.
- **Iterative version chahiye** to explicit stack use karo (deep recursion stack overflow se bachne ke liye on huge inputs).

## When to Use This Pattern

"Use every **edge** exactly once" / "traverse every road once and return a single trail" → **Eulerian path → Hierholzer's algorithm**. Cue: tickets/edges ko consume karna hai (nodes nahi), aur ek single continuous path chahiye. Agar "every **node** once" hota to wo Hamiltonian/DFS hota.

## NeetCode Link

https://neetcode.io/problems/reconstruct-flight-path
