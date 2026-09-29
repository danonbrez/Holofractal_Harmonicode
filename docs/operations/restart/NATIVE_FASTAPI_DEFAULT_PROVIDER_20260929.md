# Native FastAPI Default Provider — 2026-09-29

Status: **IMPLEMENTED — VALIDATION PENDING**

## Restart identity

- Base main: `3db446fa471e1bef5a5ad413a03bb9139343679b`
- Branch: `repair/native-fastapi-default-provider`
- Merge target: `main`
- Purpose: make the repository-native FastAPI compatibility surface the automatic fallback whenever the external FastAPI dependency is not present, while preserving explicit external compatibility.

## Selection contract

`HHS_FASTAPI_PROVIDER` accepts:

- `native` (implicit default): bind repository-native FastAPI compatibility and never import external FastAPI.
- `external`: require external FastAPI and fail closed with `HHS_FASTAPI_EXTERNAL_EXPLICIT_BUT_UNAVAILABLE` when it is absent.

`hhs_backend.server` is an explicit external FastAPI composition boundary and sets `HHS_FASTAPI_PROVIDER=external` by default before importing the canonical WebSocket router. A caller may still explicitly override the environment before server import.

The provider does not create VM81 mutation, Hash72 commit, Hash216 persistence, or canonical-state authority.

## Implementation

Changed surfaces:

1. `hhs_backend/runtime/hhs_fastapi_provider_v1.py`
   - provider resolver and status receipt;
   - native fallback;
   - explicit native/external overrides.

2. `hhs_backend/runtime/hhs_native_fastapi_compat_v1.py`
   - deferred `NativeAPIRouter` / `NativeAPIRoute`;
   - structural `NativeWebSocket`;
   - `NativeWebSocketDisconnect`;
   - preserves route declaration metadata without external FastAPI.

3. `hhs_backend/runtime/runtime_ws.py`
   - imports API/WebSocket compatibility from the provider resolver instead of directly importing external FastAPI.

4. `hhs_backend/server.py`
   - explicitly selects the external provider at the canonical external FastAPI application boundary.

5. `tests/pass220/test_hhs_native_fastapi_default_provider_v1.py`
   - native router metadata;
   - automatic native fallback with all external FastAPI imports blocked;
   - explicit external fail-closed behavior;
   - explicit native mode never importing external FastAPI.

6. `.github/workflows/native-fastapi-default-provider.yml`
   - creates a clean virtual environment;
   - deliberately does **not** install FastAPI or Starlette;
   - asserts both are absent;
   - builds the exact cumulative ABI and native C11 FastAPI route kernel;
   - runs the new fallback tests plus service-registry and live-kernel/WebSocket regressions.

## Benchmark repair consequence

The earlier Lane 5 benchmark workflow added external FastAPI only to work around a missing import. Once this change is merged to main, the benchmark should remove that temporary dependency and rerun from the new main/index root so service-registry benchmarking exercises the repository-native fallback when no external FastAPI dependency is declared by the benchmark environment.

## Remaining validation

1. inspect the dedicated workflow on this branch;
2. repair only attributable implementation/test defects;
3. if green, open/merge the PR;
4. update the Lane 5 benchmark branch from the merged main;
5. remove the temporary external FastAPI install from the benchmark workflow and execute the full benchmark campaign.
