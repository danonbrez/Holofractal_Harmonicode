"""Pass220 V5: exact two-line tensor/where contract and scoped native source.

The Unicode where clause is part of canonical source, NOT normalized into
algebraic host scalars. The native Pass159 subprobe tests only the literal
outer-component boundary, not the whole composite V5 proof.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
FULL=ROOT/"contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_20261009.harmonicode"
OUTER=ROOT/"contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_OUTER_COMPONENT_20261009.harmonicode"
V4=ROOT/"contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode"
WHERE="where P⁴=AB=c⁴ and A/B≠B/A but P²=pq+(c²/(a²+b²)) and (p+q)/P(q-p)=(xy+zw)/b²"
TRANSFORM_OLD="==x==-y*("
TRANSFORM_NEW="==xA==-yB*("


def exact_source():
    raw=FULL.read_bytes()
    text=raw.decode("utf-8")
    lines=text.splitlines(keepends=True)
    assert len(lines)==2 and all(line.endswith("\n") for line in lines)
    return raw,text,lines[0].removesuffix("\n"),lines[1].removesuffix("\n")


def equality_slots(outer):
    depth=0
    slots=[]
    i=0
    while i<len(outer):
        c=outer[i]
        if c=="(":
            depth+=1
        elif c==")":
            depth-=1
            assert depth>=0
        elif outer[i:i+2]=="==":
            slots.append((i,depth))
            i+=1
        i+=1
    assert depth==0
    return slots


def test_entire_verbatim_unicode_source_is_authority() -> None:
    raw,full,outer,boundary=exact_source()
    assert boundary==WHERE
    assert raw==OUTER.read_bytes()+WHERE.encode("utf-8")+b"\n"
    assert b"\xe2\x81\xb4" in raw  # U+2074 superscript, no ASCII replacement.
    assert "P⁴=AB=c⁴" in boundary
    assert "A/B≠B/A" in boundary
    assert "P²=pq+(c²/(a²+b²))" in boundary
    assert "(p+q)/P(q-p)=(xy+zw)/b²" in boundary
    assert boundary.count("≠")==1
    assert boundary.count("=")==4
    assert "and" in boundary and "but" in boundary
    assert sha256(raw).digest()!=sha256(OUTER.read_bytes()).digest()


def test_only_authorized_v4_to_v5_outer_operator_difference() -> None:
    _,_,outer,boundary=exact_source()
    prior=V4.read_text(encoding="utf-8").rstrip("\n")
    assert prior.count(TRANSFORM_OLD)==1
    expected=prior.replace(TRANSFORM_OLD,TRANSFORM_NEW,1)
    assert outer==expected
    assert OUTER.read_text(encoding="utf-8")==outer+"\n"
    assert len(outer)==528
    assert outer.count("==")==40
    assert boundary.startswith("where ")
    assert TRANSFORM_NEW in outer
    assert outer.endswith("/(u^36==(y*x*w*z)/a^2))")


def test_40_occurrences_and_two_outer_chain_positions() -> None:
    _,_,outer,_=exact_source()
    s=equality_slots(outer)
    assert len(s)==40
    assert [pos for pos,depth in s if depth==0]==[253,257]
    assert s[0]==(10,2)
    assert s[39]==(511,2)
    assert [s[i+20][0]-s[i][0] for i in range(1,19)]==[252]*18
    assert all(s[i+20][1]==s[i][1]+1 for i in range(1,19))


def test_where_is_not_host_arithmetic_or_new_verified_gate_truth() -> None:
    _,_,outer,boundary=exact_source()
    # Scope, directional typing, implicit xA/-yB composition remain unresolved.
    assert "xA==-yB*(" in outer
    assert "P⁴=AB=c⁴" in boundary
    assert "P⁴=BA=c⁴" not in boundary
    assert "A/B≠B/A" in boundary
    assert "A/B=B/A" not in boundary
    assert "(p+q)/(P(q-p))" not in boundary
    assert "(p+q)*((q-p)/P)" not in boundary
    assert "P²=pq+1" not in boundary
    assert "P^4=9" not in boundary


@pytest.mark.parametrize("old,new",[
    ("xA==-yB*(", "x==-y*("),
    ("xA==-yB*(", "Ax==-By*("),
    ("A/B≠B/A","A/B=B/A"),
    ("P⁴=AB=c⁴","P⁴=BA=c⁴"),
    ("P²=pq+(c²/(a²+b²))","P²=pq+1"),
    ("(p+q)/P(q-p)","(p+q)/(P(q-p))"),
    ("y*x*w*z","x*y*w*z"),
])
def test_no_mutation_can_inherit_exact_v5_identity(old,new) -> None:
    raw,txt,_,_=exact_source()
    assert old in txt
    assert new!=old
    corrupted=txt.replace(old,new,1).encode("utf-8")
    assert corrupted!=raw and sha256(corrupted).digest()!=sha256(raw).digest()
    if old in WHERE:
        assert sha256(corrupted.split(b"\n",1)[0]).digest()==sha256(OUTER.read_bytes().rstrip(b"\n")).digest()


def test_full_source_cannot_be_promoted_from_outer_only_abi() -> None:
    _,_,outer,boundary=exact_source()
    assert "≠" not in outer
    assert "⁴" not in outer
    assert "where" not in outer
    assert "P⁴" in boundary
    # Pass159 source-specific outer probe has no evaluated-where proof.
    assert len(OUTER.read_bytes()) < len(FULL.read_bytes())
