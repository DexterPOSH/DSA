"""
Group Anagrams — Coding Challenge

Implement `group_anagrams(strs)` below.
- Input: list of strings `strs`
- Output: list of lists, where each inner list contains strings that are anagrams of each other

Constraints:
- Group order doesn't matter
- Order within a group doesn't matter
- Strings contain only lowercase English letters

Target: O(n * k) time using a hash map with canonical key
        (n = number of strings, k = max string length).

Run: dsa-buddy quiz check group-anagrams
"""
from collections import defaultdict


def group_anagrams(strs: list[str]) -> list[list[str]]:
    # iterate on the list of words
    groups = defaultdict(list)
    for word in strs: # O(n * k log k)
        key = "".join(sorted(word)) # O(K log k)
        groups[key].append(word)
    return list(groups.values())


# ---------- Tests (don't modify) ----------

import pytest


def _normalize(groups):
    """Sort each group and the list of groups so order doesn't affect comparison."""
    return sorted(sorted(g) for g in groups)


@pytest.mark.parametrize(
    "strs, expected",
    [
        # Classic example
        (
            ["eat", "tea", "tan", "ate", "nat", "bat"],
            [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]],
        ),
        # All anagrams
        (
            ["abc", "bca", "cab", "bac"],
            [["abc", "bca", "cab", "bac"]],
        ),
        # No anagrams
        (
            ["abc", "def", "ghi"],
            [["abc"], ["def"], ["ghi"]],
        ),
        # Single string
        (
            ["hello"],
            [["hello"]],
        ),
        # Empty input
        (
            [],
            [],
        ),
        # Empty string
        (
            [""],
            [[""]],
        ),
        # Multiple empty strings (all anagrams of each other)
        (
            ["", "", ""],
            [["", "", ""]],
        ),
        # Mixed: empty + non-empty
        (
            ["", "a", ""],
            [["", ""], ["a"]],
        ),
        # Single character anagrams
        (
            ["a", "a", "b", "a", "c", "b"],
            [["a", "a", "a"], ["b", "b"], ["c"]],
        ),
        # Repeated full strings
        (
            ["abc", "abc", "cba"],
            [["abc", "abc", "cba"]],
        ),
        # Different lengths — same letters but different counts not anagrams
        (
            ["aab", "aabb", "abb"],
            [["aab"], ["aabb"], ["abb"]],
        ),
        # Long strings
        (
            ["abcdefghij", "jihgfedcba", "aabbccddee", "eeddccbbaa"],
            [["abcdefghij", "jihgfedcba"], ["aabbccddee", "eeddccbbaa"]],
        ),
        # Words with repeated letters
        (
            ["aaa", "aaa", "aab", "baa", "aba"],
            [["aaa", "aaa"], ["aab", "baa", "aba"]],
        ),
    ],
)
def test_group_anagrams(strs, expected):
    result = group_anagrams(strs)
    assert result is not None, "group_anagrams returned None — implement the function"
    assert isinstance(result, list), f"Expected list of lists, got {type(result).__name__}"
    for group in result:
        assert isinstance(group, list), f"Each group should be a list, got {type(group).__name__}"
    assert _normalize(result) == _normalize(expected), (
        f"Expected groups {_normalize(expected)}, got {_normalize(result)}"
    )


def test_returns_all_inputs():
    """Every input string must appear exactly once in the output."""
    strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
    result = group_anagrams(strs)
    flattened = [w for group in result for w in group]
    assert sorted(flattened) == sorted(strs), (
        f"Output must contain every input exactly once. Input: {sorted(strs)}, got: {sorted(flattened)}"
    )
