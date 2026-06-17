# Max Area of Island

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

Given an `m x n` binary grid where `1` = land and `0` = water, return the **area of the largest island** (number of `1` cells, connected 4-directionally). If there is no island, return `0`.

```
grid = [
  [0,0,1,0,0],
  [0,1,1,1,0],
  [0,0,1,0,0],
  [1,1,0,0,0],
]
->  5     # the plus-shaped island in the middle
```

## Real-World Analogy

Same satellite-photo wali kahani jaise Number of Islands — par ab tumhe islands **ginne** nahi, sabse bade island ka **area naapna** hai. Socho har island ko flood-fill karte waqt tum ek counter rakhte ho: jitne land cells us flood me doobte hain, utna us island ka area. Har naye island ka area nikaalo, aur ab tak ka **maximum** yaad rakho. Akhir me jo sabse bada blob mila, wahi answer.

## Approach

Pattern: **grid flood-fill (DFS/BFS) jo size return kare**, plus ek running max.

Number of Islands se ek hi twist: `sink` function ab sirf mark nahi karta, balki "maine kitne cells doobaye" ka count return karta hai. Har seed cell ke flood ka area `max_area` se compare karke max update karo.

```python
def max_area_of_island(grid):
    rows, cols = len(grid), len(grid[0])

    def area(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
            return 0
        grid[r][c] = 0                          # mark visited
        return 1 + area(r+1, c) + area(r-1, c) + area(r, c+1) + area(r, c-1)

    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                best = max(best, area(r, c))     # area of THIS island
    return best
```

> `1 + (four directions)` — current cell ko 1 gino, fir chaaron taraf ka area jodo. Out-of-bounds ya water → 0 contribute.

## Complexity

- **Time:** O(m·n) — har cell at most ek baar visit, mark hone ke baad skip.
- **Space:** O(m·n) worst case — recursion stack (ek hi giant island ho to).

## Common Pitfalls

- **Local max ko reset karna bhul jaana** — har island ka area alag nikaalo; `area()` ka return value hi naturally per-island hai, isliye DFS function se size return karwana cleanest hai.
- **Int grid vs string grid** — yahan cells `int` (`1`/`0`) hote hain, Number of Islands ke `"1"`/`"0"` strings se ulat. Comparison match karna.
- **Visited mark na karna** → har cell baar-baar count hoga, area infinite/galat.
- **`best = 0` initialize** — koi island na ho to `0` return hona chahiye, `-inf` nahi.
- **Mutating the grid** — `area` grid destroy kar deta. Grid preserve karna ho to alag `visited` set.

## When to Use This Pattern

Number of Islands ka "size-aware" cousin. Jab "grid me sabse bade connected region ka size/area/weight" pucha jaaye → flood-fill jo aggregate (count/sum) return kare + global max. Cue: connected component + "kitna bada" → DFS return value se size carry karo.

## NeetCode Link

https://neetcode.io/problems/max-area-of-island
