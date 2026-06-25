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

**What Azure Virtual Machines are:** Azure Virtual Machines provide on-demand Windows or Linux compute in Azure, with virtual CPUs, memory, disks, and networking managed as cloud resources. Even though the VM is virtualized, arithmetic still ultimately runs on CPU hardware exposed through fixed-width registers.

**What ALU carry propagation is, and why it's used:** The Arithmetic Logic Unit (ALU) adds binary numbers by separating each bit column's partial sum from its carry. XOR gives the sum bits when carry is ignored, AND finds the columns where two 1s create a carry, and `<< 1` moves those carries to the next higher column. Hardware uses this gate-level idea because addition can be built from simple repeatable signals that settle until no carry remains.

**The mapping:** The two inputs are the Azure VM's register values. `a ^ b` computes the carry-free partial sum, `(a & b) << 1` computes the carry register, and the loop feeds those two values back into the same process until the carry becomes zero. The key insight is that integer addition is just repeated partial-sum plus shifted-carry work, so we can reproduce `+` with bit operations alone.

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
