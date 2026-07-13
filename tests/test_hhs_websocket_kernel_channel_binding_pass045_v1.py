from hhs_backend.runtime.websocket_kernel_channel_router_v1 import (
    list_kernel_websocket_channels,
    validate_kernel_channel_payload,
    websocket_kernel_channel_router_self_test,
)


def test_four_kernel_websocket_channels_declared():
    channels = list_kernel_websocket_channels()
    assert channels["channels"] == ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"]


def test_kernel_channel_payload_requires_kernel_fields():
    admitted = validate_kernel_channel_payload({
        "event_type": "runtime",
        "event_hash72": "e" * 72,
        "receipt_hash72": "r" * 72,
        "runtime_state_hash72": "s" * 72,
        "authority": "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1",
    })
    rejected = validate_kernel_channel_payload({"event_type": "runtime"})
    assert admitted["ok"] is True
    assert rejected["ok"] is False
    assert rejected["status"] == "REJECT_NON_KERNEL_WEBSOCKET_PACKET"


def test_websocket_kernel_channel_router_self_test():
    result = websocket_kernel_channel_router_self_test()
    assert result["ok"] is True
