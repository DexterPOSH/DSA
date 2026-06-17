# Reorder List

**Category:** Linked List
**Difficulty:** medium

## Problem Statement

Given the head of a singly linked list `L0 -> L1 -> ... -> Ln-1 -> Ln`, reorder it **in place** to:

```
L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...
```

You may not modify node **values** — only rearrange the nodes themselves.

```
1 -> 2 -> 3 -> 4          ->   1 -> 4 -> 2 -> 3
1 -> 2 -> 3 -> 4 -> 5     ->   1 -> 5 -> 2 -> 4 -> 3
```

## Real-World Analogy

Socho ek lambi line of people hai aur tumhe usse **"zip" karna hai** — pehla front se, phir
ekdum last wala, phir doosra front se, phir second-last... ek-ek karke aage aur peeche se
alternate. Aise karne ka sabse aasaan tareeka? Line ko **beech se kaato**: ek aadhi line
front-half, doosri back-half. Ab back-half ko **ulta ghuma do** (taaki last wala uske aage
aa jaaye), aur phir dono halves ko **alternate karke aapas me interleave (zip)** kar do.

Teen familiar moves ka combo: **find middle → reverse second half → merge/zip two halves**.

## Approach

Yeh problem teen classic sub-routines ka sandwich hai:

**Step 1 — find the middle (fast/slow):** `slow` 1 step, `fast` 2 step. `fast` end pe → `slow`
middle pe.

**Step 2 — reverse the second half:** standard 3-pointer reversal, `slow.next` se shuru. Pehli
half ka tail (`slow`) ko `None` se cut karo.

**Step 3 — merge alternately:** do heads `first` (front-half) aur `second` (reversed back-half).
Alternate karke link karo jab tak `second` khatam na ho.

```python
def reorderList(head):
    # 1) middle: slow ends at mid
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # 2) reverse second half
    prev, curr = None, slow.next
    slow.next = None              # split the list into two halves
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    second = prev

    # 3) merge two halves alternately
    first = head
    while second:
        n1, n2 = first.next, second.next
        first.next = second
        second.next = n1
        first, second = n1, n2
```

Pattern: **composition of three primitives** — fast/slow middle, in-place reverse, two-pointer
merge. Har piece akela easy hai; tricky part inko bug-free jodna.

## Complexity

- **Time:** O(n) — middle O(n) + reverse O(n) + merge O(n) = teen linear passes.
- **Space:** O(1) — sab in-place pointer rewiring, koi extra structure nahi.

## Common Pitfalls

- **Second half ko cut na karna (`slow.next = None`)** — dono halves overlap rahengi, merge me
  cycle ya infinite loop ban jaayega.
- **Merge me `n1`/`n2` save na karna** — `first.next = second` karte hi original `next` gum;
  pehle dono saved pointers nikaalo.
- **Odd-length list pe galti** — `slow` middle pe rukta hai; front-half ek node lambi (ya barabar)
  rehti hai, isliye merge `while second:` pe rukta hai (front ka aakhri node already None-terminated).
- **Values swap karne ki koshish** — problem nodes rearrange chahta, values nahi; bade lists pe
  value-copy O(n) extra space bhi le sakta. Pointer relink hi sahi.
- **Reverse karte waqt naya head (`prev`) track na karna** — merge ko reversed-half ka head chahiye.

## When to Use This Pattern

Jab ek list problem "front aur back ko interleave/compare karo" maange — reorder, palindrome-list,
"k-th from end" — to socho **fast/slow se middle nikaalo + reverse + two-pointer**. Yeh teen
primitives ka toolbox poore linked-list category ka backbone hai.

## Practice

- Visual: open `topics/linked-list/reorder-list/visual.html`

## NeetCode Link

https://neetcode.io/problems/reorder-linked-list
