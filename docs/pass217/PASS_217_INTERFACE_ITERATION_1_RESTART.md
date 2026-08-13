# Pass 217 Interface Integration — Iteration 1 Restart Record

## Authority

- Parent branch: `agent/pass217-iteration4-authority-reconciliation`
- Parent commit: `724e91c5fb1009cefc52778c3e73338257b2814c`
- Parent tree: `cdffca6979db12b4a0bfac45db20599132453ed0`
- Scope: `hhs_gui` frontend instrumentation only.
- Pass 217 backend/runtime authority modified: **no**.
- `IntegratedRuntimeClient`, `RuntimeSocketManager`, runtime/replay/graph/transport endpoints, Pass 217 contracts, evidence, and candidate artifacts remain unchanged.

## Implemented

1. Shared browser frame telemetry under `hhs_gui/runtime_os/telemetry/FrameTelemetry.ts`.
   - One RAF sampler shared by all frontend consumers.
   - 500 ms publication cadence to avoid telemetry-driven rerender pressure.
   - FPS, median refresh estimate, p50/p95/p99 frame time, jank, long-frame, and dropped-frame diagnostics.
   - Hidden-tab suspension is excluded from frame-health calculations.

2. Global frontend fetch latency instrumentation under `FetchLatencyTelemetry.ts`.
   - Idempotent patch state stored on `window`, preventing wrapper stacking during HMR/remount.
   - Correct method resolution for `Request` objects.
   - GET coalescing identity includes credentials and response-affecting headers including Authorization.
   - Every coalesced GET consumer receives its own `Response.clone()`.
   - Endpoint p50/p95/mean/error/status snapshots and in-flight request count are observable.

3. React adapter and visible interface diagnostics.
   - `useFrontendTelemetry.ts` bridges the singleton monitors with `useSyncExternalStore`.
   - `FrontendTelemetryBadge.tsx` exposes FPS, estimated refresh Hz, frame p95, in-flight requests, and slowest observed API p95.
   - `CanonicalRuntimeIDE.tsx` mounts the badge as a pointer-transparent diagnostic overlay without changing runtime transport authority.

4. Repository-visible verification.
   - Added `hhs_gui/scripts/frontend-telemetry-source-verify.mjs`.
   - Added `npm run test:frontend-telemetry:source`.

## Validation before remote publication

Completed locally against the exact source intended for the Git tree commit:

- strict TypeScript compilation of the pure frame and fetch telemetry modules;
- TSX/React syntax transpilation of the hook, badge, and modified canonical IDE;
- deterministic frame summarizer assertions for stable 60 Hz and injected jank;
- fetch instrumentation assertions for idempotency, Request POST classification, auth-isolated GET coalescing, and independent cloned response bodies;
- repository source-verification script.

No backend validation is required for this checkpoint because no backend, Pass 217 contract, evidence, runtime, or transport file is changed.

## Next iteration

Expand the same shared telemetry into the Service Registry and workspace/IDE application organization while preserving the current runtime client and on-demand socket model. Validate each frontend increment and checkpoint it to this remote branch rather than retaining uncommitted local-only work.
