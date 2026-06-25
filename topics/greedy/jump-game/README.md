# Jump Game

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

You are given an integer array `nums`. You start at index `0`. Each element `nums[i]` is the **maximum** jump length you can take forward from that index. Return `True` if you can reach the **last index**, otherwise `False`.

```
[2, 3, 1, 1, 4]   ->   True    # 0 -> 1 -> 4  (jump 1, then jump 3)
[3, 2, 1, 0, 4]   ->   False   # stuck at index 3 (value 0), can't pass it
[0]               ->   True    # already at the last index
```

## Real-World Analogy

**What Azure Monitor autoscale for Virtual Machine Scale Sets is:** Azure Monitor autoscale can automatically change the instance count of an Azure Virtual Machine Scale Set based on metrics such as CPU, queue depth, or custom signals. Instead of manually deciding every capacity change, you define rules that let Azure scale out or in while respecting limits. The purpose is to know whether the service can grow far enough to meet demand without planning every possible path.

**What farthest-reachable capacity tracking is, and why it's used:** In autoscale planning, each reachable capacity checkpoint may allow another bounded increase, but exploring every chain of scale decisions would be wasteful. A simpler feasibility check keeps the farthest capacity reachable from any checkpoint already proven reachable. If the next checkpoint is beyond that boundary, no previous rule could have gotten you there, so the target capacity is impossible.

**The mapping:** Each array index is an Azure VMSS capacity checkpoint, `nums[i]` is the maximum additional capacity reachable from that checkpoint, and `reach` is the farthest capacity Azure could have achieved so far. Scanning left to right only processes checkpoints that are within `reach`; each one may extend the boundary with `i + nums[i]`. The moment an index sits beyond `reach` the plan fails, and if `reach` covers the last index the deployment is feasible — the key insight is that reachability needs one boundary, not the exact path.
## Approach

**Backtracking / DP** se bhi ho sakta hai (har index se saare jumps try karo), but wo O(n²) ya exponential. Greedy se O(n).

**Optimal — greedy "farthest reach"** (O(n)):

`reach` = ab tak ka maximum index jahan tak pahunchna possible hai. Left se right scan karo:

```python
def can_jump(nums):
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:           # is index tak pahunch hi nahi sakte
            return False
        reach = max(reach, i + jump)   # yahan se kitna door jaa sakte the
        if reach >= len(nums) - 1:     # last index already covered
            return True
    return True
```

Greedy insight: humein exact path nahi chahiye, sirf yeh ki **last index covered hua ki nahi**. Har reachable index apni jump add karke `reach` ko aage khinchta hai. Jaise hi koi index `reach` se aage nikla, wahan tak pahunchne ka koi tareeka nahi tha → `False`.

> Ek alternate greedy (right-to-left): `goal = n-1` rakho; agar `i + nums[i] >= goal` to `goal = i`. Last me check karo `goal == 0`. Dono O(n), same idea, ulta direction.

## Complexity

- **Time:** O(n) — ek single forward pass, har index pe constant work.
- **Space:** O(1) — sirf ek `reach` variable.

## Common Pitfalls

- **`i > reach` check bhulna** — yahi wo line hai jo `0` waale dead-end ko detect karti hai. Iske bina tum aisi index ko bhi process kar loge jahan pahunchna impossible tha.
- **`reach` ko `nums[i]` se confuse karna** — `reach` absolute index hai (`i + jump`), na ki sirf jump length. Yeh galti har baar hoti hai.
- **DP/backtracking pe time waste** — yeh problem dekhte hi greedy click hona chahiye; O(n²) DP interview me weak answer hai (although correct).
- **Single-element array** — `[0]` ka answer `True` hai (tum already last index pe ho). Loop ka early-return ise handle karta hai.

## When to Use This Pattern

Jab dikhe **"kya end tak / target tak pahunchna possible hai, jahan har step pe ek range of moves available ho"** — to *reachability* greedy socho: ek "farthest I can get" pointer maintain karo. Cue: "feasibility (yes/no) chahiye, exact path nahi." Cousins: Jump Game II (min jumps), Jump Game III, Gas Station.

## Visual

Open [visual.html](visual.html) in your browser for an interactive Prev/Next walkthrough of the `reach` marker advancing.

## NeetCode Link

https://neetcode.io/problems/jump-game
