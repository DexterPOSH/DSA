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

**What Azure Durable Functions is:** Azure Durable Functions is Azure's serverless workflow service for long-running orchestrations. It coordinates functions across waits, retries, timers, and external calls while persisting enough history to recover if a worker restarts. A durable workflow moves from one deterministic state to the next until it reaches a terminal state.

**What deterministic orchestration replay is, and why it's used:** Durable Functions replays orchestration history to rebuild workflow state instead of keeping everything only in memory, so orchestrator logic must behave deterministically. If the same state transition keeps reappearing, the workflow is cycling through history rather than making progress toward success. Replay exists to make Azure workflows reliable and resumable, and loop detection tells you when a deterministic process will never reach its success state.

**The mapping:** The number `n` is the Azure orchestration state, and replacing it with the sum of squared digits is the deterministic transition to the next state. Reaching `1` is the terminal success state; seeing a previous number again means the workflow is stuck in a cycle. Floyd's slow and fast pointers act like two replay cursors moving through the same state history, and the key insight is that a deterministic process either reaches `1` or repeats, so a cycle proves the number is not happy without storing every state.

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
