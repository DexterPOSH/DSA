# Palindrome Partitioning

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given a string `s`, partition it such that **every substring of the partition is
a palindrome**. Return **all possible** palindrome partitionings of `s`.

```
s = "aab"  ->  [ ["a","a","b"], ["aa","b"] ]
s = "a"    ->  [ ["a"] ]
s = "aba"  ->  [ ["a","b","a"], ["aba"] ]
```

> Note: hum *count* nahi, **saare valid partitions** chahiye. Yeh classic
> "generate all" backtracking signal hai.

## Real-World Analogy

**What Azure Policy is:** Azure Policy is the governance service that evaluates Azure resources against rules such as required tags, allowed locations, naming conventions, or security settings. It can audit noncompliant resources or block deployments before they drift from organization standards. In this analogy, the policy rule is intentionally simple: a proposed resource-name segment must be a palindrome.

**What resource-name segment validation is, and why it's used:** Segment validation checks each proposed piece of a resource name before it becomes part of the deployment path. Azure teams use naming rules because names often encode ownership, environment, region, and purpose, and bad names make operations and compliance harder. Rejecting a bad segment immediately prevents the planner from spending time extending a deployment prefix that can never be compliant.

**The mapping:** At index `start`, the algorithm tries every possible next name segment and runs the Azure Policy-style palindrome gate on it. Valid segments are appended to the current path and recursed on; invalid segments are pruned, and completed paths are recorded when the whole string has been consumed. The key insight is to validate each local choice before going deeper, then undo it so the next segment length can be tried.

## Approach — backtracking with palindrome prefix check

State: `start` = abhi string ke kis index se aage cut karna hai, aur `path` =
ab tak chunke gaye palindrome tukde.

At `start`:
1. Agar `start == len(s)` → poori string consume ho gayi, `path` ek valid
   partition hai → result me copy daalo.
2. Har `end` for `start+1 .. len(s)` ke liye: substring `s[start:end]` lo.
   - Agar woh **palindrome** hai → `path` me add karo, `dfs(end)` recurse, fir
     **pop (backtrack)**.
   - Palindrome nahi to skip (yeh prune hai).

```python
def partition(s):
    res, path = [], []

    def is_pal(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1; r -= 1
        return True

    def dfs(start):
        if start == len(s):
            res.append(path[:])         # copy current partition
            return
        for end in range(start + 1, len(s) + 1):
            if is_pal(start, end - 1):  # prefix s[start:end] palindrome?
                path.append(s[start:end])
                dfs(end)
                path.pop()              # BACKTRACK

    dfs(0)
    return res
```

> **Optional speedup — precompute DP table:** `pal[i][j]` = kya `s[i:j+1]`
> palindrome hai, fill in O(n²). Fir har `is_pal` check O(1). Interview me
> mention karna achha; basic solution ke liye inline check bhi chalta hai.

## Complexity

- **Time:** O(n · 2ⁿ) — worst case (e.g. `"aaaa..."`) me 2^(n-1) possible cut
  positions, aur har partition ko copy karne me O(n). Palindrome check pruning
  practically isse kam kar deta.
- **Space:** O(n) recursion depth + O(n) `path` (output size alag se count nahi).

## Common Pitfalls

- **`path[:]` copy bhulna** — `res.append(path)` (without slice) saari entries ko
  same list reference se bhar dega; final me sab empty/galat dikhenge.
- **Backtrack `path.pop()` miss** — state leak ho jaata, galat partitions.
- **`end` range off-by-one** — `s[start:end]` me `end` exclusive hai; loop
  `len(s)+1` tak jana chahiye taaki last tak ke substrings cover ho.
- **Single chars** hamesha palindrome hain — base/trivial case mat bhoolna (har
  string me at least `["a","b","c"...]` wala partition hota hai).
- **Har possible cut try karna** zaroori hai (sirf pehla palindrome prefix nahi)
  — warna saare partitions nahi milenge.

## When to Use This Pattern

"Generate **all** ways to split/partition something jahan har piece ko ek
condition satisfy karni ho" → backtracking with prefix-validity check. Cue: "all
partitions / all combinations", per-piece constraint. Cousins: Word Break II,
Combination Sum, Restore IP Addresses. Mantra: choose a valid prefix → recurse on
the rest → undo.

## NeetCode Link

https://neetcode.io/problems/palindrome-partitioning
