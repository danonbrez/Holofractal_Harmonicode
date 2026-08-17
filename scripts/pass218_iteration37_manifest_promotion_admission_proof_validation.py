#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 37."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    PASS218_I37_COMPLETE_STATUS,
    PASS218_I37_VERSION,
    Pass218I37ManifestBoundPromotionAdmissionProof,
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
EVIDENCE_ROOT = ROOT / ".i37-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration37_evidence.json"


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
        {"domain": "HHS-P218-I37-EVIDENCE-GENESIS-V1"},
        {"suite": "manifest-promotion-admission-proof"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="pass218-i37-evidence.md",
                stage=CurriculumStage.REFERENCE,
                locator="pass218-i37-evidence.md",
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
        source_id="pass218-i37-evidence.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def main() -> int:
    source = (
        b"Pass 218 Iteration 37 deterministically proves that the exact frozen I36 "
        b"manifest-bound I4 candidate is reproducible and promotable. The proof does "
        b"not create an authority grant, promotion authorization, or canonical mutation."
    )
    with TemporaryDirectory(prefix="hhs-p218-i37-") as temporary:
        root = Path(temporary)
        lifecycle = ReadyLifecycle()
        authority = make_authority(source)
        i33_root = root / "state" / "cognition" / "curriculum-advance-i33"
        i34_root = root / "state" / "cognition" / "manifest-source-ingress-i34"
        i35_root = root / "state" / "cognition" / "manifest-semantic-source-transaction-i35"
        i36_root = root / "state" / "cognition" / "manifest-vector-vm5184-staging-i36"
        i37_root = root / "state" / "cognition" / "manifest-promotion-admission-proof-i37"

        i34 = Pass218I34ManifestBoundSourceIngress(
            lifecycle=lifecycle,
            authority=authority,
            i33_store_root=i33_root,
            ingress_store_root=i34_root,
        )
        i34_receipt = i34.bind(
            source_id="pass218-i37-evidence.md",
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

        i36 = Pass218I36ManifestBoundVectorVM5184Staging(
            lifecycle=lifecycle,
            i35_store=i35.store,
            state_root=i36_root,
            i35_status_provider=i35.status,
        )
        i36_receipt = i36.stage()
        i36_stage = i36.active_stage()
        assert i36_stage is not None

        first = Pass218I37ManifestBoundPromotionAdmissionProof(
            lifecycle=lifecycle,
            i36_store=i36.store,
            i35_store=i35.store,
            state_root=i37_root,
            i36_status_provider=i36.status,
        )
        receipt = first.prove()
        same_process = first.prove()
        envelope = first.active_proof()
        assert envelope is not None
        assert same_process == receipt
        assert first.i5_prove_invocation_count == 1

        restarted = Pass218I37ManifestBoundPromotionAdmissionProof(
            lifecycle=lifecycle,
            i36_store=i36.store,
            i35_store=i35.store,
            state_root=i37_root,
            i36_status_provider=i36.status,
        )
        restarted_receipt = restarted.prove()
        restarted_envelope = restarted.active_proof()
        assert restarted_receipt == receipt
        assert restarted_envelope == envelope
        assert restarted.i5_prove_invocation_count == 0

        proof = envelope["i5_promotability_proof"]
        assert receipt["status"] == PASS218_I37_COMPLETE_STATUS
        assert receipt["i36_receipt_hash72"] == i36_receipt["i36_receipt_hash72"]
        assert receipt["manifest_bound_i4_stage_hash72"] == i36_receipt["manifest_bound_i4_stage_hash72"]
        assert receipt["i35_receipt_hash72"] == i35_receipt["i35_receipt_hash72"]
        assert receipt["i34_ingress_receipt_hash72"] == i34_receipt["ingress_receipt_hash72"]
        assert receipt["manifest_binding"] == i36_receipt["manifest_binding"]
        assert receipt["i3_transaction_snapshot_hash72"] == snapshot["snapshot_hash72"]
        assert receipt["i4_entry_id_sha256"] == i36_receipt["i4_entry_id_sha256"]
        assert proof["entry_id_sha256"] == i36_receipt["i4_entry_id_sha256"]
        assert proof["staging_hash72"] == i36_receipt["i4_staging_hash72"]
        assert proof["projection_sha256"] == i36_receipt["i4_projection_sha256"]
        assert proof["promotable"] is True
        assert proof["explicit_authority_grant_present"] is False
        assert proof["canonical_mutation_permitted"] is False
        assert len(proof["proof_hash216"]) == 216
        assert all(
            validate_hash72(proof["proof_hash216"][offset:offset + 72])
            for offset in (0, 72, 144)
        )
        assert len(receipt["i37_hash216"]) == 216
        assert all(
            validate_hash72(receipt["i37_hash216"][offset:offset + 72])
            for offset in (0, 72, 144)
        )

        closed_flags = (
            "pass218_i5_promotion_invoked",
            "i5_explicit_authority_grant_present",
            "i5_promotion_authorization_invoked",
            "canonical_mutation_permitted",
            "pass218_i6_canonical_commit_invoked",
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

        for path in i37_root.rglob("*"):
            if path.is_file():
                assert source not in path.read_bytes()

        evidence = {
            "schema": "HHS-P218-I37-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I37_VERSION,
            "status": receipt["status"],
            "i34_ingress_receipt_hash72": receipt["i34_ingress_receipt_hash72"],
            "i35_receipt_hash72": receipt["i35_receipt_hash72"],
            "i36_receipt_hash72": receipt["i36_receipt_hash72"],
            "i36_hash216": receipt["i36_hash216"],
            "manifest_bound_semantic_hash72": receipt["manifest_bound_semantic_hash72"],
            "i3_transaction_id_hash72": receipt["i3_transaction_id_hash72"],
            "i3_transaction_snapshot_hash72": receipt["i3_transaction_snapshot_hash72"],
            "manifest_bound_i4_stage_hash72": receipt["manifest_bound_i4_stage_hash72"],
            "i4_entry_id_sha256": receipt["i4_entry_id_sha256"],
            "i4_staging_hash72": receipt["i4_staging_hash72"],
            "i4_projection_sha256": receipt["i4_projection_sha256"],
            "i5_dependency_scope_hash72": receipt["i5_dependency_scope_hash72"],
            "i5_vector_entry_sha256": receipt["i5_vector_entry_sha256"],
            "i5_proof_hash72": receipt["i5_proof_hash72"],
            "i5_validation_hash72": receipt["i5_validation_hash72"],
            "i5_proof_hash216": receipt["i5_proof_hash216"],
            "manifest_bound_i5_proof_hash72": receipt["manifest_bound_i5_proof_hash72"],
            "i37_validation_hash72": receipt["i37_validation_hash72"],
            "i37_receipt_hash72": receipt["i37_receipt_hash72"],
            "i37_hash216": receipt["i37_hash216"],
            "i5_promotable": receipt["i5_promotable"],
            "i5_explicit_authority_grant_present": False,
            "i5_promotion_authorization_invoked": False,
            "canonical_mutation_permitted": False,
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_i5_prove_invocations": first.i5_prove_invocation_count,
            "restart_process_i5_prove_invocations": restarted.i5_prove_invocation_count,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "closed_later_authority_flags": list(closed_flags),
        }

    payload = canonical_bytes(evidence)
    digest = sha256(payload).hexdigest()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(payload + b"\n")
    print("PASS218_I37_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
