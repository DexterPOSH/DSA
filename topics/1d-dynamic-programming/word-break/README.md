# Word Break

**Category:** 1-D Dynamic Programming
**Difficulty:** medium

## Problem Statement

Given a string `s` and a dictionary of words `wordDict`, return `True` if `s` can be segmented into a space-separated sequence of one or more dictionary words. Same dictionary word may be reused multiple times.

```
s = "leetcode",  wordDict = ["leet", "code"]    ->  True   # "leet" + "code"
s = "applepenapple", wordDict = ["apple","pen"] ->  True   # apple + pen + apple
s = "catsandog", wordDict = ["cats","dog","sand","and","cat"] ->  False
```

## Real-World Analogy

**What Azure App Configuration is:** Azure App Configuration centralizes application settings and feature flags for services running across environments. Applications read known keys and values from it so configuration can change without redeploying code. A client-side validator may need to confirm that a compact setting or connection-string fragment can be segmented into approved tokens.

**What token-based configuration validation is, and why it's used:** Token validation checks whether each segment of a composed configuration value belongs to a known dictionary of allowed keys, labels, or schema tokens. It exists to reject malformed strings early and to avoid trying every possible split repeatedly. Caching reachable boundaries lets the parser reuse prefix decisions as it moves through the value.

**The mapping:** Boundary `i` is reachable if some earlier boundary `j` was already reachable and `s[j:i]` is a known App Configuration token. The DP array stores those reachable split points, so each prefix is evaluated once instead of re-scanning all segmentations. The key insight is that the whole string is valid exactly when the final boundary can be reached through valid dictionary tokens.

## Approach

`dp[i]` = "kya `s[:i]` (pehle `i` chars) dictionary words me segment ho sakta hai?". Boolean reachability DP.

- `dp[0] = True` (empty prefix hamesha valid — base case / start stone).
- Har end-position `i` ke liye, har split-point `j < i` try karo: agar `dp[j]` `True` hai **aur** `s[j:i]` dictionary me hai, to `dp[i] = True`.
- Answer `dp[len(s)]`.

```python
def word_break(s, wordDict):
    words = set(wordDict)            # O(1) lookup
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True                     # empty prefix reachable
    for i in range(1, n + 1):
        for j in range(i):           # split point
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break                # ek valid split kaafi hai
    return dp[n]
```

Pattern: **1-D boolean reachability DP** — har index ek "kya yahan tak pahunch sakte hain" sawaal hai, jo pichhle reachable points pe depend karta hai.

## Complexity

- **Time:** O(n²·m) — outer `i` (n), inner `j` (n), aur har substring slice/compare ~O(m) jahan `m` longest word length. Set me daalne se lookup O(1) average.
- **Space:** O(n) dp array + O(dictionary) set.

## Common Pitfalls

- **`wordDict` ko list rakhna** — `s[j:i] in word_list` O(words) hai; `set` me convert karo for O(1) lookup, warna O(n²·k) ho jaata.
- **`dp[0] = True` bhulna** — base case miss kiya to poora DP `False` reh jaayega.
- **Indexing off-by-one** — `dp` ka size `n+1` hai (prefix lengths `0..n`), `s[j:i]` ka matlab "chars `j` se `i-1`". Dhyaan se.
- **Greedy soch** — "sabse lamba word pehle match karo" greedy galat hai (`catsandog` jaise cases me dead-end). Pure DP/backtracking chahiye.
- **Reuse galat samajhna** — same word baar-baar use ho sakta hai; isliye dictionary ko consume nahi karte.

## When to Use This Pattern

"Kya is sequence ko valid pieces me toda ja sakta hai?" / "string ko dictionary se segment karo" → **reachability DP** (`dp[i]` depends on earlier `dp[j]` + a local validity check). Cousins: decode-ways, palindrome-partitioning, jump-game. Cue: "har position tak pahunchna pichhle valid positions pe depend karta hai."

## NeetCode Link

https://neetcode.io/problems/word-break
