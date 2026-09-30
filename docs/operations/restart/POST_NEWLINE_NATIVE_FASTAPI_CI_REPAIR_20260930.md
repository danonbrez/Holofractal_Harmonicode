# Post-newline native FastAPI CI repair — 2026-09-30

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base commit: `03cfd529a7d99e76f920404f46497b09242ee635`
- Branch: `agent/post-newline-native-fastapi-ci-repair-20260930`
- Merge target: `main`

## Trigger

After the escaped-newline repair closed with `HHS Source Text Integrity = SUCCESS` and `HHS Consensus Gate = SUCCESS`, two independent CI failures remained.

### HHS Immutable Agent SQL Index

The inherited server-boundary suite failed during collection:

```text
AttributeError: 'NativeAPIRouter' object has no attribute 'on_startup'
```

Cause: the Lane 5 FastAPI provider had already been imported in native mode earlier in the pytest process. `server.py` correctly declares the canonical external FastAPI application boundary, but Python module caching left `runtime_ws_router` as a `NativeAPIRouter`. Passing that declaration object directly to `FastAPI.include_router()` incorrectly treated it as FastAPI's internal router type.

### Lane 5 Native Capability Provider

The native-core regression intentionally proves external FastAPI is absent. Four service-registry tests then failed because:

```text
hhs_backend/websocket/runtime_stream_manager.py
from fastapi import WebSocket
ModuleNotFoundError: No module named 'fastapi'
```

This was a direct external dependency leak around the Lane 5 provider membrane.

## Repair

- route `runtime_stream_manager.WebSocket` through `hhs_fastapi_provider_v1`;
- add `bind_native_router_to_external_app()` to the native compatibility membrane;
- project deferred native HTTP/WebSocket declarations into the external application with public `add_api_route` / `add_api_websocket_route` surfaces;
- in `server.py`, detect a cached `NativeAPIRouter` at the external composition boundary and bind it explicitly rather than passing it to `FastAPI.include_router()`;
- preserve normal `app.include_router()` behavior when the selected router is already external;
- add dependency-scoped regressions for boundary projection and the WebSocket provider import membrane.

## Authority preservation

The adapter grants no canonical VM81, Hash72, Hash216, or persistence authority. Native route declarations remain the declaration source. External FastAPI is only the server ingress/egress composition boundary.

## Validation remaining

- Lane 5 Native Capability Provider workflow;
- HHS Immutable Agent SQL Index workflow;
- source-text integrity / consensus regression;
- merge and verify main.

## Next action

Open a dependency-scoped PR, inspect the two previously failing workflows, repair-forward only newly exposed failures, then merge when the dependency cone is green or checkpoint per repository CI policy.
