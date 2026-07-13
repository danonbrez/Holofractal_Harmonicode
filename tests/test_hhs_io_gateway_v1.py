from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway, payload_hash72
from hhs_runtime.hhs_unified_hash72_ledger_v1 import verify_unified_ledger


def test_io_gateway_records_ingress_and_egress_to_unified_ledger():
    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)

    payload_a = {"b": 2, "a": 1}
    payload_b = {"a": 1, "b": 2}
    assert payload_hash72(payload_a) == payload_hash72(payload_b)

    ingress = gateway.ingress("test.io.ingress", payload_a)
    egress = gateway.egress("test.io.egress", {"ok": True})

    assert ingress["schema"] == "HHS_CANONICAL_IO_RECORD_V1"
    assert ingress["direction"] == "INGRESS"
    assert ingress["authority_audit"]["ok"] is True
    assert len(ingress["payload_hash72"]) == 72
    assert egress["direction"] == "EGRESS"
    assert egress["ledger_entry_count"] >= ingress["ledger_entry_count"]
    assert verify_unified_ledger()["ok"] is True


def test_validated_vector_cache_write_requires_backing_receipt():
    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)
    authorized = controller.authorized_tick(source="test.validated_vector_cache_write")

    record = gateway.validate_vector_cache_write(
        source="test.vector_cache",
        key="node:1",
        vector_record={"dimensions": 3, "values": [1, 0, -1]},
        backing_receipt=authorized["receipt"],
    )

    assert record["schema"] == "HHS_VALIDATED_VECTOR_CACHE_RECORD_V1"
    assert record["authority_audit"]["ok"] is True
    assert len(record["vector_hash72"]) == 72
    assert record["unified_ledger"]["entry_count"] >= 1
