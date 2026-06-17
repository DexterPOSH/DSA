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

Socho ek **odometer ko ulta padhna** hai. Tum number ke **aakhri digit ko peel** karte ho (`x % 10`), aur use ek naye number ke aage push karte ho (`result * 10 + digit`). Har step me purana number ek digit chhota hota jaata hai (`x // 10`), naya reversed number ek digit bada.

Par ek catch hai: tumhare paas ek **fixed-size meter** hai jo sirf `2147483647` tak ja sakta hai. Har digit push karne se *pehle* tumhe poochna padta hai: "agar main ise 10 se multiply karke ek aur digit lagaaun, kya meter phat jaayega?" Agar haan → `0` return karke ruk jao. Yeh **overflow ko pre-emptively** check karna hai, baad me nahi (kyunki tab tak meter already galat value pe ja chuka hoga).

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
