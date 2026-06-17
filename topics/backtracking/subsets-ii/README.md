# Subsets II

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given an integer array `nums` that **may contain duplicates**, return all possible
**unique subsets** (the power set). The solution set must not contain duplicate subsets.

```
[1, 2, 2]  ->  [[], [1], [1,2], [1,2,2], [2], [2,2]]      # NOT two copies of [2] / [1,2]
[0]        ->  [[], [0]]
```

> Plain Subsets ka problem yeh hai ki agar `nums` me duplicate values hain, to naive power
> set me same subset do baar aa jaata hai (dono `2`s ko alag-alag treat karne se). Yahan ka
> asli kaam: **duplicates ko deduplicate** karna.

## Real-World Analogy

Socho tum guests ke liye gift-bags bana rahe ho aur tumhare paas do **bilkul identical** blue
pens hain (aur ek red pen). "Ek blue pen waala bag" ek hi tarah ka bag hai — chahe tumne
pehla blue uthaaya ho ya doosra, guest ko farak nahi padta. To same multiset ko ek hi baar
count karna hai. Trick: identical items ko **side-by-side rakho (sort)**, aur jab ek hi level
pe doosra identical item dobara uthane lago, to **skip** kar do — kyunki uska subset pehle
hi ban chuka.

## Approach — sort + skip-duplicates-at-same-level

Pehle `nums.sort()` — isse equal values adjacent ho jaate. Phir build-forward template:
har node ek valid subset hai. Loop ke andar, agar current element pichle ke **equal** hai
**aur wo same loop iteration-level pe** hai (`i > start`), to use skip karo.

```python
def subsets_with_dup(nums):
    nums.sort()                              # duplicates ko adjacent lao
    res = []

    def backtrack(start, path):
        res.append(path[:])                  # har node ek unique subset
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                      # SKIP: same level pe duplicate -> dup subset
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()                        # BACKTRACK

    backtrack(0, [])
    return res
```

> **`i > start` kyun, `i > 0` kyun nahi?** Hum duplicate ko sirf **same recursion level**
> pe skip karte. `i == start` waala pehla duplicate lena ZAROORI hai (warna `[2,2]` jaise
> valid subsets ban hi nahi paayenge). Sirf jab same level pe duplicate **dobara** dikhe
> (`i > start`) tabhi skip — yeh sibling branches ke beech ka duplicate kaat-ta hai, parent→child
> wala nahi.

## Complexity

- **Time:** O(n · 2^n) worst case (all distinct → poora power set). Duplicates honge to
  unique subsets kam, search bhi proportionally chhota.
- **Space:** O(n) recursion depth + path. Output alag.

## Common Pitfalls

- **Sort bhulna** → duplicates adjacent nahi honge, `nums[i]==nums[i-1]` check kaam hi nahi
  karega, duplicate subsets aa jaayenge.
- **`i > start` ki jagah `i > 0`** likhna → valid `[2,2]` type subsets bhi skip ho jaate.
- **Set-of-tuples se dedup karna** kaam to karta but slow/hacky — interviewer ko clean skip
  logic chahiye.
- **`path[:]` copy** na karna → reference bug (har problem me same).

## When to Use This Pattern

"All unique subsets/combinations **with duplicate inputs**" dikhe → **sort + `i > start`
skip**. Yeh exact dedup trick Combination Sum II aur Permutations II me bhi aata hai. Cue:
input me repeated values + "no duplicate results".

## NeetCode Link

https://neetcode.io/problems/subsets-ii
