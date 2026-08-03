# Pass 205 Repair-Forward Restart Record

## Identity

- Contract: `HHS-P205-VM5184-G243-DETERMINISTIC-MULTIMODAL-CONTINUATION-GAMING-ML-H72-H216`
- Repair base: `1de3d5e1a62c89a238b7f47b7e7b47cb9644a768`
- Branch: `agent/pass205-production-runtime`
- Pull request: `#152`
- Merge target: `main`
- Policy: preserve the merged Pass 205 V1 compute/storage implementation and repair review gaps through additive governed projections.

## Committed tranches

1. `f5f7f8c5d99720748d2c9acba52b9f82bb1ba5eb` — native library freshness guard.
2. `eeb8bf8c8524ba1470acfa5dd2840480364027ea` — writable `/var/lib/hhs/pass205` deployment boundary.
3. `bb280b6fdfe668c52dfb20f0e3ecfd4ea1900a18` — singleton VM81 admission and reconstructive replay.
4. `905a18e0a99ec262ea90aa765cbf97c9fcbaea3d` — lossless uint64 HTTP transport and canonical retrieval ordering.
5. `10974bf6564b9157e09916974efe2d0382a9d1da` — trusted Pass 205 production workflow expansion.
6. `64a110e24a3d18ccc811083df411cf5e0f750fd3` — removal of the superseded temporary workflow.
7. `55340ca0dbf06c5eaf8397fb9df8d40ebf6fcb6e` — move synchronous kernel tick and event construction off the FastAPI event loop and serve bridge status from the last committed emission.
8. `ae141d822594ad5505a6966dea55f5b95dae9ad7` — move packet projection and graph ingestion off the FastAPI event loop while preserving startup receipt closure.
9. `540d05c39fa18870480b556c168b61d8340e5de8` — align full-application browser acceptance with the current explicit Application Preview tab contract.
10. `f977e836e4970c5865a8b71bd3772519c4637caf` — preserve inlineable empty starter script tags after readability formatting.
11. `d952650553c1fc46436a97eedb18cfc67eac023b` — regress calculator starter JavaScript inlining and executable behavior.
12. `90c646ca9edb7cc786254a70b0b4f5c334986591` and `c4fe8fec3d57a99ffbd2151f861049713bc4b56c` — follow the initialized Assistant drawer contract with valid Python Playwright regex matching.
13. `105fdaeba53aad5c41ae5cd1e6a71369ca1bf00a` — project production authority from the last Hash72-committed workflow emission without traversing mutable VM state on the request event loop.
14. `e34620f1b700e8e346b5072fa6ef4fe3037af90b` — bound public workflow authority/session projections, add a no-full-diagnostics and sub-64-KiB regression, and wire it into the trusted Pass 205 workflow.
15. `59875b1aeeb220bde986bc9cdf56c04ba0233cd5` — start the canonical public application before Pass 196–203 projection modules and defer those modules until receipt closure.
16. `9a5f4ae8955bc48d6ae90d8de14ffb43e235c74e` — regress receipt-first startup ordering, closed-authority prerequisites, inherited projection order, and burst-free sequential imports.
17. `ba70c804f1bab6d5535a35f342b8d6c0ebaf30ed` — retain inherited Pass 196–203 registration witnesses without restoring pre-receipt execution.
18. `3e8c51cd219d81221afcf76841933c38a21983f8` — run Pass 196 validation through the repository module path.
19. `b8f8f59e0a82739f77a784ba9209bedeaa30d4fb` — preserve the Pass 161 direct public-boot source contract while retaining deferred projection loading.
20. `7115fbe02f22e6bd72d7b41635509726f9fea569` — serialize application experience, interactive visual IDE, browser registry, and production integration so projections cannot block first interaction.
21. `8d5fc34ca11c0645a4e33cd54fe4534db824f83c` — regress visual interaction before browser and production projections.
22. `b8c5f140bf8b44634a78e80fc7add6ff6b46a821` — add an immutable deep-snapshot catalog identity guard for Pass 203.
23. `0bbfa1af9f6d99f669a731292609893ea6f8cd39` — install the Pass 203 catalog guard before public API federation.
24. `a95e7ef43586ed351c698afebd4cf3aa93ebb49a` and `7710d0f1162c39fcb1754ce81ecb4fefb26da3ee` — add focused and core-suite regressions for caller-isolated descriptors and atomic catalog refresh identity.

