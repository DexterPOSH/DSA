# Combination Sum

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given an array of **distinct** positive integers `candidates` and a `target`, return all
**unique combinations** where the chosen numbers sum to `target`. The **same number may be
chosen unlimited times**. Two combinations are the same if they have the same multiset of
numbers (order doesn't matter).

```
candidates = [2, 3, 6, 7], target = 7
->  [[2, 2, 3], [7]]          # 2+2+3 = 7,  7 = 7

candidates = [2, 3, 5], target = 8
->  [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
```

## Real-World Analogy

Socho tumhare paas unlimited coins hain of fixed denominations — `[2, 3, 6, 7]` rupaye ke
sikke — aur tumhe **exactly 7 rupaye** banane ka har tareeka chahiye. Ek coin jitni baar
chaaho utni baar use kar sakte ho. Tum ek coin uthate ho, remaining amount ghataate ho,
aur recurse karte ho. Agar remaining 0 ho gaya → ek valid combo mila. Agar remaining negative
ho gaya → too far, **backtrack** karo. Duplicate combos (`[2,3]` vs `[3,2]`) avoid karne ke
liye ek `start` index rakhte ho taaki coins hamesha non-decreasing order me hi pick ho.

## Approach — backtracking with reuse + `start` pointer

Key trick: same number reuse karne ke liye recurse karte waqt **`start` ko same `i` pe
rakho** (na ki `i+1`). Aur duplicates rokne ke liye loop hamesha `start` se aage hi jaata —
isse combinations sorted-ish rehte aur `[2,3]`/`[3,2]` jaisa double-count nahi hota.

```python
def combination_sum(candidates, target):
    res, path = [], []

    def backtrack(start, remain):
        if remain == 0:
            res.append(path[:])              # exact hit -> record copy
            return
        if remain < 0:
            return                            # overshoot -> prune
        for i in range(start, len(candidates)):
            path.append(candidates[i])
            backtrack(i, remain - candidates[i])   # i (not i+1) -> reuse allowed
            path.pop()                              # BACKTRACK

    backtrack(0, target)
    return res
```

> **Optional speedup:** `candidates.sort()` pehle, phir loop ke andar
> `if candidates[i] > remain: break`. Sorted hone se ek bhi element overshoot kare to baaki
> sab bhi karenge → poora loop tod do.

## Complexity

- **Time:** O(2^(target / min_candidate)) — worst case me tree ki depth `target/min` tak ja
  sakti (chhota candidate baar-baar add hota). Practically pruning isse kaabu me rakhta.
- **Space:** O(target / min) recursion depth + path. Output alag se.

## Common Pitfalls

- **`backtrack(i+1, ...)` likh dena** → reuse band ho jaata, `[2,2,3]` jaise combos miss.
- **`start` na rakhna (loop from 0)** → duplicate combos `[2,3]` aur `[3,2]` dono aa jaate.
- **`remain < 0` base case bhulna** → infinite recursion / TLE.
- **`path[:]` copy na karna** → saari stored combos baad me corrupt.
- Negative ya zero candidates assume mat karo — problem positives guarantee karta; warna
  reuse-with-zero infinite loop ban jaata.

## When to Use This Pattern

"Target tak pahunchne ke saare tareeke" / "unlimited reuse with a sum/quantity constraint"
dikhe → backtracking with a `start` pointer + reuse (`i`, not `i+1`). Coin-change ke count
variant ka cousin (lekin yahan saare combinations chahiye, sirf count nahi). Combination Sum
II me yahi pattern + per-level dedup aata hai.

## NeetCode Link

https://neetcode.io/problems/combination-target-sum
