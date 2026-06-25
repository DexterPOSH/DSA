# Surrounded Regions

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

Given an `m x n` board of `'X'` and `'O'`, **capture** all regions that are **4-directionally surrounded** by `'X'`. A region of `'O'`s is captured (flipped to `'X'`) if it is **not connected to any `'O'` on the border**. Modify the board in-place.

```
X X X X            X X X X
X O O X     ->     X X X X
X X O X            X X X X
X O X X            X O X X
```

The middle `O`s are fully surrounded → flipped. The bottom-left `O` touches the border → survives.

## Real-World Analogy

**What Azure Virtual Network is:** Azure Virtual Network (VNet) is Azure's private networking boundary for subnets, routes, NSGs, gateways, and connected workloads. Some subnets may have a route to a VPN Gateway, ExpressRoute circuit, or internet edge, while others may be separated by NSG-denied links or route-table blocks. From a topology view, “open” subnets are useful only if they can still reach an allowed edge.

**What edge-reachable subnet isolation is, and why it's used:** Edge-reachable isolation marks every open Azure subnet that can still escape to a trusted boundary, then treats the remaining open subnets as enclosed. It is used because directly searching for trapped regions is error-prone: a region might look enclosed locally but have a winding path to the edge. By proving which subnets are safe first, you can lock down only the truly surrounded areas without cutting off valid gateway or ExpressRoute paths.

**The mapping:** `O` cells are open Azure subnets, `X` cells are blocked by NSGs/routes, and the board border represents subnets with external reachability. Flood-fill from every border `O` to mark all edge-connected open subnets as safe; after that, any unmarked `O` is enclosed and gets flipped to `X`. The key insight is to search from the boundary of safety, not from every possible trapped region.


## Approach

Pattern: **flood-fill from the borders to find the "escapees"**, then a final sweep flips the rest. (Reverse thinking, just like Pacific Atlantic.)

1. Board ke chaaron border pe har `'O'` se DFS chalakr connected `'O'`s ko temporary `'#'` (safe) mark karo.
2. Poora board sweep karo: bacha hua `'O'` → `'X'` (surrounded, capture), `'#'` → `'O'` (safe, restore).

```python
def solve(board):
    if not board:
        return
    rows, cols = len(board), len(board[0])

    def guard(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != "O":
            return
        board[r][c] = "#"                       # mark border-connected as safe
        guard(r+1, c); guard(r-1, c); guard(r, c+1); guard(r, c-1)

    for r in range(rows):
        guard(r, 0); guard(r, cols-1)           # left & right borders
    for c in range(cols):
        guard(0, c); guard(rows-1, c)           # top & bottom borders

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == "O":
                board[r][c] = "X"               # surrounded -> capture
            elif board[r][c] == "#":
                board[r][c] = "O"               # safe -> restore
```

> Direct "is this region surrounded?" check har region ke liye mushkil hai (escape detection). Border-flood ulta-flip karke problem ko ek simple 2-pass me reduce kar deta hai.

## Complexity

- **Time:** O(m·n) — border flood har safe cell ko ek baar chhoota, fir ek full sweep.
- **Space:** O(m·n) worst case — DFS recursion stack.

## Common Pitfalls

- **Seedha surrounded region dhoondhne ki koshish** — escape-route detection ulajh jaata hai. Hamesha **border se safe-mark** karo, fir invert.
- **Temporary marker conflict** — `'#'` aisa char ho jo board me na ho. Phase 2 me `'#' -> 'O'` restore karna mat bhoolo.
- **Sirf corners flood karna** — poore border (top+bottom rows, left+right cols) se flood karo, sirf 4 corners se nahi.
- **In-place modify** — problem board ko jagah pe badalne ko kehta hai; naya board return mat karo (jab tak signature na maange).
- **Empty board / single row** — `not board` guard; single-row/col me har `O` border pe hai → kuch capture nahi hota.

## When to Use This Pattern

Jab "regions jo boundary tak nahi pahunchti unhe flip/capture/remove karo" dikhe → **border se flood-fill, safe mark karo, fir invert.** Cue: "enclosed/surrounded by ..." → directly enclosed find mat karo; reachable-from-border ko nikaalo aur complement lo. Cousins: Pacific Atlantic, Number of Enclaves.

## NeetCode Link

https://neetcode.io/problems/surrounded-regions
