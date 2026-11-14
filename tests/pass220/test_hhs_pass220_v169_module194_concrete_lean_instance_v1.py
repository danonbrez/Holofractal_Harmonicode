"""V169 verifies concrete Lean structural source binding without false closure."""
from __future__ import annotations
from pathlib import Path
import pytest

import hhs_runtime.hhs_pass220_v169_module194_concrete_lean_instance_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_v169_concrete_structural_lean_and_inherited_native_gate():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    out=v.bind_concrete_structural_instance(
        source_fixture(),native._RUNTIME_LIB,require_upload_identity=False)
    assert out["source_81_group_domain_bound"] is True
    assert out["source_128_slot_domain_bound"] is True
    assert out["source_typed_A_B_distinction_bound"] is True
    assert out["source_direct_mirror_phase_order_bound"] is True
    assert len(out["structural_theorem_names"])==10
    assert len(out["concrete_lean_source_sha256"])==64
    for key in ("lean_kernel_executed_in_this_function",
                "noncommutative_AB_BA_product_identity_proved",
                "input_specific_HNAN_delta_e_closure_proved",
                "i051_admitted_hypothesis_discharged",
                "physical_producer_equivalence_verified",
                "canonical_VM81_admission",
                "hash72_hash216_minted"):
        assert out[key] is False


def test_v169_missing_concrete_lean_source_rejected(tmp_path:Path):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    root=Path(".")
    prior="formal/lean/HHS/Alignment/ReciprocalTensor.lean"
    dest=tmp_path/prior
    dest.parent.mkdir(parents=True)
    dest.write_bytes((root/prior).read_bytes())
    with pytest.raises(v.V169LeanInstanceError,match="LEAN_SOURCE_UNAVAILABLE"):
        v.bind_concrete_structural_instance(
            source_fixture(),native._RUNTIME_LIB,
            repository_root=tmp_path,require_upload_identity=False)


def test_v169_native_library_absence_and_source_drift_rejected():
    with pytest.raises(ValueError,match="NATIVE_LIBRARY_REQUIRED"):
        v.bind_concrete_structural_instance(
            source_fixture(),None,require_upload_identity=False)
    with pytest.raises(ValueError,match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.bind_concrete_structural_instance(source_fixture(),None)
