#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 28 native transition evidence."""
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
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    Pass218I27DifferentiationRequest,
    Pass218I27FormalAnalogicalDifferentiator,
)
from hhs_runtime.pass218.grounded_manifold_i26 import (
    Pass218I26GroundedRelationalManifold,
    Pass218I26ManifoldRequest,
)
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    VM5184_CELL_COUNT,
    VM5184_STATE_BITS,
    Pass218I28Hash216VM5184Transition,
    Pass218I28TransitionRequest,
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
        {"domain": "HHS-P218-I28-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 28,
            "authoritative_curriculum_advance": False,
        },
    )
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I28-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "HASH216_VM5184_TRANSITION_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )
    rule_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I28-EVIDENCE-PERSPECTIVE-RULE-V1"},
        {
            "principle": "NATIVE_TRANSITION_PRESERVES_TYPED_RELATIONAL_MEANING",
            "hash216_three_segment_candidate_required": True,
            "vm5184_native_projection_required": True,
            "semantic_validation_deferred": True,
            "atomic_promotion_deferred": True,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    i24 = Pass218I24RuntimeNarrativeBeatControl(i23)
    i25 = Pass218I25RuntimePerspectiveContextControl(i24)
    i26 = Pass218I26GroundedRelationalManifold(i25)
    i27 = Pass218I27FormalAnalogicalDifferentiator(i26)
    i28 = Pass218I28Hash216VM5184Transition(i27)

    beat_request = Pass218I24BeatRequest(
        tokens=("relational", "grounding", "context"),
        context_id="pass218 hash216 vm5184 transition contract",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=28,
        source_id=source_path.name,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i28-hash216-vm5184-transition-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("relational", "grounding"),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=16,
    ).validated()

    accepted_profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-transition-perspective",
        profile_version="i28-v1",
        profile_origin="USER_AUTHORED",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-transition-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()
    alternate_profile = Pass218I25PerspectiveProfile(
        profile_id=accepted_profile.profile_id,
        profile_version="i28-v2",
        profile_origin="USER_AUTHORED",
        rules=accepted_profile.rules,
    ).validated()

    def make_request(profile: Pass218I25PerspectiveProfile) -> Pass218I28TransitionRequest:
        perspective = Pass218I25PerspectiveRequest(beat_request, profile).validated()
        manifold = Pass218I26ManifoldRequest(perspective).validated()
        differentiation = Pass218I27DifferentiationRequest(manifold).validated()
        return Pass218I28TransitionRequest(differentiation).validated()

    first = i28.construct(make_request(accepted_profile))
    replay = i28.construct(make_request(accepted_profile))
    alternate = i28.construct(make_request(alternate_profile))

    assert first == replay
    assert first["hash216_vm5184_transition_hash72"] == replay[
        "hash216_vm5184_transition_hash72"
    ]
    assert first["pass218_hash216_candidate"] == replay["pass218_hash216_candidate"]
    assert first["hash216_vm5184_transition_hash72"] != alternate[
        "hash216_vm5184_transition_hash72"
    ]
    assert first["native_continuation_token"]["continuation_root216"] != alternate[
        "native_continuation_token"
    ]["continuation_root216"]
    assert len(first["pass218_hash216_candidate"]) == 216
    segments = first["pass218_hash216_segments"]
    assert first["pass218_hash216_candidate"] == (
        segments["manifest_curriculum_hash72"]
        + segments["hydrated_transition_state_hash72"]
        + segments["prevalidation_receipt_hash72"]
    )
    assert segments["manifest_curriculum_hash72"] == curriculum_identity_hash72
    assert first["vm5184_candidate"]["state_bits"] == VM5184_STATE_BITS
    assert first["vm5184_candidate"]["cell_count"] == VM5184_CELL_COUNT
    assert len(first["vm5184_candidate"]["state_words"]) == VM5184_CELL_COUNT
    assert first["vm5184_candidate"]["populated_relation_cells"] == first["relation_count"]
    assert first["vm5184_candidate"]["native_abi_canonical_float_fields"] == 0
    assert first["native_vm5184_transition_constructed"] is True
    assert first["hash216_candidate_receipt_constructed"] is True
    assert first["hash216_continuation_constructed"] is True
    assert first["hash216_continuation_verified"] is False
    assert first["semantic_transition_validated"] is False
    assert first["vm5184_authoritative_projection_invoked"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["atomic_promotion_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False
    assert all(first["transition_conservation"].values())
    assert first["grounding_identity"]["general_english_genesis_mutated"] is False

    payload = {
        "schema": "HHS-P218-I28-EVIDENCE-V1",
        "iteration": 28,
        "source_sha256": source_sha256,
        "curriculum_identity_hash72": curriculum_identity_hash72,
        "evidence_payload_hash72": evidence_payload_hash72,
        "i27_formal_analogical_differentiation_hash72": first[
            "i27_formal_analogical_differentiation_hash72"
        ],
        "transition_state_hash72": first["transition_state_hash72"],
        "prevalidation_receipt_hash72": first["prevalidation_receipt"][
            "prevalidation_receipt_hash72"
        ],
        "pass218_hash216_candidate": first["pass218_hash216_candidate"],
        "hash216_vm5184_transition_hash72": first[
            "hash216_vm5184_transition_hash72"
        ],
        "native_state_root216": first["vm5184_candidate"]["native_state_root216"],
        "native_projection_root216": first["vm5184_candidate"][
            "native_projection_root216"
        ],
        "native_continuation_root216": first["native_continuation_token"][
            "continuation_root216"
        ],
        "native_receipt_hash72": first["native_continuation_token"][
            "receipt_hash72"
        ],
        "relation_count": first["relation_count"],
        "vm5184_state_bits": first["vm5184_candidate"]["state_bits"],
        "vm5184_cell_count": first["vm5184_candidate"]["cell_count"],
        "vm5184_populated_relation_cells": first["vm5184_candidate"][
            "populated_relation_cells"
        ],
        "vm5184_zero_padded_cells": first["vm5184_candidate"]["zero_padded_cells"],
        "native_projection_channels": first["vm5184_candidate"][
            "native_projection_channels"
        ],
        "native_abi_canonical_float_fields": first["vm5184_candidate"][
            "native_abi_canonical_float_fields"
        ],
        "deterministic_replay_equal": True,
        "profile_version_change_produces_distinct_transition": True,
        "three_segment_hash216_candidate_valid": True,
        "native_vm5184_transition_constructed": True,
        "transition_conservation_validated": True,
        "general_english_genesis_mutated": False,
        "hash216_continuation_constructed": True,
        "hash216_continuation_verified": False,
        "semantic_transition_validated": False,
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
    output_root = Path(".i28-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration28_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration28_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
