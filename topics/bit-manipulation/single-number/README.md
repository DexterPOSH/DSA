# Single Number

**Category:** Bit Manipulation
**Difficulty:** easy

## Problem Statement

Given a non-empty array `nums` where **every element appears exactly twice except one**, find that single element. Do it in **O(n) time** and **O(1) extra space**.

```
[4, 1, 2, 1, 2]  ->  4
[2, 2, 1]        ->  1
[7]              ->  7
```

## Real-World Analogy

**What Azure Blob Storage is:** Azure Blob Storage is Azure's object storage service for unstructured data such as files, backups, logs, and media. Block blobs store large objects as blocks, and Azure stores data redundantly for durability.

**What checksum reconciliation is, and why it's used:** Storage systems use compact checksums, such as MD5 or CRC64, to verify that a block's bytes still match what was written. In a simplified integrity sweep, every healthy block checksum report appears as a matching pair, while one suspect checksum appears without its mate. Reconciliation uses those fingerprints because comparing small checksum values is cheaper than rereading and byte-comparing every full block.

**The mapping:** The XOR accumulator is the Azure Blob Storage sweep's running parity value. Each duplicate checksum cancels itself because `x ^ x = 0`, and starting from zero preserves any checksum that does not find a pair because `x ^ 0 = x`. The key insight is that all paired block fingerprints vanish, leaving the one unpaired checksum that identifies the odd block to investigate.

## Approach

XOR ki teen properties yaad rakho — yahi poora trick hai:

- `x ^ x = 0`   (apne aap se XOR = 0, pair cancel)
- `x ^ 0 = x`   (zero ke saath XOR khud)
- XOR **commutative + associative** hai — order matter nahi karta, so saare duplicates apne-aap pair ho jaate hain chahe array me kahin bhi ho.

Bas ek accumulator ko 0 se start karo aur har element ko usme XOR karte jao:

```python
def single_number(nums):
    result = 0
    for n in nums:
        result ^= n
    return result
```

Ek-liner: `from functools import reduce; reduce(xor, nums, 0)` — but interview me loop likh do, intent clear rehta hai.

> Brute force (hash map se count karna) bhi O(n) time hai but O(n) **space** leta. XOR ka magic yeh hai ki space O(1) ho jaata — koi extra structure nahi.

## Complexity

- **Time:** O(n) — ek single pass, har element ko ek baar XOR.
- **Space:** O(1) — sirf ek integer accumulator, input size se independent.

## Common Pitfalls

- **Hash map / sorting pe chala jaana** — woh kaam karta hai par O(n) space ya O(n log n) time. Interviewer "O(1) space" bolega to XOR hi expected hai.
- **`result` ko 0 ke alawa kisi value se initialize karna** — 0 hi XOR ka identity hai; kuch aur loge to answer corrupt.
- **Problem assumption tod-na** — yeh trick *tabhi* chalti hai jab baaki sab elements **exactly do baar** aate hain. Agar koi teen baar aaye (Single Number II), simple XOR fail karta — wahan bit-count-mod-3 ya `~(ones | twos)` wali technique lagti.
- **Negative numbers ka darr** — XOR two's-complement bits pe chalta hai, negatives bhi sahi handle hote, koi special case nahi.

## When to Use This Pattern

Jab dikhe **"sab kuch paired/even occurrences me hai, sirf ek odd hai"** aur O(1) space chahiye → turant XOR socho. Cue words: "appears twice except one", "find the unique", "no extra memory". Cousins: missing number (`XOR of 0..n with the array`), find-the-difference, swap-without-temp.

## NeetCode Link

https://neetcode.io/problems/single-number
