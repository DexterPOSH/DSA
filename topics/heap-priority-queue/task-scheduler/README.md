# Task Scheduler

**Category:** Heap / Priority Queue
**Difficulty:** medium

## Problem Statement

You're given an array of CPU `tasks` (each a character like `A`, `B`, `C`) and a non-negative integer `n` — the **cooldown**. Two runs of the *same* task must be separated by **at least `n` intervals**. In each interval the CPU either runs one task or sits **idle**. Return the **minimum number of intervals** needed to finish all tasks.

```
tasks = ["A","A","A","B","B","B"], n = 2

A B idle A B idle A B   ->  8 intervals
```

The same task (`A`) is always ≥ 2 slots apart. We needed 2 idle slots, so total = 8.

## Real-World Analogy

Socho ek **gym instructor** hai jo same muscle group ko back-to-back train nahi karne deta — biceps ke baad **kam se kam `n` din rest** chahiye before biceps again. Tumhare paas kuch exercises hain, kuch ki reps zyada hain (jaise biceps 3 baar karni hai), kuch ki kam. Smart instructor har din **woh exercise pick karta hai jiski sabse zyada reps bachi hain** — kyunki wahi tumhe future me phasayega. Agar koi available nahi (sab cooldown me hain), to **rest day (idle)** lo. Goal: poora plan minimum dino me khatam karna.

Yahan "sabse zyada reps bachi hain" = **max-heap**, aur "cooldown ke din" = ek **waiting queue** jo time aane par task ko wapas heap me bhej deti hai.

## Approach

Do tarike — pehle clean **simulation (heap + queue)**, phir ek **O(1) math formula**.

### Approach 1 — Max-heap + cooldown queue (simulate clock)

Intuition: har tick pe sabse frequent available task chalao (greedy). Jo task abhi chala, woh `n` ticks ke liye cooldown me chala jaata hai — usse ek queue me daal do `(ready_time, remaining_count)` ke saath. Jaise hi clock `ready_time` tak pahunche, usse wapas heap me push kar do.

```python
import heapq
from collections import Counter, deque

def least_interval(tasks, n):
    counts = Counter(tasks)
    heap = [-c for c in counts.values()]   # max-heap via negatives
    heapq.heapify(heap)
    cooldown = deque()                      # (ready_time, -count)
    time = 0
    while heap or cooldown:
        time += 1
        if heap:
            cnt = heapq.heappop(heap) + 1   # ran one (less negative)
            if cnt != 0:                    # still has copies left
                cooldown.append((time + n, cnt))
        if cooldown and cooldown[0][0] == time:
            heapq.heappush(heap, cooldown.popleft()[1])
    return time
```

Har tick pe: heap se sabse zyada-bacha task lo, ek count consume karo, agar bacha hai to `time + n` pe ready karke cooldown me daal do. Agar heap khali hai par cooldown me kuch hai → woh tick **idle** (`time` badha, kuch nahi chalaya). Jab cooldown ka front task ka `ready_time == time`, usse heap me wapas bhejo.

### Approach 2 — The math shortcut (O(1) extra space)

Bottleneck hamesha **sabse frequent task** hai. Maan lo woh `f_max` baar aata hai. Use slots me arrange karo:

```
A _ _ A _ _ A          (f_max = 3, n = 2)
```

Yeh `(f_max - 1)` "frames" banata hai, har frame ki width `(n + 1)`, plus last row me woh saare tasks jinki frequency `f_max` ke barabar hai.

```python
def least_interval(tasks, n):
    counts = Counter(tasks)
    f_max = max(counts.values())
    n_max = sum(1 for c in counts.values() if c == f_max)
    return max(len(tasks), (f_max - 1) * (n + 1) + n_max)
```

`max(...)` zaroori hai: agar bahut saare distinct tasks hain to koi idle nahi lagti aur answer simply `len(tasks)` ho jaata — gaps apne aap fill ho jaate hain.

## Complexity

| Approach | Time | Space |
|----------|------|-------|
| Heap simulation | O(T) — har task ek baar tick hota, heap ops O(26 log 26)=O(1) | O(1) (max 26 keys) |
| Math formula | O(T) to count | O(1) |

- **Time:** O(T) jahan T = total tasks — har interval ek output hai, aur heap me sirf ≤26 distinct keys hone se log factor constant ban jaata.
- **Space:** O(1) — at most 26 letters, isliye heap aur queue dono bounded.

## Common Pitfalls

- **Negate karna bhulna** — Python me `heapq` min-heap hai. Max-heap chahiye to counts ko negate karo, warna sabse kam frequent task pick hoga (galat greedy).
- **Idle ko count na karna** — answer me idle intervals bhi gine jaate hain; `time` ko har tick badhana hai chahe task chale ya na chale.
- **`time + n` vs `time + n + 1`** — cooldown ka matlab `n` *gap* slots; task `time` pe chala to next earliest run `time + n + 1` hai, isliye ready_time `time + n` pe set karke uss tick ke *baad* push karna sahi banta. (Index off-by-one yahan classic bug hai.)
- **Math formula me `max(len(tasks), ...)` chhodna** — dense input (jahan idle ki zaroorat hi nahi) pe formula under-count kar dega.
- **`n = 0`** ko handle karna — koi cooldown nahi, answer bas `len(tasks)`. Dono approaches ye naturally handle karte.

## When to Use This Pattern

Jab dikhe **"greedy: har step pe sabse 'urgent'/frequent/cheapest cheez pick karo, aur kuch items temporarily unavailable ho jaate hain (cooldown/rate-limit)"** → **max-heap + waiting queue** socho. Cousins: rearrange string so no two adjacent same, CPU/job scheduling with cooldown, rate limiters. Cue: "most frequent first" + "wait before reuse".

## NeetCode Link

https://neetcode.io/problems/task-scheduling
