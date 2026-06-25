# Longest Repeating Character Replacement

**Category:** Sliding Window
**Difficulty:** medium

## Problem Statement

Given a string `s` (uppercase letters) and an integer `k`, you may replace **at most
`k` characters** with any other uppercase letter. Return the length of the **longest
substring containing the same letter** you can get after doing those replacements.

```
s = "ABAB",   k = 2   ->  4    # replace 2 B's with A (or 2 A's with B) -> "AAAA"
s = "AABABBA", k = 1   ->  4    # window "ABBA": replace the lone A -> "BBBB"
```

## Real-World Analogy

**What Azure Stream Analytics with Azure Event Hubs is:** Azure Event Hubs is Azure's high-throughput event ingestion service, and Azure Stream Analytics is the managed query engine that reads those events continuously. Together they let you process telemetry, clicks, or logs while the stream is still arriving instead of waiting for a batch job. Azure Stream Analytics keeps state for the active window so it can aggregate counts as events enter and leave.

**What windowed event-type normalization is, and why it's used:** In the existing analogy, Azure Stream Analytics groups the current window by event type and asks: "If we wanted this whole window to look like one dominant event type, how many events would need correction?" The dominant type's count is `max_count`, and every other event in the window is a mismatch. A budget `k` models a rule such as "we can normalize at most k noisy/outlier events"; if the mismatch count exceeds that budget, the window must slide forward because it is too mixed to treat as one clean segment.

**The mapping:** Each character is an Azure Event Hubs telemetry event type. Expanding `right` is Azure Stream Analytics accepting the next event, the frequency map is the per-type group state, and `window_len - max_count` is the number of events that would need replacement. When that number is greater than `k`, advancing `left` expires old Azure events until the active window is affordable again. The key insight is that the best window is the longest span where all non-majority characters fit within the replacement budget.

## Approach

**Sliding window + frequency count.** Window me har char ka count rakho. Window valid
hai jab `window_len - max_count <= k`, jahan `max_count` window me sabse frequent char
ki count hai. (`window_len - max_count` = jitne characters replace karne padenge.)

`right` se expand karo, count update karo. Agar window invalid ho gayi
(`window_len - max_count > k`), to `left` ko ek step aage karo aur uska count ghatao.

```python
def character_replacement(s, k):
    count = {}
    left = 0
    max_count = 0          # window me sabse frequent char ki frequency
    best = 0
    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_count = max(max_count, count[s[right]])
        # window invalid? -> ek char left se nikaalo
        if (right - left + 1) - max_count > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
```

> **Sneaky bit:** `max_count` ko kabhi *decrease* nahi karte jab window shrink hoti.
> Lagta hai bug hai, par nahi — answer sirf tabhi badhta jab koi *naya* zyada-frequent
> char milta hai, isliye stale (slightly high) `max_count` se window kabhi galat-bade
> nahi hoti; bas grow karti rehti hai. Yahi is problem ka famous trick hai.

## Complexity

- **Time:** O(n) — ek pass, `left` aur `right` dono monotonic. Count map fixed 26 size.
- **Space:** O(1) — count map me at most 26 uppercase letters.

## Common Pitfalls

- **`max_count` ko recompute / decrease karne ki koshish** — zaroorat nahi, aur karoge
  to har step pe O(26) lag kar code slow + over-complicated ho jaata. Stale max chalta hai.
- **Window ko `while` se shrink karna** — yahan single `if` kaafi hai kyunki hum window
  ko *kabhi chhota nahi karte*, sirf slide karte hain (right ke saath left bhi 1 badhta).
- **`window_len - max_count` ko galat samajhna** — yeh "replace karne waale" characters
  hain; yahi `k` se compare hota hai, na ki `max_count` directly.
- **Lowercase/mixed case assume karna** — problem uppercase deta; warna count size adjust karo.

## When to Use This Pattern

"Longest window jisme at most K changes/violations allowed ho" — jab aisa dikhe to
**sliding window with a 'cost = window_len - something' check** socho. Cousins:
"max consecutive ones III" (at most K zeros flip), "longest subarray with at most K
distinct". Cue: window valid rehne ke liye ek budget `k`.

## NeetCode Link

https://neetcode.io/problems/longest-repeating-substring-with-replacement
