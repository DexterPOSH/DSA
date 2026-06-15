# Cache Invalidation & Staleness — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update cache-invalidation --quiz-score N/M` -->

## Q1 (warm-up)
Cache "staleness" se aapka kya matlab hai, aur "cache invalidation" usse kaise related hai? Define both in one or two sentences.

**Ideal answer:**
- Staleness = woh window/condition jab cache mein rakhi copy source-of-truth se purani (mismatched) ho jaati hai, kyunki source update ho gaya par cache abhi tak nahi.
- Cache invalidation = woh mechanism jo us stale copy ko remove ya refresh karta hai (delete/expire/overwrite) taaki readers ko latest data mile.
- Bonus: invalidation staleness window ko close karne ka tool hai; goal hai acceptable staleness ke andar rehna while keeping a high hit ratio.

## Q2 (core)
Ek TTL-based cache mein, TTL value aur staleness window ka exact relationship kya hai? Aur ek read request TTL expiry ke time pe step-by-step kya hota hai?

**Ideal answer:**
- TTL hi worst-case staleness window define karta hai: source change hone ke baad readers up to TTL seconds tak purana data dekh sakte hain.
- Mechanics: read aata hai → entry ka stored expiry timestamp check hota hai → agar `now > expiry`, miss treat hota hai → source-of-truth se fresh value fetch → cache mein naye expiry ke saath re-store → value return.
- Tradeoff articulate kare: chhota TTL = kam staleness par zyada misses/DB load; bada TTL = ulta.
- Strong answer: TTL ek backstop/safety net hai even jab explicit invalidation use ho rahi ho.

## Q3 (tradeoff)
Write hone pe cache ko "delete (invalidate)" karna vs "update (overwrite with new value)" — dono ke tradeoffs samjhao. Aap default kaunsa choose karoge aur kyun?

**Ideal answer:**
- Delete-on-write: safer — agla read miss hokar source-of-truth se latest laata hai, isliye concurrent writers ka stale value cache mein nahi rehta. Cost: ek extra cache miss (latency + DB hit).
- Update-on-write: faster — agla read hit karega. Risk: concurrent writes ke beech race se ek purana value cache mein likh sakta hai (out-of-order writes), causing persistent staleness.
- Default usually delete-on-write (cache-aside ke saath) kyunki correctness > ek miss ki cost; high-read-fanout hot keys ke liye update consider kar sakte hain.
- Mention: ordering matters — "update DB, then delete cache".

## Q4 (gotcha)
Cache-aside pattern mein ek classic race condition hai jo cache ko persistently stale chhod sakti hai. Use describe karo, aur batao "DB update karo phir cache delete karo" kyun "cache delete karo phir DB update karo" se behtar hai.

**Ideal answer:**
- Bad order (delete cache → update DB): delete ke baad par DB-update se pehle, ek concurrent reader purani DB value padh leta hai aur cache ko re-populate kar deta hai → ab cache stale rehta hai jab tak agla write/TTL na aaye.
- Better order (update DB → delete cache): pehle source-of-truth latest ho jaata hai; jab cache delete hota hai, koi bhi subsequent read fresh value laata hai.
- Acknowledge: ye bhi perfectly race-free nahi hai (read-miss + slow repopulate window), isliye real fixes: short TTL safety net, delayed double-delete, ya single-flight.
- Naming the broader truth: invalidation best-effort hai, isliye TTL backstop zaroori.

## Q5 (applied)
Aap ek high-traffic e-commerce product page design kar rahe ho. Ek hot product (millions of views/day) ka price har kuch ghanton mein badalta hai, aur price hamesha sahi dikhna zaroori hai. Aap caching + invalidation strategy kaise design karoge, aur thundering herd se kaise bachoge?

**Ideal answer:**
- Cache-aside with Redis/Memcached aage of DB; price field ke liye chhota TTL (e.g. seconds-to-low-minutes) acceptable staleness ke hisaab se, plus **explicit invalidation on price-change event** (event-driven / CDC) taaki staleness window aur chhota ho.
- Correctness: write path pe "update DB → invalidate cache" order; invalidation ko best-effort maan ke TTL backstop rakho.
- Thundering herd / stampede mitigation hot key par: **request coalescing / single-flight** (ek request fetch kare, baaki wait karein), **stale-while-revalidate** (purana serve karo jab tak naya aaye), aur **early/probabilistic expiry refresh** taaki sab ek saath expire na ho.
- CDN/edge: page HTML ko short-TTL ya ESI/fragment caching; price jaisa dynamic part alag se fetch ya versioned.
- Strong answer: acceptable staleness ko explicitly product ke saath confirm karega, aur mention karega ki "price must look correct" → invalidation event + short TTL, not just a long TTL.
