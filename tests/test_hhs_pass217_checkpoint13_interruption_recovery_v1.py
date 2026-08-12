from __future__ import annotations

from pathlib import Path

from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import NativeDispatchRequest
from hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1 import NativeDispatchLedger
from hhs_runtime.hhs_pass217_checkpoint13_interruption_recovery_v1 import (
    CHECKPOINT13_AUTHORITIES,
    CHECKPOINT13_AUTHORITY_MAP,
    CHECKPOINT13_REQUIRED_AUTHORITIES,
    INTERRUPTION_RECOVERY_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from tests.test_hhs_pass217_checkpoint12_learning_tensor_native_v1 import (
    LEDGER_KEY,
    TENSOR_KEY,
    make_native_authority,
    synthetic_anchor,
)
from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import FULL_HYDRATION_DOMAIN
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import MovingTensorState


def _decisions(decision):
    return {
        row["authority_id"]: row
        for row in decision["inherited_execution_authority_reachability"]["decisions"]
    }


def _second_request(first: NativeDispatchRequest, authority, tensor: MovingTensorState) -> NativeDispatchRequest:
    state = authority.runtime_state
    return NativeDispatchRequest(
        entry_hash216=first.entry_hash216,
        operation_id=first.operation_id,
        expected_parent_hash216=state.current_state_root_hash216,
        expected_tensor_root_hash216=tensor.tensor_root_hash216,
        timestamp_ns=tensor.anchor.requested_timestamp_ns + 2,
        hydration_lane=4,
        operands=(10, 20),
        read_set=("register.a", "register.b"),
        write_set=("register.result",),
    )


def _recovery_fixture(tmp_path: Path):
    anchor = synthetic_anchor()
    tensor = MovingTensorState.derive(
        root_key=TENSOR_KEY,
        trusted_anchor=anchor,
        tensor_sequence=1,
        genesis_epoch=13,
        domain_size=FULL_HYDRATION_DOMAIN,
    )

    baseline_dir = tmp_path / "baseline"
    recovery_dir = tmp_path / "recovery"
    baseline_dir.mkdir()
    recovery_dir.mkdir()
    baseline, baseline_store, baseline_ledger, baseline_first_request = make_native_authority(
        baseline_dir, tensor
    )
    recovery, recovery_store, recovery_ledger, recovery_first_request = make_native_authority(
        recovery_dir, tensor
    )

    baseline_first = baseline.execute(baseline_first_request)
    recovery_first = recovery.execute(recovery_first_request)
    assert baseline_first.receipt_hash72 == recovery_first.receipt_hash72
    assert baseline_first.successor_state_root_hash216 == recovery_first.successor_state_root_hash216

    baseline_second_request = _second_request(baseline_first_request, baseline, tensor)
    recovery_second_request = _second_request(recovery_first_request, recovery, tensor)
    assert baseline_second_request.to_mapping() == recovery_second_request.to_mapping()
    baseline_second = baseline.execute(baseline_second_request)

    boundary = recovery_ledger.latest()
    assert boundary is not None
    anchor_state = recovery_ledger.anchor_state_root_hash216
    anchor_receipt = recovery_ledger.anchor_receipt_hash72
    database_path = recovery_dir / "native-dispatch.sqlite3"
    recovery_kernel = recovery.native_kernel

    # The interruption boundary is real for this test: discard the original
    # authority's durable ledger handle before the composer attempts recovery.
    recovery_ledger.close()

    request = {
        "schema": INTERRUPTION_RECOVERY_REQUEST_SCHEMA,
        "expected_recovery_sequence": 1,
        "expected_boundary_receipt_hash72": boundary["receipt_hash72"],
        "expected_boundary_state_root_hash216": boundary["successor_state_root_hash216"],
        "expected_boundary_ledger_event_root_hash216": boundary["ledger_event_root_hash216"],
        "expected_tensor_root_hash216": tensor.tensor_root_hash216,
        "next_request": recovery_second_request.to_mapping(),
        "expected_uninterrupted_request_root_hash216": baseline_second.request_root_hash216,
        "expected_uninterrupted_result_root_hash216": baseline_second.result_root_hash216,
        "expected_uninterrupted_successor_state_root_hash216": baseline_second.successor_state_root_hash216,
        "expected_uninterrupted_receipt_hash72": baseline_second.receipt_hash72,
        "expected_uninterrupted_result_values": list(baseline_second.result_values),
    }
    fixture = {
        "anchor": anchor,
        "tensor": tensor,
        "baseline": baseline,
        "baseline_store": baseline_store,
        "baseline_ledger": baseline_ledger,
        "recovery": recovery,
        "recovery_store": recovery_store,
        "database_path": database_path,
        "anchor_state": anchor_state,
        "anchor_receipt": anchor_receipt,
        "recovery_kernel": recovery_kernel,
        "request": request,
        "baseline_second": baseline_second,
    }
    return fixture


def _close_fixture(fixture) -> None:
    try:
        fixture["baseline_ledger"].close()
    except Exception:
        pass
    try:
        fixture["baseline_store"].close()
    except Exception:
        pass
    try:
        fixture["recovery_store"].close()
    except Exception:
        pass


def test_checkpoint13_maps_true_persistent_recovery_not_pause_or_snapshot() -> None:
    assert CHECKPOINT13_AUTHORITIES == ("interruption_recovery",)
    authority = CHECKPOINT13_AUTHORITY_MAP["interruption_recovery"]
    assert authority["origin_pass"] == 213
    assert authority["origin_iteration"] == 10
    assert authority["terminal_evidence_alignment_iteration"] == 11
    assert authority["persistent_ledger_required"] is True
    assert authority["distinct_from_snapshot_reuse"] is True
    assert authority["distinct_from_full_replay"] is True
    assert authority["pass213_iteration11_pause_hook_is_runtime_authority"] is False


def test_checkpoint13_no_domain_is_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "none-semantic.json"),
    )
    assert decision is not None and decision["ok"] is True
    authority = decision["inherited_execution_authority_reachability"]
    assert authority["required_authority_count"] == len(CHECKPOINT13_REQUIRED_AUTHORITIES) == 25
    assert tuple(authority["checkpoint_scope"][-1:]) == CHECKPOINT13_AUTHORITIES
    row = _decisions(decision)["interruption_recovery"]
    assert row["state"] == "NOT_APPLICABLE"
    assert row["mechanically_proven"] is True


