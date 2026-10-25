import pytest
from hhs_runtime.pass220.lane5_structural_reuse_candidate import compare_structure
from hhs_runtime.pass220.lane5_trajectory_relations import SCHEMA

def trajectory(delta=2):
    return {
        "schema":SCHEMA,"candidate_only":True,"canonical_hash216_verified":False,
        "source_tick":1,"middle_tick":2,"target_tick":3,"nucleus_id":0,
        "phase_delta_72":[delta]*72,"reciprocal_phase_delta_72":[-delta]*72,
        "ordered_neighbor_id_before":list(range(9)),
        "ordered_neighbor_id_after":list(range(9)),
        "neighbor_identity_changed":False,
    }
def check(a,b):
    return compare_structure(left=a,right=b,left_contract="image",right_contract="audio")

def test_structural_match_is_not_equivalence():
    result=check(trajectory(),trajectory())
    assert result["structural_reuse_candidate"]
    assert not result["cross_modality_equivalence_verified"]
    assert not result["native_receipts_verified"]
    assert not result["canonical_hash216_mint_authority"]

def test_difference_is_not_match():
    assert not check(trajectory(),trajectory(3))["structural_reuse_candidate"]

@pytest.mark.parametrize("change",[
    {"canonical_hash216_verified":True},
    {"target_tick":5},
    {"phase_delta_72":[1]*71},
    {"reciprocal_phase_delta_72":[1]*72},
    {"ordered_neighbor_id_before":[0]*9},
    {"neighbor_identity_changed":True},
])
def test_forged_or_illformed_candidate_rejected(change):
    bad=trajectory()
    bad.update(change)
    with pytest.raises(ValueError):
        check(trajectory(),bad)
