from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
import json

from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import (
    Pass197ABHydrationCalibration,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass217_checkpoint11_storage_snapshot_alignment_v1 import (
    CHECKPOINT11_AUTHORITIES,
    CHECKPOINT11_AUTHORITY_MAP,
    CHECKPOINT11_REQUIRED_AUTHORITIES,
    ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA,
    MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA,
    SNAPSHOT_REUSE_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES
from hhs_runtime.pass165.ingestion import MultimodalLearningService
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore


def _decisions(decision):
    return {
        row["authority_id"]: row
        for row in decision["inherited_execution_authority_reachability"]["decisions"]
    }


def _persistent_vector_fixture(tmp_path):
    key = bytes([17]) * 32
    store = PersistentEncryptedVectorStore(tmp_path / "checkpoint11-vectors.sqlite3", key=key)
    snapshot = bytes((index * 7 + 3) % 256 for index in range(SNAPSHOT_BYTES))
    legacy_root = sha256(b"pass217-checkpoint11-legacy-root").hexdigest()
    genesis_identity = sha256(b"pass217-checkpoint11-genesis").hexdigest()
    operation_identity = sha256(b"pass217-checkpoint11-operation").hexdigest()
    predecessor = hash72_digest({"lane": "predecessor"}, b"checkpoint11")
    current = hash72_digest({"lane": "current"}, snapshot)
    successor = hash72_digest({"lane": "successor"}, b"checkpoint11")
    hash216 = Hash216Array.build(
        predecessor,
        current,
        successor,
        genesis_identity=genesis_identity,
        logical_step=11,
        operation_identity=operation_identity,
        legacy_foundation_root=legacy_root,
    )
    input_hash72 = hash72_digest({"state": "input"}, b"checkpoint11")
    output_hash72 = hash72_digest({"state": "output"}, snapshot)
    operation_key = "pass217.checkpoint11.encrypted-vector-reuse"
    obj = store.admit(
        operation_key=operation_key,
        logical_step=11,
        input_hash72=input_hash72,
        output_hash72=output_hash72,
        operation_identity_sha256=operation_identity,
        hash216=hash216,
        output_snapshot=snapshot,
        legacy_foundation_root=legacy_root,
        genesis_identity=genesis_identity,
        direct_cost_units=37,
        changed_bits=19,
        parent_object_id=None,
    )
    request = {
        "schema": ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA,
        "operation_key": operation_key,
        "expected_object_id": obj.object_id,
        "expected_store_root_sha256": store.root(),
        "expected_snapshot_sha256": sha256(snapshot).hexdigest(),
        "expected_output_hash72": output_hash72,
        "legacy_foundation_root": legacy_root,
        "genesis_identity": genesis_identity,
    }
    return store, request, obj, snapshot


def _snapshot_fixture(tmp_path):
    runtime = Pass197ABHydrationCalibration(state_root=tmp_path / "checkpoint11-pass197")
    config = {
        "x_values": ["1"],
        "y_values": ["1"],
        "xy_symbol_values": [0],
        "include_domain_rejections": True,
        "full_replay": True,
    }
    report = runtime.run(config, resume=True)
    checkpoint = json.loads(runtime.checkpoint_path.read_text(encoding="utf-8"))
    request = {
        "schema": SNAPSHOT_REUSE_REQUEST_SCHEMA,
        "config": config,
        "expected_config_hash72": report["config_hash72"],
        "expected_checkpoint_hash72": checkpoint["checkpoint_hash72"],
        "expected_completed_state_count": len(checkpoint["completed"]),
        "expected_state_root_hash72": report["state_root_hash72"],
        "expected_report_hash72": report["report_hash72"],
    }
    return runtime, request, checkpoint, report


def _multimodal_request():
    text = b"alpha beta alpha beta exact\n"
    image = b"\x89PNG\r\n\x1a\n" + (b"checkpoint11-image-region" * 8)
    request = {
        "schema": MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA,
        "provenance": "pass217-checkpoint11",
        "authorization_scope": "PASS217_CHECKPOINT11_PREFLIGHT",
        "sources": [
            {
                "declared_media_type": "TEXT",
                "source_b64": b64encode(text).decode("ascii"),
                "expected_source_sha256": sha256(text).hexdigest(),
            },
            {
                "declared_media_type": "IMAGE",
                "source_b64": b64encode(image).decode("ascii"),
                "expected_source_sha256": sha256(image).hexdigest(),
            },
        ],
    }
    return request


def test_checkpoint11_maps_operational_repository_native_callables() -> None:
    assert CHECKPOINT11_AUTHORITIES == (
        "encrypted_vector_store",
        "snapshot_reuse",
        "multimodal_cross_alignment",
    )
    encrypted = CHECKPOINT11_AUTHORITY_MAP["encrypted_vector_store"]
    assert encrypted["origin_pass"] == 174
    assert encrypted["later_contract_alignment_pass"] == 194
    assert encrypted["persistent_private_vector_required"] is True
    assert encrypted["implementation_symbol"] == "EncryptedVectorStore.retrieve"
    snapshot = CHECKPOINT11_AUTHORITY_MAP["snapshot_reuse"]
    assert snapshot["origin_pass"] == 197
    assert snapshot["symbol"] == "Pass197ABHydrationCalibration.run"
    multimodal = CHECKPOINT11_AUTHORITY_MAP["multimodal_cross_alignment"]
    assert multimodal["origin_pass"] == 165
    assert multimodal["semantic_equivalence_claimed"] is False


def test_checkpoint11_no_domains_are_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint11-none.json"),
    )
    assert decision is not None and decision["ok"] is True
    authority = decision["inherited_execution_authority_reachability"]
    assert authority["required_authority_count"] >= len(CHECKPOINT11_REQUIRED_AUTHORITIES)
    scope = tuple(authority["checkpoint_scope"])
    offset = len(CHECKPOINT11_REQUIRED_AUTHORITIES) - len(CHECKPOINT11_AUTHORITIES)
    assert scope[offset : offset + len(CHECKPOINT11_AUTHORITIES)] == CHECKPOINT11_AUTHORITIES
    decisions = _decisions(decision)
    for authority_id in CHECKPOINT11_AUTHORITIES:
        assert decisions[authority_id]["state"] == "NOT_APPLICABLE"
        assert decisions[authority_id]["mechanically_proven"] is True


def test_checkpoint11_real_route_traverses_encrypted_snapshot_and_multimodal_reuse(tmp_path) -> None:
    vector_store, encrypted_request, vector_obj, vector_snapshot = _persistent_vector_fixture(tmp_path)
    snapshot_runtime, snapshot_request, checkpoint_before, report_before = _snapshot_fixture(tmp_path)
    multimodal_service = MultimodalLearningService()
    multimodal_request = _multimodal_request()
    checkpoint_bytes_before = snapshot_runtime.checkpoint_path.read_bytes()
    multimodal_status_before = multimodal_service.status()
    vector_root_before = vector_store.root()

    try:
        decision = compose_bound_route_ingress(
            "api.runtime.services.dispatch",
            {
                "service": "example",
                "encrypted_vector_store": encrypted_request,
                "snapshot_reuse": snapshot_request,
                "multimodal_cross_alignment": multimodal_request,
            },
            cache={},
            semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint11-semantic.json"),
            encrypted_vector_store=vector_store,
            snapshot_reuse_runtime=snapshot_runtime,
            multimodal_alignment_service=multimodal_service,
        )
        assert decision is not None and decision["ok"] is True
        assert decision["propagation_allowed"] is True
        authority = decision["inherited_execution_authority_reachability"]
        assert authority["required_authority_count"] >= len(CHECKPOINT11_REQUIRED_AUTHORITIES)
        decisions = _decisions(decision)
        for authority_id in CHECKPOINT11_AUTHORITIES:
            assert decisions[authority_id]["state"] == "ACTIVE_IN_PATH"
            assert decisions[authority_id]["witness_root"]

        encrypted = decisions["encrypted_vector_store"]["traversal_witness"]
        assert encrypted["object_id"] == vector_obj.object_id
        assert encrypted["snapshot_sha256"] == sha256(vector_snapshot).hexdigest()
        assert encrypted["store_root_sha256"] == vector_root_before
        assert encrypted["authenticated_encryption"] == "AES_GCM"
        assert encrypted["plaintext_persisted"] is False
        assert encrypted["retrieval_mutated_store"] is False
        assert vector_store.root() == vector_root_before

        snapshot = decisions["snapshot_reuse"]["traversal_witness"]
        assert snapshot["checkpoint_hash72"] == checkpoint_before["checkpoint_hash72"]
        assert snapshot["state_root_hash72"] == report_before["state_root_hash72"]
        assert snapshot["report_hash72"] == report_before["report_hash72"]
        assert snapshot["completed_state_count_reused"] == 1
        assert snapshot["checkpoint_bytes_unchanged"] is True
        assert snapshot["resume_reused_preexisting_checkpoint"] is True
        assert snapshot["deterministic_replay"] is True
        assert snapshot_runtime.checkpoint_path.read_bytes() == checkpoint_bytes_before

        multimodal = decisions["multimodal_cross_alignment"]["traversal_witness"]
        assert multimodal["modalities"] == ["IMAGE", "TEXT"]
        assert multimodal["projection_coordinates"] == 5184
        assert multimodal["projection_bytes"] == 648
        assert len(multimodal["records"]) == 2
        assert all(row["projection_bytes"] == 648 for row in multimodal["records"])
        assert multimodal["semantic_equivalence_claimed"] is False
        assert multimodal["alignment_claim"] == "COMMON_EXACT_PROJECTION_GEOMETRY_ONLY"
        assert multimodal["preflight_mutated_service"] is False
        assert multimodal_service.status() == multimodal_status_before
    finally:
        vector_store.close()


def test_checkpoint11_applicable_domains_without_bound_runtimes_fail_closed(tmp_path) -> None:
    multimodal_request = _multimodal_request()
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "encrypted_vector_store": {
                "schema": ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA,
                "operation_key": "missing",
                "expected_object_id": "1" * 64,
                "expected_store_root_sha256": "2" * 64,
                "expected_snapshot_sha256": "3" * 64,
                "expected_output_hash72": "x",
                "legacy_foundation_root": "4" * 64,
                "genesis_identity": "5" * 64,
            },
            "snapshot_reuse": {
                "schema": SNAPSHOT_REUSE_REQUEST_SCHEMA,
                "config": {"x_values": ["1"], "y_values": ["1"], "xy_symbol_values": [0]},
                "expected_config_hash72": "a",
                "expected_checkpoint_hash72": "b",
                "expected_completed_state_count": 1,
                "expected_state_root_hash72": "c",
                "expected_report_hash72": "d",
            },
            "multimodal_cross_alignment": multimodal_request,
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint11-missing-runtime.json"),
    )
    assert decision is not None and decision["ok"] is False
    decisions = _decisions(decision)
    expected_fragments = {
        "encrypted_vector_store": "REJECT_ENCRYPTED_VECTOR_STORE_RUNTIME_MISSING",
        "snapshot_reuse": "REJECT_SNAPSHOT_REUSE_RUNTIME_MISSING",
        "multimodal_cross_alignment": "REJECT_MULTIMODAL_ALIGNMENT_SERVICE_MISSING",
    }
    for authority_id, fragment in expected_fragments.items():
        row = decisions[authority_id]
        assert row["state"] is None
        assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in row["reasons"]
        assert fragment in row["traversal_witness"]["reason"]


def test_checkpoint11_single_modality_alignment_fails_closed(tmp_path) -> None:
    raw = b"single modality only"
    request = {
        "schema": MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA,
        "provenance": "pass217-checkpoint11",
        "authorization_scope": "PASS217_CHECKPOINT11_PREFLIGHT",
        "sources": [
            {
                "declared_media_type": "TEXT",
                "source_b64": b64encode(raw).decode("ascii"),
                "expected_source_sha256": sha256(raw).hexdigest(),
            },
            {
                "declared_media_type": "TEXT",
                "source_b64": b64encode(raw + b" second").decode("ascii"),
                "expected_source_sha256": sha256(raw + b" second").hexdigest(),
            },
        ],
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "multimodal_cross_alignment": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint11-single-modality.json"),
        multimodal_alignment_service=MultimodalLearningService(),
    )
    assert decision is not None and decision["ok"] is False
    row = _decisions(decision)["multimodal_cross_alignment"]
    assert row["state"] is None
    assert "REJECT_MULTIMODAL_ALIGNMENT_DISTINCT_MODALITIES_REQUIRED" in row["traversal_witness"]["reason"]
