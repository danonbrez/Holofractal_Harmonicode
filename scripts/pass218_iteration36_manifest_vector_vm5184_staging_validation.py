#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 36."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    Pass218I35ManifestBoundSemanticSourceTransaction,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestBoundSourceIngress,
)
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    PASS218_I36_COMPLETE_STATUS,
    PASS218_I36_VERSION,
    Pass218I36ManifestBoundVectorVM5184Staging,
)

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = ROOT / "hhs_runtime" / "Grammar Correction.csv"
EVIDENCE_ROOT = ROOT / ".i36-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration36_evidence.json"


class ReadyLifecycle:
    def require_ingestion_ready(self) -> None:
        return None

    def status(self):
        return {"ingestion_enabled": True}


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I36-EVIDENCE-GENESIS-V1"},
        {"suite": "manifest-vector-vm5184-staging"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="pass218-i36-evidence.md",
                stage=CurriculumStage.REFERENCE,
                locator="pass218-i36-evidence.md",
                checksum_sha256=sha256(source).hexdigest(),
                rights_class="REPOSITORY_NATIVE_VALIDATION_AUTHORITY",
                source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
                media_type="text/markdown",
            ),
        ),
    )
    return Pass218I33CurriculumAuthority(
        manifest=manifest,
        initial_cursor=CurriculumCursor.for_manifest(manifest),
    ).validated()


