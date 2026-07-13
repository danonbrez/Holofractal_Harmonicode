# Pass 045 — Live FastAPI Kernel Runtime

Pass 045 promotes the Python FastAPI backend to the authoritative live runtime server.

## Doctrine

Node/Vite may serve and proxy the GUI, but it may not synthesize runtime truth.
Runtime websocket packets must originate from the Python/C kernel runtime, the canonical runtime event schema, or a witnessed replay/graph/transport projection of that event.

## Live path

```text
Python/C kernel emulator
→ LiveKernelEventBridge
→ HHSRuntimeEventEnvelope
→ FastAPI websocket router
→ /ws/runtime, /ws/replay, /ws/graph, /ws/transport
→ GUI RuntimeSocketManager
```

## Added modules

- `hhs_backend/runtime/live_kernel_event_bridge_v1.py`
- `hhs_backend/runtime/live_fastapi_workflow_v1.py`
- `hhs_backend/runtime/websocket_kernel_channel_router_v1.py`
- `hhs_backend/runtime/node_proxy_contract_v1.py`

## Server bindings

- `hhs_backend/server.py` now includes `runtime_ws_router`.
- `hhs_backend/server.py` owns `LIVE_WORKFLOW`.
- `GET /api/runtime/live/status` returns bounded live workflow state.
- `POST /api/runtime/live/tick` emits one live kernel tick through the four websocket channels.

## Compatibility change

`hhs_runtime/runtime_ws_server.py` no longer emits synthetic demo packets. It delegates to `hhs_backend.server:app`.
