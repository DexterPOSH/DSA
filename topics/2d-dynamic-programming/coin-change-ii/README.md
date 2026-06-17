# Coin Change II

**Category:** 2-D Dynamic Programming (counting combinations)
**Difficulty:** medium

## Problem Statement

Given an integer `amount` and an array of distinct coin denominations `coins` (unlimited supply of each), return the **number of distinct combinations** that make up `amount`. Order does **not** matter — `[1,2]` and `[2,1]` count as the **same** combination.

```
amount = 5, coins = [1, 2, 5]   ->  4
# 5 = 5
#   = 2+2+1
#   = 2+1+1+1
#   = 1+1+1+1+1
amount = 3, coins = [2]         ->  0    # can't make 3 from 2s
amount = 0, coins = [anything]  ->  1    # one way: pick nothing
```

## Real-World Analogy

Socho cashier ko exactly ₹5 ka change banana hai, paas me ₹1, ₹2, ₹5 ke unlimited sikke. Sawaal: **kitne alag tareeke** se ban sakta hai — par `2+1+1+1` aur `1+2+1+1` ko **same** ginna hai (order matter nahi karta). Order ka double-counting rokne ka trick: **ek-ek coin denomination ko poora process karo phir agli pe jao**. Yaani "pehle decide karo ₹1 sikke kitne use karne hain (har possible count), phir ₹2 ke saath sab combos, phir ₹5". Is "outer loop coins, inner loop amount" order se har combination exactly ek baar hi count hoti hai — kyunki coins ek fixed sequence me consider hote hain.

## Approach

`dp[c][a]` = pehle `c` coins use karke `amount = a` banane ke kitne tareeke. Har coin ke liye do choices: **use mat karo** (upar wali row, `dp[c-1][a]`) ya **kam se kam ek baar use karo** (`dp[c][a - coin]` — same row, kyunki coin dobara use ho sakta hai, unlimited supply).

```
dp[c][a] = dp[c-1][a]            # skip this coin
         + dp[c][a - coin]       # use this coin (if a >= coin)
```

**Base case:** `dp[*][0] = 1` — amount 0 banane ka ek tareeka (kuch mat lo).

**Full 2-D table:**
```python
def change(amount, coins):
    n = len(coins)
    dp = [[0] * (amount + 1) for _ in range(n + 1)]
    for c in range(n + 1):
        dp[c][0] = 1                              # one way to make 0
    for c in range(1, n + 1):
        coin = coins[c-1]
        for a in range(1, amount + 1):
            dp[c][a] = dp[c-1][a]                 # don't use this coin
            if a >= coin:
                dp[c][a] += dp[c][a - coin]       # use this coin (reuse allowed)
    return dp[n][amount]
```

**Space-optimized (1-D):** sirf ek row chahiye agar coins ko **outer** loop me aur amount ko **inner** (forward) loop me chalao:

```python
def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:                # outer = coins  (order fixed => no double count)
        for a in range(coin, amount + 1):   # forward => coin reused
            dp[a] += dp[a - coin]
    return dp[amount]
```

> Pattern: **2-D DP, counting combinations (unbounded knapsack)**. Critical detail: **coins outer, amount inner** counts *combinations*; flipping to *amount outer, coins inner* counts *permutations* (a different problem — Combination Sum IV).

## Complexity

- **Time:** O(n·amount) — har (coin, amount) pair ek baar.
- **Space:** O(n·amount) full table; **O(amount)** with the rolling 1-D row.

## Common Pitfalls

- **Loop order ulta karna** — amount outer + coins inner *permutations* gin leta hai (`1+2` aur `2+1` alag). Combinations chahiye to **coins outer**. Yeh #1 bug hai.
- **1-D me inner loop backward chalana** — `range(coin, amount+1)` forward chalna chahiye taaki same coin reuse ho (unbounded). Backward (0/1 knapsack ka trick) galat answer dega.
- **`dp[0] = 1` set na karna** — amount 0 ka base case 1 hai; warna poori table 0 reh jaayegi.
- **Min-coins waala "Coin Change I" se confuse** — wo *minimum count* maangta hai (`min`, `+1`), yeh *number of ways* maangta hai (`sum`). Recurrence alag hai.

## When to Use This Pattern

"Kitne tareeke / number of ways to reach a target using items with unlimited reuse, order doesn't matter" → **counting-combinations DP (unbounded knapsack)** with coins-outer loop order. Cousins: Coin Change I (min coins), Combination Sum IV (permutations → flip loops), Partition Equal Subset Sum, Target Sum. Cue: "count combinations" + "unlimited supply" + "order irrelevant".

## Practice

- Visual: open `topics/2d-dynamic-programming/coin-change-ii/visual.html`

## NeetCode Link

https://neetcode.io/problems/coin-change-ii
