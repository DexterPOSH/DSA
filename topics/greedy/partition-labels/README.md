# Partition Labels

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

Given a string `s`, partition it into **as many parts as possible** so that each
letter appears in **at most one part**. Return a list of the sizes of these
parts (in order).

```
s = "ababcbacadefegdehijhklij"
  -> [9, 7, 8]
  # "ababcbaca" | "defegde" | "hijhklij"
  # 'a' only in part 1, 'd'/'e' only in part 2, etc.
```

## Real-World Analogy

Socho ek **road trip** hai aur har shehar (letter) ke kuch friends raaste me
bikhre hue hain. Tum tab tak ek "leg" (segment) close nahi kar sakte jab tak us
leg me jitne bhi shehar visit kiye, un sabka **aakhri occurrence** cross na ho
jaaye — warna koi friend agle leg me chhoot jaayega aur ek hi shehar do legs me
aa jaayega. To chalte chalo, ek **running "farthest I must still go" marker**
rakho. Jaise hi current position us marker tak pahunch jaye — matlab is leg ke
saare shehar khatam — leg yahin cut kar do aur naya start karo.

## Approach

Pehle har letter ka **last index** nikaalo. Phir ek pass me chalo, ek `end`
pointer maintain karo jo "is partition ko kam-se-kam yahan tak jaana hai" batata
hai. Har char pe `end` ko us char ke last index se stretch karo. Jab `i == end`
ho gaya → partition complete.

```python
def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}   # last index of each char
    res = []
    start = end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])               # stretch the partition's reach
        if i == end:                           # everything seen so far closes here
            res.append(end - start + 1)
            start = i + 1
    return res
```

Pattern: **greedy interval-merge / two-marker scan.** Har char ek interval
`[i, last[ch]]` hai; tum overlapping intervals ko merge kar rahe ho aur jab koi
gap aaye to cut. `end` running max hai — bilkul "merge intervals" jaisa.

## Complexity

- **Time:** O(n) — ek pass `last` build karne ke liye, ek pass partition ke liye.
  26 letters fixed alphabet, to `last` effectively O(1) space-key.
- **Space:** O(1) — `last` map me at most 26 entries (constant for lowercase).

## Common Pitfalls

- **First occurrence track karna** — galat. Tumhe **last** occurrence chahiye,
  kyunki partition tabhi band hoga jab us letter ka aakhri instance cover ho.
- **`end` reset karna** — `end` ko har char pe reset mat karo; sirf `max` se
  stretch karo. Reset karoge to overlapping letters tút jaayenge.
- **`i == end` ki jagah `i > end`** — equality pe hi cut hota hai; `i` kabhi
  `end` se aage nahi jaayega is loop me bina cut kiye.
- **Sizes vs indices** — answer me **lengths** chahiye (`end - start + 1`), raw
  indices nahi.

## When to Use This Pattern

"Cut a sequence into max pieces where some grouping constraint holds" ya "har
element ka pehla aur aakhri occurrence ek hi block me hona chahiye" → last-index
precompute + running `end` marker. Cousins: Merge Intervals, Jump Game (farthest
reach), Employee Free Time. Cue: "intervals jo overlap karein wo ek partition".

## NeetCode Link

https://neetcode.io/problems/partition-labels
