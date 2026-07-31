# HHS PASS 176 — DEPLOYMENT BACKEND DEGRADED-MODE AMENDMENT

## Normative identity

- Contract: `HHS-P176-DBDM-LH-CAG-P175-AIG`
- Parent: `HHS-P176-DURA-FSLJ-SPX-PB-AWR`
- Baseline: authoritative `main` at `862dc89f2ea1258db6ceb0e1a0a2d38b1eb21975`
- Scope: deployed backend liveness, capability gating, honest failure states, and frontend continuity

## Binding inheritance

This amendment is additive. It preserves all prior pass constraints, VM81 singleton authority, Hash72 commit-clock authority, Hash216 identity and indexing, exact-source preservation, no-float canonical authority, backend-only receipt issuance, deterministic replay, and restartable repository closure.

A reachable web process is not equivalent to runtime authority. The browser may continue editing, previewing, and packaging source or runnable browser artifacts while the backend is unavailable, but it may not claim lifecycle, VM81, Hash72, Hash216, firmware, terminal, or assistant completion.

## Required corrections

1. Provide dependency-light `/health` and `/api/health` liveness routes before the unknown-API fallback and static root mount.
2. Poll liveness and product health from the browser with bounded timeouts and explicit `online`, `degraded`, or `offline` states.
3. Display a persistent degraded-mode banner with retry and machine-readable diagnostic details whenever runtime or assistant capability is unavailable.
4. Keep Save, editing, preview, source ZIP, and runnable browser ZIP available during backend failure.
5. Disable governed lifecycle, ingress, interpretation, compilation, VM81, Pass 175 processor/terminal, receipt, and assistant-send controls when their required backend capability is unavailable.
6. Prevent optimistic firmware or VM status changes without a confirmed backend response; explicitly state that no authority state changed.
7. Keep the assistant prompt editable for draft preservation while gating submission when the provider is unavailable.
8. Deduplicate repeated preview-ready console messages.
9. Materialize generated starter files as clean checkpointed state and format HTML/CSS source for readable editing.
10. Preserve the advanced runtime workspace and all authority surfaces; degraded mode changes availability and explanation, not system semantics.

## Deployment boundary

This repository amendment cannot repair a deleted, renamed, suspended, DNS-unreachable, or unprovisioned Heroku application by itself. Platform DNS, dyno, build, and routing restoration must be verified through Heroku. The repository must not claim live-deployment recovery until the target URL and health endpoints are externally reachable.

## Acceptance gates

- Lightweight health routes are registered before API fallback and static mounts.
- Offline mode disables backend-authority controls without disabling local editing, preview, or export.
- Assistant prompt remains focusable and editable while send is gated.
- Pass 175 controls cannot enter optimistic running states while health is offline/degraded.
- Preview-ready logs are deduplicated.
- Starter files begin clean and readable.
- Dependency-scoped tests and syntax checks pass.

## Terminal classification

`HHS_PASS_176_DEPLOYMENT_BACKEND_DEGRADED_MODE_IMPLEMENTED`
