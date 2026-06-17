# Gas Station

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

There are `n` gas stations arranged in a **circle**. `gas[i]` is the fuel available at station `i`, and `cost[i]` is the fuel needed to travel from station `i` to station `i+1` (wrapping around). You start with an empty tank at one station and drive clockwise. Return the **starting station index** from which you can complete the full circle once, or `-1` if impossible. The answer is **guaranteed unique** if it exists.

```
gas  = [1, 2, 3, 4, 5]
cost = [3, 4, 5, 1, 2]   ->   3     # start at station 3, complete the loop

gas  = [2, 3, 4]
cost = [3, 4, 3]         ->  -1     # no valid start
```

## Real-World Analogy

Socho ek circular road-trip hai. Har petrol-pump pe kuch litre milta hai (`gas[i]`), aur agle pump tak pahunchne me kuch litre lagta hai (`cost[i]`). Tum chahte ho ek aisa pump jahan se shuru karke poora circle bina tank empty hue complete ho jaye.

Do simple sachchaiyan:
1. **Agar total petrol < total cost, to koi bhi start kaam nahi karega** — itna fuel hi nahi hai. Turant `-1`.
2. **Agar total petrol ≥ total cost, to ek valid start zaroor hoga** (problem guarantee). Ab sirf *kaunsa* dhoondhna hai.

Trick ye hai: ek running `tank` rakho jaise tum drive kar rahe ho. Jis pal `tank` negative ho jaata hai — matlab current start se yahan tak nahi pahunche — to ek **important insight** kaam aata hai: us start aur is failure-point ke beech ka koi bhi pump valid start nahi ho sakta. Kyun? Kyunki agar wo bhi `tank ≥ 0` rakhte hue idhar tak nahi la paaye (aur tum unse pehle se positive tank le kar aaye the, phir bhi fail hue), to wo akele aur bhi jaldi fail honge. To poora prefix skip karo aur **next station ko naya candidate start** maan lo. Ek hi forward pass me answer mil jaata hai.

## Approach

**Brute force** — har station ko start maano aur poora circle simulate karo: O(n²).

**Optimal — single-pass greedy** (O(n)):

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1                 # not enough fuel anywhere

    start, tank = 0, 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:              # can't reach i+1 from current start
            start = i + 1         # everything up to i is disqualified
            tank = 0              # reset; fresh start from i+1
    return start
```

Do alag cheezein track ho rahi hain:
- `sum(gas) - sum(cost)` (overall feasibility) — agar negative, `-1`.
- `tank` (current candidate start se running balance). Jab bhi `tank < 0`, current candidate fail; `start` ko `i+1` pe move karo aur `tank` reset karo.

Greedy isliye correct hai kyunki jab feasibility guaranteed ho, to **wo last reset point hi unique valid start hota hai** — uske aage koi negative dip nahi aati (warna start aage shift hota).

## Complexity

- **Time:** O(n) — ek hi pass (feasibility check bhi O(n)). Total O(n).
- **Space:** O(1) — sirf do running scalars.

## Common Pitfalls

- **Feasibility check skip karna** — agar `sum(gas) < sum(cost)` na check karo, to greedy ek `start` return kar dega jo actually circle complete nahi karta. Yeh check `-1` case ko zaroori hai.
- **`tank` reset karna bhulna** — jab `start = i+1` set karo, `tank = 0` bhi karna padta hai, warna purana negative carry hota rahega.
- **Sochna ki "max gas / min cost" wala station best start hai** — nahi. Valid start *sequence* pe depend karta hai, single station property pe nahi.
- **Circle wrap ko over-engineer karna** — modular arithmetic ki zaroorat nahi; single linear pass kaafi hai, kyunki feasible hone par wo `start` poora wrap-around handle karta hai.

## When to Use This Pattern

Jab dikhe **circular array + running balance jisme aapko ek valid starting point dhoondhna ho** (aur ek "total feasibility" condition ho) — to **prefix-reset greedy** socho: running sum negative hote hi candidate start ko aage move karo. Cue: "circular tank / running cumulative jo kabhi negative na jaaye." Cousins: Maximum Subarray (Kadane's reset idea), circular subarray problems.

## Visual

Open [visual.html](visual.html) in your browser for an interactive Prev/Next walkthrough of the running tank and start-reset logic.

## NeetCode Link

https://neetcode.io/problems/gas-station
