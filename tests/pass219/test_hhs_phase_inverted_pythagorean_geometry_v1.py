from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from hhs_runtime.hhs_phase_inverted_pythagorean_geometry_v1 import (
    A2,
    B2,
    BIPARTITE_COORDINATES,
    C2,
    C4,
    CONTINUATION,
    FINITE_PHASE,
    LO_SHU,
    MANIFOLD,
    P4_COLLAPSE,
    SCIENTIFIC_MATRIX_CELLS,
    VM5184,
    PhaseInvertedPythagoreanError,
    directional_projection_witness,
    factorization_closure_100_witness,
    full_geometry_witness,
    kappa,
    lo_shu_phase_witness,
    manifold_closure_witness,
    one_positional_anchor_witness,
    positive_factor_pairs,
    pq_orientation_witness,
    pythagorean_collapse_witness,
)


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "docs" / "whitepapers" / "HHS_PHASE_INVERTED_PYTHAGOREAN_ENTANGLEMENT_THEOREM_V1.md"
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_PHASE_INVERTED_PYTHAGOREAN_ENTANGLEMENT_THEOREM_V1.md"


def test_exact_pythagorean_seed_and_shared_third_vector() -> None:
    assert (A2, B2, C2) == (1, 2, 3)
    assert C2 == A2 + B2
    assert (C2 - B2, C2 - A2, A2 + B2) == (A2, B2, C2)
    assert C4 == P4_COLLAPSE == 9

    witness = pythagorean_collapse_witness()
    assert witness["triangle_reconstruction"] == [1, 2, 3]
    assert witness["V_Ω"] == 9
    assert witness["p2_branch_selected"] is False
    assert witness["projection_only"] is True
    assert witness["canonical_admission_authority"] is False


def test_lo_shu_magic_geometry_and_phase_partition() -> None:
    assert LO_SHU == ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    rows = [sum(row) for row in LO_SHU]
    columns = [sum(LO_SHU[row][column] for row in range(3)) for column in range(3)]
    diagonals = [sum(LO_SHU[i][i] for i in range(3)), sum(LO_SHU[i][2 - i] for i in range(3))]
    assert rows == [15, 15, 15]
    assert columns == [15, 15, 15]
    assert diagonals == [15, 15]

    assert set(FINITE_PHASE) == {4, 2, 6, 8}
    assert CONTINUATION == frozenset({9, 3, 5, 7, 1})
    assert set(FINITE_PHASE).isdisjoint(CONTINUATION)
    assert set(FINITE_PHASE) | CONTINUATION == set(range(1, 10))

    witness = lo_shu_phase_witness()
    assert witness["finite_count"] == 4
    assert witness["continuation_count"] == 5
    assert witness["delta_phase"] == 18
    assert witness["half_turn"] == 36


def test_lo_shu_complement_is_exact_half_turn() -> None:
    for digit, phase in FINITE_PHASE.items():
        opposite = kappa(digit)
        assert kappa(opposite) == digit
        assert FINITE_PHASE[opposite] == (phase + 36) % 72

    assert kappa(9) == 1
    assert kappa(3) == 7
    assert kappa(5) == 5


