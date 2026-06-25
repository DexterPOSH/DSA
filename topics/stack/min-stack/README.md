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

**What Azure Resource Manager (ARM) is:** Azure Resource Manager is Azure's control plane for deploying and updating resources from templates, Bicep files, CLI calls, and SDKs. During a deployment, ARM coordinates many resource operations, tracks their status, and exposes deployment-operation history so you can audit and debug what happened. Think of the active deployment work as a LIFO stack of operations being entered and then unwound.

**What deployment-operation tracking is, and why it's used:** ARM deployment operations record details such as the target resource, operation type, status, timing, and errors. That tracking exists because when a deployment fails, you need to know not just the latest action, but the context around the work that was active at that moment. In this analogy, we attach one extra piece of metadata to that operation history: the lowest priority/risk score seen so far, maintained in a separate running-minimum stack rather than recomputed by scanning all active operations.

**The mapping:** The main stack stores the Azure ARM operations in normal LIFO order, while `min_stack` stores the minimum score that was true after each corresponding push. On `push(val)`, append the operation and also append `min(val, previous_min)`; on `pop()`, remove both entries together so the previous minimum is restored automatically. `top()` reads the current operation, and `getMin()` reads the top of the auxiliary stack in O(1). The key insight is lock-step metadata: every stack depth carries its own minimum snapshot, so unwinding never needs a full scan.

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
