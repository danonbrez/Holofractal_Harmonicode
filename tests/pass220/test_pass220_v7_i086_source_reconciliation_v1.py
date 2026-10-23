"""Cross-PR V7 / I086 source conservation (not a native matrix-division claim)."""
from pathlib import Path
import pytest

from hhs_runtime.hhs_pass220_v7_ordered_matrix_geometry_v1 import (
    SOURCE as V7_SOURCE, ROWS as V7_ROWS, parse_quotient,
    V7SourceError,
)
from hhs_runtime.hhs_pass220_i086_ordered_3x3_vm5184_hash72_matrix_v1 import (
    SOURCE as I086_SOURCE, SOURCE_DENOMINATOR, SOURCE_RESULT, MATRIX,
    _parse_cell_expression,
)
from hhs_runtime.hhs_pass220_i088_exact_clifford_word_inverse_v1 import (
    SOURCE as I088_SOURCE,
)

FIXTURE=Path("contracts/pass220/PASS_220_V7_VM81_ORDERED_MATRIX_QUOTIENT_20261009.harmonicode")

def test_exact_same_ordered_denominator_and_separate_hash72_output_role():
    assert I086_SOURCE==V7_SOURCE+"=hash72"
    assert I088_SOURCE==I086_SOURCE
    assert SOURCE_RESULT=="hash72"
    assert SOURCE_DENOMINATOR==V7_SOURCE.removeprefix("(81*64)/")
    assert V7_SOURCE.startswith("(81*64)/")
    assert V7_SOURCE.count("((yx,y+w,wx)") == 1
    assert [list(row) for row in MATRIX]==V7_ROWS
    assert FIXTURE.read_bytes()==(V7_SOURCE+"\n").encode("ascii")
    parsed=parse_quotient(FIXTURE.read_bytes())
    assert parsed["matrix"]==V7_ROWS
    assert [v["raw_source_expression"] for v in parsed["source_bound_macro_sites"]] == [
        cell for row in MATRIX for cell in row
    ]
    assert parsed["fixed_width_positions"]==5184
    assert parsed["matrix_denominator_operation"]=="NATIVE_ORDERED_QUOTIENT_UNRESOLVED"
    assert parsed["canonical_hash72_hash216_transition_verified"] is False

def test_hnan_center_and_directed_source_lexemes_stay_ordered():
    center="x+y-z-w+xy+yx-zw-wz"
    assert MATRIX[1][1]==V7_ROWS[1][1]==center
    assert "".join(t["original_lexeme"] for t in _parse_cell_expression(center)["ordered_terms"])==center
    assert MATRIX[0][2]=="wx" and MATRIX[1][0]=="-xy-wz"
    assert MATRIX[0][0]=="yx" and MATRIX[2][0]=="xy"
    assert MATRIX[2][2]=="zw" and MATRIX[1][2]=="-zw-yx"
    assert _parse_cell_expression("wx")["ordered_terms"][0]["operand"]["extended_wx_requires_native_basis_admission"] is True

def test_attempt_to_equip_v7_with_i086_result_is_rejected_as_source_mutation():
    with pytest.raises(V7SourceError, match="UNAUTHORIZED_SOURCE_MUTATION"):
        parse_quotient((I086_SOURCE+"\n").encode("ascii"))
