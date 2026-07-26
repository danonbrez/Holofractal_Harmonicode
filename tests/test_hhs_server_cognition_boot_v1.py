from fastapi.testclient import TestClient

from hhs_backend.server import app


def test_server_lifespan_boots_cognition_and_processes_live_tick():
    with TestClient(app) as client:
        status = client.get("/api/runtime/cognition/status")
        assert status.status_code == 200
        status_body = status.json()
        assert status_body["initialized"] is True
        assert status_body["enabled"] is True

        tick = client.post("/api/runtime/live/tick")
        assert tick.status_code == 200
        tick_body = tick.json()
        assert tick_body["ok"] is True
        assert tick_body["cognition"]["processed"] is True
        assert tick_body["cognition"]["authority_rule"] == (
            "COGNITION_OBSERVES_COMMITTED_RUNTIME_STATE_AND_NEVER_MUTATES_VM81"
        )

        health = client.get("/health")
        assert health.status_code == 200
        cognition = health.json()["live_workflow"]["cognition"]
        assert cognition["processed_ticks"] >= 1
        assert cognition["authority_boundary"]["vm81_mutation"] == "DENIED"
