"""V168 retains conditional nature of inherited Lean AB/BA closure theorems."""
from __future__ import annotations
from pathlib import Path
import pytest
import hhs_runtime.hhs_pass220_v168_module194_i051_lean_closure_dependency_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_lean_declarations_bind_but_do_not_discharge_input_specific_proof():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    r=v.inspect_module194_i051_dependency(
        source_fixture(), native._RUNTIME_LIB, require_upload_identity=False)
    assert r["i051_lean_module"]=="HHS.Alignment.ReciprocalTensor"
    assert r["i051_contract_closure_names"]==["AB=P^4","BA=-P^4"]
    assert r["i051_required_conditional_theorems"]==list(v.REQUIRED_THEOREMS)
    assert len(r["i051_lean_source_sha256"])==64
    assert len(r["lean_dependency_binding_sha256"])==64
    assert r["lean_source_declarations_matched"] is True
    for name in ("lean_kernel_executed_in_this_check",
                 "module194_specific_lean_hypotheses_discharged",
                 "module194_specific_ab_ba_closure_proved",
                 "module194_interior_outer_closure_proved",
                 "complete_canonical_course_coverage_verified",
                 "physical_producer_equivalence_verified",
                 "vm81_admission","hash72_hash216_minted"):
        assert r[name] is False


def test_drifted_lean_source_fails_closed(tmp_path:Path):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    dest=tmp_path/v.LEAN_PATH
    dest.parent.mkdir(parents=True)
    dest.write_text("namespace HHS.Alignment.ReciprocalTensor\n",encoding="utf-8")
    with pytest.raises(v.V168LeanBindingError,match="I051_DECLARATION_MISSING"):
        v.inspect_module194_i051_dependency(
            source_fixture(),native._RUNTIME_LIB,
            repository_root=tmp_path,require_upload_identity=False)


def test_missing_lean_source_fails_closed(tmp_path:Path):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    with pytest.raises(v.V168LeanBindingError,match="NATIVE_LEAN_SOURCE_UNAVAILABLE"):
        v.inspect_module194_i051_dependency(
            source_fixture(),native._RUNTIME_LIB,
            repository_root=tmp_path,require_upload_identity=False)


def test_untrusted_native_and_source_identity_fail_closed():
    with pytest.raises(ValueError,match="NATIVE_LIBRARY_REQUIRED"):
        v.inspect_module194_i051_dependency(
            source_fixture(),None,require_upload_identity=False)
    with pytest.raises(ValueError,match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.inspect_module194_i051_dependency(source_fixture(),None)
