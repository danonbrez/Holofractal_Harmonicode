"""Pass220 I086 nine-cell Hash72 matrix quotient source/phase tests."""
from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime import hhs_pass220_i086_ordered_3x3_vm5184_hash72_matrix_v1 as mod
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import HNAN_CENTER_EXPRESSION

SOURCE = "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"


def test_exact_verbatim_source_and_all_nine_ordered_cell_positions():
    report = mod.formalize_i086()
    assert report["source_equation"] == SOURCE
    assert report["matrix_denominator_exact_source"] == SOURCE.split("/")[1].split("=hash72")[0]
    assert mod.MATRIX == (
        ("yx", "y+w", "wx"),
        ("-xy-wz", "x+y-z-w+xy+yx-zw-wz", "-zw-yx"),
        ("xy", "x-z", "zw"),
    )
    assert report["matrix_center_original_HNAN_exact_match"] is True
    assert report["matrix"][1][1]["native_matrix_expression"] == HNAN_CENTER_EXPRESSION
    assert [
        (cell["row"],cell["column"],cell["lo_shu_local_address"],cell["lo_shu_value"])
        for row in report["matrix"] for cell in row
    ] == [
        (0,0,0,4),(0,1,1,9),(0,2,2,2),
        (1,0,3,3),(1,1,4,5),(1,2,5,7),
        (2,0,6,8),(2,1,7,1),(2,2,8,6)
    ]
    assert all(not cell["matrix_cell_scalarized"] for row in report["matrix"] for cell in row)


def test_distinct_product_order_and_extended_wx_are_not_collapsed():
    expr = mod.matrix_cell(0,2)["native_ordered_ast"]
    assert expr["ordered_terms"][0]["operand"]["source_token"] == "wx"
    assert expr["ordered_terms"][0]["operand"]["left"]["symbol"] == "w"
    assert expr["ordered_terms"][0]["operand"]["right"]["symbol"] == "x"
    assert expr["ordered_terms"][0]["operand"]["registered_original_phase8"] is False
    assert expr["ordered_terms"][0]["operand"]["extended_wx_requires_native_basis_admission"] is True

    xy = mod.matrix_cell(2,0)["native_ordered_ast"]["ordered_terms"][0]["operand"]
    yx = mod.matrix_cell(0,0)["native_ordered_ast"]["ordered_terms"][0]["operand"]
    assert xy["left"]["symbol"] == "x" and xy["right"]["symbol"] == "y"
    assert yx["left"]["symbol"] == "y" and yx["right"]["symbol"] == "x"
    assert xy != yx
    assert expr["evaluate_native_products_as_host_scalar"] is False


def test_exact_signed_center_and_negative_lexemes_in_original_order():
    c = mod.matrix_cell(1,1)["native_ordered_ast"]
    assert [t["original_lexeme"] for t in c["ordered_terms"]] == [
        "x","+y","-z","-w","+xy","+yx","-zw","-wz"
    ]
    assert [t["sign"] for t in c["ordered_terms"]] == [1,1,-1,-1,1,1,-1,-1]
    assert mod.matrix_cell(1,0)["native_ordered_ast"]["ordered_terms"][0]["original_lexeme"] == "-xy"
    assert [t["original_lexeme"] for t in mod.matrix_cell(1,2)["native_ordered_ast"]["ordered_terms"]] == [
        "-zw","-yx"
    ]
    assert mod.matrix_cell(2,1)["native_ordered_ast"]["ordered_terms"][1]["original_lexeme"] == "-z"


@pytest.mark.parametrize("bad",["wx-wq","xy/zw","a²","x--y","yx z","", "x+z*2","xy+yx)"])
def test_unknown_native_phase_operator_is_not_silently_admitted(bad):
    with pytest.raises(mod.I086OrderedMatrixError):
        mod._parse_cell_expression(bad)


@pytest.mark.parametrize("row,col",[(3,0),(0,3),(-1,1),(True,0),(1,False),(1,1.0)])
def test_invalid_lo_shu_cell_address_fails_closed(row,col):
    with pytest.raises(mod.I086OrderedMatrixError,match="exact integer"):
        mod.matrix_cell(row,col)


