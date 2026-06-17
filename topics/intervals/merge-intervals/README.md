# Merge Intervals

**Category:** Intervals
**Difficulty:** medium

## Problem Statement

Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all
**overlapping** intervals and return the non-overlapping intervals that cover all
the input intervals.

```
[[1,3],[2,6],[8,10],[15,18]]   ->  [[1,6],[8,10],[15,18]]   # [1,3] & [2,6] overlap
[[1,4],[4,5]]                  ->  [[1,5]]                   # touching counts as overlap
```

## Real-World Analogy

Socho timeline pe kuch **highlighter strokes** maare hain — kuch ek doosre ke upar
chadh gaye hain. Tumhe overlapping strokes ko ek single lambe stroke me **combine**
karna hai. Sabse pehle strokes ko unke **start point ke order me line up** karo.
Phir left se right chalo: agla stroke agar current wale ko **chhoo raha ya overlap
kar raha** hai (`next.start <= current.end`) to dono ko stretch karke jod do (end
ko `max` tak badha do). Agar gap hai, to current stroke band karo aur naya shuru karo.

Sorting is the trick — bina sort kiye overlaps random jagah ho sakte hain.

## Approach

Pehle **sort by start**, phir ek pass me merge — classic **sort + sweep**.

```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])      # start ke order me lao
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last = merged[-1]
        if start <= last[1]:                # overlap (touch bhi) -> stretch
            last[1] = max(last[1], end)
        else:                               # gap -> naya block
            merged.append([start, end])
    return merged
```

Sort ke baad ek interval sirf apne **immediately pehle wale** se overlap check karna
kaafi hai — agar us se overlap nahi to peeche kisi se bhi nahi (sab start chote hain
aur unka end aur bhi peeche).

## Complexity

- **Time:** O(n log n) — dominant cost sorting ka hai; sweep khud O(n).
- **Space:** O(n) output ke liye (sort in-place ho to O(log n) extra for the sort itself).

## Common Pitfalls

- **Sort bhulna** — bina sort, ye pure algorithm galat. Yehi step #1 hai.
- **Touching intervals** — `[1,4]` aur `[4,5]` ko merge karo (`<=`, na ki `<`),
  warna tumhare answer me extra split rah jaayega.
- **`max(last[1], end)` na lagana** — agar nested interval ho (`[1,10]` ke andar `[2,3]`), to seedha `last[1]=end` lagane se end **chhota** ho jaayega. Hamesha `max`.
- **Sort key galat** — start ke saath kabhi end pe sort mat karo; start ka order chahiye taaki left-to-right sweep valid rahe.

## When to Use This Pattern

Jab bhi "**overlapping ranges ko combine/clean up**" karna ho → pehle sort by start,
phir single sweep. Yeh poore intervals family ka foundation hai. Cue: "ranges,
overlap, merge/coverage". Cousins: Insert Interval, Meeting Rooms, Employee Free Time.

## Practice

- Visual: open `topics/intervals/merge-intervals/visual.html`

## NeetCode Link

https://neetcode.io/problems/merge-intervals
