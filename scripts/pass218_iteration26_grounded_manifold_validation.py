#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 26 grounded-manifold evidence."""
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
    source_path = repository_root / "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md"
    source_sha256 = sha256(source_path.read_bytes()).hexdigest()

    curriculum_identity_hash72 = hash72_digest(
        {"domain": "HHS-P218-I26-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 26,
            "authoritative_curriculum_advance": False,
        },
    )
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I26-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "RELATIONAL_GROUNDING_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )
    rule_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I26-EVIDENCE-PERSPECTIVE-RULE-V1"},
        {
            "principle": "ACCEPTED_PERSPECTIVE_ORGANIZES_LOCAL_MEANING_WITHOUT_TRUTH_PROMOTION",
            "grounding_is_identity_context_binding": True,
            "formal_analogical_typing_deferred": True,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    i24 = Pass218I24RuntimeNarrativeBeatControl(i23)
    i25 = Pass218I25RuntimePerspectiveContextControl(i24)
    manifold = Pass218I26GroundedRelationalManifold(i25)

    beat_request = Pass218I24BeatRequest(
        tokens=("relational", "grounding", "context"),
        context_id="pass218 grounded relational manifold contract",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=26,
        source_id=source_path.name,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i26-grounded-manifold-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("relational", "grounding"),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=16,
    ).validated()

    accepted_profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-grounding-perspective",
        profile_version="i26-v1",
        profile_origin="USER_AUTHORED",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-grounding-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()
    inferred_profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-grounding-perspective-inferred",
        profile_version="i26-candidate-v1",
        profile_origin="INFERRED_CANDIDATE",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-grounding-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()

    accepted_request = Pass218I26ManifoldRequest(
        Pass218I25PerspectiveRequest(beat_request, accepted_profile)
    )
    first = manifold.construct(accepted_request)
    replay = manifold.construct(accepted_request)
    inferred = manifold.construct(
        Pass218I26ManifoldRequest(
            Pass218I25PerspectiveRequest(beat_request, inferred_profile)
        )
    )
    alternate_profile = Pass218I25PerspectiveProfile(
        profile_id=accepted_profile.profile_id,
        profile_version="i26-v2",
        profile_origin="USER_AUTHORED",
        rules=accepted_profile.rules,
    ).validated()
    alternate = manifold.construct(
        Pass218I26ManifoldRequest(
            Pass218I25PerspectiveRequest(beat_request, alternate_profile)
        )
    )

    assert first == replay
    assert first["grounded_relational_manifold_hash72"] == replay[
        "grounded_relational_manifold_hash72"
    ]
    assert first["grounded_relational_manifold_hash72"] != alternate[
        "grounded_relational_manifold_hash72"
    ]
    assert first["grounding_identity"]["curriculum_identity_hash72"] == alternate[
        "grounding_identity"
    ]["curriculum_identity_hash72"]
    assert first["grounding_identity"]["source_checksum_sha256"] == source_sha256
    assert first["grounding_identity"]["general_english_genesis_mutated"] is False
    assert first["grounding_invoked"] is True
    assert first["grounding_canonical"] is False
    assert first["grounded_relational_manifold_candidate_ready"] is True
    assert first["grounded_relational_manifold_ready"] is False
    assert first["grounded_relational_manifold_promoted"] is False
    assert all(first["topology_conservation"].values())
    assert first["validation_receipt"]["topology_conservation_validated"] is True
    assert first["relation_count"] == len(first["manifold_relations"])
    assert first["node_count"] == len(first["manifold_nodes"])
    assert first["relation_layer_count"] == len(first["relation_layers"])
    assert [
        item["perspective_order_rank"] for item in first["manifold_relations"]
    ] == list(range(1, first["relation_count"] + 1))
    assert all(
        item["formal_relation_type_assigned"] is False
        and item["analogical_relation_type_assigned"] is False
        and item["truth_promotion"] is False
        for item in first["manifold_relations"]
    )
    assert all(
        item["orthogonal_layer_preserved"] is True
        and item["formal_analogical_typing_applied"] is False
        for item in first["relation_layers"]
    )
    assert all(
        item["perspective_salience_delta"] == 0
        for item in inferred["manifold_relations"]
    )
    assert inferred["perspective_profile"]["accepted_for_organization"] is False
    assert first["formal_analogical_typing_invoked"] is False
    assert first["hash216_continuation_verified"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False

    payload = {
        "schema": "HHS-P218-I26-EVIDENCE-V1",
        "iteration": 26,
        "source_sha256": source_sha256,
        "curriculum_identity_hash72": curriculum_identity_hash72,
        "evidence_payload_hash72": evidence_payload_hash72,
        "i24_narrative_beat_hash72": first["i24_narrative_beat_hash72"],
        "i25_perspective_context_hash72": first[
            "i25_perspective_context_hash72"
        ],
        "grounding_identity_hash72": first["grounding_identity"][
            "grounding_identity_hash72"
        ],
        "manifold_state_hash72": first["manifold_state_hash72"],
        "grounded_relational_manifold_hash72": first[
            "grounded_relational_manifold_hash72"
        ],
        "manifold_validation_receipt_hash72": first["validation_receipt"][
            "manifold_validation_receipt_hash72"
        ],
        "node_count": first["node_count"],
        "relation_count": first["relation_count"],
        "relation_layer_count": first["relation_layer_count"],
        "polarity_conflict_candidate_count": first[
            "polarity_conflict_candidate_count"
        ],
        "deterministic_replay_equal": True,
        "profile_version_change_produces_distinct_manifold": True,
        "perspective_order_preserved": True,
        "orthogonal_relation_layers_preserved": True,
        "inferred_rules_not_applied": True,
        "topology_conservation_validated": True,
        "general_english_genesis_mutated": False,
        "grounding_invoked": True,
        "grounding_canonical": False,
        "grounded_relational_manifold_ready": False,
        "grounded_relational_manifold_promoted": False,
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
    output_root = Path(".i26-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration26_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration26_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
