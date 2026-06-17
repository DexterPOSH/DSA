# Happy Number

**Category:** Math & Geometry
**Difficulty:** easy

## Problem Statement

A number is **happy** if you repeatedly replace it with the **sum of the squares of its digits**, and eventually reach `1`. If instead you fall into a loop that never reaches `1`, it's **not happy**.

```
n = 19  ->  True
  1² + 9²            = 82
  8² + 2²            = 68
  6² + 8²            = 100
  1² + 0² + 0²       = 1   -> happy!

n = 2   ->  False   (4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4 -> ... loops)
```

## Real-World Analogy

Socho tum ek city me ghoom rahe ho aur har chauraahe pe ek fixed rule batata hai ki **agla kahaan jaana hai** (digit-square-sum). Do hi possibilities hain: ya to tum manzil "1" pe pahunch jaaoge (happy), ya phir ek **roundabout me phans jaaoge** jahaan se baar-baar wahi chauraahe aate rehte hain (loop, never reaching 1). Sawaal sirf yeh hai: kya tum kabhi pehle dekhe hue chauraahe pe **dobara** aa gaye? Agar haan — tum ek cycle me ho, 1 kabhi nahi milega. Yeh exactly **cycle detection** hai, jaise linked list me.

## Approach

Key insight: yeh process ya `1` pe rukta hai ya kisi cycle me ghoomta hai (kabhi infinitely badhta nahi — digit-square-sum bounded rehta hai). To bas **cycle detect** karna hai.

**Approach 1 — hash set (seen numbers yaad rakho):**

```python
def is_happy(n):
    def square_sum(x):
        s = 0
        while x:
            x, d = divmod(x, 10)
            s += d * d
        return s
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = square_sum(n)
    return n == 1
```

Agar `n == 1` mila → happy. Agar pehle dekha hua number dobara aaya → cycle → not happy.

**Approach 2 — Floyd's cycle detection (O(1) space, fast & slow pointers):** linked-list-cycle wali trick. `slow` ek step, `fast` do steps; agar dono milte hain to cycle, aur woh meeting point `1` hai ya nahi se answer.

```python
def is_happy(n):
    def sq(x):
        return sum(int(d) ** 2 for d in str(x))
    slow, fast = n, sq(n)
    while fast != 1 and slow != fast:
        slow = sq(slow)
        fast = sq(sq(fast))
    return fast == 1
```

## Complexity

- **Time:** O(log n) per digit-sum step; number of steps tak pahunchne ke liye bhi effectively O(log n) — sequence quickly chhote bounded numbers (< 1000) me gir jaata hai.
- **Space:** O(log n) for the hash set approach (kitne unique numbers dekhe), ya **O(1)** Floyd's two-pointer approach se.

## Common Pitfalls

- **Infinite loop without cycle detection** — agar tum bas "1 milne tak" chalाte ho aur seen-set ya fast/slow nahi rakhte, to unhappy numbers pe program hamesha ke liye atak jaata hai.
- **Digit extraction galat** — `divmod(x, 10)` se last digit aur baaki number; ya `str(x)` pe loop. Square karna mat bhulo (sum of squares, sirf sum nahi).
- **`n == 1` ko bhi happy** maानना — base case theek se handle ho.
- **Floyd's me fast ko do baar advance karna bhulna** — `fast = sq(sq(fast))`, ek nahi.

## When to Use This Pattern

Jab koi process "ek state se agli state pe deterministically jump karta hai, aur tumhe poochhna hai kya woh terminate hota hai ya loop karta hai" — to **cycle detection** socho: hash set (seen states) for simplicity, ya Floyd's fast/slow for O(1) space. Cousins: Linked List Cycle, Find the Duplicate Number, functional-graph problems. Cue: "repeat a transformation; does it converge or loop?"

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the digit-square-sum sequence and cycle detection.

## NeetCode Link

https://neetcode.io/problems/non-cyclical-number
