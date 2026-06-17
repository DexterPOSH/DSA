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

Socho ek **stack of plates** hai sink ke paas. Har baar koi open bracket aata hai
to tum ek plate rakh dete ho — sabse upar wali plate hamesha "abhi-abhi rakhi gayi"
wali hoti hai. Jab close bracket aata hai, to tum **sabse upar wali plate hi
uthaate ho** aur check karte ho: kya yeh us close bracket se match karti hai?
`(` ke upar `)` aaya — perfect, plate hat gayi. Lekin `(` ke upar `]` aa gaya?
Mismatch — galat. Yeh **Last-In-First-Out** behaviour exactly stack hai: jo aakhri
me khula, wahi pehle band hona chahiye.

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
