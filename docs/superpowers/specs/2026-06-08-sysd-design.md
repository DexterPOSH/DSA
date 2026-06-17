# SysD — System Design Learning Suite (Design Spec)

**Date:** 2026-06-08
**Status:** Approved (pending spec review)
**Author:** Deepak Dhami (with Claude)

## Purpose

Add a System Design study companion to this repo, mirroring the existing DSA
learning suite (`dsa-buddy` + `dsa-*` skills). The user is preparing for system
design interviews and wants to **learn concepts first, then be quizzed on them**.
Everything is namespaced `sysd-*` and kept fully separate from the DSA tooling so
the working DSA flow is never touched.

## Non-Goals (YAGNI)

- No pytest harness — system design answers are not unit-testable.
- No design-doc rubric grader.
- No mock-interview simulation.

These were explicitly deferred. The practice model is **conceptual Q&A only**.
Any of the above can be added later as a new quiz mode.

## Architecture

A new Click CLI `sysd-buddy` plus four skills, with separate content and state:

```
sysd_buddy/                          # new Python package (Click CLI)
  __init__.py
  cli.py                             # `sysd-buddy` entry point, command groups
  plan.py                            # plan init | next | list
  progress.py                        # progress show | update
  topic.py                           # topic init
  quiz.py                            # quiz scaffold
  curriculum_data.py                 # the two-track roadmap seed data
sysd-curriculum.json                 # seeded by `plan init`
sysd-progress.json                   # learner progress + quiz scores
sysd-topics/<category>/<topic>/
  README.md                          # the explanation (Hinglish prose)
  visual.html                        # illustrator-generated architecture visual
sysd-quizzes/<category>/
  conceptual_quiz_<topic>.md         # question bank for the topic
.claude/skills/
  sysd-learn/SKILL.md
  sysd-explain/SKILL.md
  sysd-quiz/SKILL.md
  sysd-status/SKILL.md
```

**Reuse:** the existing `illustrator` subagent generates `visual.html` for each
topic (architecture diagrams, data-flow). No new subagent required.

**Packaging:** add `sysd-buddy = "sysd_buddy.cli:cli"` to `pyproject.toml`
`[project.scripts]`. Same `click` dependency as dsa-buddy. Installed via the same
editable install.

**Conventions (inherited from DSA):**
- Explanations in **Hinglish**; code, commands, and technical terms stay English.
- Topic READMEs follow the DSA README shape adapted for concepts (see Content Model).

## CLI Commands

```
sysd-buddy plan init                 # seed sysd-curriculum.json from curriculum_data
sysd-buddy plan next                 # recommend next topic (sequence-aware, Track 1 before Track 2)
sysd-buddy plan list                 # full curriculum annotated with progress

sysd-buddy progress show             # current state (per category/track)
sysd-buddy progress update <topic> --status {not-started|in-progress|done}
                                     [--quiz-score N/M]

sysd-buddy topic init <topic>        # create sysd-topics/<category>/<topic>/README.md from template

sysd-buddy quiz scaffold <topic>     # create sysd-quizzes/<category>/conceptual_quiz_<topic>.md
```

Grading is **conversational**: the `sysd-quiz` skill reads the quiz markdown, asks
the questions, evaluates the user's typed answers, and records the result via
`progress update <topic> --quiz-score N/M`. There is no `quiz check` (no pytest).

Track gating: `plan next` recommends Track 2 (Design Problems) only after all
Track 1 (Building Blocks) topics are `done`.

## Data Model

