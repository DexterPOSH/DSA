---
name: dsa-explain
description: Explain a DSA topic with real-world analogies and visual illustrations. Invoke with "explain <topic>", "teach me about <topic>", or "what is <topic>".
---

You are explaining a DSA concept to someone who is rusty — they've seen this before but need it to click again. Use real-world analogies and clear step-by-step breakdowns.

## Flow

1. Get the topic from the user's request or from `dsa-buddy plan next`.
2. Run `dsa-buddy topic init <problem>` to create the topic directory if needed.
3. Read `topics/<category>/<problem>/README.md` if it already has content.
4. Generate or present the explanation covering:
   - **What it is** — one sentence definition
   - **Real-world analogy** — make it tangible (e.g., "A hash map is like a coat check — you hand over your coat and get a numbered ticket...")
   - **How it works** — step-by-step walkthrough
   - **Time & space complexity** — with intuition for why
   - **Common pitfalls** — mistakes to watch out for
   - **When to use it** — pattern recognition for interviews
5. Spawn the `illustrator` subagent to generate a visual explanation:
   - For the specific problem: save as `topics/<category>/<problem>/visual.html`
   - For the broader concept: save in `illustrations/<category>/`
6. Update the topic README with the generated content.
7. Tell the user about the visual file they can open in their browser.

## Style

- Lead with the analogy — make it memorable
- Use concrete examples, not abstract descriptions
- Keep code examples short (5-10 lines max)
- Reference NeetCode.io for the full problem
