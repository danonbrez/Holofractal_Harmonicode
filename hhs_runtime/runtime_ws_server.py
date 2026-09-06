"""Pass 045 compatibility launcher through the Pass170 canonical public gateway.

The former standalone websocket demo emitted synthetic packets on /ws/runtime,
/ws/replay, /ws/graph, and /ws/transport. That stub path remains retired.
Pass219 I172 removes the remaining pre-Pass170 launch bypass: imports and direct
execution now resolve through ``hhs_backend.public_api_server:app`` so the
registered public gateway is composed before any compatibility websocket use.
"""
from __future__ import annotations

from hhs_backend.public_api_server import app


def runtime_ws_server_compatibility_self_test():
    return {
        "schema": "HHS_RUNTIME_WS_SERVER_COMPATIBILITY_SELF_TEST_V1",
        "version": "PASS219-I172-PASS170-CANONICAL-GATEWAY-V1",
        "ok": True,
        "status": "DELEGATES_TO_PASS170_CANONICAL_PUBLIC_GATEWAY",
        "app": "hhs_backend.public_api_server:app",
        "node_role": "GUI_PROXY_ONLY_NO_SYNTHETIC_RUNTIME_STREAM",
        "public_port_authority": False,
        "channels": ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "hhs_backend.public_api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        ws="websockets",
        log_level="info",
    )
