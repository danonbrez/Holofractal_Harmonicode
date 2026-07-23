from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass102_17x17_trinary_phase_gear_tensor_v1 import *
R=Path(__file__).resolve().parents[1]
def test_parent(): assert load_parent(R)['manifest']['pass_id']=='PASS_101'
def test_ring_sizes(): assert [len(ring_perimeter(r)) for r in range(1,9)]==[8,16,24,32,40,48,56,64]
def test_bijection():
    coords={lane_step_to_coordinate(l,k) for l in range(4) for k in range(72)}
    assert len(coords)==288
    assert all(coordinate_to_lane_step(lane_step_to_coordinate(l,k))==(l,k) for l in range(4) for k in range(72))
def test_lane_cardinality_and_ring_sectors():
    t=build_tensor(); assert all(sum(c['lane_index']==l for c in t['cells'])==72 for l in range(4))
    assert all(sum(c['chebyshev_ring']==r and c['lane_index']==l for c in t['cells'])==2*r for r in range(1,9) for l in range(4))
def test_center_and_magic_closure():
    t=build_tensor(); assert t['center']['coordinate']==[0,0] and t['center']['trinary_state']==0
    assert all(t[k] for k in ('individual_lane_closure_verified','ring_closure_verified','row_closure_verified','column_closure_verified','diagonal_closure_verified','global_zero_sum_verified'))
def test_holographic_roots():
    t=build_tensor(); assert t['all_cells_reconstruct_manifold']
    assert all(c['full_288_step_manifold_root_hash72']==t['center']['manifold_root_hash72'] for c in t['cells'])
def test_transforms_are_invertible():
    p=(3,-5); assert transform_coordinate(transform_coordinate(p,'ROTATE_90'),'ROTATE_270')==p
    assert transform_coordinate(transform_coordinate(p,'REFLECT_X'),'REFLECT_X')==p
def test_single_cell_localization_and_correction():
    t=build_tensor(); s=diagnose(t,[3,-5]); assert s['candidate_cells']==[[3,-5]]
    c=correct(t,s); assert c['original_evidence_preserved'] and c['replay_verified']
def test_run():
    r=run(R); assert r['mapping_completeness']==1 and r['tensor_utilization']==1 and r['cell_reconstruction_coverage']==1
    assert r['correction_replay_exact'] and all(c['passed'] for c in r['negative_cases'])
def test_registry(): assert len(workloads())==14 and len(REJECTIONS)==14 and len(OUTCOMES)==10
