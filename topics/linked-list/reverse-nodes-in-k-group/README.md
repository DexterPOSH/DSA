# Reverse Nodes in K-Group

**Category:** Linked List
**Difficulty:** hard

## Problem Statement

Given the head of a linked list, reverse the nodes **`k` at a time** and return the modified list. If the number of remaining nodes is **fewer than `k`**, leave them as-is (do **not** reverse a partial group).

```
1->2->3->4->5 , k = 2   ->  2->1->4->3->5
1->2->3->4->5 , k = 3   ->  3->2->1->4->5
1->2->3->4->5 , k = 4   ->  4->3->2->1->5   # last group {5} < k, untouched
```

## Real-World Analogy

Socho ek **train** hai jiske dabbe (nodes) ek line me jude hain. Tumhe har **`k` dabbon ka group** uthana hai aur uss group ko **ulta** karke wapas patri pe jod dena hai — but groups ke beech ka connection toota nahi rehna chahiye, train continuous honi chahiye.

Har group ke liye ek shunting-yard worker: pehle wo aage jaake check karta hai ki **poore `k` dabbe bache hain ya nahi**. Agar bache → group reverse karo aur dono taraf se sahi se reconnect karo. Agar `k` se kam bache → unhe chhod do as-is. Asli mehnat hai connections sambhalna: pichle group ki tail naye reversed group ke head se jude, aur reversed group ki tail (jo pehle head thi) agle group se.

## Approach

**Pattern: in-place pointer reversal with a dummy head + group boundaries.**

Ek `dummy` node head ke aage lagao (first group reverse hone pe head badalta hai — dummy se yeh clean rehta). `group_prev` = group se theek pehle wala node.

Har iteration:
1. **Count `k` nodes aage:** `group_prev` se k step chalo (`kth`). Agar beech me `None` mil gaya → `k` nodes nahi hain → **stop**, baaki list as-is chhod do.
2. **Reverse the group:** standard 3-pointer reversal, but sirf `kth` ke baad wale node (`group_next`) tak. Group ke nodes ko ulta link karo.
3. **Reconnect:** `group_prev.next` ab group ke naye head (purani kth) se jude; group ki purani head (jo ab tail hai) `group_next` se jude.
4. `group_prev` ko us purani head (naye group ki tail) pe move karo, repeat.

```python
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        # 1) kth node from group_prev (k hops). None -> fewer than k left.
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next

        # 2) reverse the group [group_prev.next .. kth]
        prev, curr = group_next, group_prev.next
        while curr != group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt

        # 3) reconnect; group_prev.next was the old head = new tail
        old_head = group_prev.next     # this becomes the group's tail
        group_prev.next = kth          # kth is the new head of the group
        group_prev = old_head          # advance to tail for next group
```

> **Reverse loop ka twist:** normal reversal `prev = None` se shuru hota. Yahan `prev = group_next` se shuru karte — isse reversed group ki tail automatically `group_next` se judi reh jaati, ek alag reconnect step bach jaata.

## Complexity

- **Time:** O(N) — har node exactly do baar touch hota at most (ek count me, ek reverse me). N = total nodes.
- **Space:** O(1) — sirf kuch pointers, koi extra structure nahi. (Recursive version O(N/k) stack use karta — iterative wala truly O(1).)

## Common Pitfalls

- **Partial group reverse kar dena** — agar bache hue nodes `< k` hain to unhe **chhodna** hai. Count-check (`if not kth: return`) zaroori; warna tail galat ho jaayega.
- **Reconnect galat** — sabse bada bug: reverse ke baad `group_prev.next` ko naye head se, aur old-head ko `group_next` se jodna bhulna → list tooti ya cycle ban jaati.
- **`group_prev` advance bhulna** — har group ke baad `group_prev` ko us group ki *nayi tail* (= old head) pe le jaana zaroori, warna agla group galat jagah se shuru hoga.
- **Dummy head na lagana** — first group reverse hone pe actual head badalta; bina dummy ke head-tracking messy ho jaata.
- **`k = 1`** — kuch nahi badalna chahiye; code naturally handle karta (group reverse no-op).

## When to Use This Pattern

Jab linked-list ko **fixed-size chunks me reverse/rotate/process** karna ho with strict group boundaries → dummy head + count-ahead + in-place 3-pointer reversal + careful reconnect. Cousins: "reverse linked list II" (sub-range), "swap nodes in pairs" (yeh `k=2` ka special case hai), "rotate list". Cue: *"k at a time" / "in groups of k"* on a linked list → yahi structure.

## Practice

- Visual: open `topics/linked-list/reverse-nodes-in-k-group/visual.html`

## NeetCode Link

https://neetcode.io/problems/reverse-nodes-in-k-group
