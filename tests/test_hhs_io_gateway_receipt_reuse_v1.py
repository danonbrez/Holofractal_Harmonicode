from pathlib import Path

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway


def test_repeated_unchanged_get_reuses_committed_io_records(tmp_path: Path, monkeypatch):
    path = tmp_path / "gateway-ledger.json"
    monkeypatch.setattr(ledger, "default_unified_ledger_path", lambda: path)

    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)

    first_ingress = gateway.ingress("api.runtime.state", {"method": "GET"})
    first_egress = gateway.egress(
        "api.runtime.state",
        {"method": "GET", "step": controller.latest_runtime_state().get("step")},
    )
    first_count = ledger.unified_ledger_summary(path)["entry_count"]

    second_ingress = gateway.ingress("api.runtime.state", {"method": "GET"})
    second_egress = gateway.egress(
        "api.runtime.state",
        {"method": "GET", "step": controller.latest_runtime_state().get("step")},
    )
    second_count = ledger.unified_ledger_summary(path)["entry_count"]

    assert first_count == 2
    assert second_count == first_count
    assert second_ingress["io_id"] == first_ingress["io_id"]
    assert second_egress["io_id"] == first_egress["io_id"]
    assert second_ingress["cache_reuse"]["reused"] is True
    assert second_egress["cache_reuse"]["reused"] is True


def test_read_reuse_invalidates_when_runtime_state_changes(tmp_path: Path, monkeypatch):
    path = tmp_path / "gateway-ledger.json"
    monkeypatch.setattr(ledger, "default_unified_ledger_path", lambda: path)

    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)

    gateway.ingress("api.runtime.state", {"method": "GET"})
    gateway.egress(
        "api.runtime.state",
        {"method": "GET", "step": controller.latest_runtime_state().get("step")},
    )
    before = ledger.unified_ledger_summary(path)["entry_count"]

    controller.halt()
    changed_ingress = gateway.ingress("api.runtime.state", {"method": "GET"})
    changed_egress = gateway.egress(
        "api.runtime.state",
        {"method": "GET", "step": controller.latest_runtime_state().get("step")},
    )
    after = ledger.unified_ledger_summary(path)["entry_count"]

    assert "cache_reuse" not in changed_ingress
    assert "cache_reuse" not in changed_egress
    assert after == before + 2
