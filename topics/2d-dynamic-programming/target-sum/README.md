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

**What Azure Synapse Mapping Data Flow is:** Azure Synapse Mapping Data Flow is a visual, Spark-backed data transformation feature for building ETL pipelines without hand-writing all the distributed processing code. It lets teams define a sequence of transformations that derive columns, aggregate values, and route records through different logic. In this analogy, each transformation contributes a capacity delta to a running resource-balance column.

**What branching budget-delta transformation is, and why it's used:** A planning flow may need to evaluate scenarios where the same Azure resource delta can be treated as an increase or a decrease, such as capacity added versus capacity offset elsewhere. Branching each step into `+delta` and `-delta` explores those alternatives, while grouping by the running balance merges scenarios that become equivalent. This avoids carrying every full expression forward when only the current balance matters for the remaining transformations.

**The mapping:** Each number is an Azure Synapse transformation delta, each row is one more processed delta, and each column is a possible running balance. For every existing count, the DP sends that count to both `sum + num` and `sum - num`, adding counts together when different histories land on the same balance. The key insight is that many sign assignments share the same future once their running sum matches, so the algorithm counts states by balance instead of enumerating every expression separately.

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
