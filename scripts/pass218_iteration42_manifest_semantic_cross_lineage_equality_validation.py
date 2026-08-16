#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 42."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.manifest_semantic_cross_lineage_equality_i42 import (
    PASS218_I42_COMPLETE_STATUS,
    PASS218_I42_VERSION,
    Pass218I42ManifestSemanticCrossLineageEquality,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / ".i42-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration42_evidence.json"


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def main() -> int:
    helpers = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "pass218"
            / "test_pass218_iteration42_manifest_semantic_cross_lineage_equality.py"
        )
    )
    make_i41 = helpers["make_i41"]
    make_i42 = helpers["make_i42"]
    validation_request = helpers["validation_request"]
    FakeI29Validator = helpers["FakeI29Validator"]
    source = (
        b"Pass 218 Iteration 42 proves exact equality across the shared manifest "
        b"and source identity carried independently by durable I41 canonical ingress "
        b"and frozen I27 through I29 semantic validation, without invoking I30."
    )
    transient_marker = "I42 evidence transient request marker e3047d must not persist"
    with TemporaryDirectory(prefix="hhs-p218-i42-") as temporary:
        root = Path(temporary)
        lifecycle, authority, i41 = make_i41(root, source)
        validator = FakeI29Validator()
        request = validation_request(
            source,
            authority,
            context_id=transient_marker,
        )
        first = make_i42(root, lifecycle, i41, validator)
        receipt = first.prove(request)
        proof = first.store.active_proof()
        assert proof is not None
        same_process = first.prove(request)
        assert same_process == receipt
        restarted = Pass218I42ManifestSemanticCrossLineageEquality(
            lifecycle=lifecycle,
            i41_store=i41.store,
            i29_validator=validator,
            state_root=(
                root
                / "state"
                / "cognition"
                / "manifest-semantic-cross-lineage-equality-i42"
            ),
            i41_status_provider=i41.status,
            i30_status_provider=helpers["EmptyI30"]().status,
        )
        restarted_receipt = restarted.prove(request)
        assert restarted_receipt == receipt
        assert receipt["status"] == PASS218_I42_COMPLETE_STATUS
        assert receipt["target_surface"] == PASS218_I30_TARGET_SCOPE
        assert receipt["cross_lineage_shared_identity_equal"] is True
        assert receipt["i29_independently_revalidated"] is True
        assert receipt["i30_exact_validation_identity_ready"] is True
        assert receipt["i30_request_synthesized"] is False
        assert receipt["i30_authority_grant_present"] is False
        assert receipt["pass218_i30_canonical_semantic_promotion_invoked"] is False
        assert first.i30_invocation_count == 0
        assert validator.validation_count == 1
        assert proof["shared_identity"]["curriculum_identity_hash72"] == (
            authority.manifest.curriculum_identity_hash72
        )
        assert proof["shared_identity"]["source_sha256"] == sha256(source).hexdigest()
        assert proof["i29_curriculum_hash72"] == authority.manifest.curriculum_identity_hash72
        assert proof["canonical_and_semantic_roots_kept_distinct"] is True
        for path in first.store.root.rglob("*"):
            if path.is_file():
                payload = path.read_bytes()
                assert source not in payload
                assert transient_marker.encode("utf-8") not in payload
                assert b"context_id" not in payload
                assert b"tokens" not in payload
        evidence = {
            "schema": "HHS-P218-I42-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I42_VERSION,
            "status": receipt["status"],
            "i41_receipt_hash72": receipt["i41_receipt_hash72"],
            "cross_lineage_equality_hash72": receipt["cross_lineage_equality_hash72"],
            "i29_validation_request_sha256": receipt["i29_validation_request_sha256"],
            "i29_validation_hash72": receipt["i29_validation_hash72"],
            "i29_validated_hash216": receipt["i29_validated_hash216"],
            "i42_validation_hash72": receipt["i42_validation_hash72"],
            "i42_receipt_hash72": receipt["i42_receipt_hash72"],
            "i42_hash216": receipt["i42_hash216"],
            "shared_identity": proof["shared_identity"],
            "i40_canonical_root_hash72": proof["i40_canonical_root_hash72"],
            "i29_curriculum_hash72": proof["i29_curriculum_hash72"],
            "i29_transition_state_hash72": proof["i29_transition_state_hash72"],
            "i29_validation_receipt_hash72": proof["i29_validation_receipt_hash72"],
            "i29_semantic_witness_hash72": proof["i29_semantic_witness_hash72"],
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_proofs": first.proof_count,
            "restart_process_proofs": restarted.proof_count,
            "i29_validations": validator.validation_count,
            "i30_invocations": first.i30_invocation_count + restarted.i30_invocation_count,
            "cross_lineage_shared_identity_equal": True,
            "canonical_and_semantic_roots_kept_distinct": True,
            "i29_validation_request_persisted": False,
            "i30_request_synthesized": False,
            "i30_authority_grant_present": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
            "verbatim_corpus_source_retained": False,
        }
    payload = canonical_bytes(evidence)
    digest = sha256(payload).hexdigest()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(payload + b"\n")
    print("PASS218_I42_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
