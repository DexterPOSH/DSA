# Minimum Window Substring

**Category:** Sliding Window
**Difficulty:** hard

## Problem Statement

Given two strings `s` and `t`, return the **smallest substring of `s`** that contains
**every character of `t`** (including duplicates — counts must be covered). If no such
window exists, return `""`.

```
s = "ADOBECODEBANC",  t = "ABC"   ->  "BANC"
s = "a",  t = "a"                  ->  "a"
s = "a",  t = "aa"                 ->  ""      # only one 'a' available, need two
```

## Real-World Analogy

**What Azure Stream Analytics with Azure Event Hubs is:** Azure Event Hubs ingests events from many producers, and Azure Stream Analytics continuously queries those events as they arrive. Instead of storing the entire stream in application code, Azure Stream Analytics maintains query state for the current window and emits results when the window satisfies the query. This is useful for monitoring alert patterns in telemetry streams.

**What required event-type coverage is, and why it's used:** In the existing analogy, the query is looking for the shortest span of Azure events that covers a required multiset of alert types — for example one `A`, one `B`, and one `C`, or duplicates if the rule requires them. Coverage counts matter because "has an A" is not enough when the requirement says "two A events." The mechanism exists to identify the tightest incident window that contains all required evidence, while ignoring extra noise before or after it.

**The mapping:** Characters in `s` are Azure Event Hubs events, and characters in `t` are the required alert types. Expanding `right` adds events and updates `have`; `formed == required` means Azure's active window now covers every needed count. Then advancing `left` removes extra events while coverage still holds, recording the smallest valid span before coverage breaks. The key insight is "expand until complete, then contract until just barely complete" — that is the minimum window.

## Approach

**Variable sliding window with a `have/need` counter.** `need` = `t` ke har char ki
required count. `have` = window me se kitne *required* chars satisfy ho chuke. Ek
`formed` counter rakho = kitne distinct chars ka required count exactly pura hua.

1. **Expand** `right`: char andar lo, count update karo; agar us char ka window-count
   uske `need` ke barabar ho gaya, `formed += 1`.
2. **Contract** jab `formed == required` (saare characters covered): current window valid
   hai — best answer update karo, phir `left` se char hatao taaki aur chhoti window
   try kar sako. Hatate waqt agar kisi char ka count `need` se neeche gir gaya,
   `formed -= 1` aur expand pe wapas aa jao.

```python
from collections import Counter

def min_window(s, t):
    if not t or not s:
        return ""
    need = Counter(t)
    required = len(need)               # kitne distinct chars satisfy karne hain
    have = {}
    formed = 0
    left = 0
    best_len, best_l = float('inf'), 0

    for right, ch in enumerate(s):
        have[ch] = have.get(ch, 0) + 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:                 # window valid -> shrink
            if right - left + 1 < best_len:
                best_len, best_l = right - left + 1, left
            lc = s[left]
            have[lc] -= 1
            if lc in need and have[lc] < need[lc]:
                formed -= 1
            left += 1
        # left ab fir se expand ke liye taiyaar

    return "" if best_len == float('inf') else s[best_l:best_l + best_len]
```

Pattern: **expand right to become valid, contract left to stay minimal.** `right`
hamesha aage; `left` tabhi aage jab window valid ho.

## Complexity

- **Time:** O(|s| + |t|) — har pointer poore `s` pe at most ek baar chalta. `Counter`
  build O(|t|). Inner while amortized O(1) per right-step.
- **Space:** O(|s| + |t|) worst case for the count maps (practically O(charset) = O(1)).

## Common Pitfalls

- **`formed` vs char-counts gadbad** — `formed` distinct *satisfied* chars count karta,
  total nahi. `have[ch] == need[ch]` (exactly equal) pe hi increment — `>=` use karoge to
  duplicates ke saath over-count ho jaayega.
- **Shrink ke time `formed` decrement ka condition** — sirf tab `formed -= 1` jab count
  `need` se *strictly neeche* gira (`< need[lc]`), na ki har removal pe.
- **Best window store karna by length, value nahi** — `best_l` + `best_len` rakho aur
  end me slice karo; har step pe substring banaoge to O(n²) ho jaayega.
- **`t` me duplicate chars** — counts matter karte hain (`t="AABC"` me do A chahiye);
  isliye `Counter`, plain set nahi.
- **Empty `s` ya `t`** — `""` return karo, crash nahi.

## When to Use This Pattern

"Smallest / shortest window jisme kuch *poora cover* ho jaaye" — jab aisa dikhe to
**variable window: expand-to-satisfy, contract-to-minimize** socho, ek `have/need`
counter ke saath. Yeh hardest sliding-window template hai; ise solid kar lo to "minimum
window with K distinct", "smallest subarray with sum ≥ target" sab aasaan lagti hain.

## NeetCode Link

https://neetcode.io/problems/minimum-window-with-characters
