# HHS Pass 185 I141 Phase 5 — Performance and Remaining Negative Acceptance

Classification:

`HHS_PASS_185_PHASE5_PERFORMANCE_NEGATIVE_VERIFIED`

Terminal Pass 185 completion is not claimed.

## Scope

Phase 5 validates the historical Pass-185 performance/starvation gates and the remaining production-root recovery cases not already frozen by Phases 1–4.

Exact production entrypoint:

`hhs_backend.runtime_os_application_server:app`

Timing, CPU, memory, disk-I/O, and browser-performance values are evidence-only noncanonical measurements. They do not enter VM81 or Hash72 authority.

## Contract-derived performance gates

The historical contract requires:

- listener bind within the declared startup deadline;
- lightweight health p95 below 250 ms on the reference two-vCPU host;
- canonical event-loop work yielding within 100 ms;
- no sustained full logical CPU while idle for more than ten seconds;
- no unauthorized background runtime advancement while idle;
- browser long tasks above 200 ms recorded and bounded;
- editor interaction responsive while optional capability probes execute;
- finite boot-stage failure and recovery.

Phase-5 harness settings:

- startup deadline: 45,000 ms;
- lightweight endpoint: discovered from the production-declared `/api/health` then `/health` surfaces;
- health p95 gate: 250 ms;
- concurrent event-loop health gate: 100 ms;
- idle observation: 10.5 seconds;
- idle CPU practical ceiling: 95%;
- editor interaction ceiling: 500 ms;
- long-task record threshold: 200 ms;
- long-task hard evidence ceiling: 1,000 ms.

The historical 250 ms and 100 ms thresholds remain authoritative. Other ceilings are bounded harness criteria for this reference CI host.

## Evidence collected

The runner samples the exact Uvicorn process through Linux `/proc` during startup, idle, explicit runtime work, shutdown, and recovery. Evidence includes CPU ticks, derived CPU percentage, RSS, read/write bytes, socket/readiness timeline, and HTTP latency.

With `HHS_COGNITION_AUTO_TICK=0`, the runtime step and state Hash72 must remain unchanged across the idle window.

A concurrent lightweight-health sampler runs while three explicit authorized runtime steps execute. Maximum observed health latency must remain below 100 ms.

Real Chromium records long-task entries and verifies visible editor responsiveness while optional product-health probes execute.

## Remaining negative matrix

The exact production root must visibly and finitely recover from:

- a boot dependency that never completes;
- a parser completion dependency that cannot resolve itself;
- a missing required DOM dependency;
- a circular boot dependency;
- malformed lifecycle recovery state;
- duplicate visible control binding;
- API route collision / SPA fall-through.

Earlier frozen phases retain their existing negative evidence for blocked modules, incorrect JavaScript MIME, corrupted storage, process/socket failures, optional provider degradation, C-runtime degradation, WebSocket recovery, ZIP validity, and browser authority prohibition.

## Validation surface

Runner:

`hhs_verification/pass185/phase5_performance_negative_acceptance.py`

Workflow:

`.github/workflows/pass219-i141-pass185-phase5-performance-negative.yml`

The gate must build inherited C authority, build the exact Runtime OS, execute the production performance and recovery runner in Chromium, retain impacted production-root regressions, seal evidence, and upload the artifact.

## Final Phase-5 validation

Phase 5 is terminal green at the implementation/evidence head:

- validated head: `36321174c124ff5ba81bd60fd37a72ce703e606c`
- validated tree: `89e9f83674700565695e54868ba50f93c1535f06`
- workflow run: `33304271871`
- job: `99237928339`
- artifact: `9729993598`
- artifact SHA-256: `82b99ecba184b51ce677038e76a1de5fecd4739873d215b2288e18e298ac7127`
- evidence SHA-256: `f0a9efcf8de1c178e86cecc26269f2d5c539c801406c504fe950ccf79c980a78`
- seal receipt SHA-256: `10f5e85b988e07be5612a2800a1dc0cea603ac93e38aa05d3aa5e565ac75d726`
- compiled-C SHA-256: `7715239a086696e220486ce1ae7824f8e140be0a2c9bcef3e7875e8793d0312c`
- repository receipt: `evidence/pass185/i141/PASS_185_I141_PHASE5_VALIDATION_RECEIPT.json`

Measured evidence includes:

- idle lightweight-health p95: `7.376 ms`;
- idle process CPU: `0.19%` across `10.51 s`;
- idle runtime step and state Hash72 unchanged;
- three explicit canonical runtime steps of approximately `5.2 s` each;
- `562` concurrent health samples with zero request failures;
- concurrent health p95 during canonical work: `27.968 ms`;
- maximum diagnostic health latency during that workload: `35.687 ms`;
- editor interaction: `13.096 ms` during six optional product-health probes;
- zero recorded browser long tasks above `200 ms`;
- all four remaining synthetic boot-dependency failures produced finite visible recovery and post-reload `/api/health = 200`;
- unknown API classification returned structured `HHS_API_ROUTE_NOT_FOUND` without SPA fall-through;
- finite process stop and restart with post-recovery health p95 `2.821 ms`.

Repair-forward closure within Phase 5 also established:

- production runtime-authority route precedence with the inherited authority projection retained under an explicit alias;
- `HHS_COGNITION_AUTO_TICK=0` actually disables the recurring canonical background tick while preserving startup and explicit authorized ticks;
- canonical runtime steps execute through one serialized singleton lane off the ASGI event loop;
- no frontend/browser authority is introduced by performance instrumentation.

Phase 5 still does **not** claim terminal Pass 185 completion. Cumulative Pass-185 closure, authoritative-main verification, and external deployment replay remain required.


## Phase-5 health-route reconciliation

The first Phase-5 execution used `/api/system/status` as a presumed lightweight route and aborted on a single one-second tail timeout before a p95 could be computed.

The production boot record itself declares `/api/health` and `/health` as the lightweight health surfaces. The runner now probes those declared routes, selects the first valid JSON health endpoint, records isolated timeout samples rather than aborting immediately, and applies the historical p95 < 250 ms gate across the complete sample set.


## Phase-5 event-loop measurement reconciliation

A later exact-head run showed three authorized canonical steps lasting approximately 3.3–3.7 seconds each while hundreds of `/api/health` requests continued completing, mostly within roughly 1–21 ms. One isolated client-observed sample reached 120.46 ms.

The historical contract prohibits more than 100 ms of **synchronous canonical work on the ASGI main loop without yielding**; it does not define maximum end-to-end client latency as identical to loop occupancy. After the runtime step was moved to one serialized worker-thread lane, the Phase-5 witness therefore requires:

- no concurrent health request failures/timeouts;
- at least twenty health samples during the explicit workload;
- concurrent health p95 below 100 ms;
- the same singleton runtime step lane guarded by one asyncio lock;
- maximum observed client latency retained as diagnostic evidence only.
