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

Socho tum ek string banate jaa rahe ho ek character ek baar, aur tumhare paas ek
mental **stack of unclosed `(`** hai. Do hi rules yaad rakhne hain:

- Ek `(` daal sakte ho **agar abhi tak total `(` `n` se kam hain** (quota bacha hai).
- Ek `)` daal sakte ho **agar koi `(` open pada hai jise band karna baaki hai**
  (yaani open count > close count) — warna `)` pehle aa jaayega aur string invalid.

Har valid choice pe aage badho; jab string `2n` lambi ho jaaye, ek valid combination
mil gaya. Yeh wahi *"open bracket band hona chahiye"* stack-invariant hai — bas hum
saare valid raaste explore kar rahe hain. Jo branch invalid hone wali hai, usme
ghuste hi nahi (prune).

## Approach

Pattern: **backtracking guided by a stack invariant**. Hum har position pe `(` ya `)`
try karte hain, but sirf tab jab wo abhi tak ke string ko valid rakhe.

Track karo do counts: `open` (kitne `(` laga chuke) aur `close` (kitne `)`):

1. Agar `len(path) == 2n` → ek complete valid string, result me daalo.
2. Agar `open < n` → ek `(` add kar sakte ho (quota bacha).
3. Agar `close < open` → ek `)` add kar sakte ho (koi open band hone ko bacha hai).

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

`path` khud ek stack ki tarah behave karta — append/pop. Aur `close < open_` wala
guard exactly *Valid Parentheses* ka stack-non-empty check hai, bas yahan generation
me lagaya hai validity-by-construction ke liye. Isliye hume kabhi invalid string
banani hi nahi padti — har generated string already valid hai.

## Complexity

- **Time:** O(4ⁿ / √n) — yeh n-th Catalan number ki growth hai; itni hi valid strings
  hoti hain aur har ek ko build karne me O(n). Pruning ki wajah se hum invalid branches
  me time waste nahi karte.
- **Space:** O(n) recursion depth + O(n) current `path` (output store ko chhod ke).

## Common Pitfalls

- **Validity guards galat lagana** — `close < open_` (open count se, `n` se nahi).
  Common galti `close < n` likhna, jo `"))(("` jaise invalid strings allow kar deta.
- **Sirf base pe validity check karna** — pehle saari 2^(2n) strings banake phir valid
  filter karna kaam karega par bahut slow (exponential waste). Construction ke time hi
  prune karo.
- **Backtrack (`path.pop()`) bhulna** — append ke baad pop na karo to `path` corrupt
  ho jaata aur galat strings banti.
- **String concatenation overuse** — har recursive call me `path + "("` immutable copy
  banata; list + final `"".join` cleaner hai. (Dono chalte, but list zyada idiomatic.)

## When to Use This Pattern

Jab "saare valid combinations / arrangements generate karo with a constraint" dikhe →
**backtracking**, aur agar constraint *balanced / nesting / matching* type ka hai to
ek **stack-style counter invariant** (open vs close) use karke branches prune karo.
Cousins: subsets, permutations, combination-sum, valid IP addresses. Cue:
*"generate all well-formed X"* → build incrementally + prune invalid prefixes.

## NeetCode Link

https://neetcode.io/problems/generate-parentheses
