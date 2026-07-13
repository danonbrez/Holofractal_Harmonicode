# CHANGELOG PASS 003 — Automatic C Runtime Emulator

## Summary

Pass 003 converts the C runtime bridge from a manual verification surface into an emulator-style lifecycle surface.

The runtime can now:

```text
boot → validate ABI → tick C VM → commit receipt → export packet → repeat/halt
```

without requiring callers to manually sequence C build, ctypes loading, stepping, receipt commit, and packet export.

## Added

- `hhs_python/runtime/hhs_runtime_emulator.py`
  - `HHSEmulatorConfig`
  - `HHSCEmulator`
  - `boot()`
  - `tick()`
  - `run()`
  - `halt()`
  - `status()`
  - module self-test entrypoint
- `make emulate-c`
- `tests/test_hhs_c_emulator_autoboot.py`

## Changed

- `hhs_python/runtime/hhs_ctypes_bridge.py`
  - attempts automatic C ABI build when the shared library is missing
  - supports disabling auto-build with `HHS_DISABLE_C_AUTOBUILD=1`
  - adds `step(instruction=None)` compatibility alias for orchestrators
- `README.md`
  - documents automatic emulator boot and run commands

## Preserved

- C kernel semantics
- VM81 source logic
- ABI symbols
- existing Python controller behavior
- GUI/API contract shape

## Verification

- `make verify-c` passed
- `python -m hhs_python.runtime.hhs_runtime_emulator` passed
- `pytest -q` passed: 32 tests
