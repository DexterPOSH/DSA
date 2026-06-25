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

**What Azure Data Factory is:** Azure Data Factory is Azure's data integration and orchestration service for building pipelines that move and transform data across systems. Pipelines contain activities, parameters, variables, and dynamic expressions so a workflow can decide file paths, filters, retries, and activity inputs at run time. That means the pipeline runtime needs a reliable way to reduce many small expression pieces into one final value.

**What the expression engine is, and why it's used:** Azure Data Factory's expression language lets you call functions and operators over pipeline values such as parameters, variables, activity outputs, and trigger metadata. The engine resolves the inputs first, then applies the function/operator, because dynamic pipelines must calculate values from already-known context rather than hard-coded strings. This exists so the same pipeline can adapt to different runs while still producing one deterministic output for each expression.

**The mapping:** In Reverse Polish Notation, each number token is like an already resolved Azure Data Factory value, so we push it onto the evaluator stack. When an operator token appears, the two most recent values are the complete inputs for that operation: pop right, pop left, compute `left op right`, then push the result back as a new resolved value. After all tokens, one value remains, just like one evaluated pipeline expression. The key insight is that postfix order makes parentheses unnecessary because every operator appears exactly when its operands are ready.

## Approach

Pattern: **stack** of operands. The beauty of RPN is that there is no precedence or
parentheses hassle — one left-to-right pass is enough.

1. If the token is a **number** → convert it to int and **push** it onto the stack.
2. If the token is an **operator** → **pop** the top two operands. Important: the first pop
   is the **right** operand and the second pop is the **left** operand (order matters for
   `-` and `/`). Compute `left op right` and **push** the result.
3. After all tokens are processed, the single remaining stack element is the answer.

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

- **Time:** O(n) — each token is processed exactly once; push/pop are O(1).
- **Space:** O(n) — in the worst case, all numbers appear before any operator (such as
  `["1","2","3",...]`), so the whole stack fills up.

## Common Pitfalls

- **Reversing operand order** — in `a - b`, the first pop is **b** (right) and the
  second pop is **a** (left). Writing `left - right` is correct; `right - left` gives
  the wrong answer for `-` and `/`. `+`/`*` are commutative, so the issue may be hidden
  there.
- **Wrong division truncation** — Python's `//` does *floor* division (`-7 // 2 == -4`),
  but the problem requires **toward-zero** truncation (`-7 / 2 -> -3`). Use
  `int(a / b)`, not `a // b`.
- **Treating negative numbers as operators** — `"-11"` is an operand, not an operator.
  Check "is this in ops?", not "does the first character equal `-`?".
- **Forgetting int conversion** — tokens are strings; `"2" + "1"` performs string
  concatenation (`"21"`), not arithmetic.

## When to Use This Pattern

When expression evaluation, postfix/prefix parsing, or "apply an operation to the
latest results and push the result back" appears → use an **operand stack**. Cousins: infix→postfix
(Shunting-yard), basic calculator, monotonic-stack expression problems. Cue:
*"the operator appears after/near its operands, and results need to be folded"* → stack.

## NeetCode Link

https://neetcode.io/problems/evaluate-reverse-polish-notation
