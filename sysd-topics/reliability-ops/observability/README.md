# Observability (Logs/Metrics/Traces)

**Track:** Building Blocks
**Category:** Reliability & Ops

## What It Is

Observability ek system property hai jo aapke external outputs — primarily logs, metrics, aur traces (the "three pillars") — se aapko system ki internal state infer karne deti hai, taaki aap un failures ko bhi debug kar sako jinko aapne pehle se anticipate nahi kiya tha.

## Real-World Analogy

Socho aap ek hospital ke patient ko monitor kar rahe ho. Teen alag-alag tools use hote hain aur teeno ka kaam alag hai:

- **Metrics** = bedside monitor jo har second heart rate, blood pressure, aur oxygen ko number ke roop mein dikhata hai. Ye aapko turant bata deta hai ki "kuch gadbad hai" — BP suddenly gir gaya — par ye nahi batata ki *kyun*. Ye sasta hai, continuous hai, aur saari history pe alarm laga sakte ho.
- **Logs** = nurse ki diary jisme har event timestamp ke saath likha hota hai: "2:04pm — medicine X di", "2:11pm — patient ne pain complain kiya". Jab kuch galat ho, to aap diary padh ke exact event sequence reconstruct karte ho. Rich detail, par har patient ka pura diary store karna mehenga.
- **Traces** = jab patient ek department se doosre department ghoomta hai (ER → X-ray → surgery → ICU), to ek single patient-file uske saath travel karti hai aur har stop pe kitna time laga wo record karti hai. Isse pata chalta hai ki total 3-ghante ki delay mein bottleneck X-ray queue thi, surgery nahi.

Akele koi ek tool poori kahani nahi deta. Metric chillaata hai "problem hai", trace batata hai "kahan hai", aur log batata hai "exactly kya hua". Observability matlab teeno ko mila ke unknown problems ka diagnosis kar paana.

## How It Works

1. **Metrics — aggregate numbers over time:** Application code emit karta hai numeric measurements (counters, gauges, histograms) jaise `http_requests_total`, `request_latency_ms`, `cpu_usage`. Ye ek time-series database (Prometheus, InfluxDB) mein store hote hain, usually pre-aggregated over fixed intervals (e.g. har 15s ek scrape). Key property: metric ka cost cardinality pe depend karta hai, raw request volume pe nahi — 1 million requests bhi ek single counter increment hi karti hain. Isiliye metrics sabse sasti pillar hai aur 100% traffic pe chal sakti hai. Dashboards aur alerts (P99 latency > 500ms for 5 min → page) inhi pe bante hain.

2. **Logs — discrete timestamped events:** Har significant event ek log line emit karta hai. Modern systems **structured logging** use karte hain — plain text ke bajaye JSON (`{"ts":..., "level":"ERROR", "user_id":42, "trace_id":"abc"}`) — taaki machine query kar sake. Logs ek log aggregator (ELK/Elasticsearch, Loki, Splunk) mein ship hote hain. Problem: high-throughput service pe agar har request 5-10 log lines emit kare aur QPS 50k ho, to ye terabytes/day ban jaata hai, isiliye log volume ka cost dominate karta hai — yahin **sampling** aur log levels (INFO production mein off, ERROR/WARN on) kaam aate hain.

3. **Traces — request ka end-to-end journey:** Ek distributed system mein ek single user request 20-30 microservices ko hit kar sakti hai. Trace us poore journey ko capture karta hai as a tree of **spans**. Har span ek operation hai (e.g. "auth-service DB call", 12ms). Mechanics: request ke entry pe ek unique `trace_id` generate hota hai, aur har downstream call ke saath ye `trace_id` + parent `span_id` HTTP headers (W3C `traceparent`) mein propagate hote hain — isi ko **context propagation** kehte hain. Backend (Jaeger, Tempo, Zipkin) in spans ko `trace_id` se reassemble karke ek waterfall diagram banata hai jisme aap dekh sakte ho ki 800ms latency ka 600ms kis service mein gaya.

4. **Correlation — asli power:** Teeno pillars ko jodne ke liye shared identifiers use hote hain. Best practice: `trace_id` ko log lines mein bhi inject karo. To flow ye banta hai — metric alert fire hota hai (P99 spike) → aap us window ke slow traces dekhte ho → ek slow trace ka `trace_id` lete ho → us `trace_id` se exact logs pull karte ho. Yahi tabhi possible hai jab teeno correlate karein.

5. **Sampling — kyunki sab kuch store karna unaffordable hai:** 100% traces store karna at scale prohibitive hai. Do strategies: **head-based sampling** (entry pe hi decide, e.g. 1% requests trace karo — simple par interesting errors miss ho sakte hain) aur **tail-based sampling** (pura trace buffer karo, phir decide — e.g. saare error/slow traces rakho, baaki 99% normal drop karo). Tail-based zyada useful hai par memory/infra mehenga hai.

## Tradeoffs & Variants

