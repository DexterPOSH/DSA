# House Robber II

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Same as House Robber — `nums[i]` is the money in house `i`, and robbing two **adjacent** houses triggers the alarm — but now the houses are arranged in a **circle**: the **first and last houses are also adjacent**. Return the maximum money you can rob.

```
nums = [2, 3, 2]        ->  3     # houses 0 and 2 are adjacent (circle), so can't take both 2s; take house 1 -> 3
nums = [1, 2, 3, 1]     ->  4     # rob house 0 and 2 -> 1 + 3 = 4
nums = [1, 2, 3]        ->  3     # take house 2
```

## Real-World Analogy

**What Azure Update Manager is:** Azure Update Manager coordinates patching and maintenance for Azure, hybrid, and multicloud machines. It lets teams define recurring schedules so updates happen predictably while compliance stays visible. In a recurring calendar, the first and last slots can be neighbors because the schedule wraps around.

**What circular maintenance-calendar conflict handling is, and why it's used:** A circular maintenance plan must treat the end of one cycle as adjacent to the start of the next. That rule exists because choosing both edge windows could still update dependent systems too close together, even though they appear far apart in a flat list. The clean way to enforce the conflict is to solve two safe linear schedules: one excluding the first window and one excluding the last.

**The mapping:** The circular street is Azure Update Manager's recurring calendar, and each maintenance window has a value. Run the normal non-adjacent DP once on windows `0..n-2` and once on `1..n-1`, then take the better cached schedule. The key insight is that breaking the first/last conflict converts the circle into two ordinary House Robber problems.

## Approach

Linear House Robber helper banao (`max(dp[i-1], nums[i] + dp[i-2])`), phir use **do baar** chalao:
- `rob_line(nums[0 : n-1])` → first house allowed, last excluded.
- `rob_line(nums[1 : n])` → last allowed, first excluded.

Answer = `max` of the two. Edge case: agar sirf ek ghar hai (`n == 1`), to seedha `nums[0]`.

**Pattern:** circular DP → reduce to two linear subproblems.

```python
def rob(nums):
    if len(nums) == 1:
        return nums[0]

    def rob_line(houses):
        rob2, rob1 = 0, 0          # dp[i-2], dp[i-1]
        for n in houses:
            rob2, rob1 = rob1, max(rob1, n + rob2)
        return rob1

    return max(rob_line(nums[:-1]),   # exclude last
               rob_line(nums[1:]))    # exclude first
```

## Complexity

- **Time:** O(n) — do linear passes, har ek O(n).
- **Space:** O(1) — rolling two variables; slicing `nums[:-1]`/`nums[1:]` ko in-place index range se bhi avoid kar sakte ho.

## Common Pitfalls

- **`n == 1` ka special case bhulna** — `nums[:-1]` empty ho jaata aur ek branch 0 return karta, jab actual answer `nums[0]` hona chahiye. Empty slice handle karo.
- **Sirf ek line chalana** — dono ranges (`0..n-2` aur `1..n-1`) zaroori hain; ek bhula to circle constraint galat handle hoga.
- **Pehla aur aakhri dono ko ek hi line me allow kar dena** — yahi to circle me forbidden hai; isiliye to split kiya.
- **Linear House Robber ka base case galat** — same pitfalls as plain House Robber (`dp[1] = max(nums[0], nums[1])`).

## When to Use This Pattern

Jab ek **linear DP problem ko circular constraint** mil jaaye (first aur last element linked ho), to socha-samjha move: **circle ko todo do/teen fixed-choice linear cases me, har ek solve karo, best lo.** Yeh "fix one endpoint's decision, solve the rest linearly" technique circular array problems me baar-baar kaam aati hai. Cousins: House Robber (linear base), circular array max subarray, gas station style wrap-arounds.

## NeetCode Link

https://neetcode.io/problems/house-robber-ii
