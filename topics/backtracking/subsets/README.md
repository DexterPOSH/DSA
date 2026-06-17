# Subsets

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given an array `nums` of **distinct** integers, return **all possible subsets** (the power set).
The solution set must not contain duplicate subsets; order doesn't matter.

```
[1, 2, 3]  ->  [[], [1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]   # 2^3 = 8 subsets
[0]        ->  [[], [0]]
```

> For `n` elements there are exactly `2^n` subsets — har element ke paas 2 choices:
> "andar aaun ya na aaun". That's the whole problem in one line.

## Real-World Analogy

Socho tum ghar pe pizza order kar rahe ho aur teen toppings available hain: mushroom,
olive, capsicum. Har topping ke liye ek hi sawaal — **"isko daalun ya na daalun?"**
Mushroom haan/na × olive haan/na × capsicum haan/na = 8 possible pizzas. Plain cheese
(koi topping nahi) bhi ek valid pizza hai — wahi `[]` empty subset hai. Subsets generate
karna basically har element pe yeh **include / exclude** decision lena hai, recursively.

## Approach — include/exclude decision tree

Har index `i` pe do raste lo: element ko current path me **daalo**, recurse; phir use
**hatao (backtrack)**, recurse. Jab `i` array ke end pe pahunche, current `path` ek
complete subset hai — usko answer me copy kar do.

```python
def subsets(nums):
    res, path = [], []

    def backtrack(i):
        if i == len(nums):
            res.append(path[:])      # copy — warna baad ka mutation isko bhi badlega
            return
        # choice 1: include nums[i]
        path.append(nums[i])
        backtrack(i + 1)
        # choice 2: exclude nums[i]  (BACKTRACK)
        path.pop()
        backtrack(i + 1)

    backtrack(0)
    return res
```

**Alternate "build forward" template** (zyada common interview me, aur dedup variants me
ye scale karta hai) — har call pe ek subset record karo, phir aage ke elements try karo:

```python
def subsets(nums):
    res = []
    def backtrack(start, path):
        res.append(path[:])                 # har node ek valid subset hai
        for j in range(start, len(nums)):
            path.append(nums[j])
            backtrack(j + 1, path)          # j+1 -> aage wale hi, taaki order fix rahe
            path.pop()                      # BACKTRACK
    backtrack(0, [])
    return res
```

Dono O(2^n) hi hain. Pehla template decision-tree (include/exclude) clearly dikhata hai;
doosra `start` pointer se duplicates avoid karta hai aur Subsets II me natural extend hota.

## Complexity

- **Time:** O(n · 2^n) — `2^n` subsets, aur har subset ko copy karne me up to O(n) lagta.
- **Space:** O(n) recursion depth + path (output ko count na karein to). Output khud O(n·2^n).

## Common Pitfalls

- **`res.append(path)` instead of `path[:]`** — reference daal doge, aage ka `pop` saari
  stored subsets ko corrupt kar dega. Hamesha copy karo.
- **Backtrack bhulna** — `path.append` ke baad `path.pop()` na karo to state leak hoti hai.
- **`start` ki jagah `0` se loop karna** (build-forward template me) → duplicate subsets
  jaise `[1,2]` aur `[2,1]`.
- Empty subset `[]` ko answer me include karna na bhulein — wo bhi valid subset hai.

## When to Use This Pattern

"Generate **all** combinations / power set / har possible selection" dikhe → backtracking
with include-exclude ya `start`-pointer template. Cue: `2^n` ya `n!` size ka output maanga
ja raha hai aur har element pe ek binary/positional choice hai. Cousins: Combination Sum,
Permutations, Subsets II.

## NeetCode Link

https://neetcode.io/problems/subsets
