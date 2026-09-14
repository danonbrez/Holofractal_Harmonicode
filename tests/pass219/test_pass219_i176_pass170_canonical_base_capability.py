from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException

import hhs_runtime.pass219.pass170_canonical_base_capability_i176 as i176
from hhs_backend.pass170_audio_language_routes import (
    PENDING_CAPABILITY_DETAIL,
    enforce_audio_public_admission,
)

ROOT = Path(__file__).resolve().parents[2]


def test_i176_repository_state_verifies_exact_nonterminal_boundary() -> None:
    report = i176.verify_i176_canonical_base_capability(ROOT)
    assert report["evidence_verified"] is True
    assert report["observed_launcher_count"] == 6
    assert report["canonical_redirect_count"] == 6
    assert report["pending_launcher_count"] == 0
    assert report["all_public_launchers_canonical"] is True
    assert report["audio_capability_scope_resolved"] is False
    assert report["audio_public_admission_fail_closed"] is True
    assert report["new_capability_scope_created"] is False
    assert report["fastapi_constructor_count_preserved"] == 10
    assert report["target_blockers"] == list(i176.EXPECTED_TARGET_BLOCKERS)
    assert report["pass170_terminal_contract_verified"] is False
    assert report["next_boundary"] == i176.NEXT_BOUNDARY


def test_unresolved_audio_public_admission_refuses_before_execution() -> None:
    with pytest.raises(HTTPException) as exc:
        enforce_audio_public_admission()
    assert exc.value.status_code == 503
    assert exc.value.detail == PENDING_CAPABILITY_DETAIL


def test_capability_reconciliation_does_not_invent_scope() -> None:
    payload = json.loads((ROOT / i176.CAPABILITY_RECONCILIATION).read_text(encoding="utf-8"))
    audio = payload["audio_operation"]
    assert audio["reconciliation_status"] == "UNRESOLVED_NO_AUTHORITATIVE_INHERITED_AUDIO_SCOPE"
    assert audio["invent_new_scope_in_i176"] is False
    assert audio["admit_without_resolved_policy"] is False
    assert payload["invariants"]["fail_closed_until_capability_model_resolved"] is True
    assert payload["invariants"]["new_capability_authority_created"] is False


def test_launcher_registry_has_no_pending_public_launchers() -> None:
    payload = json.loads((ROOT / i176.LAUNCHER_REGISTRY).read_text(encoding="utf-8"))
    assert payload["pending_paths"] == []
    assert len(payload["launcher_records"]) == 6
    assert all(
        record["expected_target"] == "hhs_backend.public_api_server:app"
        for record in payload["launcher_records"]
    )


def test_weakened_admission_overlay_fails_closed(tmp_path: Path, monkeypatch) -> None:
    payload = json.loads((ROOT / i176.ADMISSION_OVERLAY).read_text(encoding="utf-8"))
    payload["admission_policy"] = "ALLOW_PENDING_POLICY"
    bad = tmp_path / "bad_overlay.json"
    bad.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(i176, "ADMISSION_OVERLAY", str(bad))
    report = i176.verify_i176_canonical_base_capability(ROOT, fail_closed=False)
    assert report["evidence_verified"] is False
    assert "PASS170_I176_ADMISSION_POLICY_INVALID" in report["evidence_blockers"]
