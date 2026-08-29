# HHS Pass 185 I141 Phase 3 — Browser Lifecycle Acceptance

Classification:

`HHS_PASS_185_PHASE3_BROWSER_LIFECYCLE_ACCEPTANCE_IMPLEMENTED_PENDING_VALIDATION`

Terminal Pass 185 completion is **not** claimed.

## Scope

This bounded Phase-3 block extends the already verified Phase-1 application lifecycle and Phase-2 degradation/negative acceptance with real-browser transport and persistence lifecycle evidence against the exact production entrypoint:

`hhs_backend.runtime_os_application_server:app`

The block verifies:

- on-demand ownership of the public-root `IntegratedRuntimeClient` while the Runtime surface is mounted;
- WebSocket disconnect when the production backend is stopped;
- finite reconnect after restart on the same production port;
- browser offline then online recovery;
- repeated Runtime/Application navigation alternating exactly between dormant zero-subscription state and one subscription per channel;
- full page reload from a dormant public client to a single four-channel subscription set after Runtime mount;
- local calculator edit/preview/test/ZIP while the backend is unavailable;
- local calculator edit/preview/test/ZIP while the browser is offline;
- explicit localStorage-unavailable degradation while the in-memory application remains usable;
- isolated local application state across two independent browser contexts;
- canonical backend save/witness only through the inherited workspace command ingress;
- no browser or Python replacement runtime authority.

## Repair-forward changes

### Production transport lifecycle ownership

The exact production bootstrap is `hhs_gui/bootstrap.ts -> hhs_gui/main.tsx`.

`main.tsx` constructs one `IntegratedRuntimeClient`, exposes the existing read-only diagnostic handle as `window.__HHS_RUNTIME_CLIENT__`, and mounts `CanonicalRuntimeIDE`.

`LiveRuntimeProjectionPanel` owns the intended on-demand projection lifecycle: mounting the Runtime surface invokes `IntegratedRuntimeClient.initialize()`; unmounting it invokes `IntegratedRuntimeClient.shutdown()`. Ordinary editing/application work therefore carries no live WebSocket subscription set.

The earlier Phase-3 exploratory changes to the unused `src/App.tsx -> RuntimeShell -> RuntimeOS` entry path were restored to their pre-Phase-3 blobs after this production-entrypoint reconciliation.

### Reconnect deduplication

`RuntimeSocketManager` now keeps one pending reconnect timer per channel. Repeated close/error paths cannot accumulate duplicate reconnect attempts. Shutdown clears every pending reconnect timer.

Read-only metrics expose:

- connected WebSocket channel count;
- projection subscription count;
- pending reconnect channels.

These metrics do not derive or mutate runtime truth. The gate cross-checks them against the already exposed `window.__HHS_RUNTIME_CLIENT__.getMetrics()` diagnostic handle.

### Local persistence unavailable

The Pass-185 application lifecycle catches localStorage write failures and surfaces:

`LOCAL_STORAGE_UNAVAILABLE_LOCAL_SESSION_ACTIVE`

The editor/preview/test/export path remains available in memory. No canonical persistence, Hash72 receipt, VM81 state, or backend save is fabricated.

## Validation surface

Runner:

`hhs_verification/pass185/phase3_browser_lifecycle_acceptance.py`

Workflow:

`.github/workflows/pass219-i141-pass185-phase3-browser-lifecycle.yml`

Expected evidence directory:

`/tmp/pass185-phase3`

The workflow builds the inherited compiled C authority, typechecks/builds the Runtime OS, runs real Chromium, executes the Phase-3 browser lifecycle, reruns impacted production-root regressions, and seals an artifact.

## Authority boundary

Phase 3 preserves:

- `frontend_runtime_authority: false`;
- `browser_replacement_authority: false`;
- backend runtime/Hash72/VM81 authority unchanged;
- application-local editing/preview/export as non-authoritative browser behavior;
- save/witness only through inherited workspace command ingress.

Phase 3 must remain pending until one exact branch head passes the full workflow.
