# Pacific Atlantic Water Flow

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

You're given an `m x n` grid `heights` of cell elevations. The **Pacific** ocean touches the grid's **top and left** edges; the **Atlantic** touches the **bottom and right** edges. Water flows from a cell to a neighbor (4-directionally) only if the neighbor's height is **less than or equal**. Return all cells `[r, c]` from which water can reach **both** oceans.

```
heights = [
  [1,2,2,3,5],
  [3,2,3,4,4],
  [2,4,5,3,1],
  [6,7,1,4,5],
  [5,1,1,2,4],
]
->  [[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]
```

## Real-World Analogy

Socho ek pahaadi ilaaka hai, har cell ki ek height hai, aur paani sirf neeche ya barabar height pe beh sakta hai. Tum poochh rahe ho: "kaun se points se paani **dono** samundar tak pahunch sakta hai?" Seedha approach (har cell se dono ocean tak DFS) bahut mehnga hai. Smart trick: **ulta socho** — samundar ke kinaare se ** upar ki taraf (uphill) paani chadhao**. Pacific ke border cells se shuru karke jahan-jahan paani *chadh* sakta hai (neighbor height >= current) mark karte jaao — ye saare cells "Pacific tak beh sakte hain". Yahi Atlantic ke border se karo. Dono floods ka **intersection** = answer.

## Approach

Pattern: **multi-source DFS/BFS from the borders, with reversed flow** (flow uphill from each ocean), then intersect.

Do sets banao: `pac` aur `atl`. Pacific ke top-row + left-col cells se DFS shuru karo, Atlantic ke bottom-row + right-col se. DFS me **reverse condition** — neighbor tabhi visit karo jab uski height current se `>=` ho (kyunki hum uphill chal rahe hain). Dono sets ka intersection final answer.

```python
def pacific_atlantic(heights):
    rows, cols = len(heights), len(heights[0])
    pac, atl = set(), set()

    def dfs(r, c, visited, prev_height):
        if (r < 0 or r >= rows or c < 0 or c >= cols or
                (r, c) in visited or heights[r][c] < prev_height):
            return
        visited.add((r, c))
        for dr, dc in ((1,0), (-1,0), (0,1), (0,-1)):
            dfs(r+dr, c+dc, visited, heights[r][c])

    for c in range(cols):
        dfs(0, c, pac, heights[0][c])            # Pacific top row
        dfs(rows-1, c, atl, heights[rows-1][c])  # Atlantic bottom row
    for r in range(rows):
        dfs(r, 0, pac, heights[r][0])            # Pacific left col
        dfs(r, cols-1, atl, heights[r][cols-1])  # Atlantic right col

    return [[r, c] for r in range(rows) for c in range(cols)
            if (r, c) in pac and (r, c) in atl]
```

> Key flip: paani ko cell-se-ocean trace karne ki jagah **ocean-se-uphill** trace karo. Isse har source se ek hi flood me saare reachable cells mil jaate hain — O(m·n) per ocean.

## Complexity

- **Time:** O(m·n) — har cell har ocean ke flood me at most ek baar visit hota hai (visited set guard).
- **Space:** O(m·n) — do visited sets + recursion stack.

## Common Pitfalls

- **Flow direction ulta na karna** — yahan hum uphill chal rahe hain, isliye condition `neighbor >= current` (i.e. `heights[r][c] < prev_height` pe ruk jao). Downhill condition likhoge to galat.
- **Har cell se forward DFS karna** — O((m·n)²) blow-up. Borders se reverse flood hi efficient hai.
- **`<=` vs `<`** — equal height pe paani beh sakta hai, isliye `>=` allow karo (strictly greater nahi).
- **Corner cells** — top-left Pacific dono edges, top-right/bottom-left dono oceans ko touch karte hain; loops me overlap se koi dikkat nahi (set dedupes).
- **Alag `prev_height` track** — visited check ke saath height-comparison dono chahiye, warna neeche bhi chala jaayega.

## When to Use This Pattern

Jab "kaun se cells multiple targets/boundaries tak pahunch sakte hain" pucha jaaye → **reverse the direction**, targets se multi-source flood karo, fir intersect. Cue: "reach from many sources to many sinks" → flip karo aur sinks se BFS/DFS. Cousins: 01 Matrix (multi-source BFS), Walls and Gates.

## NeetCode Link

https://neetcode.io/problems/pacific-atlantic-water-flow
