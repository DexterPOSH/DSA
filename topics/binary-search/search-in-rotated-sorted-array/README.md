# Search in Rotated Sorted Array

**Category:** Binary Search
**Difficulty:** medium

## Problem Statement

You're given an integer array `nums` that was originally sorted in ascending order, then **rotated** at some unknown pivot, and a `target`. Return the index of `target`, or `-1` if it's not present. All values are distinct. The catch: you must do it in **O(log n)** — so plain linear scan is disqualified.

```
nums = [4, 5, 6, 7, 0, 1, 2], target = 0   ->  4
nums = [4, 5, 6, 7, 0, 1, 2], target = 3   ->  -1
nums = [6, 7, 0, 1, 2, 4, 5], target = 7   ->  1
```

The array `[0,1,2,4,5,6,7]` rotated at pivot index 4 becomes `[4,5,6,7,0,1,2]`.

## Real-World Analogy

**What Azure Cosmos DB is:** Azure Cosmos DB is a distributed NoSQL database that routes data by hashing a partition key into an ordered key-range space. Those key ranges are assigned to physical partitions so the service can scale and split partitions over time. Conceptually, the ordered hash space wraps around like a ring, even if a displayed range list starts from the middle.

**What a partition hash ring is, and why it's used:** A partition hash ring gives the router a stable way to decide which range owns a target hash, even as ranges split or move. It exists so Cosmos DB can distribute load while still finding the correct partition without scanning every range. If you list the ring from an arbitrary starting point, the list is sorted except for one wrap where the largest hashes roll over to the smallest hashes.

**The mapping:** The rotated `nums` array is that Azure Cosmos DB hash-ring list, `target` is the hash range you are trying to find, and `lo`, `mid`, and `hi` bound the visible window. At every step, either `lo…mid` or `mid…hi` is still normally sorted; if the target falls inside that sorted side, keep it, otherwise keep the other side that contains the wrap. The key insight is that even in a rotated structure, one half remains trustworthy enough to eliminate the other half.
## Approach

Standard binary search ka twist: pehle decide karo ki `mid` ke kis side wala half sorted hai, phir decide karo target us sorted half me hai ya nahi.

Har iteration pe `mid = (lo + hi) // 2`:

1. **`nums[mid] == target`** → mil gaya, index return.
2. **Left half sorted hai** (`nums[lo] <= nums[mid]`):
   - Agar `nums[lo] <= target < nums[mid]` → target left me hai, `hi = mid - 1`.
   - Warna `lo = mid + 1` (right me dhoondo).
3. **Warna right half sorted hai**:
   - Agar `nums[mid] < target <= nums[hi]` → target right me hai, `lo = mid + 1`.
   - Warna `hi = mid - 1`.

```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:            # left half sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                 # right half sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

Pattern: **modified binary search** — invariant "ek half sorted hai" use karke search space half karte raho.

## Complexity

- **Time:** O(log n) — har step pe search space aadha hota hai, bilkul vanilla binary search jaisa.
- **Space:** O(1) — sirf teen pointers (`lo`, `mid`, `hi`), koi extra structure nahi.

## Common Pitfalls

- **`<=` vs `<` me galti** — `nums[lo] <= nums[mid]` me `=` zaroori hai (jab `lo == mid`, single element left half ko sorted maano). Range checks me boundaries (`nums[lo] <= target < nums[mid]`) galat lagana = wrong half, infinite loop ya miss.
- **Duplicates assume kar lena** — yeh version distinct maanta hai. Agar duplicates ho (LeetCode 81), `nums[lo] == nums[mid]` ambiguous ho jaata aur worst case O(n) ban jaata — interviewer se clarify karo.
- **Pivot alag se dhoondhne ki koshish** — pehle pivot find karke phir search karna bhi chalega (do binary searches), but ek hi pass me ho jaata hai. Over-engineer mat karo.
- **`mid = (lo + hi) // 2`** — Python me overflow nahi, but Java/C++ me `lo + (hi - lo) // 2` likho.

## When to Use This Pattern

Jab "sorted but disturbed" array dikhe aur **O(log n)** maanga jaaye — rotated array, mountain array, ya koi bhi structure jisme local monotonicity guarantee ho. Cue: array fully sorted nahi hai but **har point pe ek side predictable** hai → binary search ko "kaun sa half trust karein" wali condition ke saath modify karo. Cousins: Find Minimum in Rotated Sorted Array, Search in 2D Matrix, Peak Element.

## Practice

- Visual: open `topics/binary-search/search-in-rotated-sorted-array/visual.html`

## NeetCode Link

https://neetcode.io/problems/find-target-in-rotated-sorted-array
