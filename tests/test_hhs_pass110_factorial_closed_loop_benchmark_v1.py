import pytest

from hhs_runtime.hhs_pass110_factorial_closed_loop_benchmark_v1 import (
    FactorialBenchmarkError,
    FactorialClosedLoopBenchmark,
    ResourceContract,
    pass110_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass110_self_test()


def test_pass110_executes_every_admitted_operation_individually(result):
    assert result["status"] == "PASS"
    individual = [x for x in result["loop_receipts"] if x["loop_class"] == "GRADE_0_INDIVIDUAL"]
    assert len(individual) == 3
    assert {x["ordered_operation_ids"][0] for x in individual} == {"BACKEND", "ATTACKS", "COMPOSITION"}
    assert all(x["real_production_execution_count"] == 1 for x in individual)


def test_pass110_executes_both_native_serial_orders(result):
    pairs = [x for x in result["loop_receipts"] if x["loop_class"] == "GRADE_2_ORDERED_PAIR"]
    assert len(pairs) == 2
    assert {tuple(x["ordered_operation_ids"]) for x in pairs} == {
        ("BACKEND", "ATTACKS"), ("ATTACKS", "BACKEND")
    }


def test_pass110_runs_bounded_factorial_grade_truthfully(result):
    assert result["grade3_raw_factorial_space"] == 6
    assert result["grade3_executed_unique_permutations"] == 0
    assert result["grade3_execution_mode"] == "BOUNDED_FRONTIER"
    assert result["sampled_space_reported_as_exhaustive"] is False
    assert result["termination_status"] == "RESOURCE_BOUND_REACHED"


def test_pass110_executes_parallel_schedules(result):
    parallel = [x for x in result["loop_receipts"] if x["loop_class"] == "PARALLEL_PARTIAL_ORDER"]
    assert len(parallel) == 1  # bounded by total real-operation budget
    assert parallel[0]["parallel_schedule_id"] in {
        "BACKEND_LEFT_ATTACKS_RIGHT", "ATTACKS_LEFT_BACKEND_RIGHT"
    }
    assert parallel[0]["real_production_execution_count"] == 3


def test_pass110_closure_is_receipt_reconstructable_not_fake_inverse(result):
    assert result["all_closure_vectors_passed"] is True
    assert result["failed_loops"] == 0
    assert all(x["loop_status"] == "VALID_RECEIPT_RECONSTRUCTABLE_CLOSED_LOOP" for x in result["loop_receipts"])
    assert all(x["mock_components"] == [] for x in result["loop_receipts"])
    assert all(x["parallel_test_computation_used"] is False for x in result["loop_receipts"])


def test_pass110_frontier_is_resumable_and_exact(result):
    frontier = result["frontier"]
    assert frontier["executed_grade3_permutations"] == 0
    assert frontier["next_permutation_index"] == 0
    assert frontier["pending_grade3_permutations"] == 6
    assert frontier["continuation_root_hash72"]


def test_pass110_enforces_resource_contract():
    benchmark = FactorialClosedLoopBenchmark(ResourceContract(maximum_real_operation_invocations=0))
    benchmark.started_ns = 1
    with pytest.raises(FactorialBenchmarkError) as exc:
        benchmark._budget_check(1)
    assert exc.value.code == "REJECT_RESOURCE_CONTRACT_OVERRUN"


def test_pass110_service_registered_and_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.factorial_closed_loop_benchmark.pass110")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "zero_bypass_runtime_interposer" in service["guards"]
    assert "sampled_space_never_reported_as_exhaustive" in service["guards"]
