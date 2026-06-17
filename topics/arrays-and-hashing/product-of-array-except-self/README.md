# Product of Array Except Self

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Given an integer array `nums`, return an array `output` where `output[i]` is the **product of every element except `nums[i]`**. You must solve it **without using division**, and in **O(n)** time.

```
nums   = [1, 2, 3, 4]
output = [24, 12, 8, 6]
# output[0] = 2*3*4 = 24, output[1] = 1*3*4 = 12, output[2] = 1*2*4 = 8, output[3] = 1*2*3 = 6
```

## Real-World Analogy

Socho ek classroom me bachche ek line me khade hain, har ek ke haath me ek number. Har bachche ko ek aisa badge chahiye jis pe likha ho **"meri left ki taraf ke sabka product × meri right ki taraf ke sabka product"** — yaani mujhe chhod ke sabka product. Ab teacher do baar walk karti hai. **Pehli walk left-se-right:** har bachche ke kaan me whisper karti hai "tujhse pehle wale sabka product itna hai" (prefix product). **Doosri walk right-se-left:** ab whisper karti hai "tere baad wale sabka product itna hai" (suffix product) aur badge pe dono ko multiply kar deti hai. Bas — kisi ka apna number kabhi badge me nahi aata, aur division ki zaroorat hi nahi padi. Do passes, har bachche ka jawab tayyar.

## Approach

Brute force me har `i` ke liye baaki sab multiply karte = O(n²). Division use kar lo to total product / nums[i] — par **zero ke saath fatega** aur problem ne division mana kiya hai.

**Optimal — prefix × suffix products** (O(n) time, O(1) extra space):

Har `output[i]` = (i se pehle sab ka product) × (i ke baad sab ka product). Do passes:

1. **Left-to-right:** `output[i]` me i ke **left** ka running product bhar do.
2. **Right-to-left:** ek `suffix` variable rakho, `output[i]` ko us suffix se multiply karo, phir suffix update karo.

```python
def product_except_self(nums):
    n = len(nums)
    output = [1] * n

    prefix = 1                       # i ke left ka product
    for i in range(n):
        output[i] = prefix
        prefix *= nums[i]

    suffix = 1                       # i ke right ka product
    for i in range(n - 1, -1, -1):
        output[i] *= suffix
        suffix *= nums[i]

    return output
```

Output array ko hi prefix store karne ke liye reuse karte hain, isliye extra space O(1) (output ko nahi ginte). Pattern: **prefix/suffix accumulation**.

## Complexity

- **Time:** O(n) — sirf do linear passes, koi nested loop nahi.
- **Space:** O(1) extra — output array ke alawa sirf do scalar variables (`prefix`, `suffix`). (Output array count nahi hota.)

## Common Pitfalls

- **Division use karna** — explicitly banned, aur array me **zero** ho to crash/galat (kis se divide karoge?). Prefix/suffix approach zero ko naturally handle karta hai.
- **Suffix pass me output reset kar dena** — second pass me `output[i] *= suffix` karo (multiply), `=` nahi — warna pehle pass ka prefix mit jaayega.
- **prefix/suffix ko 1 se shuru na karna** — multiply ka identity `1` hai. `0` se shuru karoge to sab zero ho jayega.
- **Extra prefix/suffix arrays banana** — chalta hai par O(n) space leta hai; output array ko reuse karke O(1) extra me ho jaata hai.
- **Single suffix variable ki jagah array** — beginner aksar do full arrays banate hain; ek running scalar kaafi hai.

## When to Use This Pattern

Jab har index ke liye answer **"is index ko chhod ke baaki sab ka aggregate"** ya **"left ka kuch combined with right ka kuch"** ho — socho **prefix + suffix scan**. Range products/sums, "running totals from both ends", "har position pe before-and-after info chahiye" — ye sab do directional passes se O(n) me ho jaate hain.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of the prefix and suffix passes.

## NeetCode Link

https://neetcode.io/problems/products-of-array-discluding-self
