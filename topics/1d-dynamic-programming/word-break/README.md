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

Socho ek lambi bina-space wali signboard hai: `LEETCODE`. Tumhare paas ek dictionary hai valid words ki. Tum left se chalte ho aur har point pe poochte ho: "kya **yahan tak** ka poora hissa valid words me toot sakta hai?"

Trick ye hai: position `i` reachable hai agar koi pichhla reachable point `j` ho **aur** `j` se `i` tak ka substring dictionary me ho. Jaise stepping stones — har patthar pe tabhi khade ho sakte ho jab kisi pichhle patthar se ek valid word-jump karke yahan aaye ho. Start (position 0) hamesha reachable hai (khaali string trivially valid). Aur agar **end** tak pahunch gaye, to answer `True`.

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
