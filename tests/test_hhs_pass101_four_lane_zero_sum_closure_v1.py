from pathlib import Path
import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass101_four_lane_zero_sum_closure_v1 import *

R = Path(__file__).resolve().parents[1]


def test_parent_and_cardinality():
    assert load_parent(R)['manifest']['pass_id'] == 'PASS_100'
    m = build_manifold()
    assert m['lane_count'] == 4 and m['step_count'] == 72 and m['lane_step_check_count'] == 288


def test_all_288_residues_and_reconstructions_close():
    m = build_manifold()
    assert m['individual_lane_residues_zero']
    assert m['collective_step_residues_zero']
    assert m['all_step_cycle_reconstructions_exact']
    assert m['full_cycle_root_recovered_from_every_lane_step']


def test_raw_lane_histories_remain_distinct():
    m = build_manifold()
    assert m['raw_lane_histories_distinct'] and len(set(m['lane_history_roots'])) == 4


def test_every_step_reconstructs_full_cycle():
    cycle = canonical_cycle()
    m = build_manifold(cycle)
    assert all(reconstruct_from_receipt(step) == cycle for step in m['steps'])


def test_zero_is_residue_not_raw_state_erasure():
    s = make_step(canonical_cycle(), 2, 17)
    assert any(s['raw_state']) and all(v == 0 for v in s['normalization_residue'])


def test_single_error_localized_and_corrected_with_provenance():
    cycle = canonical_cycle(); s = make_step(cycle, 2, 17); raw = list(s['raw_state']); raw[9] += 1
    syn = diagnose_step(cycle, 2, 17, raw)
    assert syn['candidate_raw_positions'] == [9]
    rec = correct_step(cycle, 2, 17, raw, syn)
    assert rec['original_evidence_preserved'] and tuple(decode_projection(rec['corrected_raw_state'], 2, 17)) == cycle


def test_compensating_errors_do_not_hide_individual_failure():
    cycle = canonical_cycle(); a = list(project_cycle(cycle,0,8)); b = list(project_cycle(cycle,1,8))
    a[0] = (a[0] + 7) % 72; b[0] = (b[0] - 7) % 72
    assert not diagnose_step(cycle,0,8,a)['individual_zero']
    assert not diagnose_step(cycle,1,8,b)['individual_zero']


def test_ambiguous_correction_rejected():
    cycle = canonical_cycle(); raw = list(project_cycle(cycle,0,0)); raw[0] += 1; raw[1] += 1
    syn = diagnose_step(cycle,0,0,raw)
    with pytest.raises(ContractError, match=REJECTIONS[11]):
        correct_step(cycle,0,0,raw,syn)


def test_missing_receipt_rejected():
    with pytest.raises(ContractError, match=REJECTIONS[10]):
        reconstruct_from_receipt({'lane_index':0,'step_index':0})


def test_run_and_replay():
    r = run(R)
    assert r['holographic_reconstruction_coverage'] == 1
    assert r['checkpoint_replay_exact'] and r['correction_replay_exact']
    assert r['compensating_errors_detected'] and all(c['passed'] for c in r['negative_cases'])


def test_workloads_and_taxonomy():
    assert len(workloads()) == 14 and len(OUTCOMES) == 9 and len(REJECTIONS) == 14
