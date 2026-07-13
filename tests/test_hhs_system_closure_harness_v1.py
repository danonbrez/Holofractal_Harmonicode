import asyncio

from hhs_runtime.hhs_system_closure_harness_v1 import system_closure_harness_self_test
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
from hhs_backend.api import runtime_routes


def _assert_hash72(value):
    assert isinstance(value, str)
    assert len(value) == 72


def test_system_closure_harness_converges_normalized_signature():
    result = system_closure_harness_self_test({"cycles": 2, "A": 1.0005, "B": 1.0, "max_steps": 2})
    assert result["schema"] == "HHS_SYSTEM_CLOSURE_HARNESS_V1"
    assert result["ok"] is True
    assert result["converged"] is True
    assert len(set(result["closure_signatures"])) == 1
    _assert_hash72(result["stable_signature"])
    assert result["ledger"]["ok"] is True

    first_cycle = result["cycles"][0]
    assert first_cycle["schema"] == "HHS_SYSTEM_CLOSURE_CYCLE_SUMMARY_V1"
    _assert_hash72(first_cycle["closure_signature"])
    assert first_cycle["closure_witness"]["schema"] == "HHS_HASH72_KERNEL_WITNESS_V1"
    assert first_cycle["closure_witness"]["zero_sum"] is True
    _assert_hash72(first_cycle["ingress_payload_hash72"])
    _assert_hash72(first_cycle["semantic_payload_hash72"])
    _assert_hash72(first_cycle["vector_hash72"])
    _assert_hash72(first_cycle["egress_payload_hash72"])
    assert first_cycle["srcg"]["ok"] is True
    assert first_cycle["srcg"]["trace_zero_sum"] is True
    assert first_cycle["srcg"]["quartic_carrier_preserved"] is True
    assert first_cycle["api_response_contract"]["contract_type"] == "api_response"
    assert first_cycle["io"]["ingress_direction"] == "INGRESS"
    assert first_cycle["io"]["egress_direction"] == "EGRESS"


def test_system_closure_harness_registered_as_guarded_service():
    registry = make_default_service_registry()
    assert registry.has_service("system_closure.harness_self_test")
    payload = {"cycles": 2}
    interposition = registry.interpose_dispatch("system_closure.harness_self_test", payload)
    dispatch = registry.dispatch(
        "system_closure.harness_self_test",
        payload,
        zero_bypass_interposition_token=interposition["interposition_token"],
    )
    assert dispatch["schema"] == "HHS_SERVICE_DISPATCH_RECORD_V1"
    assert dispatch["result"]["ok"] is True
    assert dispatch["result"]["converged"] is True
    assert dispatch["post_authority_audit"]["ok"] is True


def test_system_closure_harness_backend_route_emits_api_contract():
    response = asyncio.run(
        runtime_routes.system_closure_harness(
            runtime_routes.ClosureHarnessRequest(cycles=2, A=1.0005, B=1.0, max_steps=2)
        )
    )
    assert response["schema"] == "HHS_SYSTEM_CLOSURE_HARNESS_V1"
    assert response["ok"] is True
    assert response["converged"] is True
    assert response["runtime_contract"]["contract_type"] == "api_response"
    assert response["runtime_contract"]["route"] == "/api/runtime/closure/harness"
    assert response["io"]["ingress"]["direction"] == "INGRESS"
    assert response["io"]["egress"]["direction"] == "EGRESS"
