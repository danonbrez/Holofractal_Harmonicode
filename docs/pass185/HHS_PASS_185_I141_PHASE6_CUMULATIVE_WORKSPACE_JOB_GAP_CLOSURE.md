# HHS Pass 185 I141 Phase 6 — Cumulative Workspace and Governed Job Gap Closure

Classification:

`HHS_PASS_185_PHASE6_WORKSPACE_JOB_GAPS_IMPLEMENTED_PENDING_VALIDATION`

Terminal Pass 185 completion is not claimed.

## Purpose

Phase 6 closes contract items that remained individually unproven after frozen Phases 1–5. It does not reinterpret adjacent evidence as proof.

The exact production entrypoint remains:

`hhs_backend.runtime_os_application_server:app`

## Production workspace gaps addressed

The Runtime OS now exposes visible, testable controls for:

- New File;
- upload ingress into the source buffer;
- project-object / Explorer selection;
- editor typing;
- Save/Witness through the existing workspace command ingress;
- Build through the existing `compile.execute` authority;
- Create emulator;
- Run through the existing `emulator.run` authority;
- inherited Pass-175 terminal open, readiness, ping/pong, and close;
- governed Pass-191 durable job create, run/resume, cancel, refresh, and recovery/new-job lifecycle.

New File and upload do not create canonical state. They remain local editable buffers until the user explicitly invokes Witness source.

## Authority boundaries

No new VM81, Hash72, terminal, or persistence authority is introduced.

A guarded `POST /api/runtime/authority/tick` surface exposes one complete execution packet from the existing singleton `HHSRuntimeController.authorized_tick`. It is serialized behind the same runtime-step lock already used by the production runtime API.

Pass-191 durable job mutations continue to validate that inherited packet through the existing VM81 admission bridge.

The browser cannot construct, substitute, or promote its own Hash72 authority.

## Cooperative running-job cancellation

Inspection of the inherited Pass-191 runtime found that `cancel_job` could race a concurrently executing `resume_job` because resume retained a stale local job object.

Phase 6 repairs that inherited lifecycle with:

- per-job cancellation events;
- serialized durable transitions;
- cancellation checks before later running-stage writes;
- a cancellation check after repository discovery and before manifest persistence;
- cancellation-specific resume handling that returns the durable cancelled state instead of rewriting it as failure;
- terminal `CANCELLED` receipt ownership remaining with the explicitly authorized cancel request.

The concurrency regression blocks the discovery stage, cancels the job from another thread, releases discovery, and requires the durable final state to remain `CANCELLED` with no later completion receipt or stage overwrite.

## Real-browser acceptance

The Phase-6 Playwright runner uses the exact production root and visible controls.

Required sequence:

`New File → Upload → Witness → Explorer select → Build → Create emulator → Run`

Then:

`Terminal → Open → READY → Ping → PONG → Close`

Then:

`Jobs → Create → QUEUED → Run → RUNNING → Cancel → CANCELLED → Recover/new job → QUEUED`

The running-job cancellation must be driven by visible browser controls while the synchronous Pass-191 resume request is in flight on the exact production server.

## Remaining cumulative scope

Phase 6 does not yet claim the complete historical Pass-185 matrix. After it is frozen, the remaining reconciliation must still prove any contract scenarios not individually covered by Phases 1–6, including outstanding process/socket, cache/network/browser-history, provider-ready/activation-failure, and final evidence-package requirements.

Authoritative-main verification and external deployment replay remain mandatory after cumulative local closure.
