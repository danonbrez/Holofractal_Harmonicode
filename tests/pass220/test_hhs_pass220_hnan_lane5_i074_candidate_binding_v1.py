"""End-to-end candidate receipts across I148, HNAN, I074 and I065."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256

import pytest

import hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 as binding
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    build_candidate as build_i074_candidate,
)


@pytest.fixture(scope="module")
def inherited_i074():
    return build_i074_candidate()


def test_one_full_native_candidate_lineage(inherited_i074, monkeypatch) -> None:
    # I074's native source/hydration contract already validates its builder;
    # use inherited validation for externally supplied candidates separately.
    monkeypatch.setattr(binding, "build_i074_candidate", lambda: inherited_i074)
    raw = "".join(f"{b:08b}" for b in sha256(b"HNAN").digest()) * 81
    assert len(raw) == 20736  # ensure the input fixture is not silently truncated
    raw = raw[:5184]
    receipt = binding.execute_candidate(raw)
    assert receipt["raw5184_sha256"] == sha256(raw.encode("ascii")).hexdigest()
    assert receipt["raw5184_width"] == 5184
    assert receipt["vm81_cells"] == 81
    assert receipt["trinary_role_quads"] == 20
    assert receipt["radix_binary_triples"] == 1728
    assert receipt["radix_balanced_trits"] == 3456
    assert receipt["radix_base64_sextets"] == 864
    assert receipt["i074_hash216"] == (
        receipt["i074_previous_hash72"]
        + receipt["i074_change_hash72"]
        + receipt["i074_receipt_hash72"]
    )
    assert receipt["i074_hash216_components"] == 15552
    assert receipt["hash72_expanded_vertices"] == 0
    assert receipt["candidate_only"] is True
    assert receipt["hnan_terminal_source"] == "xy+epsilon"
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_commit_authority"] is False
    assert receipt["canonical_hash216_persistence_authority"] is False
    assert len(receipt["candidate_receipt_sha256"]) == 64


def test_lineage_break_rejected_before_ingress(inherited_i074, monkeypatch) -> None:
    bad = deepcopy(inherited_i074)
    bad["candidate_hash216"] = bad["candidate_hash216"][1:] + bad["candidate_hash216"][:1]
    monkeypatch.setattr(binding, "build_i074_candidate", lambda: bad)
    with pytest.raises(binding.Lane5HNANBindingError, match="HASH216_ORDERED"):
        binding.execute_candidate("0" * 5184)


def test_missing_hash216_hydration_rejected(inherited_i074, monkeypatch) -> None:
    bad = deepcopy(inherited_i074)
    bad["hydration"]["roundtrip_exact"] = False
    monkeypatch.setattr(binding, "build_i074_candidate", lambda: bad)
    with pytest.raises(binding.Lane5HNANBindingError, match="HYDRATION_NOT_ADMITTED"):
        binding.execute_candidate("0" * 5184)


def test_external_candidate_must_use_inherited_validator(inherited_i074, monkeypatch) -> None:
    def reject_external(_candidate):
        raise ValueError("native I074 validation rejected supplied candidate")
    monkeypatch.setattr(binding, "validate_i074_candidate", reject_external)
    with pytest.raises(ValueError, match="native I074 validation"):
        binding.execute_candidate("0" * 5184, candidate=inherited_i074)


def test_missing_palindrome_rejected_only_when_requested(inherited_i074, monkeypatch):
    from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import I065HydrationError
    monkeypatch.setattr(binding, "build_i074_candidate", lambda: inherited_i074)
    with pytest.raises(I065HydrationError):
        binding.execute_candidate("1" + "0" * 5183, require_i065_palindrome=True)
