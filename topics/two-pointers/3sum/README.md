# 3Sum

**Category:** Two Pointers
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, return **all unique triplets** `[a, b, c]` such
that `a + b + c == 0`. The solution set must **not contain duplicate triplets**
(order within/among triplets doesn't matter).

```
[-1, 0, 1, 2, -1, -4]  ->  [[-1, -1, 2], [-1, 0, 1]]
[0, 1, 1]              ->  []          # no triplet sums to 0
[0, 0, 0]              ->  [[0, 0, 0]]
```

## Real-World Analogy

Yeh basically **Two Sum II ka bada bhai** hai. Socho tum ek number ko "anchor"
(`a`) bana ke fix karte ho, aur fir poochte ho: "baaki array me do aise numbers
hain jinka sum `-a` ho?" — kyunki `a + b + c = 0` matlab `b + c = -a`.

Pehle array ko **sorted** kar lo (line me khada kar do, chhote se bade). Ab har
anchor ke aage wale hisse pe wahi **taraazu wala two-pointer** chalao jo Two Sum II
me tha. Sorted hone se ek aur bonus milta hai: duplicate triplets ko skip karna
trivial ho jaata — same value lagataar aaye to use chhod do.

## Approach

Pattern: **sort + fix one + two-pointer** (O(n²)). Sorting do cheezein deta hai —
two-pointer chal sakta hai, aur duplicates adjacent aa jaate hain (easy skip).

```python
def three_sum(nums):
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if nums[i] > 0:                       # sorted -> baaki sab positive, sum != 0
            break
        if i > 0 and nums[i] == nums[i - 1]:  # duplicate anchor skip
            continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:  # dup skip on left
                    l += 1
                while l < r and nums[r] == nums[r + 1]:  # dup skip on right
                    r -= 1
    return res
```

> **Brute force** teen nested loops = O(n³). Sort + two-pointer isse **O(n²)** tak
> le aata, aur duplicate handling sorting ke kaaran clean rehti.

## Complexity

- **Time:** O(n²) — outer loop O(n), andar two-pointer O(n). Sort O(n log n) chhota
  pad jaata.
- **Space:** O(1) extra (output ko chhod kar) — in-place sort, sirf pointers.

## Common Pitfalls

- **Duplicate triplets** — sabse bada trap. Anchor pe `nums[i] == nums[i-1]` skip,
  aur match ke baad dono pointers pe dup-skip — dono zaroori hain.
- **Set use karke dedupe karna** — kaam karta hai par slow aur memory-heavy;
  sorted-skip cleaner hai aur interviewer wahi chahta.
- **`nums[i] > 0` break miss karna** — sorted array me anchor positive ho gaya to
  aage kuch nahi milega; bina iske bhi correct hai par optimization chhoot jaata.
- **Pointer move karna bhulna match ke baad** — `l += 1; r -= 1` na karo to infinite
  loop / same triplet repeat.

## When to Use This Pattern

Jab "k numbers dhundo jinka sum = target" dikhe → **sort, fir (k-1) ko nested
two-pointer me reduce karo**. 3Sum = 1 fix + 2-pointer; 4Sum = 2 fix + 2-pointer.
Cue: "find triplets/quadruplets summing to X, no duplicates."

## NeetCode Link

https://neetcode.io/problems/three-integer-sum
