from hhs_runtime.hhs_runtime_contract_v1 import (
    CONTRACT_VERSION,
    assert_contract,
    make_execution_request,
    make_receipt_contract,
    make_runtime_packet,
    make_service_descriptor_contract,
    make_api_response_contract,
    envelope_api_response,
    runtime_contract_self_test,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway


def test_runtime_contract_builds_and_validates_core_objects():
    fake_hash72 = "H" * 72
    request = make_execution_request("test.contract", "operation", {"b": 2, "a": 1})
    packet = make_runtime_packet("INGRESS", "test.contract", request)
    receipt = make_receipt_contract({"step": 1, "state_hash72": fake_hash72, "receipt_hash72": fake_hash72}, source="test.contract")
    service = make_service_descriptor_contract({
        "name": "demo.service",
        "module": "demo.module",
        "function": "run",
        "service_type": "demo",
    })
    api_response = make_api_response_contract("/api/runtime/state", "GET", {"ok": True})

    for obj, expected in [
        (request, "execution_request"),
        (packet, "runtime_packet"),
        (receipt, "receipt"),
        (service, "service_descriptor"),
        (api_response, "api_response"),
    ]:
        validation = assert_contract(obj, expected_type=expected)
        assert validation["ok"] is True
        assert obj["contract_version"] == CONTRACT_VERSION
        assert len(obj["contract_hash72"]) == 72


def test_service_registry_exposes_canonical_service_contracts():
    registry = make_default_service_registry()
    services = registry.services()
    assert any(service["name"] == "runtime_contract.self_test" for service in services)
    for service in services:
        contract = service["runtime_contract"]
        assert contract["contract_type"] == "service_descriptor"
        assert assert_contract(contract, expected_type="service_descriptor")["ok"] is True

    interposition = registry.interpose_dispatch("runtime_contract.self_test")
    record = registry.dispatch(
        "runtime_contract.self_test",
        zero_bypass_interposition_token=interposition["interposition_token"],
    )
    assert record["execution_request"]["contract_type"] == "execution_request"
    assert record["runtime_packet"]["contract_type"] == "runtime_packet"
    assert record["service_contract"]["contract_type"] == "service_descriptor"
    assert record["result"]["contract_version"] == CONTRACT_VERSION


def test_io_gateway_records_carry_runtime_packet_contract():
    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)
    ingress = gateway.ingress("test.contract.io", {"message": "sealed"})
    contract = ingress["runtime_contract"]
    assert contract["contract_type"] == "runtime_packet"
    assert contract["direction"] == "INGRESS"
    assert assert_contract(contract, expected_type="runtime_packet")["ok"] is True


def test_runtime_contract_self_test_is_valid():
    result = runtime_contract_self_test()
    assert result["schema"] == "HHS_RUNTIME_CONTRACT_SELF_TEST_V1"
    assert all(v["ok"] for v in result["validations"])


def test_api_response_envelope_is_canonical_contract():
    response = envelope_api_response("/api/runtime/demo", "GET", {"schema": "DEMO_RESPONSE", "value": 1})
    contract = response["runtime_contract"]
    assert contract["contract_type"] == "api_response"
    assert contract["route"] == "/api/runtime/demo"
    assert contract["method"] == "GET"
    assert assert_contract(contract, expected_type="api_response")["ok"] is True
