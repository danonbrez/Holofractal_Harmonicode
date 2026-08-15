#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 29 transition-validation evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_backend.runtime_os_pass218_narrative_beat_i24 import (
    Pass218I24RuntimeNarrativeBeatControl,
)
from hhs_backend.runtime_os_pass218_perspective_context_i25 import (
    Pass218I25RuntimePerspectiveContextControl,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
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
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
    Pass218I25PerspectiveRule,
)
from scripts.pass218_iteration24_narrative_beat_validation import I23EvidenceAdapter


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

    accepted_profile = Pass218I25PerspectiveProfile(
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
    alternate_profile = Pass218I25PerspectiveProfile(
        profile_id=accepted_profile.profile_id,
        profile_version="i29-v2",
        profile_origin="USER_AUTHORED",
        rules=accepted_profile.rules,
    ).validated()

    def make_request(profile: Pass218I25PerspectiveProfile) -> Pass218I29ValidationRequest:
        perspective = Pass218I25PerspectiveRequest(beat_request, profile).validated()
        manifold = Pass218I26ManifoldRequest(perspective).validated()
        differentiation = Pass218I27DifferentiationRequest(manifold).validated()
        transition = Pass218I28TransitionRequest(differentiation).validated()
        return Pass218I29ValidationRequest(transition).validated()

    first = i29.validate(make_request(accepted_profile))
    replay = i29.validate(make_request(accepted_profile))
    alternate = i29.validate(make_request(alternate_profile))

    assert first == replay
    assert first["hash216_vm5184_validation_hash72"] == replay[
        "hash216_vm5184_validation_hash72"
    ]
    assert first["pass218_validated_hash216"] == replay["pass218_validated_hash216"]
    assert first["hash216_vm5184_validation_hash72"] != alternate[
        "hash216_vm5184_validation_hash72"
    ]
    assert len(first["pass218_validated_hash216"]) == 216
    segments = first["pass218_validated_hash216_segments"]
    assert first["pass218_validated_hash216"] == (
        segments["manifest_curriculum_hash72"]
        + segments["hydrated_transition_state_hash72"]
        + segments["validation_receipt_hash72"]
    )
    assert segments["manifest_curriculum_hash72"] == curriculum_identity_hash72
    assert all(validate_hash72(value) for value in segments.values())
    assert first["relation_count"] == 14
    assert first["semantic_validation_witness"]["relation_count"] == 14
    assert first["hash216_continuation_verified"] is True
    assert first["semantic_transition_validated"] is True
    assert first["vm5184_candidate_projection_verified"] is True
    assert first["candidate_semantic_binding_verified"] is True
    assert first["formal_semantic_round_trip_verified"] is False
    assert first["atomic_promotion_candidate_ready"] is True
    assert first["atomic_promotion_authorized"] is False
    assert first["native_validation"]["candidate_projection_rederived"] is True
    assert first["native_validation"]["authoritative_projection"] is False
    assert first["native_validation"]["canonical_float_fields"] == 0
    assert first["vm5184_authoritative_projection_invoked"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["atomic_promotion_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False

    payload = {
        "schema": "HHS-P218-I29-EVIDENCE-V1",
        "iteration": 29,
        "source_sha256": source_sha256,
        "curriculum_identity_hash72": curriculum_identity_hash72,
        "evidence_payload_hash72": evidence_payload_hash72,
        "i28_hash216_vm5184_transition_hash72": first[
            "i28_hash216_vm5184_transition_hash72"
        ],
        "transition_state_hash72": first["transition_state_hash72"],
        "validation_receipt_hash72": first["validation_receipt"][
            "validation_receipt_hash72"
        ],
        "validated_hash216": first["pass218_validated_hash216"],
        "hash216_vm5184_validation_hash72": first[
            "hash216_vm5184_validation_hash72"
        ],
        "semantic_witness_hash72": first["semantic_validation_witness"][
            "semantic_witness_hash72"
        ],
        "native_state_root216": first["native_validation"]["state_root216"],
        "native_projection_root216": first["native_validation"]["projection_root216"],
        "native_continuation_root216": first["native_validation"][
            "continuation_root216"
        ],
        "relation_count": first["relation_count"],
        "deterministic_replay_equal": True,
        "profile_version_change_produces_distinct_validation": True,
        "validated_three_segment_hash216_valid": True,
        "hash216_continuation_verified": True,
        "semantic_transition_validated": True,
        "candidate_semantic_binding_verified": True,
        "formal_semantic_round_trip_verified": False,
        "vm5184_candidate_projection_verified": True,
        "native_projection_rederived": True,
        "native_abi_canonical_float_fields": first["native_validation"][
            "canonical_float_fields"
        ],
        "atomic_promotion_candidate_ready": True,
        "atomic_promotion_authorized": False,
        "vm5184_authoritative_projection_invoked": False,
        "vm81_authorization_invoked": False,
        "atomic_promotion_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i29-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration29_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration29_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
