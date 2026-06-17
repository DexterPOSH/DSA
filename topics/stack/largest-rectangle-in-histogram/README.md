# Largest Rectangle in Histogram

**Category:** Stack (Monotonic Stack)
**Difficulty:** hard

## Problem Statement

Given an array `heights` representing the heights of bars in a histogram (each bar
width `1`), find the **area of the largest rectangle** that can be formed within
the histogram.

```
heights = [2, 1, 5, 6, 2, 3]
->  10        # bars at index 2 and 3 (heights 5 and 6) -> width 2 x height 5 = 10
```

## Real-World Analogy

Socho ek **city skyline** hai — alag-alag width 1 ki buildings ek line me. Tumhe
sabse bada **rectangular banner** lagana hai jo poora ek continuous range me, aur
ek fixed height pe, fit ho jaaye. Banner ki height us range me sabse **chhoti
building** se zyada nahi ho sakti (warna woh chhoti building ke upar latak jaayega).
To har building ke liye socho: "agar **main** sabse chhoti building hoon banner ki,
to wo banner kitna **chaura** (left aur right) faila sakta hai?" — yaani left aur
right me kahan tak buildings **mujhse lambi ya barabar** hain. Us width × meri
height = ek candidate banner. Sabse bada candidate hi answer.

Har bar ke liye "left aur right tak kahan tak main shortest hoon" — ye **monotonic
increasing stack** se ek hi pass me nikal jaata hai.

## Approach

Stack me **indices** rakho, aur heights ko **non-decreasing (increasing)** order me
maintain karo. Jab koi naya bar aata hai jo stack-top wale bar se **chhota** hai,
matlab top wale bar ke liye **right boundary** mil gayi (wo aage nahi faila sakta).
Use pop karo aur uska rectangle area compute karo:

- popped bar ki **height** = `heights[popped]`
- **right boundary** = current index `i` (yahin ruk gaya)
- **left boundary** = naya stack-top ka index + 1 (uske baad se ye bar shortest tha)
- **width** = `i - stack[-1] - 1` (agar stack khali to width `= i`)

```python
def largest_rectangle_area(heights):
    stack = []                    # indices with increasing heights
    max_area = 0
    for i, h in enumerate(heights):
        # current bar chhota hai top se -> top bar ka right boundary yahin
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i - stack[-1] - 1 if stack else i
            max_area = max(max_area, height * width)
        stack.append(i)
    # bache hue bars: inka right boundary = end (n)
    n = len(heights)
    while stack:
        height = heights[stack.pop()]
        width = n - stack[-1] - 1 if stack else n
        max_area = max(max_area, height * width)
    return max_area
```

> **Sentinel trick (cleaner):** `heights` ke end me ek `0` append kar do — ye final
> flush wala doosra loop khatam kar deta hai, kyunki `0` sab bars ko pop kara deta.

## Complexity

- **Time:** O(n) — har index exactly ek baar push aur ek baar pop. `while` ke
  bawajood amortized linear.
- **Space:** O(n) — stack worst case (fully increasing histogram) me saare indices.

## Common Pitfalls

- **Width formula galat** — sabse common bug. Pop ke **baad** `i - stack[-1] - 1`
  use karo (left boundary = naya top), aur agar stack khali ho gaya to width `= i`
  (poore left tak faila). Yahan off-by-one se area galat aata hai.
- **End me bache bars flush karna bhulna** — increasing histogram (`[1,2,3,4]`) me
  loop ke andar koi pop hi nahi hota; saara kaam final `while` loop me hota hai. Use
  miss karoge to answer galat.
- **`>` vs `>=`** — `heights[stack[-1]] > h` (strictly greater pop). Equal heights
  ko stack pe rehne dena theek hai; width baad me popped bar ke through correctly
  account ho jaati. `>=` bhi kaam karta but boundaries thoda shift hote — `>` rakho
  consistent rehne ke liye.
- **Indices vs values** — width ke liye index chahiye, value se distance nahi banti.

## When to Use This Pattern

"Har element ke liye **left aur right tak kitna faila** sakte ho jab tak wo dominant
(min/max) rahe" → monotonic stack. Cue: histogram / skyline / "sabse bada rectangle
or span jahan ek element limiting factor hai". Ye problem ek building block hai:
**Maximal Rectangle** (2D binary matrix) har row ko histogram maan ke isi ko call
karta hai. Cousins: Trapping Rain Water, Daily Temperatures, Stock Span.

## Practice

- Visual: open `topics/stack/largest-rectangle-in-histogram/visual.html`

## NeetCode Link

https://neetcode.io/problems/largest-rectangle-in-histogram
