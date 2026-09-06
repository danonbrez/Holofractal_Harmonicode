from __future__ import annotations

import asyncio
from pathlib import Path
import sys

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import hhs_backend.pass170_audio_language_routes as audio
from hhs_runtime.pass190.completion import PASS190_NATIVE_PYTHON
from hhs_runtime.pass219.pass170_capability_extension_constructor_i177 import (
    AUDIO_SCOPE,
    verify_i177_capability_extension_constructor,
)

if str(PASS190_NATIVE_PYTHON) not in sys.path:
    sys.path.insert(0, str(PASS190_NATIVE_PYTHON))
from hhs_pass190_capability import issue_capability_token  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SECRET = "pass170-i177-audio-capability-secret-" + ("x" * 40)


def _token(*scopes: str) -> str:
    return issue_capability_token(
        SECRET,
        principal="pass219-i177-test",
        scopes=scopes,
        ttl_seconds=900,
        nonce="pass219-i177-fixed-test-nonce",
    )


class _FakeReceipt:
    def to_dict(self) -> dict[str, object]:
        return {"schema": "HHS_I177_FAKE_AUDIO_RECEIPT", "ok": True}


def _client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv(audio.CAPABILITY_SECRET_ENV, SECRET)
    monkeypatch.setattr(
        audio,
        "run_audio_language_feedback_cycle",
        lambda **_kwargs: _FakeReceipt(),
    )
    app = FastAPI()
    app.include_router(audio.build_pass170_audio_language_router())
    return TestClient(app)


def _body() -> dict[str, object]:
    return {
        "expression": "x+y",
        "items": [],
        "audio_manifest": {},
        "audio_roundtrip_receipt": None,
    }


def test_i177_repository_gate() -> None:
    report = verify_i177_capability_extension_constructor(ROOT)
    assert report["evidence_verified"] is True
    assert report["parent_i176_exact_main_verified"] is True
    assert report["audio_capability_scope"] == AUDIO_SCOPE
    assert report["audio_capability_binding_verified"] is True
    assert report["audio_public_signed_admission_verified"] is True
    assert report["audio_internal_ecc_pq_boundary_preserved"] is True
    assert report["pass190_token_verifier_reused"] is True
    assert report["new_capability_scope_registered"] is True
    assert report["new_capability_token_authority"] is False
    assert report["parent_fastapi_constructor_count"] == 10
    assert report["fastapi_constructor_count"] == 9
    assert report["retired_constructor_count"] == 1
    assert report["observed_launcher_count"] == 6
    assert report["canonical_redirect_count"] == 6
    assert "PASS170_PUBLIC_AUDIO_CAPABILITY_BINDING_PENDING" not in report["target_blockers"]


def test_audio_admission_requires_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(audio.CAPABILITY_SECRET_ENV, raising=False)
    with pytest.raises(HTTPException) as excinfo:
        audio.enforce_audio_public_admission(
            f"{audio.AUTHORIZATION_SCHEME} {_token(AUDIO_SCOPE)}"
        )
    assert excinfo.value.status_code == 503
    assert excinfo.value.detail == "HHS_PASS170_AUDIO_CAPABILITY_SECRET_REQUIRED"


def test_audio_admission_denies_missing_and_wrong_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(audio.CAPABILITY_SECRET_ENV, SECRET)
    with pytest.raises(HTTPException) as missing:
        audio.enforce_audio_public_admission(None)
    assert missing.value.status_code == 401
    assert missing.value.detail == "HHS_PASS170_AUDIO_CAPABILITY_REQUIRED"

    with pytest.raises(HTTPException) as wrong:
        audio.enforce_audio_public_admission(
            f"{audio.AUTHORIZATION_SCHEME} {_token('pass170.other')}"
        )
    assert wrong.value.status_code == 403
    assert wrong.value.detail == "HHS_PASS170_AUDIO_CAPABILITY_SCOPE_REQUIRED"


def test_audio_admission_accepts_inherited_signed_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(audio.CAPABILITY_SECRET_ENV, SECRET)
    admission = audio.enforce_audio_public_admission(
        f"{audio.AUTHORIZATION_SCHEME} {_token(AUDIO_SCOPE)}"
    )
    assert admission["required_scope"] == AUDIO_SCOPE
    assert AUDIO_SCOPE in admission["authorized_scopes"]
    assert admission["new_token_authority"] is False
    assert admission["pass190_verifier_reused"] is True
    assert isinstance(admission["token_hash72"], str)
    assert len(admission["token_hash72"]) == 72


def test_public_audio_routes_fail_closed_then_execute_when_authorized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(monkeypatch)

    rejected = client.post(audio.CANONICAL_PATH, json=_body())
    assert rejected.status_code == 401
    assert rejected.json()["detail"] == "HHS_PASS170_AUDIO_CAPABILITY_REQUIRED"

    wrong = client.post(
        audio.CANONICAL_PATH,
        json=_body(),
        headers={"Authorization": f"{audio.AUTHORIZATION_SCHEME} {_token('pass170.other')}"},
    )
    assert wrong.status_code == 403

    authorized = client.post(
        audio.CANONICAL_PATH,
        json=_body(),
        headers={"Authorization": f"{audio.AUTHORIZATION_SCHEME} {_token(AUDIO_SCOPE)}"},
    )
    assert authorized.status_code == 200
    payload = authorized.json()
    assert payload["ok"] is True
    assert payload["capability_admission"]["required_scope"] == AUDIO_SCOPE
    assert payload["capability_admission"]["new_token_authority"] is False

    legacy = client.post(
        audio.LEGACY_ALIAS_PATH,
        json=_body(),
        headers={"Authorization": f"{audio.AUTHORIZATION_SCHEME} {_token(AUDIO_SCOPE)}"},
    )
    assert legacy.status_code == 200


def test_internal_audio_adapter_remains_governed_without_public_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio,
        "run_audio_language_feedback_cycle",
        lambda **_kwargs: _FakeReceipt(),
    )
    request = audio.AudioLanguageRunRequest(**_body())
    payload = asyncio.run(audio.execute_audio_language_feedback_request(request))
    assert payload["ok"] is True
    assert "capability_admission" not in payload
    assert payload["vm81_commit_required"] is False


def test_heroku_constructor_is_retired_to_canonical_alias() -> None:
    source = (ROOT / "hhs_backend/heroku_server.py").read_text(encoding="utf-8")
    assert "FastAPI(" not in source
    assert "from fastapi import FastAPI" not in source
    assert "from hhs_backend.public_api_server import app" in source
    assert 'CANONICAL_TARGET = "hhs_backend.public_api_server:app"' in source
