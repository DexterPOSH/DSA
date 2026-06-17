---
name: dsa-status
description: Show DSA learning progress — what you've done, what's next, weak areas. Invoke with "dsa status", "where am I", "show progress", or "how am I doing".
---

You are showing the user their DSA learning progress.

## Flow

1. Run `dsa-buddy progress show` to get the full progress JSON.
2. Run `dsa-buddy plan list` to get the curriculum with statuses.
3. Present a clear summary:
   - **Overall:** X/150 problems completed
   - **Current category:** name + progress (e.g., "Arrays & Hashing: 5/9")
   - **Categories breakdown:** table or list showing done/total per category
   - **Weak areas:** any problems with quiz scores below 60% — suggest reviewing
   - **Next up:** the recommended next problem from `dsa-buddy plan next`
4. If no progress exists yet, say: "You haven't started yet! Say 'let's study DSA' to begin."

## Tone

- Factual and encouraging
- Highlight progress, not gaps
- If they've been consistent: "You're on a roll!"
- If returning after a break: "Welcome back! Let's pick up where you left off."
