# Climbing Stairs

**Category:** 1-D Dynamic Programming
**Difficulty:** easy

## Problem Statement

You are climbing a staircase with `n` steps. Each time you can climb **either 1 or 2 steps**. In how many **distinct ways** can you reach the top?

```
n = 2  ->  2     # (1+1), (2)
n = 3  ->  3     # (1+1+1), (1+2), (2+1)
n = 5  ->  8
```

## Real-World Analogy

Socho tum ek seedhi ke sabse upar (step `n`) pe khade ho aur peeche mudke soch rahe ho: "Main yahan tak pahuncha kaise?" Sirf do hi tareeke the — ya to main step `n-1` pe tha aur ek chhoti chhalaang (1 step) maari, ya main step `n-2` pe tha aur badi chhalaang (2 step) maari. Bas. Koi teesra raasta hai hi nahi.

Toh `n` tak pahunchne ke total tareeke = (`n-1` tak pahunchne ke tareeke) + (`n-2` tak pahunchne ke tareeke). Yeh seedha-saadha Fibonacci hai — har step apne pichhle do steps ka jod hai. DP ki poori jaan yahi soch hai: bada sawaal apne se chhote sawaalon ke jawaab par tika hota hai.

## Approach

Define `dp[i]` = step `i` tak pahunchne ke distinct ways.

Recurrence:
```
dp[i] = dp[i-1] + dp[i-2]
```
Base cases: `dp[0] = 1` (already at top, ek hi "khaali" way), `dp[1] = 1`.

**Pattern:** bottom-up 1-D DP (Fibonacci). Pehle chhote steps solve karo, aage badhte jao.

Naive recursion (`climb(n-1) + climb(n-2)`) exponential O(2ⁿ) hai kyunki same subproblems baar-baar compute hote hain. DP table un answers ko ek baar compute karke yaad rakhti hai.

**Optimal — sirf do variables se** (full array ki zaroorat nahi, kyunki har step ko bas pichhle do chahiye):
```python
def climb_stairs(n):
    one, two = 1, 1          # ways to reach i-1 and i-2
    for _ in range(n):
        one, two = one + two, one
    return one
```

Aur clarity chahiye to full table version:
```python
def climb_stairs(n):
    if n <= 1:
        return 1
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

## Complexity

- **Time:** O(n) — har step ek baar fill hota hai, constant kaam per step.
- **Space:** O(1) two-variable version me — sirf pichhle do values yaad rakhne hain. O(n) agar poora table rakho.

## Common Pitfalls

- **Base case galat** — `dp[0]` ko 0 maan lena. `n=0` pe ek (khaali) way hota hai, isliye `dp[0] = 1`. Iske bina poori sequence ek shift ho jaati hai.
- **Naive recursion bina memoization** — TLE on bade `n`. Same subproblem (e.g. `climb(3)`) hazaaron baar compute hota hai.
- **Off-by-one** — array size `n+1` rakho aur `dp[n]` return karo, `dp[n-1]` nahi.
- **Ise permutation/combinatorics formula se solve karne ki koshish** — order matters (1+2 ≠ 2+1), toh seedha DP/Fibonacci hi cleanest hai.

## When to Use This Pattern

Jab dikhe **"kitne distinct ways / paths ho sakte hain"** aur har move limited choices (1 step ya 2 step) deta ho, to socho: "current state pe pahunchne wale last moves kaun-kaun se the?" Har last-move ke options ko jod do → recurrence ban jaata hai. Yeh Fibonacci-style 1-D DP ka classic signature hai. Cousins: Min Cost Climbing Stairs, House Robber, Decode Ways.

## NeetCode Link

https://neetcode.io/problems/climbing-stairs
