# Registry-Driven Visual Programming Repair Checkpoint

```text
status: IN_PROGRESS
repository: danonbrez/Holofractal_Harmonicode
authoritative_base_commit: edffcc17aea81bfd2a89e9f80c227b6dcfa097fd
branch: main
merge_target: main
worktree_clean: true
created_at_utc: 2026-07-30T01:21:00Z
```

## Confirmed workflow defect

The current public interface overcorrected a performance problem by removing the runtime application graph and most registered functionality from the product surface. Replacing thousands of repository modules with a one-page list or a few static buttons is not acceptable.

## Required product architecture

```text
backend guarded service registry
+ frontend runtime application registry
+ workspace operations
→ typed executable visual objects
→ schema-derived input/output ports
→ composable directed edges
→ shared project/object/artifact state
→ guarded node or graph execution
→ human-readable results and Hash72 receipts
```

## Binding constraints

- Every registered backend service must be discoverable and addable as an executable node.
- Registry entries must not be represented as inactive decorative cards.
- Nodes must expose editable payloads, typed/schema metadata, execution status, result state, and receipt evidence.
- Connections must move actual prior-node result data into downstream payloads.
- A graph run must execute in deterministic dependency order and stop visibly on rejection.
- Expensive application views and runtime transports must remain lazy/on-demand rather than removed.
- Existing project, ingress, interpretation, compilation, emulator, assistant, runtime, and receipt workflows must remain reachable.
- Mobile must show one active canvas/inspector surface without mounting every application.
- No synthetic success response is permitted.

## Existing authoritative surfaces

- `GET /api/runtime/services` returns the guarded service registry.
- `POST /api/runtime/services/dispatch` executes a named registered service through zero-bypass interposition and runtime authority.
- `RuntimeApplicationRegistry.tsx` defines lazy GUI application modules.
- `WorkspaceCommandClient` exposes governed project/object/compiler/emulator operations.

## Files expected to change

```text
hhs_gui/runtime_os/workspace/RegistryVisualProgrammer.tsx        (new)
hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx               (integrate)
hhs_gui/runtime_os/core/RuntimeApplicationRegistry.tsx            (metadata/access only if required)
hhs_gui/scripts/workspace-source-verify.mjs                       (contracts)
.github/workflows/build-runtime-os-frontend.yml                    (bundle gate if required)
docs/operations/recovery_receipts/REGISTRY_VISUAL_PROGRAMMING_REPAIR_2026-07-29_IN_PROGRESS.md
```

## Completed analysis

```text
CONFIRMED: backend registry is executable and returns machine-readable service descriptors.
CONFIRMED: guarded dispatch route already exists.
CONFIRMED: frontend application registry already supports lazy loaders.
CONFIRMED: current public shell exposes only a narrow fixed workflow.
```

## Exact next action

```text
Implement the executable registry canvas, bind it to guarded dispatch and shared workspace state, preserve lazy application loading, run bounded backend/frontend validation, publish the generated bundle, verify main, and replace this checkpoint with a terminal receipt.
```
