# Jump Game II

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

You are given an integer array `nums` (length `n`). You start at index `0`. Each `nums[i]` is the **maximum** forward jump from index `i`. It is **guaranteed** you can reach the last index. Return the **minimum number of jumps** to reach index `n - 1`.

```
[2, 3, 1, 1, 4]   ->   2     # 0 -> 1 -> 4
[2, 3, 0, 1, 4]   ->   2     # 0 -> 1 -> 4
[0]               ->   0     # already at the end
```

## Real-World Analogy

**What Azure Monitor autoscale for Virtual Machine Scale Sets is:** Azure Monitor autoscale adjusts an Azure Virtual Machine Scale Set's instance count when metric rules say the workload needs more or less capacity. It works with configured minimum, maximum, and default capacities so scaling stays controlled instead of chaotic. For this analogy, each scale-out action is a wave that can extend the amount of capacity Azure can safely reach.

**What scale-out wave planning is, and why it's used:** A scale-out action often has to be reasoned about in stages: all capacities reachable with the current number of actions form one band, and only after that band is exhausted do you need another action. This is like a compressed breadth-first search over capacity levels. Tracking the current band boundary and the farthest next boundary avoids storing every possible path while still proving the minimum number of scale-out actions.

**The mapping:** Each index is an Azure VMSS capacity checkpoint, `nums[i]` is how far one more scale-out wave could extend from there, `cur_end` is the end of the current action band, and `farthest` is the best next band discovered while scanning. When the scan reaches `cur_end`, Azure must spend one more scale-out action and move the boundary to `farthest`. The first band whose boundary covers the target gives the answer — the key insight is that minimum jumps are BFS levels compressed into two greedy boundaries.
## Approach

**BFS (explicit)** se bhi solve hota hai — har level ke indices ko queue me daalo — but O(n) space. Greedy isi BFS ko **two pointers** se O(1) space me kar deta hai.

**Optimal — greedy BFS by boundaries** (O(n)):

```python
def jump(nums):
    jumps = 0
    cur_end = 0       # current jump-level ka right boundary
    farthest = 0      # is level se reachable maximum index
    for i in range(len(nums) - 1):       # last index pe ruko mat
        farthest = max(farthest, i + nums[i])
        if i == cur_end:                 # current level khatam
            jumps += 1                   # ek jump kharch karo
            cur_end = farthest           # next level ka boundary
    return jumps
```

`farthest` har reachable index ki reach ko absorb karta jaata hai. Jab `i` current level ke `cur_end` ko chhoo leta hai, matlab is level me jitna explore karna tha ho gaya → ek jump badhao aur boundary ko `farthest` tak push kar do (yeh ban jaata hai next level ka end). Loop `n-1` tak hi chalta hai kyunki last index *pe pahunchne* ke baad aur jump nahi chahiye — last cell pe boundary touch karke extra jump count karne se off-by-one ho jaata.

## Complexity

- **Time:** O(n) — single pass, har index par constant work.
- **Space:** O(1) — sirf teen scalars (`jumps`, `cur_end`, `farthest`).

## Common Pitfalls

- **Loop ko `n` tak chalana (instead of `n-1`)** — agar last index pe `i == cur_end` ho jaaye to tum ek extra jump count kar loge. `range(len(nums) - 1)` se yeh bug avoid hota hai.
- **Har index se DFS/greedy "jitna door ho sake utna jump" karna** — yeh hamesha optimal nahi hota; jo jump door pahunchta hai wo zaroori nahi minimum jumps de. BFS-by-level hi correct min deta hai.
- **`cur_end` aur `farthest` ko gadbad karna** — `farthest` continuously update hota hai; `cur_end` sirf level boundary par jump karta hai. Dono alag pointers hain.
- **`reach` vs jump-count confuse karna** — Jump Game I sirf feasibility (`reach`) maangta tha; yahan reachability guaranteed hai, hum *jumps* gin rahe hain.

## When to Use This Pattern

Jab dikhe **"minimum number of steps / jumps / levels to reach a target, jahan har position se ek range of moves ho"** — to **BFS-by-levels** socho, aur agar moves "har index se ek contiguous forward range" ho to use O(1) greedy-boundary me compress kar do. Cue: "min hops on a line." Cousins: Jump Game (feasibility), shortest-path-on-grid BFS, word-ladder.

## Visual

Open [visual.html](visual.html) in your browser for an interactive Prev/Next walkthrough showing BFS levels and the `cur_end` / `farthest` boundaries.

## NeetCode Link

https://neetcode.io/problems/jump-game-ii
