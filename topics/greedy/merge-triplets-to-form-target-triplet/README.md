# Merge Triplets to Form Target Triplet

**Category:** Greedy
**Difficulty:** medium

## Problem Statement

You are given a list of `triplets`, where `triplets[i] = [a, b, c]`, and a
`target = [x, y, z]`. You may repeatedly pick two triplets and **merge** them
into `[max(a1,a2), max(b1,b2), max(c1,c2)]` (component-wise max). Return `True`
if you can obtain `target` as one of your triplets after any number of merges.

```
triplets = [[2,5,3],[1,8,4],[1,7,5]], target = [2,7,5]
  -> True   # merge [1,7,5] and [2,5,3] -> [2,7,5]

triplets = [[3,4,5],[4,5,6]], target = [3,2,5]
  -> False  # no way to get a 2 in the middle without exceeding it
```

## Real-World Analogy

Socho tum **3 alag skill scores** (coding, design, communication) ka exact
target hire-bar match karna chahte ho, aur har candidate ke paas teeno me kuch
score hai. Merge ka matlab — do candidates ko "team up" karao, team ka har skill
me **best of the two** count hota hai. Ek dikkat: agar kisi candidate ka koi
skill target se **zyada** hai (over-qualified in that axis), to wo team me aate
hi us axis ko overshoot kara dega — wo candidate **useless** hai, skip karo.
Bache hue "safe" candidates me se, kya har skill axis pe **koi na koi** candidate
exactly target tak pahunchta hai? Agar teeno axes covered → target ban jaayega.

## Approach

Max merge ka ek pyara property hai: **galat (over-target) triplets ko ignore
kar do**, kyunki max kabhi ghcatega nahi — ek baar overshoot, hamesha overshoot.

To sirf un triplets ko dekho jisme **koi component target se bada nahi** hai
(`a<=x and b<=y and c<=z`). In "valid" triplets me se, har position pe check
karo: kya koi triplet us position pe **exactly** target value rakhta hai?

```python
def merge_triplets(triplets, target):
    x, y, z = target
    hit = set()                          # which positions we've matched exactly
    for a, b, c in triplets:
        if a > x or b > y or c > z:
            continue                      # over-target -> would overshoot, skip
        if a == x: hit.add(0)
        if b == y: hit.add(1)
        if c == z: hit.add(2)
    return len(hit) == 3
```

Greedy insight: merge sirf max leta hai, to merge karne se kabhi koi axis
ghatega nahi — isliye humein per-axis independently dekhna kaafi hai. Jin valid
triplets ne axis 0 ko `x` tak pahuchaaya, axis 1 ko `y` tak, axis 2 ko `z` tak —
un sabko merge kar do, target mil jaata hai.

## Complexity

- **Time:** O(n) — ek hi pass over the triplets, har triplet pe O(1) checks.
- **Space:** O(1) — bas ek 3-element set (positions 0,1,2).

## Common Pitfalls

- **Over-target triplets ko skip na karna** — agar `a > x` hai aur tum `a==x`
  wala condition match karne ki koshish me ise count kar lo, galat. Pehle poora
  triplet reject karo agar kisi bhi axis pe target cross kare.
- **"sum" ya "any one triplet equals target" sochna** — har axis independently
  match hota hai different triplets se; ek single triplet ka target ke barabar
  hona zaroori nahi.
- **`<` vs `<=`** — valid hone ke liye har component `<= target`, aur match ke
  liye `==`. Equal allowed hai (that's the whole point).

## When to Use This Pattern

"Component-wise max/min merge se ek target banana" → har axis ko independently
greedily satisfy karo, aur jo elements target ko cross karein unhe pehle filter
karo. Cue: monotonic merge operation (max only grows) → ek-baar-kharab-hamesha-
kharab → filter then per-dimension cover.

## NeetCode Link

https://neetcode.io/problems/merge-triplets-to-form-target
