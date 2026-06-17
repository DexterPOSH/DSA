# Observability (Logs/Metrics/Traces) — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update observability --quiz-score N/M` -->

## Q1 (warm-up)
What are the "three pillars" of observability, and in one line each, what is the primary job of each?

**Ideal answer:**
- **Metrics** — aggregated numeric measurements over time (counters/gauges/histograms); cheap, continuous, good for dashboards/alerts. Tell you *that* something is wrong.
- **Logs** — discrete timestamped event records (ideally structured/JSON); high detail. Tell you *what exactly* happened.
- **Traces** — end-to-end record of a single request's journey across services as a tree of spans. Tell you *where* (which service/hop) the time or failure went.
- Bonus: no single pillar gives the full picture; their power is in correlation.

## Q2 (core)
In distributed tracing, how does a single `trace_id` end up tying together work done by 20 different microservices? Walk through the mechanism.

**Ideal answer:**
- At the request entry point, a unique `trace_id` is generated; the first operation is the root **span**.
- Each unit of work is a **span** with its own `span_id` and a `parent_span_id`, forming a tree.
- **Context propagation**: the `trace_id` and current `span_id` are passed to every downstream call via headers (e.g. W3C `traceparent`), so each service continues the same trace rather than starting a new one.
- The tracing backend (Jaeger/Zipkin/Tempo) collects spans and reassembles them by `trace_id` into a waterfall, showing per-hop latency.
- Strong answer mentions injecting `trace_id` into logs too, for cross-pillar correlation.

## Q3 (tradeoff)
You run a service at 50k QPS and your logging bill is exploding. What levers do you pull to control cost, and what do you trade off with each?

**Ideal answer:**
- **Log levels**: keep ERROR/WARN on in prod, turn off DEBUG/INFO; trade off = less context for routine debugging.
- **Sampling**: keep all error/slow logs, sample the rest; trade off = some normal-path detail lost.
- **Retention tiers**: hot storage (SSD, ~7 days) for recent, cold/object storage (~90 days) for archive; trade off = slower cold queries.
- **Structured logging**: cheaper/faster to index and query than free text.
- Recognize that metrics are far cheaper (cost scales with cardinality, not request volume), so push aggregate questions to metrics instead of logs. Mention that observability cost can exceed compute cost at scale.

## Q4 (gotcha)
An engineer adds `user_id` and `request_id` as labels on a Prometheus counter so they can "slice metrics per user." Why is this a problem, and where should that data live instead?

**Ideal answer:**
- **Cardinality explosion**: metric cost scales with the number of *unique label-value combinations*. `user_id`/`request_id` are high-cardinality (millions of values) → millions of separate time-series → TSDB memory blows up / OOM.
- Metrics are for low-cardinality aggregates (status code, route, region).
- High-cardinality, per-request data belongs in **logs and traces**, where `trace_id`/`user_id` are fields you filter on, not pre-aggregated series.
- Bonus: this is also the monitoring-vs-observability point — per-user explorability comes from traces/structured logs, not metrics.

## Q5 (applied)
Production alert fires at 3am: P99 latency jumped from 80ms to 900ms. Using all three pillars, walk through how you'd find root cause, and explain why each pillar is needed.

**Ideal answer:**
- **Metric** detects/confirms the problem (P99 spike alert) and scopes it — which service/endpoint/region, since when. Tells you *that* and roughly *where at aggregate level*.
- **Traces**: pull slow traces from that time window; the span waterfall shows which downstream hop ate the latency (e.g. 800ms in a DB call), telling you *where* precisely.
- **Logs**: take the `trace_id` from a slow trace and pull correlated log lines to see *what exactly* happened (e.g. timeout, lock contention, a specific error/exception).
- Emphasize **correlation via shared `trace_id`** is what makes the workflow fast; without it you'd be grepping 20 services blind.
- Strong answer: mentions error-biased / tail-based sampling ensures the failing trace was actually captured, and that this whole flow drives down MTTR.
