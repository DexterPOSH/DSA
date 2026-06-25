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

**What Azure landing-zone catalogs are:** Azure landing-zone catalogs collect reusable ARM or Bicep modules for standard environments, such as networking, Private Endpoints, monitoring, and security baselines. They help teams assemble consistent Azure deployments without rebuilding the same resource patterns each time. Sometimes a catalog contains equivalent entries that produce the same resource shape.

**What duplicate-equivalent module handling is, and why it's used:** Duplicate-equivalent modules can appear because two teams publish the same option, two versions are temporarily identical, or two catalog entries represent separate but matching capacity. For enumeration, choosing the first identical Private Endpoint module or the second at the same decision level would create the same ARM deployment footprint. Sorting the catalog and skipping same-level duplicates removes repeated footprints, while still allowing a branch that intentionally includes multiple copies when the input contains them.

**The mapping:** Each item is an Azure landing-zone module option, sorted so equivalent modules sit next to each other. Backtracking chooses an option, recurses past it, then pops it; when a duplicate appears as a sibling choice at the same depth, it is skipped because that deployment shape was already explored. The key insight is to skip duplicates only among sibling branches, not down a chosen path, so the result set is unique without losing valid multi-copy selections.

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
