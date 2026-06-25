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

**What Azure Blob Storage is:** Azure Blob Storage is Azure's object storage service for files such as images, logs, backups, and application data. A blob can be overwritten many times under the same name, but production systems often need a way to recover or inspect older contents. Versioning gives that blob a history instead of only keeping the latest bytes.

**What blob versioning is, and why it's used:** Blob versioning automatically keeps immutable previous versions when a blob is changed or deleted, with each version addressable by its version ID and associated timestamp metadata. It exists for recovery, audit, and accidental-overwrite protection: you can list the versions and choose an older one instead of losing history. If you build an "as of time `T`" read on top of that version list, you need the newest version whose timestamp is `<= T`, not necessarily an exact timestamp match.

**The mapping:** The key in `TimeMap` is the Azure Blob Storage blob name, each `(timestamp, value)` pair is a stored blob version, and `get(key, T)` is an as-of lookup. Because `set` calls append strictly increasing timestamps, the version list is already sorted; when `arr[mid][0] <= T`, save that value and search right for a later still-valid version, and when it is too new, search left. The key insight is to find the floor timestamp — the rightmost version not newer than the requested time.
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
