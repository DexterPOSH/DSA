# Target Sum

**Category:** 2-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given an integer array `nums` and an integer `target`, you must assign a `+` or `-`
sign to **every** number, then concatenate them into an expression. Return the
**number of distinct ways** to assign signs so the expression evaluates to `target`.

```
nums = [1, 1, 1, 1, 1], target = 3   ->  5
# -1+1+1+1+1, +1-1+1+1+1, +1+1-1+1+1, +1+1+1-1+1, +1+1+1+1-1
```

## Real-World Analogy

Socho tumhare paas 5 coins hain aur har coin ko ya to **left pocket** (`+`) me
daalna hai ya **right pocket** (`-`) me. Game ye hai: end me `(left ka sum) - (right ka
sum)` exactly `target` aana chahiye. Sawaal "kitne tareeke" ka hai — ginti karni hai,
koi ek answer nahi. Brute force me har coin ke 2 choices → `2^n` expressions. Lekin
dhyaan do: alag-alag sign assignments often **same running sum** pe pohochte hain. Jab
do raaste same intermediate sum pe milte hain, aage ka kaam bilkul identical hai — to
unhe alag-alag mat gino, ek hi count me merge kar do. Yahi DP ka core hai.

## Approach

**Brute force — try both signs (O(2ⁿ)):**

```python
def find_target_sum_ways(nums, target):
    def dfs(i, total):
        if i == len(nums):
            return 1 if total == target else 0
        return dfs(i + 1, total + nums[i]) + dfs(i + 1, total - nums[i])
    return dfs(0, 0)
```

Ye correct hai but exponential. State sirf `(i, total)` pe depend karta hai — to
**memoize** karo. Yahi 2-D DP hai: ek axis index `i`, dusra axis running `total`.

**Optimal — DP over `(index, running_sum)`:**

```python
def find_target_sum_ways(nums, target):
    memo = {}                              # (i, total) -> ways
    def dfs(i, total):
        if i == len(nums):
            return 1 if total == target else 0
        if (i, total) in memo:
            return memo[(i, total)]
        memo[(i, total)] = dfs(i + 1, total + nums[i]) \
                         + dfs(i + 1, total - nums[i])
        return memo[(i, total)]
    return dfs(0, 0)
```

**Bonus — subset-sum reframing.** Let `P` = subset getting `+`, `N` = subset getting
`-`. Then `sum(P) - sum(N) = target` aur `sum(P) + sum(N) = total`. Add karo →
`sum(P) = (target + total) / 2`. To problem ban gaya: *kitne subsets hain jinka sum
`(target+total)/2` hai* — classic 0/1 knapsack count, O(n·S) 1-D DP. (Agar
`target + total` odd ya negative ho → 0 ways.)

## Complexity

- **Time:** O(n · S) — `n` indices × range of reachable sums `S` (≈ `2·sum(nums)+1`).
  Memoization har `(i, total)` ko ek hi baar compute karta hai.
- **Space:** O(n · S) memo + O(n) recursion depth. Subset-sum version O(S) space.

## Common Pitfalls

- **Negative sums as keys** — running `total` negative ho sakta hai. Dict use karo, ya
  array me `sum(nums)` ka offset add karo. Plain `[0..S]` array index out-of-range dega.
- **Subset-sum parity check bhulna** — `(target + total)` agar **odd** hai ya
  `abs(target) > total` hai to answer `0` hai. Bina check ke `// 2` galat subset banata.
- **Zeros in `nums`** — `0` ko `+0` ya `-0` dono assign kar sakte ho (dono valid,
  distinct sign assignments). Pure DFS count ye automatically handle karta; agar tum
  zeros ko collapse karoge to undercount hoga.
- **Empty array edge** — `nums=[]`, `target=0` → 1 way (empty expression).

## When to Use This Pattern

"Har element pe +/- ya include/exclude jaisa **binary choice**, aur **count the ways**
to hit a target" → DP over `(index, accumulated_value)`. Cue: brute force `2^n`
dikhe aur states `(i, sum)` repeat hote dikhein → memoize. Cousins: Partition Equal
Subset Sum, Coin Change II, Last Stone Weight II — sab subset-sum family.

## NeetCode Link

https://neetcode.io/problems/target-sum
