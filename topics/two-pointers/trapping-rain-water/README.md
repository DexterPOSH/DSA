# Trapping Rain Water

**Category:** Two Pointers
**Difficulty:** hard

## Problem Statement

Given `n` non-negative integers `height` representing an elevation map (bar widths
= 1), compute **how much water it can trap** after raining.

```
[0,1,0,2,1,0,1,3,2,1,2,1]   ->  6
[4,2,0,3,2,5]               ->  9
```

Each bar traps water on top of itself equal to
`min(maxLeft, maxRight) - height[i]` (if positive), where `maxLeft`/`maxRight` are
the tallest bars to its left/right.

## Real-World Analogy

Socho ek pahaadi jaisa terrain hai — kuch oonche peaks, kuch gaddhe (valleys).
Baarish ke baad paani **gaddhon** me ruk jaata hai. Kisi ek point pe kitna paani
rukega? Wo us point ke **dono taraf ki sabse oonchi deewar** pe depend karta —
paani utna hi bhar sakta jitni **chhoti wali boundary** allow kare (warna woh side
se beh jaayega). Us point ke khud ki height ghata do, jo bacha woh trapped water.

Two-pointer insight: do log dono ends se andar aate hain. Har step pe **jis side
ki abhi tak ki max wall chhoti hai, wahi side process karo** — kyunki us side ka
trapped water uski apni side ke max se hi decide ho jaata, doosri side guaranteed
usse oonchi (ya barabar) hai.

## Approach

Pattern: **two pointers + running max from both ends** (O(n) time, O(1) space).

```python
def trap(height):
    if not height:
        return 0
    l, r = 0, len(height) - 1
    left_max, right_max = height[l], height[r]
    water = 0
    while l < r:
        if left_max < right_max:
            l += 1
            left_max = max(left_max, height[l])
            water += left_max - height[l]    # left_max guaranteed limiting wall
        else:
            r -= 1
            right_max = max(right_max, height[r])
            water += right_max - height[r]
    return water
```

**Kyun safe hai?** Agar `left_max < right_max`, to left pointer pe paani ki height
`left_max` se decide hoti — kyunki right side pe koi wall hai jo `left_max` se badi
hai (right_max), to woh paani ko rok legi. Isiliye `left_max - height[l]` add karna
correct hai bina right side jaane.

> **Alternatives:**
> - **Prefix/suffix arrays:** har index ke liye `maxLeft[]` aur `maxRight[]`
>   precompute karo, fir ek pass. O(n) time **par O(n) space**.
> - **Monotonic stack:** bars ko stack me rakho, "layer by layer" paani bharo.
>   O(n)/O(n). Two-pointer **O(1) space** deta — best.

## Complexity

- **Time:** O(n) — har bar at most ek baar process hota.
- **Space:** O(1) — sirf do pointers aur do running maxes (stack/array version
  O(n) leta).

## Common Pitfalls

- **`max(left_max, height[l])` se pehle/baad pointer move ka order** — pehle
  pointer khisko, fir us nayi position ka height max me merge karo, fir water add.
  Order galat hua to current bar ka contribution galat aayega.
- **Container With Most Water samajh lena** — wahaan **width × min height** ka
  *single* max area chahiye; yahaan har gaddhe ka paani *sum* karna hai. Alag
  problem, alag formula.
- **Negative water add karna** — two-pointer version me yeh automatically avoid ho
  jaata (`left_max - height[l]` hamesha >= 0 by construction), par naive per-index
  approach me `max(0, ...)` lagana padta.
- **Empty array** — `if not height: return 0`, warna `height[r]` index error.

## When to Use This Pattern

Jab "har position ka answer dono taraf ke max/min pe depend kare" → socho
**running max from both ends with two pointers**, ya prefix/suffix precompute, ya
monotonic stack. Cue: "elevation / histogram me trapped water, har point ko left
aur right context chahiye."

## NeetCode Link

https://neetcode.io/problems/trapping-rain-water
