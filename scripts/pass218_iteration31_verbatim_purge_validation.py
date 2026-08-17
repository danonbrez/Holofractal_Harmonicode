#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 31 verbatim-purge evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from hhs_backend.runtime_os_pass218_narrative_beat_i24 import (
    Pass218I24RuntimeNarrativeBeatControl,
)
from hhs_backend.runtime_os_pass218_perspective_context_i25 import (
    Pass218I25RuntimePerspectiveContextControl,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_TARGET_SCOPE,
    Pass218I30AtomicSemanticPromoter,
    Pass218I30PromotionRequest,
)
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    Pass218I27DifferentiationRequest,
    Pass218I27FormalAnalogicalDifferentiator,
)
from hhs_runtime.pass218.grounded_manifold_i26 import (
    Pass218I26GroundedRelationalManifold,
    Pass218I26ManifoldRequest,
)
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    Pass218I28Hash216VM5184Transition,
    Pass218I28TransitionRequest,
)
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    Pass218I29Hash216VM5184Validator,
    Pass218I29ValidationRequest,
)
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
    Pass218I25PerspectiveRule,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGED_STATUS,
    PASS218_I31_QUARANTINED_STATUS,
    PASS218_I31_PURGE_SCOPE,
    Pass218I31PurgeConfirmationError,
    Pass218I31PurgeRequest,
    Pass218I31VerbatimPurger,
)
from scripts.pass218_iteration24_narrative_beat_validation import I23EvidenceAdapter

