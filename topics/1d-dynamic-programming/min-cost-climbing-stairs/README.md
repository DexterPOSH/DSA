# Min Cost Climbing Stairs

**Category:** 1-D Dynamic Programming
**Difficulty:** easy

## Problem Statement

You are given an integer array `cost` where `cost[i]` is the cost of **stepping on** the `i`-th stair. Once you pay, you can climb **1 or 2** steps. You may start from index `0` or index `1`. Return the **minimum cost** to reach the **top** (just past the last stair).

```
cost = [10, 15, 20]            ->  15
       # start at index 1, pay 15, jump 2 steps to the top.

cost = [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]  ->  6
```

## Real-World Analogy

Socho ek seedhi ke har step pe ek toll booth lagi hai — us step pe pao rakha to utna paisa dena padega. Tum 1 ya 2 step chadh sakte ho, aur tumhe sabse upar (chhat ke uss paar) sabse saste me pahunchna hai. Har step pe khade hoke tum sochte ho: "Yahan tak main do hi tareeko se aa sakta tha — neeche wale (i-1) step se, ya uske bhi neeche (i-2) wale se. Dono raaston ka jo total ab tak ka kharcha tha, usme se **sasta wala chuno**, aur uske upar apna current toll jodo." Bas yahi har step pe dohraate jao — har step ka cheapest-arrival cost yaad rakho.

## Approach

Define `dp[i]` = **us step `i` ke top tak (i.e. step `i` paar karne tak)** ka minimum cost. Asaan formulation: `dp[i]` = step `i` par khade hone tak ka min cost.

Step `i` par do hi raaste se aaya ja sakta hai — `i-1` se (1 step) ya `i-2` se (2 step). Dono ke min lo, phir `cost[i]` jodo:
```
dp[i] = cost[i] + min(dp[i-1], dp[i-2])
```
Base cases: `dp[0] = cost[0]`, `dp[1] = cost[1]` (start dono me se kahin se ho sakta hai, no prior cost).

Top last step ke aage hai, toh answer = `min(dp[n-1], dp[n-2])` — kyunki top pe wahin se chhalaang maaroge.

**Pattern:** bottom-up 1-D DP with a `min` choice at each cell.

**Optimal — O(1) space** (har cell ko bas pichhle do chahiye):
```python
def min_cost_climbing_stairs(cost):
    a, b = 0, 0          # min cost to stand "before" steps i-2, i-1 (top = past last)
    for c in reversed(cost):
        a, b = c + min(a, b), a
    return min(a, b)
```

Aur clarity ke liye forward table version:
```python
def min_cost_climbing_stairs(cost):
    n = len(cost)
    dp = [0] * n
    dp[0], dp[1] = cost[0], cost[1]
    for i in range(2, n):
        dp[i] = cost[i] + min(dp[i-1], dp[i-2])
    return min(dp[n-1], dp[n-2])
```

## Complexity

- **Time:** O(n) — ek pass, har step pe ek `min` aur ek add.
- **Space:** O(1) two-variable version me; O(n) full table me.

## Common Pitfalls

- **"Top" ko galat samajhna** — top last index ke *aage* hai. Answer `dp[n-1]` nahi, balki `min(dp[n-1], dp[n-2])` hai, kyunki aakhri ya second-last step se chhalaang lag sakti hai.
- **Cost kab add karna** — tum step *par khade hone* ka cost dete ho, jump ka nahi. `cost[i]` ko `min(...)` ke baahar jodo, andar nahi.
- **Base case** — `dp[0]` aur `dp[1]` dono `cost` se directly aate hain (start free hai). `dp[0]=0` likh dena galat hai.
- **Greedy lalach** — har step pe sabse sasta immediate move chunna galat answer de sakta hai; pichhla mehenga step aage bahut bacha sakta hai. DP hi sahi.

## When to Use This Pattern

Jab dikhe **"minimum / maximum cost ya value to reach a goal"** aur har state limited pichhle states se reachable ho, to socho: "is state pe pahunchne ke kaun-kaun se last moves the? Har move ka best-so-far lo, phir current cost jodo." `min(...)` ya `max(...)` over predecessors + current value = recurrence. Cousins: Climbing Stairs, House Robber, Min Path Sum.

## NeetCode Link

https://neetcode.io/problems/min-cost-climbing-stairs
