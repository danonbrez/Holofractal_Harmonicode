from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactRuntimeBridge
from hhs_runtime.pass219_quantization_constraint_reference_v1 import (
    A2,
    B2,
    LO_SHU_MAGIC_SUM,
    LO_SHU_POLYNOMIAL_PROJECTION,
    N12,
    N36,
    N66,
    N72,
    N73,
    N5256,
    ORDERED_TAG_XY,
    ORDERED_TAG_YX,
    PHASE_X,
    PHASE_Y,
    ZERO_L,
    build_witness,
    full_cycle_b2_exponent,
    lo_shu_lines,
    metric_closure_identity,
    primitive_b2_exponent,
    quadratic_reciprocity_bit,
    quadratic_reciprocity_lane,
    quadratic_reciprocity_phase,
    reference_invariants,
)

ROOT = Path(__file__).resolve().parents[1]


def test_lo_shu_tensor_polynomial_projection_is_exact() -> None:
    assert LO_SHU_POLYNOMIAL_PROJECTION == ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    assert all(sum(line) == LO_SHU_MAGIC_SUM for line in lo_shu_lines())
    assert LO_SHU_MAGIC_SUM == 15


def test_lo_shu_derived_numerals_close_exactly() -> None:
    assert N12 == 12
    assert N36 == 36
    assert N72 == 72
    assert N73 == 73
    assert N66 == 66
    assert N5256 == 5256
    assert N72 - (B2 * 3) == N66
    assert N72 * N73 == N5256


def test_dyadic_quantization_metric_derivation_is_exact_rational() -> None:
    assert primitive_b2_exponent(A2) == Fraction(-11, 12)
    assert full_cycle_b2_exponent(A2) == -N66
    power, exponent = metric_closure_identity(A2)
    assert power == N5256
    assert exponent == -N66


def test_quadratic_reciprocity_phase_lift_exhausts_odd_residues_mod_n72() -> None:
    for p in range(1, N72, 2):
        for q in range(1, N72, 2):
            expected_bit = A2 if (p % 4 == 3 and q % 4 == 3) else ZERO_L
            assert quadratic_reciprocity_bit(p, q) == expected_bit
            assert quadratic_reciprocity_lane(p, q) == ("yx" if expected_bit == A2 else "xy")
            assert quadratic_reciprocity_phase(p, q) == (N36 if expected_bit == A2 else ZERO_L)


def test_reference_witness_keeps_metric_and_phase_orientation_typed() -> None:
    xy_witness = build_witness(3, 5)
    yx_witness = build_witness(3, 7)
    assert xy_witness.u_power == N5256
    assert xy_witness.full_cycle_b2_exponent == -N66
    assert xy_witness.qr_lane == "xy"
    assert xy_witness.qr_phase == ZERO_L
    assert yx_witness.qr_lane == "yx"
    assert yx_witness.qr_phase == N36


def test_exact_abi_matches_xy_yx_quadratic_reciprocity_phase_pair() -> None:
    assert HHSExactRuntimeBridge.validate()
    xy = HHSExactRuntimeBridge.phase_product(PHASE_X, PHASE_Y)
    yx = HHSExactRuntimeBridge.phase_product(PHASE_Y, PHASE_X)
    assert xy["phase"] == ZERO_L
    assert yx["phase"] == N36
    assert xy["ordered_tag"] == ORDERED_TAG_XY
    assert yx["ordered_tag"] == ORDERED_TAG_YX
    assert xy["ordered_tag"] != yx["ordered_tag"]


def test_xy_yx_phase_witness_is_preserved_for_every_vm81_cell() -> None:
    xy = HHSExactRuntimeBridge.phase_product(PHASE_X, PHASE_Y)
    yx = HHSExactRuntimeBridge.phase_product(PHASE_Y, PHASE_X)
    for cell in range(81):
        xy_address = HHSExactRuntimeBridge.vm5184_address(cell, PHASE_X, PHASE_Y)
        yx_address = HHSExactRuntimeBridge.vm5184_address(cell, PHASE_Y, PHASE_X)
        assert HHSExactRuntimeBridge.vm5184_decode(xy_address) == (cell, PHASE_X, PHASE_Y)
        assert HHSExactRuntimeBridge.vm5184_decode(yx_address) == (cell, PHASE_Y, PHASE_X)
        assert xy["phase"] == ZERO_L
        assert yx["phase"] == N36


def test_entire_vm5184_phase_address_plane_is_exact_and_quarter_cycle_bounded() -> None:
    allowed = {0, 18, 36, 54}
    for address in range(5184):
        cell, left, right = HHSExactRuntimeBridge.vm5184_decode(address)
        assert HHSExactRuntimeBridge.vm5184_address(cell, left, right) == address
        product = HHSExactRuntimeBridge.phase_product(left, right)
        assert product["phase"] in allowed


def test_reference_oracle_has_no_approximate_numeric_authority() -> None:
    source = (ROOT / "hhs_runtime" / "pass219_quantization_constraint_reference_v1.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "float(",
        "double",
        "<math.h>",
        "sqrt(",
        "sin(",
        "cos(",
        "pow(",
        "log(",
        "exp(",
    ):
        assert forbidden not in source


def test_reference_invariant_bundle_is_all_true() -> None:
    assert all(reference_invariants().values())
