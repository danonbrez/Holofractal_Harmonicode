"""Regression for supplied source and supplementary ordered phase relation.

Projection checks are non-authoritative. Native admission remains the VM81 ABI's job.
"""
from pathlib import Path
from fractions import Fraction

PATH = Path("contracts/pass220/PASS_220_ORDERED_TENSOR_QUOTIENT_USER_SOURCE_20261009.harmonicode")
ORIGINAL = "List(List(List(x==-y,x+y==0,x*y,y==a^2/x),List(z==-w,z+w==0,z*w,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2,c^2==a^2+b^2)/((x*y+z*w)/b^2==a^2+x+y-z-w)),-List(1,1,6,(-8)))"
SUPPLEMENT = "xy+zw=b²"


def _exact_source(text: str) -> bool:
    return text.splitlines() == [ORIGINAL, SUPPLEMENT] and text.endswith("\n")


def test_verbatim_user_source_and_new_relation_are_one_source_envelope() -> None:
    data = PATH.read_bytes()
    text = data.decode("utf-8")
    assert _exact_source(text)
    assert text.count("==") == 10
    assert text.count("\n") == 2
    assert "a^2==c^2-b^2" in ORIGINAL
    assert "a^2==b^2+c^2" not in ORIGINAL
    assert "(x*y+z*w)/b^2==a^2+x+y-z-w" in ORIGINAL
    assert "-List(1,1,6,(-8))" in ORIGINAL
    assert "b²" in SUPPLEMENT


def test_mutations_do_not_inherit_source_identity() -> None:
    text = PATH.read_text(encoding="utf-8")
    assert not _exact_source(text.replace("a^2==c^2-b^2", "a^2==b^2+c^2", 1))
    assert not _exact_source(text.replace("xy+zw=b²", "xy+zw=0", 1))
    assert not _exact_source(text.replace("z*w", "w*z", 1))


def test_projection_only_coordinate_and_correction_balance() -> None:
    a2, b2, c2, e2 = map(Fraction, (1, 2, 3, 8))
    assert [c2-b2-a2, a2-(c2-b2), b2-(c2-a2), c2-(a2+b2)] == [0,0,0,0]
    assert sum((-a2, -a2, -b2*c2, e2)) == 0
    assert (b2/b2) == a2
    # Only an exact scalar projection of the new ASSUMED native source edge.
    # The ordinary complex candidate xy=1, zw=-1 cannot satisfy this edge.
    assert Fraction(1) + Fraction(-1) != b2
