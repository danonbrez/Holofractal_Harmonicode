from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_source_closure_i32 import (
    PASS218_I32_CLOSE_PATH,
    PASS218_I32_STATUS_PATH,
    install_pass218_i32_source_closure_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSED_STATUS,
    PASS218_I32_CLOSURE_SCOPE,
    Pass218I32ClosureRequest,
    Pass218I32ClosureStateError,
    Pass218I32ClosureValidationError,
    Pass218I32SourceCloser,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGE_RECEIPT_SCHEMA,
    PASS218_I31_PURGE_SCOPE,
    PASS218_I31_PURGE_VERSION,
    PASS218_I31_PURGED_STATUS,
    Pass218I31PurgeStore,
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


class _I31Control:
    def __init__(self, store_root: Path) -> None:
        self.store_root = store_root


def _h72(label: str, payload: object) -> str:
    return hash72_digest({"domain": "HHS-P218-I32-TEST-" + label}, payload)


def _make_i31_success(root: Path) -> dict[str, object]:
    promotion_receipt_hash72 = _h72("I30-PROMOTION-RECEIPT", {"source": 32})
    promotion_hash72 = _h72("I30-PROMOTION", {"source": 32})
    i29_validation_hash72 = _h72("I29-VALIDATION", {"source": 32})
    validated_hash216 = (
        _h72("VALIDATED-A", {"source": 32})
        + _h72("VALIDATED-B", {"source": 32})
        + _h72("VALIDATED-C", {"source": 32})
    )
    promoted_object_hash72 = _h72("PROMOTED-OBJECT", {"source": 32})
    canonical_root_hash72 = _h72("CANONICAL-ROOT", {"source": 32})
    candidate_sha256 = sha256(b"pass218-i32-candidate").hexdigest()
    durability_witness_hash72 = _h72("DURABILITY", {"source": 32})
    persisted_inventory_hash72 = _h72("INVENTORY", {"source": 32})
    purge_validation_hash72 = _h72(
        "PURGE-VALIDATION",
        {
            "promotion_receipt": promotion_receipt_hash72,
            "promoted": promoted_object_hash72,
            "durability": durability_witness_hash72,
        },
    )
    receipt_body = {
        "schema": PASS218_I31_PURGE_RECEIPT_SCHEMA,
        "version": PASS218_I31_PURGE_VERSION,
        "purge_scope": PASS218_I31_PURGE_SCOPE,
        "purge_status": PASS218_I31_PURGED_STATUS,
        "i30_promotion_receipt_hash72": promotion_receipt_hash72,
        "i30_promotion_hash72": promotion_hash72,
        "i29_validation_hash72": i29_validation_hash72,
        "validated_hash216": validated_hash216,
        "promoted_object_hash72": promoted_object_hash72,
        "canonical_root_hash72": canonical_root_hash72,
        "candidate_sha256": candidate_sha256,
        "durability_witness_hash72": durability_witness_hash72,
        "persisted_inventory_hash72": persisted_inventory_hash72,
        "purge_validation_hash72": purge_validation_hash72,
        "purge_mode": "MANAGED_BUFFER_ABSENCE_PROOF",
        "managed_buffer_count_before": 0,
        "managed_buffer_count_after": 0,
        "managed_buffers_absent_before": True,
        "managed_buffers_absent_after": True,
        "managed_buffer_zeroization_performed": False,
        "managed_buffer_witnesses": [],
        "durable_nonverbatim_store_verified": True,
        "verbatim_purge_invoked": True,
        "purge_confirmation_verified": True,
        "purge_receipt_issued": True,
        "quarantined": False,
        "curriculum_advance_permitted": False,
        "closure_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "physical_memory_erasure_claimed": False,
        "external_source_storage_erasure_claimed": False,
        "authoritative_float_weights_created": False,
    }
    purge_receipt_hash72 = hash72_digest(
        {"domain": "HHS-P218-I31-VERBATIM-PURGE-RECEIPT-V1"}, receipt_body
    )
    purge_hash216 = promotion_hash72 + purge_validation_hash72 + purge_receipt_hash72
    purge_gate_root_hash72 = hash72_digest(
        {"domain": "HHS-P218-I31-PURGE-GATE-ROOT-V1"},
        {
            "canonical_root_hash72": canonical_root_hash72,
            "promoted_object_hash72": promoted_object_hash72,
            "purge_validation_hash72": purge_validation_hash72,
            "purge_receipt_hash72": purge_receipt_hash72,
            "purge_hash216": purge_hash216,
        },
    )
    receipt = {
        **receipt_body,
        "purge_receipt_hash72": purge_receipt_hash72,
        "purge_hash216": purge_hash216,
        "purge_hash216_semantics": [
            "I30_ATOMIC_PROMOTION",
            "I31_PURGE_VALIDATION",
            "I31_PURGE_RECEIPT",
        ],
        "purge_gate_root_hash72": purge_gate_root_hash72,
    }
    Pass218I31PurgeStore(root).commit_success(receipt)
    return receipt


def _request(receipt: dict[str, object], *, previous: str | None = None) -> Pass218I32ClosureRequest:
    source_sha256 = sha256(b"pass218-i32-source").hexdigest()
    curriculum_identity_hash72 = _h72("CURRICULUM", {"source": source_sha256})
    return Pass218I32ClosureRequest(
        expected_i31_purge_receipt_hash72=str(receipt["purge_receipt_hash72"]),
        expected_i31_purge_validation_hash72=str(receipt["purge_validation_hash72"]),
        expected_i31_purge_gate_root_hash72=str(receipt["purge_gate_root_hash72"]),
        expected_i31_purge_hash216=str(receipt["purge_hash216"]),
        expected_i30_promotion_receipt_hash72=str(
            receipt["i30_promotion_receipt_hash72"]
        ),
        expected_promoted_object_hash72=str(receipt["promoted_object_hash72"]),
        expected_canonical_root_hash72=str(receipt["canonical_root_hash72"]),
        source_id="repository-native-i32-source",
        source_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=32,
        source_stage=2,
        previous_closure_hash72=previous,
        closure_scope=PASS218_I32_CLOSURE_SCOPE,
    ).validated()


def _closer(tmp_path: Path, *, ready: bool = True):
    i31_root = tmp_path / "i31"
    receipt = _make_i31_success(i31_root)
    lifecycle = _Lifecycle(ready)
    closer = Pass218I32SourceCloser(
        lifecycle=lifecycle,
        i31_store_root=i31_root,
        closure_store_root=tmp_path / "i32",
    )
    return closer, lifecycle, receipt


def test_i32_closes_exact_i31_receipt_without_advancing_curriculum(tmp_path: Path) -> None:
    closer, lifecycle, purge = _closer(tmp_path)
    request = _request(purge)
    first = closer.close(request)
    replay = closer.close(request)

    assert first == replay
    assert first["closure_status"] == PASS218_I32_CLOSED_STATUS
    assert first["closure_invoked"] is True
    assert first["source_closed"] is True
    assert first["purge_confirmation_verified"] is True
    assert first["durable_nonverbatim_store_verified"] is True
    assert first["source_binding_requires_curriculum_match_before_advance"] is True
    assert first["curriculum_advance_permitted"] is False
    assert first["curriculum_cursor_advanced"] is False
    assert first["stage_advance_permitted"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["physical_memory_erasure_claimed"] is False
    assert first["authoritative_float_weights_created"] is False
    assert validate_hash72(first["source_closure_hash72"])
    assert validate_hash72(first["closure_validation_hash72"])
    assert validate_hash72(first["closure_chain_root_hash72"])
    assert len(first["closure_hash216"]) == 216
    assert lifecycle.require_count == 2

    restarted = Pass218I32SourceCloser(
        lifecycle=lifecycle,
        i31_store_root=tmp_path / "i31",
        closure_store_root=tmp_path / "i32",
    )
    assert restarted.close(request) == first
    status = restarted.status()
    assert status["source_closed"] is True
    assert status["curriculum_advance_permitted"] is False


def test_i32_binds_previous_closure_without_advancing_cursor(tmp_path: Path) -> None:
    closer, _, purge = _closer(tmp_path)
    previous = _h72("PREVIOUS-CLOSURE", {"ordinal": 31})
    result = closer.close(_request(purge, previous=previous))
    assert result["previous_closure_hash72"] == previous
    assert result["curriculum_cursor_advanced"] is False
    assert result["closure_hash216"].startswith(str(purge["purge_receipt_hash72"]))


def test_i32_rejects_i31_identity_mismatch_without_fabricating_closure(tmp_path: Path) -> None:
    closer, _, purge = _closer(tmp_path)
    request = _request(purge)
    wrong = Pass218I32ClosureRequest(
        **{
            **request.__dict__,
            "expected_i31_purge_gate_root_hash72": _h72("WRONG-GATE", {"source": 32}),
        }
    )
    with pytest.raises(Pass218I32ClosureValidationError, match="P218_I32_I31_IDENTITY_MISMATCH"):
        closer.close(wrong)
    assert closer.store.active_record() is None
    assert closer.status()["curriculum_advance_permitted"] is False


def test_i32_requires_successful_i31_purge_before_closure(tmp_path: Path) -> None:
    lifecycle = _Lifecycle(True)
    closer = Pass218I32SourceCloser(
        lifecycle=lifecycle,
        i31_store_root=tmp_path / "empty-i31",
        closure_store_root=tmp_path / "i32",
    )
    fake = {
        "purge_receipt_hash72": _h72("FAKE-PURGE-RECEIPT", {}),
        "purge_validation_hash72": _h72("FAKE-PURGE-VALIDATION", {}),
        "purge_gate_root_hash72": _h72("FAKE-PURGE-GATE", {}),
        "purge_hash216": _h72("FAKE-A", {}) + _h72("FAKE-B", {}) + _h72("FAKE-C", {}),
        "i30_promotion_receipt_hash72": _h72("FAKE-I30", {}),
        "promoted_object_hash72": _h72("FAKE-OBJECT", {}),
        "canonical_root_hash72": _h72("FAKE-ROOT", {}),
    }
    with pytest.raises(Pass218I32ClosureValidationError, match="P218_I32_I31_PURGE_RECEIPT_REQUIRED"):
        closer.close(_request(fake))
    assert closer.store.active_record() is None


def test_i32_writer_fence_required(tmp_path: Path) -> None:
    closer, lifecycle, purge = _closer(tmp_path, ready=False)
    with pytest.raises(RuntimeError, match="P218_TEST_WRITER_FENCE_CLOSED"):
        closer.close(_request(purge))
    assert lifecycle.require_count == 1
    assert closer.store.active_record() is None


def test_i32_runtime_os_exposes_close_only_not_curriculum_advance(tmp_path: Path) -> None:
    i31_root = tmp_path / "i31"
    purge = _make_i31_success(i31_root)
    app = FastAPI()
    lifecycle = _Lifecycle(True)
    control = install_pass218_i32_source_closure_control(
        app,
        _I31Control(i31_root),
        lifecycle,
        state_root=tmp_path,
    )
    client = TestClient(app)

    status = client.get(PASS218_I32_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["curriculum_advance_permitted"] is False

    request = _request(purge)
    payload = {"closure_binding": request.__dict__}
    closed = client.post(PASS218_I32_CLOSE_PATH, json=payload)
    assert closed.status_code == 200
    assert closed.json()["closure_status"] == PASS218_I32_CLOSED_STATUS
    assert control.status()["source_closed"] is True

    paths = {str(route.path) for route in app.routes}
    assert PASS218_I32_STATUS_PATH in paths
    assert PASS218_I32_CLOSE_PATH in paths
    assert not any("curriculum" in path and "advance" in path for path in paths)
    assert not any("source-text" in path or "buffer" in path for path in paths)


def test_i32_conflicting_second_closure_is_rejected(tmp_path: Path) -> None:
    closer, _, purge = _closer(tmp_path)
    first = closer.close(_request(purge))
    request = _request(purge)
    conflict = Pass218I32ClosureRequest(
        **{
            **request.__dict__,
            "source_sha256": sha256(b"different-source").hexdigest(),
        }
    )
    with pytest.raises(Pass218I32ClosureStateError, match="P218_I32_PREVIOUS_SOURCE_CLOSURE_CONFLICT"):
        closer.close(conflict)
    assert closer.store.active_record() == first
