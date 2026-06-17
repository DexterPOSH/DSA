# Best Time to Buy and Sell Stock

**Category:** Sliding Window
**Difficulty:** easy

## Problem Statement

You're given an array `prices` where `prices[i]` is the price of a stock on day `i`.
You want to **buy on one day and sell on a later day**. Return the maximum profit
you can make. If no profit is possible, return `0` (you simply don't trade).

```
[7, 1, 5, 3, 6, 4]  ->  5    # buy at 1 (day 1), sell at 6 (day 4): 6 - 1 = 5
[7, 6, 4, 3, 1]     ->  0    # prices only fall — best move is to not trade
```

> Key constraint: you must **buy before you sell** — selling on an earlier day than
> you bought is not allowed.

## Real-World Analogy

Socho tum ek shopkeeper ho aur har din ka stock-rate ek diary me note kar rahe ho.
Tumhe **sabse sasta din yaad rakhna hai jo ab tak guzar chuka hai** ("ab tak ka
lowest"), aur har naye din pe sochna hai: "agar main aaj bechu, to us sabse saste
din wale rate pe khareed kar kitna profit hota?" Tum future me nahi jhaank sakte —
sirf aaj tak ka sabse sasta din pata hai. Diary me ek hi cheez track karo: **ab tak
ka minimum price**, aur uske against har din ka profit compute karte raho.

## Approach

Ye ek **single-pointer sliding window** jaisa hai: `buy` pointer hamesha ab tak ke
sabse saste din pe rehta hai, aur `sell` pointer (current day) aage badhta jaata hai.
Window `[buy, sell]` ko hum tab "shrink" karte hain jab ek naya, sasta din mil jaata
hai — buy ko wahi le aate hain.

Do cheezein track karo: `min_price` (ab tak ka sabse sasta) aur `max_profit`.

```python
def max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        if price < min_price:        # naya sasta din -> yahin se kharidna better
            min_price = price
        else:                        # aaj bech kar dekho profit
            max_profit = max(max_profit, price - min_price)
    return max_profit
```

Ek hi pass me, har din pe: ya to `min_price` update karo, ya us min ke against
profit nikaalo. Future dekhne ki zaroorat nahi — kyunki jis bhi din bechoge, uske
pehle ka cheapest already paas hai.

## Complexity

- **Time:** O(n) — ek hi loop, har element ek baar.
- **Space:** O(1) — sirf do scalars (`min_price`, `max_profit`), koi extra structure nahi.

## Common Pitfalls

- **`buy` ko `sell` ke aage le jaana** — agar tum `min_price` ko current day se hi
  start karke profit nikaalo aur order galat ho, to invalid (future me kharid) ho
  sakta. Loop ka structure ensure karta hai ki min hamesha *current se pehle/equal* hai.
- **Negative profit return karna** — sab prices girte hue ho to answer `0` hona chahiye,
  koi negative number nahi. `max_profit` ko `0` se initialize karna isko sambhalta hai.
- **Do nested loops likhna** (O(n²)) — har pair try karna kaam karega par interview me
  O(n) single-pass expected hai.
- **`min_price = prices[0]` assume karna jab array khaali ho** — empty/None input
  handle kar lo.

## When to Use This Pattern

"Best profit / max gain between an earlier and a later element" ya "running minimum/
maximum ke against kuch compute karna" — jab aisa dikhe to socho: **ek pass me running
extreme track karo**. Yahi cue Maximum Subarray (Kadane), water-trapping aur kai
"so-far-best" problems me kaam aata hai.

## NeetCode Link

https://neetcode.io/problems/buy-and-sell-crypto
