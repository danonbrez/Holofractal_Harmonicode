"""V4 source-general obligation topology verified against real Pass159 receipts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import pytest
from hhs_runtime.hhs_pass220_v4_ordered_gate_obligations_v1 import (
    build_obligations,ObligationError,
)

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode"
NATIVE=ROOT/"evidence/pass220/PASS220_V4_40_GATE_REPLAY_PREFLIGHT_37946520150.json"
RESULT=ROOT/"artifacts/pass220/v4-obligations/ordered_gate_obligations.json"


def inputs():
    return SRC.read_bytes(),json.loads(NATIVE.read_text())


def test_exact_40_gate_obligation_topology() -> None:
    data,receipt=inputs()
    graph=build_obligations(data,receipt)
    assert graph["gate_count"]==40
    assert graph["families"]=={
        "LEFT_COPY":18,"RIGHT_COPY":18,"OUTER_CHAIN":2,
        "PHASE_72":1,"PHASE_36":1,
    }
    assert len(graph["copy_pairs"])==18
    assert [p["address_delta"] for p in graph["copy_pairs"]]==[250]*18
    assert graph["gates"][19]["rhs"]==graph["gates"][20]["lhs"]=="x"
    assert graph["gates"][0]["lhs"]=="u^72"
    assert graph["gates"][39]["lhs"]=="u^36"
    assert graph["gates"][39]["rhs"]=="(y*x*w*z)/a^2"
    assert graph["native_source_hash216"]==receipt["source_hash216"]
    assert all(g["native_boolean_truth"]=="UNRESOLVED" for g in graph["gates"])
    assert all(g["proof_provider"] is None for g in graph["gates"])
    assert all(p["cross_copy_truth"]=="UNRESOLVED" for p in graph["copy_pairs"])
    assert not any(graph[k] for k in (
        "shared_environment_proven","cross_layer_revalidation_proven",
        "typed_denominator_admissibility_proven","all_40_gate_truths_proven",
        "pqc_signed_vm81_admission_verified",
        "canonical_hash72_hash216_transition_verified",
    ))


@pytest.mark.parametrize("old,new",[
    (b"y*x*w*z",b"x*y*w*z"),
    (b"==x==-y*(",b"==-y==x*("),
    (b"x*y+z*w",b"z*w+x*y"),
    (b"(u^72==x*y)",b"(u^36==x*y)"),
])
def test_changed_ordered_source_cannot_inherit_proof_obligations(old,new) -> None:
    data,receipt=inputs()
    assert old in data
    with pytest.raises(ObligationError,match="V4_SOURCE_SHA256"):
        build_obligations(data.replace(old,new,1),receipt)


def test_counterfeit_native_gate_truth_rejected() -> None:
    data,receipt=inputs()
    receipt["gates"][37]["truth"]="TRUE"
    with pytest.raises(ObligationError,match="UNAUTHORIZED_GATE_TRUTH"):
        build_obligations(data,receipt)


def test_native_source_witness_cannot_shift_its_position() -> None:
    data,receipt=inputs()
    receipt["gates"][39]["offset"]=508
    with pytest.raises(ObligationError,match="NATIVE_GATE_POSITION_MISMATCH"):
        build_obligations(data,receipt)


def test_duplicate_copy_address_provenance_cannot_be_swapped() -> None:
    data,receipt=inputs()
    receipt["gates"][21]["occurrence_sha256"]=receipt["gates"][1]["occurrence_sha256"]
    with pytest.raises(ObligationError,match="NATIVE_GATE_PROVENANCE_MISMATCH"):
        build_obligations(data,receipt)


def test_false_vm81_proof_promotion_rejected() -> None:
    data,receipt=inputs()
    receipt["proof"]["canonical_vm81_admission_verified"]=True
    with pytest.raises(ObligationError,match="UNAUTHORIZED_AUTHORITY_PROMOTION"):
        build_obligations(data,receipt)


def test_materialized_obligation_graph_matches_runtime_bound_source() -> None:
    if not RESULT.is_file():
        pytest.skip("Targeted workflow emits source-bound obligation graph")
    result=json.loads(RESULT.read_text())
    expected=build_obligations(*inputs())
    assert result==expected
    assert len({g["occurrence_sha256"] for g in result["gates"]})==40
    assert len({p["ordered_edge_sha256"] for p in result["copy_pairs"]})>=1
