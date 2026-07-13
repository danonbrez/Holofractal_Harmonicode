# TEST REPORT PASS 006

## Verified Commands

```bash
pytest -q
make verify-c
make service-registry
make backend-routes
python -c 'from hhs_backend.server import app; print(app.title)'
python -c 'from hhs_runtime.hhs_unified_hash72_ledger_v1 import verify_unified_ledger; print(verify_unified_ledger()["ok"])'
```

## Results

- `pytest -q` → 40 passed
- `make verify-c` → passed; existing C warnings remain non-blocking
- `make service-registry` → passed; registry dispatch remains guarded
- `make backend-routes` → passed
- Backend app import → passed
- Unified Hash72 ledger verification → true after canonical rebuild

## New Tests

- `tests/test_hhs_backend_guarded_routes_v1.py`
  - Confirms `/api/runtime/step` route uses emulator tick history and produces authority-audited receipt execution.
  - Confirms backend service list exposes default guarded services.
  - Confirms backend service dispatch produces a service dispatch record with successful post-authority audit and ledger append.
