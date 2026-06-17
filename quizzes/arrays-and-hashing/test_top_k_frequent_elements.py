"""
Top K Frequent Elements — Coding Challenge (NeetCode / LeetCode 347)

Implement `topKFrequent(nums, k)` below.
- Return the `k` most frequent elements (any order).
- It's guaranteed the answer is unique for the given k.

Target: O(n) time using a frequency Counter + bucket sort by frequency
        (buckets indexed 0..n, since an element can appear at most n times).
        Avoid the easy O(n log n) full sort if you can.

Run: dsa-buddy quiz check top-k-frequent-elements
  or: pytest quizzes/arrays-and-hashing/test_top_k_frequent_elements.py
"""


def topKFrequent(nums: list[int], k: int) -> list[int]:
    # TODO: implement (Counter + bucket sort by frequency).
    pass


# ---------- Tests (don't modify) ----------

import pytest


@pytest.mark.parametrize(
    "nums, k, expected_set",
    [
        # Classic example
        ([1, 1, 1, 2, 2, 3], 2, {1, 2}),
        # Single element
        ([1], 1, {1}),
        # Tie at the top, clear boundary below
        ([1, 2, 1, 2, 1, 3, 3, 3], 2, {1, 3}),   # 1->3, 3->3, 2->2
        # Negatives present
        ([4, 1, -1, 2, -1, 2, 3], 2, {-1, 2}),   # -1->2, 2->2, rest->1
        # All same
        ([7, 7, 7, 7], 1, {7}),
        # k == number of distinct elements -> everything
        ([1, 2, 3, 4, 5], 5, {1, 2, 3, 4, 5}),
        # One clear winner
        ([10, 10, 20, 20, 20, 30], 1, {20}),
    ],
)
def test_top_k_frequent(nums, k, expected_set):
    result = topKFrequent(list(nums), k)
    assert len(result) == k, f"expected {k} elements, got {len(result)}"
    assert len(set(result)) == k, "elements must be distinct"
    assert set(result) == expected_set
