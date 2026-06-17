# Network Delay Time

**Category:** Advanced Graphs
**Difficulty:** medium

## Problem Statement

You're given a network of `n` nodes labelled `1..n` and a list of `times[i] = [u, v, w]` meaning a signal travels from `u` to `v` taking `w` time (a **directed, weighted** edge). A signal starts at node `k`. Return the **time it takes for all `n` nodes to receive the signal**, or `-1` if some node is unreachable.

The answer is the **maximum** of the shortest-path times from `k` to every other node.

```
times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
  ->  2     # 2->1 (1), 2->3 (1), 2->3->4 (2); max = 2
```

> Single-source shortest paths on a non-negative weighted directed graph → **Dijkstra**.

## Real-World Analogy

Socho node `k` se ek **afwah (rumor)** phailti hai. Har edge ek dost-ko-batane ka delay hai. Afwah hamesha sabse **tez raaste** se kisi tak pahunchti hai. Tum ek priority queue (min-heap) rakhte ho jisme "abhi tak ka sabse jaldi pahunchne wala node" upar rehta hai. Usse pop karo, uske dosto ko ( neighbours) thoda aur delay jod ke push karo. Jis node tak afwah pehli baar pahunchti hai, wahi uska shortest time hai — lock kar do.

Saare nodes tak afwah pahunchne me jitna time laga, uska **maximum** hi network delay hai (kyunki sabse aakhri banda jab sunta hai tabhi "sab" cover hue).

## Approach — Dijkstra with a min-heap

`dist` map me har node ka pehla (sabse chhota) arrival time store karo. Heap se sabse jaldi node nikaalo; agar pehli baar dekha to lock karo aur neighbours relax karo.

```python
import heapq
from collections import defaultdict

def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {}
    heap = [(0, k)]                      # (time_so_far, node)
    while heap:
        t, node = heapq.heappop(heap)
        if node in dist:
            continue                     # already locked with smaller t
        dist[node] = t
        for nei, w in graph[node]:
            if nei not in dist:
                heapq.heappush(heap, (t + w, nei))

    return max(dist.values()) if len(dist) == n else -1
```

Heap hamesha sabse chhota `t` upar deta hai, isliye jab ek node pehli baar pop hota hai to wahi uska shortest distance hai — usse dobara update karne ki zaroorat nahi.

## Complexity

- **Time:** O(E log V) — har edge ek push, heap pop log V. (E = edges, V = nodes.)
- **Space:** O(V + E) — graph + heap + dist.

## Common Pitfalls

- **`if node in dist: continue` bhulna** — heap me ek node ke multiple entries aate hain; without this skip you re-process and may overwrite with a larger time. Pehli pop hi minimum hai.
- **Negative weights** — Dijkstra negative edges pe galat answer deta. Tab Bellman-Ford chahiye. (Yahaan weights non-negative hain.)
- **Reachability check** — `len(dist) == n` warna agar koi node unreachable raha to `-1` return karna hai.
- **1-indexed nodes** — labels `1..n` hain; off-by-one se bacho.
- **Answer = max, sum nahi** — "all nodes receive" matlab sabse der wale ka time.

## When to Use This Pattern

"Shortest time/cost from one source to all nodes, **non-negative** weights" → **Dijkstra (min-heap)**. Cue: weighted graph, single source, "fastest/cheapest path", "kab tak sab tak pahunch jaayega". Negative weights dikhe to Bellman-Ford soch.

## NeetCode Link

https://neetcode.io/problems/network-delay-time
