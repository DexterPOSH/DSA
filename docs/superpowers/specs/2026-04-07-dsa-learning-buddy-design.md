# DSA Learning Buddy — Design Spec

## Overview

A personal DSA study companion that generates learning plans, quizzes, and visual explanations aligned with NeetCode.io. Built as a Python CLI with skills and subagents that work across any AI coding agent (Claude Code, GitHub Copilot, Codex, OpenClaw).

**Target user:** Rusty on DSA — knows the concepts but needs them unlocked with good explanations, real-world analogies, and consistent practice.

**Primary language:** Python.

## Architecture

Two layers, skills-first and agent-agnostic.

### Skills & Subagents (the interface)

Markdown files discoverable by any modern AI agent. Located in `.claude/skills/` and `.claude/agents/`.

**Skills:**

| Skill | Purpose |
|-------|---------|
| `dsa-learn` | Study session orchestrator. Reads progress, suggests what to do next, coordinates quiz/explain/coding flows. |
| `dsa-quiz` | Two modes: conversational (agent asks questions in terminal, grades answers) and pytest (scaffolds coding challenges). |
| `dsa-explain` | Explains a topic with real-world analogy, complexity analysis, common pitfalls. Spawns illustrator for visuals. |
| `dsa-status` | Reads progress, presents summary: current category, done/remaining, weak areas, next recommendation. |

**Subagents:**

| Agent | Purpose |
|-------|---------|
| `illustrator` | Generates HTML files with step-by-step visual walkthroughs and SVG for static diagrams. Every illustration includes a title, real-world analogy callout, and step-by-step breakdown. |
| `quiz-builder` | Creates `conceptual_quiz.md` (5 multiple-choice questions) and `test_<problem>.py` (pytest with stubs, hints as comments, multiple test cases). |

### Python CLI (the data engine)

Package: `dsa_buddy/`. Installed via `pip install -e .` with a `pyproject.toml`.

Dependencies: `click`, `pytest`. No heavy frameworks.

All commands output JSON so any agent can parse results. Human-readable summaries come from the skills layer.

```
dsa-buddy plan next                # → {topic, category, reason}
dsa-buddy plan list                # → curriculum with status markers
dsa-buddy plan init                # → seeds curriculum.json with NeetCode roadmap

dsa-buddy quiz scaffold <topic>    # → creates pytest + conceptual quiz files
dsa-buddy quiz check <topic>       # → runs pytest, returns pass/fail JSON

dsa-buddy progress show            # → JSON summary of current state
dsa-buddy progress update <topic> --status done --quiz-score 4/5 --pytest pass

dsa-buddy topic init <topic>       # → creates topic dir with README template
```

## Directory Structure

```
DSA/
├── AGENTS.md                       # Universal context for all AI agents
├── CLAUDE.md                       # Claude-specific instructions
├── dsa_buddy/                      # Python CLI package
│   ├── __init__.py
│   ├── cli.py                      # Click entry point
│   ├── plan.py                     # Curriculum management + adaptive ordering
│   ├── quiz.py                     # Quiz scaffolding & test running
│   ├── progress.py                 # Progress tracking
│   └── topic.py                    # Topic directory scaffolding
├── pyproject.toml                  # Package config + editable install
├── .claude/
│   ├── skills/
│   │   ├── dsa-learn/SKILL.md
│   │   ├── dsa-quiz/SKILL.md
│   │   ├── dsa-explain/SKILL.md
│   │   └── dsa-status/SKILL.md
│   └── agents/
│       ├── illustrator.md
│       └── quiz-builder.md
├── curriculum.json                 # NeetCode categories + problem list
├── progress.json                   # Completions, scores, timestamps
├── topics/
│   └── <category>/
│       └── <problem>/
│           ├── README.md           # Explanation + real-world analogy
│           └── visual.html         # Interactive illustration
├── quizzes/
│   └── <category>/
│       ├── conceptual_quiz.md      # For conversational quizzing
│       └── test_<problem>.py       # Pytest challenge
├── illustrations/
│   └── <category>/
│       ├── <analogy>.html          # Category-level concept visuals (e.g., hash-map-analogy.html)
│       └── <diagram>.svg           # Category-level static diagrams (e.g., two-pointer.svg)
└── tests/
    └── test_plan.py                # Tests for the CLI itself
```

Topics follow NeetCode's category naming: `arrays-and-hashing`, `two-pointers`, `sliding-window`, `stack`, `binary-search`, `linked-list`, `trees`, `tries`, `heap-priority-queue`, `backtracking`, `graphs`, `advanced-graphs`, `1d-dynamic-programming`, `2d-dynamic-programming`, `greedy`, `intervals`, `math-and-geometry`, `bit-manipulation`.

## Data Models

### curriculum.json

The NeetCode roadmap as structured data. Seeded by `dsa-buddy plan init`.

