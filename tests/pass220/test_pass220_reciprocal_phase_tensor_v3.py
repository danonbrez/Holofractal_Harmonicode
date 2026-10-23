"""Pass 220 source-bound reciprocal tensor V3: checks are not a canonical proof.

Keep V2 frozen. Preserve the LHS inner-only quotient, RHS whole-tensor
quotient and non-commuting ordered product y*x*w*z without scalar promotion.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path

SOURCE = "List((u^72==x*y)/List(List(x==-y,x+y==0,x*y,y==a^2/x),List(z==-w,z+w==0,z*w,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==x*y+z*w,c^2==a^2+b^2)/((x*y+z*w)/b^2==a^2+x+y-z-w)),-List(1==z*w,1==x*y,6==b^2*c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))==List(List(List(x==-y,x+y==0,x*y,y==a^2/x),List(z==-w,z+w==0,z*w,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==x*y+z*w,c^2==a^2+b^2)/((x*y+z*w)/b^2==a^2+x+y-z-w)),-List(1==z*w,1==x*y,6==b^2*c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))/(u^36==(y*x*w*z)/a^2)"
FIXTURE = Path("contracts/pass220/PASS_220_RECIPROCAL_PHASE_TENSOR_V3_20261009.harmonicode")
V2_PATH = Path("contracts/pass220/PASS_220_ORDERED_TENSOR_SIGNED_EQUALITY_V2_20261009.harmonicode")


def top_level_commas(expr: str) -> list[int]:
    depth = 0
    commas: list[int] = []
    for i, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            assert depth >= 0
        elif char == "," and depth == 0:
            commas.append(i)
    assert depth == 0
    return commas


def outer_gate_positions(expr: str) -> list[int]:
    depth = 0
    positions: list[int] = []
    for i, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            assert depth >= 0
        elif expr[i : i + 2] == "==" and depth == 0:
            positions.append(i)
    assert depth == 0
    return positions


def make_expected_source_from_inherited_v2() -> str:
    prior = V2_PATH.read_text(encoding="utf-8").rstrip("\n")
    assert prior.startswith("List(") and prior.endswith(")")
    body = prior[5:-1]
    commas = top_level_commas(body)
    assert len(commas) == 1
    cut = commas[0]
    inner, signed = body[:cut], body[cut + 1 :]
    assert inner.startswith("List(List(")
    assert signed.startswith("-List(")
    assert prior == f"List({inner},{signed})"
    return (
        f"List((u^72==x*y)/{inner},{signed})"
        f"=={prior}/(u^36==(y*x*w*z)/a^2)"
    )


def test_exact_source_has_39_positioned_gates_one_outer_equal_and_two_phase_gates() -> None:
    assert FIXTURE.read_bytes() == (SOURCE + "\n").encode("utf-8")
    assert len(SOURCE.encode("utf-8")) == 518
    assert SOURCE.count("==") == 39
    assert outer_gate_positions(SOURCE) == [253]
    assert SOURCE.startswith("List((u^72==x*y)/List(")
    assert SOURCE.endswith("/(u^36==(y*x*w*z)/a^2)")
    assert "u^72==x*y" in SOURCE
    assert "u^36==(y*x*w*z)/a^2" in SOURCE


def test_copies_match_prior_tensor_but_quotient_scope_is_asymmetric() -> None:
    expected = make_expected_source_from_inherited_v2()
    assert SOURCE == expected
    prior = V2_PATH.read_text(encoding="utf-8").rstrip("\n")
    assert SOURCE.count(prior) == 1  # Whole tensor on RHS.
    assert SOURCE.count("1==z*w") == 2
    assert SOURCE.count("6==b^2*c^2==b^2+c^2+a^2") == 2
    assert SOURCE.count("(-(e^2==c^2+d^2==b^6==8))") == 2


def test_phase_reversal_or_quotient_scope_mutation_changes_source_identity() -> None:
    prior = V2_PATH.read_text(encoding="utf-8").rstrip("\n")
    original = sha256(FIXTURE.read_bytes()).hexdigest()
    changed_sources = [
        SOURCE.replace("y*x*w*z", "x*y*z*w", 1),
        SOURCE.replace("u^72==x*y", "u^36==x*y", 1),
        SOURCE.replace("u^36==(y*x*w*z)/a^2", "u^72==(y*x*w*z)/a^2", 1),
        SOURCE.replace("=="+prior+"/(u^36", "=="+prior+"*(u^36", 1),
        SOURCE.replace("-List(1==z*w", "List(1==z*w", 1),
        SOURCE.replace("1==z*w", "1==w*z", 1),
        SOURCE.replace("=="+prior+"/", "="+prior+"/", 1),
    ]
    assert all(changed != SOURCE for changed in changed_sources)
    for changed in changed_sources:
        assert sha256((changed + "\n").encode("utf-8")).hexdigest() != original


def test_exact_projection_diagnostic_only() -> None:
    a2, b2, c2, d2, e2 = map(Fraction, [1, 2, 3, 5, 8])
    assert [c2-b2-a2, a2-(c2-b2), b2-(c2-a2),
            c2-(a2+b2), Fraction(6)-b2*c2,
            Fraction(6)-(a2+b2+c2), e2-(c2+d2),
            e2-b2**3] == [0]*8
    assert sum([-1, -1, -6, 8]) == 0
    # Conventional commutative phasing cannot supply both the former
    # z=-w, w=1/w branch and the native 1==z*w target.
    for w in (Fraction(1), Fraction(-1)):
        z = -w
        assert z*w == -1
    # The test does not cancel either tensor denominator or promote
    # inner Boolean gates to host rational denominators.
