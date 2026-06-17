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

Socho ek crate me oranges rakhe hain aur kuch already sad chuke hain. Sadan ek hi orange se shuru nahi hota — **jitne bhi rotten oranges hain, sab ek saath apne padosiyon ko infect karte hain**. Pehle minute me har rotten orange apne 4 touching neighbours ko rot karta hai. Agle minute me wo naye-rotten oranges aage spread karte hain. Yeh ek "fire spreading from many sources at once" wala scene hai — isliye hum **single source nahi, multi-source BFS** chalate hain. BFS ki har " wave" = ek minute.

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
