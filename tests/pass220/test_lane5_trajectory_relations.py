import pytest
from hhs_runtime.pass220.lane5_nucleus_group_selection import select_group
from hhs_runtime.pass220.lane5_neighborhood_phase_exchange import prepare_neighborhood_exchange
from hhs_runtime.pass220.lane5_trajectory_relations import compare_trajectory_exchanges

def packet(tick, phase_shift=0):
    xyz={i:(i,0,0) for i in range(10368)}
    group=select_group(xyz,0,8,tick)
    ids=group["selected_ids"]
    phase={i:tuple(i+j+phase_shift for j in range(8)) for i in ids}
    reciprocal={i:tuple(-p for p in phase[i]) for i in ids}
    return prepare_neighborhood_exchange(group=group,phase_by_particle=phase,reciprocal_phase_by_particle=reciprocal,tick=tick)

def test_exact_phase_deltas_are_ordered_and_non_minting():
    before=packet(3)
    after=packet(4,2)
    r=compare_trajectory_exchanges(before,after)
    assert r["source_tick"]==3 and r["target_tick"]==5
    assert r["phase_delta_72"]==[2]*72
    assert r["reciprocal_phase_delta_72"]==[-2]*72
    assert len(r["changed_phase_positions"])==72
    assert not r["canonical_hash216_verified"]
    assert not r["canonical_vm81_mutation_authority"]

def test_identical_phases_and_temporal_discontinuity():
    before=packet(3)
    same=packet(4)
    assert compare_trajectory_exchanges(before,same)["changed_phase_positions"]==[]
    with pytest.raises(ValueError,match="discontinuous"):
        compare_trajectory_exchanges(before,packet(5))

def test_tamper_rejection():
    before=packet(3)
    after=packet(4)
    forged=dict(after,reciprocal_phase_offsets=[0]*72)
    with pytest.raises(ValueError,match="reciprocal"):
        compare_trajectory_exchanges(before,forged)
    forged=dict(after,hash72_receipt_minted=True)
    with pytest.raises(ValueError,match="unsigned"):
        compare_trajectory_exchanges(before,forged)
