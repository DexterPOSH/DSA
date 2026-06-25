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

**What Azure Cosmos DB is:** Azure Cosmos DB is Microsoft's globally distributed NoSQL database for applications that need low-latency reads and writes at scale. Data is stored as documents/items, and queries are charged in request units (RUs), so avoiding unnecessary reads matters. A sorted index lets Cosmos DB answer a lookup by navigating the ordered keys instead of scanning every item.

**What a range index is, and why it's used:** A Cosmos DB range index keeps comparable property values, like numbers or strings, in an ordered index structure that supports equality, range filters, and ordered queries. It exists because a point query such as `age = 42` or a range query such as `age > 42` should not burn RUs by checking every document. Since the index keys are sorted, one comparison can prove that an entire lower or upper slice cannot contain the target.

**The mapping:** The sorted `nums` array is the Azure Cosmos DB range index, `lo` and `hi` are the current slice of indexed keys, and `mid` is the key we probe. If `nums[mid]` equals the target, the document is found; if it is smaller, every key to the left is too small, so `lo = mid + 1`; if it is larger, every key to the right is too large, so `hi = mid - 1`. The key insight is that sorted order turns one comparison into permission to discard half the search space.
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
