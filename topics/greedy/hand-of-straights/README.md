# Hand of Straights

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

You are given an integer array `hand` (cards in your hand) and an integer
`groupSize`. Return `True` if you can rearrange the cards into groups where each
group has exactly `groupSize` cards **and the values are consecutive** (a
"straight"). Otherwise return `False`.

```
hand = [1,2,3,6,2,3,4,7,8], groupSize = 3
  -> True     # [1,2,3] [2,3,4] [6,7,8]

hand = [1,2,3,4,5], groupSize = 4
  -> False    # 5 cards can't split into groups of 4
```

## Real-World Analogy

Socho tum **Rummy** khel rahe ho aur tumhe poore haath ko fixed-length
consecutive "runs" me todna hai — bina koi card bache. Yahan ek hi smart move
hai: **hamesha sabse chhoti available card uthao.** Wo chhoti card kisi na kisi
group ka *starting* card banni hi padegi (uske neeche koi card hai hi nahi jo
use absorb kar le). To agar smallest card `x` hai, to tumhe `x, x+1, x+2, ...`
poora group banana *zaroori* hai. Wo cards nahi mile? Game over, `False`.

## Approach

Greedy: **smallest card pehle.** Counts maintain karo, aur baar-baar minimum
available card se ek straight banane ki koshish karo.

1. Agar `len(hand) % groupSize != 0` → turant `False` (perfectly nahi banega).
2. `Counter` banao, keys ko sorted order me process karo (ya min-heap).
3. Har `min` value `x` ke liye, `x, x+1, …, x+groupSize-1` har value ka count
   `count[x]` se decrement karo. Beech me koi value missing/zero → `False`.

```python
from collections import Counter
import heapq

def is_n_straight_hand(hand, groupSize):
    if len(hand) % groupSize:
        return False
    count = Counter(hand)
    heap = list(count.keys())
    heapq.heapify(heap)                      # min-heap of distinct values
    while heap:
        start = heap[0]                      # smallest remaining card
        for x in range(start, start + groupSize):
            if count[x] == 0:
                return False                 # consecutive chain toота
            count[x] -= 1
            if count[x] == 0:
                if x != heap[0]:
                    return False             # a "hole" in the middle ran out
                heapq.heappop(heap)
    return True
```

Pattern: **greedy + frequency map.** Smallest-first choice locally optimal hai,
aur globally bhi sahi nikalta — koi exchange argument se prove hota hai.

## Complexity

- **Time:** O(n log n) — heap pe `n` distinct values, har ek pe log work; ya
  sort + scan. Group banana O(groupSize) per start but total decrements = n.
- **Space:** O(n) — counter + heap.

## Common Pitfalls

- **Divisibility check bhulna** — `len(hand) % groupSize != 0` hote hi `False`.
- **Smallest se start na karna** — kisi random/biggest card se shuru karoge to
  greedy break ho jaata. Hamesha current minimum group ka head hota hai.
- **Heap top check** — jab beech ki value ka count `0` ho jaye but wo `heap[0]`
  nahi hai, matlab ek "hole" exhaust ho gaya jise abhi bhi aage chahiye tha →
  `False`. Sirf top hone par hi pop karo.
- **Naya sorted scan har baar** — counts decrement karke heap reuse karo, warna
  O(n²) ho jaayega.

## When to Use This Pattern

"Items ko fixed-size consecutive/ordered groups me baato, kuch bacha nahi"
→ greedy with **smallest-element-first** + frequency map. Cousins: meeting-room
grouping, divide-array-in-sets-of-k-consecutive (literally same problem).
Cue: "consecutive sequence banani hai aur ek forced choice dikhe (min element)".

## NeetCode Link

https://neetcode.io/problems/hand-of-straights
