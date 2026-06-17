# Time Based Key Value Store

**Category:** Binary Search
**Difficulty:** medium

## Problem Statement

Design a key-value store where each key can have **multiple values at different timestamps**. Implement two operations:

- `set(key, value, timestamp)` — store `value` for `key` at the given `timestamp`.
- `get(key, timestamp)` — return the value that was set for `key` at the **largest stored timestamp `<= timestamp`**. If none exists, return `""`.

Timestamps for a given key are strictly increasing across `set` calls.

```
set("foo", "bar", 1)
get("foo", 1)   ->  "bar"      # exact match
get("foo", 3)   ->  "bar"      # nothing at 3, fall back to ts=1
set("foo", "baz", 4)
get("foo", 4)   ->  "baz"      # exact match
get("foo", 0)   ->  ""         # nothing <= 0
```

## Real-World Analogy

Socho ek **git commit history** hai ek file ki. Har commit ka ek timestamp hai aur ek snapshot. Koi pooche "is file ka content time `T` pe kya tha?" — tum exact `T` wala commit nahi dhoondhte, balki **`T` se pehle ka sabse recent commit** dhoondhte ho (kyunki wahi version us waqt live tha). Commits already time order me hain, to poori history scan karne ki zaroorat nahi — seedha **binary search** se "`T` se chhota-ya-barabar wala latest" pe jump kar jao.

## Approach

Key insight: kyunki timestamps **increasing order me append hote hain**, har key ki list automatically sorted-by-timestamp rehti hai. To `get` ek **"rightmost value with ts <= target"** binary search ban jaata hai — yeh classic *upper bound* / "floor" search hai.

```python
class TimeMap:
    def __init__(self):
        self.store = {}                      # key -> list of [timestamp, value]

    def set(self, key, value, timestamp):
        self.store.setdefault(key, []).append([timestamp, value])

    def get(self, key, timestamp):
        arr = self.store.get(key, [])
        lo, hi, res = 0, len(arr) - 1, ""
        while lo <= hi:
            mid = (lo + hi) // 2
            if arr[mid][0] <= timestamp:
                res = arr[mid][1]            # candidate; try to find a later one
                lo = mid + 1
            else:
                hi = mid - 1
        return res
```

Narration: jab `arr[mid][0] <= timestamp` ho, ye ek **valid candidate** hai — usse `res` me yaad rakho, phir `lo = mid + 1` karke aur **bada (lekin still <= target)** timestamp dhoondho. Jab `arr[mid][0] > timestamp` ho, ye bahut aage hai → `hi = mid - 1`. Loop khatam, `res` me last valid value bachti hai. (`bisect_right` se bhi ho jaata, but explicit loop interview-friendly hai.)

## Complexity

- **Time:** `set` → O(1) amortized (sirf append). `get` → O(log n) per key, n = us key ke entries.
- **Space:** O(n) total entries across all keys.

## Common Pitfalls

- **Linear scan from the end** — tempting, but O(n) per `get`; interviewer O(log n) chahta hai. Binary search use karo.
- **Candidate yaad na rakhna** — jab `arr[mid][0] <= timestamp` mile to value ko `res` me store karna *zaroori* hai before moving right; warna last valid answer kho doge.
- **`<=` vs `<` confusion** — exact timestamp match bhi valid answer hai (`get("foo",1)` after `set(...,1)` returns "bar"), to condition `<=` honi chahiye.
- **Timestamps sorted maan lena bina justify kiye** — yeh isiliye sorted hain kyunki problem guarantee deta hai increasing `set` order. Agar wo guarantee na ho, har `set` pe `bisect.insort` karna padta.
- **Empty / missing key** — `get` on a never-set key should return `""`, na ki crash.

## When to Use This Pattern

Jab data **timestamp/version ordered** ho aur "as-of time T" / "floor of T" query karni ho → binary search for *rightmost element <= target*. Yeh "upper bound minus one" pattern hai. Cue: "largest value not exceeding X", "version control as-of", "snapshot at time T", "ceiling/floor in sorted list". Cousins: Search Insert Position, Find First/Last Position, any `bisect`-shaped query.

## Practice

- Visual: open `topics/binary-search/time-based-key-value-store/visual.html`

## NeetCode Link

https://neetcode.io/problems/time-based-key-value-store
