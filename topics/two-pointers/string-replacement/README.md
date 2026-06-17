# String Replacement

**Category:** Strings / Two-Pointer scan
**Source:** LinkedIn CA1 question bank (go/ca1) — levels: jr, mid, sr
**Difficulty:** easy-to-write, edge-case heavy

## Problem Statement

Implement a function `replace(orig, find, repl)` that returns `orig` with **all
non-overlapping occurrences** of the substring `find` replaced by `repl`.

> Restriction: do **not** use `str.replace`, regex, or any built-in find/replace.
> You may use indexing and a result buffer.

```
replace("AFoxRunsInTheField", "Fox", "Cat")  ->  "ACatRunsInTheField"
```

**Interviewer tip (from the bank):** many edge cases hide here. A good candidate
finishes in ~30 min and the final solution runs in **linear time** (or explains
why a sub-linear search like KMP works rather than reciting it from memory).

## Real-World Analogy

Socho ek proofreader ek manuscript padh raha hai aur usse har jagah "Fox" word
ko "Cat" se badalna hai. Wo left-se-right ek hi baar poora page scan karta hai.
Jab "F" dikhta hai to wo agle few letters peek karta hai — kya yeh poora "Fox"
banta hai? Agar haan, to "Cat" likh deta hai apni clean copy me aur original me
"Fox" ke aage jump kar jaata hai. Agar nahi (sirf "F" tha but aage "Fox" nahi
bana), to wo wahi original letter clean copy me likh deta hai aur ek step aage
badh jaata hai. Ek hi pass, koi dobara-padhai nahi (ideally).

## Approach (clean O(n·m) scan — the safe interview answer)

Pointer `i` ko `orig` pe chalao. Har position pe check karo ki kya
`orig[i : i+len(find)]` exactly `find` ke equal hai:

1. **Match mila** → result me `repl` append karo, aur `i` ko `len(find)` aage
   badha do (non-overlapping, isliye poore match ke aage jump).
2. **Match nahi mila** → result me `orig[i]` append karo, `i += 1`.
3. End tak yahi repeat. Last me result join karke return.

```python
def replace(orig, find, repl):
    if find == "":                  # edge: empty needle is undefined -> raise
        raise ValueError("find must be non-empty")
    if find == repl:                # micro-opt: nothing changes
        return orig
    res, i, n, m = [], 0, len(orig), len(find)
    while i < n:
        if i + m <= n and orig[i:i+m] == find:   # manual window compare
            res.append(repl)
            i += m                  # jump past the match (non-overlapping)
        else:
            res.append(orig[i])
            i += 1
    return "".join(res)
```

> **Why a list buffer, not `res += char`?** Python strings are immutable —
> repeated `+=` is O(n²) (har baar poora string copy hota hai). List append +
> final `"".join` is O(n). Java me yahi reason `StringBuilder` use karne ka hai.

## Complexity

- **Time:** O(n·m) worst case — har position pe up to `m` chars compare.
  (n = len(orig), m = len(find)). For small/fixed `find` this is effectively
  linear in `n`.
- **Space:** O(n) for the result buffer.
- **True linear O(n+m):** KMP — precompute the failure function so on a partial
  mismatch you don't re-scan from scratch. Mention it as a follow-up; the
  interviewer explicitly does *not* want it recited from memory.

## Common Pitfalls (yeh interview me points dilate hain)

1. **Empty `find`** → infinite loop / undefined. Decide and state: raise an error.
2. **`find == repl`** → harmless but a nice early return.
3. **Overlapping matches** → e.g. `find="aa"`, `orig="aaaa"`. Non-overlapping
   means result is `repl+repl` (2 matches), not 3. Jumping by `len(find)` handles
   this correctly; advancing by 1 would double-count.
4. **`repl` contains `find`** → e.g. replace "a" with "aa". Must NOT re-scan the
   inserted text, warna infinite growth. Writing to a *separate* result buffer
   (not mutating `orig`) avoids this automatically.
5. **Immutable-string O(n²) trap** → use a buffer/StringBuilder.
6. **null / empty `orig`** → return as-is (or "").
7. **Case sensitivity** → ask the interviewer; default is case-sensitive.

## When to Use This Pattern

Substring scan-and-build shows up in: templating engines, tokenizers,
sanitizers, find/replace in editors. Pattern cue: "transform a string by
locating a sub-pattern and emitting something else" → single left-to-right pass
with an output buffer, jump pointer past consumed input.

## Practice

- Solve file: `quizzes/two-pointers/test_string_replacement.py`
- Run: `dsa-buddy quiz check string-replacement` (or `pytest` that file)
- Visual: open `topics/two-pointers/string-replacement/visual.html`
