# Multiply Strings

**Category:** Math & Geometry
**Difficulty:** medium

## Problem Statement

Given two non-negative integers `num1` and `num2` represented as **strings**, return their
product, **also as a string**. You must not use any built-in BigInteger library or convert
the inputs directly to an integer.

```
"2"   × "3"    ->  "6"
"123" × "456"  ->  "56088"
"99"  × "99"   ->  "9801"
"0"   × "anything" -> "0"
```

> The "no int conversion" rule is the whole point: the numbers can be **hundreds of digits
> long**, so you implement **grade-school long multiplication** digit by digit.

## Real-World Analogy

Yaad hai school me **long multiplication** kaise karte the? `123 × 456`: pehle `123 × 6`,
phir `123 × 5` (ek jagah left shift), phir `123 × 4` (do jagah left shift), aur sab ko jod
do. Hum bilkul wahi kar rahe hain — par ek clean trick ke saath.

Socho ek **multiplication grid** banate ho. `num1` ke har digit `i` ko `num2` ke har digit
`j` se multiply karte ho. Yahan magic insight hai: **digit `i` aur digit `j` ka product hamesha
result ke position `i + j` (aur carry `i + j + 1`) pe jaata hai** — agar dono numbers ke
digits right se number kiye jaayein... actually hum left-indexed strings use karenge to position
`i + j + 1` (low) aur `i + j` (carry). Yeh "position = sum of indices" wali baat hi pura
bookkeeping simple kar deti hai — koi alag shifting handle nahi karni, sab ek flat array me
sahi jagah gir jaata hai.

## Approach

Ek result array banao size `len(num1) + len(num2)` (do n-digit numbers ka product **at most**
itne digits ka hota hai). Phir har pair `(i, j)` ka product us array me sahi position pe add karo,
carry handle karte hue.

```python
def multiply(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"
    n, m = len(num1), len(num2)
    res = [0] * (n + m)                       # max possible digits

    for i in range(n - 1, -1, -1):            # right to left over num1
        for j in range(m - 1, -1, -1):        # right to left over num2
            mul = (ord(num1[i]) - 48) * (ord(num2[j]) - 48)
            low = i + j + 1                    # units position of this product
            total = mul + res[low]            # add into existing partial
            res[low] = total % 10             # keep the digit
            res[i + j] += total // 10         # carry to the left neighbour

    out = "".join(map(str, res)).lstrip("0")  # drop leading zeros
    return out or "0"
```

The key invariant: **`num1[i] * num2[j]` contributes to `res[i+j+1]` (low digit) and carries
into `res[i+j]`**. Saare partial products usi flat array me accumulate ho jaate hain — koi alag
padded strings add nahi karni.

Pattern: **digit-array long multiplication with positional accumulation**.

## Complexity

- **Time:** O(n · m) — har digit-pair exactly ek baar process hota hai (n = len(num1), m = len(num2)).
- **Space:** O(n + m) — result array. (Karatsuba O(n^1.585) tak utar sakta hai, but interview me
  ye grid solution expected hai.)

## Common Pitfalls

- **Zero case bhulna** — `"0" × "..."` agar handle na karo to result `"000..."` ban ke `lstrip("0")`
  ke baad **empty string** reh jaata hai. Early-return `"0"` ya `out or "0"` zaroori.
- **Galat position formula** — `i + j` vs `i + j + 1` me confuse hona sabse common bug. Left-indexed
  strings ke liye: low digit `i+j+1`, carry `i+j`.
- **Result array ka size galat** — `n + m` chahiye. `max(n, m)` ya `n + m - 1` lene pe overflow.
- **Carry ko purane value me add na karna** — `total = mul + res[low]` me **existing** partial ko
  add karna zaroori (pichhle pairs ne already kuch likha ho sakta hai).
- **Leading zeros** — `res` me front me extra `0` aa sakte (jab product ke digits `n+m` se kam ho);
  `lstrip("0")` se hata do, par phir empty-string guard rakho.
- **`int(num1) * int(num2)` likh dena** — problem explicitly mana karta hai; aur bade inputs pe
  conversion-free hi expected hai.

## When to Use This Pattern

Jab "arbitrary-precision arithmetic on number-strings/arrays" — multiply, add, power of big
numbers — aur built-in bignum allowed na ho. Cue: "numbers as strings", "up to N digits", "no
BigInteger". The positional `i+j` trick generalize hota hai polynomial multiplication tak (FFT
isi ka fast version hai). Cousins: Add Strings, Plus One, Add Two Numbers.

## NeetCode Link

https://neetcode.io/problems/multiply-strings
