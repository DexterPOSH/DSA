# Median of Two Sorted Arrays

**Category:** Binary Search
**Difficulty:** hard

## Problem Statement

Given two sorted arrays `nums1` and `nums2` of sizes `m` and `n`, return the **median** of the combined sorted array. The required run time is **O(log(m + n))** — so merging the two arrays (O(m + n)) is not good enough for full credit.

```
nums1 = [1, 3], nums2 = [2]        ->  2.0     # merged = [1,2,3], middle = 2
nums1 = [1, 2], nums2 = [3, 4]     ->  2.5     # merged = [1,2,3,4], avg(2,3)
nums1 = [1, 3], nums2 = [2, 7]     ->  2.5     # merged = [1,2,3,7], avg(2,3)
```

## Real-World Analogy

**What Azure Cosmos DB is:** Azure Cosmos DB is a distributed NoSQL database that can store related data across multiple physical partitions. Cross-partition queries coordinate results from those partitions, and ordered queries may have to combine already-sorted streams. When the goal is a percentile such as global P50 latency, the important value is an order statistic, not the full merged list.

**What a sorted cross-partition merge is, and why it's used:** In a normal cross-partition `ORDER BY`-style query, the query engine can read sorted results from each partition and merge them so the client sees one globally ordered stream. That is useful, but fully materializing the stream can waste RUs and time if you only need the middle value. A smarter approach is to find a partition cut: enough items on the left to cover half the combined data, with every left boundary value less than or equal to every right boundary value.

**The mapping:** The two sorted arrays are two Azure Cosmos DB partition streams, and binary search chooses a cut `i` in the smaller stream while deriving `j = half - i` in the other. `Aleft`, `Aright`, `Bleft`, and `Bright` are the boundary records around the cut; if `Aleft > Bright`, the cut in `A` is too far right, and if `Bleft > Aright`, it is too far left. The key insight is that once the boundary checks pass, the median comes from those four edge values, so no full merge is needed.
## Approach

Hum **chhoti array pe binary search** karte hain. Maan lo `A` = chhoti, `B` = badi. Ek partition `i` (A me) choose karo; tab `j = half - i` (B me), jahan `half = (m + n + 1) // 2`. Yeh ensure karta hai left half me exactly `half` elements aayein.

Char boundary values:

- `Aleft = A[i-1]`, `Aright = A[i]`
- `Bleft = B[j-1]`, `Bright = B[j]`
  (out-of-range pe `-inf` / `+inf` use karo.)

**Valid partition** tab hai jab `Aleft <= Bright` **and** `Bleft <= Aright`. Tab:
- total length odd → median = `max(Aleft, Bleft)`.
- even → median = `(max(Aleft, Bleft) + min(Aright, Bright)) / 2`.

Agar `Aleft > Bright` → A ne left me bahut bheja, `i` ghatao (`hi = i - 1`). Agar `Bleft > Aright` → A ne kam bheja, `i` badhao (`lo = i + 1`).

```python
def find_median_sorted_arrays(nums1, nums2):
    A, B = nums1, nums2
    if len(A) > len(B):
        A, B = B, A                          # binary search on the SHORTER array
    m, n = len(A), len(B)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2                   # cut in A
        j = half - i                         # cut in B
        Aleft  = A[i-1] if i > 0 else float('-inf')
        Aright = A[i]   if i < m else float('inf')
        Bleft  = B[j-1] if j > 0 else float('-inf')
        Bright = B[j]   if j < n else float('inf')
        if Aleft <= Bright and Bleft <= Aright:        # correct partition
            if (m + n) % 2:
                return float(max(Aleft, Bleft))
            return (max(Aleft, Bleft) + min(Aright, Bright)) / 2
        elif Aleft > Bright:
            hi = i - 1                        # move cut in A left
        else:
            lo = i + 1                        # move cut in A right
    return 0.0                                # unreachable for valid input
```

Pattern: **binary search on the partition index**, not on values. Hum answer ki position ko guess-and-narrow karte hain.

## Complexity

- **Time:** O(log(min(m, n))) — binary search chhoti array (length `m`) pe chalti hai, har step O(1). Yeh O(log(m + n)) requirement ke andar comfortably aata hai.
- **Space:** O(1) — koi merge, koi extra array nahi; sirf boundary variables.

## Common Pitfalls

- **Chhoti array pe search na karna** — `lo, hi = 0, m` chhoti array pe hone chahiye, warna `j = half - i` negative ya out-of-range ho jaata. Swap step skip mat karo.
- **`half = (m + n + 1) // 2`** ka `+1` — yeh odd-length case me median ko left half me daalta hai (`max(Aleft, Bleft)` se nikaalne ke liye). `+1` chhodo to odd case toot-ta hai.
- **Infinity sentinels bhoolna** — jab partition kisi array ke bilkul edge pe ho (`i == 0` ya `i == m`), `-inf`/`+inf` use karo taaki comparisons valid rahein bina special-casing ke.
- **`<=` vs `<`** — equal elements ke saath bhi partition valid hona chahiye, isliye `Aleft <= Bright` (strict `<` nahi).
- **Float division** — odd case me `float(...)` cast karo, even case `/2` already float deta hai; integer median return karke marks mat gawao.

## When to Use This Pattern

Jab do (ya zyada) **sorted inputs** ho aur ek **order-statistic** (median, k-th smallest) chahiye **sub-linear** time me → binary search on partition / on the answer. Cue: "sorted", "k-th smallest across arrays", "median without merging", "O(log) on combined size". Yeh classic **binary-search-the-answer** family ka sabse tough relative hai. Cousins: Kth Smallest in Sorted Matrix, Split Array Largest Sum, Koko Eating Bananas.

## Practice

- Visual: open `topics/binary-search/median-of-two-sorted-arrays/visual.html`

## NeetCode Link

https://neetcode.io/problems/median-of-two-sorted-arrays
