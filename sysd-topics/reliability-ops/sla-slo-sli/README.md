# SLA / SLO / SLI

**Track:** Building Blocks
**Category:** Reliability & Ops

## What It Is

SLI ek measured metric hai (jaise success rate ya p99 latency), SLO us SLI pe set kiya gaya internal target hai (jaise "99.9% requests success"), aur SLA wo external, contractually-promised guarantee hai jiske toot-ne pe customer ko penalty/refund milta hai.

## Real-World Analogy

Socho ek pizza delivery shop hai jo promise karti hai "30 minute ya free."

- **SLI** = wo actual stopwatch reading jo har order pe measure hoti hai — "aaj ki deliveries mein se kitne % 30 min ke andar pahunche." Ye raw measurement hai, sach jaisa hai waisa.
- **SLO** = shop ka apna internal target — "hum chahte hain ki 95% deliveries 30 min ke andar ho." Ye andar ka goal hai jis pe team kaam karti hai; customer ko ispe penalty nahi milti.
- **SLA** = wo printed promise jo customer ko diya gaya hai — "agar 30 min se late hua to pizza free." Ye toot-ne pe shop ko paisa (refund) dena padta hai.

Notice karo: shop ka internal target (SLO = 95% on-time) hamesha external promise (SLA = "har late order pe refund") se **strict** rakha jaata hai, taaki ek-aadha late order shop ko bankrupt na kar de. SLI sirf measure karta hai, SLO andar ka lakshya hai, SLA bahar ki contractual guarantee hai. Yahi teen cheezon ka fark interviewer test karta hai.

## How It Works

1. **SLI define karo (the measurement):** Sabse pehle ek meaningful metric chuno jo user ke experience ko reflect kare. Typical SLIs: **availability** (`good requests / total requests`), **latency** (jaise "% of requests served under 200ms"), **error rate**, ya **throughput/QPS**. Achha SLI hamesha ek ratio of good events / valid events hota hai, taaki wo 0-100% ke beech normalize ho. Example: ek service jo 10,000 QPS handle karti hai, agar 1 minute mein 600,000 requests aayi aur 599,400 success huyi, to availability SLI = `599400 / 600000 = 99.9%`.

2. **SLO set karo (the internal target):** SLI pe ek target rakho over a time window. Common form: **"99.9% availability over a rolling 28-day window"** ya **"p99 latency < 200ms over 7 days."** Ye number business needs aur cost ke beech ka balance hota hai — har extra "nine" exponentially mehnga padta hai.

3. **Error budget nikaalo (SLO ka sabse powerful by-product):** Agar SLO 99.9% hai, to allowed failure = `100% - 99.9% = 0.1%`. Yahi 0.1% tumhara **error budget** hai. Concrete: 28-day window mein total minutes ≈ `28 × 24 × 60 = 40,320 min`. 0.1% of that = **~40.3 minutes** ka allowed downtime per 28 days. Ye budget ek currency ki tarah hai — jaise-jaise outages/errors hote hain, budget kharch hota jaata hai.

4. **Error budget se decisions chalao:** Agar budget bacha hua hai → team naye features ship kar sakti hai, risky deploys le sakti hai. Agar budget khatam → feature freeze, sirf reliability work allowed jab tak budget recover na ho. Isse "ship fast" vs "stay stable" ka tension ek objective number se settle hota hai, na ki opinion se.

5. **SLA banao (the external contract):** SLA wo subset hai jo customer ko promise kiya jaata hai, aur ismе **consequences** (refund/service credits) jude hote hain. Industry rule: **SLA hamesha SLO se loose/weaker rakho.** Agar internal SLO 99.9% hai, to public SLA shayad 99.5% promise karega — ye buffer team ko penalty se bachata hai. AWS, GCP jaise providers SLA toot-ne pe percentage-based service credits dete hain (jaise 99.0%-99.95% uptime → 10% credit).

6. **Monitor + alert:** SLIs ko continuously measure karo (Prometheus/monitoring se), SLO compliance dashboard pe dikhao, aur **error budget burn rate** pe alert lagao — jaise "agar budget 2 ghante mein 5% burn ho raha hai" to page karo. Burn-rate alerting fixed-threshold alerting se behtar hai kyunki ye SLO-aware hota hai.

## Tradeoffs & Variants

- **Kitni "nines" chahiye?** Har additional nine cost ko roughly order-of-magnitude badha deta hai (redundancy, multi-region, on-call burden). 99.9% (~43 min/month downtime) zyada-tar internal services ke liye theek hai; 99.99% (~4.3 min/month) sirf critical revenue-path services ke liye, aur 99.999% (~26 sec/month) bahut mehnga aur rarely justified. Interviewer probe karta hai: "kya tumhe itne nines chahiye, aur uski cost worth hai?"

