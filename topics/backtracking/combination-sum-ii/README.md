# Combination Sum II

**Category:** Backtracking
**Difficulty:** medium

## Problem Statement

Given a collection of candidate numbers `candidates` (**may contain duplicates**) and a
`target`, find all **unique combinations** that sum to `target`. **Each number may be used at
most once** in a combination. The solution set must not contain duplicate combinations.

```
candidates = [10, 1, 2, 7, 6, 1, 5], target = 8
->  [[1,1,6], [1,2,5], [1,7], [2,6]]

candidates = [2, 5, 2, 1, 2], target = 5
->  [[1,2,2], [5]]
```

## Real-World Analogy

**What Azure Capacity Reservations are:** Azure Capacity Reservations let you reserve compute capacity for specific VM sizes in a region or Availability Zone so future VM deployments have capacity waiting for them. A reservation group can contain a finite set of reserved VM-size slots, and a matching VM consumes one of those slots when it is placed. Unlike reusable SKU planning, each reserved slot is a concrete capacity unit that can be used at most once.

**What finite-slot duplicate handling is, and why it's used:** A capacity reservation group may contain multiple separate slots for the same VM SKU, such as two 1-vCPU reservations. Those duplicates are real capacity, so a deployment may use both, but swapping which identical slot you name first does not create a new Azure plan. Sorting identical SKUs together and skipping duplicates at the same recursion level removes repeated plans while preserving the ability to consume multiple copies when needed.

**The mapping:** Each number is one Azure reservation slot, `remain` is the target quota left, and choosing a slot moves recursion to `i + 1` because that exact slot cannot be reused. If the branch hits zero, the reservation mix is complete; if it overshoots or runs out, backtracking restores the slot and tries the next unique option. The key insight is to distinguish duplicate values from duplicate choices: use each slot once, but report each capacity combination once.

## Approach — sort + (`i+1` for one-use) + same-level dedup

Combination Sum se do changes:
1. **One-use:** recurse karte waqt `i + 1` do (na ki `i`) — same element dobara nahi.
2. **Dedup:** sort + `if i > start and candidates[i] == candidates[i-1]: continue`.

```python
def combination_sum2(candidates, target):
    candidates.sort()                         # duplicates ko adjacent + early break
    res, path = [], []

    def backtrack(start, remain):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue                       # SKIP same-level duplicate
            if candidates[i] > remain:
                break                          # sorted -> aage sab overshoot, stop
            path.append(candidates[i])
            backtrack(i + 1, remain - candidates[i])   # i+1 -> each used once
            path.pop()                                  # BACKTRACK

    backtrack(0, target)
    return res
```

> **`i+1` vs `i` — yahi Combination Sum I se asli farak.** I me reuse allowed tha (`i`),
> yahan har coin once (`i+1`). Aur dedup line bilkul Subsets II jaisi — pattern transfer ho
> raha hai.

## Complexity

- **Time:** O(2^n) worst case (n = len(candidates)) — har element pe include/exclude jaisa;
  sort `O(n log n)` usme dab jaata. Pruning (`break` + dedup) isse practically chhota karta.
- **Space:** O(n) recursion depth + path.

## Common Pitfalls

- **`i` likh dena (reuse)** instead of `i+1` → same coin do baar, "use once" rule toot-ta.
- **Sort ya dedup line bhulna** → duplicate combinations jaise do `[1,7]`.
- **`i > start` ki jagah `i > 0`** → first duplicate ko bhi skip kar deta, valid `[1,1,6]`
  type combos miss.
- **`break` (sorted overshoot) ki jagah `continue`** → kaam to karega but slower; sorted me
  ek overshoot ka matlab baaki sab overshoot.

## When to Use This Pattern

"Unique combinations, each element **once**, input me **duplicates**" → sort + `i+1` + same-level
skip. Yeh Combination Sum I (reuse) + Subsets II (dedup) ka exact mashup hai. Cue: "use each
number at most once" + repeated values in input.

## NeetCode Link

https://neetcode.io/problems/combination-target-sum-ii
