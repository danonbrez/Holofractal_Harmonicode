#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 32 source-closure evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSED_STATUS,
    PASS218_I32_CLOSURE_SCOPE,
    Pass218I32ClosureRequest,
    Pass218I32ClosureValidationError,
    Pass218I32SourceCloser,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGED_STATUS,
    Pass218I31VerbatimPurger,
)
from scripts.pass218_iteration31_verbatim_purge_validation import (
    FROZEN_I29_VALIDATED_HASH216,
    FROZEN_I29_VALIDATION_HASH72,
    FROZEN_I30_CANDIDATE_SHA256,
    FROZEN_I30_CANONICAL_ROOT_HASH72,
    FROZEN_I30_PROMOTED_OBJECT_HASH72,
    FROZEN_I30_PROMOTION_HASH72,
    FROZEN_I30_PROMOTION_RECEIPT_HASH72,
    build_frozen_chain,
    canonical_bytes,
    make_purge_request,
    promote_exact_i30,
)

FROZEN_I31_PURGE_VALIDATION_HASH72 = "bSyXs*6kx7)CyoBc>HVM-LibwV3Qi20VsIE-ld6Kr*2M+Z2k)3TLLNxPh+k5b2t6(EN??PH<"
FROZEN_I31_PURGE_RECEIPT_HASH72 = "/O2Fb4ep?-CN31xw4Lw(vRSe1(3jJBZbpLQAkcQ2cF<2Ldv0ukX33DpdKvz35MYf2nMRwAhH"
FROZEN_I31_PURGE_GATE_ROOT_HASH72 = "+PPjaYe+Z*?XQu(Rg8*6(br+Eh)2)vdFhV0qMUPBbN7cPzc80N(R7xfh-1C0BM>9q+kR1<ks"
FROZEN_I31_PURGE_HASH216 = (
    FROZEN_I30_PROMOTION_HASH72
    + FROZEN_I31_PURGE_VALIDATION_HASH72
    + FROZEN_I31_PURGE_RECEIPT_HASH72
)
SOURCE_NAME = "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md"


def make_closure_request(source_sha256: str, purge: dict[str, object]) -> Pass218I32ClosureRequest:
    curriculum_identity_hash72 = hash72_digest(
        {"domain": "HHS-P218-I29-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 29,
            "authoritative_curriculum_advance": False,
        },
    )
    return Pass218I32ClosureRequest(
        expected_i31_purge_receipt_hash72=str(purge["purge_receipt_hash72"]),
        expected_i31_purge_validation_hash72=str(purge["purge_validation_hash72"]),
        expected_i31_purge_gate_root_hash72=str(purge["purge_gate_root_hash72"]),
        expected_i31_purge_hash216=str(purge["purge_hash216"]),
        expected_i30_promotion_receipt_hash72=str(
            purge["i30_promotion_receipt_hash72"]
        ),
        expected_promoted_object_hash72=str(purge["promoted_object_hash72"]),
        expected_canonical_root_hash72=str(purge["canonical_root_hash72"]),
        source_id=SOURCE_NAME,
        source_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=29,
        source_stage=2,
        previous_closure_hash72=None,
        closure_scope=PASS218_I32_CLOSURE_SCOPE,
    ).validated()


