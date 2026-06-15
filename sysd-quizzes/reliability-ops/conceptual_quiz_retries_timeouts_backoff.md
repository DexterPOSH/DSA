# Retries, Timeouts & Backoff — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update retries-timeouts-backoff --quiz-score N/M` -->

## Q1 (warm-up)
In one or two lines, what problem does a **timeout** on a remote call solve, and why is "no timeout" dangerous?

**Ideal answer:**
- A timeout bounds how long a caller waits for a response before giving up, so a slow/hung dependency can't block the caller indefinitely.
- Without a timeout, a slow downstream ties up the caller's threads/connections, which exhausts the pool and causes failures to cascade upstream.
- Bonus: timeouts make failures fast and detectable instead of silent hangs.

## Q2 (core)
Walk through how **exponential backoff with jitter** works between retries. Give the rough formula and explain what each piece (exponential part, jitter) buys you.

**Ideal answer:**
- Wait grows between attempts; exponential form is roughly `wait = base * 2^attempt` (e.g. base 100ms → 100, 200, 400, 800ms).
- Exponential growth spreads retries out over time and gives the struggling downstream room to recover instead of being hammered immediately.
- Jitter adds randomness, e.g. full jitter `wait = random(0, base * 2^attempt)`.
- Jitter prevents many clients that failed at the same instant from retrying in lock-step (synchronized spikes / thundering herd); it smooths retries into a continuous spread.
- Should also mention a cap on max attempts and/or an overall deadline.

## Q3 (tradeoff)
Retries are supposed to improve availability, but they can also make an outage worse. Explain this tension and what mechanisms you'd add to keep retries safe.

**Ideal answer:**
- Each retry is an extra request, so blanket retries can multiply load (3x–4x) on a downstream exactly when it's already struggling — "retry amplification."
- This can turn a minor blip into a cascading failure / collapse.
- Safeguards: backoff + jitter (spread load), a max-attempt cap and overall deadline (no infinite retries), a retry budget (e.g. retries ≤ 10% of requests, like gRPC/Envoy), and a circuit breaker to fail-fast when failures are sustained rather than transient.
- Bonus: avoid nested retries at every layer (multiplicative amplification, e.g. 3x at A × 3x at B = 9x).

## Q4 (gotcha)
A teammate says "just retry every failed request automatically — it's safer." Where does this go wrong? Name at least two cases where a retry is the wrong move.

**Ideal answer:**
- Non-idempotent operations: a timeout doesn't mean the request didn't execute (response may have been lost). Blindly retrying can cause duplicate side-effects (double charge, double order). Fix: idempotency keys.
- Non-retryable errors: 4xx like 400 (bad request), 401/403 (auth), 404 will fail deterministically on retry — pure wasted load. Only retry transient errors (5xx/503, 429, timeouts, connection resets).
- Retries without backoff/jitter/cap → thundering herd and amplification.
- Strong answer distinguishes "retry only transient + idempotent-safe failures."

## Q5 (applied)
You're designing service A that calls B, which calls C, all over RPC. How would you apply timeouts, retries, and backoff across this chain? Mention any real systems/patterns you'd lean on.

**Ideal answer:**
- Put a timeout on every hop, sized from the downstream's p99 latency plus headroom (not a giant default like 30s).
- Use a timeout/deadline budget across the chain (deadline propagation): split the overall deadline across hops so A doesn't give up while C is still working, and avoid wasted work.
- Retry only on transient errors with exponential backoff + jitter, capped attempts (e.g. 3) and an overall deadline.
- Avoid retrying at every layer (centralize retries at one layer or use a retry budget) to prevent multiplicative amplification.
- Add a circuit breaker so sustained failures fail-fast instead of retry-storming.
- Real systems: gRPC / Envoy / Istio service mesh retry policies and retry budgets, Finagle, AWS SDK exponential-backoff-with-jitter; DLQ for async/message-consumer paths.
