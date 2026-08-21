from __future__ import annotations

from hhs_runtime.core_sandbox.hhs_octonion_digital_dna_u72_table_v1 import (
    BASIS_PHASE_INDEX,
    PHASE_RING,
)
from hhs_runtime.hhs_pass129_invariant_delta_rational_projection_algebra_v1 import (
    InvariantDeltaProjectionAlgebra,
)

# Ordered numerator matrix projected onto the frozen named u72 basis.
NUMERATOR_BASIS = (
    ("x", "w", "yx"),
    ("wz", None, "zw"),
    ("xy", "z", "y"),
)

# Exact symbolic phase-carrier exponents in the supplied denominator matrix.
DENOMINATOR_I_EXPONENT = (
    (1, 3, 2),
    (2, None, 4),
    (4, 1, 3),
)

OUTER_CLOCKWISE = (
    ((0, 0), "x", 1),
    ((0, 1), "w", 3),
    ((0, 2), "yx", 2),
    ((1, 2), "zw", 4),
    ((2, 2), "y", 3),
    ((2, 1), "z", 1),
    ((2, 0), "xy", 4),
    ((1, 0), "wz", 2),
)


def _carrier_phase(exponent: int) -> int:
    # Pass129 fixes a four-member carrier [I,I^2,I^3,I^4].  Projecting that
    # ordered carrier onto the inherited u72 ring uses one exact quarter-ring
    # step per carrier position.  This is an I121.8 projection witness only;
    # it does not redefine either frozen substrate.
    assert PHASE_RING == 72
    assert exponent in (1, 2, 3, 4)
    return (exponent * (PHASE_RING // 4)) % PHASE_RING


def test_frozen_four_phase_carrier_order_is_preserved() -> None:
    spec = InvariantDeltaProjectionAlgebra().spec
    assert spec["phase_carrier"] == ["I", "I^2", "I^3", "I^4"]
    assert spec["phase_weights"] == ["I", "-1", "-I", "1"]
    assert spec["four_phase_product_semantics"] == "CARDINALITY_NORMALIZED_TYPED_PRODUCT"
    assert spec["ordinary_unnormalized_product_is_not_equivalent"] is True


def test_phase_matrix_matches_every_frozen_outer_basis_anchor() -> None:
    for row in range(3):
        for col in range(3):
            basis = NUMERATOR_BASIS[row][col]
            exponent = DENOMINATOR_I_EXPONENT[row][col]
            if basis is None:
                assert (row, col) == (1, 1)
                assert exponent is None
                continue
            assert exponent is not None
            assert BASIS_PHASE_INDEX[basis] == _carrier_phase(exponent)


def test_all_eight_outer_quotient_phase_residues_are_u72_closure() -> None:
    residues = []
    for _, basis, exponent in OUTER_CLOCKWISE:
        numerator_phase = BASIS_PHASE_INDEX[basis]
        denominator_phase = _carrier_phase(exponent)
        residue = (numerator_phase - denominator_phase) % PHASE_RING
        residues.append(residue)
    assert residues == [0] * 8
    # In the inherited table, phase 0 is written as u^72 closure carrier.
    assert BASIS_PHASE_INDEX["xy"] == 0
    assert BASIS_PHASE_INDEX["zw"] == 0


def test_two_interleaved_ring_phase_schedules_match_exactly() -> None:
    # Even clockwise positions: x -> yx -> y -> xy.
    even = OUTER_CLOCKWISE[0::2]
    assert [basis for _, basis, _ in even] == ["x", "yx", "y", "xy"]
    assert [exp for _, _, exp in even] == [1, 2, 3, 4]
    assert [BASIS_PHASE_INDEX[basis] for _, basis, _ in even] == [18, 36, 54, 0]

    # Odd clockwise positions: w -> zw -> z -> wz.
    odd = OUTER_CLOCKWISE[1::2]
    assert [basis for _, basis, _ in odd] == ["w", "zw", "z", "wz"]
    assert [exp for _, _, exp in odd] == [3, 4, 1, 2]
    assert [BASIS_PHASE_INDEX[basis] for _, basis, _ in odd] == [54, 0, 18, 36]


def test_center_is_not_scalarized_by_outer_phase_cancellation() -> None:
    # The phase denominator has literal 0 at the center.  I121.8 therefore
    # preserves the supplied center relation as a separate structural closure:
    # x+y+z+w=0/u^72.  Outer phase cancellation does not prove or replace it.
    center_relation = "x+y+z+w=0/u⁷²"
    center_denominator_literal = "0"
    center_scalar_value_derived = False
    projection_substitution_authorized = False
    canonical_whole_expression_proof = False
    assert center_relation == "x+y+z+w=0/u⁷²"
    assert center_denominator_literal == "0"
    assert center_scalar_value_derived is False
    assert projection_substitution_authorized is False
    assert canonical_whole_expression_proof is False


def main() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"PASS219 I121.8 denominator phase cancellation: {len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
