# Rotting Oranges

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

You're given an `m x n` grid where each cell is one of:

- `0` — empty cell
- `1` — a fresh orange
- `2` — a rotten orange

Every minute, any fresh orange that is **4-directionally adjacent** (up/down/left/right) to a rotten orange becomes rotten. Return the **minimum number of minutes** until no fresh orange remains. If some fresh orange can never rot, return `-1`.

```
[[2,1,1],
 [1,1,0],
 [0,1,1]]   ->  4

[[2,1,1],
 [0,1,1],
 [1,0,1]]   ->  -1   # the bottom-left orange is unreachable
```

## Real-World Analogy

**What Azure availability-zone and scale-set architecture is:** Azure availability-zone and Virtual Machine Scale Set architecture combines physically separate datacenter zones with groups of identical VM instances for scalable workloads. During an Azure incident, unhealthy zones, instances, or dependent services can affect nearby nodes through traffic, dependencies, or shared infrastructure. The important detail is that there may be many unhealthy sources at the same time.

**What multi-source incident propagation is, and why it's used:** Multi-source propagation models the blast radius from all initial Azure failures simultaneously instead of pretending there is only one starting point. It is used to estimate time-to-impact: after one minute, every healthy node one hop away from any current failure is affected; after two minutes, the next layer is affected. Processing all current failures together prevents one source from unfairly getting a head start over another.

**The mapping:** Rotten oranges are initially unhealthy Azure zones or scale-set nodes, fresh oranges are still-healthy nodes, and empty cells are missing or unreachable space. Multi-source BFS seeds every unhealthy node at minute `0`, expands level by level to adjacent healthy nodes, and the last BFS layer gives the total minutes. The key insight is that time equals BFS depth from the nearest initial failure, and any fresh node never reached is isolated from the incident wave.


## Approach

Yeh classic **multi-source BFS** hai. Key insight: saare rotten oranges ko BFS queue me **ek hi baar me** daal do (level 0). Phir BFS ko level-by-level chalao — har level ek minute represent karta hai.

**Steps:**
1. Pehle ek pass me: saare rotten oranges (`2`) ko queue me daalo, aur `fresh` count karo (kitne `1` hain).
2. BFS chalao. Har minute (level) pe queue me jo abhi hai, sab ko pop karo, unke fresh neighbours ko rot karo (`1 -> 2`), queue me push karo, `fresh -= 1`.
3. Jab ek poora level process ho jaaye aur usme koi naya orange rot hua ho, `minutes += 1`.
4. End me agar `fresh == 0` → return `minutes`, warna `-1` (kuch oranges trapped reh gaye).

```python
from collections import deque

def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c))      # multi-source: all rotten seeded
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    while q and fresh > 0:
        for _ in range(len(q)):       # process exactly one "minute" of oranges
            r, c = q.popleft()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2  # rot it
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1                  # one wave done = one minute passed

    return minutes if fresh == 0 else -1
```

> **Why snapshot `len(q)` at the start of the loop?** Bilkul level-order traversal jaisa — us minute ke oranges utne hi process karne hain. Loop ke andar jo naye push hote hain, wo **agle** minute ke hain.

## Complexity

- **Time:** O(m·n) — har cell ek baar enqueue/visit hota hai, aur dirs constant (4).
- **Space:** O(m·n) — worst case queue me poora grid (saare rotten) ho sakta hai.

## Common Pitfalls

1. **`fresh == 0` from the start** (no fresh oranges at all) → answer is `0`, not `-1`. The `while q and fresh > 0` guard handles this — loop never runs, `minutes` stays 0.
2. **`minutes += 1` ko level loop ke andar daal dena** → har orange ke liye count badhega, galat. Increment poore level ke baad hota hai.
3. **Single-source BFS** chalana (ek hi rotten se shuru) → galat, kyunki sab simultaneously spread karte hain. **Seed all sources first.**
4. **Off-by-one minute** — agar `fresh > 0` guard nahi lagaya to ek extra empty wave count ho sakta. Guard se last wasted minute avoid hota.
5. **Unreachable fresh oranges** check karna bhulna → end me `fresh > 0` ka matlab `-1`.

## When to Use This Pattern

Jab dikhe **"spread / infection / shortest time from multiple starting points simultaneously"** — multi-source BFS socho. Cue: ek grid/graph jisme kayi sources ek saath wave-by-wave fail-ate hain, aur tumhe **minimum steps/time to cover everything** chahiye. Cousins: Walls and Gates, 01-matrix (nearest 0), fire/flood spread, "shortest distance from any of k sources." Trick same: saare sources ko level 0 me seed karo, fir normal BFS.

## Practice

- Visual: open `topics/graphs/rotting-oranges/visual.html`

## NeetCode Link

https://neetcode.io/problems/rotting-fruit
