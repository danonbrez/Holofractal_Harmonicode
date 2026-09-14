from __future__ import annotations

import json
from pathlib import Path

import hhs_runtime.pass219.pass170_audio_route_migration_i175 as i175


ROOT = Path(__file__).resolve().parents[2]


def test_i175_repository_state_verifies_exact_nonterminal_boundary() -> None:
    report = i175.verify_i175_audio_route_migration(ROOT)
    assert report["evidence_verified"] is True
    assert report["successor_operation_record_count"] == 48
    assert report["audio_operation_id"] == "public.audio_language.feedback.run"
    assert report["audio_canonical_route"] == "/v1/audio-language/run"
    assert report["audio_ecc_role_verified"] is True
    assert report["audio_internal_pq_security_role_verified"] is True
    assert report["public_crypto_authority_created"] is False
    assert report["observed_launcher_count"] == 6
    assert report["canonical_redirect_count"] == 5
    assert report["pending_launcher_paths"] == ["hhs_backend/server.py"]
    assert report["fastapi_constructor_count_preserved"] == 10
    assert report["target_blockers"] == list(i175.EXPECTED_TARGET_BLOCKERS)
    assert report["pass170_terminal_contract_verified"] is False
    assert report["next_boundary"] == i175.NEXT_BOUNDARY


def test_audio_security_profile_keeps_pq_role_internal_and_redundant() -> None:
    profile = json.loads((ROOT / i175.SECURITY_PROFILE).read_text(encoding="utf-8"))
    ecc = profile["error_correction"]
    pq = profile["post_quantum_security"]
    assert ecc["required_when_temporal"] is True
    assert ecc["invalid_witness_must_fail_closed"] is True
    assert pq["boundary"] == "INTERNAL_KERNEL_AND_INTEGRATED_RUNTIME_ONLY"
    assert pq["audio_witness_is_redundant_constraint_input"] is True
    assert pq["public_independent_crypto_operation"] is False
    assert pq["public_key_or_kem_authority"] is False
    assert pq["standardized_post_quantum_security_claim"] is False


def test_audio_operation_record_preserves_local_and_cross_cutting_roles() -> None:
    shard = json.loads((ROOT / i175.EXTENSION).read_text(encoding="utf-8"))
    record = shard["records"][0]
    assert record["operation_id"] == "public.audio_language.feedback.run"
    assert record["VM81_commit_required"] is False
    assert record["auxiliary_persistence"] is True
    assert record["canonical_vm81_mutation"] is False
    assert "LOCAL_AUDIO_LANGUAGE_APPLICATION" in record["cross_cutting_roles"]
    assert "HARMONIC_TIME_AUDIO_ERROR_CORRECTION_WITNESS_SOURCE" in record["cross_cutting_roles"]
    assert "INTERNAL_POST_QUANTUM_ORIENTED_SECURITY_ENFORCEMENT_SIGNAL" in record["cross_cutting_roles"]


def test_weakened_audio_security_profile_fails_closed(tmp_path: Path, monkeypatch) -> None:
    profile = json.loads((ROOT / i175.SECURITY_PROFILE).read_text(encoding="utf-8"))
    profile["post_quantum_security"]["public_independent_crypto_operation"] = True
    bad_profile = tmp_path / "bad_audio_security_profile.json"
    bad_profile.write_text(json.dumps(profile), encoding="utf-8")
    monkeypatch.setattr(i175, "SECURITY_PROFILE", str(bad_profile))
    report = i175.verify_i175_audio_route_migration(ROOT, fail_closed=False)
    assert report["evidence_verified"] is False
    assert "PASS170_I175_PQ_PUBLIC_BOUNDARY_INVALID:public_independent_crypto_operation" in report["evidence_blockers"]


def test_plus_v1_is_compatibility_shim_not_route_owner() -> None:
    source = (ROOT / "hhs_runtime_api_server_plus_v1.py").read_text(encoding="utf-8")
    assert "from hhs_backend.public_api_server import app" in source
    assert '"hhs_backend.public_api_server:app"' in source
    assert "@app.post" not in source
    assert "@app.get" not in source
    assert "@app.websocket" not in source
