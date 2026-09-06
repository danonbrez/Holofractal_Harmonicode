from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import hhs_backend.pass170_audio_language_routes as audio
from hhs_runtime.pass190.completion import PASS190_NATIVE_PYTHON
from hhs_runtime.pass219 import pass170_audio_transport_i178 as transport
from hhs_runtime.pass219.pass170_constructor_transport_i178 import (
    verify_i178_constructor_transport,
)

if str(PASS190_NATIVE_PYTHON) not in sys.path:
    sys.path.insert(0, str(PASS190_NATIVE_PYTHON))
from hhs_pass190_capability import issue_capability_token  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SECRET = "pass170-i178-audio-transport-secret-" + ("x" * 40)


def _token(*scopes: str) -> str:
    return issue_capability_token(
        SECRET,
        principal="pass219-i178-test",
        scopes=scopes,
        ttl_seconds=900,
        nonce="pass219-i178-fixed-test-nonce",
    )


def _authorization(*scopes: str) -> str:
    return f"{audio.AUTHORIZATION_SCHEME} {_token(*scopes)}"


def _body() -> dict[str, object]:
    return {
        "expression": "x+y",
        "items": [],
        "audio_manifest": {"schema": "HHS_I178_TEST_AUDIO_MANIFEST"},
        "audio_roundtrip_receipt": None,
    }


class _FakeReceipt:
    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "HHS_I178_FAKE_AUDIO_RECEIPT",
            "ok": True,
            "deterministic_value": "i178-parity",
        }


def _patch_audio(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(audio.CAPABILITY_SECRET_ENV, SECRET)
    monkeypatch.setattr(
        audio,
        "run_audio_language_feedback_cycle",
        lambda **_kwargs: _FakeReceipt(),
    )


def test_i178_repository_gate() -> None:
    report = verify_i178_constructor_transport(ROOT)
    assert report["evidence_verified"] is True
    assert report["parent_i177_exact_main_verified"] is True
    assert report["parent_fastapi_constructor_count"] == 9
    assert report["fastapi_constructor_count"] == 8
    assert report["newly_retired_constructor_count"] == 1
    assert report["cumulative_retired_constructor_count"] == 2
    assert report["retired_constructor_path"] == "hhs_runtime/main.py"
    assert report["observed_launcher_count"] == 6
    assert report["canonical_redirect_count"] == 6
    assert report["audio_http_transport_verified"] is True
    assert report["audio_cli_transport_verified"] is True
    assert report["audio_python_transport_verified"] is True
    assert report["audio_native_abi_verified"] is False
    assert report["shared_signed_admission_preserved"] is True
    assert report["audio_internal_ecc_pq_boundary_preserved"] is True
    assert report["new_capability_token_authority"] is False
    assert "PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING" not in report["target_blockers"]
    assert "PASS170_PUBLIC_NATIVE_ABI_PARITY_PENDING" in report["target_blockers"]


def test_python_transport_executes_shared_governed_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_audio(monkeypatch)
    result = transport.invoke_audio_language_python(
        _body(),
        authorization=_authorization(audio.AUDIO_CAPABILITY_SCOPE),
    )
    assert result["ok"] is True
    assert result["deterministic_value"] == "i178-parity"
    assert result["operation_id"] == transport.OPERATION_ID
    assert result["capability_admission"]["required_scope"] == audio.AUDIO_CAPABILITY_SCOPE
    assert result["capability_admission"]["new_token_authority"] is False
    assert result["transport"]["surface"] == "python"
    assert result["transport"]["shared_admission_gate"] is True
    assert result["transport"]["shared_internal_adapter"] is True
    assert result["transport"]["native_abi_invoked"] is False


def test_cli_transport_executes_same_operation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_audio(monkeypatch)
    monkeypatch.setenv(
        transport.CLI_AUTHORIZATION_ENV,
        _authorization(audio.AUDIO_CAPABILITY_SCOPE),
    )
    code = transport.main([
        "invoke",
        "--payload-json",
        json.dumps(_body(), sort_keys=True),
    ])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["deterministic_value"] == "i178-parity"
    assert payload["operation_id"] == transport.OPERATION_ID
    assert payload["capability_admission"]["required_scope"] == audio.AUDIO_CAPABILITY_SCOPE
    assert payload["transport"]["surface"] == "cli"
    assert payload["transport"]["python_binding_reused"] == transport.PYTHON_BINDING


def test_cli_transport_fails_closed_without_capability(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_audio(monkeypatch)
    monkeypatch.delenv(transport.CLI_AUTHORIZATION_ENV, raising=False)
    code = transport.main([
        "invoke",
        "--payload-json",
        json.dumps(_body(), sort_keys=True),
    ])
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["http_status"] == 401
    assert payload["detail"] == "HHS_PASS170_AUDIO_CAPABILITY_REQUIRED"
    assert payload["canonical_state_mutated"] is False


def test_http_python_transport_core_result_parity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_audio(monkeypatch)
    authorization = _authorization(audio.AUDIO_CAPABILITY_SCOPE)

    app = FastAPI()
    app.include_router(audio.build_pass170_audio_language_router())
    client = TestClient(app)
    http_result = client.post(
        audio.CANONICAL_PATH,
        json=_body(),
        headers={"Authorization": authorization},
    )
    assert http_result.status_code == 200

    python_result = transport.invoke_audio_language_python(
        _body(),
        authorization=authorization,
    )
    http_payload = http_result.json()
    for key in (
        "schema",
        "ok",
        "deterministic_value",
        "operation_id",
        "canonical_path",
        "compatibility_alias",
        "vm81_commit_required",
        "auxiliary_persistence",
    ):
        assert http_payload[key] == python_result[key]
    assert http_payload["capability_admission"]["required_scope"] == python_result["capability_admission"]["required_scope"]


def test_runtime_main_constructor_retired_but_launcher_preserved() -> None:
    source = (ROOT / "hhs_runtime/main.py").read_text(encoding="utf-8")
    assert "FastAPI(" not in source
    assert "from fastapi import FastAPI" not in source
    assert "from hhs_backend.public_api_server import app" in source
    assert 'uvicorn.run(\n        "hhs_backend.public_api_server:app"' in source
    assert 'CANONICAL_TARGET = "hhs_backend.public_api_server:app"' in source


def test_transport_record_does_not_claim_native_or_public_crypto() -> None:
    record_path = ROOT / "contracts/pass219/pass170_operation_records_i178/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_TRANSPORT_V1.json"
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    record = payload["records"][0]
    assert record["native_ABI_symbol"] is None
    assert record["transport_parity_status"] == "HTTP_CLI_PYTHON_EXECUTABLE_NATIVE_ABI_PENDING"
    assert record["transport_invariants"]["native_abi_claimed"] is False
    assert record["transport_invariants"]["parallel_operation_engine_created"] is False
    assert record["security_boundary"]["internal_audio_ecc_exposed_by_public_transport"] is False
    assert record["security_boundary"]["internal_pq_oriented_signal_exposed_by_public_transport"] is False
    assert record["security_boundary"]["public_crypto_primitive"] is False
    assert record["security_boundary"]["standardized_pq_crypto_claim"] is False
