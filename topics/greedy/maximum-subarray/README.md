# Maximum Subarray

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, find the **contiguous subarray** (containing at least one number) with the **largest sum**, and return that sum.

```
[-2, 1, -3, 4, -1, 2, 1, -5, 4]   ->   6     # subarray [4, -1, 2, 1]
[5, 4, -1, 7, 8]                  ->   23    # whole array
[-3, -1, -2]                      ->   -1    # best is the single element -1
```

> "Contiguous" matters — you cannot skip elements. The answer is one unbroken slice.

## Real-World Analogy

Socho tum ek road-trip pe ho aur har stretch pe ya to paisa kamate ho (positive) ya kharch karte ho (negative). Tumhe sabse profitable **continuous stretch** dhoondhna hai.

Tum drive karte jaate ho aur ek "running profit" maintain karte ho. Simple rule: **agar abhi tak ka running profit negative ho gaya, to use carry mat karo — wahi se fresh start lo.** Kyun? Kyunki ek negative baggage ko aage le jaane se aane wale har stretch ka total *kam* hi hoga. Better hai ki "abhi tak ka loss bhool jao" aur naya count yahin se shuru karo. Saath hi saath, ab tak ka best-ever profit ek diary me note karte raho. Yahi Kadane's algorithm hai.

## Approach

**Brute force** — har possible subarray ka sum (O(n²)): har start `i` se har end `j` tak loop. Slow.

**Optimal — Kadane's algorithm** (O(n), greedy/DP):

Do running values rakho:
- `cur` = sabse bada subarray-sum jo **abhi current index pe khatam** hota hai.
- `best` = ab tak dekha gaya overall maximum.

Har element pe ek greedy choice: kya is element ko pichle `cur` ke saath jodu, ya isi element se naya subarray shuru karu?

```python
def max_subarray(nums):
    cur = best = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)   # extend ya fresh start — greedy decision
        best = max(best, cur)   # overall best ko update karte raho
    return best
```

`cur = max(x, cur + x)` hi poora khel hai. Agar `cur + x < x`, matlab pichla `cur` negative tha aur bojh ban raha tha → drop it, `x` se fresh start. `best` ko side me track karte raho kyunki maximum kahin beech me bhi aa sakta hai (end pe nahi).

## Complexity

- **Time:** O(n) — ek hi pass, har element pe constant work.
- **Space:** O(1) — sirf do scalar variables, koi extra array nahi.

## Common Pitfalls

- **`best = 0` se initialize karna** — agar saare numbers negative ho (`[-3, -1, -2]`), to galat `0` return karoge. Hamesha `nums[0]` se init karo, kyunki subarray me kam se kam ek element hona hi chahiye.
- **`cur` ko negative jaane dena aur carry karna** — `max(x, cur + x)` ka pehla argument (`x`) hi yeh reset handle karta hai. Bhuloge to running sum me purana loss ghiste rahega.
- **`best` ko sirf end pe check karna** — maximum subarray beech me khatam ho sakta hai, isliye `best` ko har iteration pe update karo, na ki loop ke baad ek baar.
- **Indices return karne ki demand** — agar interviewer start/end index bhi maange, to jis index pe `cur` reset hua (fresh start) use `tempStart` me yaad rakho, aur jab `best` update ho tab `start, end` commit karo.

## When to Use This Pattern

Jab dikhe **"contiguous subarray / substring ka maximum (ya minimum) kuch find karo"** — sum, product, length — to running-value greedy/DP socho. Cue: "har position pe ek choice — pichle accumulated result ko extend karu ya yahin se naya shuru?" Kadane's iska canonical example hai. Cousins: Maximum Product Subarray, Best Time to Buy/Sell Stock, Maximum Circular Subarray.

## Visual

Open [visual.html](visual.html) in your browser for an interactive Prev/Next walkthrough of Kadane's running totals.

## NeetCode Link

https://neetcode.io/problems/maximum-subarray
