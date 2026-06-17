# Course Schedule II

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

There are `numCourses` courses labelled `0` to `numCourses - 1`, with `prerequisites` where `[a, b]` means **you must take `b` before `a`**. Return **any valid order** in which to take all courses. If it's impossible (a cycle exists), return an **empty list** `[]`.

```
numCourses = 2, prerequisites = [[1, 0]]                    ->  [0, 1]
numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]   ->  [0, 1, 2, 3]   (or [0,2,1,3])
numCourses = 2, prerequisites = [[1, 0], [0, 1]]            ->  []   (cycle)
```

Course Schedule I poochta tha "kya finish kar sakte ho?" (boolean). Yahan tumhe **actual order** chahiye — yani ek full **topological sort**.

## Real-World Analogy

Socho ek recipe me steps hain: "dough banao", "phir bake karo", "phir ice karo". Tumhe ek **aisi sequence** chahiye jisme har step se pehle uske saare prerequisites already done ho. Course Schedule II basically yahi maangta hai — ek aisi line me sab courses lagao ki koi bhi course tab hi aaye jab uske saare prereqs uske aage already aa chuke ho. Agar do steps ek doosre pe circularly depend karein (cycle), to koi valid line ban hi nahi sakti → khaali list.

## Approach

Yeh **topological sort** hai. Best fit: **Kahn's algorithm (BFS with indegree)** — kyunki yeh order naturally build karta hai aur cycle detection free me deta hai.

**Steps:**
1. Adjacency list `pre -> course` (prereq apne dependent course ko unlock karta hai) aur har course ka **indegree** banao.
2. Saare indegree-0 courses queue me daalo (jinke koi prereq nahi).
3. Queue se ek course nikaalo → use **order me append** karo. Uske har dependent ka indegree `-1` karo; jo 0 ho jaaye, queue me daalo.
4. Jab queue khali ho: agar `len(order) == numCourses` → return `order`. Warna cycle tha → return `[]`.

```python
from collections import deque

def find_order(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    indegree = [0] * num_courses
    for course, pre in prerequisites:
        graph[pre].append(course)        # pre unlocks course
        indegree[course] += 1

    q = deque(i for i in range(num_courses) if indegree[i] == 0)
    order = []
    while q:
        node = q.popleft()
        order.append(node)               # safe to take now
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)

    return order if len(order) == num_courses else []
```

> **DFS alternative:** post-order DFS karke, jab ek node ke saare descendants explore ho jaayein tab use stack pe push karo. End me stack ko **reverse** karo — wahi topo order hai. Cycle detect karne ke liye wahi 3-color trick. Kahn's BFS zyada intuitive hai is problem ke liye.

## Complexity

- **Time:** O(V + E) — har course aur prerequisite ek baar process hota hai.
- **Space:** O(V + E) — adjacency list + indegree array + queue + output.

## Common Pitfalls

1. **Cycle pe `[]` return karna bhulna** — agar `len(order) != numCourses` to partial order return mat karo, **khaali list** do.
2. **Edge direction galat** — `[a, b]` = `b` pehle. Graph me `b -> a` (`pre -> course`). Ulta kiya to order reverse aa jaayega.
3. **DFS me reverse karna bhulna** — post-order push ka result reversed topo order hota; bina reverse ke ulta jawab.
4. **`courses with no prereqs` skip ho jaana** — saare indegree-0 nodes initial queue me hone chahiye, sirf jo prerequisites me dikhe wo nahi.
5. **Multiple valid answers** — interviewer ko bata do ki ek se zyada valid order ho sakte hain; tumhara koi bhi ek valid chalega.

## When to Use This Pattern

Jab dikhe **"give an order / sequence / arrangement respecting dependencies"** → topological sort (Kahn's BFS ya DFS post-order). Difference from Course Schedule I: wahan sirf feasibility (boolean), yahan **actual ordering** chahiye. Cue: build order, task scheduling with deps, package install order, Alien Dictionary (letter order infer karna), compilation order.

## Practice

- Visual: open `topics/graphs/course-schedule-ii/visual.html`

## NeetCode Link

https://neetcode.io/problems/course-schedule-ii
