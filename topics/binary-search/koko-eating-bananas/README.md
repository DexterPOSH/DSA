# Koko Eating Bananas

**Category:** Binary Search
**Difficulty:** medium

## Problem Statement

There are `n` piles of bananas; `piles[i]` is the count in pile `i`. Koko eats at a speed of `k` bananas/hour. Each hour she picks one pile and eats up to `k` from it — if the pile has fewer than `k`, she finishes it and **stops for that hour** (doesn't carry over to another pile). She wants to finish all piles within `h` hours. Return the **minimum integer `k`** that lets her finish in time.

```
piles = [3, 6, 7, 11], h = 8    ->  4
piles = [30, 11, 23, 4, 20], h = 5   ->  30
```

At `k = 4`: pile 3 → 1hr, pile 6 → 2hr, pile 7 → 2hr, pile 11 → 3hr = 8 hours. ✅ And `k = 3` needs 9 hours. So 4 is the minimum.

## Real-World Analogy

**What Azure Cosmos DB is:** Azure Cosmos DB is a globally distributed NoSQL database where you provision throughput in request units per second (RU/s). Every read, write, and query consumes RUs, so the RU/s setting controls how much work the database can handle each second. More RU/s gives the workload more capacity, but it also costs more, so teams want the smallest setting that still meets their SLA.

**What provisioned throughput is, and why it's used:** Provisioned throughput reserves a chosen RU/s capacity for a container or database so performance is predictable. If the setting is too low for a workload, requests can be throttled or take too long; if it is high enough, the workload finishes within the target window. That creates a monotonic feasibility curve: low RU/s values fail, and after some threshold, all higher RU/s values pass.

**The mapping:** Koko's eating speed `k` is the Azure Cosmos DB RU/s candidate, each banana pile is a batch of work that needs capacity, and `ceil(pile / k)` is how many time slices that batch consumes at that capacity. The `feasible(k)` check sums those slices and asks whether the workload finishes within `h`; if it passes, binary search keeps `k` but tries cheaper lower capacity, and if it fails, it searches higher. The key insight is to binary-search the monotonic threshold for the minimum feasible capacity, not to simulate every possible speed.
## Approach

Pattern: **binary search on the answer**. Speed range `[1, max(piles)]` hai — max se zyada speed ka koi faayda nahi (ek pile ek hour me hi khatam). Har candidate `k` ke liye check karo: kitne hours lagenge?

Ek pile `p` ko khane ke hours = `ceil(p / k)` = `(p + k - 1) // k`.

```python
import math

def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        k = (lo + hi) // 2
        hours = sum(math.ceil(p / k) for p in piles)
        if hours <= h:
            hi = k          # k feasible -> try slower (smaller k), keep k
        else:
            lo = k + 1      # k too slow -> need faster
    return lo               # lo == hi == smallest feasible speed
```

Yahan **`lo < hi` (half-open, "lower-bound" style)** use kiya — kyunki hum *boundary* (smallest feasible) dhoond rahe, exact match nahi. `hi = k` (not `k-1`) kyunki `k` khud answer ho sakta. Loop khatam hone pe `lo == hi` = first speed jahan `hours <= h`.

## Complexity

- **Time:** O(n · log(max(piles))) — binary search `log(max)` iterations, har iteration me poore `n` piles pe feasibility sum.
- **Space:** O(1) — sirf pointers aur running sum.

## Common Pitfalls

- **Linear scan `k = 1, 2, 3…`** — `max(piles)` huge ho sakta (10⁹), TLE. Answer pe binary search must.
- **Integer ceil galat** — `p // k` floor deta; chahiye `ceil`. Use `(p + k - 1) // k` ya `math.ceil(p / k)`. Floor use kiya to under-count hours → galat answer.
- **`hi = k - 1` likh dena lower-bound search me** — feasible `k` ko discard kar dega, answer se off-by-one. Boundary search me `hi = mid`.
- **`lo = 0` se start** — speed 0 matlab kabhi khatam nahi (divide by zero bhi). Min speed `1` hai.
- **Per-hour "ek hi pile" rule miss karna** — woh `ceil` me capture hota hai (bachi-khuchi bananas bhi poora hour lete), isliye `ceil`, plain division nahi.

## When to Use This Pattern

Cue: **"minimum/maximum value such that some condition holds"** + condition **monotonic** hai (ek threshold ke baad hamesha true/false). Phrase like "minimum speed", "smallest capacity", "least time", "largest x such that…". Tab answer ki range pe binary search lagao + ek `feasible(x)` checker likho. Cousins: Capacity to Ship Packages, Split Array Largest Sum, Minimize Max Distance.

## NeetCode Link

https://neetcode.io/problems/eating-bananas
