"""V162: inherited HNAN exact AST and read-only receipt regressions."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_v162_module194_ordered_hnan_native_boundary_v1 import (
    V162HNANError, verify_inherited_ordered_boundary,
)
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_existing_hnan_jordan_loshu_qgu_receipts_are_executed():
    result = verify_inherited_ordered_boundary(
        source_fixture(), require_upload_identity=False)
    assert result["module194_groups"] == 81
    assert result["module194_reciprocal_pairs"] == 5184
    assert result["inherited_ordered_xy_yx_ast_distinct"]
    assert result["inherited_ordered_zw_wz_ast_distinct"]
    assert result["inherited_hnan_1_over_0_ast_preserved"]
    assert result["inherited_epsilon_residual_retained"]
    for key in ("inherited_jordan_receipt_sha256",
                "inherited_loshu_receipt_sha256",
                "inherited_qgu_receipt_sha256"):
        assert len(result[key]) == 64
    for key in ("native_c_lean_checker_executed_for_module194",
                "module194_fractalization_tensor_equivalence_verified",
                "course_source_freeze_verified", "module194_physical_origin_verified",
                "vm81_admission", "hash72_hash216_minted",
                "physics_mutation_authority"):
        assert result[key] is False


def test_inherited_gate_rejects_wrong_transition():
    from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import hnan_gate
    with pytest.raises(ValueError):
        hnan_gate(0, 1)


def test_source_tampering_rejected():
    with pytest.raises(ValueError, match="SOURCE_CONTRACT_MISMATCH"):
        verify_inherited_ordered_boundary(
            source_fixture().replace(b"m194Prob[g]-=mean", b"m194Prob[g]+=mean"),
            require_upload_identity=False)


def test_fail_closed_if_inherited_jordan_check_is_corrupt(monkeypatch):
    import hhs_runtime.hhs_pass220_v162_module194_ordered_hnan_native_boundary_v1 as v
    monkeypatch.setattr(v, "jordan_refinement_receipt",
                        lambda: {"status": "PASS", "checks": {"rank_m01_3": False},
                                 "receipt_sha256": "0" * 64})
    with pytest.raises(V162HNANError, match="JORDAN_REJECTED"):
        v.verify_inherited_ordered_boundary(source_fixture(), require_upload_identity=False)


def test_fail_closed_if_inherited_hnan_source_check_fails(monkeypatch):
    import hhs_runtime.hhs_pass220_v162_module194_ordered_hnan_native_boundary_v1 as v
    monkeypatch.setattr(v, "HNAN_LO_SHU_TENSOR", ((("wrong",), ("Sum", "x", "y"), v.YX),\n                                                       v.HNAN_LO_SHU_TENSOR[1],\n                                                       v.HNAN_LO_SHU_TENSOR[2]))
    with pytest.raises(V162HNANError, match="ORDERED_HNAN_AST_REJECTED"):
        v.verify_inherited_ordered_boundary(source_fixture(), require_upload_identity=False)
