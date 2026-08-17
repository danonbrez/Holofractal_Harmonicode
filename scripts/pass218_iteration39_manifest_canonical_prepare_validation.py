#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 39."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES, THREADS
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_canonical_prepare_i39 import (
    PASS218_I39_COMPLETE_STATUS,
    PASS218_I39_VERSION,
    Pass218I39ManifestBoundCanonicalPrepare,
)
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    Pass218I37ManifestBoundPromotionAdmissionProof,
)
from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import (
    Pass218I38ManifestBoundPromotionAuthorization,
)
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    Pass218I35ManifestBoundSemanticSourceTransaction,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestBoundSourceIngress,
)
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    Pass218I36ManifestBoundVectorVM5184Staging,
)

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = ROOT / "hhs_runtime" / "Grammar Correction.csv"
EVIDENCE_ROOT = ROOT / ".i39-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration39_evidence.json"


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
        {"domain": "HHS-P218-I39-EVIDENCE-GENESIS-V1"},
        {"suite": "manifest-canonical-prepare"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="pass218-i39-evidence.md",
                stage=CurriculumStage.REFERENCE,
                locator="pass218-i39-evidence.md",
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
    seed = SimpleNamespace(
        genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        payload={"distinctions": []},
    )
    return NarrativeBeatHydrator(paragraphs_per_beat=1).hydrate(
        source.decode("utf-8"),
        source_id="pass218-i39-evidence.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=seed,
        grammar_rule_set=compile_grammar_rules(GRAMMAR_PATH),
        expected_source_sha256=sha256(source).hexdigest(),
    )


def main() -> int:
    source = (
        b"Pass 218 Iteration 39 binds the exact frozen I38 authorization to the "
        b"frozen I6 noncanonical prepare membrane. All 64 VM81 lanes prove the "
        b"5,184-bit image while canonical commit and I7 persistence remain closed."
    )
    with TemporaryDirectory(prefix="hhs-p218-i39-") as temporary:
        root = Path(temporary)
        state = root / "state" / "cognition"
        lifecycle = ReadyLifecycle()
        authority = make_authority(source)

        i34 = Pass218I34ManifestBoundSourceIngress(
            lifecycle=lifecycle,
            authority=authority,
            i33_store_root=state / "curriculum-advance-i33",
            ingress_store_root=state / "manifest-source-ingress-i34",
        )
        i34.bind(source_id="pass218-i39-evidence.md", source_bytes=source)
        i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=lifecycle,
            i34_store_root=state / "manifest-source-ingress-i34",
            transaction_store_root=state / "manifest-semantic-source-transaction-i35",
            manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
            i34_store=i34.store,
            i34_status_provider=i34.status,
        )
        i35.ingest(semantic_candidate=make_candidate(source, authority), source_bytes=source)
        i36 = Pass218I36ManifestBoundVectorVM5184Staging(
            lifecycle=lifecycle,
            i35_store=i35.store,
            state_root=state / "manifest-vector-vm5184-staging-i36",
            i35_status_provider=i35.status,
        )
        i36_receipt = i36.stage()
        i37 = Pass218I37ManifestBoundPromotionAdmissionProof(
            lifecycle=lifecycle,
            i36_store=i36.store,
            i35_store=i35.store,
            state_root=state / "manifest-promotion-admission-proof-i37",
            i36_status_provider=i36.status,
        )
        i37.prove()
        i38 = Pass218I38ManifestBoundPromotionAuthorization(
            lifecycle=lifecycle,
            i37_store=i37.store,
            state_root=state / "manifest-promotion-authorization-i38",
            i37_status_provider=i37.status,
        )
        i38_receipt = i38.authorize()

        i39_root = state / "manifest-canonical-prepare-i39"
        first = Pass218I39ManifestBoundCanonicalPrepare(
            lifecycle=lifecycle,
            i38_store=i38.store,
            i37_store=i37.store,
            i36_store=i36.store,
            state_root=i39_root,
            i38_status_provider=i38.status,
            i36_status_provider=i36.status,
        )
        receipt = first.prepare()
        same_process = first.prepare()
        prepare_envelope = first.store.active_prepare()
        assert prepare_envelope is not None
        prepared = prepare_envelope["i6_prepare_record"]
        assert same_process == receipt
        assert first.i6_prepare_invocation_count == 1

        restarted = Pass218I39ManifestBoundCanonicalPrepare(
            lifecycle=lifecycle,
            i38_store=i38.store,
            i37_store=i37.store,
            i36_store=i36.store,
            state_root=i39_root,
            i38_status_provider=i38.status,
            i36_status_provider=i36.status,
        )
        restarted_receipt = restarted.prepare()
        assert restarted_receipt == receipt
        assert restarted.store.active_prepare() == prepare_envelope
        assert restarted.i6_prepare_invocation_count == 0

        assert receipt["status"] == PASS218_I39_COMPLETE_STATUS
        assert receipt["i38_receipt_hash72"] == i38_receipt["i38_receipt_hash72"]
        assert receipt["manifest_bound_i4_stage_hash72"] == i36_receipt["manifest_bound_i4_stage_hash72"]
        assert receipt["i5_authorization_hash72"] == i38_receipt["i5_authorization_hash72"]
        assert receipt["i6_vm81_shadow_commit_count"] == THREADS
        assert receipt["i6_projection_bytes"] == SNAPSHOT_BYTES
        assert prepared["vm81_prepared_snapshot_hash72"] == prepared["projection_hash72"]
        assert prepared["prepare_hash216"] == (
            prepared["authorization_hash72"]
            + prepared["prepare_hash72"]
            + prepared["validation_hash72"]
        )
        assert receipt["i39_hash216"] == (
            receipt["i38_receipt_hash72"]
            + receipt["i6_prepare_hash72"]
            + receipt["i39_receipt_hash72"]
        )
        for value in (receipt["i6_prepare_hash216"], receipt["i39_hash216"]):
            assert len(value) == 216
            assert all(validate_hash72(value[offset:offset + 72]) for offset in (0, 72, 144))

        closed_flags = (
            "pass218_i6_canonical_commit_invoked",
            "pass218_i7_durable_persistence_invoked",
            "pass218_i30_canonical_semantic_promotion_invoked",
            "pass218_i31_verbatim_purge_invoked",
            "pass218_i32_source_closure_invoked",
            "curriculum_cursor_advanced",
            "stage_advance_permitted",
            "truth_promotion",
            "action_authority_minted",
            "authoritative_vector_store_promotion",
            "canonical_vector_store_mutation_invoked",
            "canonical_vm81_commit_invoked",
            "canonical_learning_commit_invoked",
            "model_activation_invoked",
            "authoritative_float_weights_created",
        )
        assert all(receipt[field] is False for field in closed_flags)
        for path in i39_root.rglob("*"):
            if path.is_file():
                payload = path.read_bytes()
                assert source not in payload
                assert b"vm5184_projection_b64" not in payload
                assert b"source_text" not in payload

        evidence = {
            "schema": "HHS-P218-I39-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I39_VERSION,
            "status": receipt["status"],
            "i38_receipt_hash72": receipt["i38_receipt_hash72"],
            "i38_hash216": receipt["i38_hash216"],
            "i5_authorization_hash72": receipt["i5_authorization_hash72"],
            "manifest_bound_i4_stage_hash72": receipt["manifest_bound_i4_stage_hash72"],
            "i6_prepare_hash72": receipt["i6_prepare_hash72"],
            "i6_validation_hash72": receipt["i6_validation_hash72"],
            "i6_prepare_hash216": receipt["i6_prepare_hash216"],
            "i6_target_root_before_hash72": receipt["i6_target_root_before_hash72"],
            "i6_vm81_prepared_snapshot_hash72": receipt["i6_vm81_prepared_snapshot_hash72"],
            "i6_vm81_prepared_state_hash72": receipt["i6_vm81_prepared_state_hash72"],
            "i6_vm81_shadow_commit_count": receipt["i6_vm81_shadow_commit_count"],
            "i6_vm81_prepare_receipts_root_hash72": receipt["i6_vm81_prepare_receipts_root_hash72"],
            "manifest_bound_i6_prepare_hash72": receipt["manifest_bound_i6_prepare_hash72"],
            "i39_validation_hash72": receipt["i39_validation_hash72"],
            "i39_receipt_hash72": receipt["i39_receipt_hash72"],
            "i39_hash216": receipt["i39_hash216"],
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_i6_prepare_invocations": first.i6_prepare_invocation_count,
            "restart_process_i6_prepare_invocations": restarted.i6_prepare_invocation_count,
            "vm81_shadow_prepare_only": True,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "closed_later_authority_flags": list(closed_flags),
        }

    payload = canonical_bytes(evidence)
    digest = sha256(payload).hexdigest()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(payload + b"\n")
    print("PASS218_I39_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
