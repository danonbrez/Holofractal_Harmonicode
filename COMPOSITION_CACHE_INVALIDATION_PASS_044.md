# Pass 044 — Composition Cache Invalidation

- Validates cached entries against current conformance roots before reuse.
- Rejects stale cache hits when dependency roots drift.
- Prevents the semantic DB from becoming a hidden parallel authority lane.
