"""Source-preserving exact checks for the revised signed equality tensor.

The tests here are syntax/projection checks, never a VM81 admission oracle.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import re

SOURCE = "List(List(List(x==-y,x+y==0,x*y,y==a^2/x),List(z==-w,z+w==0,z*w,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==x*y+z*w,c^2==a^2+b^2)/((x*y+z*w)/b^2==a^2+x+y-z-w)),-List(1==z*w,1==x*y,6==b^2*c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))"
PATH = Path("contracts/pass220/PASS_220_ORDERED_TENSOR_SIGNED_EQUALITY_V2_20261009.harmonicode")


def test_exact_source_preserved_without_scalarizing_ordered_gates() -> None:
    data = PATH.read_bytes()
    assert data == (SOURCE + "\n").encode("utf-8")
    assert len(re.findall(r"==", SOURCE)) == 18
    assert "b^2==c^2-a^2==x*y+z*w" in SOURCE
    assert "1==z*w,1==x*y" in SOURCE
    assert "6==b^2*c^2==b^2+c^2+a^2" in SOURCE
    assert "(-(e^2==c^2+d^2==b^6==8))" in SOURCE
    assert SOURCE.startswith("List(List(List(")
    assert SOURCE.endswith("))))")
    # This is the new complete source, not the earlier two-line source + separate equation.
    assert "\n" not in SOURCE


def test_signed_equality_order_cannot_be_reused_for_changed_source() -> None:
    original = sha256(PATH.read_bytes()).hexdigest()
    mutations = (
        SOURCE.replace("x*y+z*w", "z*w+x*y", 1),
        SOURCE.replace("1==z*w,1==x*y", "1==x*y,1==z*w", 1),
        SOURCE.replace("b^2==c^2-a^2==x*y+z*w", "b^2==x*y+z*w==c^2-a^2", 1),
        SOURCE.replace("(-(e^2==c^2+d^2==b^6==8))", "(e^2==c^2+d^2==b^6==8)", 1),
        SOURCE.replace("z*w", "w*z", 1),
    )
    for changed in mutations:
        assert changed != SOURCE
        assert sha256((changed + "\n").encode("utf-8")).hexdigest() != original


def test_exact_coordinate_and_signed_numeric_projection_only() -> None:
    a2, b2, c2, d2, e2 = map(Fraction, [1, 2, 3, 5, 8])
    expected_residuals = [
        c2-b2-a2,
        a2-(c2-b2),
        b2-(c2-a2),
        b2-(1+1),
        c2-(a2+b2),
        (1+1)-b2,
        Fraction(6)-b2*c2,
        Fraction(6)-(b2+c2+a2),
        e2-(c2+d2),
        e2-b2**3,
        e2-Fraction(8),
    ]
    assert expected_residuals == [0] * len(expected_residuals)
    anchors = [-1, -1, -6, 8]
    assert sum(anchors) == 0
    assert sum(map(abs, anchors)) == 16


def test_no_unlicensed_complex_scalar_branch_substitution() -> None:
    # In the ordinary complex projection, z=-w and w=1/w imply zw=-1.
    # This is not a native tensor proof, and cannot establish the new typed zw=1 gate.
    for w in (1, -1):
        z = -w
        assert z*w == -1
        assert z*w != 1
