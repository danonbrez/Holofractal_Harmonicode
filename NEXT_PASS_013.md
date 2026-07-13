# NEXT PASS 013 — Frontend Contract Adapter

## Primary Goal
Expose the canonical API/runtime contract cleanly to the GUI layer.

## Recommended Work

1. Add TypeScript contract definitions matching `hhs_runtime_contract_v1.py`.
2. Add frontend API client adapter that reads `runtime_contract` envelopes.
3. Normalize runtime state, service list, vector, packet, and websocket data at the frontend boundary.
4. Keep legacy fields usable during transition.
5. Add lightweight frontend-side contract guards where possible without requiring Node dependency installation.

## Constraints

- Do not change kernel semantics.
- Do not create unguarded frontend/backend shortcuts.
- Do not remove legacy response fields until the GUI is fully migrated.
