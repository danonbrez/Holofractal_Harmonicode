from __future__ import annotations

import copy
from pathlib import Path

import pytest

import hhs_runtime.pass219.pass170_launcher_retirement_i174 as i174

ROOT = Path(__file__).resolve().parents[2]


def test_repository_i174_launcher_retirement_evidence_is_green() -> None:
    report = i174.verify_i174_launcher_retirement(ROOT)
    assert report["evidence_verified"] is True
    assert report["evidence_blockers"] == []
    assert report["classification"] == i174.CLASSIFICATION
    assert report["parent_i173_exact_main_verified"] is True
    assert report["i173_operation_record_count_preserved"] == 47
    assert report["observed_launcher_count"] == 6
    assert report["canonical_redirect_count"] == 4
    assert report["pending_launcher_count"] == 2
    assert report["newly_redirected_paths"] == list(i174.EXPECTED_REDIRECTED)
    assert report["pending_launcher_paths"] == sorted(i174.EXPECTED_PENDING)
    assert report["fastapi_constructor_count_preserved"] == 10
    assert report["target_blockers"] == list(i174.EXPECTED_TARGET_BLOCKERS)
    assert report["pass170_terminal_contract_verified"] is False
    assert report["canonical_state_mutated"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["floating_point_canonical_authority"] is False
    assert report["next_boundary"] == i174.NEXT_BOUNDARY


def test_three_new_legacy_launchers_target_canonical_gateway() -> None:
    observed = {
        item["path"]: item["target"]
        for item in i174._scan_uvicorn_launchers(ROOT)
    }
    for path in i174.EXPECTED_REDIRECTED:
        assert observed[path] == i174.CANONICAL_GATEWAY


def test_i174_fails_closed_on_redirect_regression(monkeypatch: pytest.MonkeyPatch) -> None:
    original = i174._scan_uvicorn_launchers(ROOT)
    mutated = copy.deepcopy(original)
    record = next(item for item in mutated if item["path"] == "hhs_runtime/main.py")
    record["target"] = "hhs_runtime.main:app"
    monkeypatch.setattr(i174, "_scan_uvicorn_launchers", lambda _root: mutated)
    with pytest.raises(i174.Pass170I174VerificationError, match="LAUNCHER_TARGET_MISMATCH"):
        i174.verify_i174_launcher_retirement(ROOT)


def test_i174_fails_closed_if_i173_record_count_drifts(monkeypatch: pytest.MonkeyPatch) -> None:
    original_json = i174._json

    def fake_json(path: Path):
        payload = original_json(path)
        if path.name == i174.OPERATION_INDEX:
            payload = copy.deepcopy(payload)
            payload["aggregate_record_count"] = 46
        return payload

    monkeypatch.setattr(i174, "_json", fake_json)
    with pytest.raises(i174.Pass170I174VerificationError, match="OPERATION_RECORD_COUNT_MISMATCH"):
        i174.verify_i174_launcher_retirement(ROOT)


def test_i174_fails_closed_on_parent_artifact_identity_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    original_json = i174._json

    def fake_json(path: Path):
        payload = original_json(path)
        if path.name == i174.REGISTRY:
            payload = copy.deepcopy(payload)
            payload["parent_i173_exact_main_artifact"] = 0
        return payload

    monkeypatch.setattr(i174, "_json", fake_json)
    with pytest.raises(i174.Pass170I174VerificationError, match="PARENT_I173_ARTIFACT_MISMATCH"):
        i174.verify_i174_launcher_retirement(ROOT)
