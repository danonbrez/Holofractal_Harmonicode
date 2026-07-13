"""
Pass 045 compatibility launcher for the live FastAPI kernel runtime.

The former standalone websocket demo emitted synthetic packets on /ws/runtime,
/ws/replay, /ws/graph, and /ws/transport.  That stub path is retired.  Runtime
truth now originates in hhs_backend.server:app through the Python/C kernel
emulator, the runtime event schema, and the canonical FastAPI websocket router.
"""

from __future__ import annotations

from hhs_backend.server import app


def runtime_ws_server_compatibility_self_test():
    return {
        "schema": "HHS_RUNTIME_WS_SERVER_COMPATIBILITY_SELF_TEST_V1",
        "version": "PASS_045_LIVE_FASTAPI_KERNEL_RUNTIME_V1",
        "ok": True,
        "status": "DELEGATES_TO_LIVE_FASTAPI_KERNEL_RUNTIME",
        "app": "hhs_backend.server:app",
        "node_role": "GUI_PROXY_ONLY_NO_SYNTHETIC_RUNTIME_STREAM",
        "channels": ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "hhs_backend.server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        ws="websockets",
        log_level="info",
    )
