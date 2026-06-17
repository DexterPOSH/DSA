# Permutations

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given an array `nums` of **distinct** integers, return **all possible permutations** (every
ordering). Order of the permutations in the output doesn't matter.

```
[1, 2, 3]  ->  [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]   # 3! = 6
[0, 1]     ->  [[0,1], [1,0]]
```

> `n` distinct elements ke `n!` permutations hote hain — pehli position ke liye `n` choices,
> agli ke liye `n-1`, aur aage. Subsets se key difference: yahan **order maayne rakhta hai**
> aur har permutation me **saare** elements aate hain.

## Real-World Analogy

Socho ek race me 3 dhaavak hain — A, B, C — aur tumhe **podium ke saare possible orders**
(gold-silver-bronze) likhne hain. Gold ke liye 3 me se koi bhi → maan lo A. Ab silver ke liye
sirf bache hue do (B ya C) → maan lo B. Bronze automatically C. Ek arrangement complete.
Phir tum **wapas jaate ho (backtrack)**: silver pe B hata ke C try karo, aur aise hi gold
badal ke poora dobara. Har bar tum ek "used" set rakhte ho taaki ek hi dhaavak do positions
pe na aa jaaye.

## Approach — pick-an-unused-element backtracking

Ek `used` boolean array (ya set) rakho. Har recursion level pe, **jo abhi tak use nahi hua**
har element ko current position pe try karo: usko `path` me daalo + `used` mark karo, recurse,
phir undo (backtrack). Jab `path` ki length `n` ho jaaye → ek full permutation mila.

```python
def permute(nums):
    res, path = [], []
    used = [False] * len(nums)

    def backtrack():
        if len(path) == len(nums):
            res.append(path[:])              # full ordering -> record copy
            return
        for i in range(len(nums)):
            if used[i]:
                continue                      # already placed -> skip
            used[i] = True
            path.append(nums[i])
            backtrack()
            path.pop()                        # BACKTRACK
            used[i] = False                   # un-mark

    backtrack()
    return res
```

> **Swap trick (O(1) extra space):** `used` array ki jagah array ko in-place swap karke
> permute kar sakte ho — `for i in range(start, n): swap(start,i); rec(start+1); swap(start,i)`.
> Same complexity, kam memory, but `used`-version padhna/samajhna aasaan.

## Complexity

- **Time:** O(n · n!) — `n!` permutations, har ek ko O(n) me build/copy karte.
- **Space:** O(n) recursion depth + `used` + path (output excluded).

## Common Pitfalls

- **`used` ko un-mark na karna** (`used[i] = False` bhulna) → galat results, kuch permutations
  gayab.
- **`path.pop()` aur `used[i]=False` ka order/jodi** miss karna → state corruption.
- Subsets wale `start` pointer ka idea yahan **galat** hai — permutations me har level pe
  poore array se choose karna hai (sirf already-used skip karte), `start` se nahi.
- **`path[:]` copy** na karna → reference bug.

## When to Use This Pattern

"Saare orderings / arrangements / sequences" dikhe (jahan order maayne rakhta aur sab elements
use hote) → backtracking with a `used` set. Cue: output size `n!`. Cousins: N-Queens
(placement orderings), string anagrams, Permutations II (with duplicates → sort + skip).

## NeetCode Link

https://neetcode.io/problems/permutations
