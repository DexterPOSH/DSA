# Reverse Linked List

**Category:** Linked List
**Difficulty:** easy

## Problem Statement

Given the `head` of a singly linked list, reverse the list and return the new head.

```
1 -> 2 -> 3 -> 4 -> 5 -> None   ->   5 -> 4 -> 3 -> 2 -> 1 -> None
```

## Real-World Analogy

**What Azure Logic Apps is:** Azure Logic Apps is Azure's workflow automation service for building processes out of connected actions. Each workflow definition records which actions depend on other actions, so the service can run them in the right order and resume reliably. A simple straight-line workflow behaves like a linked list of actions.

**What `runAfter` dependency modeling is, and why it's used:** In Azure Logic Apps, `runAfter` declares that an action should wait for one or more earlier actions to finish with specific statuses, such as `Succeeded` or `Failed`. This explicit dependency model makes ordering visible in the workflow JSON and supports branching instead of hiding control flow inside code. In a simple chain, changing those dependency edges changes which action is considered next.

**The mapping:** Each node is one Azure Logic Apps action, and the linked-list `next` pointer is the chain edge represented by the workflow dependency relationship. Reversing the list means walking the chain once and rewiring the current action to point back to the previous action instead of forward. Before overwriting that edge you save the original next action as `nxt`, so the key insight is to preserve the remaining chain before flipping each pointer.

## Approach

**Iterative (3-pointer) — the standard answer:**

Ek `prev = None` se shuru karo. `curr` ko list pe chalao. Har node pe:

1. `nxt = curr.next` — aage ka raasta save karo (link torne se *pehle*).
2. `curr.next = prev` — pointer ulta karo, ab `curr` peeche ko point karta hai.
3. `prev = curr; curr = nxt` — dono ek step aage khisko.

Jab `curr` `None` ho jaye, `prev` naya head hai.

```python
def reverseList(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next      # save next before we clobber it
        curr.next = prev     # flip the pointer
        prev = curr          # advance prev
        curr = nxt           # advance curr
    return prev              # prev is the new head
```

**Recursive** — same idea, stack pe chalti hai:

```python
def reverseList(head):
    if not head or not head.next:
        return head
    new_head = reverseList(head.next)
    head.next.next = head    # the node ahead now points back to me
    head.next = None         # and I point to nothing (for now)
    return new_head
```

Pattern: **pointer reassignment with a saved `next`**. Yeh linked-list ka sabse core muscle hai.

## Complexity

- **Time:** O(n) — har node ko exactly ek baar visit karte hain.
- **Space:** O(1) iterative (sirf teen pointers). Recursive O(n) call-stack ke kaaran.

## Common Pitfalls

- **`nxt` save karna bhool jaana** — agar `curr.next = prev` pehle kar diya, to aage ka poora
  list gaayab. Order matters: pehle save, phir flip.
- **`head` ko return karna** — galat! Original head ab list ka **last** node hai. Naya head
  `prev` hai.
- **Empty list / single node** — `while curr` loop dono ko gracefully handle karta hai; recursive
  me explicit base case chahiye.
- **Recursive me `head.next = None` chhodna** — warna last node aur uske aage cycle ban jaata.

## When to Use This Pattern

Jab bhi "reverse a list", "reverse a sub-list", ya "reverse in groups of k" dikhe — yeh
3-pointer dance base hai. Palindrome-linked-list aur reorder-list jaise problems isi ko
half-list pe apply karte hain. Cue: **list ki direction badalni hai → prev/curr/next walk**.

## Practice

- Visual: open `topics/linked-list/reverse-linked-list/visual.html`

## NeetCode Link

https://neetcode.io/problems/reverse-a-linked-list
