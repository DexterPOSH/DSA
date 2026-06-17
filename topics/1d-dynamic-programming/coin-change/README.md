# Coin Change

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given an array `coins` of distinct coin denominations and an integer `amount`, return the **fewest number of coins** needed to make up that amount. You may use each coin **unlimited times**. If the amount cannot be made, return `-1`.

```
coins = [1, 2, 5], amount = 11   ->  3      (5 + 5 + 1)
coins = [2], amount = 3          ->  -1     (can't make odd amount with 2s)
coins = [1], amount = 0          ->  0      (zero coins for zero amount)
```

## Real-World Analogy

Socho tum ek **cashier ho aur exact change dena hai** — minimum coins me. Tumhare paas har denomination ki **unlimited supply** hai (yeh "unbounded" ka matlab — ek coin baar-baar use kar sakte ho, unlike a regular knapsack jahan har item ek hi baar).

Ab smart cashier kya karta hai? Wo chhote amounts ka jawab pehle nikal leta hai aur likh ke rakh leta hai. `amount = 11` ka best change nikalne ke liye wo sochta: "Agar main ek `5` ka coin abhi de doon, to bacha `6` — aur `6` ka best main pehle se jaanta hoon. Ya ek `2` doon to bacha `9`... har coin try karo, jo pichhla-best sabse chhota hai usme +1." Yeh **bottom-up table building** hai — har sub-amount ka answer ek baar compute karke reuse karo.

## Approach

**Pattern: Unbounded Knapsack / 1-D DP over amounts.** Let `dp[a]` = minimum coins to make amount `a`. We build it from `0` up to `amount`.

- `dp[0] = 0` — zero amount ke liye zero coins. Base case.
- `dp[a]` = `1 + min(dp[a - c])` over every coin `c` where `a - c >= 0`. (Ek coin `c` use karo, baaki `a-c` ka best already pata hai.)
- Initialize all other `dp[a] = infinity` (abhi tak unreachable). End me agar `dp[amount]` abhi bhi infinity hai → `-1`.

```python
def coinChange(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0                              # base: 0 coins for amount 0

    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1      # use coin c, reuse dp[a-c]

    return dp[amount] if dp[amount] != float('inf') else -1
```

**Why unbounded (not 0/1)?** Notice the inner loop lets the same coin `c` be picked again for a larger amount — `dp[a]` pulls from `dp[a-c]`, which itself may have used `c`. Coin reuse is built in. (In 0/1 knapsack you'd iterate amounts in reverse to *prevent* reuse — here we *allow* it.)

> **Greedy doesn't work** — "always take the biggest coin" fails. E.g. `coins=[1,3,4], amount=6`: greedy gives `4+1+1=3`, but optimal is `3+3=2`. Isiliye DP zaroori hai.

## Complexity

- **Time:** O(amount × len(coins)) — har amount ke liye saare coins try karte hain.
- **Space:** O(amount) — ek 1-D dp array. (Already optimal; isse kam nahi ho sakta yahan.)

## Common Pitfalls

- **Greedy lagana** — sabse common galti. Greedy minimum coins guarantee nahi karta (counter-example upar). Always DP.
- **`dp[0] = 0` bhulna** — yeh base case hai. Agar isse miss karoge to poora table galat seed hoga.
- **Unreachable = infinity** — jo amounts ban hi nahi sakte (jaise `coins=[2], amount=3`) unke liye `dp[a]` infinity rehna chahiye, aur final answer `-1`. `inf` check zaroori.
- **`-1` return karna bhulna** — `dp[amount] == inf` case handle na karoge to galat (huge) number return hoga.
- **Coin > amount** — `if c <= a` guard zaroori, warna negative index access ho jaayega.
- **"Number of ways" se confuse hona** — yeh problem *minimum coins* maangti, *number of combinations* nahi. Combinations wala variant (Coin Change II) ka recurrence alag hota (`dp[a] += dp[a-c]`).

## When to Use This Pattern

"Minimum/maximum items to reach a target, items reusable" → **unbounded knapsack 1-D DP**. Cue: ek target value banani hai chote pieces se, har piece unlimited baar, aur optimize (min/max count) karna hai. Cousins: **Coin Change II** (count ways), **Combination Sum IV**, **Perfect Squares**. Greedy fail kare → DP socho.

## NeetCode Link

https://neetcode.io/problems/coin-change
