from __future__ import annotations

import json


def test_public_authority_status_uses_only_bounded_committed_workflow_projection(monkeypatch):
    from hhs_backend import production_server
    from hhs_backend import server as canonical

    class BoundedWorkflow:
        def authority_status(self):
            return {
                "schema": "HHS_LIVE_FASTAPI_WORKFLOW_AUTHORITY_STATUS_V1",
                "running": True,
                "authority_ready": True,
                "background_task_active": True,
                "tick_count": 7,
                "receipt_ready": True,
                "last_emission": {
                    "ok": True,
                    "event_hash72": "event-hash72",
                    "receipt_hash72": "receipt-hash72",
                    "sequence_id": 7,
                    "kernel_tick": 7,
                    "runtime_state_hash72": "runtime-state-hash72",
                },
                "errors": [],
                "bridge": {
                    "sequence_id": 7,
                    "emulator": {
                        "boot_id": "bounded-authority-test",
                        "runtime_step": 7,
                        "runtime_state_hash72": "runtime-state-hash72",
                        "receipt_hash72": "receipt-hash72",
                        "committed_emission_snapshot": True,
                    },
                },
                "channels": ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"],
                "node_role": "GUI_PROXY_ONLY_NO_RUNTIME_EVENT_AUTHORITY",
                "event_loop_blocking_kernel_work": False,
                "payload_bounded": True,
                "full_cognition_payload_included": False,
                "full_emission_payload_included": False,
            }

        def status(self):
            raise AssertionError("public status must not serialize full workflow diagnostics")

    monkeypatch.setattr(canonical, "LIVE_WORKFLOW", BoundedWorkflow())
    for key in ("runtime_initialized", "graph_initialized", "websocket_ready"):
        monkeypatch.setitem(canonical.SERVER_STATE, key, True)

    status = production_server._runtime_authority_status()
    assert status["ok"] is True
    assert status["status"] == "HHS_RUNTIME_AUTHORITY_ONLINE"
    assert status["status_read_is_bounded"] is True
    assert status["receipt_hash72"] == "receipt-hash72"
    assert status["runtime_state_hash72"] == "runtime-state-hash72"
    assert status["runtime"]["committed_emission_snapshot"] is True
    assert status["runtime"]["bounded_status_projection"] is True
    assert status["runtime"]["mutable_runtime_traversal_performed"] is False
    assert status["live_workflow"]["payload_bounded"] is True
    assert status["live_workflow"]["full_cognition_payload_included"] is False
    assert status["live_workflow"]["full_emission_payload_included"] is False
    assert "cognition" not in status["live_workflow"]
    assert "last_cognition" not in status["live_workflow"]
    assert len(json.dumps(status, sort_keys=True).encode("utf-8")) < 64_000

    workspace = production_server._workspace_session_snapshot()
    assert workspace["runtime"]["live_workflow"]["payload_bounded"] is True
