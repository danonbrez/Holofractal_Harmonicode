# INTEGRATION REPORT PASS 006

## Summary
Pass 006 moves the auto-run chain one layer outward: the backend API now uses the guarded emulator/service registry instead of calling direct runtime step execution for normal API control.

This establishes the backend as a projection surface over the same guarded execution graph used by the emulator and service registry.

```text
Backend API
  → HHSCEmulator
    → HHSServiceRegistry / HHSRuntimeController.authorized_tick
      → C Runtime ABI
      → receipt commit
      → authority audit
      → unified Hash72 ledger append
```

## API Binding

### Runtime Step
`POST /api/runtime/step` now returns schema `HHS_GUARDED_RUNTIME_STEP_RESPONSE_V1` and executes through `runtime_emulator.run()`.

### Service Discovery
`GET /api/runtime/services` exposes registered guarded services for GUI command-palette or API consumers.

### Service Status
`GET /api/runtime/services/status` returns service registry status, runtime state, authority audit, and unified ledger verification.

### Service Dispatch
`POST /api/runtime/services/dispatch` dispatches named services through the guarded service registry.

## Hash72 Ledger Determinism
The unified Hash72 ledger previously relied on Python object stringification for nested payload hashing. Pass 006 replaces this with canonical JSON projection for stable replay verification and includes a repair migration for existing records.

## Authority Boundary
Backend callers now have a clear public route into guarded execution. Direct controller methods remain available internally for diagnostics, but the public API route path is now aligned with the non-bypass execution rule.
