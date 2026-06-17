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

Socho ek bag me alag-alag weight ke items hain, aur tumhe dekhna hai ki kya tum **exactly aadha total weight** ek taraf rakh sakte ho. Agar haan, to baaki apne aap doosri taraf barabar ban jaayega. To asli sawaal ek hi hai: **"kya kisi subset ka sum exactly `total/2` ban sakta hai?"**

Ye ek **0/1 knapsack** hai — har item ya to lo (in the subset) ya chhodo, koi half-half nahi. Tum ek checklist banate ho: "kaun-kaun se exact sums achievable hain?" `0` to hamesha achievable (kuch mat lo). Phir har item ko dekhte ho aur jo nayi sums woh unlock karta hai, unhe checklist me tick kar dete ho. Agar `total/2` tick ho gaya — done.

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
