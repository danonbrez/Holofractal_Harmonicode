#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 38."""
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
    Pass218I37ManifestBoundPromotionAdmissionProof,
)
from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import (
    PASS218_I38_COMPLETE_STATUS,
    PASS218_I38_VERSION,
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
from hhs_runtime.pass218.promotion import PROMOTION_SCOPE

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = ROOT / "hhs_runtime" / "Grammar Correction.csv"
EVIDENCE_ROOT = ROOT / ".i38-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration38_evidence.json"


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
        {"domain": "HHS-P218-I38-EVIDENCE-GENESIS-V1"},
        {"suite": "manifest-promotion-authorization"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="pass218-i38-evidence.md",
                stage=CurriculumStage.REFERENCE,
                locator="pass218-i38-evidence.md",
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
        source_id="pass218-i38-evidence.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=seed,
        grammar_rule_set=compile_grammar_rules(GRAMMAR_PATH),
        expected_source_sha256=sha256(source).hexdigest(),
    )


def main() -> int:
    source = (
        b"Pass 218 Iteration 38 binds the exact frozen I37 promotability proof to "
        b"an explicit promotion grant and authorization. Canonical I6 execution "
        b"remains a separate, uninvoked boundary."
    )
    with TemporaryDirectory(prefix="hhs-p218-i38-") as temporary:
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
        i34.bind(source_id="pass218-i38-evidence.md", source_bytes=source)
        i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=lifecycle,
            i34_store_root=state / "manifest-source-ingress-i34",
            transaction_store_root=state / "manifest-semantic-source-transaction-i35",
            manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
            i34_store=i34.store,
            i34_status_provider=i34.status,
        )
        i35.ingest(
            semantic_candidate=make_candidate(source, authority),
            source_bytes=source,
        )
        i36 = Pass218I36ManifestBoundVectorVM5184Staging(
            lifecycle=lifecycle,
            i35_store=i35.store,
            state_root=state / "manifest-vector-vm5184-staging-i36",
            i35_status_provider=i35.status,
        )
        i36.stage()
        i37 = Pass218I37ManifestBoundPromotionAdmissionProof(
            lifecycle=lifecycle,
            i36_store=i36.store,
            i35_store=i35.store,
            state_root=state / "manifest-promotion-admission-proof-i37",
            i36_status_provider=i36.status,
        )
        i37_receipt = i37.prove()

        i38_root = state / "manifest-promotion-authorization-i38"
        first = Pass218I38ManifestBoundPromotionAuthorization(
            lifecycle=lifecycle,
            i37_store=i37.store,
            state_root=i38_root,
            i37_status_provider=i37.status,
        )
        receipt = first.authorize()
        same_process = first.authorize()
        grant = first.active_grant()
        authorization = first.active_authorization()
        assert grant is not None and authorization is not None
        assert same_process == receipt
        assert first.i5_grant_invocation_count == 1
        assert first.i5_authorize_invocation_count == 1

        restarted = Pass218I38ManifestBoundPromotionAuthorization(
            lifecycle=lifecycle,
            i37_store=i37.store,
            state_root=i38_root,
            i37_status_provider=i37.status,
        )
        restarted_receipt = restarted.authorize()
        assert restarted_receipt == receipt
        assert restarted.active_grant() == grant
        assert restarted.active_authorization() == authorization
        assert restarted.i5_grant_invocation_count == 0
        assert restarted.i5_authorize_invocation_count == 0

        manifest = receipt["manifest_binding"]
        assert receipt["status"] == PASS218_I38_COMPLETE_STATUS
        assert receipt["i37_receipt_hash72"] == i37_receipt["i37_receipt_hash72"]
        assert receipt["manifest_bound_i5_proof_hash72"] == i37_receipt["manifest_bound_i5_proof_hash72"]
        assert grant["grantor_authority_hash72"] == manifest["authority_root_hash72"]
        assert grant["grant_sequence"] == manifest["curriculum_position"]
        assert grant["target_scope"] == PROMOTION_SCOPE
        assert grant["entry_id_sha256"] == receipt["i4_entry_id_sha256"]
        assert authorization["entry_id_sha256"] == receipt["i4_entry_id_sha256"]
        assert authorization["projection_sha256"] == receipt["i4_projection_sha256"]
        assert authorization["state"] == "AUTHORIZED_PENDING_CANONICAL_COMMIT"
        assert authorization["canonical_mutation_permitted"] is True
        assert receipt["canonical_mutation_permitted"] is True

        for value in (
            receipt["i5_grant_hash216"],
            receipt["i5_authorization_hash216"],
            receipt["i38_hash216"],
        ):
            assert len(value) == 216
            assert all(validate_hash72(value[offset:offset + 72]) for offset in (0, 72, 144))

        closed_flags = (
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
            "canonical_vector_store_mutation_invoked",
            "canonical_vm81_commit_invoked",
            "canonical_learning_commit_invoked",
            "model_activation_invoked",
            "authoritative_float_weights_created",
        )
        assert all(receipt[field] is False for field in closed_flags)
        for path in i38_root.rglob("*"):
            if path.is_file():
                assert source not in path.read_bytes()

        evidence = {
            "schema": "HHS-P218-I38-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I38_VERSION,
            "status": receipt["status"],
            "i37_receipt_hash72": receipt["i37_receipt_hash72"],
            "i37_hash216": receipt["i37_hash216"],
            "manifest_bound_i5_proof_hash72": receipt["manifest_bound_i5_proof_hash72"],
            "i5_proof_hash72": receipt["i5_proof_hash72"],
            "i5_grantor_authority_hash72": receipt["i5_grantor_authority_hash72"],
            "i5_grant_sequence": receipt["i5_grant_sequence"],
            "i5_target_scope": receipt["i5_target_scope"],
            "i5_grant_hash72": receipt["i5_grant_hash72"],
            "i5_grant_hash216": receipt["i5_grant_hash216"],
            "i5_authorization_hash72": receipt["i5_authorization_hash72"],
            "i5_authorization_hash216": receipt["i5_authorization_hash216"],
            "manifest_bound_i5_authorization_hash72": receipt["manifest_bound_i5_authorization_hash72"],
            "i38_validation_hash72": receipt["i38_validation_hash72"],
            "i38_receipt_hash72": receipt["i38_receipt_hash72"],
            "i38_hash216": receipt["i38_hash216"],
            "authorized_pending_canonical_commit": receipt["i5_authorized_pending_canonical_commit"],
            "canonical_mutation_permitted": receipt["canonical_mutation_permitted"],
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_grant_invocations": first.i5_grant_invocation_count,
            "first_process_authorize_invocations": first.i5_authorize_invocation_count,
            "restart_process_grant_invocations": restarted.i5_grant_invocation_count,
            "restart_process_authorize_invocations": restarted.i5_authorize_invocation_count,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "closed_later_authority_flags": list(closed_flags),
        }

    payload = canonical_bytes(evidence)
    digest = sha256(payload).hexdigest()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(payload + b"\n")
    print("PASS218_I38_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
