"""
Valid Anagram — Coding Challenge

Implement `valid_anagram(s, t)` below.
- Input: two strings `s` and `t`
- Output: True if `t` is an anagram of `s`, else False

Target: O(n) time, O(1) extra space (for lowercase English letters).
Avoid using `sorted()` — use a frequency-counting approach.

Run: dsa-buddy quiz check valid-anagram
"""
from collections import defaultdict
import pytest

def valid_anagram(s: str, t: str) -> bool:
    # if lengths are different they are not anagram
    if len(s) != len(t):
        return False
    
    dictionary = defaultdict(int)

    for c in s:
        dictionary[c] += 1
    
    for c in t:
        dictionary[c] -= 1
        if dictionary[c] < 0:
            # at any point the value goes negative, then it is a mismatch
            return False
    return True


# ---------- Tests (don't modify) ----------




@pytest.mark.parametrize(
    "s, t, expected",
    [
        # Basic positive cases
        ("anagram", "nagaram", True),
        ("listen", "silent", True),
        ("aabb", "bbaa", True),
        ("aabb", "abab", True),
        # Basic negative cases
        ("rat", "car", False),
        ("hello", "world", False),
        # Length mismatch
        ("a", "ab", False),
        ("abc", "ab", False),
        ("", "a", False),
        # Empty strings
        ("", "", True),
        # Single character
        ("a", "a", True),
        ("a", "b", False),
        # Same letters, different counts
        ("aabbcc", "abbbcc", False),
        ("aaa", "aa", False),
        # Longer strings
        ("abcdefghij", "jihgfedcba", True),
        ("abcdefghij", "jihgfedcbb", False),
        # Repeated characters
        ("aaaa", "aaaa", True),
        ("aaab", "abaa", True),
        ("aaab", "abbb", False),
    ],
)
def test_valid_anagram(s, t, expected):
    assert valid_anagram(s, t) == expected, (
        f"valid_anagram({s!r}, {t!r}) expected {expected}"
    )


def test_does_not_use_sorted():
    """Soft check — encourages frequency-map approach over sorted()."""
    import inspect

    source = inspect.getsource(valid_anagram)
    assert "sorted(" not in source, (
        "Try the frequency-map approach instead of sorted() for O(n) time"
    )
