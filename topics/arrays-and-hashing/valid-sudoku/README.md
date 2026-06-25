# Valid Sudoku

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given a `9 x 9` Sudoku board (partially filled, empty cells marked `"."`), determine if the current state is **valid**. Valid means: each **row**, each **column**, and each of the nine **3×3 sub-boxes** contains the digits `1-9` with **no repeats**. You only validate what's filled — you don't have to solve the board.

```
A board where row 0 has two 8s  ->  False
A board with no row/col/box repeats among filled cells  ->  True
```

## Real-World Analogy

**What Azure Policy/RBAC scoped validation is:** Azure Policy evaluates whether resources comply with rules, while Azure RBAC controls which principals have permissions. Both systems reason about Azure scopes such as subscriptions, resource groups, and individual resources. A rule or assignment is meaningful inside its scope, not as one global bucket for the entire cloud.

**What scoped validation is, and why it's used:** Scoped validation checks a constraint within each boundary where that constraint applies. Azure uses scopes so a policy assignment, exemption, or role assignment can be evaluated in the right place without confusing it with unrelated scopes elsewhere. This solves the problem of enforcing local correctness: something may be valid in one scope but conflicting or noncompliant in another.

**The mapping:** Treat every Sudoku row, column, and 3x3 box as its own Azure scope with a set of digits already seen. When a digit appears, validate it against all three relevant scope sets; if any one already contains the digit, the board violates the rule. The key insight is that Sudoku validity is scoped uniqueness, so separate hash sets let one scan enforce every local constraint at once.
## Approach

Look at each filled cell exactly once. Each digit belongs to three "identities": its **row**, its **column**, and its **3×3 box**. Maintain `seen` sets for all three; if a digit is already present in any of them → invalid.

Trick for computing the box index: `(r // 3, c // 3)` — this returns `(0..2, 0..2)` and uniquely identifies the 9 boxes.

```python
from collections import defaultdict

def is_valid_sudoku(board):
    rows = defaultdict(set)
    cols = defaultdict(set)
    boxes = defaultdict(set)          # key = (r // 3, c // 3)

    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val == ".":
                continue
            box = (r // 3, c // 3)
            if val in rows[r] or val in cols[c] or val in boxes[box]:
                return False           # repeat found
            rows[r].add(val)
            cols[c].add(val)
            boxes[box].add(val)
    return True
```

Pattern: **hash sets for constraint/uniqueness tracking** across multiple groupings simultaneously.

## Complexity

- **Time:** O(1) effectively — the board is always 9×9 = 81 cells, and each cell does constant work. (For a general `n×n` board, O(n²).)
- **Space:** O(1) — at most 9 sets × 9 digits each, because the board size is fixed. (In the general case, O(n²).)

## Common Pitfalls

- **Adding empty cells (`"."`) to the set** — track only filled digits; otherwise, `.` will look like a duplicate.
- **Computing the box index incorrectly** — use `(r // 3, c // 3)`. A common alternative is `r // 3 * 3 + c // 3` (a single integer key — this also works if used carefully). Integer division is the key, not `r % 3`.
- **Trying to solve the board** — you only need to check *current* validity, not solvability. Backtracking is not needed here.
- **Checking only rows or only columns** — all three groups (row, column, box) must be verified together.
- **String vs int digit mismatch** — the board stores `"5"` as a string, so treat digits consistently as strings.

## When to Use This Pattern

When one element must be checked for uniqueness or constraints across **multiple overlapping groups**, think **per-group hash sets, single pass**. Grids, scheduling conflicts (the same person in two meetings?), and questions like "does any value repeat along a dimension" all use the same idea: keep one set per grouping and validate them together.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough that scans the board and lights up row/column/box sets.

## NeetCode Link

https://neetcode.io/problems/valid-sudoku
