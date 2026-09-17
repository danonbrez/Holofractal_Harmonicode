from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import re

from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import (
    pythagorean_base_witness,
    scale_ladder_witness,
)

ROOT = Path(__file__).resolve().parents[2]
WHITEPAPER = ROOT / "docs" / "whitepapers" / "HHS_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_V1.md"
THEOREM = ROOT / "docs" / "whitepapers" / "HHS_PHASE_INVERTED_PYTHAGOREAN_ENTANGLEMENT_THEOREM_V1.md"
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_1_49.md"
HEADER = ROOT / "hhs_runtime" / "include" / "hhs_pass219_lane5_pythagorean_phase_geometry_1_49.h"
SOURCE = ROOT / "hhs_runtime" / "c" / "hhs_pass219_lane5_pythagorean_phase_geometry_1_49.c"

MATRIX_SHA256 = "d6b3653517009673d3a8732a5884b9c887eef06ed489daeebdb52047b217776a"
COMPLEX_SHA256 = "0359848875ccfc0e7cd28ecf9dae2f2831e6c9b6d4b3ee7f07d5ad4ed970c5c5"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def verbatim_block(marker: str) -> str:
    section = read(WHITEPAPER).split(marker, 1)[1]
    match = re.search(r"```text\n(.*?)\n```", section, flags=re.DOTALL)
    assert match is not None
    return match.group(1)


def exact_rational(value: dict[str, object]) -> Fraction:
    assert value["type"] == "EXACT_RATIONAL"
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def test_verbatim_surfaces_are_preserved() -> None:
    matrix = verbatim_block("### A.1 Matrix/collapse surface")
    complex_surface = verbatim_block("### A.2 ComplexInfinity constructor surface")
    assert len(matrix.encode("utf-8")) == 1629
    assert len(complex_surface.encode("utf-8")) == 620
    assert sha256(matrix.encode("utf-8")).hexdigest() == MATRIX_SHA256
    assert sha256(complex_surface.encode("utf-8")).hexdigest() == COMPLEX_SHA256


def test_derived_exact_constants_and_loshu_geometry() -> None:
    a2, b2, c2 = 1, 2, 3
    assert a2 + b2 == c2
    assert c2 * c2 == 9

    loshu = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    assert [sum(row) for row in loshu] == [15, 15, 15]
    assert [sum(loshu[r][c] for r in range(3)) for c in range(3)] == [15, 15, 15]
    assert sum(loshu[i][i] for i in range(3)) == 15
    assert sum(loshu[i][2 - i] for i in range(3)) == 15
    assert loshu[1][1] == 5

    flat = tuple(value for row in loshu for value in row)
    for index, denominator in enumerate(flat):
        inverse_index = 8 - index
        assert flat[inverse_index] == 10 - denominator
        assert 8 - inverse_index == index

    corner_phase = {4: 0, 2: 18, 6: 36, 8: 54}
    for denominator, phase in corner_phase.items():
        inverse_denominator = 10 - denominator
        assert corner_phase[inverse_denominator] == (phase + 36) % 72

    continuation = {1, 3, 5, 7, 9}
    assert set(flat) - set(corner_phase) == continuation


def test_phase_pair_and_manifold_involutions() -> None:
    phases = (0, 18, 36, 54)
    inverse = {q: (q + 36) % 72 for q in phases}
    assert inverse == {0: 36, 18: 54, 36: 0, 54: 18}
    assert all(inverse[inverse[q]] == q for q in phases)

    for orientation in (0, 1):
        assert ((orientation ^ 1) ^ 1) == orientation

    manifold = 72**72
    assert manifold == 5184**36
    assert manifold.bit_length() == 445


def test_existing_exact_fibonacci_pythagorean_layer_is_reused() -> None:
    base = pythagorean_base_witness()
    assert exact_rational(base["a²"]) == 1
    assert exact_rational(base["b²"]) == 2
    assert exact_rational(base["c²"]) == 3
    assert exact_rational(base["residual"]) == 0
    assert base["projection_only"] is True
    assert base["floating_point_authority"] is False

    ladder = scale_ladder_witness(7)
    states = [exact_rational(value) for value in ladder["square_states"]]
    assert states == [1, 2, 3, 5, 8, 13, 21]
    assert all(exact_rational(value) == 0 for value in ladder["recurrence_residuals"])
    assert ladder["canonical_admission_authority"] is False
    assert ladder["floating_point_authority"] is False


def test_pq_symmetric_antisymmetric_projection_exactly_closes() -> None:
    for p_macro in (-8, -3, -1, 1, 3, 8):
        p = Fraction(p_macro - 1)
        q = Fraction(p_macro + 1)
        P = Fraction(p_macro)
        assert p + q == 2 * P
        assert p * q == P * P - 1
        assert (q - p) * (q - p) == 4
        sigma = (q - p) / 2
        assert sigma in (Fraction(-1), Fraction(1))
        assert ((q - p) * P) / (p + q) == sigma

        p_inv, q_inv = q, p
        assert p_inv + q_inv == p + q
        assert p_inv * q_inv == p * q
        assert (q_inv - p_inv) / 2 == -sigma


def test_runtime_surface_matches_whitepaper_boundary() -> None:
    paper = read(WHITEPAPER) + "\n" + read(THEOREM)
    contract = read(CONTRACT)
    header = read(HEADER)
    source = read(SOURCE)

    for needle in (
        "HHS-L144-011",
        "c⁴ = 9",
        "I72(I72(q)) = q",
        "J(J(k,o)) = (k,o)",
        "kappa(d) = 10-d",
        "q-p = +/-2",
        "DEVELOPMENT_CANDIDATE",
        "not derivable",
        "`q=-1` alone",
    ):
        assert needle in paper, needle

    for needle in (
        "projected_P4 == 9",
        "candidate_only = 1",
        "canonical_vm81_mutation_authority = 0",
        "does not encode `ab-ba=0`",
        "4 finite phase anchors + 5 continuation cells",
    ):
        assert needle in contract, needle

    for needle in (
        "HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_A2",
        "HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_B2",
        "HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C2",
        "HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C4",
        "HHS_EXACT_PASS219_LANE5_PAIR_AB",
        "HHS_EXACT_PASS219_LANE5_PAIR_XY",
        "HHS_EXACT_PASS219_LANE5_PAIR_ZW",
        "HHS_EXACT_PASS219_LANE5_PAIR_PQ",
        "lo_shu_complement_involution_exact",
        "finite_corner_phase_correspondence_exact",
    ):
        assert needle in header, needle

    assert "hhs_lane5_p149_inverse_phase" in source
    assert "hhs_lane5_p149_inverse_lo_shu_cell" in source
    assert "hhs_lane5_p149_corner_phase" in source
    assert "HHS_EXACT_PASS192_FIB_MAX_DEPTH" in source
