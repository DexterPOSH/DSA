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

Socho ek **graph paper** pe pins thok rahe ho. Koi tumhe ek query pin `(qx, qy)` deta hai
aur poochta hai: "is pin ko ek corner maan ke, kitne perfect (axis-aligned) square ban sakte
hain baaki thoke gaye pins se?"

Smart move: ek axis-aligned square ka **diagonally opposite corner** hi sab kuch decide kar
deta hai. Agar query corner `(qx, qy)` hai aur diagonal corner `(px, py)` hai, to square hone
ke liye us diagonal ka **horizontal aur vertical span barabar** hona chahiye —
`|px - qx| == |py - qy|` aur dono non-zero (warna line ban jaayegi, square nahi). Diagonal fix
ho gaya to baaki **do corners apne-aap** decide ho jaate hain: `(qx, py)` aur `(px, qy)`. Bas
ginna hai kitni baar wo do corners pehle add hue.

To strategy: har **same column** wale point `(qx, py)` ko diagonal candidate ki tarah dekho,
phir check karo baaki teen corners exist karte hain ya nahi, aur unke counts multiply kar do.

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
