# House Robber

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

You are a robber planning to rob houses along a street. `nums[i]` is the money in house `i`. The catch: **adjacent houses have connected alarms** — robbing two adjacent houses on the same night triggers the police. Return the **maximum money** you can rob without ever robbing two adjacent houses.

```
nums = [1, 2, 3, 1]        ->  4     # rob house 0 and 2 -> 1 + 3 = 4
nums = [2, 7, 9, 3, 1]     ->  12    # rob 0, 2, 4 -> 2 + 9 + 1 = 12
```

## Real-World Analogy

Socho tum ek chor ho aur ek gali me ghar-ghar loot rahe ho, par har do bagal wale gharon ke alarm aapas me jude hain. Toh har ghar par tumhare paas do hi choices hain: **"is ghar ko loot lo"** (par phir pichhle bagal wale ghar ko chhodna padega) ya **"is ghar ko chhod do"** (toh pichhle ghar tak ki best loot bachi rahegi).

Har ghar par tum yeh do options ka **max** lete ho:
- **Loot:** is ghar ka paisa + do-ghar-pehle tak ki best loot (`nums[i] + dp[i-2]`)
- **Skip:** ekdam pichhle ghar tak ki best loot (`dp[i-1]`)

Yeh "take it or leave it" choice DP ka asli flavor hai — har step pe do raaste, dono ka best yaad rakho, aage badho.

## Approach

Define `dp[i]` = house `i` tak (inclusive) consider karte hue maximum loot.

Recurrence:
```
dp[i] = max(dp[i-1], nums[i] + dp[i-2])
```
- `dp[i-1]` → current house skip kiya.
- `nums[i] + dp[i-2]` → current house looto, isliye `i-1` skip, `i-2` tak ka best add.

Base cases: `dp[0] = nums[0]`, `dp[1] = max(nums[0], nums[1])`.

**Pattern:** "take vs skip" 1-D DP. Answer = `dp[n-1]`.

**Optimal — O(1) space** (har cell ko bas pichhle do values chahiye):
```python
def rob(nums):
    rob2, rob1 = 0, 0        # dp[i-2], dp[i-1]
    for n in nums:
        take = n + rob2
        rob2, rob1 = rob1, max(rob1, take)
    return rob1
```

Full table version for clarity:
```python
def rob(nums):
    if len(nums) == 1:
        return nums[0]
    dp = [0] * len(nums)
    dp[0], dp[1] = nums[0], max(nums[0], nums[1])
    for i in range(2, len(nums)):
        dp[i] = max(dp[i-1], nums[i] + dp[i-2])
    return dp[-1]
```

## Complexity

- **Time:** O(n) — har house pe ek `max` of two options.
- **Space:** O(1) two-variable version me; O(n) full table me.

## Common Pitfalls

- **`dp[i-2]` ki jagah `dp[i-1]` add karna** jab current house loota — yeh adjacency rule tod deta. Looto to do-pehle wale tak hi jaa sakte ho.
- **Base case `dp[1]`** ko `nums[1]` maan lena — actually `max(nums[0], nums[1])` hai, kyunki pehle do me se bada chunna better.
- **Empty ya single-element array** handle na karna — `len(nums)==1` ka early return rakho.
- **Greedy "har doosra ghar loot lo"** — galat. `[2, 1, 1, 2]` me alternate lena 4 deta, par best bhi 4 hai... lekin `[2, 7, 9, 3, 1]` me blind-alternate galat ho sakta. Hamesha `max` of two options DP chahiye.

## When to Use This Pattern

Jab dikhe **"max/min subset value with an adjacency / no-two-consecutive constraint"** — har element par "include vs exclude" choice ho aur include karne pe pichhla element forbidden ho — to socho House Robber. Recurrence hamesha `max(skip = dp[i-1], take = val + dp[i-2])`. Cousins: House Robber II (circular), Delete and Earn, max sum of non-adjacent elements.

## NeetCode Link

https://neetcode.io/problems/house-robber
