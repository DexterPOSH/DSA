# CDN

**Track:** Building Blocks
**Category:** Caching & CDN

## What It Is

CDN (Content Delivery Network) ek geographically distributed network of edge servers hai jo content (static files, media, ya cached dynamic responses) ko user ke physically closest server se serve karta hai, taaki latency kam ho aur origin server ka load ghate.

## Real-World Analogy

Socho ek popular book publisher Mumbai mein hai (ye hamara **origin server** hai). Agar Chennai, Delhi, aur Kolkata ke har reader ko book seedhe Mumbai warehouse se courier karni pade, to har order mein 3-4 din lagenge aur Mumbai warehouse overload ho jaayega.

Iske badle publisher har bade sheher mein ek **local bookstore** khol deta hai (ye **edge servers / PoPs** hain). Pehli baar jab Chennai ka koi reader book maangta hai, local bookstore Mumbai se ek copy mangwa ke apne shelf pe rakh leta hai (**cache fill / origin fetch**). Ab Chennai ke baaki saare readers wahi book apne local bookstore se 1 din mein paa lete hain — Mumbai ko baar-baar disturb nahi karna padta.

Har book ke cover pe ek "best before" date hoti hai (**TTL**). Jab wo expire ho jaati hai, bookstore Mumbai se confirm karta hai ki nayi edition aayi ya wahi chalegi. Yahi CDN ka core idea hai: content ko user ke paas le jao, origin ko sirf cold misses ke liye bachao.

## How It Works

1. **DNS-based routing:** User `cdn.example.com` ke liye DNS query karta hai. CDN ka authoritative DNS (ya Anycast IP) user ke resolver location ke hisaab se uske **nearest edge PoP** (Point of Presence) ka IP return karta hai. Bade CDNs ke 300+ PoPs hote hain duniya bhar mein. Result: user ek faraway origin (jaise cross-continent ~150-250 ms RTT) ki jagah nearby edge (~5-30 ms RTT) hit karta hai.

2. **Cache lookup (HIT vs MISS):** Edge server request ka **cache key** banata hai (usually URL + kuch headers jaise `Accept-Encoding`). Agar object cache mein fresh hai → **cache HIT**, edge directly serve kar deta hai, often <10 ms mein. Agar nahi → **cache MISS**.

3. **Origin fetch on miss:** Miss pe edge content origin se fetch karta hai (often ek **shield / mid-tier cache** ke through, taaki saare edges seedhe origin ko na hammer karein). Object ko cache karke user ko bhej deta hai. Pehla user "warm up" pay karta hai (full origin RTT), baaki sab edge se fast paate hain.

4. **Freshness via TTL & validation:** Origin `Cache-Control: max-age=3600` jaise headers se batata hai object kitni der fresh hai. TTL expire hone pe edge object ko stale maan leta hai, aur origin se `If-None-Match` (ETag) / `If-Modified-Since` ke saath **revalidate** karta hai. Agar unchanged → origin `304 Not Modified` bhejta hai (no body, bandwidth bachta hai), edge TTL refresh kar deta hai.

5. **Cache hit ratio:** CDN ki effectiveness ka key metric. 95% hit ratio matlab sirf 5% requests origin tak pahunchti hain — agar site 100k QPS le rahi hai, to origin sirf ~5k QPS dekhta hai. Ye origin offload hi CDN ka sabse bada scalability win hai.

6. **Invalidation / purge:** Jab content turant badalna ho (jaise galat price publish ho gaya), origin TTL expire hone ka wait nahi kar sakta. CDN ek **purge API** deta hai jo edges ko object evict karne ka signal bhejti hai — global purge usually seconds-to-minutes mein propagate hoti hai.

## Tradeoffs & Variants

- **Static vs dynamic content:** CDN classic strength static assets (JS, CSS, images, video) pe hai — ye highly cacheable hain. Dynamic/personalized responses (jaise logged-in user ka feed) by default cacheable nahi, par modern CDNs **edge compute** (Cloudflare Workers, Lambda@Edge, Fastly Compute) se dynamic logic edge pe chala sakte hain.

