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
2. Run `dsa-buddy quiz scaffold <problem>` to create the test file if needed.
3. Tell the user the file path and what to implement.
4. When the user says they're ready, run `dsa-buddy quiz check <problem>`.
5. If tests pass: "All tests pass!" → `dsa-buddy progress update <problem> --pytest pass`
6. If tests fail: show the failures, offer hints, let them try again.
