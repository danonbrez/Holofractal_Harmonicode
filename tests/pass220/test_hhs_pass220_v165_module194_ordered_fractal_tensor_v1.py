"""V165 exact Module194 ordered 3x3x3x3 source and inherited C gate."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_v165_module194_ordered_fractal_tensor_v1 import (
    A2, A4, B2, SEEDS, LO_SHU_ROWS, V165TensorError,
    flattened_source_tensor, fractal_term, inspect_ordered_tensor,
    source_tensor,
)
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_exact_81_entries_preserve_source_exponents_and_order():
    t = source_tensor()
    entries = flattened_source_tensor()
    assert len(entries) == 81
    assert len(set((i,j,r,k) for i,j,r,k,_ in entries)) == 81
    assert LO_SHU_ROWS == ((4,9,2),(3,5,7),(8,1,6))
    assert SEEDS == (
        ("Power", ("CellSymbol","a"),2),
        ("Power", ("CellSymbol","a"),4),
        ("Sum",("Power",("CellSymbol","a"),4),
               ("Power",("CellSymbol","b"),2)),
    )
    assert t[0][0][0][0] == ("OrderedWeight",4,A2)
    assert t[0][0][0][1] == ("OrderedWeight",4,A4)
    assert t[0][0][0][2] == ("OrderedWeight",4,("Sum",A4,B2))
    assert t[0][1][1][0] == ("OrderedWeight",9,("Power",A2,2))
    assert t[1][1][1][1] == ("OrderedWeight",5,("Power",A4,2))
    assert t[2][1][2][2] == (
        "OrderedWeight",1,
        ("Sum",("Power",("Sum",A4,B2),2),
               ("Power",("Sum",A4,B2),4))
    )
    assert t[2][2][2][1] == (
        "OrderedWeight",6,("Sum",("Power",A4,2),("Power",A4,4))
    )
    for i,j,r,k,term in entries:
        assert term == ("OrderedWeight",LO_SHU_ROWS[i][j],fractal_term(SEEDS[k],r))


def test_inherited_native_hnan_precedes_symbolic_tensor_witness():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    result = inspect_ordered_tensor(
        source_fixture(), native._RUNTIME_LIB, require_upload_identity=False
    )
    assert result["ordered_81_source_entries"] == 81
    assert result["particle_group_address_mapping_checked"] is True
    assert result["inherited_native_hnan_rules_verified"] == [10,11,12,13]
    assert result["A_B_distinct_even_if_magnitude_P2"] is True
    assert len(result["fractalization_ast_sha256"]) == 64
    for key in (
        "native_hnan_ab_ba_for_fractal_tensor_proved",
        "native_fractal_tensor_operator_equivalence_proved",
        "native_interior_outer_delta_e_type_resolution_proved",
        "canonical_196_course_complete_source_verified",
        "module194_force_producer_provenance_verified",
        "vm81_admission", "hash72_hash216_minted",
    ):
        assert result[key] is False


def test_source_identity_still_mandatory():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    with pytest.raises(ValueError, match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        inspect_ordered_tensor(source_fixture(), native._RUNTIME_LIB)
    with pytest.raises(ValueError, match="SOURCE_CONTRACT_MISMATCH"):
        inspect_ordered_tensor(
            source_fixture().replace(b"i+5184",b"i+5183"),
            native._RUNTIME_LIB, require_upload_identity=False
        )


def test_unknown_inner_row_rejected():
    with pytest.raises(V165TensorError, match="INNER_ROW_OUT_OF_RANGE"):
        fractal_term(SEEDS[0],3)


def test_fake_native_library_rejected():
    with pytest.raises(ValueError, match="NATIVE_CDLL_REQUIRED"):
        inspect_ordered_tensor(source_fixture(),object(),require_upload_identity=False)
