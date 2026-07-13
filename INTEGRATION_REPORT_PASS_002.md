# Integration Report — Pass 002

## Summary

Pass 002 continued release consolidation around the GUI/runtime boundary. The primary issue was stale GUI projection code referencing earlier `RuntimeOS` surfaces (`state`, `workspace`) while the canonical runtime implementation now exposes `store`, `socketManager`, and `windowManager`.

## Integration Decisions

### RuntimeOS remains orchestration/projection only

No authority was moved into the frontend. `RuntimeOS.getMetrics()` now adapts existing runtime/socket/window/store metrics into the stable GUI-facing shape expected by shell components.

### Stale shell implementation converted to compatibility export

`hhs_gui/src/components/RuntimeShell.tsx` contained an older implementation with broken relative imports and obsolete runtime assumptions. It now re-exports the canonical shell under `runtime_os/core` so older import paths resolve without duplicating runtime shell logic.

### Workspace references replaced with window manager access

Current canonical window state lives in `RuntimeWindowManager`. Dock/topbar/sidebar/graph surfaces now use `windowManager` or `getMetrics()` rather than a removed `workspace` facade.

## Current Boundary Contract

```text
Backend / runtime authority
  → websocket events
  → RuntimeSocketManager
  → RuntimeStateStore
  → RuntimeOS metrics adapter
  → RuntimeShell / Desktop / Instruments
```

## Remaining Integration Work

- Install GUI Node dependencies and run `npm run typecheck` / `npm run build`.
- Confirm backend canonical launch command and websocket route contract.
- Decide whether to preserve or remove older workspace abstraction files after canonical GUI build passes.
