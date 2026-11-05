"""Exact V7 ordered 3x3 source and 81x64 <-> 72x72 coordinates."""
from pathlib import Path
from hashlib import sha256
import json
import pytest

from hhs_runtime.hhs_pass220_v7_ordered_matrix_geometry_v1 import (
    parse_quotient,to_hash72_address,from_hash72_address,verify_bijection,
    V7SourceError,SOURCE,ROWS,
)

ROOT=Path(__file__).resolve().parents[2]
SOURCE_FILE=ROOT/"contracts/pass220/PASS_220_V7_VM81_ORDERED_MATRIX_QUOTIENT_20261009.harmonicode"
ART=ROOT/"artifacts/pass220/v7-matrix/denominator_geometry.json"

def test_all_nine_ordered_source_cells_and_nucleus():
    raw=SOURCE_FILE.read_bytes()
    o=parse_quotient(raw)
    assert raw==(SOURCE+"\n").encode("ascii")
    assert o["source_sha256"]==sha256(raw).hexdigest()
    assert o["matrix"]==ROWS
    assert o["numerator_exact_integer"]==5184
    assert o["matrix_macro_site_count"]==9
    assert o["matrix"][1][1]=="x+y-z-w+xy+yx-zw-wz"
    assert o["center_ordered_terms"]==[
        "x","+y","-z","-w","+xy","+yx","-zw","-wz"
    ]
    assert [c["macro_site"] for c in o["source_bound_macro_sites"]]==list(range(9))
    assert [c["raw_source_expression"] for c in o["source_bound_macro_sites"]]==sum(ROWS,[])
    assert len({c["source_byte_offset"] for c in o["source_bound_macro_sites"]})==9
    assert len({c["occurrence_sha256"] for c in o["source_bound_macro_sites"]})==9
    assert all(c["native_semantic_value"]=="UNRESOLVED" for c in o["source_bound_macro_sites"])
    assert [x["word"] for x in o["ordered_channel_tokens"]]==[
        "yx","wx","xy","wz","xy","yx","zw","wz","zw","yx","xy","zw"
    ]

def test_all_5184_addresses_bijectively_roundtrip():
    result=verify_bijection()
    assert result["total_vm81_cells"]==81
    assert result["bijective_positions"]==result["hash72_lattice_positions"]==5184
    assert result["address_roundtrip"]=="VERIFIED"
    for s in range(9):
        for c in range(9):
            for bit in range(64):
                row,col=to_hash72_address(s,c,bit)
                assert from_hash72_address(row,col)==(s,c,bit)
    assert to_hash72_address(0,0,0)==(0,0)
    assert to_hash72_address(8,8,63)==(71,71)

@pytest.mark.parametrize("bad",[
    "(81*64)*((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))",
    "(81*64)/((xy,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(yx,x-z,zw))",
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+yx+xy-zw-wz,-zw-yx),(xy,x-z,zw))",
    "(81*64)/((yx,y+w,wx),(-xy-zw,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))",
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-yx-zw),(xy,x-z,zw))",
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,z-x,zw))",
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,wz))",
])
def test_forbidden_phase_order_and_quotient_mutations_fail_closed(bad):
    assert bad!=SOURCE
    with pytest.raises(V7SourceError,match="UNAUTHORIZED_SOURCE_MUTATION"):
        parse_quotient((bad+"\n").encode("ascii"))

def test_unqualified_matrix_division_is_not_admitted():
    o=parse_quotient(SOURCE_FILE.read_bytes())
    assert o["matrix_denominator_operation"]=="NATIVE_ORDERED_QUOTIENT_UNRESOLVED"
    for key in ("matrix_inverse_proven","global_denominator_admissibility_proven",
                "source_specific_native_tensor_truth_proven",
                "pqc_signed_vm81_admission_verified",
                "canonical_hash72_hash216_transition_verified"):
        assert o[key] is False

@pytest.mark.parametrize("args",[
    (-1,0,0),(9,0,0),(0,-1,0),(0,9,0),(0,0,-1),(0,0,64),
    (0,0,0.0),(True,0,0)
])
def test_invalid_vm81_address_rejected(args):
    with pytest.raises(V7SourceError):
        to_hash72_address(*args)

@pytest.mark.parametrize("args",[
    (-1,0),(72,0),(0,-1),(0,72),(0,0.0),(True,0)
])
def test_invalid_hash72_address_rejected(args):
    with pytest.raises(V7SourceError):
        from_hash72_address(*args)

def test_generated_graph_replays():
    if not ART.is_file():
        pytest.skip("Focused CI generates source-bound geometry JSON")
    out=json.loads(ART.read_text(encoding="utf-8"))
    expected=parse_quotient(SOURCE_FILE.read_bytes())
    expected["address_bijection"]=verify_bijection()
    assert out==expected
