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

Socho ek **circular ghadi (clock)** hai jisme numbers sorted hain, but kisi ne usse ghuma diya — ab "12" top pe nahi, kahin beech me hai. Tumhe ek particular number dhoondhna hai. Trick ye hai: bhale hi poora array rotated ho, koi bhi do points (`lo` aur `hi`) ke beech mid lo to **kam se kam ek aadha (half) hamesha properly sorted hota hai**. Wo sorted half dekho — agar target uski range me aata hai, udhar jao; warna doosre (potentially messy) half me jao. Har step pe aadha array kaat do. Bas yahi hai poora khel.

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
