# Course Schedule

**Category:** Graphs
**Difficulty:** medium

## Problem Statement

There are `numCourses` courses labelled `0` to `numCourses - 1`. You're given `prerequisites` where `[a, b]` means **you must take course `b` before course `a`**. Return `True` if you can finish all courses, otherwise `False`.

```
numCourses = 2, prerequisites = [[1, 0]]          ->  True    # take 0, then 1
numCourses = 2, prerequisites = [[1, 0], [0, 1]]  ->  False   # 0 needs 1, 1 needs 0 — deadlock
```

In graph terms: the question is simply **"does this directed graph have a cycle?"** No cycle → you can finish all courses.

## Real-World Analogy

Socho tum subah ready ho rahe ho. "Shoes pehnne se pehle socks pehno", "socks se pehle pant pehno" — ye sab **dependencies** hain. Jab tak chain ek direction me chalti hai, koi dikkat nahi: ek valid order nikal aata hai. Lekin agar koi keh de "A se pehle B" aur saath hi "B se pehle A" — to tum **kabhi shuru hi nahi kar paoge**. Yeh circular dependency hi cycle hai. Course Schedule basically poochta hai: kya is dependency graph me koi aisa deadlock loop hai?

## Approach

Do classic tareeke hain. Dono O(V + E).

### Approach 1 — DFS with 3-color cycle detection

Har node ko ek state do: `0 = unvisited`, `1 = visiting (current DFS path pe)`, `2 = done`. Agar DFS ke dauraan tum kisi node tak pahunche jo abhi `visiting` (state 1) hai → us node ko hum already current path pe explore kar rahe the → **back-edge → cycle**.

```python
def can_finish(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    for course, pre in prerequisites:
        graph[course].append(pre)        # course depends on pre

    state = [0] * num_courses            # 0=unvisited, 1=visiting, 2=done

    def dfs(node):
        if state[node] == 1:             # node on current path -> cycle!
            return False
        if state[node] == 2:             # already cleared
            return True
        state[node] = 1                  # mark on-path
        for nxt in graph[node]:
            if not dfs(nxt):
                return False
        state[node] = 2                  # fully explored, safe
        return True

    return all(dfs(i) for i in range(num_courses))
```

### Approach 2 — BFS / Kahn's topological sort (indegree)

Har node ka **indegree** (kitne prereqs uspe point karte) count karo. Saare indegree-0 nodes (jo abhi available hain) queue me daalo. Ek-ek nikaalo, "complete" maano, unke dependents ka indegree `-1` karo; jab koi 0 ho jaaye to queue me daalo. Agar end me **saare courses process ho gaye** → no cycle. Agar kuch reh gaye (unka indegree kabhi 0 nahi hua) → cycle.

```python
from collections import deque

def can_finish(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    indegree = [0] * num_courses
    for course, pre in prerequisites:
        graph[pre].append(course)        # edge pre -> course
        indegree[course] += 1

    q = deque(i for i in range(num_courses) if indegree[i] == 0)
    taken = 0
    while q:
        node = q.popleft()
        taken += 1
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)

    return taken == num_courses          # all taken => no cycle
```

> **Edge direction me confuse mat hona.** DFS version me main `course -> pre` rakhta hoon (depends-on). Kahn version me `pre -> course` rakhta hoon (unlocks). Dono valid, bas consistent raho.

## Complexity

- **Time:** O(V + E) — V = numCourses, E = prerequisites. Har node aur edge ek baar process.
- **Space:** O(V + E) — adjacency list + state/indegree + recursion stack ya queue.

## Common Pitfalls

1. **2-color (sirf visited/unvisited) se cycle detect karna** → galat. Tumhe **3 states** chahiye — "currently on path" alag se track karo, warna ek already-finished node ko cycle samajh loge (false positive).
2. **Edge direction galat** — `[a, b]` ka matlab `b` pehle, `a` baad me. DFS me `a -> b`, Kahn me `b -> a`. Mix mat karo.
3. **Disconnected components** — saare nodes pe DFS shuru karna (`all(dfs(i) ...)`), warna kuch courses kabhi visit hi nahi honge.
4. **Recursion depth** — bade graphs pe DFS stack overflow ho sakta; Kahn's BFS iterative hai, safer.
5. **`taken == num_courses` check bhulna** Kahn me — yahi cycle ka signal hai (leftover nodes never hit indegree 0).

## When to Use This Pattern

Jab dikhe **"dependencies / ordering / 'X before Y' / can this be scheduled?"** → directed graph + cycle detection ya topological sort socho. Cue words: prerequisites, build order, task scheduling, "is a valid order possible". Cycle hai → impossible. Cousins: Course Schedule II (actual order), Alien Dictionary, build systems (make), package managers.

## Practice

- Visual: open `topics/graphs/course-schedule/visual.html`

## NeetCode Link

https://neetcode.io/problems/course-schedule
