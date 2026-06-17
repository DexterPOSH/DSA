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

Socho highway pe ek single lane hai, overtaking allowed nahi. Sabse aage wali car
ka **arrival time** fix hai. Uske peeche koi tej car aati hai — agar wo destination
pe pehle pahunchti (akele chalti to), matlab wo aage wali ko **pakad legi** raaste
me, aur fir uske peeche chipak ke ussi pace pe chalegi → **same fleet**. Lekin agar
peeche wali car aage wali se bhi *zyada time* leti hai (slower effectively), to wo
kabhi nahi pakad paayegi → **apni alag nayi fleet** ban jaati hai, aur ab *wo* nayi
"leader" ban jaati hai jise peeche walon ko match karna hoga.

Trick: cars ko **destination ke najdik se door ki taraf** (right-to-left) process
karo. Har car ka "akele lagne wala time" nikaalo. Ek stack jaisa leader-time rakho.

## Approach

Har car ka **time-to-reach** akele chalne pe: `(target - position) / speed`.
Cars ko **position ke descending order** me sort karo (destination ke sabse paas
wali pehle). Ab left-to-right is sorted order me chalo:

- Agar current car ka time **strictly zyada** hai pichhli fleet-leader ke time se,
  to ye car kabhi nahi pakad paayegi → **nayi fleet**, ye nayi leader ban jaati.
- Agar current car ka time **<=** leader ke time se hai, to ye pakad legi →
  same fleet me merge, leader nahi badalti.

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

`len(stack)` hi fleets ka count hai — har stack entry ek alag leader/fleet hai.

> **Stack kyun?** Technically yahan ek running-max bhi kaam karta, lekin
> conceptually ye **monotonic stack** hai: stack ke arrival times bottom→top
> increasing rehte hain, aur ek choti (faster-catching) car peeche wali ko "absorb"
> kar leti — bilkul next-greater style pop-merge logic.

## Complexity

- **Time:** O(n log n) — sorting dominate karti hai. Sort ke baad single pass O(n).
- **Space:** O(n) — pairs aur stack ke liye.

## Common Pitfalls

- **Sort direction galat** — destination ke **paas** wali car pehle aani chahiye
  (descending position). Ascending karoge to leader logic ulta ho jaayega.
- **`>` vs `>=`** — current time leader ke time ke **barabar** ho to wo same time pe
  pahunchti hai → problem statement ke mutabik **same fleet**. Isliye nayi fleet
  sirf jab `time > stack[-1]` (strictly greater).
- **Integer division** — `(target - pos) // spd` mat karo; time float hai, warna
  tie-breaking aur catch-up galat compute hoga. Plain `/` use karo.
- **Equal positions** — single lane me do car ek hi spot pe nahi ho sakti
  (constraint), so usually safe; par sort stable rakho.

## When to Use This Pattern

"Order-preserving merge / kaun kisko 'absorb' karega aage" type questions — jahan
elements ek direction me process hote hain aur ek monotonic property maintain hoti
hai. Cue: "cars/people/intervals jo ek doosre ko overtake nahi kar sakte" → right-
to-left scan + leader/stack. Cousins: Asteroid Collision, Next Greater Element.

## Practice

- Visual: open `topics/stack/car-fleet/visual.html`

## NeetCode Link

https://neetcode.io/problems/car-fleet
