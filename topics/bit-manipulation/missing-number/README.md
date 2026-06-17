# Missing Number

**Category:** Bit Manipulation
**Difficulty:** easy

## Problem Statement

Given an array `nums` containing `n` distinct numbers taken from the range `[0, n]`, return the **one number in that range that is missing** from the array.

```
[3, 0, 1]        ->  2     # range is [0,3], 2 is absent
[0, 1]           ->  2     # range is [0,2], 2 is absent
[9,6,4,2,3,5,7,0,1] -> 8   # range is [0,9], 8 is absent
```

> Array me `n` numbers hain but range `[0, n]` me `n+1` possible values hain — to thik ek value gayab hai. Wahi return karni hai, ideally O(n) time aur O(1) extra space me.

## Real-World Analogy

Socho ek classroom me roll numbers `0` se `n` tak hone chahiye, par ek student absent hai. Tum do tarah se pata laga sakte ho:

1. **Sum wala tarika** — pehle se pata hai ki agar sab present hote to roll numbers ka total kitna hota (`0+1+...+n`). Phir jo students actually present hain unke roll numbers jod do. Dono ka **difference** = absent student ka roll number. Seedha ghatao, ho gaya.
2. **XOR wala tarika** — har expected roll number ko ek "switch" maano. Tum pehle saare expected `0..n` ko ek baar flip karte ho, phir saare present roll numbers ko dobara flip karte ho. Jo number dono jagah aaya (expected + present) wo do baar flip hua → wapas off. Sirf absent number ek hi baar flip hua → on reh gaya. Wahi answer hai.

XOR wala tarika overflow-proof hai, isliye interview me thoda zyada elegant maana jaata hai.

## Approach

**Approach 1 — Gauss sum** (O(n), simple, par bade `n` pe overflow ho sakta hai non-Python languages me):

```python
def missing_number(nums):
    n = len(nums)
    expected = n * (n + 1) // 2     # 0 + 1 + ... + n
    return expected - sum(nums)
```

**Approach 2 — XOR** (O(n), no overflow, pattern: *self-canceling XOR*):

XOR ke do magic properties yaad rakho:
- `x ^ x = 0` (koi number apne aap se XOR kare to gayab)
- `x ^ 0 = x` (0 se XOR kuch nahi badalta)

To agar hum index aur values dono ko ek saath XOR kar dein, har wo number jo **index bhi hai aur value bhi** wo pair me cancel ho jaata hai. Sirf missing number bachta hai (uska index aaya par value kabhi nahi aayi):

```python
def missing_number(nums):
    res = len(nums)                 # start with n (the top of the range)
    for i, num in enumerate(nums):
        res ^= i ^ num              # cancel matching index/value pairs
    return res
```

`res` ko `n` se start karte hain kyunki index `0..n-1` tak hi jaata hai, par range `0..n` hai — to top value `n` ko manually seed karna padta hai.

## Complexity

| Approach | Time | Space | Why |
|----------|------|-------|-----|
| Sort + scan | O(n log n) | O(1) | Adjacent gap dhoondo |
| Gauss sum | O(n) | O(1) | Ek formula + ek pass |
| **XOR** | **O(n)** | **O(1)** | Ek pass, pairs cancel ho jaate hain, koi overflow nahi |

- **Time:** O(n) — har element ko thik ek baar touch karte hain.
- **Space:** O(1) — sirf ek accumulator (`res`), koi extra array/set nahi.

## Common Pitfalls

- **Range off-by-one** — range `[0, n]` hai (inclusive), to `n+1` possible values hain magar array me sirf `n`. `res` ko `n` se seed karna mat bhoolo, warna top value miss ho jaayegi.
- **Sum overflow** — Python me int unbounded hai to safe, par Java/C++ me `n*(n+1)/2` 32-bit overflow kar sakta hai. Interview me ye bolo aur XOR ya `(expected - actual)` running difference suggest karo.
- **Set bana dena** — `set(range(n+1)) - set(nums)` chalega par O(n) extra space leta hai; XOR/sum O(1) me kaam karta hai.
- **XOR ko `n-1` se seed karna** — common galti. Seed `n` hona chahiye (`len(nums)`), na ki last index.

## When to Use This Pattern

Jab "ek element gayab/extra hai" ya "har element exactly do baar except one" type problems dikhe — XOR ka self-canceling property socho. Cue: *paired elements cancel, the odd one out survives*. Cousins: **Single Number**, **Find the Duplicate**, **Two Single Numbers**. Jab range bounded aur known ho (`0..n`) to sum/XOR dono O(1)-space tricks ban jaati hain.

## Visual

Open [visual.html](visual.html) in your browser for an interactive bit-cell walkthrough of the XOR approach.

## NeetCode Link

https://neetcode.io/problems/missing-number
