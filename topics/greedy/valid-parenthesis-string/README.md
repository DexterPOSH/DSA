# Valid Parenthesis String

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

Given a string `s` containing only `'('`, `')'`, and `'*'`, return `True` if `s`
is a **valid** parenthesis string. Each `'*'` can be treated as a `'('`, a `')'`,
or an empty string `""`. Valid means: every `'('` has a matching `')'` after it,
every `')'` has a matching `'('` before it, and they nest correctly.

```
"(*)"   -> True   # * = empty (or '(' then... ) -> "()"
"(*))"  -> True   # * = empty -> "())"? no -> * = '(' -> "(())"
"(((**" -> False  # too many '(' even if both * become ')'
```

## Real-World Analogy

Socho ek **accountant** ek ledger left-se-right padh raha hai jahan har `'('` ek
"open IOU" hai aur `')'` ek IOU close karta hai. Problem ye ki har `'*'` ek
**wildcard** hai — pata nahi open hai, close hai, ya kuch nahi. To accountant do
counters chalata hai: **`low`** = "kam-se-kam kitne IOU abhi open ho sakte hain"
aur **`high`** = "zyada-se-zyada kitne open ho sakte hain". Wildcard dono ko
alag-alag direction me khींchta hai. Agar kabhi `high` negative ho gaya — matlab
optimistic case me bhi zyada `)` aa gaye — game over. Aur end pe agar `low` `0`
tak aa sakta hai, to ek valid interpretation exist karta hai.

## Approach

Brute force (har `*` ke 3 choices) exponential hai. Smart greedy: ek **range
`[low, high]`** track karo of possible "open bracket" counts.

- `'('` → `low++`, `high++` (definitely ek open add).
- `')'` → `low--`, `high--` (definitely ek open close).
- `'*'` → `low--` (agar `*` = `)`), `high++` (agar `*` = `(`). Range fail jata.

Rules: `high < 0` kabhi bhi → `False` (best case me bhi `)` zyada). `low` ko
`0` se neeche mat jaane do (clamp `low = max(low, 0)`) — kyunki "negative open"
ka matlab kuch nahi, `*` ko empty maan lo.

```python
def is_valid(s):
    low = high = 0
    for ch in s:
        if ch == '(':
            low += 1; high += 1
        elif ch == ')':
            low -= 1; high -= 1
        else:                      # '*'
            low -= 1; high += 1
        if high < 0:               # even most-open reading has extra ')'
            return False
        low = max(low, 0)          # can't have negative open brackets
    return low == 0                # some reading closes everything
```

Pattern: **greedy interval/range tracking.** Ek hi pass, O(1) space — har char
pe possible-open-count ka window maintain hota hai. (DP `O(n²)` bhi possible hai
but ye range trick cleaner aur faster.)

## Complexity

- **Time:** O(n) — single left-to-right pass.
- **Space:** O(1) — sirf `low` aur `high` do integers.

## Common Pitfalls

- **`low` ko clamp na karna** — agar `low` negative jaane do bina `max(low,0)`,
  to end-check `low == 0` galat ho jaata. Negative open meaningless hai → 0 pe
  floor karo.
- **`high < 0` check bhulna** — ye early-exit zaroori hai; bina iske tum `)` ko
  "future `(`" se illegally balance kar loge.
- **End pe `high == 0` check karna** — galat. `low == 0` check karo: low 0 tak
  pahunch sakta hai matlab ek valid reading hai jaha sab close ho gaya.
- **`*` ko sirf empty ya sirf bracket maanna** — teeno possibilities ek saath
  range me capture hoti hain; isliye `low`/`high` dono move karte hain.

## When to Use This Pattern

"Wildcard / uncertain choices ke saath balance ya feasibility check" → ek range
`[min, max]` of reachable states track karo bajaye har branch explore karne ke.
Cue: "har element ke multiple interpretations hain, par tum bas *koi ek* valid
combination chahte ho" → optimistic/pessimistic bounds ek saath chalao.

## NeetCode Link

https://neetcode.io/problems/valid-parenthesis-string
