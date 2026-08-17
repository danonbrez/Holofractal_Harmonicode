from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_curriculum_advance_i33 import (
    PASS218_I33_ADVANCE_PATH,
    PASS218_I33_STATUS_PATH,
    install_pass218_i33_curriculum_advance_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import (
    PASS218_I33_ADVANCED_STATUS,
    PASS218_I33_STAGE_GATE_STATUS,
    Pass218I33CurriculumAdvancer,
    Pass218I33CurriculumAuthority,
    Pass218I33CurriculumBindingError,
)
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSURE_SCOPE,
    Pass218I32ClosureRequest,
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


class _I32Control:
    def __init__(self, store_root: Path) -> None:
        self.store_root = store_root


def _h72(label: str, payload: object) -> str:
    return hash72_digest({"domain": "HHS-P218-I33-TEST-" + label}, payload)


def _manifest(*, second_stage: CurriculumStage = CurriculumStage.EXPOSITORY):
    source_one = CurriculumSource(
        source_id="repository-native-i33-source-one",
        stage=CurriculumStage.EXPOSITORY,
        locator="001-source-one",
        checksum_sha256=sha256(b"pass218-i33-source-one").hexdigest(),
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        media_type="text/markdown",
    )
    source_two = CurriculumSource(
        source_id="repository-native-i33-source-two",
        stage=second_stage,
        locator="002-source-two",
        checksum_sha256=sha256(b"pass218-i33-source-two").hexdigest(),
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        media_type="text/markdown",
    )
    manifest = build_curriculum_manifest(
        _h72("GENESIS", {"iteration": 33}),
        [source_two, source_one],
    )
    authority = Pass218I33CurriculumAuthority(
        manifest=manifest,
        initial_cursor=CurriculumCursor.for_manifest(manifest),
    ).validated()
    return authority, source_one, source_two


def _make_i31_success(
    root: Path,
    *,
    upstream_curriculum_hash72: str,
) -> dict[str, object]:
    promotion_receipt_hash72 = _h72("I30-PROMOTION-RECEIPT", {"source": 33})
    promotion_hash72 = _h72("I30-PROMOTION", {"source": 33})
    i29_validation_hash72 = _h72("I29-VALIDATION", {"source": 33})
    validated_hash216 = (
        upstream_curriculum_hash72
        + _h72("VALIDATED-B", {"source": 33})
        + _h72("VALIDATED-C", {"source": 33})
    )
    promoted_object_hash72 = _h72("PROMOTED-OBJECT", {"source": 33})
    canonical_root_hash72 = _h72("CANONICAL-ROOT", {"source": 33})
    candidate_sha256 = sha256(b"pass218-i33-candidate").hexdigest()
    durability_witness_hash72 = _h72("DURABILITY", {"source": 33})
    persisted_inventory_hash72 = _h72("INVENTORY", {"source": 33})
    purge_validation_hash72 = _h72(
        "PURGE-VALIDATION",
        {
            "promotion_receipt": promotion_receipt_hash72,
            "promoted": promoted_object_hash72,
            "durability": durability_witness_hash72,
        },
    )
    body = {
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
        {"domain": "HHS-P218-I31-VERBATIM-PURGE-RECEIPT-V1"}, body
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
        **body,
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


def _close(
    tmp_path: Path,
    *,
    authority: Pass218I33CurriculumAuthority,
    declared_identity: str | None = None,
    declared_position: int = 0,
    upstream_identity: str | None = None,
    ready: bool = True,
):
    source = authority.manifest.source_at(0)
    curriculum_identity = (
        authority.manifest.curriculum_identity_hash72
        if declared_identity is None
        else declared_identity
    )
    upstream = curriculum_identity if upstream_identity is None else upstream_identity
    i31_root = tmp_path / "i31"
    purge = _make_i31_success(
        i31_root,
        upstream_curriculum_hash72=upstream,
    )
    lifecycle = _Lifecycle(ready)
    i32_root = tmp_path / "i32"
    closer = Pass218I32SourceCloser(
        lifecycle=lifecycle,
        i31_store_root=i31_root,
        closure_store_root=i32_root,
    )
    request = Pass218I32ClosureRequest(
        expected_i31_purge_receipt_hash72=str(purge["purge_receipt_hash72"]),
        expected_i31_purge_validation_hash72=str(purge["purge_validation_hash72"]),
        expected_i31_purge_gate_root_hash72=str(purge["purge_gate_root_hash72"]),
        expected_i31_purge_hash216=str(purge["purge_hash216"]),
        expected_i30_promotion_receipt_hash72=str(
            purge["i30_promotion_receipt_hash72"]
        ),
        expected_promoted_object_hash72=str(purge["promoted_object_hash72"]),
        expected_canonical_root_hash72=str(purge["canonical_root_hash72"]),
        source_id=str(source["source_id"]),
        source_sha256=str(source["checksum_sha256"]),
        source_authority=str(source["source_authority"]),
        rights_class=str(source["rights_class"]),
        curriculum_identity_hash72=curriculum_identity,
        curriculum_position=declared_position,
        source_stage=int(source["stage"]),
        previous_closure_hash72=None,
        closure_scope=PASS218_I32_CLOSURE_SCOPE,
    ).validated()
    closure = closer.close(request)
    return lifecycle, i32_root, closure


def test_i33_advances_exact_manifest_bound_closure_and_restarts_idempotently(
    tmp_path: Path,
) -> None:
    authority, _, _ = _manifest()
    lifecycle, i32_root, closure = _close(tmp_path, authority=authority)
    advancer = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=i32_root,
        advance_store_root=tmp_path / "i33",
        authority=authority,
    )
    first = advancer.advance()
    replay = advancer.advance()

    assert first == replay
    assert first["advance_status"] == PASS218_I33_ADVANCED_STATUS
    assert first["source_binding_matches_authoritative_manifest"] is True
    assert first["upstream_semantic_curriculum_binding_verified"] is True
    assert first["curriculum_advance_permitted"] is True
    assert first["curriculum_cursor_advanced"] is True
    assert first["stage_advance_permitted"] is False
    assert first["stage_transition_required"] is False
    assert first["next_cursor"]["next_ordinal"] == 1
    assert first["next_cursor"]["last_closure_hash72"] == closure["source_closure_hash72"]
    assert first["i32_source_closure_hash72"] == closure["source_closure_hash72"]
    assert validate_hash72(first["transition_hash72"])
    assert validate_hash72(first["advance_receipt_hash72"])
    assert len(first["advance_hash216"]) == 216
    assert first["vm81_authorization_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["authoritative_float_weights_created"] is False

    restarted = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=i32_root,
        advance_store_root=tmp_path / "i33",
        authority=authority,
    )
    assert restarted.advance() == first
    assert restarted.status()["curriculum_cursor_advanced"] is True


def test_i33_stops_at_stage_acceptance_when_next_source_is_later_stage(
    tmp_path: Path,
) -> None:
    authority, _, _ = _manifest(second_stage=CurriculumStage.SIMPLE_NARRATIVE)
    lifecycle, i32_root, _ = _close(tmp_path, authority=authority)
    result = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=i32_root,
        advance_store_root=tmp_path / "i33",
        authority=authority,
    ).advance()
    assert result["advance_status"] == PASS218_I33_STAGE_GATE_STATUS
    assert result["stage_transition_required"] is True
    assert result["stage_advance_permitted"] is False
    assert result["next_expected_stage"] == int(CurriculumStage.SIMPLE_NARRATIVE)


