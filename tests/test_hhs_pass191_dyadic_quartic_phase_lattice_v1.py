from fractions import Fraction

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_formal_outcomes_v1 import (
    FALSIFIED,
    OBSTRUCTED,
    PROVED,
    build_formal_outcome_ledger,
    verify_formal_outcome_ledger,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_phase_lattice_v1 import (
    PhaseState,
    WORKLOAD_IDS,
    assert_workloads,
    collatz_orbit,
    integer_phase_embedding,
    phase_trace,
    quadratic_reciprocity_checks,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_runner_v2 import (
    AUTHORIZED_REPOSITORY_BASELINE,
    BENCHMARK_TIMING_CLASSIFICATION,
    VOLATILE_BENCHMARK_FIELDS,
    formal_workloads,
    normalize_benchmark_artifact,
)


def test_quartic_dyadic_trace_is_exact():
    trace = phase_trace(PhaseState(0, 0), 4)
    assert [state.magnitude() for state in trace] == [
        Fraction(1),
        Fraction(2),
        Fraction(4),
        Fraction(8),
        Fraction(16),
    ]
    assert [state.quartic_phase for state in trace] == [0, 1, 2, 3, 0]


def test_integer_embedding_reconstructs_bounded_sample():
    for n in range(-128, 129):
        row = integer_phase_embedding(n)
        assert row["reconstruction"] == n


def test_collatz_seed_seven_exact_orbit_prefix():
    orbit = collatz_orbit(7, 64)
    assert orbit[-1] == 1
    assert orbit[:4] == [7, 11, 17, 26]


def test_quadratic_reciprocity_exact_bounded_cases():
    rows = quadratic_reciprocity_checks(43)
    assert rows
    assert all(row["ok"] for row in rows)


def test_all_workloads_close_with_registered_formal_obligations():
    workloads = formal_workloads()
    assert tuple(workloads) == WORKLOAD_IDS
    assert_workloads(workloads)
    assert workloads["W191-C"]["checks"]["rh_transfer_obligation_registered"]
    assert workloads["W191-D"]["checks"]["collatz_global_obligation_registered"]
    assert workloads["W191-E"]["checks"]["quadratic_reciprocity_transfer_obligation_registered"]


def test_formal_outcome_ledger_hashes_and_counts_close():
    ledger = build_formal_outcome_ledger()
    result = verify_formal_outcome_ledger(ledger)
    assert result["ok"] is True
    assert result["outcome_count"] == 10
    assert result["outcome_counts"] == {
        PROVED: 4,
        FALSIFIED: 3,
        OBSTRUCTED: 3,
    }


def test_literal_candidates_receive_exact_counterexamples():
    ledger = build_formal_outcome_ledger()
    by_id = {row["obligation_id"]: row for row in ledger["outcomes"]}

    resonance = by_id["DQPL-RESONANCE-LITERAL"]
    assert resonance["status"] == FALSIFIED
    assert resonance["certificate"]["counterexample"] == "t=0"
    assert resonance["certificate"]["left"]["exact_value"] == "i"
    assert resonance["certificate"]["right"]["exact_value"] == "-1"

    critical_axis = by_id["DQPL-CRITICAL-AXIS-LITERAL"]
    assert critical_axis["status"] == FALSIFIED
    assert critical_axis["certificate"]["difference"] == "1"

    fibonacci_product = by_id["DQPL-FIBONACCI-PRODUCT"]
    assert fibonacci_product["status"] == FALSIFIED
    assert fibonacci_product["certificate"]["left"] == "F(3)=2"
    assert fibonacci_product["certificate"]["right"] == "phi*psi=-1"


def test_rh_transfer_obstruction_names_complete_bridge_set():
    ledger = build_formal_outcome_ledger()
    by_id = {row["obligation_id"]: row for row in ledger["outcomes"]}
    rh = by_id["DQPL-RH-TRANSFER"]
    assert rh["status"] == OBSTRUCTED
    assert rh["certificate"]["registered_derivation_path_exists"] is False
    assert rh["dependencies"] == [
        "ZETA_DOMAIN_AND_ANALYTIC_CONTINUATION_ENCODING",
        "ZETA_ZERO_TO_PHASE_CLOSURE_EQUIVALENCE",
        "PHASE_MAP_FAITHFULNESS",
        "OFF_AXIS_ZERO_EXCLUSION_OR_COUNTEREXAMPLE_TRANSFER",
    ]
    assert ledger["hypothesis_decisions"]["RIEMANN_HYPOTHESIS"]["controlling_obligation"] == "DQPL-RH-TRANSFER"


def test_benchmark_normalization_is_stable_across_wall_clock_variance():
    common = {
        "schema": "HHS_PASS_191_NATIVE_BENCHMARK_V1",
        "status": "DETERMINISTIC_BIFURCATION_VERIFIED",
        "branch_count": 4,
        "determinism_mismatch_count": 0,
        "closure_coordinate_roots_match": True,
        "receipt_chain_locks": True,
        "replay_receipt_root_hash72": "stable-root",
        "canonical_float_authority_used": False,
    }
    first = normalize_benchmark_artifact(
        {
            **common,
            "total_execution_ns": 100,
            "native_invocation_ns_reported": 10,
            "operations_per_second": 40.0,
        }
    )
    second = normalize_benchmark_artifact(
        {
            **common,
            "total_execution_ns": 900,
            "native_invocation_ns_reported": 90,
            "operations_per_second": 4.0,
        }
    )

    assert first == second
    assert normalize_benchmark_artifact(first) == first
    assert first["timing_classification"] == BENCHMARK_TIMING_CLASSIFICATION
    assert first["volatile_fields_excluded_from_authority"] == list(
        VOLATILE_BENCHMARK_FIELDS
    )
    assert all(field not in first for field in VOLATILE_BENCHMARK_FIELDS)
    assert AUTHORIZED_REPOSITORY_BASELINE == "992b4e92a54d4656d66af4edfab7e03922addca6"
