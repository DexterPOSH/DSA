# Array Equal Partition

**Category:** Backtracking
**Source:** LinkedIn CA1 question bank (go/ca1) — levels: jr, mid · LeetCode 698
**Difficulty:** medium

## Problem Statement

Given an integer array `nums` and an integer `k`, return `True` if it's possible
to divide `nums` into **k non-empty subsets whose sums are all equal**.

```
[4, 3, 2, 3, 5, 2, 1], k = 4   ->  True    # (5)(1,4)(2,3)(2,3), each = 5
[3, 1, 1, 2, 4, 4], k = 3      ->  True    # (3,2)(1,4)(1,4), each = 5
[3, 3, 3, 3, 4], k = 4         ->  False   # can't make four equal sums
```

> Set-partition in general is NP-complete; this k-equal-sum variant is the
> classic backtracking test. No clever formula — you *search* with pruning.

## Real-World Analogy

Socho `k` doston me ek restaurant ka bill **exactly barabar** baatna hai. Har
dost ke paas ek "plate" (bucket) hai jisme uska hissa `target = total/k` tak
bharna hai. Tum items ek-ek uthate ho aur kisi dost ki plate me daalte ho. Agar
kisi item ko daalne se aage koi valid baatwara nahi banta, to **wapas le lo
(backtrack)** aur agle dost ki plate try karo. Saare items sahi fit ho gaye →
barabar baat ho gaya.

## Approach — bucket-filling backtracking

**Step 0 — feasibility shortcuts (interview me yeh pehle bolo):**
- `total = sum(nums)`. Agar `total % k != 0` → turant `False` (barabar baat
  possible hi nahi).
- `target = total // k`. Agar koi single element `> target` → `False`.
- `k <= 0` ya `k > len(nums)` → `False`.

**Step 1 — search:** `k` empty buckets banao, har ek ko `target` tak bharna hai.
Har element ke liye, use kisi bhi bucket me daalne ki koshish karo, recurse karo;
dead-end pe backtrack.

```python
def can_partition_k_subsets(nums, k):
    total = sum(nums)
    if k <= 0 or total % k != 0:
        return False
    target = total // k
    nums.sort(reverse=True)          # bada element pehle -> jaldi prune
    if nums[0] > target:
        return False
    buckets = [0] * k

    def backtrack(idx):
        if idx == len(nums):
            return True              # saare elements placed -> har bucket == target (guaranteed)
        val = nums[idx]
        for b in range(k):
            if buckets[b] + val <= target:        # capacity prune
                buckets[b] += val
                if backtrack(idx + 1):
                    return True
                buckets[b] -= val                 # BACKTRACK
            if buckets[b] == 0:                    # KEY prune: empty bucket failed ->
                break                              #   koi aur empty bucket bhi fail karega
        return False

    return backtrack(0)
```

## Why the two prunes matter (warna TLE)

1. **Capacity prune** — `buckets[b] + val <= target`: overflow hone wale bucket
   me daalo hi mat.
2. **Empty-bucket prune** — agar `val` ko ek *empty* bucket me daalne se solution
   nahi bana, to baaki *empty* buckets identical hain → unme bhi fail hoga, to
   `break`. Yeh symmetry kaat-ta hai, yahi sabse bada speedup hai.
3. **Sort descending** — bade elements pehle place karne se trees jaldi prune
   hote hain (bada element kam jagah fit hota).

> ⚠️ **Negatives:** agar array me negative numbers ho (jaise `[1,-1,2,-2]`,
> target 0), to `+val <= target` wala capacity prune galat ho jaata — tab woh
> prune hata dena padta. LeetCode 698 sirf positives deta, but interviewer yeh
> twist puchh sakta. Jaante ho yeh, to bonus points.

## Complexity

- **Time:** ~O(k · 2ⁿ) worst case; pruning isse practically tractable bana deta.
  (Alternative: bitmask DP over subsets → O(n · 2ⁿ).)
- **Space:** O(k) buckets + O(n) recursion depth.

## Common Pitfalls

1. `total % k != 0` check bhulna → galat search.
2. **Backtrack na karna** — `buckets[b] -= val` miss karoge to state corrupt.
3. Empty-bucket `break` prune chhodna → TLE on bigger inputs.
4. `nums[0] > target` (after sort) ka early-exit miss karna.
5. Element ko ek se zyada bucket me count kar dena (placement exclusive hona chahiye).

## When to Use This Pattern

"Items ko groups me baato with a constraint" / "subset(s) banao jo X satisfy
kare" → backtracking with buckets. Cousins: Sudoku, N-Queens, word-break,
combination-sum. Cue: choices × recurse × undo (backtrack).

## Practice

- Solve file: `quizzes/backtracking/test_array_equal_partition.py`
- Run: `pytest quizzes/backtracking/test_array_equal_partition.py`
- Visual: open `topics/backtracking/array-equal-partition/visual.html`
