# Daily Temperatures

**Category:** Stack (Monotonic Stack)
**Difficulty:** medium

## Problem Statement

Given an array `temperatures` of daily temperatures, return an array `answer` such
that `answer[i]` is the **number of days you have to wait** after day `i` to get a
warmer temperature. If there is no future day that is warmer, `answer[i] = 0`.

```
temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
answer        = [ 1,  1,  4,  2,  1,  1,  0,  0]
```

Day 0 (73) → next warmer is day 1 (74), wait 1 day.
Day 2 (75) → next warmer is day 6 (76), wait 4 days.
Day 6 (76) → koi din aage warmer nahi → 0.

## Real-World Analogy

Socho tum ek line me khade logon ka **height comparison** kar rahe ho — har banda
puchh raha hai "mere aage pehla banda kaun hai jo mujhse **lamba** hai, aur wo
kitni jagah door hai?" Ab brute-force me har banda apne aage poori line scan kare
to bahut time lagega. Smarter tareeka: ek **stack me un logon ko pakad ke rakho
jinhe abhi tak apna 'taller person' nahi mila**. Jaise hi koi naya, taller banda
aata hai, wo stack ke top wale chhote logon ka jawab ban jaata hai — pop karke
unhe answer de do. Stack hamesha **decreasing height** me rehta hai (top pe sabse
chhota jo abhi tak wait kar raha hai). Yahi monotonic stack ka core hai.

## Approach

Hum **indices** ko stack me rakhenge (values nahi), taaki distance `i - prev`
nikal saken. Stack ko **strictly decreasing temperature** me maintain karenge.

Brute force pehle samajh lo (taaki appreciate ho optimal): har `i` ke liye aage
`j` chala ke pehla warmer dhoondo → O(n²).

**Optimal — monotonic decreasing stack** (O(n)):

```python
def daily_temperatures(temperatures):
    answer = [0] * len(temperatures)
    stack = []                       # holds indices; temps at these indices are decreasing
    for i, temp in enumerate(temperatures):
        # current temp warmer hai stack-top wale din se? -> uska answer mil gaya
        while stack and temp > temperatures[stack[-1]]:
            prev = stack.pop()
            answer[prev] = i - prev  # kitne din wait karna pada
        stack.append(i)
    return answer
```

Har din ko stack pe push karo. Naya din jab aata hai aur wo stack-top wale din se
**warmer** hai, to top wale din ka intazaar khatam — pop karo aur `i - prev`
distance likh do. Jo din stack me reh gaye (end tak), unke aage koi warmer nahi
mila → unka answer `0` rehta hai (already initialized).

## Complexity

| Approach | Time | Space | Why |
|----------|------|-------|-----|
| Brute force | O(n²) | O(1) | Har day apne aage poora scan karta |
| **Monotonic stack** | **O(n)** | **O(n)** | Har index **exactly ek baar** push, ek baar pop |

- **Time:** O(n) — bhale `while` loop dikhta hai, har index lifetime me sirf
  ek baar push aur ek baar pop hota hai. Amortized total work linear hai.
- **Space:** O(n) — worst case (strictly decreasing temps, jaise `[80,70,60]`)
  saare indices stack pe ek saath baith jaate hain.

## Common Pitfalls

- **Values push karna instead of indices** — distance `i - prev` nikalne ke liye
  index chahiye. Sirf value rakhoge to "kitne din" calculate nahi hoga.
- **`>=` vs `>`** — strictly warmer chahiye, isliye `temp > temperatures[stack[-1]]`.
  `>=` lagaoge to equal temperature ko galti se "warmer" maan loge.
- **`while` ke bajaye `if`** — ek naya warmer din stack ke **kayi** purane dino ka
  jawab ho sakta hai. `if` sirf top ek ko pop karega → galat answers.
- **Stack me bache indices ko zero set karna bhulna** — agar `answer` ko `0` se
  initialize nahi kiya, to leftover dino ka answer garbage reh jaayega.

## When to Use This Pattern

"Har element ke liye **next greater / next smaller / previous greater** element
(ya uski distance) dhoondo" → ye classic **monotonic stack** signal hai. Jab brute
force O(n²) lage aur tum "next bigger thing to the right" type relationship dhoondh
rahe ho, to stack me un elements ko pakdo jinka jawab abhi pending hai. Cousins:
Next Greater Element, Stock Span, Largest Rectangle in Histogram.

## Practice

- Visual: open `topics/stack/daily-temperatures/visual.html`

## NeetCode Link

https://neetcode.io/problems/daily-temperatures
