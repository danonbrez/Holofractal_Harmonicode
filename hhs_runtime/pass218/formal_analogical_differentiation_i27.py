"""Pass 218 Iteration 27 formal/analogical relation differentiation.

Iteration 27 consumes only the frozen Iteration 26 grounded relational manifold
candidate. It adds a deterministic, non-authoritative differentiation layer
that keeps upstream relation type, direction, polarity, provenance, exact
strength, grounding identity, and perspective order intact while separating
formal/analogical relation families.

Differentiation is descriptive candidate typing only. It does not verify
Hash216 continuation, invoke authoritative VM5184 projection or VM81 mutation
authority, promote truth, mint action authority, activate models, retain
verbatim corpus sources, create authoritative float weights, or commit
canonical learning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.grounded_manifold_i26 import Pass218I26ManifoldRequest

PASS218_I27_DIFFERENTIATION_VERSION = "HHS-P218-I27-FORMAL-ANALOGICAL-DIFFERENTIATION-V1"
PASS218_I27_DIFFERENTIATION_SCHEMA = (
    "HHS-P218-I27-FORMAL-ANALOGICAL-DIFFERENTIATION-CANDIDATE-V1"
)
PASS218_I27_STATUS_SCHEMA = "HHS-P218-I27-FORMAL-ANALOGICAL-DIFFERENTIATION-STATUS-V1"

I27_RELATION_FAMILIES = (
    "ASSOCIATION",
    "SIMILARITY",
    "SYMBOLIZATION",
    "IMPLICATION",
    "CAUSALITY",
    "IDENTITY_FORMAL_ENTAILMENT",
    "ANALOGY",
    "COUNTERFACTUAL_IMAGINATION",
    "CONTRADICTION",
    "EMPIRICAL_OBSERVATION",
)

I27_REQUIRED_TOPOLOGY_FIELDS = (
    "i24_beat_identity_preserved",
    "i25_perspective_identity_preserved",
    "curriculum_identity_preserved",
    "source_identity_preserved",
    "context_identity_preserved",
    "attention_configuration_preserved",
    "perspective_order_preserved",
    "relation_direction_preserved",
    "relation_type_preserved",
    "exact_status_preserved",
    "epistemic_modality_preserved",
    "provenance_preserved",
    "orthogonal_relation_layers_preserved",
    "authorization_not_widened",
    "validation_status_not_promoted",
)

_EXPLICIT_RELATION_TYPE_FAMILY = {
    "ASSOCIATION": "ASSOCIATION",
    "CO_OCCURRENCE": "ASSOCIATION",
    "DISTRIBUTIONAL_NEIGHBOR": "ASSOCIATION",
    "SIMILARITY": "SIMILARITY",
    "SEMANTIC_SIMILARITY": "SIMILARITY",
    "LEXICAL_SYNONYM": "SIMILARITY",
    "SYMBOLIZATION": "SYMBOLIZATION",
    "SYMBOLIZES": "SYMBOLIZATION",
    "REPRESENTS": "SYMBOLIZATION",
    "SIGNIFIES": "SYMBOLIZATION",
    "IMPLICATION": "IMPLICATION",
    "IMPLIES": "IMPLICATION",
    "LEXICAL_HYPERNYM": "IMPLICATION",
    "LEXICAL_HYPONYM": "IMPLICATION",
    "CAUSALITY": "CAUSALITY",
    "CAUSES": "CAUSALITY",
    "CAUSAL_PRECEDENT": "CAUSALITY",
    "IDENTITY": "IDENTITY_FORMAL_ENTAILMENT",
    "EQUIVALENCE": "IDENTITY_FORMAL_ENTAILMENT",
    "FORMAL_ENTAILMENT": "IDENTITY_FORMAL_ENTAILMENT",
    "LOGICAL_ENTAILMENT": "IDENTITY_FORMAL_ENTAILMENT",
    "ANALOGY": "ANALOGY",
    "ANALOGOUS_TO": "ANALOGY",
    "METAPHORICAL_MAPPING": "ANALOGY",
    "COUNTERFACTUAL": "COUNTERFACTUAL_IMAGINATION",
    "IMAGINED": "COUNTERFACTUAL_IMAGINATION",
    "HYPOTHETICAL": "COUNTERFACTUAL_IMAGINATION",
    "COUNTERFACTUAL_IMAGINATION": "COUNTERFACTUAL_IMAGINATION",
    "CONTRADICTION": "CONTRADICTION",
    "CONTRADICTS": "CONTRADICTION",
    "LEXICAL_ANTONYM": "CONTRADICTION",
    "EMPIRICAL_OBSERVATION": "EMPIRICAL_OBSERVATION",
    "OBSERVES": "EMPIRICAL_OBSERVATION",
    "MEASURED_RELATION": "EMPIRICAL_OBSERVATION",
}

_FORMAL_FAMILIES = {
    "IMPLICATION",
    "IDENTITY_FORMAL_ENTAILMENT",
    "CONTRADICTION",
}
_ANALOGICAL_FAMILIES = {"ANALOGY"}

_RELATION_MODES = {
    "ASSOCIATION": "ASSOCIATIVE",
    "SIMILARITY": "COMPARATIVE",
    "SYMBOLIZATION": "SYMBOLIC",
    "IMPLICATION": "FORMAL",
    "CAUSALITY": "CAUSAL",
    "IDENTITY_FORMAL_ENTAILMENT": "FORMAL",
    "ANALOGY": "ANALOGICAL",
    "COUNTERFACTUAL_IMAGINATION": "COUNTERFACTUAL",
    "CONTRADICTION": "FORMAL",
    "EMPIRICAL_OBSERVATION": "EMPIRICAL",
}


class Pass218I27DifferentiationError(RuntimeError):
    """Fail-closed Iteration 27 relation differentiation error."""


class Pass218I26GroundedManifoldControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def construct(self, request: Pass218I26ManifoldRequest) -> dict[str, Any]: ...


@dataclass(frozen=True)
class Pass218I27DifferentiationRequest:
    manifold_request: Pass218I26ManifoldRequest

    def validated(self) -> "Pass218I27DifferentiationRequest":
        return Pass218I27DifferentiationRequest(
            manifold_request=self.manifold_request.validated(),
        )


class Pass218I27FormalAnalogicalDifferentiator:
    """Differentiate grounded candidate relation families without promotion."""

    _FORBIDDEN_I26_TRUE = (
        "grounding_canonical",
        "grounded_relational_manifold_ready",
        "grounded_relational_manifold_promoted",
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

    def __init__(self, i26_control: Pass218I26GroundedManifoldControlProtocol) -> None:
        self.i26_control = i26_control
        self.differentiation_count = 0
        self.last_differentiation_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _validated_i26_status(self) -> dict[str, Any]:
        status = self.i26_control.status()
        if not bool(status.get("grounded_relational_manifold_candidate_ready")):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_GROUNDED_MANIFOLD_PROVIDER_REQUIRED"
            )
        if status.get("grounded_relational_manifold_status") != (
            "REVISABLE_GROUNDED_RELATIONAL_MANIFOLD_CANDIDATE"
        ):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_SEMANTICS_INVALID"
            )
        for field in self._FORBIDDEN_I26_TRUE:
            if bool(status.get(field)):
                raise Pass218I27DifferentiationError(
                    f"P218_I27_I26_SAFETY_DRIFT:{field}"
                )
        return status

    def _validated_i26_state(
        self,
        request: Pass218I26ManifoldRequest,
    ) -> dict[str, Any]:
        state = self.i26_control.construct(request)
        if state.get("grounded_relational_manifold_status") != (
            "REVISABLE_GROUNDED_RELATIONAL_MANIFOLD_CANDIDATE"
        ):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_STATE_SEMANTICS_INVALID"
            )
        if not bool(state.get("grounded_relational_manifold_candidate_ready")):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_STATE_NOT_READY"
            )
        if not bool(state.get("grounding_invoked")):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_GROUNDING_REQUIRED"
            )
        for field in self._FORBIDDEN_I26_TRUE:
            if bool(state.get(field)):
                raise Pass218I27DifferentiationError(
                    f"P218_I27_I26_STATE_SAFETY_DRIFT:{field}"
                )
        for field in (
            "grounded_relational_manifold_hash72",
            "manifold_state_hash72",
            "i24_narrative_beat_hash72",
            "i25_perspective_context_hash72",
        ):
            if not validate_hash72(str(state.get(field) or "")):
                raise Pass218I27DifferentiationError(
                    f"P218_I27_I26_{field.upper()}_REQUIRED"
                )
        grounding = state.get("grounding_identity")
        if not isinstance(grounding, Mapping) or not validate_hash72(
            str(grounding.get("grounding_identity_hash72") or "")
        ):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_GROUNDING_IDENTITY_REQUIRED"
            )
        conservation = state.get("topology_conservation")
        if not isinstance(conservation, Mapping):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_TOPOLOGY_CONSERVATION_REQUIRED"
            )
        for field in I27_REQUIRED_TOPOLOGY_FIELDS:
            if conservation.get(field) is not True:
                raise Pass218I27DifferentiationError(
                    f"P218_I27_I26_TOPOLOGY_CONSERVATION_INVALID:{field}"
                )
        receipt = state.get("validation_receipt")
        if not isinstance(receipt, Mapping) or receipt.get(
            "topology_conservation_validated"
        ) is not True:
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_VALIDATION_RECEIPT_REQUIRED"
            )
        relations = state.get("manifold_relations")
        if not isinstance(relations, list):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_RELATIONS_LIST_REQUIRED"
            )
        if int(state.get("relation_count", -1)) != len(relations):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_RELATION_COUNT_MISMATCH"
            )
        return state

    @staticmethod
    def _family_for_relation(relation: Mapping[str, Any]) -> tuple[str | None, str]:
        relation_type = str(relation.get("relation_type") or "").strip().upper()
        family = _EXPLICIT_RELATION_TYPE_FAMILY.get(relation_type)
        if family is None:
            return None, "UNRESOLVED_UPSTREAM_RELATION_TYPE"
        return family, "EXPLICIT_UPSTREAM_RELATION_TYPE_MAP"

    @staticmethod
    def _mode_for_family(family: str | None) -> str:
        if family is None:
            return "UNRESOLVED"
        mode = _RELATION_MODES.get(family)
        if mode is None:
            raise Pass218I27DifferentiationError(
                "P218_I27_INTERNAL_RELATION_FAMILY_INVALID"
            )
        return mode

    @classmethod
    def _validated_relation(
        cls,
        relation: Mapping[str, Any],
        expected_rank: int,
    ) -> dict[str, Any]:
        for field in (
            "source_id_hash72",
            "target_id_hash72",
            "grounded_relation_hash72",
            "grounding_identity_hash72",
            "i25_perspective_context_hash72",
        ):
            if not validate_hash72(str(relation.get(field) or "")):
                raise Pass218I27DifferentiationError(
                    f"P218_I27_RELATION_{field.upper()}_INVALID"
                )
        rank = relation.get("perspective_order_rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank != expected_rank:
            raise Pass218I27DifferentiationError(
                "P218_I27_PERSPECTIVE_ORDER_INVALID"
            )
        status = relation.get("status")
        if isinstance(status, bool) or not isinstance(status, int) or status not in {-1, 0, 1}:
            raise Pass218I27DifferentiationError(
                "P218_I27_RELATION_EXACT_STATUS_INVALID"
            )
        if relation.get("relation_direction_preserved") is not True:
            raise Pass218I27DifferentiationError(
                "P218_I27_RELATION_DIRECTION_CONSERVATION_REQUIRED"
            )
        if relation.get("relation_type_preserved") is not True:
            raise Pass218I27DifferentiationError(
                "P218_I27_RELATION_TYPE_CONSERVATION_REQUIRED"
            )
        if relation.get("exact_status_preserved") is not True:
            raise Pass218I27DifferentiationError(
                "P218_I27_RELATION_STATUS_CONSERVATION_REQUIRED"
            )
        if bool(relation.get("formal_relation_type_assigned")) or bool(
            relation.get("analogical_relation_type_assigned")
        ):
            raise Pass218I27DifferentiationError(
                "P218_I27_I26_PREMATURE_TYPING_DETECTED"
            )

        family, basis = cls._family_for_relation(relation)
        body = dict(relation)
        body.update(
            {
                "upstream_relation_type": relation["relation_type"],
                "relation_family_candidate": family,
                "differentiation_mode": cls._mode_for_family(family),
                "differentiation_basis": basis,
                "relation_family_resolved": family is not None,
                "formal_relation_type_assigned": (
                    family in _FORMAL_FAMILIES if family is not None else False
                ),
                "analogical_relation_type_assigned": (
                    family in _ANALOGICAL_FAMILIES if family is not None else False
                ),
                "association_relation_type_assigned": family == "ASSOCIATION",
                "similarity_relation_type_assigned": family == "SIMILARITY",
                "symbolization_relation_type_assigned": family == "SYMBOLIZATION",
                "causal_relation_type_assigned": family == "CAUSALITY",
                "counterfactual_relation_type_assigned": (
                    family == "COUNTERFACTUAL_IMAGINATION"
                ),
                "empirical_observation_relation_type_assigned": (
                    family == "EMPIRICAL_OBSERVATION"
                ),
                "formal_entailment_verified": False,
                "causality_verified": False,
                "empirical_observation_verified": False,
                "logical_contradiction_verified": False,
                "upstream_relation_type_preserved": True,
                "relation_direction_preserved": True,
                "exact_status_preserved": True,
                "provenance_preserved": True,
                "perspective_order_preserved": True,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
            }
        )
        body["differentiated_relation_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I27-DIFFERENTIATED-RELATION-V1"},
            body,
        )
        return body

    @classmethod
    def _differentiate_relations(
        cls,
        relations: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        differentiated: list[dict[str, Any]] = []
        for rank, raw in enumerate(relations, start=1):
            if not isinstance(raw, Mapping):
                raise Pass218I27DifferentiationError(
                    "P218_I27_RELATION_OBJECT_REQUIRED"
                )
            differentiated.append(cls._validated_relation(raw, rank))
        return differentiated

    @staticmethod
    def _family_layers(relations: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[str]] = {}
        for relation in relations:
            family = relation.get("relation_family_candidate")
            key = str(family) if family is not None else "UNRESOLVED"
            grouped.setdefault(key, []).append(
                str(relation["differentiated_relation_hash72"])
            )
        layers: list[dict[str, Any]] = []
        for family in sorted(grouped):
            body = {
                "relation_family_candidate": None if family == "UNRESOLVED" else family,
                "relation_count": len(grouped[family]),
                "differentiated_relation_hashes": sorted(grouped[family]),
                "candidate_only": True,
                "cross_family_collapse_invoked": False,
                "truth_resolution_invoked": False,
            }
            body["relation_family_layer_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I27-RELATION-FAMILY-LAYER-V1"},
                body,
            )
            layers.append(body)
        return layers

    @staticmethod
    def _taxonomy_manifest() -> dict[str, Any]:
        body = {
            "relation_families": list(I27_RELATION_FAMILIES),
            "formal_families": sorted(_FORMAL_FAMILIES),
            "analogical_families": sorted(_ANALOGICAL_FAMILIES),
            "relation_modes": dict(sorted(_RELATION_MODES.items())),
            "unknown_relation_types_fail_closed_to_unresolved": True,
            "family_assignment_is_truth_promotion": False,
            "family_assignment_is_action_authority": False,
        }
        body["taxonomy_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I27-RELATION-TAXONOMY-V1"},
            body,
        )
        return body

    def differentiate(
        self,
        request: Pass218I27DifferentiationRequest,
    ) -> dict[str, Any]:
        validated = request.validated()
        try:
            self._validated_i26_status()
            state = self._validated_i26_state(validated.manifold_request)
            relations = self._differentiate_relations(state["manifold_relations"])
            family_layers = self._family_layers(relations)
            taxonomy = self._taxonomy_manifest()
            unresolved = [
                item for item in relations if not bool(item["relation_family_resolved"])
            ]
            observed_families = sorted(
                {
                    str(item["relation_family_candidate"])
                    for item in relations
                    if item["relation_family_candidate"] is not None
                }
            )

            conservation = {
                "i26_manifold_identity_preserved": True,
                "grounding_identity_preserved": True,
                "i24_beat_identity_preserved": True,
                "i25_perspective_identity_preserved": True,
                "perspective_order_preserved": True,
                "relation_direction_preserved": True,
                "upstream_relation_type_preserved": True,
                "exact_status_preserved": True,
                "exact_strength_preserved_where_present": True,
                "epistemic_modality_preserved": True,
                "provenance_preserved": True,
                "orthogonal_family_layers_preserved": True,
                "authorization_not_widened": True,
                "validation_status_not_promoted": True,
            }
            core = {
                "i26_grounded_relational_manifold_hash72": state[
                    "grounded_relational_manifold_hash72"
                ],
                "i26_manifold_state_hash72": state["manifold_state_hash72"],
                "grounding_identity": dict(state["grounding_identity"]),
                "i24_narrative_beat_hash72": state["i24_narrative_beat_hash72"],
                "i25_perspective_context_hash72": state[
                    "i25_perspective_context_hash72"
                ],
                "perspective_profile": dict(state["perspective_profile"]),
                "active_context": dict(state["active_context"]),
                "attention_configuration": dict(state["attention_configuration"]),
                "manifold_nodes": [dict(item) for item in state["manifold_nodes"]],
                "polarity_conflict_candidates": [
                    dict(item) for item in state["polarity_conflict_candidates"]
                ],
                "relation_taxonomy": taxonomy,
                "differentiated_relations": relations,
                "relation_family_layers": family_layers,
                "relation_count": len(relations),
                "resolved_relation_count": len(relations) - len(unresolved),
                "unresolved_relation_count": len(unresolved),
                "observed_relation_families": observed_families,
                "relation_family_layer_count": len(family_layers),
                "differentiation_complete": len(unresolved) == 0,
                "meaning_conservation": conservation,
            }
            differentiation_state_hash72 = hash72_digest(
                {"domain": PASS218_I27_DIFFERENTIATION_SCHEMA},
                core,
            )
            receipt_body = {
                "i26_grounded_relational_manifold_hash72": state[
                    "grounded_relational_manifold_hash72"
                ],
                "differentiation_state_hash72": differentiation_state_hash72,
                "taxonomy_hash72": taxonomy["taxonomy_hash72"],
                "relation_count": len(relations),
                "resolved_relation_count": len(relations) - len(unresolved),
                "unresolved_relation_count": len(unresolved),
                "meaning_conservation_validated": all(conservation.values()),
                "truth_promotion_permitted": False,
                "hash216_continuation_verified": False,
                "vm5184_authoritative_projection_verified": False,
                "vm81_authorization_verified": False,
                "canonical_mutation_permitted": False,
                "action_authority_permitted": False,
            }
            receipt = {
                **receipt_body,
                "differentiation_validation_receipt_hash72": hash72_digest(
                    {
                        "domain": (
                            "HHS-P218-I27-DIFFERENTIATION-VALIDATION-RECEIPT-V1"
                        )
                    },
                    receipt_body,
                ),
            }
            body = {
                "schema": PASS218_I27_DIFFERENTIATION_SCHEMA,
                "version": PASS218_I27_DIFFERENTIATION_VERSION,
                **core,
                "differentiation_state_hash72": differentiation_state_hash72,
                "validation_receipt": receipt,
                "i20_binding_hash72": state.get("i20_binding_hash72"),
                "i21_batch_hash72": state.get("i21_batch_hash72"),
                "i22_graph_hash72": state.get("i22_graph_hash72"),
                "i23_contextual_state_hash72": state.get("i23_contextual_state_hash72"),
                "formal_analogical_differentiation_status": (
                    "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
                ),
                "formal_analogical_differentiation_candidate_ready": True,
                "formal_analogical_typing_invoked": True,
                "formal_analogical_typing_canonical": False,
                "grounded_relational_manifold_ready": False,
                "grounded_relational_manifold_promoted": False,
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
            differentiation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I27-DIFFERENTIATION-RESULT-V1"},
                body,
            )
            result = {
                **body,
                "formal_analogical_differentiation_hash72": differentiation_hash72,
            }
            self.differentiation_count += 1
            self.last_differentiation_hash72 = differentiation_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I27DifferentiationError):
                raise
            raise Pass218I27DifferentiationError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i26 = self.i26_control.status()
        ready = (
            bool(i26.get("grounded_relational_manifold_candidate_ready"))
            and i26.get("grounded_relational_manifold_status")
            == "REVISABLE_GROUNDED_RELATIONAL_MANIFOLD_CANDIDATE"
            and not any(bool(i26.get(field)) for field in self._FORBIDDEN_I26_TRUE)
        )
        return {
            "schema": PASS218_I27_STATUS_SCHEMA,
            "version": PASS218_I27_DIFFERENTIATION_VERSION,
            "formal_analogical_differentiation_candidate_ready": ready,
            "differentiation_count": self.differentiation_count,
            "last_differentiation_hash72": self.last_differentiation_hash72,
            "i27_error_code": self.last_error_code,
            "relation_families": list(I27_RELATION_FAMILIES),
            "formal_analogical_differentiation_status": (
                "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
            ),
            "formal_analogical_typing_canonical": False,
            "grounded_relational_manifold_ready": False,
            "grounded_relational_manifold_promoted": False,
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
    "I27_RELATION_FAMILIES",
    "I27_REQUIRED_TOPOLOGY_FIELDS",
    "PASS218_I27_DIFFERENTIATION_SCHEMA",
    "PASS218_I27_DIFFERENTIATION_VERSION",
    "PASS218_I27_STATUS_SCHEMA",
    "Pass218I27DifferentiationError",
    "Pass218I27DifferentiationRequest",
    "Pass218I27FormalAnalogicalDifferentiator",
]
