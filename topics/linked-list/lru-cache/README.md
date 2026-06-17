# LRU Cache

**Category:** Linked List
**Difficulty:** medium

## Problem Statement

Design a data structure for a **Least Recently Used (LRU) cache** with a fixed `capacity`. Support two operations, both in **O(1)** average time:

- `get(key)` — return the value if `key` exists, else `-1`. A successful `get` marks that key as *most recently used*.
- `put(key, value)` — insert/update. If inserting exceeds `capacity`, **evict the least recently used** key first.

```
cache = LRUCache(2)
cache.put(1, 1)        # cache: {1=1}
cache.put(2, 2)        # cache: {1=1, 2=2}
cache.get(1)    -> 1   # 1 is now most-recently-used; order: 2 (LRU) ... 1 (MRU)
cache.put(3, 3)        # capacity full -> evict key 2 -> cache: {1=1, 3=3}
cache.get(2)    -> -1  # 2 was evicted
```

## Real-World Analogy

Socho ek chhoti si **study table** hai jisme sirf 2 kitaabein aa sakti hain. Jab bhi tum koi kitaab padhte ho (get) ya nayi rakhte ho (put), tum usse **table ke top pe** rakh dete ho — "abhi-abhi use ki". Jab table full ho aur nayi kitaab aaye, tum **sabse neeche padi kitaab** (jise sabse purana chhua tha) hata dete ho.

Ab do cheezein chahiye: (1) kisi bhi kitaab ko naam se turant dhoondhna — yeh kaam **hashmap** karta hai (`key -> node`). (2) "kaun sabse recent, kaun sabse purana" ka order maintain karna aur kisi bhi kitaab ko beech se nikaal ke top pe daalna — yeh kaam **doubly linked list** karti hai. Dono milke har operation O(1) bana dete hain.

## Approach

**Pattern: hashmap + doubly linked list (DLL).**

DLL me order rakho: **head ke paas MRU**, **tail ke paas LRU**. Hashmap har key ko uske DLL node se map karta hai, taaki node ko seedha O(1) me locate kar sako (warna list me dhoondhna O(n) ho jaata).

Do dummy sentinel nodes — `head` aur `tail` — rakhne se edge cases (empty list, first/last node) khatam ho jaate hain. Koi `None`-check ki zaroorat nahi.

Core moves:
- `_remove(node)` — node ko uske prev/next se unlink karo.
- `_insert_front(node)` — node ko `head` ke turant baad daalo (MRU bana do).
- `get` = remove + insert_front (touch karke recent banao).
- `put` = agar key exists to remove karke value update; phir insert_front; agar size > capacity to `tail.prev` (LRU) evict.

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}                       # key -> Node
        self.head, self.tail = Node(), Node()   # dummy sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _insert_front(self, node):          # right after head = MRU
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._insert_front(node)            # mark most-recently-used
        return node.val

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self.map[key] = node
        self._insert_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev            # node just before tail
            self._remove(lru)
            del self.map[lru.key]           # key chahiye, isliye Node me key store ki
```

> **Note:** Python me `collections.OrderedDict` (with `move_to_end` + `popitem(last=False)`) ya plain `dict` (3.7+ insertion-ordered) se yeh shortcut me ho jaata. But interview me **DLL khud banake dikhana** asli test hai — woh data-structure understanding prove karta hai.

## Complexity

- **Time:** O(1) per `get` / `put` — hashmap lookup O(1), DLL unlink/insert O(1) (pointer reassignments, koi scan nahi).
- **Space:** O(capacity) — at most `capacity` nodes in the map + list.

## Common Pitfalls

- **Node me `key` store na karna** — eviction ke time `tail.prev` node mila, but uski key kya thi? Bina key ke `del self.map[...]` nahi kar paoge. Isliye node me `key` rakhna zaroori hai.
- **Sentinels skip karna** — bina dummy head/tail ke, empty-list / single-node / head / tail wale special cases me `None` pointers handle karna padta. Sentinels yeh saara bloat hata dete hain.
- **`get` pe "touch" bhulna** — agar successful get pe node ko front pe move nahi kiya, to LRU order galat ho jaata aur galat key evict hoti hai.
- **`put` (update) pe purana node remove na karna** — same key dobara aaye to pehle purana unlink karo, warna list me duplicate / stale node reh jaayega.
- **Evict order ulta** — yaad rakho head = MRU, tail = LRU. `tail.prev` evict hota hai, `head.next` nahi.

## When to Use This Pattern

Jab bhi dikhe **"O(1) lookup AND maintain an order / recency / priority that you mutate from the middle"** → hashmap (fast find) + doubly linked list (fast reorder). Yahi combo LRU/LFU caches, browser history with quick jump, MRU lists, aur OS page-replacement me aata hai. Cue: "design a cache" ya "evict the oldest/least-used" → turant hashmap + DLL socho.

## Practice

- Visual: open `topics/linked-list/lru-cache/visual.html`

## NeetCode Link

https://neetcode.io/problems/lru-cache
