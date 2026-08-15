#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 35 manifest-bound transaction evidence."""
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
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    PASS218_I35_COMPLETE_STATUS,
    Pass218I35BindingError,
    Pass218I35ManifestBoundSemanticSourceTransaction,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestBoundSourceIngress,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = REPOSITORY_ROOT / "hhs_runtime" / "Grammar Correction.csv"
EVIDENCE_ROOT = REPOSITORY_ROOT / ".i35-evidence"
SOURCE_ID = "pass218-i35-evidence-source.md"
SOURCE = (
    b"Manifest authority precedes semantic construction. "
    b"The frozen I3 transaction remains non-authoritative and restartable."
)


class ReadyLifecycle:
    def require_ingestion_ready(self) -> None:
        return None

    def status(self):
        return {"ingestion_enabled": True}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_authority() -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I35-EVIDENCE-GENESIS-V1"},
        {"repository": REPOSITORY_ROOT.name, "source_id": SOURCE_ID},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id=SOURCE_ID,
                stage=CurriculumStage.REFERENCE,
                locator=f"evidence://{SOURCE_ID}",
                checksum_sha256=sha256(SOURCE).hexdigest(),
                rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
                source_authority="PASS218_I35_REPOSITORY_EVIDENCE",
                media_type="text/markdown",
            ),
        ),
    )
    return Pass218I33CurriculumAuthority(
        manifest=manifest,
        initial_cursor=CurriculumCursor.for_manifest(manifest),
    ).validated()


def build_candidate(authority: Pass218I33CurriculumAuthority):
    fake_seed = SimpleNamespace(
        genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        payload={"distinctions": []},
    )
    return NarrativeBeatHydrator(paragraphs_per_beat=1).hydrate(
        SOURCE.decode("utf-8"),
        source_id=SOURCE_ID,
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=compile_grammar_rules(GRAMMAR_PATH),
        expected_source_sha256=sha256(SOURCE).hexdigest(),
    )


