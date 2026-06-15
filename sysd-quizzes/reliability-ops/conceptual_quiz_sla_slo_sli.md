# SLA / SLO / SLI — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update sla-slo-sli --quiz-score N/M` -->

## Q1 (warm-up)
Apne shabdon mein SLI, SLO, aur SLA ke beech ka fark batao. Ek concrete example (jaise availability) ke saath teeno ko distinguish karo.

**Ideal answer:**
- **SLI** = the actual measured metric (e.g., availability = `good requests / total requests`, or p99 latency). It is a number/ratio reflecting real behavior.
- **SLO** = an internal target set on that SLI over a window (e.g., "99.9% availability over 28 days"). No external penalty; it's the team's own goal.
- **SLA** = an external, contractual promise to the customer (e.g., "99.5% uptime or you get service credits") with consequences/penalty when breached.
- Concrete example: SLI = measured 99.93% success; SLO = 99.9% target (met); SLA = 99.5% promised to customer (also met).
- Bonus: notes the strictness ordering — SLA is looser than the SLO.

## Q2 (core)
Error budget kya hota hai? Ek 99.9% SLO over a 28-day window ke liye error budget calculate karke dikhao, aur batao ki teams ise kaise use karti hain.

**Ideal answer:**
- Error budget = `100% - SLO` = the allowed amount of failure/unreliability (here `0.1%`).
- Calculation: 28-day window = `28 × 24 × 60 = 40,320` minutes; `0.1%` of that ≈ **40.3 minutes** of allowed downtime (or ~0.1% of total requests if request-based).
- It's a "currency" that gets spent as outages/errors accumulate.
- Usage: budget remaining → team can ship features / take risky deploys; budget exhausted → feature freeze, only reliability work until budget recovers.
- Key insight: error budget gives an objective referee for the "ship fast vs stay stable" tension.

## Q3 (tradeoff)
Ek interviewer poochta hai: "Apni service ke liye SLO 99.99% rakhoge ya 99.9%?" Tum is decision ko kaise approach karoge? Cost aur "nines" ka tradeoff samjhao.

**Ideal answer:**
- Each additional "nine" costs roughly an order of magnitude more (redundancy, multi-region, on-call load).
- Downtime intuition: 99.9% ≈ 43 min/month, 99.99% ≈ 4.3 min/month, 99.999% ≈ 26 sec/month.
- Decision driver: set the SLO **as low as users will tolerate** — don't pay for nines users don't notice.
- Factors: revenue criticality of the path, user expectations/complaints, dependency SLOs (composed availability), and cost of redundancy.
- Good answer rejects "100%": it leaves zero error budget, blocks all deploys, and costs infinite money.
- Mentions window choice / measurement as part of the tradeoff is a bonus.

## Q4 (gotcha)
Ek teammate kehta hai: "Hamara public SLA 99.99% hai aur internal SLO 99.9% hai — strong promise hai, customers khush honge." Is statement mein kya galti hai?

**Ideal answer:**
- The SLA (99.99%) is **stricter** than the SLO (99.9%) — this is backwards and dangerous.
- Rule: SLA must always be **looser/weaker** than the internal SLO, so the internal target gives a safety buffer before penalties trigger.
- With this inversion, the team will breach the SLA (and pay credits/penalties) even while meeting its own internal target.
- Correct setup: internal SLO 99.9% → public SLA something looser like 99.5%, with the gap absorbing variance.
- Bonus: SLA breaches cost money (service credits/refunds), so the buffer is non-negotiable.

## Q5 (applied)
Tum ek B2B payments API design kar rahe ho jise enterprise customers consume karenge. Tum SLIs, SLOs, aur SLA kaise choose karoge, aur kaunse real systems se inspiration loge?

**Ideal answer:**
- **SLIs:** availability (`successful API calls / valid calls`), latency as a percentile (e.g., p99 < 200ms — not average), and error rate; exclude health-checks and clearly-client (4xx) errors from the denominator where appropriate.
- **SLOs:** payments are revenue-critical, so a high target like 99.99% availability over a rolling 28-day window; latency SLO like "p99 < 200ms over 7 days."
- **Error budget:** derive from the SLO (99.99% → ~4.3 min/month) and gate releases on burn rate; set burn-rate alerts rather than fixed thresholds.
- **SLA:** offer customers a looser contractual number (e.g., 99.95%) with tiered service credits, like AWS/Stripe/Cloudflare do.
- **Real systems:** references AWS (99.99% region SLA with service credits), GCP/Azure, Stripe, or Google SRE's error-budget model.
- Bonus: account for composed availability of downstream dependencies (`0.999 × 0.999 = 0.998`) when committing a number.