def test_i33_rejects_frozen_style_non_authoritative_curriculum_claim(
    tmp_path: Path,
) -> None:
    authority, _, _ = _manifest()
    source_sha256 = str(authority.manifest.source_at(0)["checksum_sha256"])
    non_authoritative_claim = hash72_digest(
        {"domain": "HHS-P218-I29-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 29,
            "authoritative_curriculum_advance": False,
        },
    )
    lifecycle, i32_root, _ = _close(
        tmp_path,
        authority=authority,
        declared_identity=non_authoritative_claim,
        declared_position=29,
        upstream_identity=non_authoritative_claim,
    )
    advancer = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=i32_root,
        advance_store_root=tmp_path / "i33",
        authority=authority,
    )
    with pytest.raises(
        Pass218I33CurriculumBindingError,
        match="P218_I33_AUTHORITATIVE_CURRICULUM_MISMATCH:curriculum_identity_hash72",
    ):
        advancer.advance()
    assert advancer.store.state_record() is None
    assert advancer.status()["curriculum_cursor_advanced"] is False


def test_i33_rejects_posthoc_i32_rebinding_to_unrelated_upstream_identity(
    tmp_path: Path,
) -> None:
    authority, _, _ = _manifest()
    unrelated = _h72("UNRELATED-UPSTREAM-CURRICULUM", {"iteration": 33})
    lifecycle, i32_root, _ = _close(
        tmp_path,
        authority=authority,
        upstream_identity=unrelated,
    )
    advancer = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=i32_root,
        advance_store_root=tmp_path / "i33",
        authority=authority,
    )
    with pytest.raises(
        Pass218I33CurriculumBindingError,
        match="P218_I33_UPSTREAM_CURRICULUM_IDENTITY_MISMATCH",
    ):
        advancer.advance()
    assert advancer.store.state_record() is None


