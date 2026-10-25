import pytest
from hhs_runtime.pass220.lane5_nucleus_group_selection import select_group
from hhs_runtime.pass220.lane5_neighborhood_phase_exchange import prepare_neighborhood_exchange

def inputs():
    coordinates={i:(i,0,0) for i in range(10368)}
    group=select_group(coordinates,0,8,11)
    ids=group["selected_ids"]
    phase={i:tuple(i+j for j in range(8)) for i in ids}
    reciprocal={i:tuple(-p for p in phase[i]) for i in ids}
    return group,phase,reciprocal

def test_complete_reciprocal_72_packet_is_candidate_only():
    group,p,r=inputs()
    result=prepare_neighborhood_exchange(group=group,phase_by_particle=p,reciprocal_phase_by_particle=r,tick=11)
    assert len(result["character_offsets"])==72
    assert len(result["phase_offsets"])==72
    assert len(result["reciprocal_phase_offsets"])==72
    assert result["expanded_phase_occurrences"]==144
    assert all(a+b==0 for a,b in zip(result["phase_offsets"],result["reciprocal_phase_offsets"]))
    assert result["target_tick"]==12
    assert not result["hash72_receipt_minted"]
    assert not result["canonical_vm81_mutation_authority"]

def test_forged_reciprocal_and_bad_shapes_fail_closed():
    group,p,r=inputs()
    bad=dict(r)
    bad[0]=(99,)+r[0][1:]
    with pytest.raises(ValueError,match="opposition"):
        prepare_neighborhood_exchange(group=group,phase_by_particle=p,reciprocal_phase_by_particle=bad,tick=11)
    bad=dict(p)
    bad[1]=bad[1][:7]
    with pytest.raises(ValueError,match="eight exact"):
        prepare_neighborhood_exchange(group=group,phase_by_particle=bad,reciprocal_phase_by_particle=r,tick=11)
    with pytest.raises(ValueError,match="same-tick"):
        prepare_neighborhood_exchange(group=group,phase_by_particle=p,reciprocal_phase_by_particle=r,tick=12)
    with pytest.raises(ValueError,match="same-tick"):
        prepare_neighborhood_exchange(group=dict(group, candidate_only=False),phase_by_particle=p,reciprocal_phase_by_particle=r,tick=11)
    with pytest.raises(ValueError,match="eight unique"):
        prepare_neighborhood_exchange(group=dict(group,selected_ids=group["selected_ids"][:8]),phase_by_particle=p,reciprocal_phase_by_particle=r,tick=11)
