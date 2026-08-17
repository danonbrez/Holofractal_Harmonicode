from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_formal_analogical_i27 import (
    PASS218_I27_CANDIDATES_PATH,
    PASS218_I27_STATUS_PATH,
    install_pass218_i27_differentiation_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    I27_RELATION_FAMILIES,
    Pass218I27DifferentiationError,
    Pass218I27DifferentiationRequest,
    Pass218I27FormalAnalogicalDifferentiator,
)
from hhs_runtime.pass218.grounded_manifold_i26 import Pass218I26ManifoldRequest
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


_TOPOLOGY = {
    "i24_beat_identity_preserved": True,
    "i25_perspective_identity_preserved": True,
    "curriculum_identity_preserved": True,
    "source_identity_preserved": True,
    "context_identity_preserved": True,
    "attention_configuration_preserved": True,
    "perspective_order_preserved": True,
    "relation_direction_preserved": True,
    "relation_type_preserved": True,
    "exact_status_preserved": True,
    "epistemic_modality_preserved": True,
    "provenance_preserved": True,
    "orthogonal_relation_layers_preserved": True,
    "authorization_not_widened": True,
    "validation_status_not_promoted": True,
}

_TYPES = (
    ("DISTRIBUTIONAL_NEIGHBOR", "ASSOCIATION"),
    ("LEXICAL_SYNONYM", "SIMILARITY"),
    ("SYMBOLIZES", "SYMBOLIZATION"),
    ("IMPLIES", "IMPLICATION"),
    ("CAUSES", "CAUSALITY"),
    ("FORMAL_ENTAILMENT", "IDENTITY_FORMAL_ENTAILMENT"),
    ("ANALOGY", "ANALOGY"),
    ("COUNTERFACTUAL", "COUNTERFACTUAL_IMAGINATION"),
    ("CONTRADICTION", "CONTRADICTION"),
    ("EMPIRICAL_OBSERVATION", "EMPIRICAL_OBSERVATION"),
)


