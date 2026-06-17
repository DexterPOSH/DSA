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

Socho ek exam hall hai jisme 9 rows, 9 columns, aur 9 chhote cluster (3×3) hain. Rule: ek hi roll number (1-9) ek row me, ek column me, ya ek cluster me do baar nahi baith sakta. Ab ek invigilator har student ka roll number dekhte hi teen registers me check karta hai — *"is row ke register me yeh number pehle se hai? Is column ke register me? Is cluster ke register me?"* Agar kisi bhi register me already hai, to seating invalid — turant pakad lo. Har register ek **hash set** hai. Bas ek hi baar poora hall scan karo, har student pe teen O(1) lookups, aur valid/invalid ka faisla ho jaata hai.

## Approach

Har filled cell ko ek hi baar dekho. Uske liye teen "identities" hain: konsi **row**, konsa **column**, aur konsa **3×3 box**. Teeno ke liye `seen` sets maintain karo; agar digit kisi me already hai → invalid.

Box index nikalne ki trick: `(r // 3, c // 3)` — ye `(0..2, 0..2)` deta hai, total 9 boxes ko uniquely identify karta hai.

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

- **Time:** O(1) effectively — board hamesha 9×9 = 81 cells ka hai, har cell pe constant kaam. (General `n×n` ke liye O(n²).)
- **Space:** O(1) — at most 9 sets × 9 digits each, board size fixed hai. (General me O(n²).)

## Common Pitfalls

- **Empty cells (`"."`) ko set me daal dena** — sirf filled digits track karo, warna `.` "duplicate" lagega.
- **Box index galat compute karna** — `(r // 3, c // 3)` use karo. Common galti: `r // 3 * 3 + c // 3` (single int key — ye bhi chalta hai par carefully). Integer division key hai, `r % 3` nahi.
- **Board ko solve karne ki koshish** — sirf *current* validity check karni hai, solvability nahi. Backtracking yahan zaroorat nahi.
- **Sirf rows ya sirf cols check karna** — teeno (row, col, box) ek saath verify karne padte hain.
- **String vs int digit mismatch** — board me `"5"` string hota hai; consistently string treat karo.

## When to Use This Pattern

Jab ek hi element ko **multiple overlapping groups** ke against uniqueness/constraint ke liye check karna ho — socho **per-group hash sets, single pass**. Grids, scheduling conflicts (same person do meetings me?), "kya koi value kisi dimension me repeat karti hai" — har grouping ka ek set rakho aur saath-saath validate karo.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough that scans the board and lights up row/column/box sets.

## NeetCode Link

https://neetcode.io/problems/valid-sudoku
