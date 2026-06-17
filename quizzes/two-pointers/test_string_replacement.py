"""
String Replacement — Coding Challenge (LinkedIn CA1)

Implement `replace(orig, find, repl)` below.
- Return `orig` with every NON-OVERLAPPING occurrence of `find` replaced by `repl`.
- Do NOT use str.replace, regex, or any built-in find/replace helper.
- Decide on edge cases deliberately (see tests): empty `find` should raise
  ValueError; `repl` may itself contain `find` (must not re-scan inserted text);
  matches are non-overlapping (advance past the whole match).

Target: O(n*m) time with a list/StringBuilder result buffer (O(n) space).
        (n = len(orig), m = len(find)). KMP gets you O(n+m) as a follow-up.

Run: dsa-buddy quiz check string-replacement
  or: pytest quizzes/two-pointers/test_string_replacement.py
"""

def matches_at(orig: str, find: str, i: int) -> bool:
    if i + len(find) > len(orig):
        return False
    for j in range(len(find)):
        if orig[i + j] != find[j]:
            return False
    return True

def replace(orig: str, find: str, repl: str) -> str:
    # TODO: implement. No str.replace / no regex.
    if find == "":
        raise ValueError(f"string to match {find} is empty")
    if find == repl:
        return orig
    
    result = []
    i=0
    while i < len(orig):
        # if i + len(find) > len(orig):
        #     # no match here
        
        # for j in range(len(find)):
        #     if orig[i+j] != find[j]:
        #         # no match
        #     # match, here we should repalce

        if matches_at(orig, find, i):
            # match
            result.append(repl)
            i += len(find)
        else:
            result.append(orig[i])
            i += 1
    
    return "".join(result)
        


# ---------- Tests (don't modify) ----------

import pytest


@pytest.mark.parametrize(
    "orig, find, repl, expected",
    [
        # Canonical example from the question bank
        ("AFoxRunsInTheField", "Fox", "Cat", "ACatRunsInTheField"),
        # Multiple, non-adjacent occurrences
        ("a-b-c", "-", "_", "a_b_c"),
        # Multiple adjacent occurrences
        ("aaa", "a", "b", "bbb"),
        # find longer than 1, several hits
        ("xxabxxab", "ab", "Z", "xxZxxZ"),
        # No occurrence -> unchanged
        ("hello world", "xyz", "Q", "hello world"),
        # find == repl -> unchanged
        ("abcabc", "abc", "abc", "abcabc"),
        # repl shorter than find
        ("oneTWOthree", "TWO", "2", "one2three"),
        # repl longer than find
        ("a.b", ".", "DOT", "aDOTb"),
        # NON-overlapping semantics: "aa" in "aaaa" -> 2 matches, not 3
        ("aaaa", "aa", "X", "XX"),
        # Odd-length leftover after non-overlapping matches
        ("aaaaa", "aa", "X", "XXa"),
        # repl CONTAINS find -> must not re-scan the inserted text (no infinite/expand)
        ("cat", "a", "aa", "caat"),
        # find at the very start and very end
        ("abXYab", "ab", "_", "_XY_"),
        # whole string is the match
        ("match", "match", "done", "done"),
        # case sensitive by default
        ("Apple apple", "apple", "ORANGE", "Apple ORANGE"),
        # empty orig -> empty
        ("", "a", "b", ""),
        # find not present, single char orig
        ("z", "a", "b", "z"),
    ],
)
def test_replace(orig, find, repl, expected):
    assert replace(orig, find, repl) == expected


def test_empty_find_raises():
    with pytest.raises(ValueError):
        replace("anything", "", "x")


def test_no_builtin_replace_used():
    """Lightweight guard: the source of `replace` must not call str.replace/re."""
    import inspect

    src = inspect.getsource(replace)
    lowered = src.lower()
    assert ".replace(" not in lowered, "Do not use the built-in str.replace"
    assert "import re" not in lowered and "re.sub" not in lowered, "Do not use regex"
