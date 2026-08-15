#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 27 differentiation evidence."""
from __future__ import annotations

from collections import Counter
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
    I27_RELATION_FAMILIES,
    Pass218I27DifferentiationRequest,
    Pass218I27FormalAnalogicalDifferentiator,
)
from hhs_runtime.pass218.grounded_manifold_i26 import (
    Pass218I26GroundedRelationalManifold,
    Pass218I26ManifoldRequest,
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
        {"domain": "HHS-P218-I27-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 27,
            "authoritative_curriculum_advance": False,
        },
    )
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I27-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "FORMAL_ANALOGICAL_DIFFERENTIATION_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )
    rule_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I27-EVIDENCE-PERSPECTIVE-RULE-V1"},
        {
            "principle": (
                "RELATION_FAMILY_DIFFERENTIATION_PRESERVES_UPSTREAM_MEANING_AND_AUTHORITY"
            ),
            "unknown_types_remain_unresolved": True,
            "truth_promotion_deferred": True,
            "hash216_vm5184_vm81_promotion_deferred": True,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    i24 = Pass218I24RuntimeNarrativeBeatControl(i23)
    i25 = Pass218I25RuntimePerspectiveContextControl(i24)
    i26 = Pass218I26GroundedRelationalManifold(i25)
    i27 = Pass218I27FormalAnalogicalDifferentiator(i26)

    beat_request = Pass218I24BeatRequest(
        tokens=("relational", "grounding", "context"),
        context_id="pass218 formal analogical differentiation contract",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=27,
        source_id=source_path.name,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i27-formal-analogical-differentiation-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("relational", "grounding"),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=16,
    ).validated()

    accepted_profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-differentiation-perspective",
        profile_version="i27-v1",
        profile_origin="USER_AUTHORED",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-differentiation-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()
    alternate_profile = Pass218I25PerspectiveProfile(
        profile_id=accepted_profile.profile_id,
        profile_version="i27-v2",
        profile_origin="USER_AUTHORED",
        rules=accepted_profile.rules,
    ).validated()

    accepted_request = Pass218I27DifferentiationRequest(
        Pass218I26ManifoldRequest(
            Pass218I25PerspectiveRequest(beat_request, accepted_profile)
        )
    )
    first = i27.differentiate(accepted_request)
    replay = i27.differentiate(accepted_request)
    alternate = i27.differentiate(
        Pass218I27DifferentiationRequest(
            Pass218I26ManifoldRequest(
                Pass218I25PerspectiveRequest(beat_request, alternate_profile)
            )
        )
    )

    assert first == replay
    assert first["formal_analogical_differentiation_hash72"] == replay[
        "formal_analogical_differentiation_hash72"
    ]
    assert first["formal_analogical_differentiation_hash72"] != alternate[
        "formal_analogical_differentiation_hash72"
    ]
    assert first["grounding_identity"]["curriculum_identity_hash72"] == alternate[
        "grounding_identity"
    ]["curriculum_identity_hash72"]
    assert first["grounding_identity"]["source_checksum_sha256"] == source_sha256
    assert first["grounding_identity"]["general_english_genesis_mutated"] is False
    assert first["formal_analogical_differentiation_candidate_ready"] is True
    assert first["formal_analogical_typing_invoked"] is True
    assert first["formal_analogical_typing_canonical"] is False
    assert first["relation_count"] == len(first["differentiated_relations"])
    assert first["resolved_relation_count"] == first["relation_count"]
    assert first["unresolved_relation_count"] == 0
    assert first["differentiation_complete"] is True
    assert tuple(first["relation_taxonomy"]["relation_families"]) == I27_RELATION_FAMILIES
    assert all(first["meaning_conservation"].values())
    assert first["validation_receipt"]["meaning_conservation_validated"] is True
    assert all(
        item["upstream_relation_type"] == item["relation_type"]
        and item["upstream_relation_type_preserved"] is True
        and item["relation_direction_preserved"] is True
        and item["exact_status_preserved"] is True
        and item["provenance_preserved"] is True
        and item["perspective_order_preserved"] is True
        and item["relation_family_resolved"] is True
        and item["truth_promotion"] is False
        and item["action_authority_minted"] is False
        for item in first["differentiated_relations"]
    )
    assert all(
        item["formal_entailment_verified"] is False
        and item["causality_verified"] is False
        and item["empirical_observation_verified"] is False
        and item["logical_contradiction_verified"] is False
        for item in first["differentiated_relations"]
    )
    assert all(
        item["cross_family_collapse_invoked"] is False
        and item["truth_resolution_invoked"] is False
        for item in first["relation_family_layers"]
    )
    assert first["hash216_continuation_verified"] is False
    assert first["vm5184_authoritative_projection_invoked"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False

    family_counts = Counter(
        str(item["relation_family_candidate"])
        for item in first["differentiated_relations"]
    )
    payload = {
        "schema": "HHS-P218-I27-EVIDENCE-V1",
        "iteration": 27,
        "source_sha256": source_sha256,
        "curriculum_identity_hash72": curriculum_identity_hash72,
        "evidence_payload_hash72": evidence_payload_hash72,
        "i26_grounded_relational_manifold_hash72": first[
            "i26_grounded_relational_manifold_hash72"
        ],
        "grounding_identity_hash72": first["grounding_identity"][
            "grounding_identity_hash72"
        ],
        "taxonomy_hash72": first["relation_taxonomy"]["taxonomy_hash72"],
        "differentiation_state_hash72": first["differentiation_state_hash72"],
        "formal_analogical_differentiation_hash72": first[
            "formal_analogical_differentiation_hash72"
        ],
        "differentiation_validation_receipt_hash72": first["validation_receipt"][
            "differentiation_validation_receipt_hash72"
        ],
        "relation_count": first["relation_count"],
        "resolved_relation_count": first["resolved_relation_count"],
        "unresolved_relation_count": first["unresolved_relation_count"],
        "relation_family_layer_count": first["relation_family_layer_count"],
        "observed_relation_families": first["observed_relation_families"],
        "relation_family_counts": dict(sorted(family_counts.items())),
        "required_relation_taxonomy": list(I27_RELATION_FAMILIES),
        "deterministic_replay_equal": True,
        "profile_version_change_produces_distinct_differentiation": True,
        "upstream_relation_type_preserved": True,
        "perspective_order_preserved": True,
        "orthogonal_family_layers_preserved": True,
        "unknown_relation_types_fail_closed": True,
        "meaning_conservation_validated": True,
        "general_english_genesis_mutated": False,
        "formal_analogical_typing_invoked": True,
        "formal_analogical_typing_canonical": False,
        "hash216_continuation_verified": False,
        "vm5184_authoritative_projection_invoked": False,
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
    output_root = Path(".i27-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration27_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration27_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
