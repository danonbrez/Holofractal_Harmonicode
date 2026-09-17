from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WHITEPAPER = ROOT / "docs" / "whitepapers" / "HHS_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_V1.md"
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


def test_runtime_surface_matches_whitepaper_boundary() -> None:
    paper = read(WHITEPAPER)
    contract = read(CONTRACT)
    header = read(HEADER)
    source = read(SOURCE)

    for needle in (
        "HHS-L144-011",
        "c⁴ = 9",
        "I72(I72(q)) = q",
        "J(J(k,o)) = (k,o)",
        "DEVELOPMENT_CANDIDATE",
        "not derivable from `q=-1` alone",
    ):
        assert needle in paper, needle

    for needle in (
        "projected_P4 == 9",
        "candidate_only = 1",
        "canonical_vm81_mutation_authority = 0",
        "does not encode `ab-ba=0`",
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
    ):
        assert needle in header, needle

    assert "hhs_lane5_p149_inverse_phase" in source
    assert "HHS_EXACT_PASS192_FIB_MAX_DEPTH" in source
