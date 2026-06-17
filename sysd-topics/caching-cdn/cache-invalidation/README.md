# Cache Invalidation & Staleness

**Track:** Building Blocks
**Category:** Caching & CDN

## What It Is

Cache invalidation woh process hai jisse ek cached copy ko remove ya update kiya jaata hai jab underlying source-of-truth data badal jaata hai, taaki readers ko stale (purana) data na mile — aur staleness us time-window ko kehte hain jiske dauraan cache aur source-of-truth ke beech mismatch reh sakta hai.

## Real-World Analogy

Socho ek office ke notice board (cache) pe canteen ka menu chipka hua hai, aur asli menu canteen ki kitchen (source-of-truth / database) mein decide hota hai. Log fast access ke liye board dekh lete hain — kitchen tak jaane ki zaroorat nahi. Ye fast hai, par ek problem hai: jis din kitchen menu change karti hai, agar koi board update na kare to log purana menu padh ke "paneer" maangte rahenge jo aaj hai hi nahi. Yahi **staleness** hai.

Ab board ko sync karne ke teen tareeke hain. Pehla: board pe likh do "ye menu sirf aaj subah 10 baje tak valid hai" — 10 baje ke baad koi bhi reader ise expired maan ke khud kitchen se naya menu le aata hai. Ye **TTL** hai. Doosra: jaise hi kitchen menu badle, ek banda bhaag ke board ka purana parcha phaad de — agle reader ko board khaali milega aur wo fresh kitchen se laayega. Ye **invalidation on write** hai. Teesra: kitchen menu badalte hi turant naya parcha khud board pe chipka de. Ye **write-through / refresh** hai. Cache invalidation poori is baat ka khel hai ki board aur kitchen ke beech ka gap kitna bada ho sakta hai, aur use kab aur kaise band karein.

## How It Works

Cache ek read-mostly fast layer hai (RAM ya CDN edge) jiska latency ~0.2–2 ms hota hai, jabki source DB ka read 10–50 ms le sakta hai. Goal: zyादातर reads cache se serve karna (high hit ratio, jaise 90–99%) bina readers ko galat data diye. Invalidation ke main approaches:

1. **TTL-based expiry (passive):** Har cache entry ke saath ek expiry timestamp store hota hai (jaise TTL = 60s). Read aane pe agar `now > expiry`, to entry ko miss maana jaata hai, source se fresh value laayi jaati hai, aur dobara cache hoti hai. Yahaan staleness window TTL ke barabar hai — TTL 60s matlab worst case 60s tak readers purana data dekh sakte hain. Chhota TTL → kam staleness par zyada DB load (zyada misses); bada TTL → kam DB load par zyada staleness.

2. **Explicit invalidation on write (active):** Jab koi writer source data update kare, wo cache ko bhi signal bhejta hai. Do flavors:
   - **Delete/invalidate:** Cache key ko delete kar do (`DEL user:42`). Agla read miss karega aur fresh value laayega. Ye safe hai kyunki agle read pe hamesha source se latest aata hai.
   - **Update/refresh:** Cache key ko naye value se overwrite kar do. Fast (agla read hit karega), par race conditions ka risk zyada hai (concurrent writers ka stale value likh dena).

3. **Write policies:**
   - **Write-through:** Write pehle cache mein jaata hai, phir synchronously source mein — cache aur source hamesha consistent, par write latency badhti hai.
   - **Write-back (write-behind):** Write sirf cache mein, source ko async update — fast writes par crash pe data loss ka risk.
   - **Write-around:** Write seedha source mein jaata hai, cache ko bypass karke; cache sirf reads pe (lazily) populate hota hai — write-heavy keys ke liye accha jo padhe nahi jaate.

4. **CDN / edge invalidation:** CDN pe content thousands of edge POPs pe cached hota hai. Invalidation do tarah se: **purge** (sab edges ko bolo ye URL ka object hata do — propagate hone mein seconds-to-minutes lagte hain) ya **versioned URLs / cache-busting** (file ka naam hi badal do, jaise `app.v2.js` ya `app.abc123.js`, taaki naya URL ek brand-new object ban jaaye aur purana naturally expire ho jaaye). Versioning aksar purge se behtar hai kyunki ye instant aur globally consistent hai.

5. **Event-driven invalidation:** Bade systems mein DB change (CDC — change data capture, jaise Debezium reading the binlog) ek event stream (Kafka) pe publish hota hai, aur consumers affected cache keys ko invalidate karte hain. Ye decoupled hai par invalidation propagation latency (event lag) introduce karta hai.

## Tradeoffs & Variants

