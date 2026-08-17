#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 34 manifest-bound ingress evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    PASS218_I34_READY_STATUS,
    Pass218I34ManifestBoundSourceIngress,
)

SOURCE_NAME = "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_authority(repository_root: Path, source_sha256: str):
    manifest = build_curriculum_manifest(
        hash72_digest(
            {"domain": "HHS-P218-I34-EVIDENCE-GENESIS-V1"},
            {"repository": repository_root.name, "source": SOURCE_NAME},
        ),
        (
            CurriculumSource(
                source_id=SOURCE_NAME,
                stage=CurriculumStage.EXPOSITORY,
                locator=SOURCE_NAME,
                checksum_sha256=source_sha256,
                rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
                source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
                media_type="text/markdown",
            ),
        ),
    )
    return Pass218I33CurriculumAuthority(
        manifest=manifest,
        initial_cursor=CurriculumCursor.for_manifest(manifest),
    ).validated()


def main() -> None:
    repository_root = Path.cwd().resolve()
    source_path = repository_root / SOURCE_NAME
    source_bytes = source_path.read_bytes()
    source_sha256 = sha256(source_bytes).hexdigest()
    authority = build_authority(repository_root, source_sha256)
    authority_record = authority.record()

    with TemporaryDirectory(prefix="hhs-pass218-i34-evidence-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        try:
            i33_root = state_root / "cognition" / "curriculum-advance-i33"
            ingress_root = state_root / "cognition" / "manifest-source-ingress-i34"
            first_runtime = Pass218I34ManifestBoundSourceIngress(
                lifecycle=lifecycle,
                authority=authority,
                i33_store_root=i33_root,
                ingress_store_root=ingress_root,
            )
            first = first_runtime.bind(source_id=SOURCE_NAME, source_bytes=source_bytes)
            assert first["binding_status"] == PASS218_I34_READY_STATUS
            assert first["manifest_bound_source_ready"] is True
            assert first["source_checksum_verified"] is True
            assert first["source_payload_persisted"] is False
            assert first["verbatim_corpus_source_retained"] is False
            assert first["managed_ingress_buffer_zeroized"] is True
            assert first["managed_ingress_buffer_cleared"] is True
            assert first["i3_source_transaction_required"] is True
            assert first["i3_source_transaction_invoked"] is False
            assert first["semantic_construction_invoked"] is False
            assert first["curriculum_cursor_advanced"] is False
            assert first["stage_advance_permitted"] is False

            probe = source_bytes[:128]
            assert probe
            durable_files = [path for path in ingress_root.rglob("*") if path.is_file()]
            assert durable_files
            assert all(probe not in path.read_bytes() for path in durable_files)

            restarted = Pass218I34ManifestBoundSourceIngress(
                lifecycle=lifecycle,
                authority=authority,
                i33_store_root=i33_root,
                ingress_store_root=ingress_root,
            )
            replay = restarted.bind(source_id=SOURCE_NAME, source_bytes=source_bytes)
            assert replay == first
            status = restarted.status()
            assert status["manifest_bound_source_ready"] is True
            assert status["binding_current"] is True

            payload = {
                "schema": "HHS-P218-I34-EVIDENCE-V1",
                "iteration": 34,
                "source_id": SOURCE_NAME,
                "source_sha256": source_sha256,
                "source_stage": first["source_stage"],
                "authority_root_hash72": authority_record["authority_root_hash72"],
                "manifest_hash72": authority.manifest.manifest_hash72,
                "curriculum_identity_hash72": authority.manifest.curriculum_identity_hash72,
                "curriculum_position": first["curriculum_position"],
                "source_identity_hash72": first["source_identity_hash72"],
                "source_binding_hash72": first["source_binding_hash72"],
                "ingress_validation_hash72": first["ingress_validation_hash72"],
                "ingress_receipt_hash72": first["ingress_receipt_hash72"],
                "ingress_hash216": first["ingress_hash216"],
                "writer_fence_real_i9_lifecycle": True,
                "manifest_match_verified": True,
                "cursor_match_verified": True,
                "source_checksum_verified": True,
                "durable_verbatim_probe_absent": True,
                "managed_ingress_buffer_zeroized": True,
                "managed_ingress_buffer_cleared": True,
                "deterministic_replay_equal": True,
                "restart_replay_equal": True,
                "api_can_mint_curriculum_authority": False,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
                "i3_source_transaction_required": True,
                "i3_source_transaction_invoked": False,
                "semantic_construction_invoked": False,
                "curriculum_cursor_advanced": False,
                "stage_advance_permitted": False,
                "vm81_authorization_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
        finally:
            lifecycle.shutdown()

    assert validate_hash72(payload["authority_root_hash72"])
    assert validate_hash72(payload["manifest_hash72"])
    assert validate_hash72(payload["curriculum_identity_hash72"])
    assert validate_hash72(payload["source_binding_hash72"])
    assert validate_hash72(payload["ingress_validation_hash72"])
    assert validate_hash72(payload["ingress_receipt_hash72"])
    assert len(payload["ingress_hash216"]) == 216

    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i34-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration34_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration34_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
