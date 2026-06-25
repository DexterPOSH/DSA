# Best Time to Buy and Sell Stock with Cooldown

**Category:** 2-D Dynamic Programming (state-machine DP)
**Difficulty:** medium

## Problem Statement

You are given an array `prices` where `prices[i]` is the stock price on day `i`. You may complete **as many transactions as you like** (buy then sell), but with two rules:

- You can hold **at most one share** at a time (must sell before buying again).
- After you **sell**, you must **cooldown one day** — you cannot buy on the very next day.

Return the **maximum profit**.

```
prices = [1, 2, 3, 0, 2]   ->  3
# buy@1, sell@2 (profit 1), cooldown day, buy@0, sell@2 (profit 2)  => 3
```

## Real-World Analogy

**What Azure Monitor autoscale for Azure VM Scale Sets is:** Azure Monitor autoscale watches metrics like CPU, queue length, or custom signals and automatically changes the instance count of an Azure VM Scale Set. It is meant to keep enough capacity online for demand without leaving extra VMs running when traffic drops. Each evaluation is like one trading day: the controller decides whether to keep capacity allocated, release it, or stay idle.

**What autoscale cooldown is, and why it's used:** Autoscale rules include a cooldown period after a scaling action so Azure has time to provision or remove instances and let metrics settle before making another decision. Without cooldown, a scale set can flap — scaling in, immediately scaling out, then scaling in again — because the next metric sample may still reflect the previous state. The cooldown exists to enforce a temporary "no immediate re-entry" rule after releasing capacity.

**The mapping:** Buying/holding stock is like having VM capacity allocated, selling is like scaling in and realizing savings, and the cooldown state is the forced waiting period before capacity can be allocated again. The DP keeps separate values for holding, just-sold/cooling-down, and resting because the best future action depends on which operational state Azure is in, not just on the current profit number. The key insight is that selling creates profit but also creates a constraint, so the algorithm must model state transitions explicitly instead of greedily buying right after every sale.

## Approach

Teen running states, har din update. Maan lo aaj din `i`, price `p`:

- `hold` = aaj share pakde hue best profit
- `sold` = aaj bech ke (so kal cooldown) best profit
- `rest` = aaj free, share nahi (cooldown over) best profit

Transitions (kal ke states se):
- `hold  = max(hold_prev, rest_prev - p)`   → pakde raho, ya REST se aaj khareedo
- `sold  = hold_prev + p`                    → jo pakde tha use aaj becho
- `rest  = max(rest_prev, sold_prev)`        → free raho, ya kal ka cooldown khatam

```python
def max_profit(prices):
    if not prices:
        return 0
    hold, sold, rest = float('-inf'), 0, 0     # day 0: can't have sold/rested with profit
    for p in prices:
        prev_sold = sold
        sold = hold + p                         # sell today
        hold = max(hold, rest - p)              # keep holding, or buy from rest
        rest = max(rest, prev_sold)             # stay resting, or finish cooldown
    return max(sold, rest)                       # never end while still holding
```

> Pattern: **state-machine DP**. Conceptually `dp[i][state]` — har din × har state ka best profit. Yahan 3 states ko 3 scalars me roll kar diya (O(1) space), lekin soch wahi "2-D table over days × states" wali hai.

## Complexity

- **Time:** O(n) — ek pass over prices, har din O(1) transitions.
- **Space:** O(1) — sirf teen running variables (full `dp[n][3]` table O(n) hoti, par zaroorat nahi).

## Common Pitfalls

- **`hold` ko 0 se initialize karna** — galat. Day 0 pe "share pakda hua" matlab paisa kharch hua hai, to `hold` ko `-inf` (ya `-prices[0]`) se shuru karo, warna phantom free share mil jaata hai.
- **Cooldown logic skip karna** — buy seedha `sold_prev` se mat karo; `rest` (cooldown-cleared) state se hi buy hona chahiye. Yeh extra `rest` state hi cooldown enforce karta hai.
- **Update order me variable overwrite** — `sold = hold + p` ko `hold` update hone se *pehle* karo, aur `rest` ke liye `prev_sold` save karo. Order galat hua to same-day stale values use ho jaati hain.
- **Holding state me end karna** — answer `max(sold, rest)` hai, `hold` include mat karo — share haath me reh gaya to wo realized profit nahi.

## When to Use This Pattern

Jab problem me **discrete states/modes** ho aur har step pe state transitions ho ("hold/sold/rest", "even/odd", "locked/unlocked", "buying/selling with k transactions") — to **state-machine DP** socho: har step pe har state ka best track karo. Cousins: poori Buy-Sell-Stock family (II/III/IV, with fee), paint-house, string-DP with modes. Cue: "next step ka choice current 'mode' pe depend karta hai".

## Practice

- Visual: open `topics/2d-dynamic-programming/best-time-to-buy-and-sell-stock-with-cooldown/visual.html`

## NeetCode Link

https://neetcode.io/problems/buy-and-sell-crypto-with-cooldown
