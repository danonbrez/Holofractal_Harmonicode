from pathlib import Path
import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass092_prime_product_harmonic_manifolds_v1 import (
    commutator, default_workload, generate_seeds, negative_cases, run, verify_replay, workload_registry,
)

R = Path(__file__).resolve().parents[1]


def test_square_free_seed_lattice_is_exact_and_reconstructable():
    seeds = generate_seeds(R, basis_size=4, max_exponent=1)
    assert len(seeds) == 16
    assert len({tuple(s["factor_vector"]) for s in seeds}) == 16
    assert all(isinstance(s["exact_value"], int) for s in seeds)


def test_operator_parameter_and_seed_identity_are_independent():
    result = run(R, default_workload(R, workload_id="T92:axes", basis_size=3, operator_count=3))
    assert result["operator_prime_count"] == 3
    assert result["lane_count"] == len(result["workload"]["seeds"]) * 3
    assert all(l["seed_root_hash72"] and l["operator_root_hash72"] for l in result["lane_receipts"])


def test_generalized_cycle_discovery_does_not_force_421():
    result = run(R, default_workload(R, workload_id="T92:cycles", basis_size=2, operator_count=2, max_steps=128))
    p5 = [l for l in result["lane_receipts"] if l["operator_prime"] == 5 and l["exact_seed_value"] == 1][0]
    assert p5["cycle_status"] == "NEW_CYCLE_DETECTED"
    assert p5["cycle_states"] == [1, 6, 3, 16, 8, 4, 2]


def test_noncommutative_prime_operator_commutator_is_exact():
    c = commutator(5, 7, 11)
    assert c["difference"] == c["expected"] == -2


def test_cross_operator_same_state_does_not_authorize_shared_future():
    result = run(R, default_workload(R, workload_id="T92:cross", basis_size=3, operator_count=3, max_steps=64))
    cross = [e for e in result["state_intersections"] if not e["same_operator_family"]]
    assert cross
    assert all(not e["shared_future_authorized"] for e in cross)


def test_factor_vector_identity_survives_every_lane():
    result = run(R, default_workload(R, workload_id="T92:factors", basis_size=4, operator_count=2))
    seed_vectors = {s["seed_root_hash72"]: s["factor_vector"] for s in result["workload"]["seeds"]}
    assert all(l["factor_vector"] == seed_vectors[l["seed_root_hash72"]] for l in result["lane_receipts"])


def test_scheduled_operator_order_is_identity_bearing_and_replayable():
    w = default_workload(R, workload_id="T92:schedule", basis_size=3, operator_count=3, mode="PRIME_SCHEDULED_MANIFOLD")
    replay = verify_replay(R, w)
    assert replay["deterministic_replay_verified"]


def test_bounded_results_are_not_asymptotic_claims():
    w = default_workload(R, workload_id="T92:bound", basis_size=4, operator_count=3, max_steps=1)
    result = run(R, w)
    assert result["bounded_lanes"] > 0
    assert result["unbounded_curriculum_not_single_run"] is True


def test_all_mandatory_negative_cases_pass():
    assert all(c["passed"] for c in negative_cases(R))


def test_registry_has_w92_01_through_w92_12():
    workloads = workload_registry(R)
    assert len(workloads) == 12
    assert workloads[0]["workload_id"].startswith("W92-01")
    assert workloads[-1]["workload_id"].startswith("W92-12")
