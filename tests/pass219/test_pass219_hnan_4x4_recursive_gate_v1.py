from __future__ import annotations

import json
from pathlib import Path

import pytest

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_CENTER_EXPRESSION,
    HNAN_GATE_10,
    HNAN_NUMERATOR,
    HNAN_ZERO_CLOSURE_SOURCE,
    M01_JORDAN_STRUCTURE,
    MXY_GENERIC_CONDITIONS,
    SERIALIZED_4X4,
    STATE_0,
    STATE_1,
    TENSOR_01,
    TENSOR_XY,
    WZ,
    XY,
    YX,
    ZW,
    HNANGateError,
    deserialize_4x4,
    hnan_gate,
    invariant_receipt,
    jordan_refinement_receipt,
    materialize_xy_view,
    materialize_xy_view_reference,
    recursive_two_view,
    recursive_two_view_reference,
    serialize_4x4,
)


def test_serialized_4x4_round_trip_and_balance():
    assert len(SERIALIZED_4X4) == 16
    assert deserialize_4x4(SERIALIZED_4X4) == TENSOR_01
    assert serialize_4x4(TENSOR_01) == SERIALIZED_4X4
    assert SERIALIZED_4X4.count(0) == 8
    assert SERIALIZED_4X4.count(1) == 8


def test_two_views_are_synchronized_and_reuse_immutable_cache():
    assert materialize_xy_view_reference() == TENSOR_XY
    assert materialize_xy_view() is TENSOR_XY
    assert sum(
        cell == STATE_0 for row in TENSOR_XY for cell in row
    ) == 8
    assert sum(
        cell == STATE_1 for row in TENSOR_XY for cell in row
    ) == 8


def test_hnan_gate_preserves_ordered_channels_and_emptyset_denominator():
    assert XY != YX
    assert ZW != WZ
    assert HNAN_NUMERATOR == (
        "Sum",
        "x",
        "y",
        ("Negate", "z"),
        ("Negate", "w"),
        XY,
        YX,
        ("Negate", ZW),
        ("Negate", WZ),
    )
    assert hnan_gate(1, 0) == HNAN_GATE_10
    assert HNAN_GATE_10[-1] == "EmptySet"
    assert HNAN_GATE_10 != ("Quotient", STATE_1, STATE_0)


def test_hnan_gate_fails_closed_for_undefined_binary_pairs():
    for pair in ((0, 0), (0, 1), (1, 1), (False, 0), (1, True)):
        with pytest.raises(HNANGateError):
            hnan_gate(*pair)


def test_recursive_two_view_lifts_exact_10_gate_without_scalarization():
    source = (
        "Envelope",
        TENSOR_01,
        ("Quotient", 1, 0),
        ("OrderedPair", 0, 1),
    )
    reference = recursive_two_view_reference(source)
    optimized = recursive_two_view(source)
    assert optimized == reference
    assert optimized[1] == TENSOR_XY
    assert optimized[2] == HNAN_GATE_10
    assert optimized[3] == ("OrderedPair", STATE_0, STATE_1)


def test_receipt_closes_without_canonical_authority():
    receipt = invariant_receipt()
    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())
    assert receipt["hnan_center_expression"] == HNAN_CENTER_EXPRESSION
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["host_scalar_division_authorized"] is False
    assert receipt["ordered_product_commutation_authorized"] is False
    assert len(receipt["receipt_sha256"]) == 64


def test_existing_lane5_center_expression_is_identical():
    source = Path(
        "hhs_runtime/pass219/lane5_genesis_orientation_u9_qe_bridge.py"
    ).read_text(encoding="utf-8")
    assert f'"{HNAN_CENTER_EXPRESSION}"' in source


def test_wolfram_evidence_closed():
    evidence = json.loads(
        Path(
            "evidence/pass219/"
            "hnan_4x4_recursive_gate_wolfram_20260926_v1.output.json"
        ).read_text(encoding="utf-8")
    )
    assert evidence["status"] == "PASS"
    assert evidence["check_count"] == 16
    assert evidence["pass_count"] == 16
    assert evidence["failed"] == []
    assert evidence["xy_yx_distinct"] is True
    assert evidence["zw_wz_distinct"] is True


def test_exact_jordan_refinement_receipt_closes():
    receipt = jordan_refinement_receipt()
    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())
    assert receipt["rank_m01"] == 3
    assert receipt["nullity_m01"] == 1
    assert receipt["nullity_m01_squared"] == 2
    assert (
        receipt["characteristic_polynomial"]
        == "lambda^2*(lambda-2)*(lambda+1)"
    )
    assert receipt["minimal_polynomial"] == receipt["characteristic_polynomial"]
    assert receipt["jordan_structure"] == M01_JORDAN_STRUCTURE
    assert receipt["generic_lift_conditions"] == MXY_GENERIC_CONDITIONS
    assert receipt["special_loci"]["r=s"]["nullity_for_r_nonzero"] == 3
    assert receipt["special_loci"]["r=-s"]["nullity_for_r_nonzero"] == 2
    assert receipt["hnan_zero_closure_source"] == HNAN_ZERO_CLOSURE_SOURCE
    assert HNAN_ZERO_CLOSURE_SOURCE == "0=∅=AB/P⁴∅=HNAN"
    assert receipt["zero_closure_scalar_cancellation_authorized"] is False


def test_jordan_wolfram_evidence_closed_and_generic_scope_exact():
    evidence = json.loads(
        Path(
            "evidence/pass219/"
            "hnan_4x4_jordan_refinement_wolfram_20260926_v1.output.json"
        ).read_text(encoding="utf-8")
    )
    assert evidence["status"] == "PASS"
    assert evidence["rank_m01"] == 3
    assert evidence["nullity_m01"] == 1
    assert evidence["nullity_m01_squared"] == 2
    assert evidence["degree4_recurrence_exact"] is True
    assert evidence["lower_degree_recurrence_excluded_by_independence"] is True
    assert evidence["jordan_zero_chain_depth_2"] is True
    assert evidence["minimal_polynomial_equals_characteristic_polynomial"] is True
    assert evidence["lifted_recurrence_exact"] is True
    assert evidence["generic_lift_conditions"] == ["r!=s", "r+s!=0"]
    assert evidence["generic_nullity_mxy"] == 1
    assert evidence["generic_nullity_mxy_squared"] == 2
    assert evidence["generic_krylov_rank_I_M_M2_M3"] == 4
    assert evidence["r_equals_s_nullity"] == 3
    assert evidence["r_equals_minus_s_nullity"] == 2
    assert evidence["sum_invariant_n1_to_n4"] == [True, True, True, True]
