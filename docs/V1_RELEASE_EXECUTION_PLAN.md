# Holofractal Harmonicode v1 Release Execution Plan

Status: active release-finalization plan  
Mode: finish existing interfaces; no new theory, no redesign, no ontology expansion.

## Release Principle

The math, symbolic logic, ethics, security, and kernel authority model are treated as fixed project specification for v1. Engineering work must preserve the declared public vocabulary, constants, operators, file boundaries, and user-facing semantics unless an explicit release-change request is made.

## v1 Definition of Done

A v1 release is complete when the existing runtime surfaces can be built, imported, executed, and documented through one stable path:

```text
C VM81 / ABI -> Python ctypes bridge -> backend runtime -> GUI/interface -> receipt/export surfaces
```

The release target is not additional features. The release target is a working, inspectable, testable interface over the already-defined system.

## Frozen Scope

Allowed:

- fix imports and package markers
- normalize repository-relative paths
- add deterministic build commands
- wire the C shared library to the Python bridge
- document entrypoints and execution commands
- add smoke tests around existing surfaces
- remove duplicate/stale interface paths after verification
- stabilize the GUI/backend connection

Disallowed without explicit instruction:

- new symbolic operators
- new kernel authority layers
- renaming canonical constants or invariants
- replacing the C kernel design
- redesigning the runtime model
- adding speculative features

## Current Confirmed State

- Python topology suite: mostly passing, with release-integration failures previously isolated to package metadata, authoritative kernel import resolution, and sandbox-specific path literals.
- C VM81 substrate: standalone build target exists and can be verified through `--verify` once built.
- C ABI layer: source exists under `hhs_runtime/c/` and exports the Python-facing runtime surface once compiled.
- Python bridge: `hhs_python/runtime/hhs_ctypes_bridge.py` expects the compiled shared library under `hhs_runtime/builds/`.
- Backend: `hhs_backend/server.py` remains the backend runtime entrypoint.
- GUI: `hhs_gui/` remains the interface surface to be stabilized after backend/runtime verification.

## Execution Phases

### Phase 1 — Topology Stabilization

Goal: make the repository import and test as a coherent package without changing functionality.

Tasks:

- add backend package marker
- normalize kernel discovery
- remove sandbox-specific absolute runtime assumptions
- ensure authoritative kernel imports under standard and test loaders
- run Python topology tests

Acceptance gate:

```bash
pytest -q
```

### Phase 2 — C Kernel Build Surface

Goal: make the C kernel and ABI buildable from a single repo-level command.

Tasks:

- add `Makefile` build targets
- build standalone VM81 binary
- build `hhs_runtime/builds/libhhs_runtime.so`
- verify required ABI symbols exist
- keep generated binaries out of source-control decisions unless release packaging explicitly requires them

Acceptance gate:

```bash
make verify-c
```

### Phase 3 — Python ↔ C Bridge Verification

Goal: confirm Python can load the compiled C ABI from the canonical location.

Tasks:

- build shared library into `hhs_runtime/builds/`
- import `hhs_python.runtime.hhs_ctypes_bridge`
- initialize runtime state through ABI
- run one deterministic runtime step
- confirm receipt/hash fields are populated

Acceptance gate:

```bash
python -m hhs_python.runtime.hhs_ctypes_bridge
```

If the bridge class/function names differ, preserve the existing bridge API and adjust only the verification command/documentation.

### Phase 4 — Backend Runtime Wiring

Goal: make backend startup resolve the same runtime path as tests and the Python bridge.

Tasks:

- confirm `hhs_backend.server` imports cleanly
- ensure backend runtime code does not hardcode local sandbox paths
- expose one health/status route if already present
- document backend startup command

Acceptance gate:

```bash
python -m hhs_backend.server
```

### Phase 5 — GUI Interface Finalization

Goal: finalize the existing interface; do not redesign it.

Tasks:

- identify current GUI entrypoint
- wire all visible controls to existing backend/runtime endpoints
- remove dead controls or mark them disabled
- confirm import/export paths
- add user-facing validation messages
- document the v1 workflow

Acceptance gate:

```text
A user can open the interface, execute the canonical runtime action, receive a receipt/output, and save/export the result.
```

### Phase 6 — Release Documentation

Goal: make v1 usable by a fresh checkout.

Tasks:

- update README quickstart
- document C build
- document Python test command
- document backend startup
- document GUI startup
- list frozen v1 surfaces
- list intentionally deferred work