class FakeI26Control:
    def __init__(
        self,
        *,
        safety_drift: str | None = None,
        topology_drift: str | None = None,
        include_unknown: bool = False,
    ) -> None:
        self.safety_drift = safety_drift
        self.topology_drift = topology_drift
        self.include_unknown = include_unknown
        self.calls = 0

    def status(self) -> dict:
        result = {
            "grounded_relational_manifold_candidate_ready": True,
            "grounded_relational_manifold_status": (
                "REVISABLE_GROUNDED_RELATIONAL_MANIFOLD_CANDIDATE"
            ),
            "grounding_canonical": False,
            "grounded_relational_manifold_ready": False,
            "grounded_relational_manifold_promoted": False,
            "formal_analogical_typing_invoked": False,
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
        if self.safety_drift:
            result[self.safety_drift] = True
        return result

    def construct(self, request: Pass218I26ManifoldRequest) -> dict:
        self.calls += 1
        request.validated()
        grounding_hash = h72("I27-GROUNDING", "fixture")
        i25_hash = h72("I27-I25", "fixture")
        relation_specs = list(_TYPES)
        if self.include_unknown:
            relation_specs.append(("UNMAPPED_NATIVE_RELATION", None))
        relations = []
        nodes = []
        for rank, (relation_type, _family) in enumerate(relation_specs, start=1):
            source = f"source-{rank}"
            target = f"target-{rank}"
            source_hash = h72("I27-NODE", source)
            target_hash = h72("I27-NODE", target)
            relation = {
                "source_token": source,
                "target_token": target,
                "source_id_hash72": source_hash,
                "target_id_hash72": target_hash,
                "relation_type": relation_type,
                "status": -1 if relation_type == "CONTRADICTION" else 1,
                "provenance": "I27_TEST_FIXTURE",
                "upstream_hash72": h72("I27-UPSTREAM", relation_type),
                "i22_edge_hash72": h72("I27-I22-EDGE", relation_type),
                "beat_relation_hash72": h72("I27-BEAT-REL", relation_type),
                "perspective_relation_hash72": h72("I27-I25-REL", relation_type),
                "perspective_order_rank": rank,
                "perspective_salience_delta": rank,
                "candidate_grounding_applied": True,
                "relation_direction_preserved": True,
                "relation_type_preserved": True,
                "exact_status_preserved": True,
                "epistemic_modality_preserved": True,
                "provenance_preserved": True,
                "perspective_salience_preserved": True,
                "formal_relation_type_assigned": False,
                "analogical_relation_type_assigned": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "grounding_identity_hash72": grounding_hash,
                "i25_perspective_context_hash72": i25_hash,
            }
            if relation_type == "DISTRIBUTIONAL_NEIGHBOR":
                relation["exact_strength"] = {"numerator": 81, "denominator": 100}
            relation["grounded_relation_hash72"] = h72(
                "I27-GROUNDED-REL", [relation_type, rank]
            )
            relations.append(relation)
            nodes.extend(
                [
                    {
                        "distinction_id_hash72": source_hash,
                        "observed_tokens": [source],
                        "candidate_only": True,
                        "truth_authority": False,
                    },
                    {
                        "distinction_id_hash72": target_hash,
                        "observed_tokens": [target],
                        "candidate_only": True,
                        "truth_authority": False,
                    },
                ]
            )
        topology = dict(_TOPOLOGY)
        if self.topology_drift:
            topology[self.topology_drift] = False
        result = {
            **self.status(),
            "grounding_invoked": True,
            "grounded_relational_manifold_hash72": h72("I27-I26-RESULT", "fixture"),
            "manifold_state_hash72": h72("I27-I26-STATE", "fixture"),
            "i24_narrative_beat_hash72": h72("I27-I24", "fixture"),
            "i25_perspective_context_hash72": i25_hash,
            "grounding_identity": {
                "grounding_identity_hash72": grounding_hash,
                "curriculum_identity_hash72": h72("I27-CURRICULUM", "fixture"),
                "source_checksum_sha256": "a" * 64,
                "general_english_genesis_mutated": False,
            },
            "perspective_profile": {
                "profile_id": "i27-test-perspective",
                "profile_version": "v1",
                "perspective_profile_hash72": h72("I27-PROFILE", "v1"),
                "general_english_genesis_mutated": False,
            },
            "active_context": {"context_id": "i27-formal-analogical-test"},
            "attention_configuration": {
                "attention_tokens": ["relation"],
                "attention_radius": 1,
                "max_hydrated_nodes": 24,
            },
            "manifold_nodes": nodes,
            "manifold_relations": relations,
            "polarity_conflict_candidates": [],
            "relation_count": len(relations),
            "node_count": len(nodes),
            "topology_conservation": topology,
            "validation_receipt": {
                "topology_conservation_validated": not bool(self.topology_drift),
                "manifold_validation_receipt_hash72": h72("I27-I26-RECEIPT", "fixture"),
            },
            "i20_binding_hash72": h72("I20", "binding"),
            "i21_batch_hash72": h72("I21", "batch"),
            "i22_graph_hash72": h72("I22", "graph"),
            "i23_contextual_state_hash72": h72("I23", "state"),
        }
        if self.safety_drift:
            result[self.safety_drift] = True
        return result


def manifold_request() -> Pass218I26ManifoldRequest:
    beat = Pass218I24BeatRequest(
        tokens=("relation", "meaning"),
        context_id="i27 formal analogical differentiation fixture",
        curriculum_identity_hash72=h72("I27-CURRICULUM", "request"),
        curriculum_position=27,
        source_id="i27-fixture",
        source_checksum_sha256="b" * 64,
        source_authority="REPOSITORY_NATIVE",
        rights_class="REPOSITORY_NATIVE",
        evidence_id="i27-fixture-evidence",
        evidence_type="RELATIONAL_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=h72("I27-EVIDENCE", "request"),
        attention_tokens=("relation",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=24,
    ).validated()
    profile = Pass218I25PerspectiveProfile(
        profile_id="i27-test-perspective",
        profile_version="v1",
        profile_origin="USER_AUTHORED",
        rules=(),
    ).validated()
    perspective = Pass218I25PerspectiveRequest(
        beat_request=beat,
        perspective_profile=profile,
    ).validated()
    return Pass218I26ManifoldRequest(perspective_request=perspective).validated()


def request() -> Pass218I27DifferentiationRequest:
    return Pass218I27DifferentiationRequest(
        manifold_request=manifold_request(),
    ).validated()


def api_payload() -> dict:
    perspective = manifold_request().perspective_request
    beat = perspective.beat_request
    profile = perspective.perspective_profile
    return {
        "tokens": list(beat.tokens),
        "context_id": beat.context_id,
        "curriculum_identity_hash72": beat.curriculum_identity_hash72,
        "curriculum_position": beat.curriculum_position,
        "source_identity": {
            "source_id": beat.source_id,
            "source_checksum_sha256": beat.source_checksum_sha256,
            "source_authority": beat.source_authority,
            "rights_class": beat.rights_class,
        },
        "evidence": {
            "evidence_id": beat.evidence_id,
            "evidence_type": beat.evidence_type,
            "epistemic_status": beat.evidence_epistemic_status,
            "payload_hash72": beat.evidence_payload_hash72,
        },
        "attention_tokens": list(beat.attention_tokens),
        "top_k": beat.top_k,
        "attention_radius": beat.attention_radius,
        "max_hydrated_nodes": beat.max_hydrated_nodes,
        "allowed_relation_families": list(beat.allowed_relation_families),
        "perspective_profile": {
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
            "profile_origin": profile.profile_origin,
            "rules": [],
        },
    }


def test_i27_distinguishes_all_required_relation_families_without_promotion() -> None:
    result = Pass218I27FormalAnalogicalDifferentiator(FakeI26Control()).differentiate(
        request()
    )
    assert result["formal_analogical_differentiation_candidate_ready"] is True
    assert result["formal_analogical_typing_invoked"] is True
    assert result["formal_analogical_typing_canonical"] is False
    assert result["differentiation_complete"] is True
    assert result["unresolved_relation_count"] == 0
    assert tuple(result["relation_taxonomy"]["relation_families"]) == I27_RELATION_FAMILIES
    assert set(result["observed_relation_families"]) == set(I27_RELATION_FAMILIES)
    assert [
        item["relation_family_candidate"] for item in result["differentiated_relations"]
    ] == [family for _relation_type, family in _TYPES]
    assert result["truth_promotion"] is False
    assert result["action_authority_minted"] is False
    assert result["canonical_learning_commit_invoked"] is False
    assert result["hash216_continuation_verified"] is False
    assert result["vm5184_authoritative_projection_invoked"] is False
    assert result["vm81_authorization_invoked"] is False


def test_i27_preserves_upstream_relation_identity_order_and_exact_strength() -> None:
    result = Pass218I27FormalAnalogicalDifferentiator(FakeI26Control()).differentiate(
        request()
    )
    relations = result["differentiated_relations"]
    assert [item["perspective_order_rank"] for item in relations] == list(
        range(1, len(relations) + 1)
    )
    assert [item["upstream_relation_type"] for item in relations] == [
        relation_type for relation_type, _family in _TYPES
    ]
    assert relations[0]["exact_strength"] == {"numerator": 81, "denominator": 100}
    assert all(item["upstream_relation_type_preserved"] is True for item in relations)
    assert all(item["truth_promotion"] is False for item in relations)
    assert all(result["meaning_conservation"].values())


def test_i27_unknown_upstream_type_fails_closed_to_unresolved_candidate() -> None:
    result = Pass218I27FormalAnalogicalDifferentiator(
        FakeI26Control(include_unknown=True)
    ).differentiate(request())
    unknown = result["differentiated_relations"][-1]
    assert unknown["relation_family_candidate"] is None
    assert unknown["differentiation_mode"] == "UNRESOLVED"
    assert unknown["relation_family_resolved"] is False
    assert unknown["differentiation_basis"] == "UNRESOLVED_UPSTREAM_RELATION_TYPE"
    assert result["unresolved_relation_count"] == 1
    assert result["differentiation_complete"] is False
    assert result["truth_promotion"] is False


def test_i27_replay_is_exact_and_taxonomy_is_hash72_sealed() -> None:
    control = FakeI26Control()
    differentiator = Pass218I27FormalAnalogicalDifferentiator(control)
    first = differentiator.differentiate(request())
    replay = differentiator.differentiate(request())
    assert first == replay
    assert first["formal_analogical_differentiation_hash72"] == replay[
        "formal_analogical_differentiation_hash72"
    ]
    assert first["relation_taxonomy"]["taxonomy_hash72"]
    assert first["validation_receipt"]["differentiation_validation_receipt_hash72"]


def test_i27_fails_closed_on_i26_authority_or_topology_drift() -> None:
    for field in (
        "grounding_canonical",
        "grounded_relational_manifold_ready",
        "formal_analogical_typing_invoked",
        "hash216_continuation_verified",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
    ):
        with pytest.raises(
            Pass218I27DifferentiationError,
            match="P218_I27_I26_SAFETY_DRIFT",
        ):
            Pass218I27FormalAnalogicalDifferentiator(
                FakeI26Control(safety_drift=field)
            ).differentiate(request())

    with pytest.raises(
        Pass218I27DifferentiationError,
        match="P218_I27_I26_TOPOLOGY_CONSERVATION_INVALID",
    ):
        Pass218I27FormalAnalogicalDifferentiator(
            FakeI26Control(topology_drift="relation_type_preserved")
        ).differentiate(request())


def test_i27_runtime_surface_is_candidate_only_and_browser_safe() -> None:
    app = FastAPI()
    control = install_pass218_i27_differentiation_control(app, FakeI26Control())
    assert control.status()["formal_analogical_differentiation_candidate_ready"] is True

    with TestClient(app) as client:
        status = client.get(PASS218_I27_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["truth_promotion"] is False

        response = client.post(PASS218_I27_CANDIDATES_PATH, json=api_payload())
        assert response.status_code == 200
        payload = response.json()
        assert payload["formal_analogical_differentiation_status"] == (
            "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
        )
        assert payload["differentiation_complete"] is True
        assert payload["truth_promotion"] is False
        assert client.get(PASS218_I27_CANDIDATES_PATH).status_code == 405
        assert client.post(PASS218_I27_STATUS_PATH, json={}).status_code == 405
