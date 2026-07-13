# KNOWN ISSUES PASS 006

## Remaining Open Items

1. GUI TypeScript build still requires Node dependencies; `node_modules` are not bundled in the repository ZIP.
2. GUI command palette is not yet bound to `GET /api/runtime/services` or `POST /api/runtime/services/dispatch`.
3. Some internal modules may still call low-level controller/runtime methods directly for diagnostics; these must be audited and classified as guarded, diagnostic-only, deprecated, or plugin-entry.
4. C runtime still compiles with existing warnings in native/demo initializer code.
5. Backend websocket stream still emits latest packet state but does not yet stream service registry events as first-class command/event packets.

## Resolved In This Pass

- Backend runtime step route no longer uses direct `runtime_controller.run_steps()` for normal API execution.
- Unified Hash72 ledger verification is now stable under canonical JSON hashing.
