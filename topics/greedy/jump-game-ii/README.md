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

Socho ek bus route hai. Index `0` ek bus-stop hai, aur wahan se tum ek single jump me kuch stops tak ja sakte ho — yeh tumhara "**level 1 reachable zone**" hai (1 jump me jahan-jahan pahunch sakte ho). Ab us poore zone ke andar khade har stop se aage dekho — un sab ki combined reach tumhara "**level 2 zone**" banati hai (2 jumps me reachable). Phir level 3, aur aise hi.

Yeh bilkul **BFS level-by-level expansion** jaisa hai: har "jump" ek BFS level hai. Tum individually har stop ko visit nahi karte — bas current level ka **right boundary** (`cur_end`) aur us level se reachable **farthest** point (`farthest`) track karte ho. Jab tum current level ke boundary pe pahunch jaate ho, ek jump count badha do aur next level me chale jao. Destination jis level me pehli baar aata hai, wahi minimum jumps hai.

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
