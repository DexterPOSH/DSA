# Copy List With Random Pointer

**Category:** Linked List
**Difficulty:** medium

## Problem Statement

A linked list is given where **each node has two pointers**: `next` (normal) and `random` (points to *any* node in the list, or `None`). Return a **deep copy** of the list — brand new nodes, where the new `random` pointers mirror the original structure but point into the **copied** nodes (never the originals).

```
Original:   A -> B -> C        random: A.random = C,  B.random = A,  C.random = B
Copy:       A'-> B'-> C'       random: A'.random = C', B'.random = A', C'.random = B'
```

> Mushkil ye hai ki jab tum `A'` banaate ho, uska `random` `C` ki taraf point karta hai — but `C'` abhi tak exist hi nahi karta. "Future node" ko kaise point karoge?

## Real-World Analogy

Socho tumhare paas dosto ka ek **circle** hai. Har dost ke paas ek "next friend" (line me agla) aur ek "best friend" (koi bhi, kahin bhi) hai. Tumhe is poore circle ka ek **duplicate group** banana hai jisme rishte bilkul same ho — but duplicates ke best-friend bhi *duplicates* hi hone chahiye, original log nahi.

Sabse seedha tareeka: ek **phonebook (hash map)** rakho jo har original dost ke saamne uska clone likhe — `original -> clone`. Pehle sab clones bana lo (bina rishte jode). Phir dobara ghoomo aur har clone ke `next` / `best-friend` ko phonebook me lookup karke set kar do. "Original ke best friend ka clone kaun?" → phonebook bata dega.

## Approach

**Approach 1 — hash map (saaf aur intuitive, O(n) space):** Do pass. Pehle pass me har original node ka clone banao aur `mapping[orig] = clone` store karo. Doosre pass me har clone ke `next` aur `random` ko set karo — `mapping[orig.next]` aur `mapping[orig.random]` use karke (yaani original ke pointer ko follow karke uska clone uthao).

```python
def copyRandomList(head):
    if not head:
        return None
    mapping = {}                          # orig node -> cloned node
    cur = head
    while cur:                            # pass 1: clones banao
        mapping[cur] = Node(cur.val)
        cur = cur.next
    cur = head
    while cur:                            # pass 2: pointers wire karo
        mapping[cur].next   = mapping.get(cur.next)
        mapping[cur].random = mapping.get(cur.random)
        cur = cur.next
    return mapping[head]
```

> `mapping.get(...)` use karte hain taaki `None` (list ka end ya null random) bhi gracefully `None` map ho jaaye.

**Approach 2 — interleaving (O(1) extra space, slick):** Har original node ke *theek baad* uska clone interleave kar do: `A -> A' -> B -> B' -> ...`. Ab har clone `A'` apne original `A` ke `next` par hai, to `A'.random = A.random.next` (original ke random ka clone uske theek baad hi to hai!). Phin do lists ko un-weave karke alag kar do. Koi hash map nahi.

## Complexity

- **Time:** O(n) — dono approaches list ko constant number of passes me ghoomte hain.
- **Space:** Hash map → O(n) extra (mapping ke liye). Interleaving → O(1) extra (output ke alawa).

## Common Pitfalls

- **`random` ko original node pe point kar dena** — sabse common bug. Copy ka random hamesha *copy* ko point kare; mapping/interleaving isi liye chahiye.
- **`None` random / next handle na karna** — `mapping.get()` (ya explicit `if`) use karo warna `KeyError` ya null-deref.
- **Empty list (`head is None`)** — turant `None` return, warna pehle hi line pe crash.
- **Interleaving me un-weave karna bhoolna** — agar tumne lists separate nahi ki to original list corrupt return karta hai (interviewer usually original restore karwana chahta hai).
- **Ek hi pass me random wire karne ki koshish** — clone abhi bana nahi (future node), isiliye 2 passes ya interleaving chahiye.

## When to Use This Pattern

Jab kisi structure ka **deep copy** chahiye jisme nodes ke beech **arbitrary / non-linear references** ho (sirf next/parent nahi) → **old→new hash map** banao, phir references remap karo. Yahi pattern graph cloning (Clone Graph), tree-with-random-pointer, aur kisi bhi "duplicate this object graph" problem me chalta hai. Cue: "copy" + "pointer kahin bhi point kar sakta hai".

## NeetCode Link

https://neetcode.io/problems/copy-linked-list-with-random-pointer
