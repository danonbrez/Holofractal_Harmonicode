# I047 FastAPI WebSocket Boundary Repair — Restart Record

Base commit: `7c7dae820da99acc82cfae764df8ae0020fed9ed`
Branch: `repair/i047-fastapi-websocket-boundary-20260930`
Merge target: `main`

## Failure evidence

PR #669 exact-head workflow run 36707031893 failed `Pass 220 FastAPI1 Native Route Kernel`.
The dependency test `test_fastapi1_native_modules_do_not_import_fastapi_starlette_or_pydantic`
found `from fastapi import WebSocket as ExternalWebSocket` inside
`hhs_backend/runtime/hhs_native_fastapi_compat_v1.py`.

## Repair

- Native compatibility membrane no longer imports FastAPI.
- External WebSocket type is injected explicitly by the canonical FastAPI server boundary.
- VM81, Hash72, Hash216 and canonical state mutation authority flags remain unchanged and false on the compatibility projection.

## Changed files

- `hhs_backend/runtime/hhs_native_fastapi_compat_v1.py`
- `hhs_backend/server.py`
- this restart record

## Validation

Required CI: `Pass 220 FastAPI1 Native Route Kernel`.
Dependency-scoped regression command represented by that workflow:
`python -m pytest -q tests/pass220/test_hhs_pass220_fastapi1_native_route_kernel_v1.py`

## Remaining

Wait for exact-head CI. Merge only when the required FastAPI1 gate is green; then verify authoritative main. Repair forward any attributable failure.