def test_pq_symmetric_magnitude_and_antisymmetric_orientation() -> None:
    forward = pq_orientation_witness(p=1, q=3, P=2)
    reverse = pq_orientation_witness(p=3, q=1, P=2)

    assert forward["p_plus_q"] == {"type": "EXACT_RATIONAL", "numerator": 4, "denominator": 1}
    assert forward["pq"] == {"type": "EXACT_RATIONAL", "numerator": 3, "denominator": 1}
    assert forward["sigma"] == {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    assert reverse["sigma"] == {"type": "EXACT_RATIONAL", "numerator": -1, "denominator": 1}
    assert forward["sigma_squared"] == reverse["sigma_squared"] == {
        "type": "EXACT_RATIONAL",
        "numerator": 1,
        "denominator": 1,
    }
    assert forward["orientation_quotient_closed"] is True
    assert reverse["orientation_quotient_closed"] is True


def test_pq_projection_rejects_unlicensed_values_and_floats() -> None:
    with pytest.raises(PhaseInvertedPythagoreanError, match="PQ_PROJECTION_PRECONDITION_FAILED"):
        pq_orientation_witness(p=1, q=4, P=2)
    with pytest.raises(PhaseInvertedPythagoreanError, match="forbids bool/float"):
        pq_orientation_witness(p=1.0, q=3, P=2)


def test_directional_projection_remains_typed_not_globally_commutative() -> None:
    witness = directional_projection_witness()
    assert witness["ordered_source_symbols"] == ["xy", "yx", "zw", "wz"]
    assert witness["typed_projection"] == {"yx": "xy", "zw": "wz"}
    assert witness["global_commutativity_authorized"] is False
    assert witness["normalized_matrix"][1][1] == "(2xy+x+y-z-w-2wz)/5"


def test_one_anchor_preserves_known_position_and_does_not_invent_bigint_index() -> None:
    witness = one_positional_anchor_witness()
    assert witness["scalar_unit"] == 1
    assert witness["lo_shu_position_1based"] == [3, 2]
    assert witness["lo_shu_position_0based"] == [2, 1]
    assert witness["scientific_matrix_shape"] == [10, 10]
    assert witness["scientific_matrix_cells"] == 100
    assert witness["bigint_string_position"] is None
    assert witness["bigint_string_position_resolved"] is False


def test_all_positive_factorizations_of_100_agree() -> None:
    expected = ((1, 100), (2, 50), (4, 25), (5, 20), (10, 10))
    assert SCIENTIFIC_MATRIX_CELLS == 100
    assert positive_factor_pairs(100) == expected
    assert all(left * right == 100 for left, right in expected)

    witness = factorization_closure_100_witness()
    assert witness["positive_factor_pairs"] == [list(pair) for pair in expected]
    assert witness["all_factorizations_agree"] is True
    assert witness["prime_factorization"] == "2²*5²"


def test_72_72_manifold_and_fibonacci_scaling_are_exact() -> None:
    assert VM5184 == 72**2 == 81 * 64 == 5184
    assert MANIFOLD == 72**72 == 5184**36
    assert BIPARTITE_COORDINATES == 144

    witness = manifold_closure_witness()
    assert witness["72²"] == 5184
    assert witness["81*64"] == 5184
    assert witness["72^72"] == MANIFOLD
    assert witness["5184^36"] == MANIFOLD
    assert witness["bipartite_coordinates"] == 144
    assert witness["finite_phi_substitution"] is False
    expected = [
        {"type": "EXACT_RATIONAL", "numerator": value, "denominator": 1}
        for value in (1, 2, 3, 5, 8, 13, 21, 34, 55)
    ]
    assert witness["fibonacci_square_states"] == expected


def test_full_witness_is_deterministic_and_non_authoritative() -> None:
    first = full_geometry_witness()
    second = full_geometry_witness()
    assert first == second
    assert len(first["receipt_sha256"]) == 64
    assert first["projection_only"] is True
    assert first["canonical_admission_authority"] is False
    assert first["floating_point_authority"] is False


def test_whitepaper_preserves_new_source_surface_and_declared_closures() -> None:
    text = PAPER.read_text(encoding="utf-8")
    assert "G³=((P²-pq)×(xA(1.112)+(123.321)×1,000" in text
    assert "Mod(2^81^(-81),72^72)/a^2" in text
    assert "u^72==1" in text
    assert "The 1 symbol is tied to the lo shu 1 cell and it's bigint string position in the 10*10 scientific notation matrix" in text
    assert "The 100 is derived by the closure that requires all factorizations of 100 to agree" in text
    assert "(c²-b², c²-a², a²+b²) = (1,2,3) = (a²,b²,c²)" in text
    assert "72^72 = (72²)^36 = 5184^36" in text


def test_contract_keeps_authority_and_unresolved_position_boundaries() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    required = (
        "canonical_admission_authority = false",
        "Floating-point authority is forbidden",
        "BIGINT_POSITION_INVENTED",
        "FACTOR_100_CLOSURE_FAILED",
        "PQ_ORIENTATION_MISMATCH",
        "72^72 == 5184^36",
    )
    for needle in required:
        assert needle in text
