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

At runtime, if a native capability is declared but its native implementation is not complete, implicit resolution fails closed unless an external provider was explicitly selected.

During pull-request validation only, an unavailable native provider falls back to that capability's declared external compatibility provider. The fallback must emit both a runtime warning and a machine-readable warning receipt naming the capability, native-unavailable reason, and external target. The fallback remains compatibility-only and cannot acquire VM81, Hash72, Hash216, canonical-state, or host-float authority.

Unknown capabilities still fail closed until registered.

## Provider controls

- Global explicit override: `HHS_LANE5_PROVIDER_DEFAULT=native|external`
- Per-capability explicit override: `HHS_LANE5_PROVIDER_<CAPABILITY>=native|external`
- Per-capability selection overrides the global value.
- Provider context: `HHS_LANE5_PROVIDER_CONTEXT=runtime|pull_request`.
- `pull_request` permits warned declared-external fallback only when native is unavailable.

External selection or PR fallback is compatibility-only. Provider selection itself grants no VM81 mutation, Hash72 commit, Hash216 persistence, canonical state, or host-float authority.

## Current registered capabilities

- FastAPI → native ASGI compatibility + C11 route kernel; external FastAPI/Starlette only when explicitly selected.
- Python1 → native C11 parser/5,184-digit BigInt executor; CPython is compatibility/differential surface.
- Python2 → native RNA class-registration cell wall; CPython object/class model is external compatibility.
- NumPy → HARMONICODE array/scalar engine + C11 shape/broadcast kernel; NumPy is compatibility/differential surface.
- Matplotlib → native provider not yet implemented; runtime default therefore fails closed. Pull-request validation falls back to declared external Matplotlib with a warning; runtime external Matplotlib still requires explicit selection.
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
2. installs bounded validation dependencies plus declared Matplotlib PR fallback;
3. deliberately does not install FastAPI or Starlette;
4. proves both external FastAPI packages are absent while native FastAPI remains available;
5. compiles the provider and compatibility surfaces;
6. resolves PR provider status and emits GitHub warning annotations for each fallback;
7. proves Matplotlib resolves to its declared external provider in PR context;
8. builds the cumulative exact ABI;
9. builds/tests the native FastAPI C11 route kernel;
10. tests runtime fail-closed behavior and PR fallback behavior;
11. runs service-registry and live WebSocket regressions.

NumPy and Matplotlib may be installed in the validation environment. Installation alone does not override a working native provider; Matplotlib is selected externally only because its native provider is declared unavailable in PR context.

## Benchmark consequence

After merge, the Lane 5 integrated benchmark should:

1. rebase/restart from the then-current main/index root;
2. remove the temporary external `fastapi` install added after run `36560225418`;
3. leave provider variables unset for capabilities intended to exercise native defaults;
4. explicitly declare external compatibility providers for runtime/differential workloads where required;
5. when benchmark execution is attached to PR validation and a native provider is unavailable, accept only the declared external fallback with its warning receipt;
6. measure provider context, selected provider, fallback flag, and warning receipt as part of the integrated benchmark evidence.

## Repair-forward state

The earlier FastAPI-only implementation was generalized rather than discarded. Existing commits on this branch remain part of the lineage; the authoritative branch head is the latest commit.

If CI fails, repair only the attributable provider/compatibility/test surface. Do not weaken exactness, authority, replay, or fail-closed invariants.
