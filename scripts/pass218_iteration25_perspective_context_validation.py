#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 25 perspective/context evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_backend.runtime_os_pass218_narrative_beat_i24 import (
    Pass218I24RuntimeNarrativeBeatControl,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveContextHydrator,
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
    source_path = repository_root / "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md"
    source_sha256 = sha256(source_path.read_bytes()).hexdigest()

    curriculum_identity_hash72 = hash72_digest(
        {"domain": "HHS-P218-I25-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 25,
            "authoritative_curriculum_advance": False,
        },
    )
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I25-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "PERSPECTIVE_AUTHORITY_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )
    rule_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I25-EVIDENCE-PERSPECTIVE-RULE-V1"},
        {
            "principle": "USER_AUTHORED_OR_ACCEPTED_PERSPECTIVE_MAY_ORGANIZE_MEANING",
            "inferred_rules_require_acceptance": True,
            "general_english_genesis_mutated": False,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    i24 = Pass218I24RuntimeNarrativeBeatControl(i23)
    hydrator = Pass218I25PerspectiveContextHydrator(i24)

    beat_request = Pass218I24BeatRequest(
        tokens=("perspective", "context", "meaning"),
        context_id="pass218 perspective authority contract",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=25,
        source_id=source_path.name,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i25-perspective-contract-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("perspective",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=12,
    ).validated()

    accepted_profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-perspective-profile",
        profile_version="i25-v1",
        profile_origin="USER_AUTHORED",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-local-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()
    inferred_profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-perspective-profile-inferred",
        profile_version="i25-candidate-v1",
        profile_origin="INFERRED_CANDIDATE",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-local-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()

    first = hydrator.hydrate(
        Pass218I25PerspectiveRequest(beat_request, accepted_profile)
    )
    replay = hydrator.hydrate(
        Pass218I25PerspectiveRequest(beat_request, accepted_profile)
    )
    inferred = hydrator.hydrate(
        Pass218I25PerspectiveRequest(beat_request, inferred_profile)
    )
    alternate_profile = Pass218I25PerspectiveProfile(
        profile_id=accepted_profile.profile_id,
        profile_version="i25-v2",
        profile_origin="USER_AUTHORED",
        rules=accepted_profile.rules,
    ).validated()
    alternate = hydrator.hydrate(
        Pass218I25PerspectiveRequest(beat_request, alternate_profile)
    )

    assert first == replay
    assert first["perspective_context_hash72"] == replay["perspective_context_hash72"]
    assert first["perspective_context_hash72"] != alternate["perspective_context_hash72"]
    assert first["i24_narrative_beat_hash72"] == alternate["i24_narrative_beat_hash72"]
    assert first["i24_narrative_beat_hash72"] == inferred["i24_narrative_beat_hash72"]
    assert first["perspective_profile"]["accepted_for_organization"] is True
    assert first["perspective_profile"]["separately_versioned_from_general_english_genesis"] is True
    assert first["perspective_profile"]["general_english_genesis_mutated"] is False
    assert first["accepted_rule_count"] == 1
    assert inferred["accepted_rule_count"] == 0
    assert inferred["inferred_candidate_rule_count"] == 1
    assert all(
        relation["perspective_salience_delta"] == 5
        for relation in first["perspective_relations"]
    )
    assert all(
        relation["perspective_salience_delta"] == 0
        for relation in inferred["perspective_relations"]
    )
    assert all(first["meaning_conservation"].values())
    assert first["validation_receipt"]["meaning_conservation_validated"] is True
    assert first["perspective_hydration_invoked"] is True
    assert first["perspective_hydration_canonical"] is False
    assert first["grounded_relational_manifold_ready"] is False
    assert first["formal_analogical_typing_invoked"] is False
    assert first["hash216_continuation_verified"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False

    payload = {
        "schema": "HHS-P218-I25-EVIDENCE-V1",
        "iteration": 25,
        "source_sha256": source_sha256,
        "curriculum_identity_hash72": curriculum_identity_hash72,
        "evidence_payload_hash72": evidence_payload_hash72,
        "i24_narrative_beat_hash72": first["i24_narrative_beat_hash72"],
        "perspective_profile_hash72": first["perspective_profile"][
            "perspective_profile_hash72"
        ],
        "perspective_state_hash72": first["perspective_state_hash72"],
        "perspective_context_hash72": first["perspective_context_hash72"],
        "perspective_validation_receipt_hash72": first["validation_receipt"][
            "perspective_validation_receipt_hash72"
        ],
        "candidate_relation_count": first["candidate_relation_count"],
        "accepted_rule_count": first["accepted_rule_count"],
        "inferred_candidate_rule_count": inferred["inferred_candidate_rule_count"],
        "deterministic_replay_equal": True,
        "profile_version_change_produces_distinct_state": True,
        "inferred_rules_not_applied": True,
        "meaning_conservation_validated": True,
        "general_english_genesis_mutated": False,
        "perspective_hydration_invoked": True,
        "perspective_hydration_canonical": False,
        "grounded_relational_manifold_ready": False,
        "formal_analogical_typing_invoked": False,
        "hash216_continuation_verified": False,
        "vm81_authorization_invoked": False,
        "authoritative_semantic_compression_ready": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i25-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration25_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration25_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
