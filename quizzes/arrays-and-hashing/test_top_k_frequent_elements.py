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
from collections import Counter

def topKFrequent(nums: list[int], k: int) -> list[int]:
    # TODO: implement (Counter + bucket sort by frequency).
    counter = Counter(nums)

    # we want a bucket of len(nums) + 1 to use the index as the occurrence counter
    frequency = [[] for i in range(len(nums) +1)]
    
    for no, freq in counter.items():
        frequency[freq].append(no)

    result = []
    for i in range(len(frequency) -1, 0, -1):
        for num in frequency[i]:
            result.append(num)
            if len(result) == k:
                return result
        

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


def test_two_element_array():
    # Smallest non-trivial case: distinct counts, k pulls the more frequent one.
    result = topKFrequent([5, 5, 9], 1)
    assert set(result) == {5}


def test_large_input_stays_linear():
    # 100k elements: a correct O(n) bucket-sort solution returns instantly.
    # An accidental O(n^2) approach (nested scans) would crawl here.
    nums = [i % 1000 for i in range(100_000)] + [42] * 50_000
    result = topKFrequent(nums, 1)
    assert set(result) == {42}


def test_approach_avoids_full_sort():
    # Soft nudge: the intended solution is Counter + bucket sort (O(n)),
    # not a full comparison sort. Discourage sorted()/.sort() on the data.
    import inspect

    src = inspect.getsource(topKFrequent)
    body = "\n".join(
        line for line in src.splitlines() if not line.strip().startswith("#")
    )
    assert "sorted(" not in body and ".sort(" not in body, (
        "Try the O(n) bucket-sort approach instead of a full sort — "
        "bucket numbers by their frequency and scan high to low."
    )
