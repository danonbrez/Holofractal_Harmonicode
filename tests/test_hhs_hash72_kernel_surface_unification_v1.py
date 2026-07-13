from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway, payload_hash72_witness
from hhs_runtime.hhs_semantic_memory_guard_v1 import semantic_hash72_witness, commit_semantic_record
from hhs_runtime.hhs_runtime_contract_v1 import payload_hash72_witness as contract_payload_hash72_witness, make_runtime_packet
from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController


def _assert_kernel_witness(witness):
    assert witness["schema"] == "HHS_HASH72_KERNEL_WITNESS_V1"
    assert witness["zero_sum"] is True
    assert len(witness["dna"]) == 72
    assert len(witness["digest"]) == 72
    assert len(witness["positions"]) == 72
    assert len(witness["rotation_profile"]) == 72
    assert witness["trace_count"] >= 1


def test_contract_io_and_semantic_hashes_emit_kernel_witnesses():
    payload = {"b": 2, "a": 1, "message": "kernel surface unification"}
    _assert_kernel_witness(payload_hash72_witness(payload))
    _assert_kernel_witness(semantic_hash72_witness(payload))
    _assert_kernel_witness(contract_payload_hash72_witness(payload))


def test_io_records_include_payload_and_vector_kernel_witnesses():
    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)
    ingress = gateway.ingress("test.kernel_surface.ingress", {"value": 179971})
    _assert_kernel_witness(ingress["payload_hash72_kernel_witness"])

    authorized = controller.authorized_tick(source="test.kernel_surface.vector")
    vector = gateway.validate_vector_cache_write(
        source="test.kernel_surface.vector",
        key="kernel-surface-vector",
        vector_record={"dims": 3, "values": [1, 0, -1]},
        backing_receipt=authorized["receipt"],
    )
    _assert_kernel_witness(vector["vector_hash72_kernel_witness"])


def test_semantic_guard_record_includes_kernel_witness():
    record = commit_semantic_record("KERNEL_SURFACE", "test.kernel_surface.semantic", {"text": "meaning conservation"})
    _assert_kernel_witness(record["payload_hash72_kernel_witness"])


def test_runtime_packet_contract_payload_hash_is_kernel_backed():
    packet = make_runtime_packet("PROPAGATION", "test.kernel_surface.contract", {"value": "contract"})
    _assert_kernel_witness(contract_payload_hash72_witness(packet["payload"]))
    assert packet["payload_hash72"] == contract_payload_hash72_witness(packet["payload"])["digest"]
