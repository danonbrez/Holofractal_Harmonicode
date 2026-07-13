"""
HHS WebSocket Kernel Channel Router v1
======================================

Pass 045 declares the four canonical websocket channels as projections of a
single FastAPI kernel authority.  The channels may project runtime, replay,
graph, and transport views, but they may not synthesize runtime truth.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

from hhs_backend.runtime.runtime_ws import runtime_ws_health

VERSION = "PASS_045_WEBSOCKET_KERNEL_CHANNEL_ROUTER_V1"
CHANNELS = ("/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport")


def list_kernel_websocket_channels() -> Dict[str, Any]:
    return {
        "schema": "HHS_WEBSOCKET_KERNEL_CHANNEL_LIST_V1",
        "version": VERSION,
        "authority": "FASTAPI_WEBSOCKET_KERNEL_CHANNEL_ROUTER_V1",
        "channels": list(CHANNELS),
        "projection_rule": "ALL_CHANNEL_PAYLOADS_ORIGINATE_FROM_HHSRuntimeEventEnvelope_OR_WITNESSED_PROJECTION",
    }


def validate_kernel_channel_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = ["event_type", "event_hash72", "receipt_hash72", "runtime_state_hash72", "authority"]
    missing = [field for field in required if not payload.get(field)]
    status = "ADMIT_KERNEL_CHANNEL_PACKET" if not missing else "REJECT_NON_KERNEL_WEBSOCKET_PACKET"
    return {
        "schema": "HHS_WEBSOCKET_KERNEL_CHANNEL_VALIDATION_V1",
        "version": VERSION,
        "ok": not missing,
        "status": status,
        "missing": missing,
        "channel": payload.get("channel"),
        "event_hash72": payload.get("event_hash72"),
    }


def websocket_kernel_channel_router_self_test() -> Dict[str, Any]:
    channels = list_kernel_websocket_channels()
    health = runtime_ws_health()
    sample = validate_kernel_channel_payload({
        "event_type": "runtime",
        "event_hash72": "x" * 72,
        "receipt_hash72": "r" * 72,
        "runtime_state_hash72": "s" * 72,
        "authority": "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1",
        "channel": "/ws/runtime",
    })
    rejected = validate_kernel_channel_payload({"event_type": "runtime"})
    return {
        "schema": "HHS_WEBSOCKET_KERNEL_CHANNEL_ROUTER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(len(channels["channels"]) == 4 and sample.get("ok") and not rejected.get("ok")),
        "channels": channels,
        "health": health,
        "sample": sample,
        "rejected": rejected,
    }


if __name__ == "__main__":
    print(websocket_kernel_channel_router_self_test())
