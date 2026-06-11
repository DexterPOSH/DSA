# Consistent Hashing — Conceptual Quiz

<!-- Agent (sysd-quiz skill): grade the user conversationally against the Ideal
     answer for each question, then record the score with:
     `sysd-buddy progress update consistent-hashing --quiz-score N/M` -->

## Q1 (warm-up)
A consistent-hash ring has 4 nodes and ~1000 keys. You add a 5th node. Roughly how many keys move, and why is it not "almost all of them" like in modulo hashing?

**Ideal answer:**
- Only ~K/N keys move; here K/N = 1000/5 ≈ **200 keys** remap, ~800 stay put.
- New node only "steals" the keys in the arc between itself and its predecessor on the ring; every other arc is untouched.
- Contrast with `hash(key) % N`: changing N from 4 to 5 changes `hash(key) % N` for nearly every key, so ~all 1000 keys remap.
- Bonus: this small blast radius is exactly why consistent hashing avoids cache stampedes / DB overload on scaling events.

## Q2 (core)
What problem do virtual nodes (vnodes) solve, and how do they solve it?

**Ideal answer:**
- Problem: with one ring position per physical node, random placement gives uneven arc sizes → **load imbalance / hot spots**; and removing a node dumps all its keys onto a single successor.
- Fix: place each physical node at many points on the ring (e.g. A#1…A#150) — these are vnodes.
- More points → each physical node's total arc averages out (law of large numbers) → smoother, more even load.
- Bonus: on node removal, its keys spread across many successors instead of one.
- Tradeoff to mention: more vnodes = more routing/metadata to track (~100-256 per node is typical).

## Q3 (tradeoff)
How does consistent hashing differ from `hash(key) % N`, and specifically what breaks in the modulo scheme when N changes?

**Ideal answer:**
- Modulo: key→node mapping depends directly on N; assignment = `hash(key) % N`.
- When N changes (add/remove node), the modulus changes so `hash(key) % N` changes for ~all keys → near-total remap.
- Consequence: massive data movement, cache misses everywhere, possible cache stampede / backend overload.
- Consistent hashing decouples mapping from N: keys and nodes both live on a fixed ring; only the arc near the changed node is affected, so only ~K/N keys move.

## Q4 (gotcha)
Where do a key and a node each land on the ring, and how is a key assigned to a node? What role does the hash function's quality play?

**Ideal answer:**
- Both node IDs (IP/hostname) and keys are hashed by the **same hash function** into the same circular space (e.g. 0 … 2^32−1), wrapping around.
- A key is assigned to the **first node found going clockwise** from the key's position (the successor node).
- Hash function must be uniform / well-distributed (e.g. MurmurHash) so points don't cluster; clustering causes uneven arcs and hot spots even with vnodes.
- Note: cryptographic strength isn't the goal — distribution quality and speed are.

## Q5 (applied)
Name a real-world system that uses consistent hashing and describe one failure mode it can hit plus the mitigation.

**Ideal answer:**
- Valid examples: distributed cache (ring of Memcached/Redis servers), load balancers, databases like **Cassandra / Amazon DynamoDB** (partitioning + replica placement on clockwise successors), sharding layers.
- Failure mode: **hot spots** — without vnodes (or with a poor hash), one node gets a disproportionately large arc and gets overloaded; or a node removal dumps all keys onto one successor.
- Mitigation: use virtual nodes to even out arc sizes and spread redistribution; optionally weight powerful nodes with more vnodes; pick a well-distributed hash function.