Acceptance gate:

```text
A new developer can clone, build, test, and run the v1 interface using documented commands only.
```

## Immediate Punch List

- [x] Add v1 release execution plan to docs.
- [x] Add repo-level C kernel build targets.
- [x] Add backend package marker.
- [x] Remove stale sandbox path literals from Python runtime files.
- [x] Run full Python test suite and record result. Result: `30 passed`.
- [x] Run C kernel verification and record result. Result: `make verify-c` completed; VM81 `--verify` executed; ABI symbols exported.
- [x] Verify Python ctypes bridge can load the compiled ABI. Result: `HHSRuntimeBridge` imports, validates ABI, steps runtime, and commits receipt.
- [x] Inspect backend startup path. Result: `hhs_backend.server` imports; runtime entrypoint remains `python -m hhs_backend.server`.
- [x] Inspect GUI entrypoint and current control wiring. Result: `hhs_gui/src/App.tsx` boots `RuntimeOS` and `RuntimeShell`; GUI is currently websocket-oriented through `/ws/runtime`, `/ws/replay`, `/ws/graph`, and `/ws/transport`.
- [x] Update README with final v1 commands.

## Release Engineering Rule

Every change must answer one of these questions:

1. Does it make the existing interface build?
2. Does it make the existing interface run?
3. Does it make the existing interface testable?
4. Does it document the existing interface?

If the answer is no, defer it beyond v1.

## Execution Log

### 2026-06-29 Snapshot Execution

Completed release-finalization actions:

- Added `hhs_backend/__init__.py` so the backend resolves as a physical package instead of an import-hook-only namespace.
- Added repo-level `Makefile` with `c-kernel`, `c-abi`, `vm81`, `verify-c`, `test`, and `clean` targets.
- Built `hhs_runtime/builds/libhhs_runtime.so` from the canonical ABI sources.
- Built `hhs_runtime/builds/hhs_vm81` from `hhs_runtime/HARMONICODE_VM_RUNTIME.c`.
- Verified C substrate with `make verify-c`.
- Verified exported ABI symbols: `hhs_runtime_init`, `hhs_runtime_step`, `hhs_validate_abi`, `hhs_hash216_compute`.
- Removed Python runtime dependencies on sandbox-specific absolute paths.
- Added kernel import compatibility for loaders that do not pre-register `sys.modules`.
- Verified Python test suite: `30 passed`.
- Verified Python ctypes bridge loads the compiled ABI and performs a runtime step/receipt commit.
- Verified backend module import: `hhs_backend.server`.

Remaining release-finalization actions:

- Inspect GUI control wiring in `hhs_gui/src/App.tsx`.
- Confirm frontend build/typecheck in a Node environment with dependencies installed.
- Add README quickstart commands for backend and GUI once interface path is confirmed.
- Decide whether generated C binaries should be ignored, packaged, or released as artifacts.



### 2026-07-07 Local Development Pass 001

Completed in local release-integration environment:

- Rebuilt C ABI and VM81 with `make verify-c`; verification completes and required symbols are exported.
- Re-ran Python topology suite with `pytest -q`; result: `30 passed`.
- Confirmed bridge verification command is `python -m hhs_python.runtime.hhs_ctypes_bridge`; existing bridge API uses `runtime_init()`, `runtime_step()`, `receipt_commit()`, and `export_runtime_dict()`.
- Confirmed backend import path: `hhs_backend.server` exposes `app`.
- Inspected GUI boot path: `hhs_gui/src/App.tsx` configures `RuntimeOS` with relative websocket endpoints and renders `RuntimeShell`.
- Fixed malformed JSX in `hhs_gui/runtime_os/workspace/HHSRuntimeSpatialOrchestrator.tsx` that blocked TypeScript parsing.
- Normalized `hhs_gui/tsconfig.json` include scope so app sources are not mixed with referenced node config sources.

Open blockers after this pass:

- GUI dependencies are not vendored in the ZIP; local TypeScript verification cannot finish without installing `react`, `react-dom`, and declared type packages.
- `src/App.tsx` passes `diagnosticsEnabled` and `mobileMode` into `RuntimeOS`, but `RuntimeOSConfig` currently declares only endpoint fields. Either extend the config interface or remove unused keys after confirming intended GUI behavior.
- `src/components/RuntimeShell.tsx` appears to be a stale/parallel shell path with local imports that do not match the canonical `runtime_os/core` layout; classify as deprecated, shim, or migrate.
