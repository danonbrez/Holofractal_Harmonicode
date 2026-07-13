# CHANGELOG PASS 006 — Guarded Backend/API Binding

## Objective
Bind the backend runtime API to the guarded emulator/service execution path so network-facing runtime commands cannot bypass Hash72 receipts, the four invariants, or the canonical algebraic authority gate.

## Changes

- Added backend-global `runtime_emulator` sharing the canonical `runtime_controller`.
- Changed `/api/runtime/step` from direct `run_steps()` execution to guarded `HHSCEmulator.run()` execution.
- Added service discovery and dispatch API routes:
  - `GET /api/runtime/services`
  - `GET /api/runtime/services/status`
  - `POST /api/runtime/services/dispatch`
- Updated backend startup to boot the guarded emulator and persist boot authority audit state.
- Added optional controller injection to `HHSCEmulator` so backend/API/GUI surfaces can share one authority-owning runtime path.
- Hardened `HHSServiceRegistry.register_function()` so optional diagnostic parameters do not accidentally receive service payload dictionaries.
- Stabilized unified Hash72 ledger hashing with canonical JSON projection.
- Added `rebuild_unified_ledger()` repair migration for pre-canonical ledger entries.
- Added `make backend-routes` verification target.
- Added backend guarded route tests.

## Non-Goals

- No kernel invariant changes.
- No C runtime semantic changes.
- No new feature expansion outside backend/API binding and Hash72 ledger determinism.
- No GUI dependency install or GUI build execution.
