# Partition Equal Subset Sum

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given an integer array `nums` (positive integers), return `True` if you can partition it into **two subsets whose sums are equal**.

```
[1, 5, 11, 5]   ->  True    # [1, 5, 5] and [11], both sum to 11
[1, 2, 3, 5]    ->  False   # total = 11, odd -> impossible
[2, 2, 1, 1]    ->  True    # [2, 1] and [2, 1], both sum to 3
```

## Real-World Analogy

**What Azure Resource Manager is:** Azure Resource Manager is Azure's control plane for deploying and managing resources consistently. It processes templates and resource operations so teams can plan infrastructure changes as repeatable deployments. A planning step may need to check whether a set of compute reservations can be balanced across regions.

**What Azure capacity-reservation balancing is, and why it's used:** Azure Capacity Reservations reserve VM capacity in a chosen region or zone so workloads have capacity available when needed. When planning paired-region resilience, teams may want the reserved capacity split evenly so failover or active-active deployments stay balanced. The feasibility question is not every possible grouping; it is whether one subset can reach exactly half the total capacity.

**The mapping:** Each reservation size is a number, half the total is the target regional capacity, and `dp[s]` records whether sum `s` is reachable after considering each reservation once. Scanning sums backward is the ARM planning guardrail that prevents reusing the same reservation twice in one pass. The key insight is that an equal split exists exactly when the half-total subset sum is reachable.

## Approach

**Step 0 — feasibility:** agar `total` odd hai, do equal halves impossible → turant `False`.

**DP:** `target = total // 2`. Boolean `dp[s]` = "kya sum `s` achievable hai kuch subset se?". `dp[0] = True` (empty subset). Har number `num` ke liye, har achievable sum `s` ko `s + num` reachable bana do.

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True                          # khaali subset -> sum 0
    for num in nums:
        # IMPORTANT: ulta (high se low) chalo taaki ek num do baar use na ho
        for s in range(target, num - 1, -1):
            if dp[s - num]:
                dp[s] = True
        if dp[target]:                    # jaldi exit
            return True
    return dp[target]
```

Pattern: **0/1 knapsack as 1-D boolean reachability DP**. 2-D table (`dp[i][s]`) ko ek rolling 1-D row me squeeze karte hain — par tabhi sahi jab inner loop **reverse** (high→low) chale.

## Complexity

- **Time:** O(n · target) = O(n · total/2) — pseudo-polynomial (sum ke magnitude pe depend).
- **Space:** O(target) — single rolling boolean row.

## Common Pitfalls

- **Inner loop forward chalana** — agar `s` low→high gaya, to ek hi `num` ek hi pass me multiple baar count ho jaata (woh unbounded knapsack ban jaata, 0/1 nahi). **Reverse** (`target` se `num` tak) chalna mandatory hai 1-D version me.
- **Odd-total check bhulna** — odd total pe equal split impossible; ye early-exit poora kaam bacha deta.
- **`dp[0] = True` na set karna** — base case; iske bina koi sum unlock hi nahi hoga.
- **Subset reconstruct karne ki koshish** — sirf boolean possibility chahiye; actual subset nikalna ho to alag tracking lagega.
- **Negatives / zeros** — classic version positive integers maanta hai; negatives ho to target/range logic badalna padta.

## When to Use This Pattern

"Items ko do barabar (ya target-sum wale) groups me baato" / "kya koi subset exact sum banata hai?" → **subset-sum / 0/1 knapsack boolean DP**. Cousins: target-sum, coin-change (count/min), last-stone-weight-II. Cue: "har item ek binary choice (lo/chhodo), aur ek numeric target hit karna hai."

## NeetCode Link

https://neetcode.io/problems/partition-equal-subset-sum
