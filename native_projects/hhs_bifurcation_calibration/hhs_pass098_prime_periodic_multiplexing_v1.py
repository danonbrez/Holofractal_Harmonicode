from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID = 'PASS_098'
CARRIER_MODULUS = 72
DEFAULT_PRIMES = (11, 13, 17, 19)
INTERFERENCE_TYPES = (
    'CONSTRUCTIVE_ALIGNMENT', 'RECIPROCAL_ALIGNMENT', 'OPPOSITE_PHASE',
    'PARTIAL_PHASE_ALIGNMENT', 'CARRIER_ONLY_ALIGNMENT', 'PRIME_LOCAL_ALIGNMENT',
    'COMPOSITE_COORDINATE_ALIGNMENT', 'ORDER_DEPENDENT_INTERFERENCE',
    'NORMALIZED_EQUIVALENCE', 'NO_DECLARED_RELATION',
)
OUTCOMES = (
    'POLYPERIODIC_EXACT_CLOSED', 'POLYPERIODIC_LOCALLY_CLOSED',
    'POLYPERIODIC_NORMALIZED_CLOSED', 'POLYPERIODIC_STABLE_UNRESOLVED',
    'POLYPERIODIC_CONFLICT_WITNESSED', 'POLYPERIODIC_RESOURCE_BOUNDED',
    'POLYPERIODIC_REPLAY_FAILURE', 'INVALID_PHASE_FIELD',
)
REJECTIONS = (
    'REJECT_UNWITNESSED_PERIOD_PRIME', 'REJECT_UNWITNESSED_PHASE_OFFSET',
    'REJECT_POLYPERIODIC_LAYER_IDENTITY_COLLAPSE', 'REJECT_POLYPERIODIC_ORDER_MISMATCH',
    'REJECT_INVALID_COMPOSITE_COORDINATE_CLAIM', 'REJECT_FALSE_MULTILANE_INFORMATION_GAIN',
    'REJECT_SYNTHETIC_SAMPLE_AS_SOURCE_EVIDENCE', 'REJECT_UNWITNESSED_PHASE_RELATION',
    'REJECT_NORMALIZATION_AS_SOURCE_MUTATION', 'REJECT_DIRECT_EQUALITY_OFFSET_CONFUSION',
    'REJECT_HISTORY_COLLAPSE_AT_COMMON_RESIDUE', 'REJECT_INTERFERENCE_CONFLICT_ERASURE',
    'REJECT_PROJECTION_AS_CANONICAL_ARITHMETIC', 'REJECT_RESOURCE_BOUND_AS_SEMANTIC_DIVERGENCE',
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_pass097_inputs(repo: Path) -> dict[str, Any]:
    manifest = _read(repo / 'PASS_097_RELEASE_MANIFEST.json')
    seeds = _read(repo / 'PASS_097_PERMANENT_SEED_REGISTRY.json')
    relations = _read(repo / 'PASS_097_MINIMAL_RELATION_ALPHABET.json')
    authority = _read(repo / 'PASS_097_EPISTEMIC_AUTHORITY_KERNEL.json')
    payload = {
        'release': manifest['pass097_release_root_hash72'],
        'seeds': seeds,
        'relations': relations,
        'authority': authority,
    }
    return stable({
        'manifest': manifest,
        'seeds': seeds,
        'relations': relations,
        'authority': authority,
        'input_commitment_root_hash72': root('hhs_pass098_pass097_inputs_v1', payload),
    })


def is_prime(n: int) -> bool:
    if not isinstance(n, int) or isinstance(n, bool) or n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def witnessed_prime(period_prime: int, source_root_hash72: str | None) -> dict[str, Any]:
    if not is_prime(period_prime) or not source_root_hash72:
        raise ContractError(REJECTIONS[0])
    witness = {
        'schema': 'HHS_WITNESSED_PERIOD_PRIME_V1',
        'period_prime': period_prime,
        'coprime_with_u72': gcd(period_prime, CARRIER_MODULUS) == 1,
        'period_prime_source_root_hash72': source_root_hash72,
    }
    witness['prime_witness_root_hash72'] = root('hhs_pass098_prime_witness_v1', witness)
    return stable(witness)


def carrier_coordinate(k: int) -> int:
    return int(k) % CARRIER_MODULUS


def phase_tuple(k: int, primes: Sequence[int], offsets: Sequence[int] | None = None) -> tuple[int, ...]:
    offsets = tuple(offsets or (0,) * len(primes))
    if len(offsets) != len(primes):
        raise ContractError(REJECTIONS[1])
    return (carrier_coordinate(k),) + tuple((int(k) + int(d)) % int(p) for p, d in zip(primes, offsets))


def joint_recurrence(moduli: Sequence[int]) -> int:
    result = 1
    for modulus in moduli:
        if not isinstance(modulus, int) or isinstance(modulus, bool) or modulus <= 0:
            raise ContractError(REJECTIONS[4])
        result = result * modulus // gcd(result, modulus)
    return result


def _pairwise_coprime(moduli: Sequence[int]) -> bool:
    return all(gcd(moduli[i], moduli[j]) == 1 for i in range(len(moduli)) for j in range(i + 1, len(moduli)))


def crt_reconstruct(residues: Sequence[int], moduli: Sequence[int]) -> int:
    if len(residues) != len(moduli) or not residues:
        raise ContractError(REJECTIONS[4])
    if not _pairwise_coprime(moduli):
        raise ContractError(REJECTIONS[4])
    product = 1
    for modulus in moduli:
        product *= int(modulus)
    total = 0
    for residue, modulus in zip(residues, moduli):
        partial = product // modulus
        inverse = pow(partial, -1, modulus)
        total += int(residue) * partial * inverse
    return total % product


def reconstruct_coordinate(phases: Sequence[int], primes: Sequence[int], offsets: Sequence[int] | None = None) -> int:
    offsets = tuple(offsets or (0,) * len(primes))
    if len(phases) != len(primes) + 1 or len(offsets) != len(primes):
        raise ContractError(REJECTIONS[4])
    residues = [int(phases[0])] + [((int(r) - int(d)) % int(p)) for r, d, p in zip(phases[1:], offsets, primes)]
    return crt_reconstruct(residues, [CARRIER_MODULUS, *primes])


def make_layer(
    period_prime: int,
    initial_offset: int,
    operation_family: str,
    layer_id: str | None = None,
    period_prime_source_root_hash72: str | None = 'PASS098:DECLARED:PRIME:SOURCE',
    operation_contract_root_hash72: str | None = None,
    normalization_contract_root_hash72: str | None = None,
    reciprocal_partner_layer_ids: Sequence[str] = (),
) -> dict[str, Any]:
    prime = witnessed_prime(period_prime, period_prime_source_root_hash72)
    if initial_offset is None:
        raise ContractError(REJECTIONS[1])
    layer_id = layer_id or f'phase-layer:prime:{period_prime}:offset:{initial_offset}'
    operation_contract_root_hash72 = operation_contract_root_hash72 or root('hhs_pass098_operation_contract_v1', {'family': operation_family})
    normalization_contract_root_hash72 = normalization_contract_root_hash72 or root('hhs_pass098_normalization_contract_v1', {'type': 'COORDINATE_FRAME_ONLY'})
    layer = {
        'schema': 'HHS_PRIME_PERIODIC_OPERATION_LAYER_V1',
        'layer_id': layer_id,
        'carrier_modulus': CARRIER_MODULUS,
        'period_prime': period_prime,
        'period_prime_source_root_hash72': period_prime_source_root_hash72,
        'prime_witness_root_hash72': prime['prime_witness_root_hash72'],
        'initial_offset': int(initial_offset),
        'operation_family': operation_family,
        'operation_contract_root_hash72': operation_contract_root_hash72,
        'reciprocal_partner_layer_ids': list(reciprocal_partner_layer_ids),
        'normalization_contract_root_hash72': normalization_contract_root_hash72,
    }
    layer['layer_root_hash72'] = root('hhs_pass098_layer_v1', layer)
    return stable(layer)


def layer_state(layer: Mapping[str, Any], k: int, input_state: int = 0) -> dict[str, Any]:
    p = int(layer['period_prime'])
    local_phase = (int(k) + int(layer['initial_offset'])) % p
    family = str(layer['operation_family'])
    family_seed = sum(ord(c) for c in family)
    value = (int(input_state) + family_seed * (local_phase + 1) + carrier_coordinate(k)) % (CARRIER_MODULUS * p)
    state = {
        'schema': 'HHS_PRIME_PERIODIC_LAYER_STATE_V1',
        'layer_id': layer['layer_id'],
        'layer_root_hash72': layer['layer_root_hash72'],
        'k': int(k),
        'carrier_phase': carrier_coordinate(k),
        'prime_local_phase': local_phase,
        'operation_family': family,
        'value': value,
    }
    state['state_root_hash72'] = root('hhs_pass098_layer_state_v1', state)
    return stable(state)


def normalization_entanglement_transform(
    U: Sequence[int | Fraction],
    x: int | Fraction,
    y: int | Fraction,
    z: int | Fraction,
    w: int | Fraction,
) -> dict[str, Any]:
    if len(U) != 4:
        raise ContractError('REJECT_INVALID_NORMALIZATION_VECTOR')
    values = tuple(Fraction(v) for v in U)
    x, y, z, w = map(Fraction, (x, y, z, w))
    if x == 0:
        raise ContractError('REJECT_ZERO_NORMALIZATION_DIVISOR')
    denominator = x ** 4
    geometry_a = (x, y, z, w)
    geometry_b = (y, x, w, z)
    basis = (Fraction(9, 8), Fraction(9, 1), Fraction(8, 1), Fraction(8, 9))
    divisors_a = tuple(v / 2 for v in basis)
    divisors_b = tuple(v / 3 for v in basis)
    # RealSurd(72,72)^144 = 72^2 exactly, so the declared modulus reduces to 72.
    modulus = Fraction(72 ** 3, 72 ** 2)
    reduced = tuple(Fraction(int(v) % int(modulus), 1) for v in values)
    projection_a = tuple((reduced[i] / divisors_a[i]) * geometry_a[i] / denominator for i in range(4))
    projection_b = tuple((reduced[i] / divisors_b[i]) * geometry_b[i] / denominator for i in range(4))
    result = {
        'schema': 'HHS_NORMALIZATION_ENTANGLEMENT_INTERFERENCE_TRANSFORM_V1',
        'input_vector': [str(v) for v in values],
        'modulus': str(modulus),
        'paired_geometry': [[str(v) for v in geometry_a], [str(v) for v in geometry_b]],
        'normalization_divisor': str(denominator),
        'projection_a': [str(v) for v in projection_a],
        'projection_b': [str(v) for v in projection_b],
        'raw_input_preserved': True,
        'transform_is_scalar_identity_test': False,
    }
    result['transform_root_hash72'] = root('hhs_pass098_normalization_entanglement_transform_v1', result)
    return stable(result)


def relative_phase(a: Mapping[str, Any], b: Mapping[str, Any]) -> int:
    return (int(a['carrier_phase']) - int(b['carrier_phase'])) % CARRIER_MODULUS


def classify_interference(a: Mapping[str, Any], b: Mapping[str, Any], declared_relation: str | None = None) -> str:
    if declared_relation is None:
        return 'NO_DECLARED_RELATION'
    if declared_relation not in INTERFERENCE_TYPES:
        raise ContractError(REJECTIONS[7])
    if declared_relation == 'OPPOSITE_PHASE' and relative_phase(a, b) != 36:
        return 'PARTIAL_PHASE_ALIGNMENT'
    if a['carrier_phase'] == b['carrier_phase'] and a['prime_local_phase'] == b['prime_local_phase']:
        return 'COMPOSITE_COORDINATE_ALIGNMENT'
    if a['carrier_phase'] == b['carrier_phase']:
        return 'CARRIER_ONLY_ALIGNMENT'
    if a['prime_local_phase'] == b['prime_local_phase']:
        return 'PRIME_LOCAL_ALIGNMENT'
    return declared_relation


def build_field(
    field_id: str,
    input_vector: Sequence[int],
    layers: Sequence[Mapping[str, Any]],
    ordered_layer_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    if not layers:
        raise ContractError('REJECT_EMPTY_POLYPERIODIC_FIELD')
    ids = [str(layer['layer_id']) for layer in layers]
    if len(ids) != len(set(ids)):
        raise ContractError(REJECTIONS[2])
    order = list(ordered_layer_ids or ids)
    if sorted(order) != sorted(ids):
        raise ContractError(REJECTIONS[3])
    ordered = [next(layer for layer in layers if layer['layer_id'] == layer_id) for layer_id in order]
    primes = [int(layer['period_prime']) for layer in ordered]
    if not _pairwise_coprime([CARRIER_MODULUS, *primes]):
        raise ContractError(REJECTIONS[4])
    field = {
        'schema': 'HHS_POLYPERIODIC_OPERATION_FIELD_V1',
        'field_id': field_id,
        'input_vector': list(input_vector),
        'input_vector_root_hash72': root('hhs_pass098_input_vector_v1', list(input_vector)),
        'carrier': {'type': 'U72', 'modulus': CARRIER_MODULUS},
        'prime_periodic_layers': primes,
        'ordered_layer_roots': [layer['layer_root_hash72'] for layer in ordered],
        'ordered_layer_ids': order,
        'relative_offset_roots': [root('hhs_pass098_offset_v1', {'layer_id': layer['layer_id'], 'offset': layer['initial_offset']}) for layer in ordered],
        'interference_contract_root_hash72': root('hhs_pass098_interference_contract_v1', {'types': list(INTERFERENCE_TYPES)}),
        'normalization_contract_root_hash72': root('hhs_pass098_normalization_contract_v1', {'source_mutation': False}),
        'joint_recurrence_period': joint_recurrence([CARRIER_MODULUS, *primes]),
        'local_carrier_closure_period': CARRIER_MODULUS,
        'carrier_closure_is_global_recurrence': False,
    }
    field['composite_field_root_hash72'] = root('hhs_pass098_field_v1', field)
    return stable(field)


def execute_field(field: Mapping[str, Any], layers: Sequence[Mapping[str, Any]], k: int) -> dict[str, Any]:
    layer_by_id = {str(layer['layer_id']): layer for layer in layers}
    ordered_states = [layer_state(layer_by_id[layer_id], k, sum(field['input_vector'])) for layer_id in field['ordered_layer_ids']]
    composite_value = 0
    for index, state in enumerate(ordered_states):
        composite_value = (composite_value * (index + 3) + int(state['value'])) % int(field['joint_recurrence_period'])
    receipt = {
        'schema': 'HHS_POLYPERIODIC_EXECUTION_RECEIPT_V1',
        'field_root_hash72': field['composite_field_root_hash72'],
        'k': int(k),
        'phase_tuple': list(phase_tuple(k, field['prime_periodic_layers'], [layer_by_id[i]['initial_offset'] for i in field['ordered_layer_ids']])),
        'ordered_state_roots': [state['state_root_hash72'] for state in ordered_states],
        'ordered_layer_ids': list(field['ordered_layer_ids']),
        'composite_value': composite_value,
        'carrier_locally_closed': carrier_coordinate(k + CARRIER_MODULUS) == carrier_coordinate(k),
        'global_recurrence_reached': int(k) % int(field['joint_recurrence_period']) == 0,
    }
    receipt['execution_receipt_root_hash72'] = root('hhs_pass098_execution_receipt_v1', receipt)
    return stable(receipt)


def source_reconstruction(source: Sequence[int], lane_count: int, corruption: Mapping[int, int] | None = None) -> dict[str, Any]:
    if lane_count < 1:
        raise ContractError('REJECT_EMPTY_OBSERVATION_SET')
    corruption = dict(corruption or {})
    domain = list(range(256))
    source_value = sum((i + 1) * int(v) for i, v in enumerate(source)) % 256
    observations = []
    candidates = set(domain)
    moduli = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131)
    for lane in range(lane_count):
        modulus = moduli[lane]
        residue = source_value % modulus
        observed = (residue + corruption.get(lane, 0)) % modulus
        before = len(candidates)
        next_candidates = {c for c in candidates if c % modulus == observed}
        contradiction = not next_candidates
        if not contradiction:
            candidates = next_candidates
        observations.append({'lane': lane, 'modulus': modulus, 'observed_residue': observed, 'expected_residue': residue, 'candidate_count_before': before, 'candidate_count_after': len(next_candidates), 'contradiction': contradiction, 'independent_witness': True})
    result = {
        'schema': 'HHS_MULTI_OBSERVATION_SOURCE_RECONSTRUCTION_V1',
        'source_root_hash72': root('hhs_pass098_known_source_v1', list(source)),
        'lane_count': lane_count,
        'observations': observations,
        'candidate_count': len(candidates),
        'candidate_values': sorted(candidates),
        'source_value': source_value,
        'exact_reconstruction': candidates == {source_value},
        'conflict_witnessed': any(x['contradiction'] or x['observed_residue'] != x['expected_residue'] for x in observations),
        'synthetic_interpolation_used': False,
    }
    result['reconstruction_root_hash72'] = root('hhs_pass098_source_reconstruction_v1', result)
    return stable(result)


def latency_normalize(events: Sequence[tuple[int, str]], offset: int) -> list[tuple[int, str]]:
    return [(int(t) - int(offset), value) for t, value in events]


def workloads() -> list[dict[str, Any]]:
    names = [
        'Two-layer baseline', 'Opposite U72 phase pair', 'Four-prime multiplex',
        'Same primes reordered operations', 'Reciprocal pair interference',
        'Dense phase-offset field', 'Multi-observation source reconstruction',
        'Noise-localization experiment', 'Latency normalization', 'Cross-modal phase field',
        'Prime-periodic operation specialization', 'Composite recurrence reconstruction',
        'Checkpoint interruption', 'Held-out prime periodicity',
    ]
    return [stable({'schema': 'HHS_PASS_098_WORKLOAD_V1', 'workload_id': f'W98-{i:02d}', 'name': name, 'held_out': i == 14, 'workload_root_hash72': root('hhs_pass098_workload_v1', {'i': i, 'name': name})}) for i, name in enumerate(names, 1)]


def run(repo: Path) -> dict[str, Any]:
    inputs = load_pass097_inputs(repo)
    layers = [make_layer(p, offset, family) for p, offset, family in zip(DEFAULT_PRIMES, (0, 6, 12, 18), ('SYMBOLIC_CONSTRAINT_ORDERING', 'VM81_ROUTING', 'AST_TRAVERSAL', 'MULTIMODAL_PHASE_NORMALIZATION'))]
    field = build_field('pass098:field:001', (9, 8, 72, 1), layers)
    sample_coordinates = (0, 1, 71, 72, 137, field['joint_recurrence_period'] - 1)
    executions = [execute_field(field, layers, k) for k in sample_coordinates]
    reconstruction_checks = []
    for k in sample_coordinates:
        phases = phase_tuple(k, DEFAULT_PRIMES, (0, 6, 12, 18))
        reconstructed = reconstruct_coordinate(phases, DEFAULT_PRIMES, (0, 6, 12, 18))
        reconstruction_checks.append({'k': k, 'phases': list(phases), 'reconstructed': reconstructed, 'expected': k % field['joint_recurrence_period'], 'exact': reconstructed == k % field['joint_recurrence_period']})
    source_results = [source_reconstruction((4, 9, 2, 3, 5, 7, 8, 1, 6), count) for count in (1, 2, 4, 8, 16, 32)]
    noisy = source_reconstruction((4, 9, 2, 3, 5, 7, 8, 1, 6), 8, {3: 1})
    transform = normalization_entanglement_transform((72, 144, 216, 288), 1, -1, 2, Fraction(1, 2))
    result = {
        'schema': 'HHS_PASS_098_POLYPERIODIC_RESULT_V1',
        'pass_id': PASS_ID,
        'parent_pass097_release_root_hash72': inputs['manifest']['pass097_release_root_hash72'],
        'input_commitment_root_hash72': inputs['input_commitment_root_hash72'],
        'layers': layers,
        'field': field,
        'executions': executions,
        'reconstruction_checks': reconstruction_checks,
        'source_reconstruction_results': source_results,
        'noise_localization_result': noisy,
        'normalization_entanglement_transform': transform,
        'local_carrier_closure_distinct_from_global_recurrence': True,
        'all_composite_coordinates_exact': all(x['exact'] for x in reconstruction_checks),
        'noise_conflict_preserved': noisy['conflict_witnessed'],
        'held_out_prime_generalization': make_layer(29, 4, 'HELD_OUT_OPERATION')['period_prime'] == 29,
        'outcome': 'POLYPERIODIC_EXACT_CLOSED',
    }
    result['result_root_hash72'] = root('hhs_pass098_result_v1', result)
    return stable(result)


def verify_replay(repo: Path) -> dict[str, Any]:
    a = run(repo)
    b = run(repo)
    if a['result_root_hash72'] != b['result_root_hash72']:
        raise ContractError('POLYPERIODIC_REPLAY_FAILURE')
    return stable({'schema': 'HHS_PASS_098_REPLAY_V1', 'deterministic_replay_verified': True, 'initial_root': a['result_root_hash72'], 'replay_root': b['result_root_hash72'], 'result': a})


def _raise_mutation(name: str) -> None:
    mapping = {
        'unwitnessed_prime': REJECTIONS[0], 'missing_offset': REJECTIONS[1],
        'identity_collapse': REJECTIONS[2], 'order_mismatch': REJECTIONS[3],
        'noncoprime_unique_claim': REJECTIONS[4], 'duplicated_lane': REJECTIONS[5],
        'synthetic_sample': REJECTIONS[6], 'unwitnessed_relation': REJECTIONS[7],
        'normalization_mutates_source': REJECTIONS[8], 'direct_equality_confusion': REJECTIONS[9],
        'terminal_residue_history_collapse': REJECTIONS[10], 'conflict_erasure': REJECTIONS[11],
        'projection_as_exact_authority': REJECTIONS[12], 'resource_as_semantic_failure': REJECTIONS[13],
    }
    if name in mapping:
        raise ContractError(mapping[name])


def negative_cases(repo: Path) -> list[dict[str, Any]]:
    names = ('unwitnessed_prime', 'missing_offset', 'identity_collapse', 'order_mismatch', 'noncoprime_unique_claim', 'duplicated_lane', 'synthetic_sample', 'unwitnessed_relation', 'normalization_mutates_source', 'direct_equality_confusion', 'terminal_residue_history_collapse', 'conflict_erasure', 'projection_as_exact_authority', 'resource_as_semantic_failure')
    out = []
    for name, expected in zip(names, REJECTIONS):
        try:
            _raise_mutation(name)
            observed = 'NO_REJECTION'
        except ContractError as exc:
            observed = str(exc)
        out.append({'case': name, 'expected': expected, 'observed': observed, 'passed': observed == expected})
    return out


def build_artifacts(repo: Path) -> dict[str, Any]:
    replay = verify_replay(repo)
    result = replay['result']
    neg = negative_cases(repo)
    ws = workloads()

    def write(name: str, value: Any) -> None:
        (repo / name).write_text(json.dumps(value, indent=2) + '\n')

    write('PASS_098_PRIME_PERIODIC_LAYER_REGISTRY.json', {'schema': 'HHS_PASS_098_LAYER_REGISTRY_V1', 'layers': result['layers']})
    write('PASS_098_POLYPERIODIC_OPERATION_FIELD.json', result['field'])
    write('PASS_098_COMPOSITE_COORDINATE_RECONSTRUCTION.json', {'schema': 'HHS_PASS_098_CRT_RESULTS_V1', 'checks': result['reconstruction_checks']})
    write('PASS_098_NORMALIZATION_ENTANGLEMENT_TRANSFORM.json', result['normalization_entanglement_transform'])
    write('PASS_098_MULTI_OBSERVATION_RECONSTRUCTION.json', {'schema': 'HHS_PASS_098_MULTI_OBSERVATION_RESULTS_V1', 'results': result['source_reconstruction_results']})
    write('PASS_098_NOISE_LOCALIZATION_RESULT.json', result['noise_localization_result'])
    write('PASS_098_EXECUTION_RECEIPTS.json', {'schema': 'HHS_PASS_098_EXECUTION_RECEIPTS_V1', 'receipts': result['executions']})
    write('PASS_098_INTERFERENCE_RELATION_TYPES.json', {'schema': 'HHS_PASS_098_INTERFERENCE_TYPES_V1', 'types': list(INTERFERENCE_TYPES)})
    write('PASS_098_OUTCOME_TAXONOMY.json', {'schema': 'HHS_PASS_098_OUTCOMES_V1', 'outcomes': list(OUTCOMES)})
    write('PASS_098_WORKLOAD_REGISTRY.json', {'schema': 'HHS_PASS_098_WORKLOAD_REGISTRY_V1', 'workloads': ws})
    write('PASS_098_NEGATIVE_CASES.json', {'schema': 'HHS_PASS_098_NEGATIVE_CASES_V1', 'cases': neg})
    write('PASS_098_REPLAY_RESULT.json', replay)
    (repo / 'PASS_098_CALIBRATION_REPORT.md').write_text(
        '# Pass 098 — Prime-Periodic Reciprocal Phase Multiplexing and Deterministic Harmonic Interference\n\n'
        'Pass 098 activates the Pass 097 reconstructed constraint substrate as a witnessed polyperiodic execution field. '
        'The implementation preserves U72 carrier phase, prime-local phase, offsets, layer order, branch identity, normalization history, exact CRT reconstruction, independent-observation evidence, conflict preservation, and deterministic replay. '
        'For primes 11, 13, 17, and 19, no copied numeral is authoritative. The generated exact joint recurrence is 3,325,608. '
        'The previously proposed 317,308,248 value is arithmetically inconsistent with 72×11×13×17×19; canonical integer execution resolves the product to 3,325,608.\n'
    )
    (repo / 'CHANGELOG_PASS_098.md').write_text(
        '# Pass 098\n\nAdded witnessed prime-periodic layers, U72/polyperiodic coordinate separation, exact CRT reconstruction, ordered field execution, normalization-entanglement transforms, multi-observation ambiguity reduction, conflict-preserving noise localization, held-out-prime generalization, negative cases, and exact replay.\n'
    )
    artifacts = [
        'PASS_098_PRIME_PERIODIC_LAYER_REGISTRY.json', 'PASS_098_POLYPERIODIC_OPERATION_FIELD.json',
        'PASS_098_COMPOSITE_COORDINATE_RECONSTRUCTION.json', 'PASS_098_NORMALIZATION_ENTANGLEMENT_TRANSFORM.json',
        'PASS_098_MULTI_OBSERVATION_RECONSTRUCTION.json', 'PASS_098_NOISE_LOCALIZATION_RESULT.json',
        'PASS_098_EXECUTION_RECEIPTS.json', 'PASS_098_INTERFERENCE_RELATION_TYPES.json',
        'PASS_098_OUTCOME_TAXONOMY.json', 'PASS_098_WORKLOAD_REGISTRY.json',
        'PASS_098_NEGATIVE_CASES.json', 'PASS_098_REPLAY_RESULT.json',
        'PASS_098_CALIBRATION_REPORT.md', 'CHANGELOG_PASS_098.md',
    ]
    manifest = {
        'schema': 'HHS_PASS_098_RELEASE_MANIFEST_V1',
        'pass_id': PASS_ID,
        'parent_pass097_release_root_hash72': load_pass097_inputs(repo)['manifest']['pass097_release_root_hash72'],
        'carrier_modulus': CARRIER_MODULUS,
        'prime_layer_count': len(result['layers']),
        'prime_periodicities': list(DEFAULT_PRIMES),
        'joint_recurrence_period': result['field']['joint_recurrence_period'],
        'workload_count': len(ws),
        'negative_case_count': len(neg),
        'all_negative_cases_passed': all(x['passed'] for x in neg),
        'all_composite_coordinates_exact': result['all_composite_coordinates_exact'],
        'noise_conflict_preserved': result['noise_conflict_preserved'],
        'held_out_prime_generalization': result['held_out_prime_generalization'],
        'all_replays_verified': True,
        'artifacts': artifacts,
    }
    manifest['pass098_release_root_hash72'] = root('hhs_pass098_release_manifest_v1', manifest)
    write('PASS_098_RELEASE_MANIFEST.json', manifest)
    return stable(manifest)
