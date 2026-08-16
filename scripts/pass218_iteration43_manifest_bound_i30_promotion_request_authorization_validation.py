#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 43."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.manifest_bound_i30_promotion_request_authorization_i43 import (
    PASS218_I43_AUTHORIZED_PENDING_STATUS,
    PASS218_I43_COMPLETE_STATUS,
    PASS218_I43_VERSION,
    Pass218I43ManifestBoundI30PromotionRequestAuthorization,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / ".i43-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration43_evidence.json"


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
            / "test_pass218_iteration43_manifest_bound_i30_promotion_request_authorization.py"
        )
    )
    source = (
        b"Pass 218 Iteration 43 binds a separate explicit frozen-I30 authority grant "
        b"to the exact I42 request fingerprint and independently replayed I29 identity, "
        b"without invoking I30 promotion."
    )
    transient_marker = "I43 evidence transient request marker 932bce must not persist"
    with TemporaryDirectory(prefix="hhs-p218-i43-") as temporary:
        root = Path(temporary)
        (
            _,
            lifecycle,
            _,
            validator,
            validation_request,
            i42,
            i42_receipt,
        ) = helpers["prepare_i42"](
            root,
            source=source,
            context_id=transient_marker,
        )
        request = helpers["promotion_request"](validation_request, i42_receipt)
        first = helpers["make_i43"](root, lifecycle, i42, validator)
        receipt = first.authorize(request)
        proof = first.store.active_proof()
        assert proof is not None
        same_process = first.authorize(request)
        assert same_process == receipt
        i30_status = helpers["FakeI30Runtime"]()
        restarted = Pass218I43ManifestBoundI30PromotionRequestAuthorization(
            lifecycle=lifecycle,
            i42_store=i42.store,
            i29_validator=validator,
            state_root=(
                root
                / "state"
                / "cognition"
                / "manifest-bound-i30-promotion-request-authorization-i43"
            ),
            i42_status_provider=i42.status,
            i30_status_provider=i30_status.status,
        )
        restarted_receipt = restarted.authorize(request)
        assert restarted_receipt == receipt
        assert receipt["status"] == PASS218_I43_COMPLETE_STATUS
        assert receipt["authorization_status"] == PASS218_I43_AUTHORIZED_PENDING_STATUS
        assert receipt["target_surface"] == PASS218_I30_TARGET_SCOPE
        assert receipt["i42_exact_request_identity_bound"] is True
        assert receipt["i29_independently_revalidated"] is True
        assert receipt["i30_explicit_authority_grant_present"] is True
        assert receipt["i30_grant_hash_matches_frozen_i30_derivation"] is True
        assert receipt["i30_promotion_request_authorized"] is True
        assert receipt["authorized_pending_i30_invocation"] is True
        assert receipt["pass218_i30_canonical_semantic_promotion_invoked"] is False
        assert receipt["vm5184_authoritative_projection_invoked"] is False
        assert first.i30_invocation_count == 0
        assert restarted.i30_invocation_count == 0
        assert validator.validation_count == 2
        assert proof["i29_validation_request_sha256"] == i42_receipt[
            "i29_validation_request_sha256"
        ]
        assert proof["i30_grant_hash72"] == receipt["i30_grant_hash72"]
        for path in first.store.root.rglob("*"):
            if path.is_file():
                payload = path.read_bytes()
                assert source not in payload
                assert transient_marker.encode("utf-8") not in payload
                assert b"context_id" not in payload
                assert b'"tokens"' not in payload
                assert b'"validation_request"' not in payload
        evidence = {
            "schema": "HHS-P218-I43-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I43_VERSION,
            "status": receipt["status"],
            "authorization_status": receipt["authorization_status"],
            "i42_receipt_hash72": receipt["i42_receipt_hash72"],
            "i42_cross_lineage_equality_hash72": receipt[
                "i42_cross_lineage_equality_hash72"
            ],
            "i29_validation_request_sha256": receipt[
                "i29_validation_request_sha256"
            ],
            "i30_promotion_request_sha256": receipt[
                "i30_promotion_request_sha256"
            ],
            "i29_validation_hash72": receipt["i29_validation_hash72"],
            "i29_validated_hash216": receipt["i29_validated_hash216"],
            "grantor_authority_hash72": receipt["grantor_authority_hash72"],
            "grant_sequence": receipt["grant_sequence"],
            "i30_grant_hash72": receipt["i30_grant_hash72"],
            "manifest_bound_i30_request_authorization_hash72": receipt[
                "manifest_bound_i30_request_authorization_hash72"
            ],
            "i43_validation_hash72": receipt["i43_validation_hash72"],
            "i43_receipt_hash72": receipt["i43_receipt_hash72"],
            "i43_hash216": receipt["i43_hash216"],
            "shared_identity": proof["shared_identity"],
            "i29_semantic_witness_hash72": proof["i29_semantic_witness_hash72"],
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_authorizations": first.authorization_count,
            "restart_process_authorizations": restarted.authorization_count,
            "i29_validations_total_including_i42": validator.validation_count,
            "i30_invocations": first.i30_invocation_count + restarted.i30_invocation_count,
            "i42_exact_request_identity_bound": True,
            "i30_explicit_authority_grant_present": True,
            "i30_grant_hash_matches_frozen_i30_derivation": True,
            "i30_promotion_request_authorized": True,
            "authorized_pending_i30_invocation": True,
            "i29_validation_request_persisted": False,
            "i30_promotion_request_persisted": False,
            "vm5184_authoritative_projection_invoked": False,
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
    print("PASS218_I43_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
