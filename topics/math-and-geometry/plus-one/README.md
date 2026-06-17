# Plus One

**Category:** Math & Geometry
**Difficulty:** easy

## Problem Statement

You're given a non-negative integer represented as an array of digits `digits`, where the **most significant digit is first** (i.e. `[1, 2, 3]` means the number 123). Each element is a single digit `0–9`. Increment the number by one and return the resulting array of digits.

```
[1, 2, 3]      ->  [1, 2, 4]      # 123 + 1 = 124
[1, 2, 9]      ->  [1, 3, 0]      # 129 + 1 = 130  (carry)
[9, 9, 9]      ->  [1, 0, 0, 0]   # 999 + 1 = 1000 (grows by one digit)
```

> Catch: you can't just do `int("".join(...)) + 1` and call it a day — the whole point is
> to handle the **carry by hand**, exactly like grade-school addition. For huge inputs
> (hundreds of digits) the integer trick also overflows in languages without bignums.

## Real-World Analogy

Socho tum ek **car ka odometer** ho. Number badhana hai by one. Tum sabse right wale
digit (ones place) se shuru karte ho. Agar wo `9` se kam hai — easy, bas usse `+1` kar do,
kaam khatam. Lekin agar wo `9` hai, to wo `0` ho jaata hai aur ek **carry** left me chala
jaata hai (`...9` → `...0` plus "ek aur seedhe left wale ko"). Yeh carry tab tak left
travel karta hai jab tak koi non-9 digit nahi mil jaata. Aur agar **saare hi 9 the**
(jaise `999`), to carry poore number se bahar nikal jaata hai aur ek naya leading `1` lag
jaata hai — odometer `999 → 1000`. Bas yahi puri kahani hai.

## Approach

Right-to-left ek hi pass. Har digit pe carry handle karo:

1. Last digit se shuru karo. Agar wo `< 9` hai → bas `+1` karke turant return (no carry, done).
2. Agar wo `9` hai → usse `0` set karo aur left wale digit pe move karो (carry propagate).
3. Loop khatam ho gaya bina early return ke → matlab saare 9 the → front me ek `1` prepend.

```python
def plus_one(digits):
    for i in range(len(digits) - 1, -1, -1):   # right -> left
        if digits[i] < 9:
            digits[i] += 1                       # no carry, done early
            return digits
        digits[i] = 0                            # 9 -> 0, carry travels left
    return [1] + digits                          # all were 9: 999 -> 1000
```

Pattern: **digit-array carry propagation** — wahi school-wala addition, sirf base 10 me, ek array pe.

## Complexity

- **Time:** O(n) — worst case (all 9s) puri array touch karte hain. Best case O(1) (last digit `< 9`).
- **Space:** O(1) extra normally (in-place). Sirf all-9s case me O(n) naya array banta hai (`[1, 0, ...]`).

## Common Pitfalls

- **All-9s case bhulna** — `[9,9,9]` ko handle na karne pe answer galat ya crash. Loop ke baad
  `[1] + digits` zaroori hai.
- **Galat direction** — carry **right se left** chalta hai (least → most significant). Left se
  shuru karoge to logic ulta ho jaayega.
- **`int(...)` shortcut pe atak jaana** — chhote inputs pe chalega, but interviewer manual carry
  dekhna chahta hai; bignum-free languages me overflow bhi hota hai.
- **Early return miss karna** — agar `< 9` case pe turant return nahi kiya, to baaki digits ko
  bewajah touch karoge (correctness to theek, but intent kamzor lagta hai).
- **Leading zero** — `[1] + digits` me `digits` already saare `0` ho chuke hain, isliye result
  `[1,0,0,...]` clean banta hai — bas prepend `1`, naya leading digit kabhi `0` nahi hoga.

## When to Use This Pattern

Jab "number ko digit-array me represent karke us pe arithmetic karna ho" — big-integer add,
multiply, increment, ya base-conversion — to socho: **right-to-left scan + carry**. Cue:
"digits given as a list, MSB first" ya "number itna bada ki int me na samaye". Cousins:
Add Two Numbers (linked list), Multiply Strings, Add Binary.

## NeetCode Link

https://neetcode.io/problems/plus-one
