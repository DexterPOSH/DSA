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

Yeh ek **"answer pe binary search"** problem hai — array me kuch nahi dhoond rahe, hum *speed `k`* dhoond rahe hain. Socho ek shower ka **temperature knob**: bahut dheere (low `k`) ghumao to time zyada lagega, bahut tez (high `k`) sab jaldi ho jaayega. Ek **threshold** hota hai — usse upar ki har speed "kaam ho jaata in time" (feasible), usse neeche ki har speed "time nikal gaya" (infeasible). Yeh monotonic flip — `false false false TRUE TRUE TRUE` — exactly binary search ke liye bana hai. Hum **smallest feasible speed** dhoond rahe.

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
