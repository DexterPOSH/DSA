# Clone Graph

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

Given a reference to a node in a **connected undirected graph**, return a **deep copy** (clone) of the graph. Each node has a value and a list of its neighbors:

```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors or []
```

```
Input:  1 — 2
        |   |
        4 — 3
Output: a brand-new graph with the same shape, zero shared node objects.
```

## Real-World Analogy

**What Azure Virtual Network is:** Azure Virtual Network (VNet) is Azure's private networking boundary for cloud resources, where subnets, NICs, VMs, private endpoints, gateways, and peering relationships define how traffic can move. A real Azure environment is not just a flat list of resources; it is a topology of objects that point to and depend on each other. When teams copy an environment for testing, disaster recovery, or migration, they need the same shape without reusing the original production objects.

**What topology cloning is, and why it's used:** Cloning a VNet topology means creating brand-new resource definitions while recreating every relationship: subnet membership, NIC-to-VM links, route associations, and VNet peerings. It exists because a shallow copy would leave the new environment pointing back to the old one, while blindly walking relationships can duplicate shared resources or loop forever through bidirectional peerings. The safe pattern is to keep a translation map from each original Azure resource to its cloned resource as soon as the clone is created.

**The mapping:** In Clone Graph, each node is an Azure resource and each neighbor edge is a networking or dependency link. DFS/BFS creates the cloned node, stores it in the map, then walks neighbors and connects to their clones; if a neighbor is already mapped, reuse that clone instead of recursing again. The key insight is that the visited map is both cycle protection and the original-to-copy wiring diagram, so the clone has the same topology with entirely new nodes.


## Approach

Pattern: **graph traversal (DFS/BFS) + hash map memoization** to handle cycles and avoid duplicate clones.

`old_to_new` dictionary banao jo original node ko uske clone se map kare. DFS karo: node pe aao → agar already cloned hai to wahi return karo; warna naya node banao, map me daalo, fir uske saare neighbors ko recursively clone karke naye node ke neighbors me jodo.

```python
def clone_graph(node):
    if not node:
        return None
    old_to_new = {}

    def dfs(cur):
        if cur in old_to_new:
            return old_to_new[cur]          # already cloned -> reuse (breaks cycles)
        copy = Node(cur.val)
        old_to_new[cur] = copy              # register BEFORE recursing
        for nei in cur.neighbors:
            copy.neighbors.append(dfs(nei))
        return copy

    return dfs(node)
```

> Critical ordering: clone ko map me **recurse karne se pehle** daalo. Agar baad me daaloge, to cycle wapas isi node pe aakar dobara naya clone bana dega → galat.

## Complexity

- **Time:** O(V + E) — har node ek baar clone hota hai, har edge ek baar traverse hota hai (neighbor list copy karte waqt).
- **Space:** O(V) — `old_to_new` map me V entries, plus DFS recursion stack O(V).

## Common Pitfalls

- **Map me daalne ka order galat** — clone create karte hi, neighbors recurse karne se *pehle* map me daalo. Warna cycle pe infinite recursion.
- **Map me clone ki jagah `True` daalna** — sirf "visited" mark karna kaafi nahi; tumhe actual clone object chahiye taaki neighbor links sahi naye nodes pe point karein.
- **Neighbors me original nodes jod dena** — clone ke neighbors me original `nei` nahi, `dfs(nei)` (yaani clone) jodna hai.
- **`node is None` edge case** — empty graph pe `None` return karo, crash mat.
- **Disconnected graph** — problem connected guarantee karta hai; sirf diya hua node se reachable part hi clone hota hai.

## When to Use This Pattern

Jab kisi linked structure (graph, doubly-linked list with random pointers) ka **deep copy with cycles** banana ho → traversal + "original → copy" hash map. Cue: "deep clone" + "cycles/shared references ho sakte hain" → memoize the mapping. Cousin: Copy List with Random Pointer.

## NeetCode Link

https://neetcode.io/problems/clone-graph
