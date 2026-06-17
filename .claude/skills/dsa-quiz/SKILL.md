---
name: dsa-quiz
description: Take a DSA quiz — either conversational (agent asks questions) or pytest (coding challenge). Invoke with "quiz me", "dsa quiz", or "test me on <topic>".
---

You are quizzing the user on DSA concepts. Two modes available.

## Mode Selection

If the user says "quiz me" or "conceptual quiz" → conversational mode.
If the user says "code challenge", "coding quiz", or "pytest" → pytest mode.
If unclear, ask: "Conceptual quiz (I ask questions) or coding challenge (you implement a solution)?"

## Conversational Mode

1. Get the current topic from `dsa-buddy plan next` (or use the topic the user specified).
2. Check if `quizzes/<category>/conceptual_quiz_<problem>.md` exists by looking in the quizzes directory.
3. If not, spawn the `quiz-builder` subagent to create it.
4. Read the quiz file. Ask questions ONE AT A TIME.
5. Do NOT reveal the answer before the user responds.
6. After each answer:
   - If correct: "Correct!" + brief reinforcement.
   - If wrong: "Not quite — the answer is X because..." + clear explanation.
7. After all questions, report the score (e.g., "4/5 — solid!").
8. Run: `dsa-buddy progress update <problem> --quiz-score <score>/<total>`

## Pytest Mode

1. Get the current topic from `dsa-buddy plan next` (or use the topic the user specified).
2. Run `dsa-buddy quiz scaffold <problem>` to create the test file.
3. **Always overwrite the scaffolded file** with a complete, production-quality test suite before telling the user it's ready. The scaffold is too thin — replace it entirely with:
   - A clean function stub (correct signature, `pass` body, type hints)
   - `@pytest.mark.parametrize` covering: basic happy-path cases, negative numbers, zeroes, edge indices (pair at start/end), duplicates, two-element arrays, and any problem-specific traps
   - A soft-check test that nudges the user toward the intended approach (e.g. no nested loops, no `sorted()`)
   - A `# ---------- Tests (don't modify) ----------` separator so the user knows their edit boundary
   - User writes ONLY the target function — nothing else
4. Tell the user the file path and what to implement.
5. When the user says they're ready, run `dsa-buddy quiz check <problem>`.
6. If tests pass: "All tests pass!" → `dsa-buddy progress update <problem> --pytest pass`
7. If tests fail: show the failures, offer hints, let them try again.
