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

**What Azure Event Hubs is:** Azure Event Hubs is Azure's streaming ingestion service for collecting high-volume events from many producers. It stores events in partitions, where each partition can be read forward in the order events were accepted. A consumer can build a new output stream by reading from partition cursors and appending events in the desired order.

**What ordered partition reading is, and why it's used:** Within one partition, Event Hubs preserves event order so consumers can replay a reliable sequence for a device, user, or partition key. This is used because many streaming workflows need per-key order, while partitioning still lets the service scale horizontally. When two partitions are already sorted by a comparable key like timestamp, a consumer only needs to compare the current front event from each partition.

**The mapping:** The two linked lists are the two Azure Event Hubs partition streams, and each `next` pointer is advancing that partition cursor. The algorithm compares the two current event keys, appends the smaller node to the output, and advances only the stream that contributed it. The dummy head is the opened destination stream, making every append the same `tail.next` operation, and the key insight is that sorted inputs let you make one local comparison at a time.

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