def main() -> None:
    repository_root = Path.cwd().resolve()
    source_sha256, i27, i29, promotion_request, frozen_validation = build_frozen_chain(
        repository_root
    )

    with TemporaryDirectory(prefix="hhs-pass218-i32-success-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        assert startup["ownership_writer_authority"] is True
        try:
            promoter, promotion = promote_exact_i30(
                state_root, lifecycle, i29, i27, promotion_request
            )
            i31_root = state_root / "cognition" / "verbatim-purge-i31"
            purger = Pass218I31VerbatimPurger(
                lifecycle=lifecycle,
                i30_store_root=promoter.store.root,
                purge_store_root=i31_root,
            )
            purge = purger.purge(make_purge_request(promotion))
            assert purge["purge_status"] == PASS218_I31_PURGED_STATUS
            assert purge["purge_validation_hash72"] == FROZEN_I31_PURGE_VALIDATION_HASH72
            assert purge["purge_receipt_hash72"] == FROZEN_I31_PURGE_RECEIPT_HASH72
            assert purge["purge_gate_root_hash72"] == FROZEN_I31_PURGE_GATE_ROOT_HASH72
            assert purge["purge_hash216"] == FROZEN_I31_PURGE_HASH216

            closer = Pass218I32SourceCloser(
                lifecycle=lifecycle,
                i31_store_root=i31_root,
                closure_store_root=state_root / "cognition" / "source-closure-i32",
            )
            request = make_closure_request(source_sha256, purge)
            first = closer.close(request)
            replay = closer.close(request)
            assert first == replay
            assert first["closure_status"] == PASS218_I32_CLOSED_STATUS
            assert first["closure_invoked"] is True
            assert first["source_closed"] is True
            assert first["i31_purge_receipt_hash72"] == FROZEN_I31_PURGE_RECEIPT_HASH72
            assert first["i31_purge_gate_root_hash72"] == FROZEN_I31_PURGE_GATE_ROOT_HASH72
            assert first["source_sha256"] == source_sha256
            assert first["source_id"] == SOURCE_NAME
            assert first["previous_closure_hash72"] is None
            assert first["source_binding_requires_curriculum_match_before_advance"] is True
            assert first["curriculum_advance_permitted"] is False
            assert first["curriculum_cursor_advanced"] is False
            assert first["stage_advance_permitted"] is False
            assert first["vm81_authorization_invoked"] is False
            assert first["truth_promotion"] is False
            assert first["action_authority_minted"] is False
            assert first["canonical_learning_commit_invoked"] is False
            assert first["model_activation_invoked"] is False
            assert first["verbatim_corpus_source_retained"] is False
            assert first["physical_memory_erasure_claimed"] is False
            assert first["external_source_storage_erasure_claimed"] is False
            assert first["authoritative_float_weights_created"] is False
            assert validate_hash72(first["source_id_hash72"])
            assert validate_hash72(first["source_binding_hash72"])
            assert validate_hash72(first["closure_validation_hash72"])
            assert validate_hash72(first["source_closure_hash72"])
            assert validate_hash72(first["closure_chain_root_hash72"])
            assert len(first["closure_hash216"]) == 216
            assert all(
                validate_hash72(first["closure_hash216"][start:start + 72])
                for start in (0, 72, 144)
            )
            assert first["closure_hash216"].startswith(FROZEN_I31_PURGE_RECEIPT_HASH72)

            restarted = Pass218I32SourceCloser(
                lifecycle=lifecycle,
                i31_store_root=i31_root,
                closure_store_root=state_root / "cognition" / "source-closure-i32",
            )
            assert restarted.close(request) == first
            status = restarted.status()
            assert status["source_closed"] is True
            assert status["curriculum_advance_permitted"] is False
            success_evidence = {
                "i32_source_id_hash72": first["source_id_hash72"],
                "i32_source_binding_hash72": first["source_binding_hash72"],
                "i32_closure_validation_hash72": first["closure_validation_hash72"],
                "i32_source_closure_hash72": first["source_closure_hash72"],
                "i32_closure_hash216": first["closure_hash216"],
                "i32_closure_chain_root_hash72": first["closure_chain_root_hash72"],
                "i32_curriculum_identity_hash72": first["curriculum_identity_hash72"],
                "deterministic_replay_equal": True,
                "restart_replay_equal": True,
            }
        finally:
            lifecycle.shutdown()

    with TemporaryDirectory(prefix="hhs-pass218-i32-negative-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        try:
            closer = Pass218I32SourceCloser(
                lifecycle=lifecycle,
                i31_store_root=state_root / "cognition" / "missing-i31",
                closure_store_root=state_root / "cognition" / "source-closure-i32",
            )
            fake_purge = {
                "purge_receipt_hash72": FROZEN_I31_PURGE_RECEIPT_HASH72,
                "purge_validation_hash72": FROZEN_I31_PURGE_VALIDATION_HASH72,
                "purge_gate_root_hash72": FROZEN_I31_PURGE_GATE_ROOT_HASH72,
                "purge_hash216": FROZEN_I31_PURGE_HASH216,
                "i30_promotion_receipt_hash72": FROZEN_I30_PROMOTION_RECEIPT_HASH72,
                "promoted_object_hash72": FROZEN_I30_PROMOTED_OBJECT_HASH72,
                "canonical_root_hash72": FROZEN_I30_CANONICAL_ROOT_HASH72,
            }
            try:
                closer.close(make_closure_request(source_sha256, fake_purge))
            except Pass218I32ClosureValidationError as exc:
                assert str(exc) == "P218_I32_I31_PURGE_RECEIPT_REQUIRED"
            else:
                raise AssertionError("closure without durable I31 purge receipt was not rejected")
            assert closer.store.active_record() is None
            negative_evidence = {
                "closure_without_i31_rejected": True,
                "negative_curriculum_advance_permitted": False,
            }
        finally:
            lifecycle.shutdown()

    payload = {
        "schema": "HHS-P218-I32-EVIDENCE-V1",
        "iteration": 32,
        "source_sha256": source_sha256,
        "source_id": SOURCE_NAME,
        "relation_count": frozen_validation["relation_count"],
        "frozen_i29_validation_hash72": FROZEN_I29_VALIDATION_HASH72,
        "frozen_i29_validated_hash216": FROZEN_I29_VALIDATED_HASH216,
        "frozen_i30_candidate_sha256": FROZEN_I30_CANDIDATE_SHA256,
        "frozen_i30_promoted_object_hash72": FROZEN_I30_PROMOTED_OBJECT_HASH72,
        "frozen_i30_canonical_root_hash72": FROZEN_I30_CANONICAL_ROOT_HASH72,
        "frozen_i30_promotion_hash72": FROZEN_I30_PROMOTION_HASH72,
        "frozen_i30_promotion_receipt_hash72": FROZEN_I30_PROMOTION_RECEIPT_HASH72,
        "frozen_i31_purge_validation_hash72": FROZEN_I31_PURGE_VALIDATION_HASH72,
        "frozen_i31_purge_receipt_hash72": FROZEN_I31_PURGE_RECEIPT_HASH72,
        "frozen_i31_purge_gate_root_hash72": FROZEN_I31_PURGE_GATE_ROOT_HASH72,
        "frozen_i31_purge_hash216": FROZEN_I31_PURGE_HASH216,
        "writer_fence_real_i9_lifecycle": True,
        **success_evidence,
        **negative_evidence,
        "closure_invoked": True,
        "source_closed": True,
        "source_binding_requires_curriculum_match_before_advance": True,
        "curriculum_advance_permitted": False,
        "curriculum_cursor_advanced": False,
        "stage_advance_permitted": False,
        "vm81_authorization_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "physical_memory_erasure_claimed": False,
        "external_source_storage_erasure_claimed": False,
        "authoritative_float_weights_created": False,
    }

    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i32-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration32_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration32_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
