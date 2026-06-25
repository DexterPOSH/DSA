# Valid Parentheses

**Category:** Stack
**Difficulty:** easy

## Problem Statement

Given a string `s` containing only the characters `(`, `)`, `{`, `}`, `[`, `]`, determine if the input string is **valid**. A string is valid when:

1. every open bracket is closed by the **same type** of bracket, and
2. brackets are closed in the **correct order** (the most recently opened bracket must close first).

```
"()[]{}"   ->  True
"(]"       ->  False
"([)]"     ->  False    # wrong order — ( and [ interleave
"{[]}"     ->  True
```

## Real-World Analogy

**What Azure Resource Manager (ARM) is:** Azure Resource Manager is Azure's deployment and management layer, and Bicep is a higher-level language that compiles to ARM templates. They let you describe a hierarchy of resources and modules so Azure can create or update them consistently. Nested deployments feel a lot like structured brackets: each scope has to start, contain its work, and finish cleanly.

**What nested deployment scope management is, and why it's used:** ARM/Bicep modules can deploy to different scopes, such as a resource group, subscription, management group, or tenant. This scoping exists to keep permissions, parameters, dependencies, and resource names attached to the right deployment context instead of leaking into a sibling or parent context. When a child scope is opened, the active context should close in reverse order; closing a parent before its latest child would leave Azure reasoning about the wrong deployment boundary.

**The mapping:** An opening bracket is Azure entering a new ARM/Bicep scope, so we push the expected closing scope onto the stack. A closing bracket is Azure trying to exit a scope, so it must match the most recently opened one at the stack top; if the stack is empty or the type differs, the template shape is invalid. After the scan, the stack must be empty, meaning every opened deployment scope closed in LIFO order. The key insight is "last opened, first closed": counts alone cannot catch `([)]`, but a stack catches the wrong active context immediately.

## Approach

Pattern: **stack** (LIFO). Left-to-right scan karo:

1. **Open bracket** (`(`, `{`, `[`) dikhe → stack pe **push** karo.
2. **Close bracket** dikhe → stack ka **top pop** karo aur dekho kya wo matching
   open bracket hai. Agar stack khaali hai (koi open hi nahi tha) ya top match
   nahi karta → turant `False`.
3. Scan khatam hone par stack **empty** hona chahiye. Agar kuch bacha hai → kuch
   open brackets band nahi hue → `False`.

```python
def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}   # close -> open
    stack = []
    for ch in s:
        if ch in pairs:                       # ch is a closing bracket
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:                                 # opening bracket
            stack.append(ch)
    return not stack                          # valid only if nothing left open
```

Trick: ek `close -> open` map rakhne se code clean rehta hai — har close bracket
ke liye uska expected partner ek lookup me mil jaata.

## Complexity

- **Time:** O(n) — har char ek baar process hota, push/pop dono O(1).
- **Space:** O(n) — worst case sab open brackets (jaise `"((((("`) stack me jaate.

## Common Pitfalls

- **Empty-stack check bhulna** — `")"` pe `stack.pop()` crash karega. Pehle `not stack`
  check karo, phir pop.
- **End me stack empty check na karna** — `"("` valid lagta agar tum sirf mismatch
  dekhte ho, but stack me `(` bacha hai → invalid. `return not stack` zaroori hai.
- **Sirf count match karna** — `(` aur `)` ki ginti barabar hone se valid nahi hota;
  `"([)]"` me count barabar hai par order galat hai. Order stack hi pakadta hai.
- **Type ignore karna** — `(` ko `]` se band karna invalid hai; bracket *type* match
  hona chahiye, sirf "koi close bracket" nahi.

## When to Use This Pattern

Jab bhi "matching pairs", "nesting", ya "most-recent-first" close hone wala
structure dikhe → **stack** socho. Cousins: expression parsing, HTML/XML tag
matching, undo history, function call stack. Cue: *"Last opened, first closed"* =
LIFO = stack.

## NeetCode Link

https://neetcode.io/problems/validate-parentheses
