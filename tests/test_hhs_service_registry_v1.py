from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator
from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import (
    MISSING_INTERPOSITION_STATUS,
    SURFACE_MISMATCH_STATUS,
    interpose_runtime_surface,
)


def test_default_service_registry_exposes_guarded_services():
    registry = make_default_service_registry()
    names = {service["name"] for service in registry.services()}

    assert "authority_gate.self_test" in names
    assert "ledger.verify" in names
    assert "c_bridge.abi_self_test" in names

    status = registry.status()
    assert status["authority_audit"]["ok"] is True
    assert status["service_count"] >= 3


def test_service_dispatch_runs_through_authority_and_hash72_ledger():
    registry = make_default_service_registry()
    interposition = registry.interpose_dispatch("authority_gate.self_test")
    record = registry.dispatch(
        "authority_gate.self_test",
        zero_bypass_interposition_token=interposition["interposition_token"],
    )

    assert record["authorized_tick"]["authority_audit"]["ok"] is True
    assert record["post_authority_audit"]["ok"] is True
    assert record["result"]["ok"] is True
    assert record["zero_bypass_interposition"]["propagation_allowed"] is True
    assert record["unified_ledger"]["entry_count"] >= 1


def test_service_dispatch_rejects_direct_uninterposed_call():
    registry = make_default_service_registry()
    record = registry.dispatch("authority_gate.self_test")

    assert record["schema"] == "HHS_SERVICE_DISPATCH_REJECTION_RECORD_V1"
    assert record["zero_bypass_interposition"]["status"] == MISSING_INTERPOSITION_STATUS
    assert record["propagation_allowed"] is False
    assert record["execution_allowed"] is False
    assert record["bypass_attempt"] is True
    assert "authorized_tick" not in record
    assert "result" not in record


def test_service_dispatch_rejects_wrong_surface_token():
    registry = make_default_service_registry()
    wrong_surface = interpose_runtime_surface(
        surface="websocket.broadcast",
        request_class="canonical_full_witness_chain",
    )
    record = registry.dispatch(
        "authority_gate.self_test",
        zero_bypass_interposition_token=wrong_surface["interposition_token"],
    )

    assert record["schema"] == "HHS_SERVICE_DISPATCH_REJECTION_RECORD_V1"
    assert record["zero_bypass_interposition"]["status"] == SURFACE_MISMATCH_STATUS
    assert record["propagation_allowed"] is False
    assert "authorized_tick" not in record


def test_emulator_exposes_guarded_service_dispatch():
    emulator = HHSCEmulator()
    boot = emulator.boot()
    assert any(service["name"] == "authority_gate.self_test" for service in boot["services"])

    record = emulator.dispatch_service("authority_gate.self_test")
    assert record["service"]["name"] == "authority_gate.self_test"
    assert record["post_authority_audit"]["omega"] is True
