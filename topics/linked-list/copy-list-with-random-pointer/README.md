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

**What Azure Resource Manager is:** Azure Resource Manager (ARM) is Azure's control plane for creating, updating, and organizing resources such as virtual machines, storage accounts, and networks. Every resource has a stable resource ID, and ARM deployments can create resources in a target resource group while tracking how they relate to each other. Cloning a resource set is not just copying names; the references between resources must be rebuilt too.

**What ARM reference rewriting is, and why it's used:** ARM resources refer to each other by resource IDs and declare dependencies so Azure knows which resources must exist before another resource can be configured. These references allow a VM to point at a NIC, a NIC to point at a subnet, or a setting to point at some other resource without embedding the whole resource. When you clone into a new resource group, old IDs cannot be reused because the clone must be independent of the original graph.

**The mapping:** The first pass through the list is like creating every cloned Azure Resource Manager resource and storing an `old ID -> new ID` table, while leaving references unresolved. The second pass is where `next` and `random` are rewired by looking up each original target in that table. The key insight is that a random pointer is just a cross-resource reference: it must point to the clone of the target, not the original target, so the map is what preserves graph shape without sharing nodes.

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
