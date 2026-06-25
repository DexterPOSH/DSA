# Design Twitter

**Category:** Heap / Priority Queue
**Difficulty:** medium

## Problem Statement

Design a simplified Twitter. Support these operations:

- `postTweet(userId, tweetId)` — user posts a tweet.
- `getNewsFeed(userId)` — return the **10 most recent** tweet IDs in the user's feed: tweets by the user **and by everyone they follow**, newest first.
- `follow(followerId, followeeId)` — follower follows followee.
- `unfollow(followerId, followeeId)` — follower stops following followee.

```
postTweet(1, 5)
getNewsFeed(1)        -> [5]
follow(1, 2)
postTweet(2, 6)
getNewsFeed(1)        -> [6, 5]      # merged, newest first
unfollow(1, 2)
getNewsFeed(1)        -> [5]
```

## Real-World Analogy

**What Azure Event Hubs is:** Azure Event Hubs is Azure's high-throughput event-ingestion service for telemetry, app logs, clickstreams, and other time-ordered data. Producers append events into a hub, Azure durably buffers them, and consumer apps read those events back from streams. It is built for many independent producers and consumers moving through recent data without scanning one giant combined list.

**What a partitioned ordered stream is, and why it's used:** Event Hubs splits an event hub into **partitions**, and each partition is an ordered append-only log with offsets/sequence numbers. Ordering is guaranteed within a partition, not globally across every partition, because partitioning lets Azure scale ingestion and parallel consumers without forcing every event through one bottleneck. A consumer that needs a combined "latest first" view must merge the heads of several already-ordered streams.

**The mapping:** Treat each followed user's tweet list like one Azure Event Hubs partition: it is already ordered by timestamp, with the newest tweet at that stream's head. `getNewsFeed` seeds a max-heap with one current tweet from each relevant source, pops the newest overall, then advances only that same source and pushes its next tweet. The key insight is that you never sort all tweets; just like merging ordered Azure partitions, one live head per stream plus a heap is enough to produce the top 10 newest items.

## Approach

Data layout:
- `tweets[userId]` → list of `(timestamp, tweetId)`, append-only (newest at the end).
- `following[userId]` → set of followee IDs.
- A global monotonic `time` counter so newer tweets compare as "bigger".

`getNewsFeed` = **k-way merge of sorted lists, take top 10** → use a **max-heap keyed by timestamp**.

```python
import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self.time = 0
        self.tweets = defaultdict(list)        # user -> [(time, tweetId)]
        self.following = defaultdict(set)

    def postTweet(self, userId, tweetId):
        self.time += 1
        self.tweets[userId].append((self.time, tweetId))

    def getNewsFeed(self, userId):
        heap = []                              # max-heap via negative time
        sources = self.following[userId] | {userId}
        for uid in sources:
            tw = self.tweets[uid]
            if tw:
                idx = len(tw) - 1              # newest tweet of this user
                t, tid = tw[idx]
                heapq.heappush(heap, (-t, tid, uid, idx))
        feed = []
        while heap and len(feed) < 10:
            t, tid, uid, idx = heapq.heappop(heap)
            feed.append(tid)
            if idx > 0:                        # pull this user's next-newest
                idx -= 1
                nt, ntid = self.tweets[uid][idx]
                heapq.heappush(heap, (-nt, ntid, uid, idx))
        return feed

    def follow(self, followerId, followeeId):
        if followerId != followeeId:
            self.following[followerId].add(followeeId)

    def unfollow(self, followerId, followeeId):
        self.following[followerId].discard(followeeId)
```

Heap me kabhi bhi sirf **har relevant user ka ek "current pointer" tweet** hota hai — isliye heap size ≤ number of followees, na ki total tweets. Top pop karo, feed me daalo, aur **usi user ka agla purana tweet** push karo. Greedy k-way merge.

## Complexity

Let `f` = number of users you follow (incl. yourself), `F` = total tweets across them.

- **getNewsFeed Time:** O(f) to seed the heap + O(10 · log f) for the merge → effectively **O(f log f)** worst case. Sirf top-10 chahiye, isliye poori `F` tweets touch nahi hoti.
- **postTweet / follow / unfollow:** O(1).
- **Space:** O(total tweets + follow edges); heap is O(f) transient.

## Common Pitfalls

- **Global timestamp bhulna** — agar har user ka apna local counter ho to do users ke tweets ka relative order galat compare hoga. Ek hi monotonic `time` chahiye.
- **Max-heap direction** — Python min-heap hai; newest-first ke liye `-time` push karo, warna sabse purana tweet pehle aayega.
- **Sirf top tweet daal kar ruk jaana** — har user ka *poora* feed contribute karna hai, sirf latest nahi. Pop ke baad **usi source ka agla tweet** push karna mandatory hai.
- **Khud ke tweets miss karna** — feed me followees + **खुद** dono shamil hain (`sources = following | {userId}`).
- **`follow(x, x)` ya self-follow** — guard kar do; aur `unfollow` me `.discard` (not `.remove`) use karo taaki absent followee pe crash na ho.
- **Tie-break on equal time** — practically same global time do tweets pe nahi aata, par heap tuple me extra fields (`tid`, `uid`) rakhna comparison ko safe banata.

## When to Use This Pattern

Jab dikhe **"merge multiple already-sorted streams and pull the top-k"** → **heap-based k-way merge**. Cousins: merge k sorted lists, find k smallest in a sorted matrix, external sort. Cue: bahut saari sorted sources + "sirf top kuch chahiye" → heap me har source ka ek head rakho.

## NeetCode Link

https://neetcode.io/problems/design-twitter-feed
