# Swim in Rising Water

**Category:** Advanced Graphs
**Difficulty:** hard

## Problem Statement

You're given an `n x n` grid where `grid[i][j]` is the **elevation** at cell `(i, j)`. Rain starts and at time `t` the water level everywhere is `t`. You can swim from a cell to a 4-directionally adjacent cell **only if both cells have elevation ≤ t** (you swim instantly within reachable cells). Starting at `(0, 0)`, return the **least time `t`** at which you can reach `(n-1, n-1)`.

```
grid = [[0,2],[1,3]]            ->  3
grid = [[0,1,2,3,4],
        [24,23,22,21,5],
        [12,13,14,15,16],
        [11,17,18,19,20],
        [10,9,8,7,6]]          ->  16
```

> The answer is the path from start to end that **minimizes its maximum cell elevation** — a "minimax path". Dijkstra-style with `max` instead of `+` solves it (binary search + BFS is an alternative).

## Real-World Analogy

Socho tum ek baadh (flood) me phase ho aur ek door ke darwaze tak pahunchna hai. Har cell ki ek height hai; tum tabhi us cell me ja sakte ho jab paani us height tak chadh jaaye. Tum chahte ho **kam se kam waqt** me pahunchna — matlab aisa raasta jiska **sabse uncha cell jitna kam ho sake utna kam** ho.

Dijkstra ka twist: normal Dijkstra path ke edges ka **sum** minimize karta hai. Yahaan har cell ka "cost to be here" = us raaste pe ab tak ka **max elevation** hai. Min-heap se hamesha sabse kam "max-so-far" wala cell pop karo, uske neighbours ka naya max-so-far = `max(current, neighbour_height)` push karo. Jaise hi end cell pop hota hai — wahi answer.

## Approach — Dijkstra on "max along path" (minimax)

Heap me `(max_elevation_so_far, r, c)` rakho. Sabse kam max-so-far waala cell pop karo; agar wo end hai → answer mil gaya. Warna neighbours ke liye naya time = `max(current_time, grid[nr][nc])` push karo.

```python
import heapq

def swim_in_water(grid):
    n = len(grid)
    visited = set()
    heap = [(grid[0][0], 0, 0)]          # (time = max elev on path, r, c)

    while heap:
        t, r, c = heapq.heappop(heap)
        if (r, c) in visited:
            continue
        visited.add((r, c))
        if r == n-1 and c == n-1:
            return t                     # first time we reach end = answer
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited:
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
    return -1
```

**Alternative — binary search + BFS/DFS:** time `t` ko `0..n²-1` me binary search karo; har candidate `t` ke liye check karo kya start se end tak ek path hai jahaan sab cells `≤ t` (simple BFS). O(n² log n²). Conceptually clean, same answer.

## Complexity

- **Time:** O(n² log n) — har cell ek baar pop hota hai (n² cells), heap op log par.
- **Space:** O(n²) — heap + visited.

## Common Pitfalls

- **Sum vs max** — yeh shortest-*sum* path nahi hai; cost = path ke max elevation ka **maximum**. `+w` ki jagah `max(t, height)` use karo.
- **Start cell ka elevation** — initial time `grid[0][0]` se shuru, 0 se nahi (start cell me bhi tabhi ja sakte ho jab paani uski height tak ho).
- **`visited` skip bhulna** — same cell multiple times push hota hai; pehli pop minimum hai, baaki skip.
- **Binary search bounds** — `t` ki range `min cell .. max cell` (ya `0 .. n²-1` since elevations are a permutation).
- **End reach hote hi return** — Dijkstra guarantee deta ki pehli baar end pop hua = minimum.

## When to Use This Pattern

"Minimize the **maximum** edge/cell along a path" (minimax / bottleneck path) → **Dijkstra with `max` instead of `+`**, ya **binary-search-the-answer + reachability BFS**. Cue: "least time/height/cost such that a path exists", "rising water / increasing threshold", "widest/lowest bottleneck path".

## NeetCode Link

https://neetcode.io/problems/swim-in-rising-water