- **Window size:** Chhota window (jaise 1-day) reactive aur noisy hota hai — ek incident poora budget kha jaata hai. Bada window (jaise 28/30-day rolling) smooth aur forgiving hota hai but slow-to-react. Rolling window vs calendar-month window: rolling fairer hai kyunki month-boundary pe budget achanak reset nahi hota.

- **Availability SLI ka denominator:** "total requests" mein kya count karein? Sirf valid requests (4xx client errors exclude karne chahiye? — debatable). Health-check traffic include na karo warna number inflate hota hai. Yahi nuance interviewer poochta hai.

- **Request-based vs time-based SLO:** Request-based (`good/total requests`) high-traffic services ke liye accurate hai. Time-based (`good minutes / total minutes`) low-traffic ya batch systems ke liye behtar, jahan ek minute mein bahut kam requests hoti hain.

- **SLA strictness vs marketing:** Loose SLA (99.5%) safe hai par competitor ke against weak dikhta hai. Tight SLA (99.99%) bechne mein impressive but penalty risk zyada. Ye business decision hai, pure engineering nahi.

## When To Use It

- **Har production service ke liye SLIs/SLOs:** Google SRE practice mein har user-facing service ka kam-se-kam ek SLO hota hai. Ye baseline reliability discipline hai.
- **Cloud/B2B products jahan SLA bikti hai:** AWS EC2 (99.99% region SLA), GCP, Azure, Stripe, Cloudflare — sab paid SLAs offer karte hain with service credits. Agar tum ek platform/API bech rahe ho, SLA expected hai.
- **Error-budget-driven release process:** Jab team ko "fast shipping" aur "stability" ke beech objective referee chahiye — error budget wahi referee ban jaata hai (Google ka classic model).
- **Multi-team dependency chains:** Jab tumhari service kisi aur internal service pe depend karti hai, uske SLO ko apne SLO budget mein factor karo (composed availability — `0.999 × 0.999 = 0.998` for two serial dependencies).

## Common Interview Gotchas

- **SLA ≠ SLO ≠ SLI — sabse common confusion:** Bahut log inhe interchangeably use karte hain. Yaad rakho: **SLI = measurement (number), SLO = internal target on that number, SLA = external contract with penalty.** Direction of strictness: **SLI ≤ measured reality, SLO stricter than SLA.** "SLA missed" matlab paisa dena, "SLO missed" matlab internal alarm + feature freeze. Galti se SLA ko internal target keh dena = red flag.

- **SLO ko 100% set karna:** Naya engineer aksar "99.999% ya 100%" bol deta hai. 100% availability impossible aur counterproductive hai — error budget zero ho jaata hai, koi deploy nahi kar sakta, aur cost infinite hoti hai. Right answer: "as low as users tolerate" — agar 99.9% pe bhi koi complaint nahi, to 99.99% pe paisa waste mat karo.

- **Error budget ko punishment samajhna:** Error budget koi failure quota nahi hai jise "use up nahi karna" — wo deliberately **spend** karne ke liye hota hai (risky-but-valuable launches pe). Budget bacha rehna matlab team shayad over-cautious hai aur fast-enough ship nahi kar rahi.

- **SLA ko SLO se tight rakhna:** Agar public SLA (99.99%) tumhare internal SLO (99.9%) se strict hai, to tum design se hi penalty pay karoge. SLA hamesha SLO se **looser** hona chahiye — ye buffer non-negotiable hai.

- **"Five nines" casually bolna:** 99.999% = ~5 min/year downtime. Iska matlab har deploy, har config change, har dependency ko us bar pe meet karna — extremely costly. Interview mein "five nines" sirf tab bolo jab justify kar sako (jaise telephony/payments core), warna ye naivety dikhata hai.

- **Averages se SLI measure karna:** "Average latency 50ms" se reliability mat judge karo — averages tail latency chhupa dete hain. Hamesha **percentiles** (p50/p95/p99) use karo. p99 latency batata hai ki worst 1% users ka experience kaisa hai, jo aksar revenue-critical users hote hain.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/reliability-ops/conceptual_quiz_sla_slo_sli.md`](../../../sysd-quizzes/reliability-ops/conceptual_quiz_sla_slo_sli.md) — `sysd-buddy quiz scaffold sla-slo-sli` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update sla-slo-sli --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — SLI → SLO → SLA ka relationship, error budget burn-down, aur "nines vs downtime" table ka interactive diagram.
