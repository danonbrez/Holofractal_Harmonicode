from fractions import Fraction

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_phase_lattice_v1 import (
    PhaseState,
    WORKLOAD_IDS,
    assert_workloads,
    collatz_orbit,
    integer_phase_embedding,
    phase_trace,
    pure_workloads,
    quadratic_reciprocity_checks,
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


def test_collatz_seed_seven_only_bounded_claim():
    orbit = collatz_orbit(7, 64)
    assert orbit[-1] == 1
    assert orbit[:4] == [7, 11, 17, 26]


def test_quadratic_reciprocity_exact_bounded_cases():
    rows = quadratic_reciprocity_checks(43)
    assert rows
    assert all(row["ok"] for row in rows)


def test_all_workloads_close_without_external_theorem_claims():
    workloads = pure_workloads()
    assert tuple(workloads) == WORKLOAD_IDS
    assert_workloads(workloads)
    assert workloads["W191-C"]["checks"]["zeta_zero_not_numerically_or_analytically_claimed"]
    assert workloads["W191-D"]["checks"]["universal_collatz_convergence_not_claimed"]
