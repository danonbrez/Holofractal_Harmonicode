from hhs_backend.runtime.live_kernel_event_bridge_v1 import live_kernel_event_bridge_self_test
from hhs_backend.runtime.live_fastapi_workflow_v1 import live_fastapi_workflow_self_test


def test_live_kernel_event_bridge_emits_real_kernel_state():
    result = live_kernel_event_bridge_self_test()
    assert result["ok"] is True
    assert result["authority"] == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"
    assert result["receipt_hash72"]
    assert result["runtime_state_hash72"]


def test_live_fastapi_workflow_startup_prime_without_background_tick():
    result = live_fastapi_workflow_self_test()
    assert result["ok"] is True
    assert result["startup_status"]["authority_ready"] is True
    assert result["startup_status"]["startup_prime_complete"] is True
    assert result["startup_status"]["background_task_active"] is False
    assert result["startup_status"]["tick_count"] == 1
    assert result["emission"]["receipt_hash72"]
    assert result["emission"]["runtime_state_hash72"]
    assert result["emission"]["channels"] == ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"]
