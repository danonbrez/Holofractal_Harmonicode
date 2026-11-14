"""V170 conditional exact ordered-product premise binding (no false closure)."""
from __future__ import annotations

from pathlib import Path
import pytest
import hhs_runtime.hhs_pass220_v170_module194_ordered_product_proof_dependency_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_v170_binds_exact_lean_premises_but_does_not_mint_ab_ba_witness():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    result = v.inspect_ordered_product_dependency(
        source_fixture(), native._RUNTIME_LIB, require_upload_identity=False)
    assert result["input_specific_AB_value_required"] is True
    assert result["input_specific_BA_value_required"] is True
    assert result["nonzero_P4_witness_required_for_distinct_products"] is True
    assert result["required_theorems"] == list(v.REQUIRED)
    assert len(result["ordered_product_lean_source_sha256"]) == 64
    assert len(result["module194_typed_packet_sha256"]) == 64
    for field in (
        "lean_kernel_executed_in_this_function",
        "input_specific_direct_product_equation_proved",
        "input_specific_reverse_product_equation_proved",
        "input_specific_lean_certificate_constructed",
        "interior_outer_delta_e_closure_proved",
        "full_196_module_course_coverage_verified",
        "module194_force_equivalence_verified",
        "canonical_vm81_admission",
        "hash72_hash216_minted",
    ):
        assert result[field] is False


def test_v170_missing_lean_source_rejected(tmp_path: Path):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    for relative in (
        "formal/lean/HHS/Alignment/ReciprocalTensor.lean",
        "formal/lean/HHS/Pass220/Module194TypedClosure.lean",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((Path(".") / relative).read_bytes())
    with pytest.raises(v.V170OrderedProductError, match="LEAN_SOURCE_UNAVAILABLE"):
        v.inspect_ordered_product_dependency(
            source_fixture(), native._RUNTIME_LIB,
            repository_root=tmp_path, require_upload_identity=False)


def test_v170_missing_native_and_invalid_source_rejected():
    with pytest.raises(ValueError, match="NATIVE_LIBRARY_REQUIRED"):
        v.inspect_ordered_product_dependency(
            source_fixture(), None, require_upload_identity=False)
    with pytest.raises(ValueError, match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.inspect_ordered_product_dependency(source_fixture(), None)
