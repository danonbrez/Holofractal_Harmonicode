#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 30 atomic-promotion evidence."""
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
    PASS218_I30_PENDING_PURGE_STATUS,
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
from scripts.pass218_iteration24_narrative_beat_validation import I23EvidenceAdapter

FROZEN_I29_VALIDATION_HASH72 = "/bxa0jML7*8!UqQ0LjiroLCArlYgT)Ur9E8(sn68+SUs7RBE-p(2FHnh32?716AnIUhpw0pJ"
FROZEN_I29_VALIDATED_HASH216 = (
    "t+NzrUXXE9*Y9R1GHAPkNggGY+T<*lErK3GO0MZuCrjaQk+Pm58d!2ipuEpnTiRSA0>?JihV"
    "xo0<eSBv>e2PolH3M!wkVcWiD2APYw!MpjGf//r/EHVVFWFSunq!7CFui>x?2NZ7IXTTkthS"
    "eVFpZQ<Pv/CZV13!lhL!H)CW15HxJcwXQtCd7PEWDeMptmG(Jf+mPaec1K2DU(qGNxxFTaYx"
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def main() -> None:
    repository_root = Path.cwd().resolve()
    source_path = (
        repository_root
        / "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md"
    )
    source_sha256 = sha256(source_path.read_bytes()).hexdigest()

    # Reconstruct the exact frozen I29 evidence candidate rather than changing
    # curriculum/profile identity at the promotion boundary.
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
    assert frozen_validation["formal_semantic_round_trip_verified"] is False
    assert frozen_validation["atomic_promotion_candidate_ready"] is True
    assert frozen_validation["atomic_promotion_authorized"] is False

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

    with TemporaryDirectory(prefix="hhs-pass218-i30-evidence-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        assert startup["ownership_writer_authority"] is True
        try:
            promoter = Pass218I30AtomicSemanticPromoter(
                i29,
                i27,
                lifecycle=lifecycle,
                store_root=state_root / "cognition" / "atomic-semantic-promotion-i30",
            )
            first = promoter.promote(promotion_request)
            replay = promoter.promote(promotion_request)
            assert first == replay
            status = promoter.status()
            active = promoter.store.active_generation()
            assert active is not None
            promoted = active["promoted_object"]
            serialized_promoted = canonical_bytes(promoted)

            assert first["promotion_status"] == PASS218_I30_PENDING_PURGE_STATUS
            assert first["formal_semantic_round_trip_verified"] is True
            assert first["grounded_round_trip_verified"] is True
            assert first["perspective_round_trip_verified"] is True
            assert first["candidate_commit_verified"] is True
            assert first["prospective_root_verified"] is True
            assert first["atomic_manifest_swap"] is True
            assert first["failed_partial_promotion_possible"] is False
            assert first["vm5184_authoritative_projection_invoked"] is True
            assert first["vm5184_authoritative_state_committed"] is True
            assert first["vm81_authorization_invoked"] is False
            assert first["atomic_promotion_authorized"] is True
            assert first["atomic_promotion_invoked"] is True
            assert first["purge_status"] == "PENDING_VERBATIM_PURGE"
            assert first["verbatim_purge_invoked"] is False
            assert first["purge_receipt_issued"] is False
            assert first["curriculum_advance_permitted"] is False
            assert first["closure_invoked"] is False
            assert first["truth_promotion"] is False
            assert first["action_authority_minted"] is False
            assert first["canonical_learning_commit_invoked"] is False
            assert first["model_activation_invoked"] is False
            assert first["verbatim_corpus_source_retained"] is False
            assert first["authoritative_float_weights_created"] is False
            assert promoted["source_text_retained"] is False
            assert promoted["source_token_stream_retained"] is False
            assert b'"attention_tokens"' not in serialized_promoted
            assert b'"source_token"' not in serialized_promoted
            assert b'"target_token"' not in serialized_promoted
            assert status["promotion_present"] is True
            assert status["canonical_root_hash72"] == first["target_root_after_hash72"]
            assert status["purge_receipt_issued"] is False
            assert status["curriculum_advance_permitted"] is False

            payload = {
                "schema": "HHS-P218-I30-EVIDENCE-V1",
                "iteration": 30,
                "source_sha256": source_sha256,
                "frozen_i29_validation_hash72": FROZEN_I29_VALIDATION_HASH72,
                "frozen_i29_validated_hash216": FROZEN_I29_VALIDATED_HASH216,
                "grantor_authority_hash72": grantor_authority_hash72,
                "grant_hash72": first["grant_hash72"],
                "candidate_sha256": first["candidate_sha256"],
                "promoted_object_hash72": first["promoted_object_hash72"],
                "target_root_before_hash72": first["target_root_before_hash72"],
                "target_root_after_hash72": first["target_root_after_hash72"],
                "root_verification_hash72": first["root_verification_hash72"],
                "promotion_hash72": first["promotion_hash72"],
                "promotion_receipt_hash72": first["promotion_receipt_hash72"],
                "promotion_hash216": first["promotion_hash216"],
                "relation_count": frozen_validation["relation_count"],
                "native_state_root216": frozen_validation["native_validation"]["state_root216"],
                "native_projection_root216": frozen_validation["native_validation"]["projection_root216"],
                "native_continuation_root216": frozen_validation["native_validation"]["continuation_root216"],
                "writer_fence_real_i9_lifecycle": True,
                "deterministic_replay_equal": True,
                "candidate_commit_verified": True,
                "prospective_root_verified": True,
                "formal_semantic_round_trip_verified": True,
                "grounded_round_trip_verified": True,
                "perspective_round_trip_verified": True,
                "vm5184_authoritative_projection_invoked": True,
                "vm81_authorization_invoked": False,
                "atomic_promotion_authorized": True,
                "atomic_promotion_invoked": True,
                "atomic_manifest_swap": True,
                "failed_partial_promotion_possible": False,
                "purge_status": "PENDING_VERBATIM_PURGE",
                "verbatim_purge_invoked": False,
                "purge_receipt_issued": False,
                "curriculum_advance_permitted": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
        finally:
            lifecycle.shutdown()

    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i30-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration30_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration30_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    assert validate_hash72(payload["promotion_receipt_hash72"])
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
