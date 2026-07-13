from hhs_runtime.hhs_hash72_kernel_authority_v1 import (
    hash72_kernel_authority_self_test,
    make_hash72_kernel_witness,
)
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger


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


def test_unified_ledger_uses_kernel_hash72_authority(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    append_payload("TEST", "kernel_authority", {"x": 1, "y": 2}, ledger_path=ledger_path)
    verification = verify_unified_ledger(ledger_path)
    assert verification["ok"] is True
    assert verification["hash72_authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
