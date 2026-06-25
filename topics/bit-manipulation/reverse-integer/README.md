# Reverse Integer

**Category:** Bit Manipulation
**Difficulty:** medium

## Problem Statement

Given a signed 32-bit integer `x`, return `x` with its **digits reversed**. If reversing causes the value to go **outside the signed 32-bit range** `[-2^31, 2^31 - 1]` (i.e. `[-2147483648, 2147483647]`), return `0`.

```
x = 123     ->  321
x = -123    ->  -321
x = 120     ->  21        # trailing zero disappears
x = 1534236469 -> 0       # reversed (9646324351) overflows 32-bit -> 0
```

> Sign preserve karna hai, trailing zeros drop ho jaate hain, aur **overflow** check karna hai *bina* 64-bit ya bigger types use kiye — yahi asli challenge hai.

## Real-World Analogy

**What Azure Functions is:** Azure Functions is Azure's serverless compute service for running small pieces of code in response to events such as messages, timers, or HTTP requests. In this analogy, a function normalizes a legacy telemetry code before saving it into Azure SQL Database, Azure's managed relational database service.

**What a SQL `INT` boundary check is, and why it's used:** Azure SQL Database's `INT` type is a signed 32-bit value, from `-2,147,483,648` to `2,147,483,647`. The normalizer must validate the reversed code before writing it because the database column enforces that range, and an overflowing value should be rejected rather than treated as valid telemetry. Checking before the next digit push avoids relying on an already-invalid intermediate value.

**The mapping:** The function peels the least-significant decimal digit with `% 10`, appends it to the reversed code with `res * 10 + digit`, and shrinks the input with `// 10` after handling the sign. Before each append, it compares against the 32-bit limits just like the Azure Function validates the Azure SQL `INT` range before insert. The key insight is to reverse one digit at a time while treating overflow as a boundary condition checked during the build, not as a cleanup step at the end.

## Approach

Pattern: *peel last digit, push onto result, check overflow before each push.*

```python
def reverse(x):
    INT_MAX, INT_MIN = 2**31 - 1, -2**31     # 2147483647, -2147483648
    sign = 1 if x >= 0 else -1
    x = abs(x)
    res = 0
    while x:
        digit = x % 10
        x //= 10
        # pre-check: will res*10 + digit overflow the 32-bit magnitude?
        if res > INT_MAX // 10 or (res == INT_MAX // 10 and digit > INT_MAX % 10):
            return 0
        res = res * 10 + digit
    return sign * res
```

Logic ko todhte hain:
1. **Sign nikaal lo**, phir absolute value pe kaam karo (uniform handling).
2. **Digit peel:** `digit = x % 10`, `x //= 10`.
3. **Overflow pre-check:** push karne se pehle dekho `res * 10 + digit > INT_MAX` to nahi ho raha. Isko *bina* overflow kiye check karte hain: `res > INT_MAX // 10` (definitely overflow) ya `res == INT_MAX // 10 and digit > 7` (last-digit boundary, kyunki `INT_MAX = 2147483647` ka last digit `7` hai).
4. **Push:** `res = res * 10 + digit`.
5. End me sign wapas laga do.

> Python me int infinite hai to technically overflow nahi hota — par interview problem 32-bit languages (C++/Java) ko model karta hai. Wahan `res * 10 + digit` actually overflow karke garbage de dega, isliye pre-check **must** hai. Python me bhi same logic likho taaki language-agnostic ho.

## Complexity

- **Time:** O(log₁₀ x) — number me jitne digits utne hi iterations (~10 max for 32-bit).
- **Space:** O(1) — sirf kuch scalar variables.

## Common Pitfalls

- **Overflow ko push ke baad check karna** — C++/Java me tab tak damage ho chuka. Hamesha **multiply se pehle** check karo.
- **64-bit pe rely karna** — `long` me reverse karke compare karna kaam to karta hai but problem ki spirit (32-bit only) violate karta hai; interviewer aksar mana karta hai.
- **Negative modulo** — kuch languages me `-123 % 10` negative deta hai. Sign pehle alag karke `abs(x)` pe kaam karna safest.
- **Trailing zeros** — `120 -> 21` automatically handle ho jaata hai (`res * 10 + 0` leading zero add nahi karta), par log isse over-engineer kar dete hain.
- **`INT_MIN` ko `abs` karna** — `abs(-2^31)` 32-bit me `2^31` ho jaata hai jo overflow hai. Python me safe, par C++/Java me `INT_MIN` ko alag se handle karna padta hai.

## When to Use This Pattern

Jab digit-by-digit processing ho aur **fixed integer-width overflow** se bachna ho — "reverse / palindrome number / atoi (string to int)" type problems. Cue: *"reverse digits / parse number, 32-bit constraint, no bigger type"* → peel-and-push loop with a **pre-multiply overflow guard**. Cousins: **String to Integer (atoi)**, **Palindrome Number**, **Add Digits**.

## Visual

Open [visual.html](visual.html) in your browser for an interactive digit-by-digit walkthrough with a live 32-bit overflow guard.

## NeetCode Link

https://neetcode.io/problems/reverse-integer
