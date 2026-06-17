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

Socho tum ek trader ho aur har subah tum exactly **teen me se ek** mood me ho:
- **HOLD** — tumhare paas share hai, abhi pakde hue ho.
- **SOLD** — aaj hi becha hai, ab kal **mandatory chhutti** (cooldown), kuch nahi khareed sakte.
- **REST** — tumhare paas share nahi hai aur tum free ho (cooldown bhi nahi) — aaj khareed sakte ho.

Har din ka mood kal ke mood pe depend karta hai — yeh ek **state machine** hai. "Aaj HOLD me hoon" do tareeke se ho sakta hai: ya kal bhi HOLD tha (pakde rakha), ya kal REST tha aur aaj khareed liya. Bas har state ke liye best profit track karte chalo, din-ba-din. Ant me **bina share ke** (SOLD ya REST) wala state hi max profit dega — share haath me pakde reh jaana to loss hai.

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
