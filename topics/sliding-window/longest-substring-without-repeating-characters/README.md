# Longest Substring Without Repeating Characters

**Category:** Sliding Window
**Difficulty:** medium

## Problem Statement

Given a string `s`, return the length of the **longest substring** that contains
**no repeating characters**. A substring is a contiguous slice (not a subsequence).

```
"abcabcbb"  ->  3     # "abc"
"bbbbb"     ->  1     # "b"
"pwwkew"    ->  3     # "wke"  (note: "pwke" is a subsequence, not a substring)
""          ->  0
```

## Real-World Analogy

**What Azure Stream Analytics with Azure Event Hubs is:** Azure Event Hubs gives Azure a durable, ordered stream of incoming events, and Azure Stream Analytics can run continuous queries over that stream. An Azure Stream Analytics job often keeps a small amount of state for the current window, such as IDs, counts, or timestamps, instead of loading the whole history. That makes it suitable for online checks like uniqueness while data is still moving.

**What windowed de-duplication is, and why it's used:** Real event pipelines can receive duplicate IDs because producers retry, network calls are replayed, or downstream consumers reprocess checkpoints. Windowed de-duplication tracks IDs only inside the active window and evicts old IDs as the window start moves, keeping memory bounded. It exists to answer "is this current span clean of duplicates?" without permanently remembering every ID ever seen.

**The mapping:** Each character is an Azure Event Hubs event ID. Moving `right` adds the next ID to the active Azure Stream Analytics window and the `seen` set records IDs currently inside it. If the ID is already present, `left` advances and removes old IDs until the duplicate disappears; then the window is valid again. The key insight is that the longest substring is the largest active Azure window whose state contains no duplicate IDs.

## Approach

Classic **two-pointer sliding window** with a "seen" set. `left` aur `right` window ki
boundaries hain. `right` ko expand karte jao; jab `s[right]` window me already ho,
to `left` ko aage badha-badha kar duplicate ko window se nikaalo (set se bhi remove
karo). Har valid window pe length update karo.

```python
def length_of_longest_substring(s):
    seen = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in seen:          # duplicate -> window ko left se shrink karo
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        best = max(best, right - left + 1)
    return best
```

**Faster variant** — set ke bajaye ek dict me har char ka *last index* rakho, taaki
`left` ko ek hi jump me sahi jagah le jao (no inner while loop):

```python
def length_of_longest_substring(s):
    last = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1          # jump past the previous occurrence
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```

## Complexity

- **Time:** O(n) — `right` har char pe ek baar chalta hai; `left` bhi total milakar
  n se zyada move nahi karta (amortized). Inner while ke bawajood O(n).
- **Space:** O(min(n, charset)) — set/dict me at most unique characters (e.g. 26, 128, ya 256).

## Common Pitfalls

- **Substring vs subsequence** confuse karna — `"pwke"` ek subsequence hai par
  *contiguous* nahi, isliye answer `"wke"` (length 3), na ki 4.
- **`left` ko piche jaane dena** — dict-variant me `last[ch] >= left` check zaroori hai,
  warna ek purana index `left` ko galat (peeche) le ja sakta hai.
- **Set se remove bhulna** — while loop me `left` badhate waqt `seen.remove(s[left])`
  na karo to set stale ho jaata aur window galat band ho jaati.
- **Empty string** — answer `0` hona chahiye; loop naturally handle karta hai.

## When to Use This Pattern

"Longest / smallest contiguous segment satisfying a constraint" — jab aisa dikhe to
**variable-size sliding window** socho: right se expand, constraint toote to left se
shrink. Repeating-character, at-most-K-distinct, sum/avg constraints — sab isi family me.

## NeetCode Link

https://neetcode.io/problems/longest-substring-without-duplicates
