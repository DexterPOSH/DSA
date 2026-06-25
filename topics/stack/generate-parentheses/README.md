# Generate Parentheses

**Category:** Stack
**Difficulty:** medium

## Problem Statement

Given `n` pairs of parentheses, generate **all combinations** of well-formed
(valid) parentheses.

```
n = 1  ->  ["()"]
n = 2  ->  ["(())", "()()"]
n = 3  ->  ["((()))", "(()())", "(())()", "()(())", "()()()"]
```

The number of valid combinations is the **n-th Catalan number** (1, 2, 5, 14, 42, …).

## Real-World Analogy

**What Azure Resource Manager (ARM) is:** Azure Resource Manager is Azure's control-plane deployment service, and Bicep is the declarative language that compiles into ARM templates. Together they let you describe resources and deployments as structured templates instead of clicking through the portal. For large systems, that structure often becomes nested: a parent deployment coordinates child modules and scopes.

**What nested deployment scope management is, and why it's used:** ARM/Bicep modules can target deployment scopes such as a resource group, subscription, management group, or tenant, and child deployments let you compose a big rollout from smaller reusable pieces. Scope management exists so each module runs with the correct context, dependencies, and parameters without mixing up which resources belong where. Once you enter a child scope, that child must be completed before the parent path can be considered closed, giving the structure a natural "last opened, first closed" shape.

**The mapping:** Generating parentheses is like generating every valid Azure ARM/Bicep scope trace with `n` child scopes. Adding `(` opens a new child deployment if the quota `open < n` still allows it; adding `)` closes the most recent unmatched scope only when `close < open`. The current `path` is the active deployment stack: append to descend, pop to backtrack, then try a sibling branch. The key insight is validity-by-construction — those two guards prevent Azure scope traces that close too early or leave children unclosed, so every completed length-`2n` path is balanced.

## Approach

Pattern: **backtracking guided by a stack invariant**. At each position, try either `(` or `)`,
but only when that choice keeps the prefix valid so far.

Track two counts: `open` (how many `(` have been placed) and `close` (how many `)` have been placed):

1. If `len(path) == 2n` → you have a complete valid string, so add it to the result.
2. If `open < n` → you can add a `(` because some open quota remains.
3. If `close < open` → you can add a `)` because there is an unmatched open parenthesis to close.

```python
def generate_parenthesis(n):
    res = []

    def backtrack(path, open_, close):
        if len(path) == 2 * n:
            res.append("".join(path))
            return
        if open_ < n:                      # can still open
            path.append("(")
            backtrack(path, open_ + 1, close)
            path.pop()                     # BACKTRACK
        if close < open_:                  # can close an open one
            path.append(")")
            backtrack(path, open_, close + 1)
            path.pop()                     # BACKTRACK

    backtrack([], 0, 0)
    return res
```

`path` behaves like a stack through append/pop. The `close < open_` guard is exactly
the stack-non-empty check from *Valid Parentheses*, applied here during generation
to enforce validity by construction. That means we never have to build invalid strings —
every generated string is already valid.

## Complexity

- **Time:** O(4ⁿ / √n) — this is the growth of the n-th Catalan number; there are that
  many valid strings, and each takes O(n) to build. Pruning prevents us from wasting
  time on invalid branches.
- **Space:** O(n) recursion depth + O(n) current `path` (excluding output storage).

## Common Pitfalls

- **Using the wrong validity guards** — use `close < open_` (compare with the open count,
  not with `n`). A common mistake is writing `close < n`, which allows invalid strings
  such as `"))(("`.
- **Checking validity only at the base case** — generating all 2^(2n) strings first and
  filtering them later works, but it is extremely slow because of exponential waste.
  Prune during construction instead.
- **Forgetting to backtrack (`path.pop()`)** — if you append without popping afterward,
  `path` becomes corrupted and produces incorrect strings.
- **Overusing string concatenation** — `path + "("` creates an immutable copy on every
  recursive call; a list plus final `"".join` is cleaner. (Both work, but the list is
  more idiomatic.)

## When to Use This Pattern

When you see "generate all valid combinations / arrangements with a constraint" →
use **backtracking**. If the constraint is about *balance / nesting / matching*,
use a **stack-style counter invariant** (open vs close) to prune branches.
Cousins: subsets, permutations, combination-sum, valid IP addresses. Cue:
*"generate all well-formed X"* → build incrementally + prune invalid prefixes.

## NeetCode Link

https://neetcode.io/problems/generate-parentheses
