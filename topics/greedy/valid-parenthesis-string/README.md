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

**What Azure API Management is:** Azure API Management is Azure's gateway service for publishing, securing, transforming, and observing APIs. Teams configure gateway behavior with XML-based policies for things like authentication, rate limiting, header rewrites, and backend routing. Those policy documents must remain structurally valid XML for the gateway to apply them safely.

**What policy XML fragment validation is, and why it's used:** API Management policy fragments let teams reuse optional policy snippets across APIs instead of copying the same XML everywhere. During assembly, a fragment may effectively contribute an opening scope, a closing scope, or nothing depending on whether it is included and how it is parameterized. Branching through every possible expansion is expensive, so a validator can track the minimum and maximum possible number of unclosed scopes after each token.

**The mapping:** `'('` is an Azure API Management opening policy scope, `')'` is a closing scope, and `'*'` is an optional fragment that could open, close, or disappear. `low` is the fewest unclosed scopes still possible, while `high` is the most; if `high` drops below zero, every interpretation has too many closings, and if `low` can be clamped to zero, extra optional closings can be treated as empty. The string is valid only when zero remains possible at the end — the key insight is to keep a feasible range instead of enumerating every fragment expansion.
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
