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

**What Azure Event Hubs is:** Azure Event Hubs is Azure's high-throughput event-ingestion and streaming service for telemetry, logs, and clickstreams. It shards each event hub into partitions, which are ordered lanes of events that let consumers process data in parallel. Azure Resource Graph gives operators a searchable inventory of Azure resources, which is useful for reconciliation jobs that compare expected state with actual state.

**What a partition manifest is, and why it's used:** An Event Hubs deployment can have a manifest saying which partition IDs should exist, while the observed Azure inventory lists which IDs were actually discovered. Keeping IDs as a complete sequence makes routing and consumer assignment predictable; a gap means one partition lane is missing from the configuration. Reconciliation exists to find that gap automatically instead of manually inspecting every ID.

**The mapping:** The expected sequence `0..n` is the desired Event Hubs partition manifest, and `nums` is the actual Azure inventory snapshot. XORing both lists cancels every ID that appears in both places because `x ^ x = 0`; the sum formula compares expected and actual totals to find the same gap. The key insight is that matched IDs vanish, so the only value left is the missing partition number.

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