def make_candidate(source: bytes, authority: Pass218I33CurriculumAuthority):
    fake_seed = SimpleNamespace(
        genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        payload={"distinctions": []},
    )
    rules = compile_grammar_rules(GRAMMAR_PATH)
    return NarrativeBeatHydrator(paragraphs_per_beat=1).hydrate(
        source.decode("utf-8"),
        source_id="pass218-i36-evidence.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def main() -> int:
    source = (
        b"Pass 218 Iteration 36 deterministically binds the frozen I35 closure "
        b"to a candidate-only inherited VM5184 vector projection. No promotion, "
        b"VM81 authority, curriculum advance, or canonical learning is invoked."
    )
    with TemporaryDirectory(prefix="hhs-p218-i36-") as temporary:
        root = Path(temporary)
        lifecycle = ReadyLifecycle()
        authority = make_authority(source)
        i33_root = root / "state" / "cognition" / "curriculum-advance-i33"
        i34_root = root / "state" / "cognition" / "manifest-source-ingress-i34"
        i35_root = root / "state" / "cognition" / "manifest-semantic-source-transaction-i35"
        i36_root = root / "state" / "cognition" / "manifest-vector-vm5184-staging-i36"

        i34 = Pass218I34ManifestBoundSourceIngress(
            lifecycle=lifecycle,
            authority=authority,
            i33_store_root=i33_root,
            ingress_store_root=i34_root,
        )
        i34_receipt = i34.bind(
            source_id="pass218-i36-evidence.md",
            source_bytes=source,
        )
        i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=lifecycle,
            i34_store_root=i34_root,
            transaction_store_root=i35_root,
            manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
            i34_store=i34.store,
            i34_status_provider=i34.status,
        )
        i35_receipt = i35.ingest(
            semantic_candidate=make_candidate(source, authority),
            source_bytes=source,
        )
        snapshot = i35.closed_transaction_snapshot()
        assert snapshot is not None

        first = Pass218I36ManifestBoundVectorVM5184Staging(
            lifecycle=lifecycle,
            i35_store=i35.store,
            state_root=i36_root,
            i35_status_provider=i35.status,
        )
        receipt = first.stage()
        same_process = first.stage()
        stage = first.active_stage()
        assert stage is not None
        assert same_process == receipt
        assert first.i4_invocation_count == 1

        restarted = Pass218I36ManifestBoundVectorVM5184Staging(
            lifecycle=lifecycle,
            i35_store=i35.store,
            state_root=i36_root,
            i35_status_provider=i35.status,
        )
        restarted_receipt = restarted.stage()
        restarted_stage = restarted.active_stage()
        assert restarted_receipt == receipt
        assert restarted_stage == stage
        assert restarted.i4_invocation_count == 0

        i4 = stage["i4_stage_candidate"]
        entry = i4["vector_entry"]
        forward = entry["forward_support"]
        inverse = entry["inverse_support"]
        assert receipt["status"] == PASS218_I36_COMPLETE_STATUS
        assert receipt["i35_receipt_hash72"] == i35_receipt["i35_receipt_hash72"]
        assert receipt["i34_ingress_receipt_hash72"] == i34_receipt["ingress_receipt_hash72"]
        assert receipt["manifest_binding"] == i35_receipt["manifest_binding"]
        assert receipt["i3_transaction_snapshot_hash72"] == snapshot["snapshot_hash72"]
        assert receipt["i4_projection_bytes"] == SNAPSHOT_BYTES == 648
        assert len(forward) + len(inverse) == COORDINATES
        assert set(forward).isdisjoint(inverse)
        assert sorted(forward + inverse) == list(range(COORDINATES))
        assert entry["admission_status"] == "CANDIDATE"
        assert len(receipt["i36_hash216"]) == 216
        assert all(
            validate_hash72(receipt["i36_hash216"][offset:offset + 72])
            for offset in (0, 72, 144)
        )

        closed_flags = (
            "pass218_i5_promotion_invoked",
            "pass218_i30_canonical_semantic_promotion_invoked",
            "pass218_i31_verbatim_purge_invoked",
            "pass218_i32_source_closure_invoked",
            "curriculum_cursor_advanced",
            "stage_advance_permitted",
            "vm81_authorization_invoked",
            "truth_promotion",
            "action_authority_minted",
            "authoritative_vector_store_promotion",
            "canonical_vm81_commit_invoked",
            "canonical_learning_commit_invoked",
            "model_activation_invoked",
            "authoritative_float_weights_created",
        )
        assert all(receipt[field] is False for field in closed_flags)

        for path in i36_root.rglob("*"):
            if path.is_file():
                assert source not in path.read_bytes()

        evidence = {
            "schema": "HHS-P218-I36-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I36_VERSION,
            "status": receipt["status"],
            "i34_ingress_receipt_hash72": receipt["i34_ingress_receipt_hash72"],
            "i35_receipt_hash72": receipt["i35_receipt_hash72"],
            "i35_hash216": receipt["i35_hash216"],
            "manifest_bound_semantic_hash72": receipt["manifest_bound_semantic_hash72"],
            "i3_transaction_id_hash72": receipt["i3_transaction_id_hash72"],
            "i3_transaction_snapshot_hash72": receipt["i3_transaction_snapshot_hash72"],
            "manifest_bound_i4_stage_hash72": receipt["manifest_bound_i4_stage_hash72"],
            "i4_entry_id_sha256": receipt["i4_entry_id_sha256"],
            "i4_staging_hash72": receipt["i4_staging_hash72"],
            "i4_validation_hash72": receipt["i4_validation_hash72"],
            "i4_staging_hash216": receipt["i4_staging_hash216"],
            "i4_projection_hash72": receipt["i4_projection_hash72"],
            "i4_projection_sha256": receipt["i4_projection_sha256"],
            "i4_projection_bytes": receipt["i4_projection_bytes"],
            "i4_projection_coordinates": COORDINATES,
            "i4_forward_support_count": len(forward),
            "i4_inverse_support_count": len(inverse),
            "i4_support_partition_complete": True,
            "i4_vector_admission_status": receipt["i4_vector_admission_status"],
            "i36_validation_hash72": receipt["i36_validation_hash72"],
            "i36_receipt_hash72": receipt["i36_receipt_hash72"],
            "i36_hash216": receipt["i36_hash216"],
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_i4_invocations": first.i4_invocation_count,
            "restart_process_i4_invocations": restarted.i4_invocation_count,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "closed_later_authority_flags": list(closed_flags),
        }

    payload = canonical_bytes(evidence)
    digest = sha256(payload).hexdigest()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(payload + b"\n")
    print("PASS218_I36_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