def test_checkpoint13_reopens_persistent_ledger_and_matches_uninterrupted_control(tmp_path) -> None:
    fixture = _recovery_fixture(tmp_path)
    try:
        request = fixture["request"]
        decision = compose_bound_route_ingress(
            "api.runtime.services.dispatch",
            {"service": "example", "interruption_recovery": request},
            cache={},
            semantic_cache=SemanticCompositionCache(tmp_path / "recovery-semantic.json"),
            interruption_recovery_database_path=fixture["database_path"],
            interruption_recovery_ledger_key=LEDGER_KEY,
            interruption_recovery_anchor_state_root_hash216=fixture["anchor_state"],
            interruption_recovery_anchor_receipt_hash72=fixture["anchor_receipt"],
            interruption_recovery_protected_store=fixture["recovery_store"],
            interruption_recovery_native_kernel=fixture["recovery_kernel"],
            interruption_recovery_tensor_state=fixture["tensor"],
        )
        assert decision is not None and decision["ok"] is True
        assert decision["propagation_allowed"] is True
        authority = decision["inherited_execution_authority_reachability"]
        assert authority["required_authority_count"] == 25
        rows = _decisions(decision)
        row = rows["interruption_recovery"]
        assert row["state"] == "ACTIVE_IN_PATH"
        witness = row["traversal_witness"]
        control = fixture["baseline_second"]
        assert witness["persistent_ledger_reopened"] is True
        assert witness["prior_process_authority_reused"] is False
        assert witness["prior_process_runtime_state_reused"] is False
        assert witness["uninterrupted_control_equal"] is True
        assert witness["snapshot_reuse_used"] is False
        assert witness["full_history_replay_used"] is False
        assert witness["pass213_iteration11_pause_hook_used"] is False
        assert witness["recovered_sequence"] == 2
        assert witness["result_values"] == [30]
        assert witness["request_root_hash216"] == control.request_root_hash216
        assert witness["result_root_hash216"] == control.result_root_hash216
        assert witness["successor_state_root_hash216"] == control.successor_state_root_hash216
        assert witness["receipt_hash72"] == control.receipt_hash72

        reopened = NativeDispatchLedger(
            database_path=fixture["database_path"],
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=fixture["anchor_state"],
            anchor_receipt_hash72=fixture["anchor_receipt"],
        )
        try:
            assert reopened.count() == 2
            assert reopened.verify_chain() is True
            assert reopened.latest()["receipt_hash72"] == control.receipt_hash72
        finally:
            reopened.close()
    finally:
        _close_fixture(fixture)


def test_checkpoint13_rejects_recovery_on_read_only_route_before_mutation(tmp_path) -> None:
    request = {
        "schema": INTERRUPTION_RECOVERY_REQUEST_SCHEMA,
        "expected_recovery_sequence": 1,
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"interruption_recovery": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "readonly-semantic.json"),
    )
    assert decision is not None and decision["ok"] is False
    row = _decisions(decision)["interruption_recovery"]
    assert row["state"] is None
    assert "REJECT_INTERRUPTION_RECOVERY_CONTROLLED_MUTATION_SURFACE_REQUIRED" in row[
        "traversal_witness"
    ]["reason"]


def test_checkpoint13_stale_boundary_fails_without_advancing_ledger(tmp_path) -> None:
    fixture = _recovery_fixture(tmp_path)
    try:
        request = dict(fixture["request"])
        request["expected_boundary_state_root_hash216"] = "f" * 64
        inner = dict(request["next_request"])
        inner["expected_parent_hash216"] = "f" * 64
        request["next_request"] = inner
        decision = compose_bound_route_ingress(
            "api.runtime.services.dispatch",
            {"service": "example", "interruption_recovery": request},
            cache={},
            semantic_cache=SemanticCompositionCache(tmp_path / "stale-semantic.json"),
            interruption_recovery_database_path=fixture["database_path"],
            interruption_recovery_ledger_key=LEDGER_KEY,
            interruption_recovery_anchor_state_root_hash216=fixture["anchor_state"],
            interruption_recovery_anchor_receipt_hash72=fixture["anchor_receipt"],
            interruption_recovery_protected_store=fixture["recovery_store"],
            interruption_recovery_native_kernel=fixture["recovery_kernel"],
            interruption_recovery_tensor_state=fixture["tensor"],
        )
        assert decision is not None and decision["ok"] is False
        row = _decisions(decision)["interruption_recovery"]
        assert row["state"] is None
        assert "REJECT_INTERRUPTION_RECOVERY_PERSISTED_FRONTIER_MISMATCH" in row[
            "traversal_witness"
        ]["reason"]

        reopened = NativeDispatchLedger(
            database_path=fixture["database_path"],
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=fixture["anchor_state"],
            anchor_receipt_hash72=fixture["anchor_receipt"],
        )
        try:
            assert reopened.count() == 1
            assert reopened.verify_chain() is True
        finally:
            reopened.close()
    finally:
        _close_fixture(fixture)
