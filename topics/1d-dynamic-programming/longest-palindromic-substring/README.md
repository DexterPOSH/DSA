# Longest Palindromic Substring

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given a string `s`, return the **longest contiguous substring** of `s` that is a palindrome (reads the same forwards and backwards). If there are ties, any one valid answer is fine.

```
"babad"  ->  "bab"   (or "aba" — both length 3 are valid)
"cbbd"   ->  "bb"
"a"      ->  "a"
```

## Real-World Analogy

Socho ek shaadi me do log **back-to-back khade hain mirror ke saamne**. Tum ek center point pakad ke dono taraf ek saath bahar ki taraf chalte ho — left wala aur right wala. Jab tak dono ke "chehre match" karte hain (same character), palindrome failta jaata hai aur tum aur baahar nikalte ho. Jaise hi mismatch hua, ya deewar (string ka end) aa gayi — ruk jao, utni hi door tak ka hissa palindrome tha.

Har possible center pe yeh "expand karo dono taraf" wala kaam karo, aur jo sabse lamba palindrome mila usse yaad rakho. Bas yahi hai **expand around center**.

## Approach

**Pattern: Expand Around Center.** Ek palindrome ka ek center hota hai. Lekin center do tarah ka ho sakta hai:

- **Odd length** (jaise `"aba"`) → center ek single character hai (`b`).
- **Even length** (jaise `"bb"`) → center do characters ke beech ka gap hai.

`n` characters ke liye total `2n - 1` possible centers hote hain (har char + har gap). Har center se dono pointers `l` aur `r` bahar expand karo jab tak `s[l] == s[r]`. Jo window mila, agar wo abhi tak ke best se lambi hai to update.

```python
def longestPalindrome(s: str) -> str:
    res = ""

    def expand(l: int, r: int) -> str:
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1                      # baahar nikalte jao
            r += 1
        return s[l + 1:r]               # last valid window (l,r ek step over-shot hain)

    for i in range(len(s)):
        odd  = expand(i, i)             # center = single char
        even = expand(i, i + 1)         # center = gap between i and i+1
        res = max(res, odd, even, key=len)

    return res
```

> Loop break hote waqt `l` aur `r` **ek step zyada** ho chuke hote hain (mismatch ya boundary pe), isliye `s[l+1:r]` return karte hain — yeh hi aakhri valid palindrome tha.

There's also a classic **2-D DP table** (`dp[i][j] = is s[i..j] a palindrome`) which is also O(n²) time but takes O(n²) space. Expand-around-center is simpler and uses O(1) space, so it's the go-to.

## Complexity

- **Time:** O(n²) — `n` centers, har center se expansion worst case O(n) (jaise `"aaaa"` me poori string expand hoti hai).
- **Space:** O(1) — sirf pointers, koi extra table nahi. (DP table approach O(n²) space leta.)

## Common Pitfalls

- **Even-length centers bhulna** — sirf `expand(i, i)` karoge to `"cbbd"` ka `"bb"` kabhi nahi milega. Dono `expand(i,i)` aur `expand(i,i+1)` chahiye.
- **Slice indices galat** — break ke baad `l` aur `r` overshoot kar chuke hote hain. `s[l+1:r]` correct hai (`r` exclusive Python slice ki wajah se already sahi hai).
- **Empty string** — `""` ke liye loop chalta hi nahi, `res` `""` rehta — wahi sahi answer hai.
- **Length store karke index bhulna** — sirf best length track karoge to substring nikalne ke liye start index bhi chahiye hoga. Yahan hum directly substring return kar rahe, simpler.
- **Manacher's O(n)** — exists, but interview me almost kabhi expect nahi hota. Expand-around-center bolo, Manacher ko follow-up me mention kar do.

## When to Use This Pattern

"Palindrome substring/length" sun te hi **expand around center** socho — har center se symmetric do-pointer expansion. Cue: jab problem ek string me symmetric structure (palindrome) dhoondhne ko bole, aur tumhe har possible "middle" se grow karna ho. Cousin problem: **Palindromic Substrings** (count) — same expansion, sirf count karte hain replace of longest track karne ke.

## NeetCode Link

https://neetcode.io/problems/longest-palindromic-substring
