# Merge Two Sorted Lists

**Category:** Linked List
**Difficulty:** easy

## Problem Statement

Given the heads of two **sorted** singly linked lists `l1` and `l2`, splice them together into one
sorted list and return its head. The merged list should be made by reusing the existing nodes.

```
l1: 1 -> 2 -> 4
l2: 1 -> 3 -> 4
        ->   1 -> 1 -> 2 -> 3 -> 4 -> 4
```

## Real-World Analogy

Socho do alag-alag **already-sorted card piles** hain, dono face-up, sabse chhota card upar.
Tumhe ek single sorted pile banani hai. Tum dono piles ke top cards dekhte ho, jo **chhota
hai use uthate ho** apni nayi pile pe, aur us pile ka agla card expose ho jaata hai. Yeh
tab tak repeat karo jab tak ek pile khatam na ho jaye — phir jo bachi hui pile hai use
**poora ka poora** neeche attach kar do (woh already sorted hai).

Important trick: nayi pile shuru karne ke liye ek **dummy "placeholder" card** rakh lo. Isse
"pehla card kaunsa" wali special-case headache khatam — hamesha `tail.next` pe attach karte
raho, end me `dummy.next` return kar do.

## Approach

**Dummy head + tail pointer** — cleanest:

```python
def mergeTwoLists(l1, l2):
    dummy = tail = ListNode()      # placeholder; never moves
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1         # attach smaller node
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next           # advance the tail
    tail.next = l1 or l2           # attach the remaining (non-empty) list
    return dummy.next              # real head is one past the dummy
```

Har step pe do heads ke values compare karo, chhote wale ko `tail` ke aage jodo, us list ka
head aage badha do, aur `tail` ko move karo. Ek list khatam hote hi loop ruk jaata — bachi
list ko ek hi line me attach (`tail.next = l1 or l2`), kyunki woh already sorted hai.

Pattern: **two-pointer merge** (same engine jo merge-sort ke merge step me hota hai), with a
**dummy node** to dodge edge cases.

## Complexity

- **Time:** O(n + m) — har node exactly ek baar touch hota hai (n, m = dono lists ki length).
- **Space:** O(1) — koi naya node nahi banta, sirf pointers rewire hote hain. (Recursive version O(n+m) stack.)

## Common Pitfalls

- **Dummy node skip karna** — bina dummy ke, "head kaunsa hoga" handle karne me extra branching
  aur bugs. Dummy se code symmetric ho jaata.
- **`tail.next = l1 or l2` bhoolna** — leftover list attach na karoge to aadha answer kho doge.
- **`dummy` return karna `dummy.next` ke bajaye** — pehla node miss ho jaayega.
- **`<` vs `<=`** — duplicates ke saath stability ke liye `<=` use karo (galat answer nahi
  deta, par convention saaf rakhta).
- **Naye node `ListNode(...)` banana** — zaroorat nahi; existing nodes ko relink karo, O(1) space.

## When to Use This Pattern

"Do (ya k) sorted sequences ko ek sorted me merge karo" → two-pointer merge. K-sorted-lists,
merge-sort, aur "combine sorted streams" sab isi ki extension hain. Dummy-head trick har
list-building problem me kaam aata hai jahan head special-case lagta ho.

## Practice

- Visual: open `topics/linked-list/merge-two-sorted-lists/visual.html`

## NeetCode Link

https://neetcode.io/problems/merge-two-sorted-linked-lists
