# Canonical Visual IDE Restore Checkpoint

```text
status: IN_PROGRESS
repository: danonbrez/Holofractal_Harmonicode
authoritative_base_commit: 3fd4ca088039b1adc0d08a0644d62b979af8997d
branch: main
merge_target: main
worktree_clean: true
created_at_utc: 2026-07-29T21:12:00Z
```

## Defect

The public Heroku process is healthy, but repository integration is incorrect:

- `hhs_backend/heroku_server.py` mounts `hhs_gui/dist` while rejecting canonical runtime and workspace operations as detached.
- `hhs_gui/main.tsx` was changed from `RuntimeShell` to a replacement `ProductionApp`.
- `hhs_gui/index.html` and the compiled bundle therefore do not represent the repository's canonical Runtime OS workspace.
- The canonical backend in `hhs_backend/server.py` already owns runtime initialization, graph memory, replay, WebSockets, GUI command authority, workspace projects, multimodal pipelines, capability fabric, document perception, receipts, and mutation controls.

## Intended correction

1. Restore the canonical `RuntimeShell -> HHSWorkspaceShell` frontend entrypoint.
2. Preserve visible fatal-error and bounded boot handling.
3. Replace Vite-ignored runtime application imports with real bundled imports.
4. Compose assistant and Pass 166 APIs into the canonical backend.
5. Serve the Runtime OS bundle from the canonical backend.
6. Change the Procfile to boot the canonical server.
7. Update release-gate assertions so they reject the replacement `ProductionApp` and detached gateway.
8. Run the bounded native/backend/frontend gate.
9. Verify `main` and replace this checkpoint with a terminal receipt.

## Validation state

```text
PASS: canonical visual IDE source exists
PASS: canonical backend routes exist
CONFIRMED_DEFECT: public entrypoint uses replacement ProductionApp
CONFIRMED_DEFECT: public backend returns detached authority rejections
NOT_RUN: updated frontend build
NOT_RUN: canonical server import/startup test
NOT_RUN: API integration tests
NOT_RUN: browser verification
```

## Exact next action

```text
Apply source corrections on main, run the bounded GitHub Actions release gate, capture any first failure in this receipt, and close with a terminal completion or blocked classification.
```
