from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import pytest
from hhs_runtime.hhs_pass220_v6_loshu_projection_v1 import (
    project,V6ProjectionError,SOURCE,OUTER,WHERE,MATRIX)
ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"contracts/pass220/PASS_220_V6_XYZW_LOSHU_20261009.harmonicode"
RECORD=ROOT/"artifacts/pass220/v6-loshu/projection.json"

def test_exact_three_line_source_and_native_channel_spelling():
    data=FILE.read_bytes()
    assert data.decode("utf-8")==SOURCE
    assert OUTER.count("==")==40
    assert r"\*" in OUTER
    assert "yxwz" in OUTER and "y*x*w*z" not in OUTER
    assert "b^2c^2" in OUTER and "b^2*c^2" not in OUTER
    assert "⁴" in WHERE and "≠" in WHERE and "⁶" in MATRIX
    result=project(data)
    assert result["source_sha256"]==sha256(data).hexdigest()
    assert result["raw_escaped_asterisk_preserved"]
    assert result["outer_gate_offsets"]==[243,247]
    assert result["ordered_inner_copy_pairs"]==18
    assert result["copy_source_offset_delta"]==244

def test_all_nine_loshu_cells_and_zero_centered_rows_columns_diagonals():
    o=project(FILE.read_bytes())
    assert o["matrix"]==[[4,9,2],[3,5,7],[8,1,6]]
    assert o["zero_centered_matrix"]==[[-1,4,-3],[-2,0,2],[3,-4,1]]
    assert o["row_sums"]==o["column_sums"]==[15,15,15]
    assert o["diagonal_sums"]==[15,15]
    assert o["rational_polynomial_vertex"]=="7"
    assert o["projected_phase_ratio"]=="1"
    assert o["nucleus_coordinate"]==5
    cells=o["source_bound_cell_positions"]
    assert len(cells)==9
    assert len(set(c["source_byte_offset"] for c in cells))==9
    assert len(set(c["occurrence_sha256"] for c in cells))==9
    assert all(c["native_gate_truth"]=="UNRESOLVED" for c in cells)
    assert not any(v for k,v in o.items() if k in (
        "all_40_native_boolean_gates_proven","native_negative_List_mask_proven",
        "native_where_constraints_proven","native_typed_AB_noncommutation_proven",
        "signed_vm81_admission_verified","canonical_hash72_hash216_transition_verified"))

@pytest.mark.parametrize("old,new",[
    ("==xy","==x*y"),
    ("==zw","==z*w"),
    ("(yxwz)","(y*x*w*z)"),
    ("b^2c^2","b^2*c^2"),
    (r"\*","*"),
    ("P⁴=AB=c⁴","P⁴=BA=c⁴"),
    ("A/B≠B/A","A/B=B/A"),
    ("(p+q)/P(q-p)","(p+q)/(P(q-p))"),
    ("((b⁶-a²)(c²+b⁴))/(d²+b²)","(b⁶-a²)(c²+b⁴)/(d²+b²)"),
])
def test_mutations_cannot_inherit_the_same_provenance(old,new):
    assert old in SOURCE
    bad=SOURCE.replace(old,new,1)
    assert bad!=SOURCE
    with pytest.raises(V6ProjectionError,match="VERBATIM_SOURCE_CHANGED"):
        project(bad.encode("utf-8"))

def test_noncommutation_does_not_follow_from_reciprocal_inequality_alone():
    A,B=Fraction(1),Fraction(9)
    assert A*B==B*A==9
    assert A/B!=B/A

def test_positive_real_P_branch_in_Z_sqrt3():
    # P=sqrt3,p=sqrt3-1,q=sqrt3+1.  (a,b) means a+b*sqrt3.
    def mul(x,y): return (x[0]*y[0]+3*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    P,p,q=(0,1),(-1,1),(1,1)
    assert mul(p,q)==(2,0)
    assert (p[0]+q[0],p[1]+q[1])==mul(P,(q[0]-p[0],q[1]-p[1]))
    assert mul(mul(P,P),mul(P,P))==(9,0)

def test_projection_artifact_replay():
    if not RECORD.exists():pytest.skip("Created by focused CI")
    assert json.loads(RECORD.read_text())==project(FILE.read_bytes())
