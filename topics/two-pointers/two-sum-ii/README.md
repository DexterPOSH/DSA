# Two Sum II — Input Array Is Sorted

**Category:** Two Pointers
**Difficulty:** medium

## Problem Statement

Given a **1-indexed**, **sorted (ascending)** array `numbers` and a `target`,
return the two indices `[i, j]` (1-based, `i < j`) such that
`numbers[i] + numbers[j] == target`. Exactly one solution exists, and you may
**not** use the same element twice.

```
numbers = [2, 7, 11, 15], target = 9   ->  [1, 2]   # 2 + 7 = 9
numbers = [2, 3, 4],       target = 6   ->  [1, 3]   # 2 + 4 = 6
numbers = [-1, 0],         target = -1  ->  [1, 2]
```

## Real-World Analogy

Socho ek **taraazu (balance scale)** hai. Tum sabse halke item ko left palde me
rakhte ho aur sabse bhaari ko right palde me. Ab sum dekho:

- **Bahut zyada hai** (target se upar)? To right side se ek halka item lo — sabse
  bhaari ko hata kar uske just-chhote se replace karo. `r -= 1`.
- **Bahut kam hai**? To left side se ek bhaari item lo — sabse halke ko hata kar
  uske just-bade se replace karo. `l += 1`.

Kyunki array **sorted** hai, tumhe pata hai har taraf "halka" aur "bhaari" kahaan
milega — bina poora dhundhe. Jab sum bilkul target ke barabar ho jaaye, mil gaya
jodaa.

## Approach

Pattern: **two pointers on a sorted array** (converging). Sorted hone ki property
hi yahaan magic hai — ek pointer move karke sum ko predictably bada/chhota kar
sakte ho.

```python
def two_sum(numbers, target):
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]   # 1-indexed
        elif s < target:
            l += 1                  # need bigger -> move left up
        else:
            r -= 1                  # need smaller -> move right down
    return []                       # problem guarantees a solution
```

> **Brute force** har pair check karta (O(n²)). **Hash map** bhi O(n) time deta
> par O(n) space leta. Sorted array pe two-pointer **O(1) space** me kaam karta —
> yahi is variant ka point hai.

## Complexity

- **Time:** O(n) — `l` aur `r` ek saath beech ki taraf chalte hain, har element
  at most ek baar visit.
- **Space:** O(1) — sirf do pointers, koi extra structure nahi.

## Common Pitfalls

- **0-indexed return karna** — yeh variant **1-indexed** answer maangta hai
  (`[l+1, r+1]`). Classic galti.
- **`l <= r` likhna** — same element do baar use ho jaayega (`numbers[l]` jab
  `l == r`). Strictly `l < r` rakho.
- **Sorted hone ka faayda na uthana** — agar tum yahaan bhi hash map use karte ho
  to space waste karte ho; interviewer specifically O(1) space dekhna chahta.
- **Overflow (other languages)** — Python me nahi, par Java/C++ me `numbers[l] +
  numbers[r]` int overflow kar sakta — `long` use karo.

## When to Use This Pattern

Jab array **already sorted** ho aur "do elements dhundo jinka sum/diff/product = X"
ho → **opposite-end two pointers**. Yeh 3Sum aur 4Sum ka building block hai (outer
loop fix karke andar two-sum chalao). Cue: sorted + pair-with-condition.

## NeetCode Link

https://neetcode.io/problems/two-integer-sum-ii
