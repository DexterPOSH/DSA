# Linked List Cycle

**Category:** Linked List
**Difficulty:** easy

## Problem Statement

Given the `head` of a singly linked list, return `True` if the list has a **cycle** (some node's
`next` points back to an earlier node), and `False` otherwise.

```
3 -> 2 -> 0 -> -4
     ^---------+        ->  True   (tail -4 points back to node 2)

1 -> 2 -> None          ->  False
```

## Real-World Analogy

**What Azure Virtual Network is:** Azure Virtual Network (VNet) is Azure's private networking boundary for cloud resources, and Azure Route Server can exchange routes between that VNet and network appliances using BGP. Together they let traffic follow a series of next-hop decisions across peerings, gateways, or appliances. A healthy path eventually reaches its destination instead of looping.

**What next-hop routing is, and why it's used:** Each route tells Azure where to send a packet next, such as to a virtual appliance, gateway, peered VNet, or the internet. Next hops make large networks manageable because each component only needs to know the next step, not the full physical journey. But if a route points back to an earlier hop, traffic can cycle forever unless the loop is detected.

**The mapping:** Each linked-list node is one Azure routing hop, and `next` is the route's next-hop pointer. Floyd's `slow` probe follows one hop at a time while `fast` follows two; if the path loops, the faster probe must eventually lap the slower probe inside the cycle. If `fast` reaches `None`, the route terminates cleanly, so the key insight is that unequal-speed probes detect cycles without storing every visited hop.

## Approach

**Brute force** — har node ko ek `seen` set me daalo, repeat dikhe to cycle (O(n) space).

**Optimal — Floyd's fast/slow pointers** (O(1) space):

```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next          # 1 step
        fast = fast.next.next     # 2 steps
        if slow is fast:          # they met -> cycle
            return True
    return False                  # fast hit None -> no cycle
```

Dono `head` se shuru. Har iteration me `slow` 1 aur `fast` 2 aage. Agar loop hai, gap har step
1 se ghat-ta hai, to eventually `fast` `slow` ko **pakad leta** (modular arithmetic se guaranteed).
Agar loop nahi, `fast` ya `fast.next` `None` ho jaata aur loop ruk jaata.

> **`is` vs `==`:** node **identity** compare karni hai (same object), values nahi — isliye `is`.

Pattern: **fast & slow pointers (Floyd's cycle detection)**.

## Complexity

- **Time:** O(n) — non-cyclic me fast n/2 steps me end pe. Cyclic me bhi linear: meeting loop
  ki length ke andar ho jaati hai.
- **Space:** O(1) — sirf do pointers, koi extra set nahi (yahi brute force pe jeet hai).

## Common Pitfalls

- **`while fast and fast.next` na likhna** — `fast.next.next` access karne se pehle dono check
  karne padte, warna `None.next` pe crash.
- **`==` use karna `is` ke bajaye** — values match karne se false positive aa sakta agar duplicate
  values hon. Identity check chahiye.
- **`slow = fast = head` ke bajaye fast ko head.next se shuru karna** — kuch versions me chalta,
  par same-start version saaf aur kam buggy hai; loop condition uske hisaab se rakho.
- **"Cycle ki shuruaat kahan hai" se confuse hona** — yeh problem sirf *exists or not* poochta;
  start node nikalna (Floyd's phase 2) alag follow-up hai.

## When to Use This Pattern

"Kya linked list / sequence me loop hai", "duplicate number find karo (array as implicit list)",
ya "O(1) space me cycle/middle detect karo" → fast/slow pointers. Middle-of-list, palindrome-list,
aur find-duplicate (LC 287) sab isi tortoise-hare idea pe khade hain.

## Practice

- Visual: open `topics/linked-list/linked-list-cycle/visual.html`

## NeetCode Link

https://neetcode.io/problems/linked-list-cycle-detection
