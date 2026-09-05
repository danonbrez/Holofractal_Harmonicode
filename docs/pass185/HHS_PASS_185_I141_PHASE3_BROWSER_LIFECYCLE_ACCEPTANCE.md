# HHS Pass 185 I141 Phase 3 — Browser Lifecycle Acceptance

Classification:

`HHS_PASS_185_PHASE3_BROWSER_LIFECYCLE_VERIFIED`

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

## Final Phase-3 validation

Phase 3 is terminal green at:

- validated head: `beff7599dedff2624be712f7a215de5c193e8cbe`
- validated tree: `b20f7834ff439b3fe8f8e3bae3216da7744918e4`
- workflow run: `33294510153`
- job: `99211758381`
- artifact: `9727030968`
- artifact SHA-256: `6b02d7c0e5677cc13cf7cb75cb3885714a263fe63af30223ddf6fee4cdc472f9`
- evidence JSON SHA-256: `5caf404779f382b70735461a2fdd5009bbae579ff5fc883e6abd95af98e5ed1f`
- seal receipt SHA-256: `db3e973aaf182bf53675210cb92b541659a5669c9f84ede52cae323e8aa99f95`
- repository receipt: `evidence/pass185/i141/PASS_185_I141_PHASE3_VALIDATION_RECEIPT.json`

The exact production composition was reconciled to `bootstrap.ts -> main.tsx -> IntegratedRuntimeClient -> CanonicalRuntimeIDE -> HHSProductWorkspace`. The final gate verified on-demand four-channel Runtime transport, backend stop/restart reconnect, browser offline/online recovery, listener deduplication, localStorage-unavailable local operation, repeated mount/unmount and reload behavior, independent concurrent browser contexts, and retained production-root regressions.

Phase 3 still does **not** claim terminal Pass 185 completion.
