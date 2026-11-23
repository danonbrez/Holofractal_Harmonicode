"""I085 exhaustive x/u rational-exponent exact address crosswalk tests."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_i085_x_over_u_rational_vm81_hash72_crosswalk_v1 import (
    I085CrosswalkError, encode_address, decode_address,
    enumerate_all_addresses, formalize_i085, SOURCE_RELATION,
)


def test_all_5184_symbolic_rational_addresses_have_exact_inverse():
    coverage = enumerate_all_addresses()
    assert coverage["distinct_vm81_cell_operation_addresses"] == 5184
    assert coverage["distinct_hash72_geometry_positions"] == 5184
    assert coverage["distinct_exact_rational_exponent_labels"] == 5184
    assert coverage["ordered_basis8_count"] == 8
    assert coverage["all_81_vm81_cells_and_64_operation_slots_covered"] is True
    assert coverage["all_native_cell_values_encoded"] is False
    assert coverage["native_exponent_operator_uniqueness_proven"] is False
    assert coverage["no_hash72_mint"] is True
    assert coverage["no_vm81_mutation"] is True


@pytest.mark.parametrize("pos,vm_cell,operation,hashrow,hashcol", [
    (0,0,0,0,0),
    (63,0,63,0,63),
    (64,1,0,0,64),
    (71,1,7,0,71),
    (72,1,8,1,0),
    (80*64,80,0,71,8),
    (5183,80,63,71,71),
])
def test_inherited_exact_vm81_and_hash72_coordinate_views(
    pos, vm_cell, operation, hashrow, hashcol,
):
    carrier = encode_address(pos)
    assert decode_address(carrier) == pos
    assert carrier["vm81"] == {"cell": vm_cell, "operation64": operation}
    assert carrier["hash72_address_geometry"] == {"row": hashrow,"column":hashcol}
    rational = Fraction(pos,72)
    assert carrier["typed_constructor"]["exponent"] == {
        "numerator": rational.numerator, "denominator": rational.denominator
    }
    assert carrier["operation"]["ordered_symbol"] == (
        "x","y","z","w","xy","yx","zw","wz"
    )[operation%8]
    assert carrier["original_vm81_cell_payload_encoded"] is False
    assert carrier["hash72_cryptographic_ledger_minted"] is False


@pytest.mark.parametrize("pos", [0,1,63,64,71,72,143,144,5039,5040,5183])
def test_q144_pass186_inverse_and_u72_ring_identity(pos):
    r = encode_address(pos)
    q = r["q144"]
    native_address = (
        q["opcode_lane36"]*144 + q["root_row12"]*12 + q["root_col12"]
    )
    assert native_address == pos
    assert q["q144_index"] == pos % 144
    assert q["u72_pair"] == (pos % 144)//72
    assert q["u72_index"] == (pos % 144)%72
    assert r["operation"]["class8"] == r["vm81"]["operation64"]//8
    assert r["operation"]["basis8"] == r["vm81"]["operation64"]%8


def test_ordered_xy_and_yx_are_not_collapsed_by_scalar_magnitude():
    xy, yx = encode_address(4), encode_address(5)
    assert xy["operation"]["ordered_symbol"] == "xy"
    assert yx["operation"]["ordered_symbol"] == "yx"
    assert xy["typed_constructor"]["exponent"] != yx["typed_constructor"]["exponent"]
    assert decode_address(xy) == 4
    assert decode_address(yx) == 5


@pytest.mark.parametrize("bad", [-1,5184,1.0,True,False,"1",None])
def test_no_out_of_range_or_host_float_admission(bad):
    with pytest.raises(I085CrosswalkError, match="exact integer"):
        encode_address(bad)


@pytest.mark.parametrize("change", [
    ("vm81", "cell", 80),
    ("hash72_address_geometry", "row", 2),
    ("q144", "u72_index", 70),
    ("operation", "ordered_symbol", "yx"),
    ("typed_constructor", "formal_symbol", "u^(s/72)"),
    ("typed_constructor", "native_operator_evaluation_proven", True),
])
def test_tampered_native_order_or_source_witness_is_rejected(change):
    carrier = deepcopy(encode_address(4))
    target, key, value = change
    carrier[target][key] = value
    with pytest.raises(I085CrosswalkError, match="changed"):
        decode_address(carrier)


@pytest.mark.parametrize("numerator,denominator", [
    (1,0),(1,-1),(1,73),(1,100),(1,1.0),(True,1),(0,True),
    (-1,72),(5184,72),(5183,0),
])
def test_invalid_rational_exponent_or_out_of_bounds_is_rejected(numerator,denominator):
    carrier = deepcopy(encode_address(5))
    carrier["typed_constructor"]["exponent"] = {
        "numerator": numerator,"denominator":denominator
    }
    with pytest.raises(I085CrosswalkError):
        decode_address(carrier)


def test_complete_report_only_promotes_executed_exhaustive_address_coverage():
    partial = formalize_i085()
    assert partial["source_relation"] == SOURCE_RELATION
    assert partial["fraction_5184_over_72_squared"] == {
        "numerator": 1, "denominator": 1
    }
    assert partial["full_5184_address_bijection"] is False
    complete = formalize_i085(enumerate_all=True)
    assert complete["full_5184_address_bijection"] is True
    assert complete["full_position_enumeration"]["distinct_exact_rational_exponent_labels"] == 5184
    assert complete["inherited_i083_source_identity_sha256"] != complete["inherited_i084_source_identity_sha256"]
    assert complete["original_i082_c_root_relation"] == "c=+sqrt(a²+b²)=+sqrt(3)"
    assert complete["inherited_i071_phase_gear"]["coordinate_closure"] is True
    assert complete["native_universal_tensor_value_encoding_proven"] is False
    assert complete["native_rational_exponent_phases_evaluated"] is False
    assert complete["native_hash72_cryptographic_ledger_equivalence_proven"] is False
    assert complete["native_hash216_lineage_witness_proven"] is False
    assert complete["native_canonical_signed_admission_proven"] is False
    assert complete["canonical_vm81_mutation_authority"] is False
    assert complete["candidate_only"] is True


def test_native_quotient_and_phase_root_obligations_explicit():
    report = formalize_i085()
    assert report["x_over_u_formal_rational_exponent"] == "(x/u)^(s5184/72)"
    assert len(report["native_operator_obligations"]) == 9
    assert "coherent branch" in report["fractional_root_branch_condition"]
    assert report["u72_torus_phase_condition"] == "u^72=1 (original typed phase rule)"
