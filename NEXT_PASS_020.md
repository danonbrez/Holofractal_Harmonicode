# NEXT PASS 020 — SRCG User-Facing Instrument Panel

## Recommended Priority
Create a dedicated GUI instrument for SRCG execution and trace inspection.

## Targets
- Add SRCG workspace/instrument component.
- Allow entering A/B/max_steps and nested carrier payload.
- Display `ok`, rollback state, trace count, 1.001 invariant status, and latest Hash72/u^72 witness.
- Register the instrument in the runtime application registry.
- Keep all execution routed through `executeSRCGSelfSolve()`.
