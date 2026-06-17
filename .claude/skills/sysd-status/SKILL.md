---
name: sysd-status
description: Show System Design learning progress — what you've done, what's next, weak areas. Invoke with "sysd status", "system design progress", or "how am I doing on system design".
---

You show the user's system design learning progress.

## Flow

1. Run `sysd-buddy plan list` for the annotated curriculum and
   `sysd-buddy progress show` for scores.
2. Present:
   - Per-track, per-category completion (e.g. "Building Blocks: 6/37 topics").
   - Quiz scores; flag weak areas (topics done with score < 60%).
   - The recommended next topic (`sysd-buddy plan next`).
3. Keep it a scannable dashboard, not prose. Note that Design Problems unlock
   after Building Blocks is complete.
