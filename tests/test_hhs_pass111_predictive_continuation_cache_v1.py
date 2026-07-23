from copy import deepcopy
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import (
    ContinuationError,
    ContinuationLease,
    Hash72ReceiptChainWorkload,
    PredictiveContinuationEngine,
    ResourceContract,
    _hash,
    pass111_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass111_self_test()


def test_pass111_predicts_deterministically_inevitable_limit(result):
    prediction = result["prediction"]
    assert prediction["prediction_status"] == "LIMIT_DETERMINISTICALLY_INEVITABLE"
    assert prediction["minimum_remaining_work_steps"] == 6
    assert prediction["remaining_resource_steps"] == 0
    assert prediction["prediction_receipt_root_hash72"]


def test_pass111_cache_contains_validated_history_and_no_future_results(result):
    cache = result["cache"]
    assert cache["cache_status"] == "SUSPENDED_AWAITING_RESOURCES"
    assert cache["contains_speculative_results"] is False
    assert len(cache["ordered_receipts"]) == 12
    assert cache["pending_step_start"] == 13
    assert cache["pending_step_end"] == 18
    assert cache["continuation_cache_root_hash72"]


def test_pass111_replays_exact_final_ninth_through_production_path(result):
    cache = result["cache"]
    admission = result["resume_admission"]
    assert cache["tail_length"] == 2
    assert admission["one_ninth_tail_operation_steps"] == [11, 12]
    assert admission["production_path"] == "Hash72ReceiptChainWorkload.execute_step"
    assert admission["cached_suspension_state_root_hash72"] == admission["replayed_suspension_state_root_hash72"]
    assert admission["resume_status"] == "ADMITTED_FOR_CONTINUATION"
    assert all(admission["continuity_vector"].values())


def test_pass111_continues_without_double_count_or_lost_progress(result):
    completion = result["completion"]
    assert completion["completed_useful_steps_before_suspend"] == 12
    assert completion["tail_replay_steps"] == 2
    assert completion["new_useful_steps_after_resume"] == 6
    assert completion["total_useful_steps"] == 18
    assert completion["duplicate_progress_count"] == 0
    assert completion["lost_progress_count"] == 0
    assert result["progress_preservation_ratio"] == "1/1"


def test_pass111_resumed_final_state_matches_uninterrupted_execution(result):
    assert result["final_resumed_equals_uninterrupted"] is True
    assert result["completion"]["final_state"]["state_root_hash72"] == result["uninterrupted_final_state_root_hash72"]
    assert result["status"] == "PASS"


def test_pass111_preserves_real_pass110_frontier(result):
    cache = result["cache"]
    frontier = cache["pass110_frontier"]
    assert result["pass110_frontier_preserved"] is True
    assert frontier["pending_grade3_permutations"] == 6
    assert frontier["next_permutation_index"] == 0
    assert frontier["continuation_root_hash72"]


def _engine_fixture():
    dependency = _hash("test_dependency", {"version": 1})
    capability = _hash("test_capability", {"status": "CANONICAL_EXECUTABLE"})
    workload = Hash72ReceiptChainWorkload("test:continuation", dependency, capability)
    engine = PredictiveContinuationEngine(workload, 10, ResourceContract(6))
    genesis = workload.genesis("fixture")
    state, receipts, states = workload.execute_range(genesis, 1, 6)
    cache = engine.create_cache(
        genesis_state=genesis,
        suspension_state=state,
        states_by_step=states,
        receipts=receipts,
        prediction=engine.predict(6),
    )
    lease = ContinuationLease(workload.operation_id, dependency, capability, cache["tail_length"], 4)
    return workload, engine, cache, lease


def test_pass111_rejects_stale_dependency_cache():
    workload, engine, cache, lease = _engine_fixture()
    stale_workload = Hash72ReceiptChainWorkload(workload.operation_id, _hash("changed", {"v": 2}), workload.capability_admission_root_hash72)
    stale_engine = PredictiveContinuationEngine(stale_workload, 10, ResourceContract(6))
    with pytest.raises(ContinuationError) as exc:
        stale_engine.replay_tail(cache, lease)
    assert exc.value.code == "REJECT_STALE_CONTINUATION_DEPENDENCY"


def test_pass111_rejects_corrupted_cache():
    _, engine, cache, lease = _engine_fixture()
    corrupted = deepcopy(cache)
    corrupted["validated_current_state"]["accumulator"] += 1
    with pytest.raises(ContinuationError) as exc:
        engine.replay_tail(corrupted, lease)
    assert exc.value.code == "REJECT_CORRUPTED_CONTINUATION_CACHE"


def test_pass111_service_registered_and_conformance_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry

    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.predictive_continuation_cache.pass111")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "zero_bypass_runtime_interposer" in service["guards"]
    assert "tail_replay_uses_production_path" in service["guards"]
