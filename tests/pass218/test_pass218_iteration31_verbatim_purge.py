from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_verbatim_purge_i31 import (
    PASS218_I31_PURGE_PATH,
    PASS218_I31_STATUS_PATH,
    install_pass218_i31_verbatim_purge_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PENDING_PURGE_STATUS,
    PASS218_I30_PROMOTED_OBJECT_SCHEMA,
    PASS218_I30_PROMOTION_VERSION,
    Pass218I30AtomicSemanticStore,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGED_STATUS,
    PASS218_I31_QUARANTINED_STATUS,
    PASS218_I31_PURGE_SCOPE,
    Pass218I31ManagedBufferRegistry,
    Pass218I31PurgeConfirmationError,
    Pass218I31PurgeRequest,
    Pass218I31PurgeStateError,
    Pass218I31PurgeValidationError,
    Pass218I31VerbatimPurger,
)


class _Lifecycle:
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready
        self.require_count = 0

    def require_ingestion_ready(self) -> None:
        self.require_count += 1
        if not self.ready:
            raise RuntimeError("P218_TEST_WRITER_FENCE_CLOSED")

    def status(self) -> dict[str, object]:
        return {
            "ingestion_enabled": self.ready,
            "ownership_writer_authority": self.ready,
        }


class _I30Control:
    def __init__(self, store_root: Path) -> None:
        self.store_root = store_root


def _h72(label: str, payload: object) -> str:
    return hash72_digest({"domain": "HHS-P218-I31-TEST-" + label}, payload)


def _make_i30_store(root: Path) -> tuple[Pass218I30AtomicSemanticStore, dict[str, str]]:
    store = Pass218I30AtomicSemanticStore(root)
    i29_validation = _h72("I29-VALIDATION", {"candidate": 31})
    validated_hash216 = (
        _h72("VALIDATED-A", {"candidate": 31})
        + _h72("VALIDATED-B", {"candidate": 31})
        + _h72("VALIDATED-C", {"candidate": 31})
    )
    grant_hash72 = _h72("GRANT", {"candidate": 31})
    promoted_body = {
        "schema": PASS218_I30_PROMOTED_OBJECT_SCHEMA,
        "version": PASS218_I30_PROMOTION_VERSION,
        "i29_validation_hash72": i29_validation,
        "validated_hash216": validated_hash216,
        "semantic_payload": {
            "grounded_graph": {
                "relation_count": 1,
                "source_text_retained": False,
                "source_token_stream_retained": False,
            },
            "perspective_context": {
                "perspective_order_sequence": [1],
                "source_text_retained": False,
                "source_token_stream_retained": False,
            },
        },
        "retained_artifact_allowlist": [
            "checksums_and_identity_metadata",
            "typed_relational_graph",
            "vm5184_exact_state",
            "validation_and_lineage_receipts",
        ],
        "source_text_retained": False,
        "source_token_stream_retained": False,
        "verbatim_corpus_source_retained": False,
        "purge_status": "PENDING_VERBATIM_PURGE",
        "curriculum_advance_permitted": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "authoritative_float_weights_created": False,
    }
    promoted_object_hash72 = hash72_digest(
        {"domain": "HHS-P218-I30-PROMOTED-SEMANTIC-OBJECT-V1"},
        promoted_body,
    )
    promoted_object = {
        **promoted_body,
        "promoted_object_hash72": promoted_object_hash72,
    }
    target_before = store.empty_root_hash72()
    candidate = {
        "schema": "HHS-P218-I30-PROMOTION-CANDIDATE-COMMIT-V1",
        "version": PASS218_I30_PROMOTION_VERSION,
        "i29_validation_hash72": i29_validation,
        "validated_hash216": validated_hash216,
        "promoted_object_hash72": promoted_object_hash72,
        "promoted_object": promoted_object,
        "grant": {
            "grant_hash72": grant_hash72,
            "truth_promotion": False,
            "action_authority_minted": False,
            "learning_authority_granted": False,
        },
        "target_root_before_hash72": target_before,
        "formal_semantic_round_trip_verified": True,
        "grounded_round_trip_verified": True,
        "perspective_round_trip_verified": True,
        "vm5184_projection_rederived": True,
        "candidate_only": True,
        "atomic_promotion_invoked": False,
        "verbatim_corpus_source_retained": False,
    }
    candidate_filename, candidate_sha256 = store.commit_candidate(candidate)
    target_after = _h72(
        "TARGET-AFTER",
        {
            "target_before": target_before,
            "promoted_object_hash72": promoted_object_hash72,
            "candidate_sha256": candidate_sha256,
        },
    )
    root_verification_hash72 = _h72(
        "ROOT-VERIFY", {"target_after": target_after, "candidate": candidate_sha256}
    )
    promotion_hash72 = _h72(
        "PROMOTION", {"target_after": target_after, "grant": grant_hash72}
    )
    promotion_receipt_hash72 = _h72(
        "PROMOTION-RECEIPT",
        {"promotion_hash72": promotion_hash72, "promoted": promoted_object_hash72},
    )
    promotion_hash216 = (
        _h72("PROMOTION-COMMIT", {"candidate": candidate_sha256})
        + root_verification_hash72
        + promotion_receipt_hash72
    )
    receipt = store.atomic_promote(
        promoted_object=promoted_object,
        candidate_filename=candidate_filename,
        candidate_sha256=candidate_sha256,
        grant_hash72=grant_hash72,
        i29_validation_hash72=i29_validation,
        validated_hash216=validated_hash216,
        target_root_before_hash72=target_before,
        target_root_after_hash72=target_after,
        root_verification_hash72=root_verification_hash72,
        promotion_hash72=promotion_hash72,
        promotion_receipt_hash72=promotion_receipt_hash72,
        promotion_hash216=promotion_hash216,
    )
    assert receipt["promotion_status"] == PASS218_I30_PENDING_PURGE_STATUS
    return store, {
        "promotion_receipt_hash72": promotion_receipt_hash72,
        "promotion_hash72": promotion_hash72,
        "promoted_object_hash72": promoted_object_hash72,
        "canonical_root_hash72": target_after,
        "i29_validation_hash72": i29_validation,
    }


