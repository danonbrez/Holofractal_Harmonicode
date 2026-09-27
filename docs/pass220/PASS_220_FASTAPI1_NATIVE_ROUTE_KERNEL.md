# Pass 220 FastAPI1 — Native Route Kernel

## Status

`IMPLEMENTED ON RESTARTABLE BRANCH — CI VALIDATION PENDING`

Branch:

`pass220-fastapi1-native-route-kernel`

Base main at branch creation:

`4a342ebbfa82ed621a41346d09b9d8796780bc37`

## Objective

Begin replacing the external FastAPI/Starlette interior with a HARMONICODE-owned
native implementation while preserving the external FastAPI/ASGI contract.

The compatibility rule is:

```text
same external request contract
        ↓
same route selection / captures
        ↓
same framework-independent HHS handler
        ↓
same status + content type + observable JSON result
```

FastAPI remains an ingress/egress compatibility membrane during migration. It is
not the target internal execution substrate.

## Native route kernel

The C11 project is:

`native_projects/hhs_pass220_fastapi_native_route_kernel`

It implements fixed-storage deterministic route registration and resolution:

- no dynamic allocation;
- registration-order precedence, matching FastAPI/Starlette route ordering;
- GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD, and WebSocket method identities;
- static paths;
- single-segment `{param}` captures;
- remainder `{param:path}` captures;
- duplicate method/path rejection;
- deterministic noncanonical registry fingerprint;
- bounded route/path/capture memory.

The native route kernel has no canonical mutation, VM81 admission, Hash72
commit, or Hash216 persistence authority.

## FastAPI-free ASGI membrane

`hhs_backend.runtime.hhs_native_fastapi_compat_v1` exposes:

- `NativeRouteKernel` — ctypes binding to the C11 router;
- `HHSNativeASGIApplication` — FastAPI-free ASGI application;
- FastAPI-style `.get()`, `.post()`, `.put()`, `.patch()`, and
  `.delete()` decorators;
- deterministic JSON response serialization for the current compatibility
  subset;
- FastAPI-compatible 404 and 405 response behavior.

This module imports neither FastAPI, Starlette, nor Pydantic.

## First migrated route family

The first family is:

`/api/runtime/graphics/*`

Its behavior was extracted into:

`hhs_backend.runtime.hhs_runtime_graphics_service_v1`

The existing FastAPI router now performs only:

```text
FastAPI ingress -> shared HHS service -> FastAPI egress
```

The native path performs:

```text
ASGI ingress -> C11 native route resolution -> shared HHS service -> ASGI egress
```

This preserves the already-established graphics authority boundary:
rendering remains projection-only and neither HTTP membrane can mutate
canonical graphics/VM81 state.

## Equivalence gate

`tests/pass220/test_hhs_pass220_fastapi1_native_route_kernel_v1.py`:

1. compiles the C11 shared object with strict warnings-as-errors;
2. runs the standalone native route/capture harness;
3. builds a conventional FastAPI app with the existing graphics router;
4. builds the FastAPI-free native ASGI app over the C11 route kernel;
5. sends the same requests to both;
6. requires equal status and content type;
7. requires byte-identical JSON response bodies;
8. requires matching 404 behavior;
9. requires matching 405 + Allow behavior;
10. asserts the native modules do not import FastAPI, Starlette, or Pydantic.

## Current boundary

FastAPI is **not yet fully removed**.

FastAPI1 replaces native route resolution for the migrated family and proves a
FastAPI-free ASGI execution path. Remaining FastAPI-equivalence work includes:

- request-body and multipart parsing;
- query/header/cookie dependency binding;
- typed validation;
- exception-handler registration;
- middleware composition;
- lifespan;
- WebSockets;
- OpenAPI/schema generation;
- background tasks/streaming/files;
- dependency injection.

Those surfaces should be migrated incrementally with differential equivalence
tests rather than reimplemented as one unbounded replacement.

## Dependency sequence

The authorized external-library replacement order after this checkpoint is:

```text
FastAPI
  ↓
Pydantic/schema compatibility
  ↓
NumPy
  ↓
native palindromic symbolic float-solving bigint serialization
  ↓
HARMONICODE algebra math engine with NumPy ingress/egress behavior
  ↓
Python execution/runtime compatibility layer
```

For NumPy, floating inputs will be ingress representations only. Canonical
interior arithmetic will use the native exact palindromic/symbolic BigInt and
HARMONICODE algebra substrate, with NumPy-compatible shapes/dtypes/broadcasting
and observable egress behavior proven by differential tests.

## Restart commands

```bash
make -C native_projects/hhs_pass220_fastapi_native_route_kernel clean all test
python -m pytest -q tests/pass220/test_hhs_pass220_fastapi1_native_route_kernel_v1.py
```

## Next FastAPI checkpoint

FastAPI2 should move request/query/header/body decoding and response-schema
validation behind the native compatibility API, then migrate a mutation-capable
route family through the existing VM81 admission membrane. Only after the
FastAPI compatibility surface is sufficiently closed should the NumPy native
translation pass begin.
