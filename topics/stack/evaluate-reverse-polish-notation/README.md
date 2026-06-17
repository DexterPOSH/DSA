# Evaluate Reverse Polish Notation

**Category:** Stack
**Difficulty:** medium

## Problem Statement

You are given an array of strings `tokens` representing an arithmetic expression in
**Reverse Polish Notation** (RPN, a.k.a. postfix). Evaluate it and return the integer
result. Valid operators are `+`, `-`, `*`, `/`. Each operand is an integer, and
**division truncates toward zero**.

In RPN the operator comes *after* its two operands, so there are no parentheses:
`(2 + 1) * 3` is written `["2", "1", "+", "3", "*"]`.

```
["2", "1", "+", "3", "*"]                ->  9      # (2 + 1) * 3
["4", "13", "5", "/", "+"]               ->  6      # 4 + (13 / 5) = 4 + 2
["10","6","9","3","+","-11","*","/","*","17","+","5","+"]  ->  22
```

## Real-World Analogy

Socho ek **cafeteria tray-stack** hai. Jab number aata hai, tum ek tray (us number
ke saath) stack pe rakh dete ho. Jab koi **operator** aata hai — jaise `+` — to wo
ek instruction hai: *"upar wali do trays utha, unpe yeh operation laga, aur result ko
ek nayi single tray bana ke wapas rakh do"*. Bas yahi. Stack hamesha "abhi tak ke
adhoore results" ko hold karta hai. Aakhir me jab saare tokens khatam ho jaate hain,
stack me **theek ek tray** bachti hai — wahi final answer hai.

## Approach

Pattern: **stack** of operands. RPN ki khoobsurti yeh hai ki precedence/parentheses
ka jhanjhat hi nahi — left-to-right ek hi pass kaafi hai.

1. Token **number** hai → stack pe **push** karo (int me convert karke).
2. Token **operator** hai → top do operands **pop** karo. Dhyaan: pehla pop
   **right** operand hai, dusra pop **left** (order `-` aur `/` ke liye matter karta).
   `left op right` compute karo aur result **push** karo.
3. Saare tokens ke baad stack pe bacha akela element = answer.

```python
def eval_rpn(tokens):
    stack = []
    ops = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: int(a / b),   # truncate toward zero, NOT floor
    }
    for tok in tokens:
        if tok in ops:
            right = stack.pop()
            left = stack.pop()
            stack.append(ops[tok](left, right))
        else:
            stack.append(int(tok))
    return stack[0]
```

## Complexity

- **Time:** O(n) — har token exactly ek baar; push/pop O(1).
- **Space:** O(n) — worst case sab numbers pehle aate (jaise `["1","2","3",...]`) to
  poora stack bhar jaata before any operator.

## Common Pitfalls

- **Operand order ulta karna** — `a - b` me first-pop **b** (right) hai aur
  second-pop **a** (left). `left - right` likhna sahi; `right - left` `-` aur `/`
  pe galat answer dega. `+`/`*` commutative hain to wahan farak nahi padta — isliye
  bug chhup jaata hai.
- **Division truncation galat** — Python ka `//` *floor* karta hai (`-7 // 2 == -4`),
  problem **toward-zero** truncation maangta (`-7 / 2 -> -3`). Isliye `int(a / b)` use
  karo, `a // b` nahi.
- **Negative numbers ko operator samajhna** — `"-11"` ek operand hai, operator nahi.
  Check "is this in ops?" karo, na ki "kya pehla char `-` hai?".
- **int conversion bhulna** — tokens strings hain; `"2" + "1"` string concat dega
  (`"21"`), arithmetic nahi.

## When to Use This Pattern

Jab expression evaluation, postfix/prefix parsing, ya "ek operation latest results pe
lagao aur result wapas rakho" dikhe → **operand stack**. Cousins: infix→postfix
(Shunting-yard), basic calculator, monotonic-stack expression problems. Cue:
*"operator apne operands ke baad/aas-paas hai, results ko fold karna hai"* → stack.

## NeetCode Link

https://neetcode.io/problems/evaluate-reverse-polish-notation
