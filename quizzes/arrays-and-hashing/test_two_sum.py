"""
Two Sum — Coding Challenge

Implement `two_sum(nums, target)` below.
- Input: list of ints `nums`, int `target`
- Output: list of two indices [i, j] such that nums[i] + nums[j] == target

Constraints:
- Exactly one valid answer exists
- Cannot use the same element twice (i != j)
- Return indices in any order

Target: O(n) time using a hash map. Avoid the O(n²) nested loop approach.

Run: dsa-buddy quiz check two-sum
"""


def two_sum(nums: list[int], target: int) -> list[int]:
    # brute force below
    # for i in range(len(nums)):
    #     for j in range(i+1, len(nums)):
    #         sum = nums[i] + nums[j]
    #         if sum == target:
    #             return [i, j]

    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [i, seen[complement]]
        # add the num and it's index to the hashmap
        seen[num] = i

# ---------- Tests (don't modify) ----------

import pytest


@pytest.mark.parametrize(
    "nums, target, expected_set",
    [
        # Basic cases
        ([2, 7, 11, 15], 9,   {0, 1}),
        ([3, 2, 4],      6,   {1, 2}),
        ([3, 3],         6,   {0, 1}),
        # Negative numbers
        ([-1, -2, -3, -4, -5], -8, {2, 4}),
        ([0, 4, 3, 0],          0, {0, 3}),
        # Target at end
        ([1, 2, 3, 4, 5],       9, {3, 4}),
        # Large gap between pair — only valid pair: 7+2=9
        ([1, 5, 3, 7, 2],       9, {3, 4}),
        # Pair at start
        ([4, 3, 9, 1],          7, {0, 1}),
        # Two elements only
        ([1, 9],               10, {0, 1}),
        # Zeroes
        ([0, 0],                0, {0, 1}),
        # Negative + positive
        ([-3, 4, 3, 90],        0, {0, 2}),
        # Duplicates — correct pair is not index 0
        ([1, 3, 3, 5],          6, {1, 2}),
    ],
)
def test_two_sum(nums, target, expected_set):
    result = two_sum(nums, target)
    assert result is not None, "two_sum returned None — implement the function"
    assert len(result) == 2, f"Expected 2 indices, got {len(result)}"
    i, j = result
    assert i != j, f"Indices must be different, got i={i} j={j}"
    assert nums[i] + nums[j] == target, (
        f"nums[{i}] + nums[{j}] = {nums[i]} + {nums[j]} != {target}"
    )
    assert set(result) == expected_set, (
        f"Expected indices {expected_set}, got {set(result)}"
    )


def test_does_not_use_nested_loop():
    """Soft check — nudges toward hash map over brute force. Ignores commented lines."""
    import inspect
    source = inspect.getsource(two_sum)
    active_lines = [l for l in source.splitlines() if not l.lstrip().startswith("#")]
    active_source = "\n".join(active_lines)
    assert active_source.count("for ") <= 1, (
        "Looks like a nested loop — try the hash map approach for O(n) time"
    )
