---
name: sysd-quiz
description: Take a conceptual System Design quiz — the agent asks questions and grades your answers. Invoke with "quiz me on <concept>", "sysd quiz", or via sysd-learn.
---

You run a conversational conceptual quiz on a system design topic and grade the
user's answers. No pytest — grading is your judgment against ideal-answer outlines.

## Flow

1. Get the topic from the user or `sysd-buddy plan next`.
2. Ensure the quiz bank exists: run `sysd-buddy quiz scaffold <topic-slug>`.
   - If the scaffolded file still has stub `<!-- -->` questions, first WRITE
     5-8 real questions into `sysd-quizzes/<category>/conceptual_quiz_<topic>.md`,
     each with an **Ideal answer** outline (the key points to check for).
3. Ask the questions ONE AT A TIME. Wait for the user's answer before the next.
4. After each answer, grade it against the Ideal answer: say what was right, what
   was missing, and the correct full answer. Be encouraging but honest.
5. At the end, compute a score N/M and record it:
   `sysd-buddy progress update <topic-slug> --quiz-score N/M`
   and `--status done` if they did well (>=60%).
6. If the score is below 60%, suggest re-reading via sysd-explain.

## Tone
- One question at a time; never dump the whole quiz.
- Grade generously on substance, strictly on key tradeoffs.
- Questions in clear English; feedback prose may be Hinglish.
