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

Socho do log ek **circular running track** pe daudh rahe hain — ek **slow jogger** aur ek
**fast sprinter**. Agar track sach me circular (loop) hai, to fast wala chakkar kaat ke
**kabhi na kabhi slow wale ko peeche se aa ke pakad lega** — dono ek hi point pe mil jaayenge.
Lekin agar track seedha hai aur ek **dead-end (None)** pe khatam ho jaata hai, to fast wala
pehle hi end pe pahunch ke ruk jaayega — kabhi mil nahi paayenge.

Yahi **Floyd's Tortoise and Hare** hai: `slow` ek step, `fast` do step. Loop hai → kabhi
`slow == fast`. Loop nahi hai → `fast` `None` pe gir jaayega.

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
