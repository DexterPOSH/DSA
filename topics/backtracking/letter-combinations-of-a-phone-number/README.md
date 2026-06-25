# Letter Combinations of a Phone Number

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given a string `digits` containing digits from `2-9`, return **all possible
letter combinations** that the number could spell — like on an old phone keypad.
The mapping is the classic T9 layout (`2 -> abc`, `3 -> def`, … `9 -> wxyz`).

```
digits = "23"  ->  ["ad","ae","af","bd","be","bf","cd","ce","cf"]
digits = ""    ->  []
digits = "2"   ->  ["a","b","c"]
```

> Output order LeetCode pe strict nahi (set equality), but DFS naturally
> lexicographic order me deta hai.

## Real-World Analogy

**What Azure Resource Manager is:** Azure Resource Manager (ARM) is Azure's control plane for creating and updating resources through templates, Bicep files, REST calls, and portal actions. It takes a deployment definition plus parameter values, then materializes resources such as storage accounts, networks, or VMs. The same template can produce many candidate deployments by varying allowed parameter values.

**What parameter fan-out is, and why it's used:** A parameter fan-out, or parameter sweep, tries every allowed value for each configurable position: region, SKU, suffix, environment, and so on. Teams use this to validate supported combinations, generate test deployments, or produce candidate names without hand-writing every case. If one parameter has three allowed values and the next has three more, ARM-style planning branches into a small Cartesian product.

**The mapping:** Each digit is a deployment parameter position, and its phone letters are that parameter's allowed Azure values. DFS appends one allowed value, recurses to the next parameter, then pops it so the next value can be tried; every root-to-leaf path is one complete deployment string. The key insight is pure fan-out: make exactly one choice per position, and the recursion naturally enumerates all combinations.

## Approach — backtracking over digit positions

`digit -> letters` ka mapping ready rakho. State: `idx` = abhi `digits` ka kaunsa
position pick karna hai, `path` = ab tak chune gaye letters.

At `idx`:
1. Agar `idx == len(digits)` → ek poori combination ban gayi → result me add.
2. Warna `digits[idx]` ke har letter ke liye: `path` me append, `dfs(idx+1)`,
   fir **pop (backtrack)**.

```python
def letter_combinations(digits):
    if not digits:
        return []
    keypad = {"2":"abc","3":"def","4":"ghi","5":"jkl",
              "6":"mno","7":"pqrs","8":"tuv","9":"wxyz"}
    res, path = [], []

    def dfs(idx):
        if idx == len(digits):
            res.append("".join(path))
            return
        for ch in keypad[digits[idx]]:
            path.append(ch)
            dfs(idx + 1)
            path.pop()                  # BACKTRACK

    dfs(0)
    return res
```

> Yeh essentially ek **Cartesian product** hai. `itertools.product` se one-liner
> bhi bante hai, but interview me decision-tree backtracking dikhana zyada
> insightful hai — same skeleton subsets/permutations me reuse hota hai.

## Complexity

- **Time:** O(4ⁿ · n) — n = `len(digits)`. Har digit ke up to 4 letters
  (`7` aur `9`), to total combinations 4^n tak, aur har ek ko build karne me O(n).
- **Space:** O(n) recursion depth + `path`. Output ko alag se count na karein.

## Common Pitfalls

- **Empty input** — `digits == ""` → return `[]`, **not** `[""]`. Yeh edge case
  miss hota hai kyunki base case `[""]` produce kar deta hai agar guard na ho.
- **Backtrack `path.pop()` bhulna** — letters carry-over ho jaayenge, galat
  combinations.
- **Mapping galat** — `7 -> pqrs` aur `9 -> wxyz` me **4 letters** hain (baaki me
  3). Off-by-one se letters chhoot jaate.
- **`"".join(path)` bana ke append karna** — agar `path` reference append karoge
  (string nahi banaya), to mutation se sab corrupt. Yahan join se naya string
  ban jaata, so safe.
- **`1` ya `0`** ke liye koi letters nahi — problem `2-9` guarantee karta, but
  defensively check karna achha.

## When to Use This Pattern

"Har position pe ek set me se ek choose karo, **saare combinations** chahiye" →
backtracking decision tree (a.k.a. Cartesian product). Cue: multiple independent
choice-sets, "generate all". Cousins: Subsets, Permutations, Combination Sum.
Mantra: pick one option at this level → recurse to next level → undo.

## NeetCode Link

https://neetcode.io/problems/combinations-of-a-phone-number
