# Binary Search

**Category:** Binary Search
**Difficulty:** easy

## Problem Statement

Given a **sorted** array `nums` (ascending, all distinct) and a target value, return the index of `target` if it exists, otherwise return `-1`. The solution must run in `O(log n)` time.

```
nums = [-1, 0, 3, 5, 9, 12], target = 9   ->  4
nums = [-1, 0, 3, 5, 9, 12], target = 2   ->  -1
```

## Real-World Analogy

Socho ek **dictionary** me word dhoond rahe ho. Tum page 1 se ek-ek page nahi palatte. Tum seedha **beech me kholte ho** — agar tumhara word us page se aage aata hai (alphabetically), to aadha dictionary (left half) bhul jao, aage wale half me dekho. Phir us half ke beech me kholo, phir uske... har baar **search space aadha** kat jaata hai. 1000 pages? Sirf ~10 jumps me word mil jaata hai. Yahi binary search hai — sorted data pe "beech me dekho, aadha kaato".

## Approach

Pattern: **classic binary search** — do pointers `lo` aur `hi` jo search window ke ends mark karte hain. Har step me `mid` nikaalo, target se compare karo, aur ek half discard kar do.

```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2          # ya lo + (hi - lo) // 2  -> overflow-safe
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1              # target right half me hai
        else:
            hi = mid - 1              # target left half me hai
    return -1
```

Teen baatein note karo:
1. **`lo <= hi`** — jab tak window me kam se kam 1 element hai, chalte raho. `<` use kiya to single-element window miss ho jaayega.
2. **`mid + 1` / `mid - 1`** — `mid` already check ho chuka, use dobara mat dekho. Warna infinite loop.
3. **`lo + (hi - lo) // 2`** — bade arrays me `lo + hi` overflow kar sakta (Python me nahi, but Java/C++ me yahi safe form hai).

## Complexity

- **Time:** O(log n) — har iteration me search space half hota hai, to `log₂(n)` steps me khatam.
- **Space:** O(1) — sirf teen pointers, koi extra structure nahi. (Recursive version O(log n) stack leta.)

## Common Pitfalls

- **`while lo < hi` likh dena** — last single-element window check nahi hoga, target miss. Classic form me `<=` chahiye.
- **`lo = mid` ya `hi = mid`** (without ±1) — `mid` ko window me wapas rakh diya to loop kabhi shrink nahi karega → infinite loop / TLE.
- **Off-by-one `hi = len(nums)`** — yeh "half-open" `[lo, hi)` convention hai, jisme loop `lo < hi` aur `hi = mid` hota. Convention mix mat karo — ek style pick karke usi pe stick karo.
- **Array sorted hi nahi hai** — binary search ki pehli shart sorted data hai. Unsorted pe galat answer dega chup-chaap.

## When to Use This Pattern

Jab dikhe **"sorted array"** + **"O(log n)" ya "efficient"** + "find / exists / position" → binary search socho. Generalize: jab bhi search space **monotonic** ho (ek point ke baad condition flip ho jaaye — false…false…true…true), tum binary search laga sakte ho, chahe woh literal array ho ya answer ki range ho.

## NeetCode Link

https://neetcode.io/problems/binary-search
