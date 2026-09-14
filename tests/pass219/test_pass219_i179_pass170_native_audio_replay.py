from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys

import pytest
from fastapi import HTTPException

import hhs_backend.pass170_audio_language_routes as audio
from hhs_runtime.pass190.completion import PASS190_NATIVE_PYTHON
from hhs_runtime.pass219 import pass170_audio_native_abi_i179 as native
from hhs_runtime.pass219 import pass170_audio_transport_i178 as transport

if str(PASS190_NATIVE_PYTHON) not in sys.path:
    sys.path.insert(0, str(PASS190_NATIVE_PYTHON))
from hhs_pass190_capability import issue_capability_token  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SECRET = "pass170-i179-native-audio-secret-" + ("x" * 40)


def _token(*scopes: str) -> str:
    return issue_capability_token(
        SECRET,
        principal="pass219-i179-test",
        scopes=scopes,
        ttl_seconds=900,
        nonce="pass219-i179-fixed-test-nonce",
    )


def _authorization(*scopes: str) -> str:
    return f"{audio.AUTHORIZATION_SCHEME} {_token(*scopes)}"


def _body() -> dict[str, object]:
    return {
        "expression": "xy=-1/yx",
        "items": [
            {
                "id": "0",
                "text": "xy",
                "kind": "ORDERED_PRODUCT",
                "phaseIndex": 0,
            }
        ],
        "audio_manifest": {
            "schema": "HHS_I179_TEST_AUDIO_MANIFEST",
            "manifest_hash72": "I179-AUDIO-MANIFEST",
            "items": [],
            "temporal": {
                "sample_index": 179971,
                "sample_rate": "48000/1",
                "frame_window_samples": 144,
                "latency_ticks": 72,
                "phase_modulus": 72,
            },
        },
        "audio_roundtrip_receipt": None,
    }


def _configure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    db = tmp_path / "audio-language-i179.sqlite3"
    monkeypatch.setenv(audio.CAPABILITY_SECRET_ENV, SECRET)
    monkeypatch.setenv(audio.SEMANTIC_DB_ENV, str(db))
    library = ROOT / "hhs_runtime/builds/libhhs_runtime.so"
    assert library.is_file(), "I179 tests require the workflow-built exact runtime"
    monkeypatch.setenv(native.LIBRARY_ENV, str(library))
    return db


