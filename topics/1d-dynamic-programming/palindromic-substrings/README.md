# Palindromic Substrings

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given a string `s`, return the **total number of palindromic substrings** in it. Substrings with different start or end indices count separately, even if they are the same text.

```
"abc"   ->  3     ("a", "b", "c")
"aaa"   ->  6     ("a","a","a", "aa","aa", "aaa")
```

## Real-World Analogy

**What Azure Stream Analytics is:** Azure Stream Analytics is a real-time stream-processing service that evaluates queries over ordered telemetry events. It can detect patterns inside sliding or bounded windows and count matches as events flow through the pipeline. Here, the pattern is a symmetric window in a character stream.

**What symmetric-window expansion is, and why it's used:** Once a smaller window is confirmed symmetric, the next larger window only needs one new comparison: its left and right boundary characters. This mechanism exists because counting every substring by rebuilding it would be expensive, while expanding from centers reuses the verified inner state. Every successful expansion is immediately a counted match.

**The mapping:** Each character position, and each gap between characters, is an Azure Stream Analytics-style center to inspect. The algorithm expands while the boundary characters match and increments the count for every valid window it discovers. The key insight is that palindromic substrings are counted by successful expansions, not by generating all substrings first.

## Approach

**Pattern: Expand Around Center (counting variant).** Har character ek odd-length palindrome ka center ban sakta hai, aur har gap ek even-length palindrome ka. Total `2n - 1` centers. Har center se expand karo; **har successful match pe count++**.

```python
def countSubstrings(s: str) -> int:
    count = 0

    def expand(l: int, r: int) -> None:
        nonlocal count
        while l >= 0 and r < len(s) and s[l] == s[r]:
            count += 1                  # har valid (l,r) ek palindrome hai
            l -= 1
            r += 1

    for i in range(len(s)):
        expand(i, i)                    # odd-length center
        expand(i, i + 1)                # even-length center

    return count
```

> Notice the only difference from Longest-Palindromic-Substring: instead of tracking the longest window, we do `count += 1` **inside** the match loop. Har layer of successful expansion = ek aur palindrome.

**Why every successful expansion is a new palindrome:** jab `s[l] == s[r]` aur andar ka hissa `s[l+1..r-1]` already palindrome tha (kyunki hum bahar nikal rahe the), to `s[l..r]` bhi palindrome hai — guaranteed. So each step is a distinct, valid count.

## Complexity

- **Time:** O(n²) — `2n-1` centers, each expands up to O(n). String `"aaaa"` jaise cases me poori expansion hoti.
- **Space:** O(1) — sirf ek counter aur pointers. (2-D DP table approach O(n²) space leta but same time.)

## Common Pitfalls

- **Even centers bhulna** — `"aa"` me `expand(i, i+1)` ke bina even-length palindromes (jaise `"aa"`) miss ho jayenge.
- **Count loop ke bahar rakhna** — `count += 1` ko `while` ke **andar** rakho, bahar nahi. Bahar rakhoge to har center sirf 1 ginega, jo galat hai.
- **Single chars ginna bhulna** — har single character apne aap me ek palindrome hai. Odd-center `expand(i,i)` ka pehla iteration (`l==r`) yeh automatically `+1` karta hai — to alag se add mat karo.
- **DP table approach me base cases galat** — agar 2-D DP karoge: length-1 sab palindrome (`dp[i][i]=True`), length-2 `dp[i][i+1] = s[i]==s[i+1]`. In base cases ko miss karna common bug hai. Expand-around-center is simpler, recommended.

## When to Use This Pattern

"Count/find palindrome substrings" → **expand around center**. Agar problem bole "kitne palindromes" → counting variant; "sabse lamba" → tracking variant. Same engine, alag accumulator. Dono `expand(i,i)` + `expand(i,i+1)` chahiye hote hain odd aur even dono cover karne ke liye.

## NeetCode Link

https://neetcode.io/problems/palindromic-substrings
