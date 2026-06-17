# Longest Consecutive Sequence

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given an unsorted integer array `nums`, return the length of the **longest run of consecutive integers** (e.g. `4, 5, 6, 7`). The numbers can appear in any order in the array. You must do it in **O(n)** time.

```
nums = [100, 4, 200, 1, 3, 2]   ->  4    # the run 1,2,3,4 has length 4
nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]  ->  9   # 0..8
```

## Real-World Analogy

Socho ek bag me bohot saare numbered tickets bikhre pade hain, random order me. Tumhe sabse lambi unbroken chain dhoondhni hai (jaise `5,6,7,8`). Sort karna ek option hai par O(n log n). Smart tareeka: pehle saare tickets ko ek bade table pe daal do taaki **ek nazar me pata chale ki koi number maujood hai ya nahi** (yeh hash set hai). Ab chain dhoondhne ke liye sirf un tickets se shuru karo jo **chain ke "start" hain** — yaani jinka *ek kam wala* (`n-1`) table pe maujood hi nahi. Aise hi ek start mila, to `n, n+1, n+2…` count karte jao jab tak agla number table pe milta rahe. Sirf starts se chalne ki wajah se har number maximum ek hi baar visit hota hai — isliye poora kaam O(n) me.

## Approach

Naive: sort karke adjacent compare karo → O(n log n). Hum O(n) chahte hain.

**Optimal — hash set + start-of-run detection** (O(n)):

1. Saare numbers ko ek `set` me daalo → O(1) membership checks.
2. Har number `n` ke liye check karo: kya `n - 1` set me **nahi** hai? Agar nahi hai, to `n` kisi run ka **start** hai.
3. Sirf starts se forward count karo: `n, n+1, n+2…` jab tak `set` me milta hai. Length track karo, max update karo.

```python
def longest_consecutive(nums):
    num_set = set(nums)
    longest = 0

    for n in num_set:
        if n - 1 not in num_set:          # n is the start of a run
            length = 1
            while n + length in num_set:  # walk the run forward
                length += 1
            longest = max(longest, length)
    return longest
```

Crucial: inner `while` sirf tab chalta hai jab `n` ek start ho. Isliye har number ke aage poori chain me ek hi baar walk hota hai — overall O(n), n² nahi. Pattern: **hash set + only-extend-from-boundaries**.

## Complexity

- **Time:** O(n) — set banana O(n); har number ka `n-1` check O(1); aur inner while loop total milake har element ko at most ek baar touch karta hai (kyunki sirf run-starts se chalta hai).
- **Space:** O(n) — saare numbers set me.

## Common Pitfalls

- **Start-check chhod dena** — agar har number se forward count karoge (start-check ke bina), to inner loop bar-bar overlapping chains chalega → **O(n²)**. `if n - 1 not in set` hi O(n) banata hai.
- **Sorting kar dena** — sahi answer deta hai par O(n log n); interviewer aksar O(n) explicitly maangta hai.
- **Duplicates** — `set` automatically dedupe kar deta hai, isliye duplicate numbers length inflate nahi karte. (List use karoge to bug.)
- **Empty array** — `longest = 0` se shuru karo taaki empty input pe `0` mile.
- **`while n + length in num_set` me index/value confuse karna** — yahan `n + length` *value* hai jo set me dhoondhte hain, koi array index nahi.

## When to Use This Pattern

Jab unsorted data me **"longest consecutive / contiguous run"** ya **"kya elements ek continuous range banate hain"** dhoondhna ho bina sort kiye — socho **hash set + extend-only-from-boundaries**. Trick yahi hai: O(1) membership ke liye set me daalo, aur kaam sirf boundaries (run-starts) se shuru karke har element ko ek hi baar process karo.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough that finds run-starts and walks each chain forward.

## NeetCode Link

https://neetcode.io/problems/longest-consecutive-sequence