### sysd-curriculum.json
```json
{
  "version": 1,
  "tracks": [
    {
      "name": "Building Blocks",
      "slug": "building-blocks",
      "order": 1,
      "categories": [
        {
          "name": "Fundamentals & Networking",
          "slug": "fundamentals-networking",
          "order": 1,
          "topics": [
            { "name": "DNS & How a Request Travels", "slug": "dns-request-lifecycle" }
          ]
        }
      ]
    }
  ]
}
```
(`difficulty` is omitted — concepts aren't easy/medium/hard the way LeetCode is.)

### sysd-progress.json
```json
{
  "current_track": null,
  "current_category": null,
  "topics": {
    "dns-request-lifecycle": {
      "status": "done",
      "quiz_score": 4,
      "quiz_total": 5,
      "completed_at": "2026-06-08"
    }
  },
  "category_summary": {}
}
```

## Content Model

### Topic README (sysd-topics/<category>/<topic>/README.md)
Sections, adapted from the DSA README for concepts:
1. **Title** + category + track
2. **What it is** — one-sentence definition
3. **Real-world analogy** (Hinglish) — make it tangible
4. **How it works** — step-by-step / key mechanics
5. **Tradeoffs & variants** — the decision points an interviewer probes
6. **When to use it** — pattern recognition
7. **Common interview gotchas** — misconceptions to avoid
8. **Practice** — pointer to the conceptual quiz + visual

### Conceptual quiz (sysd-quizzes/<category>/conceptual_quiz_<topic>.md)
A bank of 5–8 questions per topic, each with: the question, an ideal-answer
outline (key points the grader looks for), and a difficulty tag. The `sysd-quiz`
skill uses the ideal-answer outline to grade conversationally.

## Skills

- **sysd-learn** — session coordinator. Runs `progress show`, seeds via
  `plan init` on first run, calls `plan next`, summarizes status, offers
  **Explain** (→ sysd-explain) or **Quiz** (→ sysd-quiz). Records progress after.
- **sysd-explain** — teaches one concept: generates/loads the topic README
  (Hinglish), then spawns the `illustrator` subagent for `visual.html`. Tells the
  user the file to open.
- **sysd-quiz** — runs the conceptual quiz: scaffolds the quiz MD if missing,
  asks questions one at a time, grades answers against the ideal-answer outlines,
  reports a score, and calls `progress update --quiz-score`.
- **sysd-status** — progress dashboard: per-track/category completion, quiz
  scores, weak areas (low scores), recommended next topic.

## Curriculum Content

### Track 1 — Building Blocks (learn first)
1. **Fundamentals & Networking** — DNS & request lifecycle; HTTP/HTTPS; TCP vs UDP; REST vs RPC vs GraphQL; WebSockets & SSE
2. **Scaling & Load Balancing** — vertical vs horizontal scaling; load balancers (L4 vs L7); reverse proxy; stateless services & session handling
3. **Caching & CDN** — cache strategies (cache-aside, write-through, write-back); eviction (LRU/LFU); CDN; cache invalidation & staleness
4. **Databases & Storage** — SQL vs NoSQL; ACID vs BASE; indexing; B-tree vs LSM-tree; blob/object storage
5. **Data Distribution** — replication (leader-follower, multi-leader); sharding/partitioning; consistent hashing
6. **Consistency & Coordination** — CAP theorem; PACELC; quorum (R+W>N); leader election; consensus (Raft/Paxos overview); distributed locks
7. **Async & Messaging** — message queues; pub/sub; Kafka basics (partitions/offsets); idempotency; backpressure; event-driven architecture
8. **Reliability & Ops** — rate limiting (token/leaky bucket); circuit breakers; retries, timeouts, exponential backoff; observability (logs/metrics/traces); SLA/SLO/SLI

### Track 2 — Design Problems (unlocked after Track 1)
Design TinyURL · Design a Rate Limiter · Design Twitter / News Feed · Design a
Chat System (WhatsApp) · Design a Web Crawler · Design a Notification System ·
Design YouTube / Video Streaming · Design Uber / Nearby Friends · Design a
Distributed Key-Value Store

Each Track-2 problem README uses the same template but emphasizes: requirements &
scope → capacity/scale estimate → API → high-level design → data model → deep
dives (the relevant building blocks) → bottlenecks & tradeoffs.

## Testing

The CLI itself is testable with pytest (mirroring `tests/` for dsa-buddy):
plan seeding, `plan next` sequence/track-gating logic, progress update + score
parsing, topic/quiz scaffold file creation. The *learning content* is not
auto-graded.

## Build Order (for the implementation plan)

1. `sysd_buddy` package skeleton + `pyproject.toml` entry point
2. `curriculum_data.py` (both tracks) + `plan init/next/list`
3. `progress.py` (show/update with score parsing) + track gating
4. `topic.py` (README template) + `quiz.py` (conceptual quiz scaffold)
5. CLI tests
6. Four `sysd-*` skills
7. Seed first category's content (Fundamentals & Networking) as a worked example
```
