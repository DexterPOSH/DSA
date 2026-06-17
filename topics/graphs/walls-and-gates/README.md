# Walls and Gates

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

You're given an `m x n` grid where each cell is one of:

- `-1` — a **wall** or obstacle (cannot pass through)
- `0` — a **gate**
- `INF` (`2147483647`) — an **empty room**

Fill each empty room with the **distance to its nearest gate** (4-directionally). If a room cannot reach any gate, leave it as `INF`. Modify the grid in place.

```
Input:                       Output:
INF  -1   0  INF             3  -1   0   1
INF INF INF  -1              2   2   1  -1
INF  -1 INF  -1              1  -1   2  -1
  0  -1 INF INF              0  -1   3   4
```

(`INF` = `2147483647`)

## Real-World Analogy

Socho ek building ka floor plan hai jisme kuch **exit gates** hain, kuch **walls**, aur baaki khaali rooms. Har room me ek sign lagana hai: "nearest exit kitne steps door hai?" Agar tum **har gate se ek saath** "main yahan hoon, 0 steps" announce karwao aur ye message ripple karke spread ho — pehla ripple jo kisi room tak pahunche, wahi uska nearest-gate distance hai. Kyunki saare gates ek saath chillate hain (**multi-source**), pehli wave jo room ko chhuye guaranteed shortest hai. Walls ripple ko rok dete hain.

## Approach

Yeh **multi-source BFS** hai — bilkul Rotting Oranges jaisa, bas yahan "source" gates hain aur hum **distance label** karte hain. BFS की property: jab BFS pehli baar kisi cell ko reach karta hai, wahi shortest distance hota hai (unweighted graph). To gate se BFS ki har wave = +1 distance.

**Steps:**
1. Saare gates (`0`) ko queue me daalo (multi-source seed). Unka distance already 0 hai.
2. BFS chalao. Ek cell pop karo, uske 4 neighbours dekho. Agar koi neighbour `INF` hai (abhi tak visit nahi hua, wall bhi nahi), to use `current_dist + 1` set karo aur queue me daalo.
3. Wall (`-1`) aur already-filled rooms ko skip karo (`INF` check khud hi handle kar leta — ek baar fill hua to dobara nahi).

```python
from collections import deque

INF = 2147483647

def walls_and_gates(rooms):
    if not rooms:
        return
    rows, cols = len(rooms), len(rooms[0])
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if rooms[r][c] == 0:
                q.append((r, c))          # seed every gate

    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and rooms[nr][nc] == INF):   # only untouched empty rooms
                rooms[nr][nc] = rooms[r][c] + 1  # one step farther than me
                q.append((nr, nc))
```

> **Why is the first visit the shortest?** BFS layers expand uniformly outward. The first time any room is dequeued-into, it came via the shortest hop count from *some* gate — and since all gates started together, that's the nearest gate. No need to re-check or relax later.

## Complexity

- **Time:** O(m·n) — har cell ek hi baar fill hota hai (`INF` check guarantee), dirs constant.
- **Space:** O(m·n) — queue worst case poore grid jitni badi.

## Common Pitfalls

1. **DFS use karna** ya **har gate se alag-alag BFS** chalana → O(gates · m · n), slow. Ek single multi-source BFS sufficient aur fast hai.
2. **`INF` check chhodna** → already-filled cells dobara visit honge, distances overwrite ho sakte hain (longer path se), galat answer + possible TLE.
3. **Walls ko handle na karna** — `-1` `INF` nahi hai, isliye `== INF` guard automatically walls skip kar deta. Lekin agar tum `!= -1` likho to galti se 0/filled cells bhi reconsider ho sakte.
4. **Empty grid** (`rooms == []`) pe crash → early return.
5. **Distance ko fixed-source maan lena** — yahan har room ka apna nearest gate alag ho sakta; multi-source isi liye zaroori hai.

## When to Use This Pattern

Same family as Rotting Oranges aur 01-Matrix: **"nearest distance from any of several sources in a grid/unweighted graph."** Cue: multiple starting points, sabse-paas-wala source dhundhna, walls/obstacles, in-place distance fill. Jab dikhe "nearest X to every cell" → saare X ko BFS me ek saath seed karo, ek pass me sab fill ho jayega.

## Practice

- Visual: open `topics/graphs/walls-and-gates/visual.html`

## NeetCode Link

https://neetcode.io/problems/islands-and-treasure
