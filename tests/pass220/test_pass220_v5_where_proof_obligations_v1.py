"""Exact-source V5 A/B/P/p/q relation obligations and fail-closed mutations."""
import json
from pathlib import Path
from hashlib import sha256
import pytest
from hhs_runtime.hhs_pass220_v5_where_proof_obligations_v1 import compile_obligations,V5SourceError

ROOT=Path(__file__).resolve().parents[2]
FULL=ROOT/"contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_20261009.harmonicode"
OUTER=ROOT/"contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_OUTER_COMPONENT_20261009.harmonicode"
ART=ROOT/"artifacts/pass220/v5-where/obligations.json"

def inputs():return FULL.read_bytes(),OUTER.read_bytes()

def test_source_bound_five_relation_closure_obligations():
    f,o=inputs()
    r=compile_obligations(f,o)
    assert r["full_source_sha256"]==sha256(f).hexdigest()
    assert r["outer_component_sha256"]==sha256(o).hexdigest()
    assert r["outer_boolean_gate_count"]==40
    assert r["top_level_gate_offsets"]==[253,257]
    assert r["paired_inner_gate_count"]==18 and r["paired_gate_source_delta"]==252
    assert r["where_declarative_equals_count"]==4
    assert r["where_directional_distinction_count"]==1
    assert [x["operator"] for x in r["where_obligations"]]==["=","=","≠","=","="]
    assert r["where_obligations"][0]["rhs"]==r["where_obligations"][1]["lhs"]=="AB"
    assert r["where_obligations"][2]["lhs"]=="A/B"
    assert r["where_obligations"][2]["rhs"]=="B/A"
    assert [x["spelling"] for x in r["typed_carriers"]]==["xA","-yB"]
    assert [x["offset"] for x in r["typed_carriers"]]==[255,259]
    assert len({x["exact_source_obligation_sha256"] for x in r["where_obligations"]})==5
    assert all(x["native_truth"]=="UNRESOLVED" for x in r["where_obligations"])
    assert all(r[k] is False for k in (
        "global_environment_verified","all_40_gate_truths_proven","where_native_semantics_proven",
        "signed_vm81_admission_verified","canonical_hash72_hash216_transition_verified",
    ))

@pytest.mark.parametrize("old,new",[
    ("P⁴=AB=c⁴","P⁴=BA=c⁴"),
    ("A/B≠B/A","A/B=B/A"),
    ("P²=pq+(c²/(a²+b²))","P²=pq+1"),
    ("(p+q)/P(q-p)","(p+q)/(P(q-p))"),
    (" and A/B"," or A/B"),
    (" but P²"," and P²"),
])
def test_rewritten_where_fails_closed(old,new):
    f,o=inputs()
    altered=f.decode("utf-8").replace(old,new,1).encode("utf-8")
    with pytest.raises(V5SourceError,match="SOURCE_CONTENT_CHANGED"):
        compile_obligations(altered,o)

@pytest.mark.parametrize("old,new",[
    (b"==xA==-yB*(",b"==x==-y*("),
    (b"y*x*w*z",b"x*y*w*z"),
])
def test_rewritten_tensor_fails_closed(old,new):
    f,o=inputs()
    with pytest.raises(V5SourceError):
        compile_obligations(f.replace(old,new,1),o)
    with pytest.raises(V5SourceError):
        compile_obligations(f,o.replace(old,new,1))

def test_unicode_noncommutative_boundary_is_preserved():
    f,o=inputs()
    assert "⁴" in f.decode() and "≠" in f.decode()
    assert "⁴" not in o.decode() and "≠" not in o.decode()
    with pytest.raises(V5SourceError):
        compile_obligations(o,o)

def test_replay_written_obligation_evidence():
    if not ART.exists():pytest.skip("CI materializes V5 source-bound graph")
    assert json.loads(ART.read_text())==compile_obligations(*inputs())