```json
{
  "version": 1,
  "categories": [
    {
      "name": "Arrays & Hashing",
      "slug": "arrays-and-hashing",
      "order": 1,
      "problems": [
        {
          "name": "Two Sum",
          "slug": "two-sum",
          "difficulty": "easy",
          "neetcode_url": "https://neetcode.io/problems/two-integer-sum"
        }
      ]
    }
  ]
}
```

### progress.json

Tracks completions, scores, and timestamps. Updated by `dsa-buddy progress update`.

```json
{
  "current_category": "arrays-and-hashing",
  "problems": {
    "two-sum": {
      "status": "done",
      "quiz_score": 4,
      "quiz_total": 5,
      "pytest_passed": true,
      "completed_at": "2026-04-08"
    }
  },
  "category_summary": {
    "arrays-and-hashing": {"done": 1, "total": 9}
  }
}
```

## Adaptive Ordering

Implemented in `plan.py`. Logic for `dsa-buddy plan next`:

1. Start with NeetCode's default category order.
2. Within a category, present problems easy → medium → hard.
3. If a quiz score is below 60%, resurface that topic in a later review cycle.
4. If all problems in a category are done with scores above 80%, move to the next category.
5. Always return the single next recommended problem with a reason string.

## Illustration Conventions

The `illustrator` subagent follows these rules:

- **HTML files** for interactive step-by-step walkthroughs (e.g., animate how a hash map resolves collisions).
- **SVG files** for static diagrams (data structure shapes, pointer diagrams, tree structures).
- Every illustration includes:
  - A title describing what it shows
  - A real-world analogy callout (e.g., "Think of a hash map like a coat check...")
  - A step-by-step breakdown of the algorithm or data structure operation
- HTML files are self-contained (inline CSS/JS, no external dependencies) so they open in any browser.
- Markdown topic READMEs embed illustrations with relative links.

## Quiz Conventions

### Conceptual Quiz (conversational)

Stored as `conceptual_quiz.md` with this structure:

```markdown
# Arrays & Hashing — Two Sum Quiz

## Q1
What is the time complexity of the brute force two sum approach?
- A) O(n)
- B) O(n log n)
- C) O(n²)
- D) O(1)

**Answer:** C
**Explanation:** Brute force checks every pair, which is n*(n-1)/2 comparisons.
```

The agent reads the file, asks questions one at a time, hides the answer, grades the response, and explains.

### Pytest Challenge

Stored as `test_<problem>.py`:

```python
"""
Two Sum — Coding Challenge

Given an array of integers and a target, return indices of two numbers that add up to target.

Hint: Think about what complement you need for each number.
"""

def two_sum(nums: list[int], target: int) -> list[int]:
    # TODO: Implement this
    pass

def test_basic():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]

def test_negative():
    assert two_sum([-1, -2, -3, -4, -5], -8) == [2, 4]

def test_duplicate():
    assert two_sum([3, 3], 6) == [0, 1]
```

The user implements the function, runs `dsa-buddy quiz check <topic>` (which runs pytest), and progress is updated.

## Skill Details

### dsa-learn (session orchestrator)

1. Run `dsa-buddy progress show` to get current state.
2. If first session, run `dsa-buddy plan init` to seed curriculum.
3. Present a brief "welcome back" with progress summary.
4. Run `dsa-buddy plan next` to get the recommended topic.
5. Offer three actions: explain the topic, take a quiz, or do a coding challenge.
6. After each activity, run `dsa-buddy progress update` with results.

### dsa-quiz

**Conversational mode:**
1. Check if `quizzes/<category>/conceptual_quiz.md` exists for the topic.
2. If not, spawn `quiz-builder` subagent to create it.
3. Read the quiz file, ask questions one at a time.
4. Grade each answer, explain wrong ones.
5. Report final score, update progress.

**Pytest mode:**
1. Check if `quizzes/<category>/test_<problem>.py` exists.
2. If not, run `dsa-buddy quiz scaffold <topic>`.
3. Tell the user to implement the function stubs.
4. When ready, run `dsa-buddy quiz check <topic>`.
5. Report results, update progress.

### dsa-explain

1. Check if `topics/<category>/<problem>/README.md` exists.
2. If not, run `dsa-buddy topic init <topic>` then generate the explanation.
3. Explanation includes: concept, real-world analogy, complexity, common pitfalls, NeetCode link.
4. Spawn `illustrator` subagent to generate visual content.
5. Present the explanation conversationally, reference the generated files.

### dsa-status

1. Run `dsa-buddy progress show`.
2. Present: current category, problems done vs remaining, weak areas (low quiz scores), next recommendation.
3. If no progress yet, suggest starting with `dsa-learn`.

## Testing

- `tests/test_plan.py` — tests adaptive ordering logic
- `tests/test_progress.py` — tests progress read/update
- `tests/test_quiz.py` — tests quiz scaffolding and checking
- `tests/test_topic.py` — tests topic directory creation

Run with `pytest tests/`.
