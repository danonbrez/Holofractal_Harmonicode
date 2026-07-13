# Pass 043 — Metadata Eviction Report

Validated expanded metadata is evicted after compaction. Persistent runtime records retain compact roots, bounded summaries, and reconstruction recipes rather than full graph copies or raw expanded traces.
