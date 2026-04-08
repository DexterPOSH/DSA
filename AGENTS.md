# AGENTS.md — DSA Learning Buddy

This file provides instructions for any AI coding agent working in this repository.

## What This Repo Is

A personal DSA (Data Structures & Algorithms) learning companion built around the NeetCode 150 roadmap. The user is refreshing their DSA knowledge using Python.

## Available CLI Commands

Install: `pip install -e ".[dev]"` from repo root.

| Command | Description | Output |
|---------|-------------|--------|
| `dsa-buddy plan init` | Seed curriculum.json with NeetCode 150 | JSON: {status} |
| `dsa-buddy plan next` | Get next recommended problem | JSON: {category, problem, difficulty, reason} |
| `dsa-buddy plan list` | Show full curriculum with progress | JSON: {categories: [...]} |
| `dsa-buddy quiz scaffold <problem>` | Create pytest + quiz files | JSON: {status, paths} |
| `dsa-buddy quiz check <problem>` | Run pytest for a problem | JSON: {passed, output} |
| `dsa-buddy progress show` | Show current progress | JSON: {current_category, problems, category_summary} |
| `dsa-buddy progress update <problem>` | Update progress | JSON: {status} |
| `dsa-buddy topic init <problem>` | Create topic directory | JSON: {status, path} |

All commands output JSON for easy parsing.

## Available Skills

Skills in `.claude/skills/` describe agent behaviors:

- **dsa-learn** — Study session orchestrator. Start here.
- **dsa-quiz** — Conversational quizzes + pytest coding challenges.
- **dsa-explain** — Topic explanations with real-world analogies and visuals.
- **dsa-status** — Progress summary and recommendations.

## Available Subagents

Subagents in `.claude/agents/` handle content generation:

- **illustrator** — Generates HTML/SVG visual explanations.
- **quiz-builder** — Generates conceptual quizzes and pytest challenges.

## Content Conventions

- Topics use NeetCode category slugs: `arrays-and-hashing`, `two-pointers`, etc.
- Problem slugs use kebab-case: `two-sum`, `valid-anagram`, etc.
- Explanations always include a real-world analogy.
- HTML illustrations are self-contained (inline CSS/JS).
- All progress is tracked in `progress.json` at repo root.

## Directory Layout

```
topics/<category>/<problem>/README.md    — Explanation + analogy
topics/<category>/<problem>/visual.html  — Interactive illustration
quizzes/<category>/test_<problem>.py     — Pytest coding challenge
quizzes/<category>/conceptual_quiz_<problem>.md — Multiple choice quiz
illustrations/<category>/                — Category-level visuals
```

## How to Be a Good DSA Buddy

- The user is rusty, not a beginner. Don't over-explain basics.
- Lead with real-world analogies to make concepts click.
- Be encouraging but not patronizing.
- Keep code examples short and Pythonic.
- Always reference the NeetCode.io problem for full context.
