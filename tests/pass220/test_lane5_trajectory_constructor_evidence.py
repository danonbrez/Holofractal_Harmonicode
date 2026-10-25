import pytest
from hhs_runtime.pass220.lane5_trajectory_constructor_evidence import associate_constructor
from hhs_runtime.pass220.lane5_trajectory_relations import SCHEMA

def trajectory():
    return dict(schema=SCHEMA,candidate_only=True,canonical_hash216_verified=False,
                source_tick=3,middle_tick=4,target_tick=5,nucleus_id=0,
                phase_delta_72=[2]*72,reciprocal_phase_delta_72=[-2]*72,
                neighbor_identity_changed=False)

def arguments():
    return dict(trajectory=trajectory(),constructor_id="native-a",
                source_contract="audio",destination_contract="image",
                elapsed_ns=123,claimed_hash216="0"*216)

def test_candidate_evidence_retains_phase_and_cost_without_promoting_proofs():
    r=associate_constructor(**arguments())
    assert r["observed_elapsed_ns"]==123
    assert r["phase_delta_72"]==[2]*72
    assert not r["native_execution_receipt_verified"]
    assert not r["cross_modality_equivalence_verified"]
    assert not r["canonical_vm81_mutation_authority"]

@pytest.mark.parametrize("patch",[
    {"elapsed_ns":-1},{"elapsed_ns":1.5},{"elapsed_ns":True},
    {"claimed_hash216":"short"},{"constructor_id":""},
    {"trajectory":dict(trajectory(),canonical_hash216_verified=True)},
    {"trajectory":dict(trajectory(),target_tick=6)},
    {"trajectory":dict(trajectory(),reciprocal_phase_delta_72=[2]*72)},
])
def test_invalid_evidence_fails_closed(patch):
    args=arguments()
    args.update(patch)
    with pytest.raises(ValueError):
        associate_constructor(**args)
