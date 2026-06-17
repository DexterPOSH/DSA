# Number of Islands

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

Given an `m x n` 2D grid of `'1'`s (land) and `'0'`s (water), return the number of **islands**. An island is a group of `'1'`s connected **4-directionally** (up/down/left/right). The grid edges are surrounded by water.

```
grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"],
]
->  3
```

## Real-World Analogy

Socho ek satellite photo hai jisme zameen (`1`) aur paani (`0`) dikh raha hai. Tumhe ginna hai kitne alag-alag landmass (islands) hain. Tum upar se neeche, baaye se daaye scan karte ho. Jaise hi ek aisa land cell milta hai jise tumne abhi tak **paint nahi kiya**, tum bolte ho "naya island mila!" — aur fir us cell se shuru karke **flood-fill** kar dete ho: us se juda har connected land cell ko paint karke `visited` mark kar dete ho, taaki wahi island dobara count na ho. Jitni baar tumhe "naya land" mila, utne islands.

## Approach

Pattern: **grid as an implicit graph** — har land cell ek node hai, adjacent land cells ke beech edge hai. Connected components ginne hain → DFS/BFS flood fill.

Grid ke har cell pe loop chalao. Agar cell `'1'` hai aur abhi tak visit nahi hua, to `count += 1` karo aur us cell se DFS chalakr poora connected island "doobo do" (mark as visited, ya `'0'` me badal do).

```python
def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    def sink(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
            return
        grid[r][c] = "0"                # mark visited (sink the land)
        sink(r + 1, c); sink(r - 1, c)
        sink(r, c + 1); sink(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)              # flood-fill the whole island
    return count
```

> BFS version: ek `deque` lo, starting cell push karo, jab tak queue khaali na ho neighbours ko visit-mark karke push karte raho. Deep grids pe BFS recursion-depth ka stack overflow avoid karta hai.

## Complexity

- **Time:** O(m·n) — har cell ko at most ek baar visit karte hain (mark hone ke baad dobara enter nahi).
- **Space:** O(m·n) worst case — DFS recursion stack (poora grid ek hi snake-shaped island ho to), ya BFS queue.

## Common Pitfalls

- **Diagonals ko bhi connected maan lena** — problem sirf 4-directional connectivity maangta hai, 8 nahi. Diagonal include karoge to count galat.
- **Visited mark karna bhul jaana** — agar cell ko `'0'`/visited mark nahi karoge to wahi cells baar-baar revisit honge → infinite recursion / TLE.
- **String vs int** — LeetCode me cells `"1"`/`"0"` (strings) hote hain, integers nahi. `grid[r][c] == 1` likhoge to silently fail.
- **Grid mutate karna allowed hai ya nahi** — `sink` original grid ko destroy kar deta hai. Agar caller grid preserve karna chahta hai to alag `visited` set rakho.
- **Empty grid** — `len(grid[0])` se pehle check karo ki grid khaali to nahi.

## When to Use This Pattern

Jab "2D grid me connected regions/components count karo" ya "ek cell se phailne wala blob" dikhe → grid-DFS/BFS flood fill. Cousins: Max Area of Island, Surrounded Regions, Flood Fill, Rotting Oranges. Cue: grid + connectivity → har unvisited seed se ek flood-fill chalao.

## NeetCode Link

https://neetcode.io/problems/count-number-of-islands
