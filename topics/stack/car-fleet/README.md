# Car Fleet

**Category:** Stack (Monotonic Stack)
**Difficulty:** medium

## Problem Statement

There are `n` cars on a single-lane road heading to a destination at position
`target`. Car `i` starts at position `position[i]` with speed `speed[i]`. A faster
car can **never pass** a slower car ahead — it catches up and then they move
together as one **fleet** (at the slower car's pace). Two cars that arrive at the
destination at the exact same time also count as one fleet.

Return the **number of car fleets** that arrive at the destination.

```
target = 12
position = [10, 8, 0, 5, 3]
speed    = [ 2, 4, 1, 1, 3]
->  3 fleets
```

## Real-World Analogy

**What Azure Virtual Machine Scale Sets is:** Azure Virtual Machine Scale Sets let you run and manage many identical VMs as one elastic compute group. Azure can add or remove instances, spread them across zones, and apply model or OS updates without treating every VM as a separate snowflake. For a service behind a load balancer, the goal is coordinated capacity: change the group while keeping enough healthy instances serving traffic.

**What the rolling upgrade mechanism is, and why it's used:** A VM Scale Set rolling upgrade applies an update in batches instead of updating every instance at once. Azure waits for each batch to complete and pass health checks before moving farther through the set, with settings such as batch size and pause time controlling blast radius. That batching exists because the rollout should be governed by safe, ordered waves rather than by whichever individual instance could finish fastest on its own.

**The mapping:** Sort cars by position descending like looking at Azure upgrade waves from the instances closest to the target state back toward the ones still behind. A car's solo arrival time is a batch's solo completion time; the stack top is the current wave leader's completion gate. If a behind car would arrive sooner or at the same time, it catches that gate and merges into the leader's fleet; if it would arrive later, it becomes a new wave leader. The key insight is that only strictly slower completion times survive on the stack, so `len(stack)` is the number of independent fleets/waves.

## Approach

Each car's solo **time-to-reach** is `(target - position) / speed`.
Sort cars by **position in descending order** (the car closest to the destination
comes first). Then scan this sorted order from left to right:

- If the current car's time is **strictly greater** than the previous fleet leader's time,
  it can never catch that fleet → **new fleet**, and this car becomes the new leader.
- If the current car's time is **<=** the leader's time, it will catch up →
  merge into the same fleet, and the leader does not change.

```python
def car_fleet(target, position, speed):
    # pair karo, fir destination ke paas wali (badi position) pehle
    cars = sorted(zip(position, speed), reverse=True)
    stack = []                                   # fleet leaders ke arrival times
    for pos, spd in cars:
        time = (target - pos) / spd
        # agar ye car aage wali fleet se zyada time leti -> alag fleet
        if not stack or time > stack[-1]:
            stack.append(time)                   # nayi fleet
        # warna: pakad legi -> same fleet (stack me kuch add nahi)
    return len(stack)
```

`len(stack)` is the fleet count — each stack entry is a separate leader/fleet.

> **Why a stack?** Technically a running maximum also works here, but conceptually
> this is a **monotonic stack**: arrival times increase from bottom→top, and a
> smaller-time (faster-catching) car gets "absorbed" by the fleet ahead — just like
> next-greater-style pop/merge logic.

## Complexity

- **Time:** O(n log n) — sorting dominates. After sorting, the scan is O(n).
- **Space:** O(n) — for the pairs and the stack.

## Common Pitfalls

- **Wrong sort direction** — the car **closest** to the destination must come first
  (descending position). If you sort ascending, the leader logic is reversed.
- **`>` vs `>=`** — if the current time is **equal** to the leader's time, it arrives
  at the same time → per the problem statement, that is the **same fleet**. Create a
  new fleet only when `time > stack[-1]` (strictly greater).
- **Integer division** — do not use `(target - pos) // spd`; time is fractional, and
  integer division breaks tie and catch-up logic. Use plain `/`.
- **Equal positions** — on a single-lane road, two cars cannot usually start at the
  same spot (constraint), so this is normally safe; still keep sorting deterministic.

## When to Use This Pattern

"Order-preserving merge / who absorbs whom ahead" type questions — where elements
are processed in one direction while a monotonic property is maintained. Cue:
"cars/people/intervals that cannot overtake each other" → right-to-left scan +
leader/stack. Cousins: Asteroid Collision, Next Greater Element.

## Practice

- Visual: open `topics/stack/car-fleet/visual.html`

## NeetCode Link

https://neetcode.io/problems/car-fleet
