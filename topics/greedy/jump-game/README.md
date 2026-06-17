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

Socho tum stepping-stones pe khade ho ek river paar karne ke liye. Har stone pe likha hai ki tum **maximum** kitne stones aage chhalang laga sakte ho (tum kam bhi laga sakte ho). Sawaal: kya tum aakhri stone tak pahunch sakte ho?

Smart trick: stone-by-stone planning mat karo. Bas ek number track karo — **"abhi tak ke information se, sabse door kaunsa stone main reach kar sakta hu?"** (called `reach`). Tum left se right chalte ho; har stone pe jisko tum chhoo sakte ho, dekho ki wahan se aur kitna aage jaa sakte the, aur apna `reach` update karo. Agar kabhi tum ek aise stone pe pahunch jao jo tumhare `reach` se aage hai — matlab beech me ek `0` ne raasta kaat diya — to game over, `False`. Agar `reach` aakhri stone tak chhoo le, `True`.

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
