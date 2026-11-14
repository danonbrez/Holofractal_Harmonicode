"""V164 actually calls inherited C HNAN ABI; no source-freeze bypass."""
from __future__ import annotations

import pytest
from hhs_runtime.hhs_pass220_v164_module194_inherited_native_hnan_163_v1 import (
    V164NativeHNANError, execute_module194_native_hnan_scope,
)
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_native_hnan_global_and_ordered_rules_executed():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    result = execute_module194_native_hnan_scope(
        source_fixture(), native._RUNTIME_LIB, require_upload_identity=False,
    )
    assert result["native_inherited_global_hnan_gate_executed"] is True
    assert result["native_mandatory_rule_mask"] == 0x7fff
    assert result["native_ordered_hnan_rule_ids_verified"] == [10, 11, 12, 13]
    assert result["module194_groups"] == 81
    assert result["module194_reciprocal_pairs"] == 5184
    for key in ("module194_81_tensor_native_equivalence_verified",
                "course_source_freeze_verified",
                "course_module4_full_proof_executed",
                "module194_physical_producer_verified",
                "lean_module194_checker_executed",
                "canonical_vm81_admission", "hash72_hash216_minted"):
        assert result[key] is False


def test_missing_native_library_rejected():
    with pytest.raises(V164NativeHNANError, match="NATIVE_LIBRARY_REQUIRED"):
        execute_module194_native_hnan_scope(
            source_fixture(), None, require_upload_identity=False)


def test_source_mutation_rejected_before_native_verifier():
    with pytest.raises(ValueError, match="SOURCE_CONTRACT_MISMATCH"):
        execute_module194_native_hnan_scope(
            source_fixture().replace(b"i+5184", b"i+5183"),
            None, require_upload_identity=False)


def test_untrusted_fake_native_verifier_does_not_admit():
    class InvalidNative:
        def __getattr__(self, name):
            raise AttributeError(name)
    with pytest.raises(V164NativeHNANError, match="NATIVE_ABI_UNAVAILABLE"):
        execute_module194_native_hnan_scope(
            source_fixture(), InvalidNative(), require_upload_identity=False)
