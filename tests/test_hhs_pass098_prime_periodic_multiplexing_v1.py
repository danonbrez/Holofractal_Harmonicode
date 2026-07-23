from fractions import Fraction
from pathlib import Path
import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass098_prime_periodic_multiplexing_v1 import *

R = Path(__file__).resolve().parents[1]


def test_pass097_parent_committed():
    assert load_pass097_inputs(R)['manifest']['pass_id'] == 'PASS_097'


def test_prime_witness_and_joint_recurrence():
    assert witnessed_prime(11, 'root')['coprime_with_u72']
    assert joint_recurrence((72, 11, 13, 17, 19)) == 3_325_608


def test_phase_tuple_and_exact_crt_round_trip():
    primes = (11, 13, 17, 19)
    offsets = (0, 6, 12, 18)
    period = joint_recurrence((72, *primes))
    for k in (0, 1, 71, 72, 137, period - 1, period + 91):
        phases = phase_tuple(k, primes, offsets)
        assert reconstruct_coordinate(phases, primes, offsets) == k % period


def test_noncoprime_unique_claim_rejected():
    with pytest.raises(ContractError, match=REJECTIONS[4]):
        crt_reconstruct((0, 0), (72, 18))


def test_layer_identity_and_order_committed():
    layers = [make_layer(11, 0, 'A'), make_layer(13, 1, 'B')]
    field_ab = build_field('ab', (1,), layers)
    field_ba = build_field('ba', (1,), layers, [layers[1]['layer_id'], layers[0]['layer_id']])
    assert field_ab['composite_field_root_hash72'] != field_ba['composite_field_root_hash72']
    assert execute_field(field_ab, layers, 5)['execution_receipt_root_hash72'] != execute_field(field_ba, layers, 5)['execution_receipt_root_hash72']


def test_normalization_entanglement_is_exact_transform():
    result = normalization_entanglement_transform((72, 144, 216, 288), 1, -1, 2, Fraction(1, 2))
    assert result['modulus'] == '72'
    assert result['raw_input_preserved']
    assert not result['transform_is_scalar_identity_test']
    assert len(result['projection_a']) == len(result['projection_b']) == 4


def test_local_carrier_closure_not_global_recurrence():
    layers = [make_layer(p, i, f'F{i}') for i, p in enumerate(DEFAULT_PRIMES)]
    field = build_field('field', (1, 2, 3, 4), layers)
    assert field['local_carrier_closure_period'] == 72
    assert field['joint_recurrence_period'] == 3_325_608
    assert not field['carrier_closure_is_global_recurrence']


def test_multi_observation_reduces_ambiguity():
    counts = [source_reconstruction((4, 9, 2, 3, 5, 7, 8, 1, 6), n)['candidate_count'] for n in (1, 2, 4, 8)]
    assert counts == sorted(counts, reverse=True)
    assert counts[-1] == 1


def test_noise_conflict_remains_witnessed():
    result = source_reconstruction((4, 9, 2, 3, 5, 7, 8, 1, 6), 8, {3: 1})
    assert result['conflict_witnessed']
    assert not result['synthetic_interpolation_used']


def test_latency_offset_normalization():
    source = [(10, 'a'), (20, 'b')]
    delayed = [(15, 'a'), (25, 'b')]
    assert latency_normalize(delayed, 5) == source


def test_workloads_w98_01_to_14():
    ws = workloads()
    assert len(ws) == 14
    assert ws[0]['workload_id'] == 'W98-01'
    assert ws[-1]['workload_id'] == 'W98-14' and ws[-1]['held_out']


def test_negative_cases_and_replay():
    assert all(case['passed'] for case in negative_cases(R))
    replay = verify_replay(R)
    assert replay['deterministic_replay_verified']
    assert replay['result']['all_composite_coordinates_exact']
    assert replay['result']['held_out_prime_generalization']