## Implemented repair scope

- Reject stale prebuilt Pass 205 libraries when any required C source or header is newer or missing.
- Configure production continuation state under `/var/lib/hhs/pass205/continuation.sqlite3` through a service-owned systemd drop-in.
- Preserve V1 deterministic state, projection, learning, Hash216, and SQLite behavior as the compute/storage substrate.
- Require one successful singleton VM81 runtime authority audit and Hash72 commit before a new continuation can be persisted.
- Store VM81 admission evidence and the native continuation receipt witness atomically with each new governed snapshot.
- Reject LOCKED, QUARANTINED, REJECTED, HALTED, missing-audit, and malformed-receipt authority outcomes.
- Reconstruct replay state, projection, learning features, roots, lineage, and receipt witnesses from ordered stored deltas.
- Encode uint64 state words, learning features, and XOR masks as decimal strings at the HTTP boundary while retaining exact integer internals.
- Sort compatible and rejected vector candidates canonically before retrieval identity construction and persistence.
- Expose `GET /api/runtime/continuation/transport` and bind hosted Pass 205 routes to the governed singleton through deterministic API federation order.
- Keep long synchronous kernel, event-construction, packet-projection, and graph-ingestion work outside the FastAPI event loop so runtime authority and visual integration requests remain serviceable during background continuation ticks.
- Serve runtime authority status from the last committed receipt/state emission instead of synchronously traversing mutable runtime-controller state.
- Bound public authority and workspace-session workflow projections so they never serialize expanding cognition or full-emission diagnostics.
- Preserve strict production acceptance: the browser still requires a real committed receipt and runtime-state Hash72 before classifying the runtime authority as online.
- Start the application and visual IDE before non-critical browser-registry, production-service, calibration, optimization, federation, and mainframe projections.
- Await the actual `HHSVisualIDEBoot` INTERACTIVE promise before constructing the browser object registry.
- Await browser-registry readiness before starting production service projection.
- Require production integration `phase=READY`, an online runtime authority, and a populated service registry before loading inherited Pass 196–203 projections.
- Load inherited projections in deterministic order with bounded spacing to prevent startup bursts of long-running status reads.
- Deep-snapshot the hosted Pass 203 catalog and return isolated descriptor copies so callers cannot mutate a previously hashed catalog.
- Atomically advance the Pass 203 catalog generation and hash only through explicit refresh.
- Install the Pass 203 identity guard before API router federation, keeping hosted and direct singleton reads on one catalog identity.
- Exercise the explicit preview-tab activation path before inspecting generated application frames.
- Preserve executable starter JavaScript after HTML readability normalization.
- Exercise the asynchronously initialized Assistant through its supported drawer launcher and close control.

## Changed files

