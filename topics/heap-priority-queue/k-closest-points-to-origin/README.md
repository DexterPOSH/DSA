# K Closest Points to Origin

**Category:** Heap / Priority Queue
**Difficulty:** medium

## Problem Statement

Diye gaye `points` (har ek `[x, y]`) aur ek integer `k`. Origin `(0, 0)` ke **k closest points** return karo. Distance Euclidean hai: `sqrt(x² + y²)` — but ranking ke liye `x² + y²` hi kaafi hai (sqrt monotonic hai, order nahi badalta). Answer kisi bhi order me ho sakta hai.

```
points = [[1,3],[-2,2],[5,8],[0,1]], k = 2
dist²:     10     8      89    1
-> [[0,1], [-2,2]]      # 2 closest (dist² = 1 and 8)
```

## Real-World Analogy

**What Azure Maps is:** Azure Maps is Azure's geospatial service for rendering maps, geocoding addresses, routing vehicles, and building location-aware applications. A dispatch or logistics app can use Azure Maps data to reason about where depots, drivers, devices, or responders are relative to a request location. The practical question is often not "sort every place on earth," but "which k candidates are closest to this point?"

**What nearest-resource selection is, and why it's used:** Nearest-resource selection ranks candidate locations by distance from a target location so an app can pick the best few resources quickly. When the candidate set is large and `k` is small, fully sorting every distance wastes work, because far-away candidates only matter if they are close enough to enter the current top-k. A bounded max-heap keeps only the best k candidates and exposes the current farthest accepted one as the easiest item to evict.

**The mapping:** Each point is an Azure Maps-style candidate location, and `x² + y²` is its distance score from the request at the origin. The heap stores the current k closest points, while the root is the farthest point still allowed in that accepted set. When a new point is closer than the root, replace the root; otherwise ignore it. The key insight is that top-k closeness only needs a moving boundary, not a full sorted ranking of every point.

## Approach

Sabse simple: saare points ko `dist²` se sort karo, pehle k lo — O(n log n). Bilkul valid, often best in practice.

**Heap of size k — O(n log k)**, jab `n` bahut bada ho aur `k` chhota. Ek **max-heap** rakho jisme largest `dist²` top pe ho. Har point ke liye: agar heap me k se kam hai to push; warna agar current point heap ke top (farthest) se closer hai to top pop karo aur current push. Antt me heap me k closest bach jaate hain.

```python
import heapq

def k_closest(points, k):
    heap = []                                  # max-heap via negated dist
    for x, y in points:
        d = x*x + y*y
        if len(heap) < k:
            heapq.heappush(heap, (-d, x, y))
        elif -d > heap[0][0]:                  # closer than current farthest
            heapq.heapreplace(heap, (-d, x, y))
    return [[x, y] for _, x, y in heap]
```

`heapreplace` = pop-then-push ek hi op me (efficient). Negate isliye kyunki Python min-heap deta but humein max chahiye.

> **Best of all — Quickselect O(n) average:** partition around a pivot dist² taaki k smallest left me aa jaayein. Sort/heap se bhi fast average-case, but worst-case O(n²) aur implement karna fiddly. Interview me mention karna bonus.

## Complexity

- **Time:** O(n log k) heap approach. Har point ek O(log k) heap op. (Sort: O(n log n); Quickselect: O(n) average.)
- **Space:** O(k) heap (sort O(n) / O(log n)).

## Common Pitfalls

- **`sqrt` lena** — non-zaroori aur floating-point error la sakta. `x² + y²` se compare karo, sqrt skip.
- **Min vs max heap confusion** — k *closest* chahiye to *max*-heap of size k rakho (farthest ko evict karne ke liye). Min-heap of size k galat elements rakhega.
- **Tuple me dist pehle na rakhna** — heap tuples ko first element pe compare karta. `(-d, x, y)` me `-d` pehle hona chahiye, warna x/y pe sort ho jayega.
- **`x == y` ya negative coords** — `x*x` always non-negative, koi issue nahi; bas `abs` ki zaroorat nahi.

## When to Use This Pattern

"Top-k closest / smallest / largest by some computed score" → max-heap (closest/smallest ke liye) ya min-heap (farthest/largest ke liye) of size k, OR quickselect agar pure O(n) chahiye. Cue: poora sort overkill lage jab sirf k chahiye. Cousins: Kth Largest in Array, Top K Frequent.

## NeetCode Link

https://neetcode.io/problems/k-closest-points-to-origin
