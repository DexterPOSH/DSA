# Two Sum

**Category:** Arrays & Hashing
**Difficulty:** easy

## Problem Statement

Given an array of integers `nums` and an integer `target`, return the **indices** of the two numbers that add up to `target`. Exactly one valid pair exists, and you can't use the same element twice.

```
nums = [2, 7, 11, 15], target = 9   ->  [0, 1]   # 2 + 7 == 9
nums = [3, 2, 4],       target = 6   ->  [1, 2]   # 2 + 4 == 6
```

## Real-World Analogy

Socho tum ek shop pe ho aur tumhare paas exactly ₹9 ka discount coupon hai jo tabhi chalega jab do items ka total exactly ₹9 ho. Naive tareeka — har item utha ke baaki sab se compare karo, thaka dene wala. Smart cashier kya karta hai? Har item dekhte waqt wo sochta hai: *"is item ki price ₹2 hai, mujhe ₹9 banane ke liye ₹7 wala item chahiye"* — aur turant apni mental note (ek diary jisme "kaunsi price kahan dikhi") me check karta hai ki ₹7 pehle aa chuka hai ya nahi. Wo diary hi hamara **hash map** hai: har number ke saath uska **complement** yaad rakho, aur ek hi pass me jodi mil jaati hai.

## Approach

**Brute force** — har pair try karo (O(n²)):

```python
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
```

**Optimal — hash map (one pass)** (O(n)):

Idea simple hai — har number `n` ke liye hume `target - n` (complement) chahiye. Array pe chalte chalte ek dictionary `seen` maintain karo jo *value -> index* map karti hai. Har number pe pehle check karo ki uska complement already `seen` me hai kya; agar hai to jodi mil gayi, indices return karo. Nahi to current number ko `seen` me daal do aur aage badho.

```python
def two_sum(nums, target):
    seen = {}                      # value -> index
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []                      # problem guarantees a pair, par safe rahna
```

Pattern: **hash map for complement lookup** — ek hi pass, har lookup O(1).

## Complexity

- **Time:** O(n) — array ko sirf ek baar scan karte hain, har dictionary lookup/insert O(1) average.
- **Space:** O(n) — worst case me poora array `seen` me chala jaata hai (jodi last me milti hai).

## Common Pitfalls

- **Same element do baar use kar dena** — `complement in seen` ko *current* number add karne se **pehle** check karna zaroori hai. Tabhi tum apne aap se add nahi karoge (e.g. `target = 2*n`).
- **Values vs indices** — problem indices maangta hai, values nahi. Dictionary me value -> index store karo, ulta nahi.
- **Duplicate values** — agar `nums` me same value do baar hai (jaise `[3, 3]`, target `6`), to value -> index map sahi kaam karta hai kyunki tum complement ko pehle dekhe gaye index se match karte ho.
- **Sorting karke two-pointer** — chalega aur O(1) extra space deta hai, par sort ke baad original indices kho jaate hain (alag se track karne padte hain). Jab indices chahiye, hash map cleaner hai.

## When to Use This Pattern

Jab dikhe *"do (ya k) elements dhoondho jinka koi relation/sum/diff target ke barabar hai"* — turant socho **hash map of complements**. "Pair that sums to X", "do numbers ka difference k hai", "kya koi a aisa hai ki target-a maujood ho" — ye sab one-pass hash lookup se O(n) me hote hain, O(n²) nested loop ki zaroorat nahi.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the one-pass hash map approach.

## NeetCode Link

https://neetcode.io/problems/two-integer-sum