- `hhs_python/runtime/__init__.py`
- `hhs_python/runtime/hhs_pass205_native_freshness_guard.py`
- `hhs_backend/production_server.py`
- `hhs_backend/runtime/hhs_pass205_governed_continuation_v2.py`
- `hhs_backend/runtime/hhs_pass205_retrieval_order_v1.py`
- `hhs_backend/runtime/live_kernel_event_bridge_v1.py`
- `hhs_backend/runtime/live_fastapi_workflow_v1.py`
- `hhs_backend/runtime/hhs_pass203_catalog_identity_guard_v1.py`
- `hhs_backend/api/a0_pass205_transport_bootstrap.py`
- `hhs_backend/api/a_pass205_governed_bootstrap.py`
- `hhs_backend/api/a_pass203_catalog_identity_bootstrap.py`
- `applications/holofractal_harmonizer/src/application-templates-runtime.mjs`
- `applications/holofractal_harmonizer/src/production-startup-coordinator.mjs`
- `applications/holofractal_harmonizer/src/public-boot.mjs`
- `applications/holofractal_harmonizer/tests/application.studio.test.mjs`
- `applications/holofractal_harmonizer/tests/production.startup.coordinator.test.mjs`
- `applications/holofractal_harmonizer/tests/public.boot.ordering.test.mjs`
- `applications/holofractal_harmonizer/ux_lab/full_application_smoke.py`
- `deployment/digitalocean/pass205_state/install.sh`
- `deployment/digitalocean/pass205_state/README.md`
- `tests/test_hhs_pass203_catalog_identity_guard_v1.py`
- `tests/test_hhs_pass203_hydrated_mainframe_v1.py`
- `bin/post_compile`
- `.github/workflows/pass196-integrated-environment.yml`
- `.github/workflows/pass205-production-runtime.yml`
- focused native-freshness, deployment, governed-continuation, transport/retrieval, bounded-authority, and catalog-identity tests.

## Validation gate

The terminal Pass 205 gate requires:

- deployment shell syntax checks;
- Python compilation for all repair surfaces;
- canonical and Pass 205 native ABI builds;
- all focused repair tests;
- the inherited exhaustive Pass 205 production suite;
- inherited Pass 205 design and GPU-translation tests;
- hosted production validation and evidence generation;
- hosted public federation binding checks;
- inherited Pass 201–204 regression tests;
- all Holofractal Harmonizer Node tests, including receipt-first and visual-interaction-first startup ordering;
- full visual application browser acceptance through the current preview-tab and Assistant-drawer workflows;
- production receipt-closure acceptance while background kernel continuation work is active;
- Pass 159, both Pass 161 architecture/finalization gates, Pass 176 stabilization, HTTPS/mobile closure, and workflow-first usability evidence.

## Current validation state

- Focused Pass 205 authority, persistence, replay, transport, retrieval, and bounded public-status tests were green on the prior repair head.
- Pass 159, both Pass 161 terminal architectures, Passes 196–201, Pass 200A/B/C, HTTPS/mobile closure, and both workflow-first usability A/B runs were green on `b8f8f59e0a82739f77a784ba9209bedeaa30d4fb`.
- The remaining browser failure on that head reached DOM content and returned the initial health, authority, product-health, and Pass 175 responses, but did not expose `HHSPass176` before the outer smoke timeout.
- Server request ordering showed browser-registry and production-integration projections began concurrently with the visual IDE. The current repair commits the visual IDE's real INTERACTIVE promise before either projection begins.
- The prior Pass 203 failure was a deterministic mismatch between the hosted status catalog hash and the direct singleton catalog hash after public startup. The current repair installs a deep immutable snapshot guard before federation and retains the original equality assertion.
- Exact-head repository-native workflows were queued but had not started when this restart record was committed; no green browser or Pass 203 terminal claim is made for the new tranche.

## Remaining work

1. Run the exact-head Pass 203 core and production validation, including hosted/direct catalog hash equality.
2. Run exact-head Pass 176, Production Harmonizer, and Full Application IDE Chromium acceptance.
3. Repair only dependency-scoped failures reported by those exact-head checks.
4. Confirm the hosted application closes runtime authority from a real committed receipt and exposes the governed singleton and lossless transport route.
5. Update PR #152 with terminal workflow and evidence identities.
6. Mark PR #152 ready and merge only after the terminal required checks are green.
7. Verify authoritative `main` and DigitalOcean guarded deployment receipts.
8. Physical GPU execution remains a separate validation boundary and is not claimed by this repair.
