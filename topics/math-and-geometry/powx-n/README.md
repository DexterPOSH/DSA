# Pow(x, n)

**Category:** Math & Geometry
**Difficulty:** medium

## Problem Statement

Implement `pow(x, n)`, which computes `x` raised to the power `n` (i.e. `x^n`). Here `x` is a
real number and `n` is a (possibly negative) integer.

```
pow(2.0, 10)   ->  1024.0
pow(2.0, -2)   ->  0.25       # = 1 / 2^2
pow(3.0, 0)    ->  1.0        # anything^0 = 1
```

> The naive "multiply x by itself n times" is O(n). The interview wants **O(log n)** —
> **fast exponentiation** (a.k.a. exponentiation by squaring / binary exponentiation).

## Real-World Analogy

Socho tumhe `x` ko **64 baar** khud se multiply karna hai (`x^64`). Ek tareeka: 64 baar
loop chala ke ek-ek karke multiply karo — 63 multiplications, thaka dene wala. Smart
tareeka: **squaring ki seedhi (ladder)** chadho. Pehle `x²` nikalo (1 multiply). Phir
usko square karo → `x⁴` (1 aur). Phir → `x⁸`, `x¹⁶`, `x³²`, `x⁶⁴`. Sirf **6 squarings**
me pahunch gaye! Har step pe exponent **double** ho raha hai, isliye n tak pahunchne me
sirf **log₂(n)** steps lagte hain.

Aur jab exponent perfect power-of-2 na ho (jaise `x¹³`)? `13 = 1101` in binary = `8 + 4 + 1`,
to `x¹³ = x⁸ · x⁴ · x¹`. Matlab: ladder chadhte jao, aur **jahan binary me `1` ho wahan
current value ko answer me multiply kar lo**. Binary representation hi bata deti hai kaunse
rungs uthane hain.

## Approach

**Binary (iterative) fast exponentiation.** `n` ke binary bits ko right se padho:

1. Negative `n` handle karo: `x^(-n) = 1 / x^n`, to `x = 1/x`, `n = -n`.
2. `result = 1`. Loop jab tak `n > 0`:
   - Agar `n` **odd** hai (lowest bit `1`) → `result *= x` (is rung ko answer me lo).
   - `x *= x` (square — agla rung), aur `n //= 2` (agla bit).

```python
def my_pow(x, n):
    if n < 0:
        x, n = 1 / x, -n          # x^-n = (1/x)^n
    result = 1.0
    while n > 0:
        if n & 1:                 # current binary bit is 1
            result *= x
        x *= x                    # square: x -> x^2 -> x^4 -> ...
        n >>= 1                   # drop the bit we just used
    return result
```

Recursive form bhi classic hai (`half = pow(x, n//2); return half*half` (+`x` agar odd)) — same
O(log n), but iterative me stack overflow ka risk nahi.

Pattern: **exponentiation by squaring / binary exponentiation** — exponent ko binary me decompose.

## Complexity

- **Time:** O(log n) — har iteration me `n` half hota hai, to ~log₂(n) iterations. Naive O(n) se bahut tez.
- **Space:** O(1) iterative (sirf do variables). Recursive version O(log n) call-stack leta hai.

## Common Pitfalls

- **Negative exponent bhulna** — `n < 0` pe `1/x` aur `n = -n` zaroori, warna galat answer.
- **`n = INT_MIN` overflow** (C++/Java) — `-n` overflow kar jaata hai jab `n` sabse chhota int ho.
  Python me ye problem nahi (arbitrary precision int), but interview me mention karo: pehle
  `long` me cast karo ya carefully handle.
- **`n = 0` edge** — `x^0 = 1` (including `0^0 = 1` by convention). `result = 1` se ye automatically theek hai.
- **Naive O(n) likh dena** — `for _ in range(n): result *= x` correct hai par TLE/slow; interview O(log n) maangti hai.
- **Float precision** — bohot bade `n` pe floating-point error accumulate hota hai; usually accept kiya jaata hai, but aware raho.
- **Odd-check ke baad square karna bhulna** — order matters: pehle `result *= x` (agar odd), phir `x *= x`.

## When to Use This Pattern

Jab kisi cheez ko **n baar repeatedly combine** karna ho aur operation **associative** ho
(multiply, matrix-multiply, modular-multiply) → exponentiation by squaring O(log n) me kaam
karwa deta. Cue: "compute x^n fast", "n is huge", "x^n mod p". Cousins: matrix-power
(Fibonacci in O(log n)), modular exponentiation (crypto / RSA), fast doubling.

## NeetCode Link

https://neetcode.io/problems/pow-x-n
