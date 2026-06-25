# Add Two Numbers

**Category:** Linked List
**Difficulty:** medium

## Problem Statement

Do non-empty linked lists diye gaye hain jo do non-negative integers ko represent karte hain. Digits **reverse order** me store hain (units digit head par), aur har node ek single digit rakhta hai. Dono numbers add karo aur sum ko ek **naye linked list** ke roop me (same reverse order me) return karo.

```
l1 = 2 -> 4 -> 3   (represents 342)
l2 = 5 -> 6 -> 4   (represents 465)
sum = 807          ->   7 -> 0 -> 8

l1 = 9 -> 9         (99)
l2 = 1              (1)
sum = 100           ->   0 -> 0 -> 1
```

> Reverse order ek tohfa hai — units digit pehle aata hai, exactly jaise tum haath se jod karte ho: right se left, carry aage le jaate hue.

## Real-World Analogy

**What Azure Service Bus is:** Azure Service Bus is a managed messaging broker for decoupling producers and consumers across cloud apps. It stores messages durably in queues or topics so a worker, such as an Azure Function, can process them reliably even if the sender and receiver run at different times. In this analogy, each Service Bus session is one ordered stream of digit messages.

**What Service Bus session ordering is, and why it's used:** A session groups related messages under a session ID and lets a receiver process that group in FIFO order while holding a session lock. This exists for workflows where order matters, like all events for one order or customer, instead of treating every message as independent. The receiver can keep a small carry value while it walks the two sessions because addition only needs the current pair of digits plus overflow from the previous pair.

**The mapping:** The two linked lists are the two Azure Service Bus sessions; each node is the current digit message, and `next` is reading the next message in that session. The algorithm adds the two current payloads plus `carry`, emits `sum % 10` as the next result message, and moves the carry `sum // 10` forward. Because the lists store least-significant digits first, the streaming order matches arithmetic order exactly; the dummy head is the already-open output stream, so every new digit appends the same way, and the key insight is to process one digit and one carry at a time.

## Approach

Ek **dummy head** se naya list build karo. Dono lists ko saath-saath traverse karo. Har step par: `l1` ka digit + `l2` ka digit + `carry` jodo. Naya digit `total % 10`, aur naya `carry = total // 10`. Loop tab tak chalao jab tak koi bhi list bachi ho **ya** carry bacha ho.

```python
def addTwoNumbers(l1, l2):
    dummy = ListNode()
    cur = dummy
    carry = 0
    while l1 or l2 or carry:
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0
        total = v1 + v2 + carry
        carry = total // 10
        cur.next = ListNode(total % 10)   # naya digit node
        cur = cur.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return dummy.next
```

Pattern: **dummy node + carry-propagation** elementary-math style traversal. `while l1 or l2 or carry` ek hi condition me teeno cases (unequal lengths + leftover carry) handle kar leta hai.

## Complexity

- **Time:** O(max(m, n)) — lambi list ke length tak ek pass (m, n = dono lengths).
- **Space:** O(max(m, n)) — output list itni hi lambi hoti hai (+1 if final carry).

## Common Pitfalls

- **Final carry bhoolna** — `99 + 1 = 100`, jisme ek extra leading digit hai. `while`-condition me `or carry` rakho warna last `1` chhoot jaayega.
- **Unequal lengths** — chhoti list khatam hone par uska digit `0` treat karo (`l1.val if l1 else 0`), warna `NoneType` crash.
- **Dummy node return karna** — `dummy.next` return karo, `dummy` nahi (uska val 0 placeholder hai).
- **Pointer advance karna bhoolna** — `cur = cur.next` aur `l1/l2` advance dono chahiye; ek bhi miss → infinite loop ya galat list.
- **Numbers ko int me convert karke add karne ki koshish** — bahut badi lists par overflow / spirit-of-problem violation; digit-by-digit hi karo.

## When to Use This Pattern

Jab linked list par **digit-by-digit arithmetic** ya koi bhi **carry/borrow propagating** sequential combine ho → dummy node se build karo aur ek carry variable saath le chalo. Cousins: Multiply Strings, Add Binary, Plus One (Linked List). Cue: "lists represent numbers" ya "process two sequences in lockstep with state carried forward".

## NeetCode Link

https://neetcode.io/problems/add-two-numbers
