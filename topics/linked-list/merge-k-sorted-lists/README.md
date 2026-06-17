# Merge K Sorted Lists

**Category:** Linked List
**Difficulty:** hard

## Problem Statement

You are given an array of `k` linked lists, each **already sorted** in ascending order. Merge them into **one** sorted linked list and return its head.

```
lists = [ 1->4->5 , 1->3->4 , 2->6 ]
        ->  1->1->2->3->4->4->5->6
```

Let `N` = total number of nodes across all lists.

## Real-World Analogy

Socho `k` alag-alag **vending machine queues** hain, har queue apne aap me sorted (sabse chhota aage). Tumhe ek single sorted line banani hai. Har baar tum saari queues ke **front (sabse aage wale) bande** ko dekho aur unme se **sabse chhota** uthao — usse final line me daal do, aur uss queue ka agla banda front pe aa jaata hai.

Har step pe "k fronts me se minimum" baar-baar chahiye — yeh exactly **min-heap (priority queue)** ka kaam hai. Heap har baar O(log k) me sabse chhota nikaal deta hai, poori queue scan kiye bina.

## Approach

Naive: saare nodes ek array me daalo, sort karo, dobara list banao — O(N log N), but lists ka *already sorted* hona waste ho jaata.

**Optimal A — min-heap (O(N log k)):**

Heap me hamesha har list ka *current front* node rakho (at most `k` nodes). Sabse chhota pop karo, result me append karo, aur uss node ke `next` ko heap me push karo. Heap kabhi `k` se bada nahi hota.

```python
import heapq

def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))  # i = tiebreaker
    dummy = tail = ListNode()
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

> **Tuple me `i` kyun?** Jab do nodes ki `val` equal ho, Python heap teesre element pe `<` try karta hai — aur do `ListNode` objects comparable nahi hote (TypeError). List-index `i` ek unique tiebreaker hai, comparison wahin ruk jaata hai.

**Optimal B — divide & conquer (O(N log k), O(1) extra):**

`k` lists ko pairwise merge karo (jaise merge-sort ka merge step), har round me list-count aadhi. `log k` rounds, har round me total O(N) kaam → O(N log k). Heap ka space bhi bachta hai.

```python
def merge_two(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val: tail.next, a = a, a.next
        else:              tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next

def merge_k_lists(lists):
    if not lists: return None
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            b = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(lists[i], b))
        lists = merged
    return lists[0]
```

## Complexity

- **Time:** O(N log k) — har node exactly ek baar process; heap op (ya merge-tree depth) O(log k). N nodes total.
- **Space:** heap version O(k) (heap me at most k nodes). Divide & conquer O(1) extra (recursion/loop chhod ke), in-place pointer relinking.

> Compare: list-banake-sort wala O(N log N) hota — `log N` vs `log k`. Kyunki `k <= N`, heap/D&C ka `log k` chhota ya barabar hai.

## Common Pitfalls

- **Heap me raw node push karna** without a tiebreaker → equal values pe `ListNode < ListNode` TypeError. Hamesha `(val, index, node)` tuple use karo.
- **Empty / `None` lists handle na karna** — `lists = []`, ya `lists = [None, None]`. Heap me push se pehle `if node` check zaroori.
- **Dummy head na use karna** — result list build karte time dummy sentinel se first-node ka special case khatam ho jaata.
- **Naya extra nodes banana** — zaroorat nahi; existing nodes ko hi relink karo (space bachao).
- **O(N·k) brute force** — har step pe k heads ko linearly scan karke min dhoondhna → total O(N·k), heap se slow. Bade `k` pe TLE.

## When to Use This Pattern

"`k` sorted sequences/streams ko merge karo" ya "har step pe k candidates me se min/max chahiye" → **min-heap of size k**. Yeh pattern external merge-sort, k-way merge in databases, aur "smallest range covering k lists" type problems me aata. Cue: *multiple sorted inputs + repeatedly pick the extreme* → heap.

## Practice

- Visual: open `topics/linked-list/merge-k-sorted-lists/visual.html`

## NeetCode Link

https://neetcode.io/problems/merge-k-sorted-linked-lists
