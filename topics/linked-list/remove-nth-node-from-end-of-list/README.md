# Remove Nth Node From End of List

**Category:** Linked List
**Difficulty:** medium

## Problem Statement

Given the `head` of a singly linked list, remove the **nth node from the end** of the list and return the head of the modified list. Do it ideally in **one pass**.

```
1 -> 2 -> 3 -> 4 -> 5,  n = 2   ->   1 -> 2 -> 3 -> 5
                                          (node "4" removed)

1,  n = 1   ->   (empty list)
```

> Linked list me tum sirf `head` se aage chal sakte ho — peeche nahi ja sakte, aur length pehle se pata nahi. "End se nth" ka matlab hai pehle ye janna padega ki list kitni lambi hai... ya phir ek chalaaki use karni padegi.

## Real-World Analogy

Socho ek train hai aur tumhe **end se 2nd dabba** nikaalna hai, but tum platform pe khade ho aur train ke aage-se-peeche poori length nahi dekh sakte. Trick: do scouts bhejo. Pehla scout **2 dabbe aage** chalna shuru karta hai. Phir dono scouts ek saath, same speed se chalte hain. Jab aage waala scout train ke **bilkul end** pe pahunchta hai, tab peeche waala scout **theek us dabbe ke just pehle** khada hota hai jise hatana hai. Bas us dabbe ka coupling skip karke agle se jod do.

Yahi **two-pointer with a gap** technique hai — gap ko `n` set karo, phir saath chalao.

## Approach

**Brute force (two pass)** — pehle poori list ka length `L` count karo, phir front se `L - n` steps chal kar previous node tak jaao aur unlink kar do. Kaam karta hai but list ko do baar traverse karta hai.

**Optimal — two pointers, one pass:** Ek **dummy node** head ke aage lagao (taaki "head hi delete ho raha hai" wala edge case bhi automatically handle ho). `fast` aur `slow` dono dummy se start. Pehle `fast` ko **n+1 steps aage** le jaao (dummy se gap banane ke liye). Phir dono ko saath chalao jab tak `fast` end (`None`) na ho jaaye. Ab `slow` us node pe khada hai jiske **just pehle** hai target — `slow.next = slow.next.next` se unlink.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n + 1):        # fast ko n+1 aage le jaao
        fast = fast.next
    while fast:                   # dono saath chalao end tak
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next    # target node ko unlink karo
    return dummy.next
```

Pattern: **two pointers with a fixed gap** on a linked list + **dummy/sentinel node** trick.

## Complexity

- **Time:** O(L) — list ko ek hi baar traverse karte hain (L = length).
- **Space:** O(1) — sirf do pointers, koi extra data structure nahi.

## Common Pitfalls

- **Dummy node skip karna** — agar pehla hi node delete karna ho (`n == length`), to bina dummy ke `head` reassign karna padega; dummy se ye case free me handle ho jaata hai.
- **Gap galat (`n` vs `n+1`)** — `fast` ko `n+1` aage le jaana hai (dummy se), warna `slow` target node *par* ruk jaayega uske *pehle* nahi, aur tum unlink nahi kar paoge.
- **`slow.next.next` se pehle null check** — agar gap sahi hai to ye safe hai, but galat gap par yahan `NoneType` crash milega.
- **Return `head` instead of `dummy.next`** — agar head delete hua to purana `head` ab detached hai; hamesha `dummy.next` return karo.

## When to Use This Pattern

Jab bhi linked list me "end se kth element" / "kth-from-last" / "list ke ek fixed offset par" wala kaam dikhe aur tum **ek hi pass** me karna chaaho — **two pointers with a gap** socho. Same idea: find middle (gap = half via slow/fast), detect cycle entry, etc. Dummy node tab use karo jab head khud modify/delete ho sakta ho.

## NeetCode Link

https://neetcode.io/problems/remove-node-from-end-of-linked-list
