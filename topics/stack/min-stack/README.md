# Min Stack

**Category:** Stack
**Difficulty:** medium

## Problem Statement

Design a stack that supports `push`, `pop`, `top`, and retrieving the **minimum
element** — all in **O(1)** time.

Implement the `MinStack` class:
- `push(val)` — push `val` onto the stack
- `pop()` — remove the element on top
- `top()` — get the top element
- `getMin()` — retrieve the minimum element currently in the stack

```
push(-2); push(0); push(-3)
getMin()  ->  -3
pop()
top()     ->  0
getMin()  ->  -2
```

## Real-World Analogy

Socho ek **stack of receipts** hai aur har receipt ke saath tum ek chhota
sticky-note bhi chipka dete ho jisme likha hai: *"is receipt tak ka sabse sasta
amount"*. Jab nayi receipt rakhte ho, to uska sticky-note banta hai =
`min(nayi receipt ka amount, neeche wali receipt ka sticky-note)`. Ab kabhi bhi
"sabse sasta kitna?" puchho — bas **sabse upar wala sticky-note** padh lo, O(1).
Aur jab receipt uthaoge, uska sticky-note bhi saath chala jayega, to neeche wala
sticky-note automatically sahi minimum dikhayega. Koi scan nahi, koi search nahi.

## Approach

Naive idea: ek normal stack rakho aur `getMin` pe poora stack scan karo → O(n).
Problem `getMin` ko O(1) maangta hai, to har element ke saath "us point tak ka min"
bhi store karna padega.

Pattern: **auxiliary / paired stack**. Do approaches:

**(a) Two stacks** — ek `stack` values ke liye, ek `min_stack` jiska top hamesha
current minimum hai.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []          # min_stack[-1] == min of everything below

    def push(self, val):
        self.stack.append(val)
        m = val if not self.min_stack else min(val, self.min_stack[-1])
        self.min_stack.append(m)

    def pop(self):
        self.stack.pop()
        self.min_stack.pop()          # keep them in lock-step

    def top(self):
        return self.stack[-1]

    def getMin(self):
        return self.min_stack[-1]
```

Dono stacks lock-step me chalte hain — har push do push, har pop do pop. `min_stack`
ka top = poore stack ka minimum, isliye `getMin` sirf ek array-index read hai.

**(b) One stack of tuples** — har element ke saath `(val, current_min)` push karo.
Same idea, ek hi list me: `self.stack.append((val, min(val, self.stack[-1][1])))`.

## Complexity

- **Time:** O(1) for **every** operation — push/pop/top/getMin sab constant; bas
  array append/pop aur top read.
- **Space:** O(n) — har value ke saath ek extra min value store hoti hai (dusra
  stack ya tuple ka dusra field).

## Common Pitfalls

- **`min_stack` ko sync me na rakhna** — agar `push` pe sirf "naya val chhota ho to
  hi" push karo wali optimization karo, to `pop` ka logic conditional ho jaata aur
  duplicates pe galti hoti. Beginner ke liye lock-step (har push pe min_stack me bhi
  push) sabse safe hai.
- **`getMin` pe scan karna** — `min(self.stack)` likhna O(n) hai, requirement O(1) ki
  hai. Yahi poora point hai is problem ka.
- **Equal-to-min element pop karna** — agar tum sirf "strictly smaller" min push karte
  ho, to do baar same minimum value push hone par pop pe min galat ho jaata. Lock-step
  ya `<=` use karo.
- **Empty stack pe `top`/`getMin`** — assume karo calls valid hain (LeetCode guarantee
  deta), but interview me edge case bata dena.

## When to Use This Pattern

Jab data structure se ek **aggregate** (min / max / running stat) constant time me
chahiye ho aur underlying structure LIFO/FIFO ho → **auxiliary structure** rakho jo
us aggregate ko har step pe maintain kare. Cousins: Max Stack, Min Queue (monotonic
queue), sliding-window maximum. Cue: *"O(1) min/max alongside push/pop"* → paired
stack.

## NeetCode Link

https://neetcode.io/problems/minimum-stack