def main() -> None:
    authority = build_authority()
    candidate = build_candidate(authority)
    with TemporaryDirectory(prefix="hhs-pass218-i35-evidence-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        i33_root = state_root / "cognition" / "curriculum-advance-i33"
        i34_root = state_root / "cognition" / "manifest-source-ingress-i34"
        i35_root = state_root / "cognition" / "manifest-semantic-source-transaction-i35"

        i34 = Pass218I34ManifestBoundSourceIngress(
            lifecycle=ReadyLifecycle(),
            authority=authority,
            i33_store_root=i33_root,
            ingress_store_root=i34_root,
        )
        ingress = i34.bind(source_id=SOURCE_ID, source_bytes=SOURCE)

        i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=ReadyLifecycle(),
            i34_store_root=i34_root,
            transaction_store_root=i35_root,
            manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
            i34_store=i34.store,
            i34_status_provider=i34.status,
        )
        receipt = i35.ingest(semantic_candidate=candidate, source_bytes=SOURCE)
        replay = i35.ingest(semantic_candidate=candidate, source_bytes=SOURCE)
        assert replay == receipt
        assert i35.i3_invocation_count == 1

        restarted = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=ReadyLifecycle(),
            i34_store_root=i34_root,
            transaction_store_root=i35_root,
            manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
            i34_store=i34.store,
            i34_status_provider=i34.status,
        )
        restart_receipt = restarted.ingest(
            semantic_candidate=candidate,
            source_bytes=SOURCE,
        )
        assert restart_receipt == receipt
        assert restarted.i3_invocation_count == 0
        snapshot = restarted.closed_transaction_snapshot()
        assert snapshot is not None
        assert snapshot["snapshot_hash72"] == receipt["i3_transaction_snapshot_hash72"]

        negative_candidate = candidate.to_record()
        negative_candidate["curriculum_identity_hash72"] = (
            authority.manifest.curriculum_identity_hash72
        )
        negative = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=ReadyLifecycle(),
            i34_store_root=i34_root,
            transaction_store_root=state_root / "negative-i35",
            manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
            i34_store=i34.store,
            i34_status_provider=i34.status,
        )
        try:
            negative.ingest(
                semantic_candidate=negative_candidate,
                source_bytes=SOURCE,
            )
        except Pass218I35BindingError as exc:
            negative_error = str(exc).split(":", 1)[0]
        else:
            raise AssertionError("P218_I35_CALLER_AUTHORITY_OVERRIDE_NOT_REJECTED")
        assert negative.i3_invocation_count == 0

        assert receipt["status"] == PASS218_I35_COMPLETE_STATUS
        assert receipt["i34_ingress_receipt_hash72"] == ingress["ingress_receipt_hash72"]
        assert receipt["manifest_binding"]["curriculum_identity_hash72"] == (
            authority.manifest.curriculum_identity_hash72
        )
        assert receipt["manifest_binding"]["source_id"] == SOURCE_ID
        assert receipt["manifest_binding"]["source_sha256"] == sha256(SOURCE).hexdigest()
        assert receipt["i3_source_transaction_invoked"] is True
        assert receipt["i3_transaction_closed"] is True
        assert receipt["i3_managed_buffer_zeroized"] is True
        assert receipt["i3_managed_buffer_cleared"] is True
        for field in (
            "pass218_i4_staging_invoked",
            "pass218_i5_promotion_invoked",
            "pass218_i30_canonical_semantic_promotion_invoked",
            "pass218_i31_verbatim_purge_invoked",
            "pass218_i32_source_closure_invoked",
            "curriculum_cursor_advanced",
            "stage_advance_permitted",
            "vm81_authorization_invoked",
            "truth_promotion",
            "action_authority_minted",
            "canonical_learning_commit_invoked",
            "model_activation_invoked",
            "authoritative_float_weights_created",
        ):
            assert receipt[field] is False

        payload = {
            "schema": "HHS-P218-I35-REPOSITORY-EVIDENCE-V1",
            "iteration": 35,
            "boundary_status": receipt["status"],
            "i34_ingress_receipt_hash72": ingress["ingress_receipt_hash72"],
            "manifest_bound_semantic_hash72": receipt["manifest_bound_semantic_hash72"],
            "i2_candidate_hash216": receipt["i2_candidate_hash216"],
            "i3_transaction_id_hash72": receipt["i3_transaction_id_hash72"],
            "i3_transaction_hash216": receipt["i3_transaction_hash216"],
            "i3_transaction_snapshot_hash72": receipt["i3_transaction_snapshot_hash72"],
            "i35_receipt_hash72": receipt["i35_receipt_hash72"],
            "i35_hash216": receipt["i35_hash216"],
            "manifest_binding": receipt["manifest_binding"],
            "same_process_replay_equal": replay == receipt,
            "same_process_i3_invocation_count": i35.i3_invocation_count,
            "restart_replay_equal": restart_receipt == receipt,
            "restart_i3_invocation_count": restarted.i3_invocation_count,
            "caller_manifest_override_rejected_before_i3": negative_error,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "later_pass218_authority_invoked": False,
            "authoritative_float_weights_created": False,
        }
        for field in (
            "i34_ingress_receipt_hash72",
            "manifest_bound_semantic_hash72",
            "i3_transaction_id_hash72",
            "i3_transaction_snapshot_hash72",
            "i35_receipt_hash72",
        ):
            assert validate_hash72(str(payload[field]))
        assert len(str(payload["i35_hash216"])) == 216
        encoded = canonical_bytes(payload)
        assert SOURCE not in encoded

        output = {
            "payload": payload,
            "payload_sha256": sha256(encoded).hexdigest(),
        }
        EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_ROOT / "evidence.json").write_bytes(
            json.dumps(
                output,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
            + b"\n"
        )
        print("PASS218_I35_EVIDENCE_SHA256=" + output["payload_sha256"])


if __name__ == "__main__":
    main()