def test_i179_native_admission_binds_ecc_raw5184_and_security(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _configure(monkeypatch, tmp_path)
    admission = audio.enforce_audio_public_admission(
        _authorization(audio.AUDIO_CAPABILITY_SCOPE)
    )
    report = native.admit_audio_native_transport(admission, _body())
    assert report["harmonic_time_audio_ecc_valid"] is True
    assert report["raw5184_audio_hydration_bound"] is True
    assert report["internal_pq_oriented_signal"] is True
    assert report["internal_pq_oriented_signal_public_crypto"] is False
    assert report["receipt_replay_binding_required"] is True
    assert len(report["binding_hash72"]) == 72
    assert report["native"]["admitted"] is True
    assert report["native"]["public_crypto_primitive"] is False
    assert report["native"]["standardized_pq_crypto_claim"] is False
    assert report["native"]["independent_key_or_kem_authority"] is False
    assert report["native"]["canonical_vm81_mutation_authority"] is False
    assert report["native"]["new_hash72_mint_authority"] is False
    assert report["native"]["hash216_persistence_authority"] is False


def test_i179_real_audio_run_and_non_reexecuting_replay(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db = _configure(monkeypatch, tmp_path)
    authorization = _authorization(audio.AUDIO_CAPABILITY_SCOPE)

    invoked = transport.invoke_audio_language_python(
        _body(),
        authorization=authorization,
    )
    assert db.is_file()
    assert invoked["operation_id"] == transport.OPERATION_ID
    assert invoked["transport"]["native_abi_invoked"] is True
    assert invoked["native_security_binding"]["native"]["admitted"] is True
    assert invoked["vm81_commit_required"] is False
    receipt_hash72 = str(invoked["receipt_hash72"])
    assert receipt_hash72

    replay = transport.replay_audio_language_python(
        receipt_hash72,
        authorization=authorization,
    )
    assert replay["receipt_hash72"] == receipt_hash72
    assert replay["receipt"]["receipt_hash72"] == receipt_hash72
    assert replay["integrity"]["receipt_hash_verified"] is True
    assert replay["integrity"]["stored_states_verified"] is True
    assert replay["integrity"]["transition_trace_verified"] is True
    assert replay["integrity"]["cross_links_verified"] is True
    assert replay["reexecuted"] is False
    assert replay["training_reexecuted"] is False
    assert replay["auxiliary_persistence_mutated"] is False
    assert replay["canonical_vm81_mutated"] is False
    assert replay["native_replay_binding"]["reexecuted"] is False
    assert replay["native_replay_binding"]["native"]["admitted"] is True
    assert replay["transport"]["native_replay_abi_invoked"] is True


def test_i179_replay_detects_tampered_stored_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db = _configure(monkeypatch, tmp_path)
    authorization = _authorization(audio.AUDIO_CAPABILITY_SCOPE)
    invoked = transport.invoke_audio_language_python(_body(), authorization=authorization)
    receipt_hash72 = str(invoked["receipt_hash72"])

    conn = sqlite3.connect(db)
    try:
        row = conn.execute(
            "SELECT receipt_json FROM audio_language_feedback_receipts_i179 WHERE receipt_hash72 = ?",
            (receipt_hash72,),
        ).fetchone()
        assert row is not None
        payload = json.loads(row[0])
        payload["semantic_db_summary"] = {"tampered": True}
        conn.execute(
            "UPDATE audio_language_feedback_receipts_i179 SET receipt_json = ? WHERE receipt_hash72 = ?",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")), receipt_hash72),
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(HTTPException) as exc_info:
        transport.replay_audio_language_python(
            receipt_hash72,
            authorization=authorization,
        )
    assert exc_info.value.status_code == 409
    assert "HHS_AUDIO_LANGUAGE_REPLAY_HASH_MISMATCH" in str(exc_info.value.detail)


def test_i179_wrong_scope_rejected_before_native_operation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db = _configure(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc_info:
        transport.invoke_audio_language_python(
            _body(),
            authorization=_authorization("pass170.other"),
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "HHS_PASS170_AUDIO_CAPABILITY_SCOPE_REQUIRED"
    assert not db.exists()


def test_i179_missing_native_library_fails_before_auxiliary_persistence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db = tmp_path / "must-not-exist.sqlite3"
    monkeypatch.setenv(audio.CAPABILITY_SECRET_ENV, SECRET)
    monkeypatch.setenv(audio.SEMANTIC_DB_ENV, str(db))
    monkeypatch.setenv(native.LIBRARY_ENV, str(tmp_path / "missing-libhhs_runtime.so"))

    with pytest.raises(HTTPException) as exc_info:
        transport.invoke_audio_language_python(
            _body(),
            authorization=_authorization(audio.AUDIO_CAPABILITY_SCOPE),
        )
    assert exc_info.value.status_code == 503
    assert "HHS_PASS170_AUDIO_NATIVE_ABI_REQUIRED" in str(exc_info.value.detail)
    assert not db.exists()


def test_i179_native_surface_is_additive_and_forbidden_authorities_absent() -> None:
    header = (ROOT / "hhs_runtime/include/hhs_pass219_audio_security_transport_1_0.h").read_text(encoding="utf-8")
    source = (ROOT / "hhs_runtime/c/hhs_pass219_audio_security_transport_1_0.inc").read_text(encoding="utf-8")
    aggregate_h = (ROOT / "hhs_runtime/include/hhs_runtime_exact_abi.h").read_text(encoding="utf-8")
    aggregate_c = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text(encoding="utf-8")
    assert "hhs_exact_pass219_audio_security_transport_admit" in header
    assert "hhs_pass219_audio_security_transport_1_0.h" in aggregate_h
    assert "hhs_pass219_audio_security_transport_1_0.inc" in aggregate_c
    assert "public_crypto_primitive != 0U" in source
    assert "canonical_vm81_mutation_authority != 0U" in source
    assert "new_hash72_mint_authority != 0U" in source
    assert "hash216_persistence_authority != 0U" in source
