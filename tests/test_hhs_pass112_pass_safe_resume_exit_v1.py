from copy import deepcopy

import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import ContinuationError
from hhs_runtime.hhs_pass112_pass_safe_resume_exit_v1 import (
    PassSafeExitEngine,
    PassSafeExitError,
    ResourceLedger,
    TrackedResource,
    _build_pass111_fixture,
    _default_resources,
    pass112_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass112_self_test()


def test_pass112_completed_exit_is_truthful_and_reconstructable(result):
    receipt = result["completed_exit"]["exit_receipt"]
    assert receipt["exit_classification"] == "EXIT_COMPLETED"
    assert receipt["workload_completed"] is True
    assert receipt["temporary_authority_retired"] is True
    assert receipt["resume_permitted"] is False
    assert result["completed_reconstruction"]["reconstruction_status"] == "RECONSTRUCTED"


def test_pass112_failed_resume_is_not_completion_and_preserves_checkpoint(result):
    bundle = result["failed_resume_exit"]
    receipt = bundle["exit_receipt"]
    checkpoint = bundle["exit_checkpoint"]
    assert receipt["exit_classification"] == "EXIT_RESUME_REJECTED"
    assert receipt["workload_completed"] is False
    assert checkpoint["last_valid_state"]["step_index"] == 12
    assert result["failed_resume_progress_mutated"] is False
    assert result["incorrect_completion_report_count"] == 0


def test_pass112_preserves_receipts_before_cleanup(result):
    for name in ("completed_exit", "failed_resume_exit"):
        checkpoint = result[name]["exit_checkpoint"]
        cleanup = result[name]["cleanup_receipt"]
        assert checkpoint["preserved_receipt_roots"]
        assert checkpoint["preserved_receipt_history_root_hash72"]
        assert cleanup["exit_checkpoint_root_hash72"] == checkpoint["exit_checkpoint_root_hash72"]
        assert cleanup["cleanup_status"] == "CLEANUP_VALIDATED"


def test_pass112_releases_replay_and_temporary_memory_and_closes_handles(result):
    cleanup = result["completed_exit"]["cleanup_receipt"]
    assert cleanup["replay_objects_released"] == ["tail_replay_buffer"]
    assert cleanup["temporary_objects_released"] == ["temporary_candidate_buffer"]
    assert cleanup["external_handles_closed"] == ["runtime_file_handle"]
    assert set(cleanup["authoritative_objects_preserved"]) == {"authoritative_exit_state", "preserved_receipt_bundle"}
    handle = next(x for x in cleanup["resource_dispositions"] if x["resource_id"] == "runtime_file_handle")
    assert handle["size_bytes"] == "TYPED_UNAVAILABLE"


def test_pass112_cleanup_is_idempotent(result):
    assert result["cleanup_idempotent"] is True
    dispositions = result["completed_exit"]["cleanup_receipt"]["resource_dispositions"]
    assert all(x["release_event_count"] <= 1 for x in dispositions)


def test_pass112_completed_result_matches_uninterrupted(result):
    assert result["completed_final_equals_uninterrupted"] is True
    assert result["status"] == "PASS"
    assert result["authoritative_state_loss_count"] == 0
    assert result["receipt_preservation_ratio"] == "1/1"


def test_pass112_rejects_cleanup_before_checkpoint_preservation():
    ledger = ResourceLedger(_default_resources())
    with pytest.raises(PassSafeExitError) as exc:
        ledger.cleanup(preservation_verified=False)
    assert exc.value.code == "REJECT_MEMORY_CLEANUP_BEFORE_STATE_PRESERVATION"


def test_pass112_rejects_open_receipt_transaction():
    workload, continuation, cache, lease, _ = _build_pass111_fixture()
    engine = PassSafeExitEngine(workload.operation_id)
    with pytest.raises(PassSafeExitError) as exc:
        engine.finalize_exit_checkpoint(
            cache=cache,
            exit_classification="EXIT_SUSPENDED_FOR_LATER_RESUME",
            open_receipt_transaction=True,
        )
    assert exc.value.code == "REJECT_EXIT_CHECKPOINT_WITH_OPEN_RECEIPT_TRANSACTION"


def test_pass112_rejects_partial_mutation_checkpoint():
    workload, _, cache, _, _ = _build_pass111_fixture()
    engine = PassSafeExitEngine(workload.operation_id)
    with pytest.raises(PassSafeExitError) as exc:
        engine.finalize_exit_checkpoint(
            cache=cache,
            exit_classification="EXIT_SUSPENDED_FOR_LATER_RESUME",
            partial_mutation_present=True,
        )
    assert exc.value.code == "REJECT_CHECKPOINT_FROM_PARTIALLY_MUTATED_STATE"


def test_pass112_dependency_failure_routes_to_repair_required():
    workload, continuation, cache, lease, _ = _build_pass111_fixture()
    stale = deepcopy(cache)
    stale["dependency_root_hash72"] = "changed"
    error = None
    try:
        continuation.replay_tail(stale, lease)
    except ContinuationError as exc:
        error = exc
    assert error is not None
    engine = PassSafeExitEngine(workload.operation_id)
    assert engine.classify_exit(completion=None, resume_error=error) == "EXIT_DEPENDENCY_REPAIR_REQUIRED"


def test_pass112_deferred_resource_exit_retains_resume_authority():
    workload, _, cache, _, _ = _build_pass111_fixture()
    engine = PassSafeExitEngine(workload.operation_id)
    classification = engine.classify_exit(completion=None, resume_error=None, defer_reason="RESOURCE_BOUND")
    checkpoint = engine.finalize_exit_checkpoint(cache=cache, exit_classification=classification)
    disposition = engine.disposition_cache(checkpoint, cache)
    assert classification == "EXIT_RESOURCE_BOUND"
    assert disposition["cache_disposition"] == "RETAINED_FOR_REVALIDATION_OR_RESUME"
    assert disposition["continuation_authority_active"] is True


def test_pass112_rejects_parallel_branch_inconsistency():
    workload, _, cache, _, _ = _build_pass111_fixture()
    engine = PassSafeExitEngine(workload.operation_id)
    branch = deepcopy(cache["validated_current_state"])
    with pytest.raises(PassSafeExitError) as exc:
        engine.finalize_exit_checkpoint(
            cache=cache,
            exit_classification="EXIT_SUSPENDED_FOR_LATER_RESUME",
            branch_states=[branch, deepcopy(branch)],
        )
    assert exc.value.code == "REJECT_PARALLEL_BRANCH_EXIT_INCONSISTENCY"


def test_pass112_detects_corrupted_cold_boot_bundle(result):
    bundle = deepcopy(result["completed_exit"])
    bundle["exit_receipt"]["workload_completed"] = False
    reconstructed = PassSafeExitEngine.reconstruct_exit(bundle)
    assert reconstructed["reconstruction_status"] == "REJECTED"
    assert reconstructed["checks"]["exit_receipt_root"] is False


def test_pass112_service_registered_and_conformance_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry

    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.pass_safe_resume_exit.pass112")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "receipt_preservation_before_cleanup" in service["guards"]
    assert "zero_bypass_runtime_interposer" in service["guards"]
