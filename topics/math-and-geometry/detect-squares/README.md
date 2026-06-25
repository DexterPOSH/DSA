# Detect Squares

**Category:** Math & Geometry
**Difficulty:** medium

## Problem Statement

Design a data structure `DetectSquares` that supports adding points on a 2D plane and counting
**axis-aligned squares** that can be formed with a given query point and three previously added
points.

- `add(point)` — add a point `[x, y]` (duplicates allowed; same point can be added multiple times).
- `count(point)` — given a query point `[qx, qy]`, return how many axis-aligned squares have
  this query point as one corner and the other three corners among the added points (counting
  multiplicities).

```
add([3, 10]); add([11, 2]); add([3, 2]);
count([11, 10])  ->  1     # square with corners (3,10)(11,10)(11,2)(3,2)
count([14, 8])   ->  0     # no matching square
```

> "Axis-aligned" matlab square ki sides x/y axes ke parallel hain (tilted nahi). Yahi
> restriction problem ko O(n) per query me solvable banata hai.

## Real-World Analogy

**What Azure Maps is:** Azure Maps is Azure's geospatial service for building map, routing, search, and location-aware experiences. Apps can send point locations such as GPS pings or asset positions and ask spatial questions quickly. For this problem, the important idea is not drawing a map; it's keeping coordinate data organized so a query point can be matched against other exact points.

**What coordinate-indexed geofence checking is, and why it's used:** A geofence is a virtual boundary around a real-world area, and Azure Maps-style location workflows need fast ways to decide which stored points line up with that boundary. Indexing events by exact coordinate and also by x-coordinate avoids scanning every location every time a square-shaped boundary is tested. Duplicate pings at the same coordinate are kept as counts because repeated events at a corner create multiple valid square combinations.

**The mapping:** `add(point)` stores Azure Maps location-event counts by coordinate, while `count(qx, qy)` treats the query point as one square corner. Every stored point in the same x-column chooses a vertical side length; once that length is known, the two possible horizontal columns are forced, and hash lookups check the other two corners. Multiplying the three corner counts accounts for repeated events, and the key insight is that one aligned corner fixes the entire square, so coordinate counts make the search fast.

## Approach

Do cheezein maintain karo: ek `Counter` jo **har exact point ka count** rakhe, aur ek list/dict
of points. `count` pe, query ke **same x-column** wale saare points ko diagonal candidate maano:

```python
from collections import defaultdict, Counter

class DetectSquares:
    def __init__(self):
        self.cnt = Counter()                 # (x,y) -> times added
        self.cols = defaultdict(list)        # x -> list of y's seen (for iteration)

    def add(self, point):
        x, y = point
        self.cnt[(x, y)] += 1
        self.cols[x].append(y)

    def count(self, point):
        qx, qy = point
        total = 0
        for py in self.cols[qx]:             # same column as query
            side = py - qy
            if side == 0:
                continue                     # need a real vertical side
            # diagonal corner is (qx + side, py); square spans to the right and left
            for dx in (side, -side):
                total += (self.cnt[(qx, py)]            # top corner (same column)
                          * self.cnt[(qx + dx, qy)]     # bottom corner (other column, query row)
                          * self.cnt[(qx + dx, py)])    # diagonal corner
        return total
```

Idea: fix the **vertical side** `(qx, qy)–(qx, py)`. Square left ya right dono taraf ban sakta
hai, isliye `dx = ±side`. Teen corners ke counts multiply (multiplicities ke liye), sab add.

> Note: hum sirf same-column points iterate karte hain (not all points), isliye query fast rehta.

Pattern: **hashmap of point-counts + fix-the-diagonal/side geometric enumeration**.

## Complexity

- **Time:** `add` O(1). `count` O(k) where k = number of points sharing the query's x-column
  (worst case O(n), but usually much less). Counts lookup O(1) each.
- **Space:** O(n) — store every added point's count plus column index.

## Common Pitfalls

- **Degenerate side bhulna** — `side == 0` (same y as query) skip karo, warna zero-area "square".
- **Sirf ek taraf check karna** — square query ke **left aur right** dono taraf ban sakta hai;
  `dx = +side` aur `-side` dono try karo, warna aadhe squares miss.
- **Duplicates (multiplicities) ignore karna** — agar koi corner 3 baar add hua, to wo 3 squares
  me contribute karta hai → counts **multiply** karo, sirf existence check nahi.
- **Iterating all points** — har point ko diagonal maan ke check karne se O(n) per query but lots
  of wasted work; same-column filter clean hai. (Ya alternatively same-row.)
- **Galat corner derive karna** — query `(qx,qy)` ke saath corners hain `(qx,py)`, `(qx+dx,qy)`,
  `(qx+dx,py)`. Inko mix-up karna common bug.
- **Non-axis-aligned squares dhoondhna** — problem sirf axis-aligned maangta hai; tilted mat socho.

## When to Use This Pattern

Jab "stream of points + repeated geometric count queries" ho aur shapes axis-aligned hon →
**hashmap of point counts + enumerate one defining element (diagonal/side) and derive the rest**.
Cue: "design a structure", "count rectangles/squares formed by added points", "axis-aligned". The
"fix one corner/diagonal, others are determined" trick recur karta hai rectangle/square counting
problems me.

## NeetCode Link

https://neetcode.io/problems/count-squares
