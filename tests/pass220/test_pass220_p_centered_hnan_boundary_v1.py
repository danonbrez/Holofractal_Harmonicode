"""Pass 220: sole-free-P centered boundary conformance (read-only).

This test makes no claim that scalar exceptional quotients are natively
evaluated. It checks their exact singularity locations and the *existing*
HNAN typed boundary graph, without minting VM81/Hash72/Hash216 state.
"""
from fractions import Fraction
import json
from pathlib import Path

import pytest

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_GATE_10,
    HNAN_LO_SHU_TENSOR,
    HNAN_NUMERATOR,
    HNAN_TERMINAL_XY_EPSILON,
    XY, YX, ZW, WZ,
    hnan_gate,
    hnan_loshu_resolution_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "contracts/pass219/PASS_219_LANE5_HNAN_GLOBAL_CONSTRAINT_GRAPH_1_63.json"


@pytest.mark.parametrize("P", [-1000, -5, -2, 2, 3, 37, 10**100])
def test_integer_centered_family_exact(P):
    p, q = P - 1, P + 1
    assert q - p == 2
    assert p + q == 2 * P
    assert P * P - p * q == 1
    assert Fraction((q - p) * P, p + q) == 1
    assert Fraction(p, q) * Fraction(q, p) == 1
    assert isinstance(p, int) and isinstance(q, int)


@pytest.mark.parametrize("P", [Fraction(1, 2), Fraction(-7, 3), Fraction(17, 5)])
def test_fractional_projection_closes_without_integer_admission(P):
    p, q = P - 1, P + 1
    assert P * P - p * q == 1
    assert (q - p) * P / (p + q) == 1
    assert (p / q) * (q / p) == 1
    assert not all(z.denominator == 1 for z in (P, p, q))


@pytest.mark.parametrize("P,zero_target", [(-1, "q"), (0, "p+q"), (1, "p")])
def test_exact_three_scalar_singularities_have_native_boundary_witness(P, zero_target):
    p, q = P - 1, P + 1
    assert P * P - p * q == 1
    assert {"p": p, "q": q, "p+q": p+q}[zero_target] == 0
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    rules = {(row[1], row[2], row[3]) for row in graph["rules"]}
    assert ("ONE_OVER_ZERO", "HNAN_GATE", "HNAN_BOUNDARY") in rules
    assert ("J2_ZERO", "HNAN_GATE", "JORDAN_CORRESPONDENCE") in rules
    assert ("ZERO", "EMPTYSET", "ORDERED_CLOSURE") in rules
    assert graph["mandatory_rule_mask"] == 0x7FFF
    assert "replace_HNAN_with_scalar_division" in graph["forbidden"]
    assert graph["authority"]["canonical_vm81_mutation_authority"] is False
    assert graph["authority"]["canonical_hash216_authority"] is False


def test_inherited_ordered_hnan_center_and_terminal_are_unchanged():
    receipt = hnan_loshu_resolution_receipt()
    assert receipt["status"] == "PASS"
    assert hnan_gate(1, 0) == HNAN_GATE_10
    assert HNAN_LO_SHU_TENSOR[1][1] == HNAN_NUMERATOR
    assert HNAN_LO_SHU_TENSOR[0][0] == XY
    assert HNAN_LO_SHU_TENSOR[0][2] == YX
    assert HNAN_LO_SHU_TENSOR[2][0] == WZ
    assert HNAN_LO_SHU_TENSOR[2][2] == ZW
    assert XY != YX and ZW != WZ
    assert HNAN_TERMINAL_XY_EPSILON != XY


def test_no_unlicensed_reverse_or_scalar_exceptional_gate():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    assert graph["resolution_precedence"][0] == "SOURCE_ORDER"
    assert "reverse_ordered_closure" in graph["forbidden"]
    assert "cancel_DELTA" in graph["forbidden"]
    assert "cancel_EMPTYSET" in graph["forbidden"]
