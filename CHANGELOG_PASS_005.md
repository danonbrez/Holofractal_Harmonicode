# CHANGELOG PASS 005 — Guarded Service Registry

## Summary
Pass 005 converts the next major execution gap into a deterministic runtime surface: services can now be registered, discovered, and dispatched through a single guarded path.

## Added
- `hhs_runtime/hhs_service_registry_v1.py`
  - `HHSServiceSpec`
  - `HHSServiceRegistry`
  - `make_default_service_registry()`
  - `service_registry_self_test()`
- `HHSCEmulator.dispatch_service(...)`
- `make service-registry`
- Tests for registry discovery, authority-gated dispatch, emulator service exposure.

## Default Services
- `authority_gate.self_test`
- `ledger.verify`
- `c_bridge.abi_self_test`

## Authority Rule
Every registered service defaults to `requires_authority=True`, which means dispatch performs a controller-owned `authorized_tick` before service logic and commits the service dispatch record to the unified Hash72 ledger afterward.

## Non-Goals
- No kernel semantics changed.
- No new mathematical logic added.
- No GUI framework rewrite.