- **Staleness vs load (the core knob):** TTL chhota karo to data fresh rehta hai par cache miss rate aur backend QPS badhta hai. TTL bada karo to backend bachta hai par staleness window badhta hai. Interviewer yahaan poochega "is data ke liye acceptable staleness kitna hai?" — pricing/inventory ke liye seconds, ek user profile pic ke liye minutes-to-hours chal jaata hai.

- **Invalidate (delete) vs update (overwrite):** Delete-on-write zyada safe hai (next read source-of-truth se laata hai, koi stale write nahi), par ek extra cache miss cost karta hai. Update-on-write fast hai par concurrent-write race conditions mein stale value cache mein chhod sakta hai.

- **Cache-aside vs write-through ordering:** Cache-aside (lazy loading) sabse common hai par ek classic race hai — "update DB then delete cache" vs "delete cache then update DB". Galat ordering pe ek concurrent reader purana value re-populate kar sakta hai. Industry-standard fix: **update DB, phir delete cache** (Cache-Aside), aur edge races ke liye **delayed double-delete** ya short TTL as a safety net.

- **Strong vs eventual consistency:** Strong consistency chaahiye to write-through + synchronous invalidation, par har write slow ho jaata hai aur availability girti hai. Zyadatar web systems eventual consistency choose karte hain (TTL + best-effort invalidation) kyunki seconds ki staleness acceptable hai.

- **Purge vs versioning (CDN):** Purge explicit par propagation slow aur eventually-consistent across POPs. Versioned URLs instant aur consistent par har deploy pe naye URLs generate karne ki machinery chahiye.

## When To Use It

- **Read-heavy, tolerant-of-staleness data:** Product catalog, user profiles, rendered HTML, feed — jahaan read:write ratio bahut high hai aur thodi staleness chalti hai.
- **Database read offloading:** Jab DB read QPS bottleneck ban raha ho, ek cache layer (Redis/Memcached) aage lagao — par tabhi jab aap invalidation strategy decide kar lo.
- **CDN static/semi-static assets:** JS/CSS/images/videos ke liye versioned-URL invalidation; news/article pages ke liye purge-on-publish.
- **Real systems:** Facebook ka **TAO** + **Memcache** (cache-aside + invalidation via the DB tier), Twitter timelines (fan-out cache), **Cloudflare/Akamai/Fastly** CDNs (Fastly instant-purge ~150ms ka dawa karta hai), Netflix **EVCache**. Stack Overflow famously Redis ke saath aggressive caching + targeted invalidation use karta hai.

## Common Interview Gotchas

- **"Cache invalidation is one of the two hard things in CS" — par WHY hard hai:** Hardness consistency aur concurrency se aati hai. Source aur cache do alag systems hain; unke beech har update atomic nahi hai, isliye races aur partial failures inevitable hain. Naam yaad rakhna kaafi nahi — interviewer specific race ya failure mode poochega.

- **Delete-then-update DB race:** Agar aap pehle cache delete karo phir DB update karo, to beech mein ek reader purani DB value padh ke cache ko re-populate kar sakta hai — ab cache permanently stale (next write tak). Sahi order: **DB update karo, phir cache delete karo** (still imperfect, isliye short TTL safety net).

- **TTL = staleness, ye direct relationship samajhna:** Log aksar bhool jaate hain ki TTL hi worst-case staleness window define karta hai. TTL 300s matlab ek reader 5 minute purana data dekh sakta hai even after the source changed.

- **Thundering herd / cache stampede:** Ek popular key expire ya invalidate hote hi hazaaron concurrent reads ek saath miss ho ke DB pe tut padte hain. Fix: **request coalescing / single-flight** (ek hi request source se laaye, baaki wait karein), **early/probabilistic refresh** (expiry se thoda pehle background mein refresh), ya **stale-while-revalidate** (purana serve karte raho jab tak naya aaye).

- **Invalidation is best-effort, not guaranteed:** Network drop, consumer lag, ya partial failure pe invalidation miss ho sakta hai — isiliye TTL ko hamesha ek backstop ke roop mein rakho, "main only invalidation events" pe blindly bharosa mat karo.

- **Distributed cache fan-out:** Ek logical entity multiple cache keys ya multiple cache nodes pe ho sakti hai (jaise denormalized views). Ek write pe saare dependent keys invalidate karna — ye dependency tracking interview mein deep-dive ka topic hai.

## Practice

- Conceptual quiz: [`../../../sysd-quizzes/caching-cdn/conceptual_quiz_cache_invalidation.md`](../../../sysd-quizzes/caching-cdn/conceptual_quiz_cache_invalidation.md) — `sysd-buddy quiz scaffold cache-invalidation` se generate hota hai; grade hone ke baad score record karo with `sysd-buddy progress update cache-invalidation --quiz-score N/M`.
- Visual: `visual.html` (same folder mein) — TTL expiry, write-on-invalidate flow, aur cache-aside race condition timeline ka interactive diagram.
