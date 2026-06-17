"""
Array Equal Partition — Coding Challenge (LinkedIn CA1 / LeetCode 698)

Implement `can_partition_k_subsets(nums, k)` below.
- Return True if `nums` can be split into k non-empty subsets with EQUAL sums.
- Classic backtracking. Expected approach: bucket-filling with pruning.

Feasibility shortcuts to handle:
- k <= 0  -> False
- sum(nums) % k != 0 -> False
- any single element > target(= sum//k) -> False
- (sort descending + empty-bucket prune to avoid TLE)

Target: backtracking ~O(k * 2^n) with pruning; O(k + n) space.
Note: tests use NON-NEGATIVE integers (matches LeetCode 698 constraints).

Run: pytest quizzes/backtracking/test_array_equal_partition.py
"""


def can_partition_k_subsets(nums: list[int], k: int) -> bool:
    # TODO: implement with backtracking (bucket-filling + pruning).
    pass


# ---------- Tests (don't modify) ----------

import pytest


@pytest.mark.parametrize(
    "nums, k, expected",
    [
        # LinkedIn question-bank examples
        ([4, 3, 2, 3, 5, 2, 1], 4, True),     # (5)(1,4)(2,3)(2,3)
        ([3, 1, 1, 2, 4, 4], 3, True),        # (3,2)(1,4)(1,4), each = 5
        ([3, 3, 3, 3, 4], 4, False),          # can't make 4 equal sums
        # LeetCode 698 example
        ([1, 2, 3, 4], 3, False),             # sum 10 not divisible by 3
        # Even splits
        ([1, 1, 1, 1], 4, True),              # each subset = 1
        ([1, 1, 1, 1], 2, True),              # (1,1)(1,1)
        ([2, 2, 2, 2], 2, True),              # (2,2)(2,2)
        ([1, 1, 1, 1, 2, 2, 2, 2], 4, True),  # target 3: (1,2) x4
        ([5, 5], 2, True),                    # (5)(5)
        # k == 1 -> whole array is the single subset
        ([2, 4, 6, 8], 1, True),
        # Indivisible sum
        ([1, 2, 3, 4, 5, 6], 2, False),       # sum 21 is odd
        # k larger than feasible / single element
        ([4], 1, True),
        ([4], 2, False),                      # k > len(nums)
        # All equal, k == len
        ([7, 7, 7], 3, True),
        # Needs real backtracking (greedy-by-largest still must search)
        ([2, 2, 2, 2, 3, 4, 5], 4, False),    # sum 20 target 5: no valid split
        # Invalid k
        ([1, 2, 3], 0, False),
    ],
)
def test_can_partition_k_subsets(nums, k, expected):
    # pass a copy so an in-place sort in the solution can't leak across cases
    assert can_partition_k_subsets(list(nums), k) is expected
