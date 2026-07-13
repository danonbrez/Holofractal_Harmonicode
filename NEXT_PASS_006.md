# NEXT PASS 006 — Backend/API Registry Binding

## Primary Target
Expose the guarded service registry through backend/API runtime surfaces so GUI/API callers can discover and dispatch services without direct module knowledge.

## Recommended Work
1. Add backend route helpers for:
   - service registry status
   - service list
   - guarded service dispatch
2. Bind websocket/runtime stream status to registry state where appropriate.
3. Add tests proving backend route functions use registry dispatch instead of direct service calls.
4. Keep direct execution as diagnostic-only.

## Acceptance Criteria
- Backend exposes service discovery and guarded dispatch.
- Dispatch emits authority audit and unified Hash72 ledger receipt.
- `pytest -q` remains green.
- `make verify-c` remains green.
