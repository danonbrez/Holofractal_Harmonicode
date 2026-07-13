# Changelog Pass 037

Pass 037 closes the first Pass 036 declared-vs-physical enforcement gap.

## Added

- Native `service_registry.dispatch` zero-bypass interposition requirement.
- `HHSServiceRegistry.interpose_dispatch(...)` helper for minting service-dispatch-scoped tokens.
- Direct registry dispatch rejection tests for missing and wrong-surface tokens.

## Changed

- `HHSServiceRegistry.dispatch(...)` now rejects before handler execution when no valid `service_registry.dispatch` interposition token is present.
- API service dispatch mints a token for the native `service_registry.dispatch` surface instead of an API-local surface.
- `HHSCEmulator.dispatch_service(...)` mints a native service dispatch token for normal guarded emulator callers.
- Legacy `hhs_v1_bundle_runner.py` now calls `run_smoke_suite()` instead of the removed `HHSSmokeTestSuiteV1` class.
- The legacy bundle runner treats the database persistence check as optional when the database bridge is unavailable.

## Verified In This Environment

- `hhs_v1_bundle_runner.py` exits `CERTIFIED_LOCKED`.
- `hhs_v1_bundle_runner-2.py` exits `CERTIFIED_LOCKED`.
- Modified Python files pass `py_compile`.

Full service-registry runtime execution was not available in this shell because the HHS C runtime DLL was not built and no compiler toolchain was exposed.
