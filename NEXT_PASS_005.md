# NEXT PASS 005 — Backend/API/GUI Authority Binding

## Goal

Ensure external surfaces cannot bypass the gated emulator/controller path.

## Required Work

1. Inventory backend/API/websocket runtime commands.
2. Replace direct execution calls with `HHSCEmulator` or `HHSRuntimeController.authorized_tick()`.
3. Add route-level tests proving emitted runtime packets include `authority_audit` and Hash72 receipt metadata.
4. Start service/module registry classification:
   - production-gated
   - diagnostic-only
   - plugin extension
   - deprecated/archive candidate
5. Update `PROJECT_STATE.json` and pass docs.

## Non-Negotiable Constraint

No service exposed to users, GUI, API, assistant, IDE, semantic search, ML, or automation may perform mutating execution without Hash72 receipt closure and invariant authority audit.
