# Next Pass 040 Recommendation

## Pass 040 — Carrier Read/Write Adapters and Reconstruction Protocol

Recommended scope:

1. Add concrete carrier adapters for PNG private ancillary chunks and text witness blocks.
2. Add deterministic round-trip tests: carrier -> HHFS capsule -> UDFP frame -> carrier validation.
3. Add bounded reconstruction protocol tests for ECC-only repair.
4. Add mutation audit tests proving every repair emits a new transformation record.
5. Keep JPEG/MP3/WAV as declared profiles until binary-safe adapters are implemented.

Pass 040 should implement physical read/write behavior for at least one binary carrier and one text carrier while preserving Pass 039's no-parallel-lane policy.
