# Sum of Two Integers

**Category:** Bit Manipulation
**Difficulty:** medium

## Problem Statement

Given two integers `a` and `b`, return their sum **without using the `+` or `-` operators**.

```
a = 2, b = 3    ->  5
a = 1, b = 1    ->  2
a = -2, b = 3   ->  1
```

> Sirf bitwise operators (`^`, `&`, `<<`) allowed hain. Negative numbers bhi handle karne hain — yahi twist medium bana deta hai.

## Real-World Analogy

Socho tum grade-school addition kar rahe ho, par har column me sirf **0 ya 1** likh sakte ho (binary). Do bits jodte waqt do cheezein hoti hain:

- **Sum-without-carry** — `1 + 0 = 1`, `1 + 1 = 0` (carry chala gaya), `0 + 0 = 0`. Yeh exactly **XOR** (`^`) hai. XOR bolta hai "in dono bits ka sum, carry ko ignore karke".
- **Carry** — carry sirf tab banta hai jab **dono** bits 1 hon (`1 + 1`). Yeh exactly **AND** (`&`) hai. Aur carry hamesha **agle column (left) me** jaata hai, to use ek position `<< 1` shift karo.

Ab tum baar-baar yeh karte ho: "sum-without-carry nikaalo, carry nikaalo aur left shift karo, phir dono ko dobara jodo" — jab tak carry **0** na ho jaaye. Jaise hand-addition me jab tak koi carry-over bacha hai tab tak agla column add karte raho.

## Approach

Pattern: *XOR for partial sum, AND-and-shift for carry, loop until carry vanishes.*

```python
def get_sum(a, b):
    mask = 0xFFFFFFFF              # 32-bit window
    while (b & mask) != 0:        # while there is still a carry
        carry = (a & b) << 1      # carry: where both bits are 1, shifted left
        a = a ^ b                 # partial sum: add without carry
        b = carry & mask          # keep carry inside 32 bits
    # if result is "negative" in 32-bit, sign-extend it for Python's big ints
    return a & mask if b > mask else _to_signed(a)

def _to_signed(x):
    return x if x < 0x80000000 else ~(x ^ 0xFFFFFFFF)
```

Loop ka core simple hai:
1. `carry = (a & b) << 1` — jahan dono 1 hain wahan carry banega, left shift.
2. `a = a ^ b` — carry chhod ke baaki sum.
3. `b = carry` — ab `b` naya carry ban gaya; dobara loop.
4. Jab `carry == 0` ho jaaye → `a` me final sum hai.

> **Negative numbers / Python masking:** C++/Java me ints 32-bit fixed hote hain to carry apne aap "overflow" hokar gayab ho jaata hai. Python me int **infinite** hai, to carry kabhi rukta nahi — isliye `0xFFFFFFFF` mask se 32-bit window enforce karte hain aur end me sign wapas extend karte hain. Java/C++ me ye masking ki zarurat hi nahi.

## Complexity

- **Time:** O(1) — fixed 32-bit width, to at most ~32 carry-propagation iterations. Input-size pe depend nahi karta.
- **Space:** O(1) — sirf kuch integer variables.

## Common Pitfalls

- **Carry ko shift karna bhoolna** — carry hamesha **next higher bit** me jaata hai, to `(a & b) << 1`. Bina shift ke galat answer.
- **Loop condition galat** — loop tab tak chalta hai jab tak **carry (`b`) non-zero** ho, na ki jab tak `a` non-zero ho.
- **Python me masking chhodna** — bina `0xFFFFFFFF` mask ke negative additions me infinite loop ya galat sign milta hai. Java/C++ me ye trap nahi.
- **`a` aur `b` ko swap-confuse karna** — har iteration me `a` becomes partial-sum, `b` becomes shifted-carry. Order matter karta hai; carry ko `a^b` se pehle compute karo warna purana `b` chala jaayega.
- **Sign extension miss karna** — masked result agar 32-bit me negative range me hai to use signed me wapas convert karna padta hai (Python-specific).

## When to Use This Pattern

Jab problem explicitly arithmetic operators ban kar de, ya tumhe **ALU-level addition** simulate karni ho. Cue: *"add/subtract/multiply without `+`/`-`/`*`"* → bits ke through carry-propagation socho. Yahi mechanism real CPUs ke adders (ripple-carry adder) me use hota hai. Cousins: multiply without `*` (shift-and-add), divide without `/` (shift-and-subtract).

## Visual

Open [visual.html](visual.html) in your browser for an interactive bit-cell walkthrough of the XOR-sum / AND-carry loop.

## NeetCode Link

https://neetcode.io/problems/sum-of-two-integers
