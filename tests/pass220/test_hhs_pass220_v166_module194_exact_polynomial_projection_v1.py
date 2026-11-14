"""V166 exact coefficient oracle and malformed source regression."""
from __future__ import annotations
import pytest
import hhs_runtime.hhs_pass220_v166_module194_exact_polynomial_projection_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_reference_quadratic_quartic_coefficients():
    assert v._expected_inner(1,2)=={(8,0):1,(4,2):2,(0,4):1}
    assert v._expected_inner(2,0)=={(4,0):1,(8,0):1}
    assert v._expected_inner(2,1)=={(8,0):1,(16,0):1}
    assert v._expected_inner(2,2)=={
        (8,0):1,(4,2):2,(0,4):1,
        (16,0):1,(12,2):4,(8,4):6,(4,6):4,(0,8):1
    }


def test_all_81_exact_projection_entries_bind_real_c_hnan():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    result=v.inspect_exact_projection(
        source_fixture(),native._RUNTIME_LIB,require_upload_identity=False)
    assert result["exact_polynomial_projection_entries_verified"]==81
    assert len(result["exact_projection_coefficient_sha256"])==64
    assert result["exact_integer_coefficients_only"] is True
    assert result["original_ordered_tensor_preserved"] is True
    for name in ("native_ab_ba_closure_for_input_proved",
                 "typed_interior_outer_closure_proved",
                 "complete_196_module_source_coverage_verified",
                 "physical_force_equivalence_proved",
                 "vm81_admission","hash72_hash216_minted"):
        assert result[name] is False


def test_wrong_exponent_is_caught_without_native_promotion(monkeypatch):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    original=v.flattened_source_tensor
    def altered():
        items=list(original())
        i,j,r,k,node=items[2]
        items[2]=(i,j,r,k,("OrderedWeight",node[1],
                             ("Sum",("Power",("CellSymbol","a"),4),
                                     ("Power",("CellSymbol","b"),4))))
        return tuple(items)
    monkeypatch.setattr(v,"flattened_source_tensor",altered)
    with pytest.raises(v.V166ProjectionError,match="EXACT_POLYNOMIAL_MISMATCH"):
        v.inspect_exact_projection(
            source_fixture(),native._RUNTIME_LIB,require_upload_identity=False)


def test_reordered_loshu_weight_rejected(monkeypatch):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    original=v.flattened_source_tensor
    def altered():
        items=list(original())
        i,j,r,k,node=items[9]
        items[9]=(i,j,r,k,("OrderedWeight",4,node[2]))
        return tuple(items)
    monkeypatch.setattr(v,"flattened_source_tensor",altered)
    with pytest.raises(v.V166ProjectionError,match="LOSHU_WEIGHT_OR_ORDER"):
        v.inspect_exact_projection(
            source_fixture(),native._RUNTIME_LIB,require_upload_identity=False)


def test_missing_native_library_and_source_mutation_rejected():
    with pytest.raises(ValueError,match="NATIVE_LIBRARY_REQUIRED"):
        v.inspect_exact_projection(source_fixture(),None,require_upload_identity=False)
    with pytest.raises(ValueError,match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.inspect_exact_projection(source_fixture(),None)