def _request(identity: dict[str, str]) -> Pass218I31PurgeRequest:
    return Pass218I31PurgeRequest(
        expected_i30_promotion_receipt_hash72=identity["promotion_receipt_hash72"],
        expected_i30_promotion_hash72=identity["promotion_hash72"],
        expected_promoted_object_hash72=identity["promoted_object_hash72"],
        expected_canonical_root_hash72=identity["canonical_root_hash72"],
        expected_i29_validation_hash72=identity["i29_validation_hash72"],
        purge_scope=PASS218_I31_PURGE_SCOPE,
    ).validated()


def _purger(tmp_path: Path, *, ready: bool = True):
    i30_root = tmp_path / "i30"
    _, identity = _make_i30_store(i30_root)
    lifecycle = _Lifecycle(ready)
    registry = Pass218I31ManagedBufferRegistry()
    purger = Pass218I31VerbatimPurger(
        lifecycle=lifecycle,
        i30_store_root=i30_root,
        purge_store_root=tmp_path / "i31",
        managed_buffers=registry,
    )
    return purger, registry, lifecycle, identity


def test_i31_absence_proof_receipts_exact_i30_promotion_without_advancing(tmp_path: Path) -> None:
    purger, _, lifecycle, identity = _purger(tmp_path)
    first = purger.purge(_request(identity))
    replay = purger.purge(_request(identity))

    assert first == replay
    assert first["purge_status"] == PASS218_I31_PURGED_STATUS
    assert first["purge_mode"] == "MANAGED_BUFFER_ABSENCE_PROOF"
    assert first["managed_buffer_count_before"] == 0
    assert first["managed_buffers_absent_before"] is True
    assert first["managed_buffers_absent_after"] is True
    assert first["managed_buffer_zeroization_performed"] is False
    assert first["durable_nonverbatim_store_verified"] is True
    assert first["verbatim_purge_invoked"] is True
    assert first["purge_confirmation_verified"] is True
    assert first["purge_receipt_issued"] is True
    assert validate_hash72(first["purge_receipt_hash72"])
    assert len(first["purge_hash216"]) == 216
    assert all(validate_hash72(first["purge_hash216"][start:start + 72]) for start in (0, 72, 144))
    assert first["purge_hash216"].startswith(identity["promotion_hash72"])
    assert first["curriculum_advance_permitted"] is False
    assert first["closure_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["physical_memory_erasure_claimed"] is False
    assert first["external_source_storage_erasure_claimed"] is False
    assert first["authoritative_float_weights_created"] is False
    assert lifecycle.require_count == 2

    status = purger.status()
    assert status["purge_receipt_issued"] is True
    assert status["purge_confirmation_verified"] is True
    assert status["quarantined"] is False
    assert status["curriculum_advance_permitted"] is False
    assert status["closure_invoked"] is False


def test_i31_zeroizes_and_clears_runtime_managed_buffer_without_retaining_source(tmp_path: Path) -> None:
    purger, registry, _, identity = _purger(tmp_path)
    raw = bytearray(b"ephemeral-source-material-for-i31-managed-buffer")
    source_sha256 = sha256(bytes(raw)).hexdigest()
    registry.register(
        "source-0",
        promotion_receipt_hash72=identity["promotion_receipt_hash72"],
        source_sha256=source_sha256,
        buffer=raw,
    )

    receipt = purger.purge(_request(identity))

    assert raw == bytearray()
    assert registry.count() == 0
    assert receipt["purge_mode"] == "MANAGED_BUFFER_ZEROIZE_AND_CLEAR"
    assert receipt["managed_buffer_count_before"] == 1
    assert receipt["managed_buffer_count_after"] == 0
    assert receipt["managed_buffer_zeroization_performed"] is True
    witness = receipt["managed_buffer_witnesses"][0]
    assert witness["source_sha256"] == source_sha256
    assert witness["managed_buffer_zeroized"] is True
    assert witness["managed_buffer_cleared"] is True
    assert witness["managed_buffer_length_after"] == 0
    serialized = json.dumps(receipt, sort_keys=True).encode("utf-8")
    assert b"ephemeral-source-material" not in serialized
    assert receipt["physical_memory_erasure_claimed"] is False


def test_i31_confirmation_failure_quarantines_and_never_issues_receipt(tmp_path: Path) -> None:
    purger, _, _, identity = _purger(tmp_path)

    with pytest.raises(Pass218I31PurgeConfirmationError, match="P218_I31_INJECTED_PURGE_CONFIRMATION_FAILURE"):
        purger.purge(_request(identity), force_confirmation_failure=True)

    status = purger.status()
    assert status["purge_status"] == PASS218_I31_QUARANTINED_STATUS
    assert status["quarantined"] is True
    assert status["purge_receipt_issued"] is False
    assert status["purge_confirmation_verified"] is False
    assert status["curriculum_advance_permitted"] is False
    assert status["closure_invoked"] is False

    with pytest.raises(Pass218I31PurgeStateError, match="P218_I31_QUARANTINED_REQUIRES_EXPLICIT_RECOVERY"):
        purger.purge(_request(identity))


def test_i31_caller_binding_mismatch_fails_without_false_quarantine(tmp_path: Path) -> None:
    purger, _, _, identity = _purger(tmp_path)
    wrong = dict(identity)
    wrong["promoted_object_hash72"] = _h72("WRONG-PROMOTED", {"candidate": 31})

    with pytest.raises(Pass218I31PurgeValidationError, match="P218_I31_EXPECTED_PROMOTED_OBJECT_MISMATCH"):
        purger.purge(_request(wrong))

    status = purger.status()
    assert status["purge_record_present"] is False
    assert status["purge_receipt_issued"] is False
    assert status["quarantined"] is False
    assert status["curriculum_advance_permitted"] is False


def test_i31_writer_fence_blocks_purge_before_any_receipt(tmp_path: Path) -> None:
    purger, _, _, identity = _purger(tmp_path, ready=False)

    with pytest.raises(RuntimeError, match="P218_TEST_WRITER_FENCE_CLOSED"):
        purger.purge(_request(identity))

    assert purger.store.status()["purge_record_present"] is False


def test_i31_runtimeos_surface_exposes_only_status_and_exact_bound_purge(tmp_path: Path) -> None:
    i30_root = tmp_path / "state" / "cognition" / "atomic-semantic-promotion-i30"
    _, identity = _make_i30_store(i30_root)
    lifecycle = _Lifecycle(True)
    app = FastAPI()
    install_pass218_i31_verbatim_purge_control(
        app,
        _I30Control(i30_root),
        lifecycle,
        state_root=tmp_path / "state",
    )
    client = TestClient(app)

    before = client.get(PASS218_I31_STATUS_PATH)
    assert before.status_code == 200
    assert before.json()["purge_receipt_issued"] is False

    payload = {
        "purge_binding": {
            "expected_i30_promotion_receipt_hash72": identity[
                "promotion_receipt_hash72"
            ],
            "expected_i30_promotion_hash72": identity["promotion_hash72"],
            "expected_promoted_object_hash72": identity["promoted_object_hash72"],
            "expected_canonical_root_hash72": identity["canonical_root_hash72"],
            "expected_i29_validation_hash72": identity["i29_validation_hash72"],
            "purge_scope": PASS218_I31_PURGE_SCOPE,
        }
    }
    response = client.post(PASS218_I31_PURGE_PATH, json=payload)
    assert response.status_code == 200
    assert response.json()["purge_receipt_issued"] is True
    assert response.json()["curriculum_advance_permitted"] is False

    paths = {str(route.path) for route in app.routes}
    assert PASS218_I31_STATUS_PATH in paths
    assert PASS218_I31_PURGE_PATH in paths
    assert not any("curriculum" in path for path in paths)
    assert not any("closure" in path for path in paths)
    assert not any("buffer" in path for path in paths)
