# Permutations

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given an array `nums` of **distinct** integers, return **all possible permutations** (every
ordering). Order of the permutations in the output doesn't matter.

```
[1, 2, 3]  ->  [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]   # 3! = 6
[0, 1]     ->  [[0,1], [1,0]]
```

> `n` distinct elements ke `n!` permutations hote hain — pehli position ke liye `n` choices,
> agli ke liye `n-1`, aur aage. Subsets se key difference: yahan **order maayne rakhta hai**
> aur har permutation me **saare** elements aate hain.

## Real-World Analogy

**What Azure Update Manager is:** Azure Update Manager helps assess and patch Windows and Linux machines across Azure, on-premises, and other cloud environments. It lets teams schedule maintenance windows, coordinate update runs, and track which machines have been patched. For critical fleets, the order of machines in a runbook can matter because teams may want to limit blast radius.

**What maintenance ordering is, and why it's used:** Maintenance ordering assigns each VM to exactly one slot in a patch sequence. It exists because a schedule like `VM-A, VM-B, VM-C` is different from `VM-C, VM-B, VM-A` when risk, dependencies, or canary rollout order matters, but the same VM should not occupy two slots in one plan. A `used` marker enforces that single-assignment rule while still allowing the planner to try every possible order.

**The mapping:** Each number is an Azure VM, and the current path is the patch order being built. The recursion chooses one unused VM for the next slot, marks it used, continues until the path length matches the fleet size, then records that complete schedule. The key insight is that permutations are all possible ordered maintenance plans where every VM appears once and backtracking frees it for a different slot in the next plan.

## Approach — pick-an-unused-element backtracking

Ek `used` boolean array (ya set) rakho. Har recursion level pe, **jo abhi tak use nahi hua**
har element ko current position pe try karo: usko `path` me daalo + `used` mark karo, recurse,
phir undo (backtrack). Jab `path` ki length `n` ho jaaye → ek full permutation mila.

```python
def permute(nums):
    res, path = [], []
    used = [False] * len(nums)

    def backtrack():
        if len(path) == len(nums):
            res.append(path[:])              # full ordering -> record copy
            return
        for i in range(len(nums)):
            if used[i]:
                continue                      # already placed -> skip
            used[i] = True
            path.append(nums[i])
            backtrack()
            path.pop()                        # BACKTRACK
            used[i] = False                   # un-mark

    backtrack()
    return res
```

> **Swap trick (O(1) extra space):** `used` array ki jagah array ko in-place swap karke
> permute kar sakte ho — `for i in range(start, n): swap(start,i); rec(start+1); swap(start,i)`.
> Same complexity, kam memory, but `used`-version padhna/samajhna aasaan.

## Complexity

- **Time:** O(n · n!) — `n!` permutations, har ek ko O(n) me build/copy karte.
- **Space:** O(n) recursion depth + `used` + path (output excluded).

## Common Pitfalls

- **`used` ko un-mark na karna** (`used[i] = False` bhulna) → galat results, kuch permutations
  gayab.
- **`path.pop()` aur `used[i]=False` ka order/jodi** miss karna → state corruption.
- Subsets wale `start` pointer ka idea yahan **galat** hai — permutations me har level pe
  poore array se choose karna hai (sirf already-used skip karte), `start` se nahi.
- **`path[:]` copy** na karna → reference bug.

## When to Use This Pattern

"Saare orderings / arrangements / sequences" dikhe (jahan order maayne rakhta aur sab elements
use hote) → backtracking with a `used` set. Cue: output size `n!`. Cousins: N-Queens
(placement orderings), string anagrams, Permutations II (with duplicates → sort + skip).

## NeetCode Link

https://neetcode.io/problems/permutations
