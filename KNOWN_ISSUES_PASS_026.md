# Known Issues — Pass 026

## Direct Plugin Execution Still Blocked

This is intentional. Pass 026 executes the semantic adapter runtime only. Candidate plugin modules remain non-imported and non-executed.

## Closure Harness Coverage Required

Before any candidate module can be considered for direct execution, it must have:

- explicit semantic adapter schema,
- closure-harness coverage,
- rollback behavior,
- IO/Hash72/u^72 witness compatibility,
- foundational conformance checks,
- explicit allowlist approval.

## Full GUI Surface Not Yet Added

The adapter runtime is service-reachable, but dedicated GUI/API views for plugin adapter execution records remain a later pass target.
