# CHANGELOG PASS 017 — GUI Runtime Contract Surface

## Priority
Move the canonical runtime contract outward into the GUI/runtime transport layer.

## Added
- `hhs_gui/runtime_os/core/RuntimeContractEnvelope.ts`
- Frontend contract validation helpers for:
  - canonical runtime contract version
  - native 72-symbol Hash72 strings
  - C `u^72` Digital DNA kernel witnesses
  - runtime packet envelopes
  - API response envelopes
- Static conformance tests for the GUI contract surface.

## Changed
- `RuntimeKernelBridge.ts` now unwraps runtime packet/API contract envelopes and records the latest contract hash/validation status.
- `RuntimeSocketManager.ts` now surfaces `contract_hash72`, `payload_hash72`, `contract_valid`, and `contract_reasons` on normalized socket events.
- `PROJECT_STATE.json` now declares the frontend runtime contract surface.

## Preserved
- No kernel mathematics changed.
- No frontend code derives runtime authority.
- GUI remains an observer/transport consumer of backend/kernel authority.