- **TTL length ka tradeoff:** Long TTL → zyada hit ratio, kam origin load, par stale content ka risk (users purani copy dekh sakte hain). Short TTL → fresher content par zyada origin traffic aur revalidation. Common pattern: **immutable versioned assets** (`app.a1b2c3.js`) ko long/`immutable` TTL do, aur HTML jaise frequently-changing cheez ko short TTL.

- **Push vs Pull CDN:** **Pull** (lazy) — edge content origin se on first miss khींchta hai; setup simple, par pehla user slow. **Push** — aap content proactively edges pe pre-load karte ho (jaise ek big launch / VOD release se pehle); control zyada par operationally heavy.

- **Cache key design:** Bahut narrow key (sirf URL) → personalized content galat user ko serve ho sakta hai (cache poisoning of correctness). Bahut wide key (har header include) → cache fragmentation, hit ratio gir jaata hai. `Vary` header aur query-string handling carefully tune karna padta hai.

- **Cost & complexity:** Egress bandwidth aur requests ka billing hota hai, plus purge/config ki operational overhead. Chhoti low-traffic site ke liye CDN overkill ho sakta hai.

## When To Use It

- **Static asset & media delivery:** Images, video, JS/CSS bundles globally serve karna — har consumer web app (e.g. Netflix Open Connect video, YouTube, Amazon CloudFront) isi pattern pe.
- **Global user base + latency-sensitive UX:** Agar users multiple continents pe hain, edge proximity se p95 latency drastically girti hai.
- **Origin offload / DDoS absorption:** Traffic spikes (flash sale, viral content) ya volumetric DDoS ko CDN edge layer absorb kar leta hai before origin ko hit kare — Cloudflare/Akamai is liye bhi famous hain.
- **Live & on-demand video streaming:** HLS/DASH segments ko edge pe cache karke millions ko scale karna.
- **Real systems:** Cloudflare, Akamai, AWS CloudFront, Fastly, Google Cloud CDN, Netflix Open Connect. Interview mein "globally low latency + high read scale" sunte hi CDN ko first-class building block ke roop mein propose karo.

## Common Interview Gotchas

- **"CDN sirf static content ke liye hai" — galat:** Ye purana view hai. Edge compute aur micro-caching (kuch seconds ka TTL bhi) se dynamic aur even API responses partially CDN se serve ho sakti hain. Micro-caching ek 1-second TTL bhi origin QPS ko dramatically gira sakta hai jab traffic high ho.

- **TTL aur invalidation ko confuse mat karo:** TTL ek **passive expiry** hai (object apne aap stale ho jaata hai). Purge/invalidation ek **active push** hai jo edges ko turant evict karwati hai. Interviewer poochega "user ko purana data dikh raha hai, kaise fix karoge" — answer dono ka combo: sensible TTLs + versioned URLs + targeted purge.

- **Cache hit ratio is the metric, not just "CDN lagaya":** Bina hit ratio measure kiye CDN ka value claim mat karo. Low hit ratio (jaise har URL unique query params ke saath) matlab CDN bypass ho raha hai aur origin abhi bhi overloaded. Cache key design directly hit ratio drive karta hai.

- **DNS routing ≠ exact geo:** CDN often user ke **DNS resolver** ki location se route karta hai, user ki actual location se nahi. Agar user public resolver (jaise 8.8.8.8) use kare to suboptimal PoP mil sakta hai. EDNS Client Subnet aur Anycast is gap ko reduce karte hain.

- **Stale-while-revalidate ko miss mat karo:** Achhe CDNs `stale-while-revalidate` support karte hain — expire hone ke baad bhi stale copy turant serve karte hue background mein revalidate karte hain, taaki user ko latency spike na dikhe. Ye availability + freshness ka smart balance hai.

- **Edge ≠ origin replacement:** CDN cache layer hai, source of truth nahi. Write/personalization/transactions ab bhi origin handle karta hai. Cache miss storm (mass TTL expiry ek saath) origin ko gira sakta hai — isiliye TTL jitter aur shield/mid-tier cache use karte hain.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/caching-cdn/conceptual_quiz_cdn.md`](../../../sysd-quizzes/caching-cdn/conceptual_quiz_cdn.md) — `sysd-buddy quiz scaffold cdn` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update cdn --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — origin, edge PoPs, DNS routing, aur cache HIT/MISS flow ka interactive diagram.
