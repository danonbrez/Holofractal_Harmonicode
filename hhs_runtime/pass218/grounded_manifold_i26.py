"""Pass 218 Iteration 26 grounded relational manifold candidates.

Iteration 26 consumes only the frozen Iteration 25 perspective/context
hydration candidate.  It binds the revisable relations to exact narrative,
perspective, curriculum, source, context, and inherited lineage identities and
materializes a bounded candidate topology.  Grounding here means deterministic
identity/context binding, not truth promotion.

The manifold preserves relation direction, relation type, exact status,
epistemic/provenance distinctions, perspective ordering, and orthogonal
relation layers.  It does not perform formal/analogical typing, Hash216
continuation, VM5184/VM81 authority, truth promotion, action authority, or
canonical learning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveRequest,
)

PASS218_I26_GROUNDED_MANIFOLD_VERSION = "HHS-P218-I26-GROUNDED-MANIFOLD-V1"
PASS218_I26_GROUNDED_MANIFOLD_SCHEMA = (
    "HHS-P218-I26-GROUNDED-RELATIONAL-MANIFOLD-CANDIDATE-V1"
)
PASS218_I26_STATUS_SCHEMA = "HHS-P218-I26-GROUNDED-MANIFOLD-STATUS-V1"

I26_REQUIRED_CONSERVATION_FIELDS = (
    "beat_identity_preserved",
    "curriculum_identity_preserved",
    "source_identity_preserved",
    "context_identity_preserved",
    "attention_configuration_preserved",
    "relation_direction_preserved",
    "relation_type_preserved",
    "exact_status_preserved",
    "epistemic_modality_preserved",
    "provenance_preserved",
    "curriculum_location_preserved",
    "authorization_not_widened",
    "validation_status_not_promoted",
)


class Pass218I26GroundedManifoldError(RuntimeError):
    """Fail-closed Iteration 26 grounded-manifold candidate error."""


class Pass218I25PerspectiveContextControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def hydrate(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class Pass218I26ManifoldRequest:
    perspective_request: Pass218I25PerspectiveRequest

    def validated(self) -> "Pass218I26ManifoldRequest":
        return Pass218I26ManifoldRequest(
            perspective_request=self.perspective_request.validated(),
        )


class Pass218I26GroundedRelationalManifold:
    """Bind I25 relations into a revisable candidate topology only."""

    _FORBIDDEN_I25_TRUE = (
        "perspective_hydration_canonical",
        "grounded_relational_manifold_ready",
        "formal_analogical_typing_invoked",
        "hash216_continuation_verified",
        "vm5184_authoritative_projection_invoked",
        "vm81_authorization_invoked",
        "authoritative_semantic_compression_ready",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )

    def __init__(self, i25_control: Pass218I25PerspectiveContextControlProtocol) -> None:
        self.i25_control = i25_control
        self.manifold_count = 0
        self.last_manifold_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    @staticmethod
    def _profile_payload(request: Pass218I25PerspectiveRequest) -> dict[str, Any]:
        profile = request.perspective_profile
        return {
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
            "profile_origin": profile.profile_origin,
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "rule_payload_hash72": rule.rule_payload_hash72,
                    "salience_delta": rule.salience_delta,
                    "relation_types": list(rule.relation_types),
                    "source_tokens": list(rule.source_tokens),
                    "target_tokens": list(rule.target_tokens),
                }
                for rule in profile.rules
            ],
        }

    @classmethod
    def _i25_payload(cls, request: Pass218I25PerspectiveRequest) -> dict[str, Any]:
        beat = request.beat_request
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
            "perspective_profile": cls._profile_payload(request),
        }

    def _validated_i25_status(self) -> dict[str, Any]:
        status = self.i25_control.status()
        if not bool(status.get("perspective_context_candidate_ready")):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_PERSPECTIVE_CONTEXT_PROVIDER_REQUIRED"
            )
        if status.get("perspective_context_status") != (
            "REVISABLE_PERSPECTIVE_CONTEXT_HYDRATION_CANDIDATE"
        ):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_SEMANTICS_INVALID"
            )
        for field in self._FORBIDDEN_I25_TRUE:
            if bool(status.get(field)):
                raise Pass218I26GroundedManifoldError(
                    f"P218_I26_I25_SAFETY_DRIFT:{field}"
                )
        return status

    def _validated_i25_state(
        self,
        request: Pass218I25PerspectiveRequest,
    ) -> dict[str, Any]:
        state = self.i25_control.hydrate(self._i25_payload(request))
        if state.get("perspective_context_status") != (
            "REVISABLE_PERSPECTIVE_CONTEXT_HYDRATION_CANDIDATE"
        ):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_STATE_SEMANTICS_INVALID"
            )
        if not bool(state.get("perspective_context_candidate_ready")):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_STATE_NOT_READY"
            )
        if not bool(state.get("perspective_hydration_invoked")):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_PERSPECTIVE_HYDRATION_REQUIRED"
            )
        for field in self._FORBIDDEN_I25_TRUE:
            if bool(state.get(field)):
                raise Pass218I26GroundedManifoldError(
                    f"P218_I26_I25_STATE_SAFETY_DRIFT:{field}"
                )
        for field in (
            "perspective_context_hash72",
            "perspective_state_hash72",
            "i24_narrative_beat_hash72",
        ):
            if not validate_hash72(str(state.get(field) or "")):
                raise Pass218I26GroundedManifoldError(
                    f"P218_I26_I25_{field.upper()}_REQUIRED"
                )
        profile = state.get("perspective_profile")
        if not isinstance(profile, Mapping):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_PERSPECTIVE_PROFILE_REQUIRED"
            )
        if not validate_hash72(str(profile.get("perspective_profile_hash72") or "")):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_PERSPECTIVE_PROFILE_HASH72_REQUIRED"
            )
        if bool(profile.get("general_english_genesis_mutated")):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_GENESIS_MUTATION_FORBIDDEN"
            )
        if not bool(profile.get("separately_versioned_from_general_english_genesis")):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_PERSPECTIVE_VERSION_BOUNDARY_REQUIRED"
            )
        conservation = state.get("meaning_conservation")
        if not isinstance(conservation, Mapping):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_MEANING_CONSERVATION_REQUIRED"
            )
        for field in I26_REQUIRED_CONSERVATION_FIELDS:
            if conservation.get(field) is not True:
                raise Pass218I26GroundedManifoldError(
                    f"P218_I26_I25_MEANING_CONSERVATION_INVALID:{field}"
                )
        receipt = state.get("validation_receipt")
        if not isinstance(receipt, Mapping) or receipt.get(
            "meaning_conservation_validated"
        ) is not True:
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_VALIDATION_RECEIPT_REQUIRED"
            )
        relations = state.get("perspective_relations")
        if not isinstance(relations, list):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_I25_RELATIONS_LIST_REQUIRED"
            )
        return state

    @staticmethod
    def _grounding_identity(
        request: Pass218I25PerspectiveRequest,
        state: Mapping[str, Any],
    ) -> dict[str, Any]:
        beat = request.beat_request
        profile = state["perspective_profile"]
        body = {
            "i24_narrative_beat_hash72": state["i24_narrative_beat_hash72"],
            "i25_perspective_context_hash72": state["perspective_context_hash72"],
            "i25_perspective_state_hash72": state["perspective_state_hash72"],
            "perspective_profile_hash72": profile["perspective_profile_hash72"],
            "curriculum_identity_hash72": beat.curriculum_identity_hash72,
            "curriculum_position": beat.curriculum_position,
            "source_id": beat.source_id,
            "source_checksum_sha256": beat.source_checksum_sha256,
            "source_authority": beat.source_authority,
            "rights_class": beat.rights_class,
            "context_id": beat.context_id,
            "evidence_payload_hash72": beat.evidence_payload_hash72,
            "epistemic_status": beat.evidence_epistemic_status,
            "grounding_scope": "LOCAL_CONTEXTUAL_CANDIDATE_ONLY",
            "external_truth_authority": False,
            "action_authority": False,
            "general_english_genesis_mutated": False,
        }
        body["grounding_identity_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I26-GROUNDING-IDENTITY-V1"}, body
        )
        return body

    @staticmethod
    def _validated_relation(relation: Mapping[str, Any], rank: int) -> dict[str, Any]:
        for field in (
            "source_id_hash72",
            "target_id_hash72",
            "beat_relation_hash72",
            "perspective_relation_hash72",
        ):
            if not validate_hash72(str(relation.get(field) or "")):
                raise Pass218I26GroundedManifoldError(
                    f"P218_I26_RELATION_{field.upper()}_INVALID"
                )
        status = relation.get("status")
        if isinstance(status, bool) or not isinstance(status, int) or status not in {-1, 0, 1}:
            raise Pass218I26GroundedManifoldError(
                "P218_I26_RELATION_EXACT_STATUS_INVALID"
            )
        salience = relation.get("perspective_salience_delta")
        if isinstance(salience, bool) or not isinstance(salience, int):
            raise Pass218I26GroundedManifoldError(
                "P218_I26_RELATION_SALIENCE_INTEGER_REQUIRED"
            )
        body = dict(relation)
        body.update(
            {
                "perspective_order_rank": rank,
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
            }
        )
        if "exact_strength" in relation:
            strength = relation["exact_strength"]
            if not isinstance(strength, Mapping):
                raise Pass218I26GroundedManifoldError(
                    "P218_I26_RELATION_EXACT_STRENGTH_INVALID"
                )
            numerator = strength.get("numerator")
            denominator = strength.get("denominator")
            if (
                isinstance(numerator, bool)
                or not isinstance(numerator, int)
                or isinstance(denominator, bool)
                or not isinstance(denominator, int)
                or denominator == 0
            ):
                raise Pass218I26GroundedManifoldError(
                    "P218_I26_RELATION_EXACT_STRENGTH_INVALID"
                )
            body["exact_strength"] = {
                "numerator": numerator,
                "denominator": denominator,
            }
        return body

    @classmethod
    def _grounded_relations(
        cls,
        state: Mapping[str, Any],
        grounding_identity: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        grounded: list[dict[str, Any]] = []
        for rank, raw in enumerate(state.get("perspective_relations", []), start=1):
            if not isinstance(raw, Mapping):
                raise Pass218I26GroundedManifoldError(
                    "P218_I26_RELATION_OBJECT_REQUIRED"
                )
            body = cls._validated_relation(raw, rank)
            body["grounding_identity_hash72"] = grounding_identity[
                "grounding_identity_hash72"
            ]
            body["i25_perspective_context_hash72"] = state[
                "perspective_context_hash72"
            ]
            body["grounded_relation_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I26-GROUNDED-RELATION-V1"}, body
            )
            grounded.append(body)
        return grounded

    @staticmethod
    def _nodes(relations: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        index: dict[str, dict[str, set[str]]] = {}
        for relation in relations:
            relation_hash = str(relation["grounded_relation_hash72"])
            for role in ("source", "target"):
                identity = str(relation[f"{role}_id_hash72"])
                token = str(relation[f"{role}_token"])
                slot = index.setdefault(
                    identity,
                    {"tokens": set(), "roles": set(), "relations": set()},
                )
                slot["tokens"].add(token)
                slot["roles"].add(role.upper())
                slot["relations"].add(relation_hash)
        nodes: list[dict[str, Any]] = []
        for identity in sorted(index):
            slot = index[identity]
            body = {
                "distinction_id_hash72": identity,
                "observed_tokens": sorted(slot["tokens"]),
                "participation_roles": sorted(slot["roles"]),
                "grounded_relation_hashes": sorted(slot["relations"]),
                "candidate_only": True,
                "semantic_priority_minted": False,
                "truth_authority": False,
            }
            body["grounded_node_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I26-GROUNDED-NODE-V1"}, body
            )
            nodes.append(body)
        return nodes

    @staticmethod
    def _relation_layers(relations: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[str]] = {}
        for relation in relations:
            key = (
                str(relation.get("relation_type") or ""),
                str(relation.get("provenance") or ""),
            )
            grouped.setdefault(key, []).append(
                str(relation["grounded_relation_hash72"])
            )
        layers: list[dict[str, Any]] = []
        for relation_type, provenance in sorted(grouped):
            body = {
                "relation_type": relation_type,
                "provenance": provenance,
                "grounded_relation_hashes": sorted(grouped[(relation_type, provenance)]),
                "relation_count": len(grouped[(relation_type, provenance)]),
                "orthogonal_layer_preserved": True,
                "formal_analogical_typing_applied": False,
            }
            body["relation_layer_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I26-RELATION-LAYER-V1"}, body
            )
            layers.append(body)
        return layers

    @staticmethod
    def _polarity_conflicts(relations: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
        for relation in relations:
            key = (
                str(relation["source_id_hash72"]),
                str(relation["target_id_hash72"]),
            )
            grouped.setdefault(key, []).append(relation)
        conflicts: list[dict[str, Any]] = []
        for key in sorted(grouped):
            members = grouped[key]
            statuses = sorted({int(item["status"]) for item in members})
            if -1 not in statuses or 1 not in statuses:
                continue
            body = {
                "source_id_hash72": key[0],
                "target_id_hash72": key[1],
                "status_polarities": statuses,
                "grounded_relation_hashes": sorted(
                    str(item["grounded_relation_hash72"]) for item in members
                ),
                "conflict_state": "REVISABLE_MIXED_POLARITY_CANDIDATE",
                "conflict_resolution_invoked": False,
                "truth_resolution_invoked": False,
            }
            body["polarity_conflict_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I26-POLARITY-CONFLICT-V1"}, body
            )
            conflicts.append(body)
        return conflicts

    def construct(self, request: Pass218I26ManifoldRequest) -> dict[str, Any]:
        validated = request.validated()
        try:
            self._validated_i25_status()
            perspective_request = validated.perspective_request
            state = self._validated_i25_state(perspective_request)
            grounding_identity = self._grounding_identity(perspective_request, state)
            relations = self._grounded_relations(state, grounding_identity)
            nodes = self._nodes(relations)
            layers = self._relation_layers(relations)
            conflicts = self._polarity_conflicts(relations)

            conservation = {
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
            manifold_core = {
                "grounding_identity": grounding_identity,
                "i24_narrative_beat_hash72": state["i24_narrative_beat_hash72"],
                "i25_perspective_context_hash72": state["perspective_context_hash72"],
                "i25_perspective_state_hash72": state["perspective_state_hash72"],
                "perspective_profile": dict(state["perspective_profile"]),
                "active_context": dict(state["active_context"]),
                "attention_configuration": dict(state["attention_configuration"]),
                "manifold_nodes": nodes,
                "manifold_relations": relations,
                "relation_layers": layers,
                "polarity_conflict_candidates": conflicts,
                "node_count": len(nodes),
                "relation_count": len(relations),
                "relation_layer_count": len(layers),
                "polarity_conflict_candidate_count": len(conflicts),
                "topology_conservation": conservation,
            }
            manifold_state_hash72 = hash72_digest(
                {"domain": PASS218_I26_GROUNDED_MANIFOLD_SCHEMA},
                manifold_core,
            )
            receipt_body = {
                "i25_perspective_context_hash72": state["perspective_context_hash72"],
                "grounding_identity_hash72": grounding_identity[
                    "grounding_identity_hash72"
                ],
                "manifold_state_hash72": manifold_state_hash72,
                "node_count": len(nodes),
                "relation_count": len(relations),
                "relation_layer_count": len(layers),
                "candidate_structure_validated": True,
                "topology_conservation_validated": all(conservation.values()),
                "formal_analogical_typing_verified": False,
                "hash216_continuation_verified": False,
                "vm81_authorization_verified": False,
                "canonical_mutation_permitted": False,
                "truth_promotion_permitted": False,
                "action_authority_permitted": False,
            }
            receipt = {
                **receipt_body,
                "manifold_validation_receipt_hash72": hash72_digest(
                    {"domain": "HHS-P218-I26-MANIFOLD-VALIDATION-RECEIPT-V1"},
                    receipt_body,
                ),
            }
            body = {
                "schema": PASS218_I26_GROUNDED_MANIFOLD_SCHEMA,
                "version": PASS218_I26_GROUNDED_MANIFOLD_VERSION,
                **manifold_core,
                "manifold_state_hash72": manifold_state_hash72,
                "validation_receipt": receipt,
                "i20_binding_hash72": state.get("i20_binding_hash72"),
                "i21_batch_hash72": state.get("i21_batch_hash72"),
                "i22_graph_hash72": state.get("i22_graph_hash72"),
                "i23_contextual_state_hash72": state.get("i23_contextual_state_hash72"),
                "grounded_relational_manifold_status": (
                    "REVISABLE_GROUNDED_RELATIONAL_MANIFOLD_CANDIDATE"
                ),
                "grounded_relational_manifold_candidate_ready": True,
                "grounding_invoked": True,
                "grounding_canonical": False,
                "perspective_hydration_invoked": True,
                "perspective_hydration_canonical": False,
                "grounded_relational_manifold_ready": False,
                "grounded_relational_manifold_promoted": False,
                "formal_analogical_typing_invoked": False,
                "hash216_continuation_identity": None,
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
            manifold_hash72 = hash72_digest(
                {"domain": "HHS-P218-I26-GROUNDED-MANIFOLD-RESULT-V1"}, body
            )
            result = {**body, "grounded_relational_manifold_hash72": manifold_hash72}
            self.manifold_count += 1
            self.last_manifold_hash72 = manifold_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I26GroundedManifoldError):
                raise
            raise Pass218I26GroundedManifoldError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i25 = self.i25_control.status()
        ready = (
            bool(i25.get("perspective_context_candidate_ready"))
            and i25.get("perspective_context_status")
            == "REVISABLE_PERSPECTIVE_CONTEXT_HYDRATION_CANDIDATE"
            and not any(bool(i25.get(field)) for field in self._FORBIDDEN_I25_TRUE)
        )
        return {
            "schema": PASS218_I26_STATUS_SCHEMA,
            "version": PASS218_I26_GROUNDED_MANIFOLD_VERSION,
            "grounded_relational_manifold_candidate_ready": ready,
            "manifold_count": self.manifold_count,
            "last_manifold_hash72": self.last_manifold_hash72,
            "i26_error_code": self.last_error_code,
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


__all__ = [
    "I26_REQUIRED_CONSERVATION_FIELDS",
    "PASS218_I26_GROUNDED_MANIFOLD_SCHEMA",
    "PASS218_I26_GROUNDED_MANIFOLD_VERSION",
    "PASS218_I26_STATUS_SCHEMA",
    "Pass218I26GroundedManifoldError",
    "Pass218I26GroundedRelationalManifold",
    "Pass218I26ManifoldRequest",
]
