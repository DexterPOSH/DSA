# Find the Duplicate Number

**Category:** Linked List (Floyd's cycle on an array)
**Difficulty:** medium

## Problem Statement

Given an array `nums` of `n + 1` integers where every value is in the range `[1, n]` (inclusive), exactly **one** value is repeated (it may appear more than once). Find that repeated number **without modifying the array** and using only **O(1) extra space**.

```
[1, 3, 4, 2, 2]   ->  2
[3, 1, 3, 4, 2]   ->  3
[1, 1]            ->  1
```

> Constraints crucial hain: no extra space (so no hash set), no array mutation (so no sorting / marking). Ye combination hi Floyd's cycle trick ko jaruri banata hai.

## Real-World Analogy

Array ko ek **chhupi hui linked list** ki tarah socho. Har index ek node hai, aur node `i` ka "next" pointer hai `nums[i]` (yaani value tumhe agle index par bhej deti hai). Index `0` se chalna shuru karo: `0 -> nums[0] -> nums[nums[0]] -> ...`.

Ab kyunki ek value **repeat** hoti hai, do alag index **same node** par point karte hain — yaani is "list" me ek **cycle** ban jaata hai, aur **cycle ka entry point hi duplicate number hai**. Ab problem reduce ho gaya: "linked list me cycle ka start dhoondo" — exactly **Floyd's Tortoise & Hare** (Linked List Cycle II). Koi extra memory nahi, array bhi untouched.

## Approach

**Phase 1 — cycle detect karo (slow/fast):** `slow` ek step (`nums[slow]`), `fast` do step (`nums[nums[fast]]`). Cycle ke andar ye zaroor milenge — ek **meeting point** par ruk jao.

**Phase 2 — cycle ka entry (= duplicate) dhoondo:** Ek pointer wapas `0` se start karo, doosra meeting point se. Dono ko **ek-ek step** chalao; jahan milenge wahi cycle entry = duplicate number (Floyd's math: head se entry tak ka distance = meeting point se entry tak ka distance).

```python
def findDuplicate(nums):
    slow = fast = 0
    while True:                       # phase 1: meeting point dhoondo
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow2 = 0                         # phase 2: entry (= duplicate) dhoondo
    while slow != slow2:
        slow  = nums[slow]
        slow2 = nums[slow2]
    return slow
```

Pattern: **Floyd's cycle detection** ko ek array par apply karna by treating `index -> nums[index]` as implicit linked-list edges.

## Complexity

- **Time:** O(n) — dono phases linear, constant passes.
- **Space:** O(1) — sirf do-teen pointers, array bilkul read-only.

## Common Pitfalls

- **Index 0 hamesha safe start kyun?** Values `[1, n]` range me hain, to koi bhi node `0` ko point nahi karta — yaani `0` cycle ke andar nahi ho sakta, perfect "list head". Isiliye start `0`.
- **Phase 2 me galat speed** — entry dhoondhte waqt **dono** pointers ko **ek-ek** step (slow speed) chalao, dono fast nahi.
- **Equality check timing (phase 1)** — pehle move karo phir compare; dono `0` se start hote hain, warna loop turant `slow == fast` maan ke galat exit kar jaayega.
- **Galat alternative chunna** — binary search on value-range (count ≤ mid) bhi O(1) space + O(n log n) me kaam karta; agar Floyd yaad na aaye to ye fallback hai, but optimal O(n) Floyd hi hai.
- **Sort ya hash set use karna** — dono constraints (no mutation / O(1) space) todte hain; interview me reject ho jaayega.

## When to Use This Pattern

Jab "duplicate / repeated element" + **no extra space** + **no mutation** dikhe, aur values khud valid indices ho (`[1, n]` in size `n+1`) → array ko implicit linked list maano aur **Floyd's cycle (Tortoise & Hare)** lagao. Yahi cycle-entry trick directly Linked List Cycle II hai — pehchaan: "value se index banta hai, repeat = cycle".

## NeetCode Link

https://neetcode.io/problems/find-duplicate-integer
