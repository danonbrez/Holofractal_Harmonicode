from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import hhs_runtime.pass219.pass170_full_operation_records_i173 as i173
from hhs_runtime.pass219.pass170_full_operation_records_i173 import (
    CLASSIFICATION,
    EXPECTED_TARGET_BLOCKERS,
    NEXT_BOUNDARY,
    Pass170I173VerificationError,
    _expected_routes,
    _route_handlers,
    verify_i173_full_operation_records,
)

ROOT = Path(__file__).resolve().parents[2]


def _json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_repository_i173_full_operation_records_are_executable_source_bound() -> None:
    report = verify_i173_full_operation_records(ROOT)
    assert report["evidence_verified"] is True
    assert report["evidence_blockers"] == []
    assert report["classification"] == CLASSIFICATION
    assert report["inherited_i172_verified"] is True
    assert report["frozen_i171_route_identity_registry_retained"] is True
    assert report["shard_count"] == 5
    assert report["expected_route_count"] == 47
    assert report["operation_record_count"] == 47
    assert report["unique_operation_id_count"] == 47
    assert report["unique_route_signature_count"] == 47
    assert report["executable_source_bound_count"] == 47
    assert report["full_operation_records_verified"] is True
    assert report["transport_parity_pending_count"] == 46
    assert report["receipt_replay_pending_count"] == 47
    assert report["target_blockers"] == list(EXPECTED_TARGET_BLOCKERS)
    assert "PASS170_FULL_OPERATION_RECORDS_PENDING" not in report["target_blockers"]
    assert report["pass170_terminal_contract_verified"] is False
    assert report["canonical_state_mutated"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["floating_point_canonical_authority"] is False
    assert report["next_boundary"] == NEXT_BOUNDARY


def test_i173_parent_route_identity_set_remains_exactly_47() -> None:
    parent = _json("HHS_PUBLIC_OPERATION_REGISTRY.json")
    expected = _expected_routes(parent)
    assert len(expected) == 47
    assert expected["public.receipts.websocket"] == {
        "method": "WEBSOCKET",
        "path": "/v1/receipts/ws",
        "module": "hhs_backend.public_api_server",
    }
    assert expected["pass168.parameter_circuit.candidate.commit"]["path"] == "/v1/parameter-circuit/candidates/{candidate_id}/commit"
    assert expected["pass169.algebra.transition.reverse"]["path"] == "/v1/algebra/transitions/{transition_id}/reverse"


def test_i173_source_binding_resolves_actual_decorated_handlers() -> None:
    direct = _route_handlers(ROOT / "hhs_backend/public_api_server.py")
    pass168 = _route_handlers(ROOT / "hhs_backend/pass168_parameter_circuit_routes.py")
    pass169 = _route_handlers(ROOT / "hhs_backend/pass169_algebra_routes.py")
    assert direct[("GET", "/v1/system/status")] == "system_status"
    assert direct[("WEBSOCKET", "/v1/receipts/ws")] == "receipt_stream"
    assert pass168[("POST", "/v1/parameter-circuit/candidates/{candidate_id}/commit")] == "commit_candidate"
    assert pass169[("POST", "/v1/algebra/transitions/{transition_id}/reverse")] == "algebra_reverse"


def test_i173_fails_closed_when_required_record_field_is_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    original = i173._load_json

    def mutated(path: Path) -> dict:
        payload = original(path)
        if path.name == "HHS_PUBLIC_OPERATION_RECORDS_DIRECT_V1.json":
            payload = copy.deepcopy(payload)
            payload["records"][0].pop("receipt_class")
        return payload

    monkeypatch.setattr(i173, "_load_json", mutated)
    report = verify_i173_full_operation_records(ROOT, fail_closed=False)
    assert report["evidence_verified"] is False
    assert "PASS170_I173_OPERATION_REQUIRED_FIELDS_MISSING" in report["evidence_blockers"]
    assert report["full_operation_records_verified"] is False


def test_i173_fails_closed_when_source_handler_is_documentation_only(monkeypatch: pytest.MonkeyPatch) -> None:
    original = i173._load_json

    def mutated(path: Path) -> dict:
        payload = original(path)
        if path.name == "HHS_PUBLIC_OPERATION_RECORDS_PASS169_B_V1.json":
            payload = copy.deepcopy(payload)
            payload["records"][-1]["source_binding"]["handler"] = "invented_handler"
        return payload

    monkeypatch.setattr(i173, "_load_json", mutated)
    report = verify_i173_full_operation_records(ROOT, fail_closed=False)
    assert report["evidence_verified"] is False
    assert "PASS170_I173_EXECUTABLE_HANDLER_MISMATCH" in report["evidence_blockers"]
    assert report["executable_source_bound_count"] == 46


def test_i173_parent_duplicate_operation_identity_is_rejected() -> None:
    parent = _json("HHS_PUBLIC_OPERATION_REGISTRY.json")
    mutated = copy.deepcopy(parent)
    mutated["router_delegates"][0]["routes"][0]["route_operation_id"] = "public.system.status"
    with pytest.raises(Pass170I173VerificationError, match="PARENT_OPERATION_ID_DUPLICATE"):
        _expected_routes(mutated)


def test_i173_report_is_deterministic() -> None:
    first = verify_i173_full_operation_records(ROOT)
    second = verify_i173_full_operation_records(ROOT)
    for report in (first, second):
        report.pop("repository_root", None)
    assert first == second
