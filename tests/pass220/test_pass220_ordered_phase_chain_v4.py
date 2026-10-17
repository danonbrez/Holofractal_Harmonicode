"""V4 source-bound two-edge outer chain, inheriting all V3 tensor constraints.

All projection assertions are non-authoritative. No host Boolean quotient.
"""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

SOURCE = "List((u^72==x*y)/List(List(x==-y,x+y==0,x*y,y==a^2/x),List(z==-w,z+w==0,z*w,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==x*y+z*w,c^2==a^2+b^2)/((x*y+z*w)/b^2==a^2+x+y-z-w)),-List(1==z*w,1==x*y,6==b^2*c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))==x==-y*(List(List(List(x==-y,x+y==0,x*y,y==a^2/x),List(z==-w,z+w==0,z*w,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==x*y+z*w,c^2==a^2+b^2)/((x*y+z*w)/b^2==a^2+x+y-z-w)),-List(1==z*w,1==x*y,6==b^2*c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))/(u^36==(y*x*w*z)/a^2))"
V4 = Path("contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode")
V3 = Path("contracts/pass220/PASS_220_RECIPROCAL_PHASE_TENSOR_V3_20261009.harmonicode")


def top_level_equalities(text: str) -> list[int]:
    depth = 0
    offsets: list[int] = []
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            assert depth >= 0
        elif text[i:i+2] == "==" and depth == 0:
            offsets.append(i)
    assert depth == 0
    return offsets


def test_verbatim_source_two_outer_edges_and_40_gate_occurrences() -> None:
    assert V4.read_bytes() == (SOURCE + "\n").encode("utf-8")
    assert len(SOURCE) == 526
    assert SOURCE.count("==") == 40
    assert top_level_equalities(SOURCE) == [253, 256]
    assert "==x==-y*(" in SOURCE
    assert SOURCE.endswith("/(u^36==(y*x*w*z)/a^2))")
    assert SOURCE.count("u^72==x*y") == 1
    assert SOURCE.count("u^36==(y*x*w*z)/a^2") == 1


def test_strict_v3_lineage_and_unchanged_tensor_copies() -> None:
    previous = V3.read_text(encoding="utf-8").rstrip("\n")
    assert top_level_equalities(previous) == [253]
    left, right = previous[:253], previous[255:]
    assert SOURCE == left + "==x==-y*(" + right + ")"
    assert SOURCE[:253] == left
    assert SOURCE[262:-1] == right
    assert SOURCE.count("1==z*w,1==x*y") == 2
    assert SOURCE.count("6==b^2*c^2==b^2+c^2+a^2") == 2
    assert SOURCE.count("(-(e^2==c^2+d^2==b^6==8))") == 2
    assert SOURCE.count("x==-y") == 3
    assert SOURCE.count("b^2==c^2-a^2==x*y+z*w") == 2


def test_outer_chain_and_orientation_mutations_change_identity() -> None:
    exact_hash = sha256(V4.read_bytes()).hexdigest()
    mutated = (
        SOURCE.replace("==x==-y*(", "==-y==x*(", 1),
        SOURCE.replace("==x==-y*(", "==x==-y/(", 1),
        SOURCE.replace("==x==-y*(", "==-y*(", 1),
        SOURCE.replace("==x==-y*(", "==x==-y*", 1),
        SOURCE.replace("y*x*w*z", "x*y*z*w", 1),
        SOURCE.replace("u^72==x*y", "u^36==x*y", 1),
        SOURCE.replace("1==z*w", "1==w*z", 1),
        SOURCE.replace("(-(e^2==c^2+d^2==b^6==8))", "(e^2==c^2+d^2==b^6==8)", 1),
    )
    assert all(changed != SOURCE for changed in mutated)
    for changed in mutated:
        assert sha256((changed + "\n").encode("utf-8")).hexdigest() != exact_hash


def test_coordinate_and_phase_projection_boundaries_remain_distinct() -> None:
    a2,b2,c2,d2,e2 = map(Fraction, (1,2,3,5,8))
    residuals = [
        c2-b2-a2, a2-(c2-b2), b2-(c2-a2), c2-(a2+b2),
        Fraction(6)-b2*c2, Fraction(6)-(b2+c2+a2),
        e2-(c2+d2), e2-b2**3,
    ]
    assert residuals == [0]*len(residuals)
    assert sum((-1,-1,-6,8)) == 0
    # Diagnostic only: the older scalar complex phase branches cannot prove
    # the typed native 1==z*w gate, and cannot substitute for a global witness.
    for w in (Fraction(1),Fraction(-1)):
        assert (-w)*w == -1


def test_outer_chain_is_not_a_conventional_scalar_identity() -> None:
    offsets = top_level_equalities(SOURCE)
    left = SOURCE[:offsets[0]]
    middle = SOURCE[offsets[0]+2:offsets[1]]
    right = SOURCE[offsets[1]+2:]
    assert middle == "x"
    assert right.startswith("-y*(")
    assert right.endswith(")")
    assert "u^72==x*y" in left
    assert "u^36==(y*x*w*z)/a^2" in right
    assert not right.startswith("-y*List(")  # Preserve the grouping.