FROZEN_I29_VALIDATION_HASH72 = "/bxa0jML7*8!UqQ0LjiroLCArlYgT)Ur9E8(sn68+SUs7RBE-p(2FHnh32?716AnIUhpw0pJ"
FROZEN_I29_VALIDATED_HASH216 = (
    "t+NzrUXXE9*Y9R1GHAPkNggGY+T<*lErK3GO0MZuCrjaQk+Pm58d!2ipuEpnTiRSA0>?JihV"
    "xo0<eSBv>e2PolH3M!wkVcWiD2APYw!MpjGf//r/EHVVFWFSunq!7CFui>x?2NZ7IXTTkthS"
    "eVFpZQ<Pv/CZV13!lhL!H)CW15HxJcwXQtCd7PEWDeMptmG(Jf+mPaec1K2DU(qGNxxFTaYx"
)
FROZEN_I30_CANDIDATE_SHA256 = "ab505d8b6f5b01a459bd97d9b77b914683f797f2a3331215a5c220e8750e4a50"
FROZEN_I30_PROMOTED_OBJECT_HASH72 = "gH8TxIO06uAv4C(v47P<Ei)MU8//HrtOlhZIl-Q97DXJ+6Hp5XPiESRfz4!03t!uHYuiF<6*"
FROZEN_I30_CANONICAL_ROOT_HASH72 = "nzJ7a*nMe8g1o6e1PcV9rKpgWf(CLT3qJILeD!22i>lCzxTcvPIlh3n<ZPEERPvM*U69DqLj"
FROZEN_I30_PROMOTION_HASH72 = "hJN5OZpB+AWpz5i*Q!KEJwqrLWXFT+HL6)vB0DPgCdk3VTE!xiET(Z<lzY?<MeIdr5PkR/Mv"
FROZEN_I30_PROMOTION_RECEIPT_HASH72 = "3vZ5j(HOt*FjP/fMJ0ZVWhc8BH>uYEN/zsDgo)9pYtg5MbieofrU*G?ldhMh)RwrKv3zKttU"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_frozen_chain(repository_root: Path):
    source_path = (
        repository_root
        / "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md"
    )
    source_bytes = source_path.read_bytes()
    source_sha256 = sha256(source_bytes).hexdigest()
    del source_bytes

    curriculum_identity_hash72 = hash72_digest(
        {"domain": "HHS-P218-I29-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 29,
            "authoritative_curriculum_advance": False,
        },
    )
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I29-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "HASH216_VM5184_VALIDATION_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )
    rule_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I29-EVIDENCE-PERSPECTIVE-RULE-V1"},
        {
            "principle": "VALIDATE_NATIVE_TRANSITION_WITHOUT_PROMOTION",
            "hash216_validation_receipt_required": True,
            "vm5184_projection_rederivation_required": True,
            "atomic_promotion_deferred": True,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    i24 = Pass218I24RuntimeNarrativeBeatControl(i23)
    i25 = Pass218I25RuntimePerspectiveContextControl(i24)
    i26 = Pass218I26GroundedRelationalManifold(i25)
    i27 = Pass218I27FormalAnalogicalDifferentiator(i26)
    i28 = Pass218I28Hash216VM5184Transition(i27)
    i29 = Pass218I29Hash216VM5184Validator(i28, i27)

    beat_request = Pass218I24BeatRequest(
        tokens=("relational", "grounding", "context"),
        context_id="pass218 hash216 vm5184 validation contract",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=29,
        source_id=source_path.name,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i29-hash216-vm5184-validation-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("relational", "grounding"),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=16,
    ).validated()
    profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-validation-perspective",
        profile_version="i29-v1",
        profile_origin="USER_AUTHORED",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-validation-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()
    perspective = Pass218I25PerspectiveRequest(beat_request, profile).validated()
    manifold = Pass218I26ManifoldRequest(perspective).validated()
    differentiation = Pass218I27DifferentiationRequest(manifold).validated()
    transition = Pass218I28TransitionRequest(differentiation).validated()
    validation_request = Pass218I29ValidationRequest(transition).validated()

    frozen_validation = i29.validate(validation_request)
    assert frozen_validation["hash216_vm5184_validation_hash72"] == FROZEN_I29_VALIDATION_HASH72
    assert frozen_validation["pass218_validated_hash216"] == FROZEN_I29_VALIDATED_HASH216
    assert frozen_validation["relation_count"] == 14

    grantor_authority_hash72 = hash72_digest(
        {"domain": "HHS-P218-I30-EVIDENCE-PROMOTION-AUTHORITY-V1"},
        {
            "source_sha256": source_sha256,
            "i29_validation_hash72": FROZEN_I29_VALIDATION_HASH72,
            "validated_hash216": FROZEN_I29_VALIDATED_HASH216,
            "target_scope": PASS218_I30_TARGET_SCOPE,
            "grant_sequence": 30,
        },
    )
    promotion_request = Pass218I30PromotionRequest(
        validation_request=validation_request,
        grantor_authority_hash72=grantor_authority_hash72,
        grant_sequence=30,
        expected_i29_validation_hash72=FROZEN_I29_VALIDATION_HASH72,
        expected_validated_hash216=FROZEN_I29_VALIDATED_HASH216,
        target_scope=PASS218_I30_TARGET_SCOPE,
    ).validated()
    return source_sha256, i27, i29, promotion_request, frozen_validation


def make_purge_request(promotion: dict[str, object]) -> Pass218I31PurgeRequest:
    return Pass218I31PurgeRequest(
        expected_i30_promotion_receipt_hash72=str(
            promotion["promotion_receipt_hash72"]
        ),
        expected_i30_promotion_hash72=str(promotion["promotion_hash72"]),
        expected_promoted_object_hash72=str(promotion["promoted_object_hash72"]),
        expected_canonical_root_hash72=str(promotion["target_root_after_hash72"]),
        expected_i29_validation_hash72=str(promotion["i29_validation_hash72"]),
        purge_scope=PASS218_I31_PURGE_SCOPE,
    ).validated()


def promote_exact_i30(
    state_root: Path,
    lifecycle: Pass218MultiprocessRuntimeLifecycle,
    i29: Pass218I29Hash216VM5184Validator,
    i27: Pass218I27FormalAnalogicalDifferentiator,
    promotion_request: Pass218I30PromotionRequest,
) -> tuple[Pass218I30AtomicSemanticPromoter, dict[str, object]]:
    promoter = Pass218I30AtomicSemanticPromoter(
        i29,
        i27,
        lifecycle=lifecycle,
        store_root=state_root / "cognition" / "atomic-semantic-promotion-i30",
    )
    promotion = promoter.promote(promotion_request)
    assert promotion["candidate_sha256"] == FROZEN_I30_CANDIDATE_SHA256
    assert promotion["promoted_object_hash72"] == FROZEN_I30_PROMOTED_OBJECT_HASH72
    assert promotion["target_root_after_hash72"] == FROZEN_I30_CANONICAL_ROOT_HASH72
    assert promotion["promotion_hash72"] == FROZEN_I30_PROMOTION_HASH72
    assert promotion["promotion_receipt_hash72"] == FROZEN_I30_PROMOTION_RECEIPT_HASH72
    return promoter, promotion


def main() -> None:
    repository_root = Path.cwd().resolve()
    source_sha256, i27, i29, promotion_request, frozen_validation = build_frozen_chain(
        repository_root
    )

    with TemporaryDirectory(prefix="hhs-pass218-i31-success-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        assert startup["ownership_writer_authority"] is True
        try:
            promoter, promotion = promote_exact_i30(
                state_root, lifecycle, i29, i27, promotion_request
            )
            purger = Pass218I31VerbatimPurger(
                lifecycle=lifecycle,
                i30_store_root=promoter.store.root,
                purge_store_root=state_root / "cognition" / "verbatim-purge-i31",
            )
            purge_request = make_purge_request(promotion)
            first = purger.purge(purge_request)
            replay = purger.purge(purge_request)
            assert first == replay
            status = purger.status()

            assert first["purge_status"] == PASS218_I31_PURGED_STATUS
            assert first["purge_mode"] == "MANAGED_BUFFER_ABSENCE_PROOF"
            assert first["managed_buffer_count_before"] == 0
            assert first["managed_buffer_count_after"] == 0
            assert first["managed_buffers_absent_before"] is True
            assert first["managed_buffers_absent_after"] is True
            assert first["managed_buffer_zeroization_performed"] is False
            assert first["durable_nonverbatim_store_verified"] is True
            assert first["verbatim_purge_invoked"] is True
            assert first["purge_confirmation_verified"] is True
            assert first["purge_receipt_issued"] is True
            assert first["quarantined"] is False
            assert first["curriculum_advance_permitted"] is False
            assert first["closure_invoked"] is False
            assert first["truth_promotion"] is False
            assert first["action_authority_minted"] is False
            assert first["canonical_learning_commit_invoked"] is False
            assert first["model_activation_invoked"] is False
            assert first["verbatim_corpus_source_retained"] is False
            assert first["physical_memory_erasure_claimed"] is False
            assert first["external_source_storage_erasure_claimed"] is False
            assert first["authoritative_float_weights_created"] is False
            assert validate_hash72(first["purge_validation_hash72"])
            assert validate_hash72(first["purge_receipt_hash72"])
            assert validate_hash72(first["purge_gate_root_hash72"])
            assert len(first["purge_hash216"]) == 216
            assert all(
                validate_hash72(first["purge_hash216"][start:start + 72])
                for start in (0, 72, 144)
            )
            assert first["purge_hash216"].startswith(FROZEN_I30_PROMOTION_HASH72)
            assert status["purge_receipt_issued"] is True
            assert status["purge_confirmation_verified"] is True
            assert status["curriculum_advance_permitted"] is False
            assert status["closure_invoked"] is False

            success_evidence = {
                "i31_purge_validation_hash72": first["purge_validation_hash72"],
                "i31_purge_receipt_hash72": first["purge_receipt_hash72"],
                "i31_purge_hash216": first["purge_hash216"],
                "i31_purge_gate_root_hash72": first["purge_gate_root_hash72"],
                "i31_durability_witness_hash72": first["durability_witness_hash72"],
                "i31_persisted_inventory_hash72": first[
                    "persisted_inventory_hash72"
                ],
                "purge_mode": first["purge_mode"],
                "deterministic_replay_equal": True,
                "purge_receipt_issued": True,
                "purge_confirmation_verified": True,
                "durable_nonverbatim_store_verified": True,
            }
        finally:
            lifecycle.shutdown()

    with TemporaryDirectory(prefix="hhs-pass218-i31-quarantine-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        try:
            promoter, promotion = promote_exact_i30(
                state_root, lifecycle, i29, i27, promotion_request
            )
            purger = Pass218I31VerbatimPurger(
                lifecycle=lifecycle,
                i30_store_root=promoter.store.root,
                purge_store_root=state_root / "cognition" / "verbatim-purge-i31",
            )
            purge_request = make_purge_request(promotion)
            try:
                purger.purge(purge_request, force_confirmation_failure=True)
            except Pass218I31PurgeConfirmationError as exc:
                assert str(exc) == "P218_I31_INJECTED_PURGE_CONFIRMATION_FAILURE"
            else:
                raise AssertionError("injected purge confirmation failure was not rejected")
            quarantine_status = purger.status()
            assert quarantine_status["purge_status"] == PASS218_I31_QUARANTINED_STATUS
            assert quarantine_status["quarantined"] is True
            assert quarantine_status["purge_receipt_issued"] is False
            assert quarantine_status["purge_confirmation_verified"] is False
            assert quarantine_status["curriculum_advance_permitted"] is False
            assert quarantine_status["closure_invoked"] is False
            quarantine_record = purger.store.active_record()
            assert quarantine_record is not None
            quarantine_evidence = {
                "quarantine_hash72": quarantine_record["quarantine_hash72"],
                "quarantine_reason_code": quarantine_record["reason_code"],
                "quarantine_receipt_issued": quarantine_record[
                    "purge_receipt_issued"
                ],
                "quarantine_curriculum_advance_permitted": quarantine_record[
                    "curriculum_advance_permitted"
                ],
            }
        finally:
            lifecycle.shutdown()

    payload = {
        "schema": "HHS-P218-I31-EVIDENCE-V1",
        "iteration": 31,
        "source_sha256": source_sha256,
        "relation_count": frozen_validation["relation_count"],
        "frozen_i29_validation_hash72": FROZEN_I29_VALIDATION_HASH72,
        "frozen_i29_validated_hash216": FROZEN_I29_VALIDATED_HASH216,
        "frozen_i30_candidate_sha256": FROZEN_I30_CANDIDATE_SHA256,
        "frozen_i30_promoted_object_hash72": FROZEN_I30_PROMOTED_OBJECT_HASH72,
        "frozen_i30_canonical_root_hash72": FROZEN_I30_CANONICAL_ROOT_HASH72,
        "frozen_i30_promotion_hash72": FROZEN_I30_PROMOTION_HASH72,
        "frozen_i30_promotion_receipt_hash72": FROZEN_I30_PROMOTION_RECEIPT_HASH72,
        "writer_fence_real_i9_lifecycle": True,
        **success_evidence,
        **quarantine_evidence,
        "managed_buffer_absence_proven": True,
        "verbatim_purge_invoked": True,
        "curriculum_advance_permitted": False,
        "closure_invoked": False,
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
    output_root = Path(".i31-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration31_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration31_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
