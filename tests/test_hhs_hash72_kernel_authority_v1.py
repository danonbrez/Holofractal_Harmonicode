import pytest

from hhs_python.runtime.hhs_ctypes_bridge import HHSHash72RingBridge
from hhs_runtime.hhs_hash72_kernel_authority_v1 import (
    HASH72_LEN,
    _transport_bytes,
    canonical_payload,
    hash72_kernel_authority_self_test,
    make_hash72_kernel_witness,
)
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger


def _legacy_bytewise_export(label, value):
    """Reference the pre-acceleration bytewise Python->C transport exactly."""

    payload = canonical_payload(value)
    ring = HHSHash72RingBridge()
    transport = _transport_bytes(label, payload)
    last_delta = 0

    for offset, byte in enumerate(transport):
        index = offset % HASH72_LEN
        delta = ((byte + offset) % HASH72_LEN) or HASH72_LEN
        last_delta = delta
        assert ring.rotate(index, delta) is True

    return payload, transport, last_delta, ring.export()


def test_hash72_kernel_authority_self_test():
    result = hash72_kernel_authority_self_test()
    assert result["ok"] is True
    assert result["witness"]["zero_sum"] is True
    assert len(result["witness"]["dna"]) == 72
    assert len(result["witness"]["rotation_profile"]) == 72


def test_kernel_witness_is_deterministic_for_canonical_payload_order():
    a = make_hash72_kernel_witness("canonical", {"b": 2, "a": 1})
    b = make_hash72_kernel_witness("canonical", {"a": 1, "b": 2})
    assert a.digest == b.digest
    assert a.dna == b.dna
    assert a.zero_sum and b.zero_sum


@pytest.mark.parametrize(
    ("label", "value", "width"),
    [
        ("empty", "", 24),
        ("canonical", {"b": 2, "a": 1}, 72),
        ("unicode", {"text": "Lo Shu ⟷ Hash72 — Ω"}, 48),
        ("multi-ring", {"payload": "abc123" * 113}, 72),
        ("large-reference", {"payload": "HHS" * 4096}, 72),
    ],
)
def test_aggregated_transport_is_exactly_equivalent_to_legacy_bytewise_trace(label, value, width):
    payload, transport, last_delta, legacy = _legacy_bytewise_export(label, value)
    optimized = make_hash72_kernel_witness(label, value, width=width)

    assert optimized.canonical_payload == payload
    assert optimized.dna == legacy["dna"]
    assert optimized.digest == legacy["dna"][:width]
    assert optimized.zero_sum == bool(legacy["zero_sum"])
    assert optimized.trace_count == len(transport) == legacy["trace_count"]
    assert optimized.rotation_profile == legacy["rotation_profile"]
    assert optimized.positions == legacy["positions"]
    assert legacy["last_index"] == (len(transport) - 1) % HASH72_LEN
    assert legacy["last_delta"] == last_delta


def test_unified_ledger_uses_kernel_hash72_authority(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    append_payload("TEST", "kernel_authority", {"x": 1, "y": 2}, ledger_path=ledger_path)
    verification = verify_unified_ledger(ledger_path)
    assert verification["ok"] is True
    assert verification["hash72_authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
