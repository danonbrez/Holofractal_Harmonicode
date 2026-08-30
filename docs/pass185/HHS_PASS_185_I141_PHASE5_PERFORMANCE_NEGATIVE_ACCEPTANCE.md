# HHS Pass 185 I141 Phase 5 — Performance and Remaining Negative Acceptance

Classification:

`HHS_PASS_185_PHASE5_PERFORMANCE_NEGATIVE_IMPLEMENTED_PENDING_VALIDATION`

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

Phase 5 remains pending until one exact branch head passes the full workflow.


## Phase-5 health-route reconciliation

The first Phase-5 execution used `/api/system/status` as a presumed lightweight route and aborted on a single one-second tail timeout before a p95 could be computed.

The production boot record itself declares `/api/health` and `/health` as the lightweight health surfaces. The runner now probes those declared routes, selects the first valid JSON health endpoint, records isolated timeout samples rather than aborting immediately, and applies the historical p95 < 250 ms gate across the complete sample set.
