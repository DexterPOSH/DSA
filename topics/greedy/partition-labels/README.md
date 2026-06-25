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

**What Azure Event Hubs export to Azure Blob Storage is:** Azure Event Hubs can be paired with Azure Blob Storage to land streaming data durably for replay, analytics, or archival. Event Hubs Capture writes partition data into blob files, and custom export jobs often add their own segmentation rules for downstream consumers. The important idea is that an ordered stream is being cut into durable blob windows.

**What checkpoint windowing by partition key is, and why it's used:** Suppose an export job must seal blob segments so every partition key's records stay inside exactly one segment for a clean downstream replay contract. To do that safely, the job needs to know the last offset where each key appears; otherwise it might close a blob and later discover the same key again. Tracking the farthest last offset among keys already seen tells the exporter the earliest safe place to seal the current window.

**The mapping:** Each character is an Azure Event Hubs partition key in the export stream, `last[ch]` is that key's final offset, and `end` is the farthest final offset required by keys in the current blob window. As you scan, seeing a key may stretch `end`; when the current index reaches `end`, no key in the window appears later, so the segment can be sealed greedily. The key insight is that overlapping key ranges must stay together, and the first point where the running farthest end closes gives the smallest valid partition.
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
