# Test Report — Pass 002

## Commands Run

```bash
python -m pytest -q
make verify-c
python -m hhs_python.runtime.hhs_ctypes_bridge
python - <<'PY'
import importlib
importlib.import_module('hhs_backend.runtime.runtime_orchestrator')
PY
```

## Results

- Python tests: `30 passed`.
- C runtime verification: completed.
- C ABI symbols verified by `make verify-c`:
  - `hhs_runtime_init`
  - `hhs_runtime_step`
  - `hhs_validate_abi`
  - `hhs_hash216_compute`
- Python ctypes bridge: `HHS ABI VALIDATED`.
- Backend runtime orchestrator import: OK.

## Warnings

`make verify-c` still emits C warnings around initializer completeness and unused static functions. These warnings do not block the current verification target but should be handled in a future hardening pass.

## Not Run

- `npm install`
- `npm run typecheck`
- `npm run build`

Reason: GUI dependencies are not included in the ZIP and were not installed in this local environment.
