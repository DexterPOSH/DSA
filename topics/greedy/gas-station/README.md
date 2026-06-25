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

**What Azure Front Door / Traffic Manager is:** Azure Front Door and Azure Traffic Manager are global routing services that help send users to the right healthy region instead of hard-coding one destination. Front Door works as an HTTP(S) edge entry point with origin health checks, while Traffic Manager uses DNS-based routing methods like priority, weighted, or performance. In both cases, the goal is to keep traffic moving around the globe even when one region cannot safely carry the next handoff.

**What regional failover capacity planning is, and why it's used:** A regional failover runbook asks, "If this region receives traffic, does it have enough spare capacity to serve users and then hand off overflow or recovery work to the next region?" Health probes tell Azure which endpoints are usable, but operators still need capacity math so failover does not push a region into overload. The total spare capacity across regions must cover total demand; otherwise no routing order can complete the circle.

**The mapping:** Each station is an Azure region, `gas[i]` is spare capacity gained there, and `cost[i]` is the capacity spent handing traffic to the next region. The running `tank` is the capacity balance for the current candidate start; if it drops below zero, that start and every region in the failed prefix are invalid because they could not survive the same accumulated handoffs. Once total capacity is feasible, resetting to the next region after each negative dip leaves the only valid start — the key insight is that a failed prefix never needs to be reconsidered.
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
