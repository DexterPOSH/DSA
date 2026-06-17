# Cheapest Flights Within K Stops

**Category:** Advanced Graphs
**Difficulty:** medium

## Problem Statement

There are `n` cities connected by `flights[i] = [from, to, price]` (directed, weighted). Find the **cheapest price** to fly from `src` to `dst` using **at most `k` stops** (i.e. at most `k + 1` edges). If no such route exists, return `-1`.

```
n = 4, flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]]
src = 0, dst = 3, k = 1
  ->  700     # 0->1->3 = 700 (1 stop). 0->1->2->3 = 400 but that's 2 stops.
```

> The "**at most k stops**" constraint is the whole game. Plain Dijkstra can pick a cheaper-but-too-many-hops path. **Bellman-Ford** (relax edges exactly `k + 1` times) handles the hop limit naturally.

## Real-World Analogy

Socho tum sasti se sasti flight dhoondh rahe ho `src` se `dst` tak, lekin ek rule hai: **zyada se zyada `k` layovers**. Bellman-Ford ka tareeka aise socho — har **round** me tum ek aur flight (ek aur hop) lene ki ijaazat dete ho. Round 1: sirf direct flights se jo prices milte hain wo note karo. Round 2: pichhle round ke best prices ko base maan ke ek aur flight aage badho. Aise `k + 1` rounds chalao (kyunki `k` stops = `k + 1` flights). Har round me prices sasti hote jaate hain par hops limited rehte hain.

Yahaan **trick** yeh hai ki har round me sab updates ek **snapshot (pichhle round ki copy)** se karo — taaki ek hi round me do hops na ho jaayein.

## Approach — Bellman-Ford, capped at k+1 relaxations

`prices` array rakho (har city ka best known cost from `src`, init `inf`, `prices[src] = 0`). `k + 1` baar: pichhle round ki copy `tmp` lo, har flight `(u, v, w)` ke liye agar `prices[u] + w < tmp[v]` to `tmp[v]` update karo. Round ke end me `prices = tmp`.

```python
def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    prices = [INF] * n
    prices[src] = 0

    for _ in range(k + 1):                 # at most k stops => k+1 edges
        tmp = prices[:]                    # snapshot: prevents extra hops this round
        for u, v, w in flights:
            if prices[u] != INF and prices[u] + w < tmp[v]:
                tmp[v] = prices[u] + w
        prices = tmp

    return prices[dst] if prices[dst] != INF else -1
```

Snapshot `tmp` kyun? Agar tum live `prices` array pe update karte rehte, to ek hi iteration me ek path do (ya zyada) edges traverse kar sakta — hop count galat ho jaata. Copy se har round me **exactly ek extra hop** add hota hai.

## Complexity

- **Time:** O(k · E) — `k + 1` rounds, har round me saari E flights relax. (E = number of flights.)
- **Space:** O(n) — prices + tmp arrays.

> Alternative: Dijkstra with state `(cost, node, stops_remaining)` in a min-heap. Works, but you can't dedupe purely on node — must track stops too, warna cheaper-but-too-long paths galat answer de denge.

## Common Pitfalls

- **Snapshot na lena** — `prices` array ko in-place update karne se ek round me multiple hops leak ho jaate; answer galat (too cheap). `tmp = prices[:]` zaroori.
- **`k` vs `k+1`** — `k` stops matlab `k + 1` flights/edges. Loop `k + 1` baar chalao. Classic off-by-one.
- **Plain Dijkstra (node pe visited)** — cheapest path zyada hops le sakta; node ko "done" mark karne se valid k-hop path miss ho jaata.
- **`INF` se relax** — `prices[u] != INF` check karo warna `INF + w` overflow / nonsense.
- **Directed edges** — flights ek tarfa hain; reverse mat jodo.

## When to Use This Pattern

"Shortest/cheapest path **with a bound on number of edges/hops**" ya "graph me negative weights ho sakte" → **Bellman-Ford**. Cue: "at most K stops", "exactly K edges", "limited transfers", "negative cycle detection". Hop-limit ke saath Bellman-Ford's round-by-round structure perfectly fit baithta hai.

## NeetCode Link

https://neetcode.io/problems/cheapest-flight-path
