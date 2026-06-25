# Burst Balloons

**Category:** 2-D Dynamic Programming (Interval DP)
**Difficulty:** hard

## Problem Statement

You have `n` balloons in a row, each painted with a number `nums[i]`. If you
**burst** balloon `i`, you get `nums[left] * nums[i] * nums[right]` coins, where
`left` and `right` are the balloons **adjacent to `i` at that moment** (already-burst
balloons are skipped). After bursting, the row closes up. Balloons just outside the
array boundary are treated as `1`.

Return the **maximum coins** you can collect by bursting all balloons.

```
nums = [3, 1, 5, 8]   ->  167
# burst 1: 3*1*5 = 15   -> [3,5,8]
# burst 5: 3*5*8 = 120  -> [3,8]
# burst 3: 1*3*8 = 24   -> [8]
# burst 8: 1*8*1 = 8    -> []
# total = 15 + 120 + 24 + 8 = 167
```

## Real-World Analogy

**What Azure Virtual WAN is:** Azure Virtual WAN is Microsoft's managed wide-area networking service for connecting branches, VNets, users, and security services through Azure hubs. It gives you centrally managed routing across a large network instead of hand-building every connection. In this analogy, traffic moves through a chain of network appliances between two fixed hub gateways.

**What service chaining with Network Virtual Appliances is, and why it's used:** A service chain sends traffic through required Network Virtual Appliances, such as firewalls or inspection devices, before it reaches the other side. Azure networking teams use this pattern to apply security, filtering, or traffic controls in a predictable order. The tricky part is that if you remove an appliance from the middle, its neighbors change, so evaluating the "first" removal makes every later decision depend on a moving boundary.

**The mapping:** The fixed left and right gateways are the sentinel balloons, each appliance is a balloon, and choosing appliance `k` as the last one removed inside an interval gives stable neighbors: the left and right boundaries. That lets the value for `k` combine cleanly with the best already-computed left subchain and right subchain, just like `nums[left] * nums[k] * nums[right] + dp[left][k] + dp[k][right]`. The key insight is to reason about the last action in a segment, because fixed boundaries turn a tangled chain into two independent cached intervals.

## Approach

Pattern: **Interval DP** — `dp[l][r]` = `(l, r)` ke beech ke saare balloons ko
(exclusive of l and r boundaries) phodne se max coins.

**Setup:** `nums` ke aage-peeche ek `1` pad karo → `arr = [1] + nums + [1]`. Ab
boundaries built-in hain.

**Transition:** har interval `(l, r)` ke liye, har candidate `k` (jo `l` aur `r` ke
beech me ho) ko *last burst* maano:

```
dp[l][r] = max over k in (l, r) of:
    arr[l] * arr[k] * arr[r]   # k last phoota -> padosi l aur r
    + dp[l][k]                  # left sub-interval pehle
    + dp[k][r]                  # right sub-interval pehle
```

Length-by-length (chhote intervals pehle) bharo, taaki `dp[l][k]` aur `dp[k][r]`
ready hon jab `dp[l][r]` compute ho.

```python
def max_coins(nums):
    arr = [1] + nums + [1]
    n = len(arr)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):           # gap between l and r
        for l in range(n - length):
            r = l + length
            for k in range(l + 1, r):    # k = last balloon burst in (l, r)
                coins = arr[l] * arr[k] * arr[r] + dp[l][k] + dp[k][r]
                dp[l][r] = max(dp[l][r], coins)
    return dp[0][n - 1]
```

## Complexity

- **Time:** O(n³) — O(n²) intervals, har ek pe O(n) choices for `k`.
- **Space:** O(n²) for the `dp` table.

## Common Pitfalls

- **"Pehle kaunsa phodun" socha** — yeh approach fail karti hai kyunki padosi
  badalte hain. Hamesha **"is interval ka last balloon"** socho — tabhi padosi
  fixed (l aur r) rehte hain.
- **Boundary `1`s pad karna bhul jaana** — bina padding ke edge balloons ke
  multiply terms galat ho jaate hain.
- **`dp[l][k]` vs `dp[k][r]` ka matlab** — yeh *exclusive* intervals hain; `k` un me
  count nahi hota, kyunki `k` last phoota.
- **Fill order galat** — agar length-by-length nahi bharoge, to sub-intervals ready
  nahi honge aur garbage padhoge.
- **`(l, r)` open interval samajhna** — l aur r khud kabhi burst nahi hote is
  recurrence me; woh sirf walls hain.

## When to Use This Pattern

Jab answer kisi range pe depend kare aur tum range ko ek *split/last point* `k` pe
do sub-ranges me todh sako → **interval DP** (`dp[l][r]`, length-by-length).
Cousins: Matrix Chain Multiplication, Minimum Cost to Cut a Stick, Stone Game,
Optimal BST, Palindrome partitioning. Cue: "burst/merge/cut in some order to
optimize, and order matters" → reverse it: "what is the *last* operation in this
interval?"

## Practice

- Visual: open `topics/2d-dynamic-programming/burst-balloons/visual.html`

## NeetCode Link

https://neetcode.io/problems/burst-balloons
