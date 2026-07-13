# Node/WebSocket Stub Deprecation — Pass 045

The standalone websocket stub has been retired.

Node/Vite is restricted to:

```text
serve GUI
proxy /api to FastAPI
proxy /ws to FastAPI
```

Node/Vite is prohibited from:

```text
generating runtime events
emitting fake runtime_loop packets
acting as kernel authority
creating synthetic graph/replay/transport truth
```

`hhs_runtime/runtime_ws_server.py` is now a compatibility launcher for `hhs_backend.server:app`.