- **Cost vs detail (per pillar):** Metrics sabse sasti par low-detail (sirf numbers, koi context nahi). Logs medium cost, high detail. Traces high cost (volume + context propagation overhead). Interviewer aksar poochta hai "log bill control kaise karoge" — answer: log levels, sampling, retention tiers (hot 7 days SSD, cold 90 days object storage), aur structured logs taaki index efficient ho.

- **Cardinality explosion (metrics ka silent killer):** Metric ka cost labels ki *unique combinations* (cardinality) pe depend karta hai. Agar aap `user_id` ya `request_id` ko metric label bana do, to har unique value ek alag time-series ban jaati hai — millions of series, jo Prometheus ko OOM kar deti hain. Rule: high-cardinality dimensions (user_id, IP, trace_id) metrics mein nahi, logs/traces mein jaate hain.

- **Head vs tail sampling:** Head simple aur cheap, par rare errors miss kar sakta hai. Tail captures all anomalies but needs to buffer entire traces, jo high memory aur a centralized collector demand karta hai.

- **Push vs pull metrics:** Prometheus **pull** model use karta hai (scrape targets) — service discovery clean, par short-lived jobs (batch) miss ho jaate hain (Pushgateway se patch karte hain). StatsD/OpenTelemetry **push** karte hain — ephemeral workloads ke liye behtar.

- **Vendor-neutral instrumentation:** Aaj **OpenTelemetry (OTel)** standard ban gaya hai — ek hi SDK se traces/metrics/logs emit karo, phir kisi bhi backend (Jaeger, Prometheus, Datadog) pe bhejo. Tradeoff: vendor lock-in se bachte ho, par ek extra collector layer maintain karna padta hai.

## When To Use It

- **Microservices / distributed systems:** Jaise hi request multiple services ko cross kare, **distributed tracing** non-negotiable ho jaata hai — bina trace ke cross-service latency debug karna almost impossible hai. Uber, Netflix isiliye Jaeger/large-scale tracing chalate hain.
- **SLO/SLA monitoring aur alerting:** Metrics pe alerts (error rate, P99 latency, saturation) banao — ye "RED" (Rate, Errors, Duration) aur "USE" (Utilization, Saturation, Errors) methods ka core hai. Google ka SRE practice metrics-driven SLOs pe hi khada hai.
- **Incident debugging / root cause analysis:** Jab production mein 3am pe pager bajta hai — metric se "kya broke" pata chalta hai, trace se "kahan", log se "kyun". Teeno chahiye for fast MTTR (Mean Time To Resolution).
- **Real systems:** Prometheus + Grafana (metrics/dashboards), ELK ya Grafana Loki (logs), Jaeger/Zipkin/Grafana Tempo (traces), Datadog/Honeycomb/New Relic (all-in-one commercial), OpenTelemetry (vendor-neutral instrumentation).

## Common Interview Gotchas

- **"Monitoring" ≠ "Observability":** Monitoring = pre-defined questions ka answer (known dashboards/alerts — "is CPU high?"). Observability = aap *unknown* questions bhi pooch sako ("which specific tenant's requests with feature-flag X on are slow?") bina naya code deploy kiye. Observability monitoring ka superset hai; high-cardinality data (especially traces aur structured logs) ye explorability deta hai. Ye distinction interviewers ko impress karta hai.

- **High-cardinality data ko metric mein mat daalo:** Sabse common mistake. `user_id` ya `trace_id` ko Prometheus label banana cardinality explosion karega aur TSDB crash. Unique-per-request data logs/traces mein jaata hai, metrics aggregates ke liye hain.

- **Logs alone se distributed system debug nahi hota:** Naye engineers sochte hain "bas zyada logging daal do". Par 30 services ke individual logs ko manually correlate karna unmanageable hai bina shared `trace_id` ke. Isiliye traces + log correlation chahiye, sirf log volume badhana solution nahi.

- **Sampling matlab data loss — design carefully:** Agar aap naively 1% head sampling karo, to ho sakta hai exact failing request ka trace hi drop ho jaaye. Errors/slow requests ke liye tail-based ya error-biased sampling use karo taaki anomalies hamesha capture hon.

- **Cost ko underestimate karna:** "Sab kuch log karo, sab trace karo" interview mein red flag hai. At scale (50k+ QPS) ye observability bill aapke compute bill se bada ho sakta hai. Sampling, retention tiers, aur cardinality budgets ke baare mein baat karna maturity dikhata hai.

- **Clocks aur ordering:** Distributed traces span timing ke liye different machines ke clocks pe depend karte hain — clock skew se spans thode galat align ho sakte hain. `trace_id` correlation isse immune hai (causal parent/child links), par wall-clock waterfall ko thoda salt-of-grain ke saath dekho.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/reliability-ops/conceptual_quiz_observability.md`](../../../sysd-quizzes/reliability-ops/conceptual_quiz_observability.md) — `sysd-buddy quiz scaffold observability` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update observability --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — three pillars (metrics/logs/traces), ek request ka trace waterfall across services, aur trace_id se logs/metrics correlation ka interactive diagram.
