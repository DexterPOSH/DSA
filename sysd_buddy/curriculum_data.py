"""System Design roadmap — two tracks: Building Blocks, then Design Problems."""

SYSD_CURRICULUM = {
    "version": 1,
    "tracks": [
        {
            "name": "Building Blocks",
            "slug": "building-blocks",
            "order": 1,
            "categories": [
                {
                    "name": "Fundamentals & Networking",
                    "slug": "fundamentals-networking",
                    "order": 1,
                    "topics": [
                        {"name": "DNS & Request Lifecycle", "slug": "dns-request-lifecycle"},
                        {"name": "HTTP & HTTPS", "slug": "http-https"},
                        {"name": "TCP vs UDP", "slug": "tcp-vs-udp"},
                        {"name": "REST vs RPC vs GraphQL", "slug": "rest-rpc-graphql"},
                        {"name": "WebSockets & SSE", "slug": "websockets-sse"},
                    ],
                },
                {
                    "name": "Scaling & Load Balancing",
                    "slug": "scaling-load-balancing",
                    "order": 2,
                    "topics": [
                        {"name": "Vertical vs Horizontal Scaling", "slug": "vertical-vs-horizontal-scaling"},
                        {"name": "Load Balancers (L4 vs L7)", "slug": "load-balancers-l4-l7"},
                        {"name": "Reverse Proxy", "slug": "reverse-proxy"},
                        {"name": "Stateless Services & Sessions", "slug": "stateless-services-sessions"},
                    ],
                },
                {
                    "name": "Caching & CDN",
                    "slug": "caching-cdn",
                    "order": 3,
                    "topics": [
                        {"name": "Cache Strategies", "slug": "cache-strategies"},
                        {"name": "Cache Eviction (LRU/LFU)", "slug": "cache-eviction"},
                        {"name": "CDN", "slug": "cdn"},
                        {"name": "Cache Invalidation & Staleness", "slug": "cache-invalidation"},
                    ],
                },
                {
                    "name": "Databases & Storage",
                    "slug": "databases-storage",
                    "order": 4,
                    "topics": [
                        {"name": "SQL vs NoSQL", "slug": "sql-vs-nosql"},
                        {"name": "ACID vs BASE", "slug": "acid-vs-base"},
                        {"name": "Indexing", "slug": "indexing"},
                        {"name": "B-Tree vs LSM-Tree", "slug": "btree-vs-lsm"},
                        {"name": "Blob / Object Storage", "slug": "object-storage"},
                    ],
                },
                {
                    "name": "Data Distribution",
                    "slug": "data-distribution",
                    "order": 5,
                    "topics": [
                        {"name": "Replication", "slug": "replication"},
                        {"name": "Sharding & Partitioning", "slug": "sharding-partitioning"},
                        {"name": "Consistent Hashing", "slug": "consistent-hashing"},
                    ],
                },
                {
                    "name": "Consistency & Coordination",
                    "slug": "consistency-coordination",
                    "order": 6,
                    "topics": [
                        {"name": "CAP Theorem", "slug": "cap-theorem"},
                        {"name": "PACELC", "slug": "pacelc"},
                        {"name": "Quorum (R+W>N)", "slug": "quorum"},
                        {"name": "Leader Election", "slug": "leader-election"},
                        {"name": "Consensus (Raft/Paxos Overview)", "slug": "consensus-raft-paxos"},
                        {"name": "Distributed Locks", "slug": "distributed-locks"},
                    ],
                },
                {
                    "name": "Async & Messaging",
                    "slug": "async-messaging",
                    "order": 7,
                    "topics": [
                        {"name": "Message Queues", "slug": "message-queues"},
                        {"name": "Pub/Sub", "slug": "pub-sub"},
                        {"name": "Kafka Basics", "slug": "kafka-basics"},
                        {"name": "Idempotency", "slug": "idempotency"},
                        {"name": "Backpressure", "slug": "backpressure"},
                        {"name": "Event-Driven Architecture", "slug": "event-driven-architecture"},
                    ],
                },
                {
                    "name": "Reliability & Ops",
                    "slug": "reliability-ops",
                    "order": 8,
                    "topics": [
                        {"name": "Rate Limiting", "slug": "rate-limiting"},
                        {"name": "Circuit Breakers", "slug": "circuit-breakers"},
                        {"name": "Retries, Timeouts & Backoff", "slug": "retries-timeouts-backoff"},
                        {"name": "Observability (Logs/Metrics/Traces)", "slug": "observability"},
                        {"name": "SLA / SLO / SLI", "slug": "sla-slo-sli"},
                    ],
                },
            ],
        },
        {
            "name": "Design Problems",
            "slug": "design-problems",
            "order": 2,
            "categories": [
                {
                    "name": "Classic Designs",
                    "slug": "classic-designs",
                    "order": 1,
                    "topics": [
                        {"name": "Design TinyURL", "slug": "design-tinyurl"},
                        {"name": "Design a Rate Limiter", "slug": "design-rate-limiter"},
                        {"name": "Design Twitter / News Feed", "slug": "design-twitter-feed"},
                        {"name": "Design a Chat System (WhatsApp)", "slug": "design-chat-system"},
                        {"name": "Design a Web Crawler", "slug": "design-web-crawler"},
                        {"name": "Design a Notification System", "slug": "design-notification-system"},
                        {"name": "Design YouTube / Video Streaming", "slug": "design-video-streaming"},
                        {"name": "Design Uber / Nearby", "slug": "design-uber-nearby"},
                        {"name": "Design a Distributed Key-Value Store", "slug": "design-kv-store"},
                    ],
                },
            ],
        },
    ],
}
