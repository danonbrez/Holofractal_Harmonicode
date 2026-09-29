# Lane 5 Native Capability Provider Policy — 2026-09-29

Status: **IMPLEMENTED — DEPENDENCY-SCOPED CI PENDING**

## Restart identity

- Base main: `3db446fa471e1bef5a5ad413a03bb9139343679b`
- Branch: `repair/native-fastapi-default-provider`
- Merge target: `main`
- Governing contract: `contracts/pass220/PASS_220_LANE5_NATIVE_CAPABILITY_PROVIDER_V1.json`
- Shared resolver: `hhs_runtime/hhs_lane5_native_capability_provider_v1.py`

## Global rule

All HARMONICODE-owned Lane 5 capabilities use the repository-native implementation by default.

External runtimes, packages, libraries, browser engines, or compatibility providers are selected only through an explicit provider declaration. An external package merely being installed does not change provider selection.

There is no `auto` provider mode.

If a native capability is declared but its native implementation is not complete, implicit resolution fails closed. It must not silently fall through to the foreign dependency.

Unknown capabilities also fail closed until registered.

## Provider controls

- Global explicit override: `HHS_LANE5_PROVIDER_DEFAULT=native|external`
- Per-capability explicit override: `HHS_LANE5_PROVIDER_<CAPABILITY>=native|external`
- Per-capability selection overrides the global value.

External selection is compatibility-only. Provider selection itself grants no VM81 mutation, Hash72 commit, Hash216 persistence, canonical state, or host-float authority.

## Current registered capabilities

- FastAPI → native ASGI compatibility + C11 route kernel; external FastAPI/Starlette only when explicitly selected.
- Python1 → native C11 parser/5,184-digit BigInt executor; CPython is compatibility/differential surface.
- Python2 → native RNA class-registration cell wall; CPython object/class model is external compatibility.
- NumPy → HARMONICODE array/scalar engine + C11 shape/broadcast kernel; NumPy is compatibility/differential surface.
- Matplotlib → native provider not yet implemented; default therefore fails closed. External Matplotlib requires explicit selection.
- Three.js → repository-native HHS3D implementation; Three.js/OrbitControls are external compatibility only.
- WebGL → HHS3D/native render-packet boundary owns the Lane 5 rendering path; direct application-owned WebGL is external/projection compatibility.
- LiteRT-LM → repository-native LiteRT-compatible language/model runtime; external LiteRT-LM/OpenAI-compatible provider is explicit compatibility.
- Mathlib → HHS.Mathlib/native arithmetic carriers; upstream substitution is not implicit.
- Lean4 → pinned HHS proof toolchain/native HHS modules; unbound external proof/runtime authority is not implicit.

This list is not the scope limit. The governing contract requires future HARMONICODE-native Lane 5 capabilities to inherit the same rule when registered.

## FastAPI integration

`hhs_backend.runtime.hhs_fastapi_provider_v1` now delegates provider selection to the shared Lane 5 resolver.

The canonical `hhs_backend.server` module explicitly selects external FastAPI because that module constructs the public external FastAPI application membrane. Runtime modules outside that explicit boundary remain native by default.

The legacy `HHS_FASTAPI_PROVIDER` variable is retained only as a compatibility alias and is normalized into the shared Lane 5 provider selection.

## Validation

Dedicated workflow: `.github/workflows/native-fastapi-default-provider.yml`

The workflow:

1. creates a clean Python virtual environment;
2. deliberately does not install FastAPI or Starlette;
3. proves both external packages are absent;
4. compiles the provider and compatibility surfaces;
5. builds the cumulative exact ABI;
6. builds/tests the native FastAPI C11 route kernel;
7. tests all registered provider defaults and fail-closed behavior;
8. verifies FastAPI native fallback;
9. runs service-registry and live WebSocket regressions.

NumPy may be present as a validation dependency; the tests prove that installation alone does not override the native NumPy provider selection.

## Benchmark consequence

After merge, the Lane 5 integrated benchmark should:

1. rebase/restart from the then-current main/index root;
2. remove the temporary external `fastapi` install added after run `36560225418`;
3. leave provider variables unset for capabilities intended to exercise native defaults;
4. explicitly declare any external compatibility provider needed by a specific differential workload;
5. measure provider status as part of the integrated benchmark receipt.

## Repair-forward state

The earlier FastAPI-only implementation was generalized rather than discarded. Existing commits on this branch remain part of the lineage; the authoritative branch head is the latest commit.

If CI fails, repair only the attributable provider/compatibility/test surface. Do not weaken exactness, authority, replay, or fail-closed invariants.