def test_denominator_is_typed_matrix_not_divided_or_hash_receipt_minted():
    report = mod.formalize_i086()
    node = report["ordered_equation_ast"]
    assert node["source"] == SOURCE
    assert node["left"]["head"] == "HHS_ORDERED_MATRIX_QUOTIENT"
    assert node["left"]["numerator"]["exact_integer_cardinality"] == 5184
    assert node["left"]["denominator"]["head"] == "HHS_POSITIONED_3X3_ORDERED_PHASE_MATRIX"
    assert node["left"]["denominator"]["native_inverse_computed"] is False
    assert node["left"]["division_side_and_native_inverse_proven"] is False
    assert node["right"]["head"] == "HHS_TYPED_HASH72_RESULT_OBLIGATION"
    assert node["right"]["canonical_72_glyph_ledger_equality_proven"] is False
    assert node["source_ordered_equality_not_symmetric_scalar_rewrite"] is True
    assert report["candidate_hash72_is_not_canonical_hash72_ledger"] is True
    assert len(report["candidate_hash72_word_from_original_I069_hash_function"]) == 72
    assert len(report["source_identity_sha256"]) == 64
    assert report["native_5184_divided_by_matrix_evaluated"] is False
    assert report["canonical_hash72_equation_proven"] is False
    assert report["canonical_hash216_receipt_proven"] is False
    assert report["universal_tensor_value_encoding_proven"] is False
    assert report["canonical_vm81_mutation_authority"] is False
    assert len(report["native_operator_obligations"]) == 10


def test_exhaustive_vm81_5184_matrix_address_lifts_cover_all_source_cells():
    coverage=mod.enumerate_all_vm5184_matrix_positions()
    assert coverage["all_5184_position_lifts_executed"] is True
    assert coverage["distinct_nucleus_cell_class_basis_positions"] == 5184
    assert coverage["original_matrix_cells"] == 9
    assert coverage["vm81_nuclei"] == 9
    assert coverage["matrix_phase_slots_per_nucleus"] == 72
    assert coverage["vm81_classes_per_phase"] == 8
    assert coverage["9_times_72_times_8_equals_5184"] is True
    assert coverage["matrix_operators_executed"] is False


@pytest.mark.parametrize("s", [0,4,5,63,64,71,72,511,512,575,576,4608,5183])
def test_inherited_pass186_vm81_i085_hash_geometry_and_i071_slot(s):
    carrier=mod.lift_vm5184_matrix_position(s)
    assert carrier["s5184"] == s
    cell=s//64
    local=cell%9
    operation=s%64
    assert carrier["vm81_cell"] == cell
    assert carrier["vm81_nucleus"] == cell//9
    assert carrier["vm81_operation64"] == operation
    assert carrier["operation_class8"] == operation//8
    assert carrier["operation_basis8"] == operation%8
    assert carrier["i071_phase_slot"] == 9*(operation%8)+local
    assert carrier["matrix_cell"]["native_matrix_expression"] == mod.MATRIX[local//3][local%3]
    assert carrier["inherited_i085_hash72_geometry"] == {"row":s//72,"column":s%72}
    assert carrier["candidate_only"] is True


@pytest.mark.parametrize("bad", [-1,5184,1.1,True,False,None,"0"])
def test_invalid_full_vm5184_position_never_coerced(bad):
    with pytest.raises(mod.I086OrderedMatrixError,match="bounded exact integer"):
        mod.lift_vm5184_matrix_position(bad)


def test_original_i070_i071_real_phase_candidate_and_hash72_binding_for_matrix():
    receipt=mod.verify_original_i071_matrix_phase_surface(nucleus_index=0)
    assert receipt["original_i070_i071_real_native_candidate_invoked"] is True
    assert receipt["nucleus"] == 0
    assert receipt["phase_slots"] == 72
    assert receipt["matrix_cell_values_matched_original_lo_shu"] is True
    assert len(receipt["i070_binding_hash72_candidate"]) == 72
    assert receipt["canonical_hash72_admitted"] is False
    r=mod.formalize_i086(enumerate_positions=False,verify_phase_nucleus=8)
    assert r["original_i070_i071_phase_binding"]["nucleus"] == 8
    assert r["position_coverage"]["all_5184_position_lifts_executed"] is False


def test_full_explicit_admission_exercises_5184_positions_without_hash_mint():
    r=mod.formalize_i086(enumerate_positions=True)
    assert r["position_coverage"]["all_5184_position_lifts_executed"] is True
    assert r["canonical_hash72_mint_authority"] is False
    assert r["candidate_only"] is True
    assert r["native_5184_divided_by_matrix_evaluated"] is False


def test_new_matrix_not_mistaken_for_original_hnan_perimeter(monkeypatch):
    """Center has inherited identity but wx is not in original eight-basis."""
    changed=deepcopy(mod.MATRIX)
    changed=list(map(list,changed))
    changed[1][1]="x+y-z-w+xy+yx-wz-zw"
    monkeypatch.setattr(mod,"MATRIX",tuple(tuple(row) for row in changed))
    with pytest.raises(mod.I086OrderedMatrixError,match="source text drift|matrix"):
        mod.formalize_i086(enumerate_positions=True)