def test_i33_requires_writer_fence_before_cursor_transition(tmp_path: Path) -> None:
    authority, _, _ = _manifest()
    lifecycle, i32_root, _ = _close(tmp_path, authority=authority)
    lifecycle.ready = False
    advancer = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=i32_root,
        advance_store_root=tmp_path / "i33",
        authority=authority,
    )
    with pytest.raises(RuntimeError, match="P218_TEST_WRITER_FENCE_CLOSED"):
        advancer.advance()
    assert advancer.store.state_record() is None


def test_i33_runtime_os_is_fail_closed_without_preconfigured_authority(
    tmp_path: Path,
) -> None:
    app = FastAPI()
    lifecycle = _Lifecycle(True)
    i32_control = _I32Control(tmp_path / "i32")
    control = install_pass218_i33_curriculum_advance_control(
        app,
        i32_control,
        lifecycle,
        state_root=tmp_path,
    )
    client = TestClient(app)
    status = client.get(PASS218_I33_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["authoritative_curriculum_ready"] is False
    assert status.json()["api_can_mint_curriculum_authority"] is False
    denied = client.post(PASS218_I33_ADVANCE_PATH)
    assert denied.status_code == 503
    assert "P218_I33_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED" in denied.text
    assert control.advancer.store.state_record() is None


def test_i33_runtime_os_advances_with_internal_authority_not_request_payload(
    tmp_path: Path,
) -> None:
    authority, _, _ = _manifest()
    lifecycle, i32_root, closure = _close(tmp_path, authority=authority)
    app = FastAPI()
    control = install_pass218_i33_curriculum_advance_control(
        app,
        _I32Control(i32_root),
        lifecycle,
        state_root=tmp_path / "runtime",
        authority=authority,
    )
    client = TestClient(app)
    status = client.get(PASS218_I33_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["authoritative_curriculum_ready"] is True
    assert status.json()["api_can_mint_curriculum_authority"] is False
    result = client.post(PASS218_I33_ADVANCE_PATH)
    assert result.status_code == 200
    assert result.json()["i32_source_closure_hash72"] == closure["source_closure_hash72"]
    assert result.json()["curriculum_cursor_advanced"] is True
    assert control.status()["stage_advance_permitted"] is False

    paths = {str(route.path) for route in app.routes}
    assert PASS218_I33_STATUS_PATH in paths
    assert PASS218_I33_ADVANCE_PATH in paths
    assert not any("stage-advance" in path for path in paths)
    assert not any("source-text" in path or "buffer" in path for path in paths)
