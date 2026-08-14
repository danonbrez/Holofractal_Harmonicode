"""Pass 218 Iteration 24 governed narrative-beat transition candidates.

Iteration 24 consumes only the revisable contextual-state candidates emitted by
Iteration 23 and organizes one bounded, typed, replayable narrative-beat
transition candidate. It binds curriculum, source, context, attention, local
relational state, and nonverbatim evidence identity without claiming that the
I23 predecessor is an admitted global state. It does not perform perspective
hydration, grounded-manifold promotion, Hash216 continuation admission, VM81
mutation authorization, natural-language projection, truth promotion, action
authority, model activation, or canonical learning commit.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.contextual_state_i23 import Pass218I23ContextQuery

PASS218_I24_NARRATIVE_BEAT_VERSION = "HHS-P218-I24-NARRATIVE-BEAT-V1"
PASS218_I24_NARRATIVE_BEAT_SCHEMA = "HHS-P218-I24-NARRATIVE-BEAT-CANDIDATE-V1"
PASS218_I24_STATUS_SCHEMA = "HHS-P218-I24-NARRATIVE-BEAT-STATUS-V1"

MAX_I24_ID_LENGTH = 512
MAX_I24_CLASS_LENGTH = 128
MAX_I24_CURRICULUM_POSITION = 10_000_000

_SPACE = re.compile(r"\s+")
_HEX = frozenset("0123456789abcdef")

I24_EPISTEMIC_STATUSES = frozenset(
    {
        "UNRESOLVED",
        "ASSOCIATED",
        "ANALOGICAL",
        "SYMBOLIC",
        "IMAGINED",
        "COUNTERFACTUAL",
        "FICTIONAL",
        "HYPOTHESIZED",
        "INFERRED",
        "REPORTED",
        "OBSERVED",
        "INTERNALLY_VALIDATED",
        "EXTERNALLY_CORROBORATED",
        "FORMALLY_PROVEN",
        "CONTRADICTED",
        "RETRACTED",
    }
)


class Pass218I24NarrativeBeatError(RuntimeError):
    """Fail-closed Iteration 24 narrative-beat candidate error."""


class Pass218I23ContextualStateControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def hydrate(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...


def _normalize_id(value: str, *, code: str) -> str:
    normalized = _SPACE.sub(" ", str(value).strip())
    if not normalized:
        raise Pass218I24NarrativeBeatError(f"{code}_REQUIRED")
    if len(normalized) > MAX_I24_ID_LENGTH:
        raise Pass218I24NarrativeBeatError(f"{code}_TOO_LONG")
    return normalized


def _normalize_class(value: str, *, code: str) -> str:
    normalized = str(value).strip().upper()
    if not normalized:
        raise Pass218I24NarrativeBeatError(f"{code}_REQUIRED")
    if len(normalized) > MAX_I24_CLASS_LENGTH:
        raise Pass218I24NarrativeBeatError(f"{code}_TOO_LONG")
    return normalized


def _validate_sha256(value: str, *, code: str) -> str:
    digest = str(value).strip().lower()
    if len(digest) != 64 or any(character not in _HEX for character in digest):
        raise Pass218I24NarrativeBeatError(f"{code}_SHA256_INVALID")
    return digest


def _validate_hash72(value: str, *, code: str) -> str:
    digest = str(value)
    if not validate_hash72(digest):
        raise Pass218I24NarrativeBeatError(f"{code}_HASH72_INVALID")
    return digest


@dataclass(frozen=True)
class Pass218I24BeatRequest:
    tokens: tuple[str, ...]
    context_id: str
    curriculum_identity_hash72: str
    curriculum_position: int
    source_id: str
    source_checksum_sha256: str
    source_authority: str
    rights_class: str
    evidence_id: str
    evidence_type: str
    evidence_epistemic_status: str
    evidence_payload_hash72: str
    attention_tokens: tuple[str, ...] = ()
    top_k: int = 8
    attention_radius: int = 1
    max_hydrated_nodes: int = 24
    allowed_relation_families: tuple[str, ...] = ()

    def validated(self) -> "Pass218I24BeatRequest":
        contextual = Pass218I23ContextQuery(
            tokens=self.tokens,
            context_id=self.context_id,
            attention_tokens=self.attention_tokens,
            top_k=self.top_k,
            attention_radius=self.attention_radius,
            max_hydrated_nodes=self.max_hydrated_nodes,
            allowed_relation_families=self.allowed_relation_families,
        ).validated()
        if isinstance(self.curriculum_position, bool) or not isinstance(
            self.curriculum_position, int
        ):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_CURRICULUM_POSITION_INTEGER_REQUIRED"
            )
        if (
            self.curriculum_position < 0
            or self.curriculum_position > MAX_I24_CURRICULUM_POSITION
        ):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_CURRICULUM_POSITION_OUT_OF_RANGE"
            )
        epistemic_status = _normalize_class(
            self.evidence_epistemic_status,
            code="P218_I24_EPISTEMIC_STATUS",
        )
        if epistemic_status not in I24_EPISTEMIC_STATUSES:
            raise Pass218I24NarrativeBeatError(
                "P218_I24_EPISTEMIC_STATUS_UNSUPPORTED"
            )
        return Pass218I24BeatRequest(
            tokens=contextual.tokens,
            context_id=contextual.context_id,
            curriculum_identity_hash72=_validate_hash72(
                self.curriculum_identity_hash72,
                code="P218_I24_CURRICULUM_IDENTITY",
            ),
            curriculum_position=self.curriculum_position,
            source_id=_normalize_id(
                self.source_id,
                code="P218_I24_SOURCE_ID",
            ),
            source_checksum_sha256=_validate_sha256(
                self.source_checksum_sha256,
                code="P218_I24_SOURCE",
            ),
            source_authority=_normalize_class(
                self.source_authority,
                code="P218_I24_SOURCE_AUTHORITY",
            ),
            rights_class=_normalize_class(
                self.rights_class,
                code="P218_I24_RIGHTS_CLASS",
            ),
            evidence_id=_normalize_id(
                self.evidence_id,
                code="P218_I24_EVIDENCE_ID",
            ),
            evidence_type=_normalize_class(
                self.evidence_type,
                code="P218_I24_EVIDENCE_TYPE",
            ),
            evidence_epistemic_status=epistemic_status,
            evidence_payload_hash72=_validate_hash72(
                self.evidence_payload_hash72,
                code="P218_I24_EVIDENCE_PAYLOAD",
            ),
            attention_tokens=contextual.attention_tokens,
            top_k=contextual.top_k,
            attention_radius=contextual.attention_radius,
            max_hydrated_nodes=contextual.max_hydrated_nodes,
            allowed_relation_families=contextual.allowed_relation_families,
        )

    def i23_payload(self) -> dict[str, Any]:
        return {
            "tokens": list(self.tokens),
            "context_id": self.context_id,
            "attention_tokens": list(self.attention_tokens),
            "top_k": self.top_k,
            "attention_radius": self.attention_radius,
            "max_hydrated_nodes": self.max_hydrated_nodes,
            "allowed_relation_families": list(self.allowed_relation_families),
        }


class Pass218I24NarrativeBeatAssembler:
    """Build a typed beat transition candidate without canonical mutation."""

    _FORBIDDEN_I23_TRUE = (
        "narrative_beat_integration_invoked",
        "perspective_hydration_invoked",
        "grounded_relational_manifold_ready",
        "formal_analogical_typing_invoked",
        "authoritative_semantic_compression_ready",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )

    def __init__(self, i23_control: Pass218I23ContextualStateControlProtocol) -> None:
        self.i23_control = i23_control
        self.beat_count = 0
        self.last_beat_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _validated_i23_status(self) -> dict[str, Any]:
        status = self.i23_control.status()
        if not bool(status.get("contextual_state_candidate_ready")):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_I23_CONTEXTUAL_STATE_PROVIDER_REQUIRED"
            )
        if status.get("contextual_state_status") != "REVISABLE_CONTEXTUAL_STATE_CANDIDATE":
            raise Pass218I24NarrativeBeatError("P218_I24_I23_SEMANTICS_INVALID")
        if not bool(status.get("contextual_hydration_candidate_ready")):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_I23_CONTEXTUAL_HYDRATION_REQUIRED"
            )
        for field in self._FORBIDDEN_I23_TRUE:
            if bool(status.get(field)):
                raise Pass218I24NarrativeBeatError(
                    f"P218_I24_I23_SAFETY_DRIFT:{field}"
                )
        return status

    def _validated_i23_state(
        self,
        request: Pass218I24BeatRequest,
        status: Mapping[str, Any],
    ) -> dict[str, Any]:
        state = self.i23_control.hydrate(request.i23_payload())
        if state.get("contextual_state_status") != "REVISABLE_CONTEXTUAL_STATE_CANDIDATE":
            raise Pass218I24NarrativeBeatError(
                "P218_I24_I23_STATE_SEMANTICS_INVALID"
            )
        if not bool(state.get("contextual_hydration_candidate_ready")):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_I23_STATE_HYDRATION_REQUIRED"
            )
        for field in self._FORBIDDEN_I23_TRUE:
            if bool(state.get(field)):
                raise Pass218I24NarrativeBeatError(
                    f"P218_I24_I23_STATE_SAFETY_DRIFT:{field}"
                )
        state_hash72 = str(state.get("contextual_state_hash72") or "")
        if not validate_hash72(state_hash72):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_I23_CONTEXTUAL_STATE_HASH72_REQUIRED"
            )
        if (
            status.get("i20_binding_hash72")
            and state.get("i20_binding_hash72") != status.get("i20_binding_hash72")
        ):
            raise Pass218I24NarrativeBeatError("P218_I24_I20_BINDING_MISMATCH")
        return state

    @staticmethod
    def _source_identity(request: Pass218I24BeatRequest) -> dict[str, Any]:
        body = {
            "source_id": request.source_id,
            "source_checksum_sha256": request.source_checksum_sha256,
            "source_authority": request.source_authority,
            "rights_class": request.rights_class,
            "verbatim_source_retained": False,
        }
        body["source_identity_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I24-SOURCE-IDENTITY-V1"},
            body,
        )
        return body

    @staticmethod
    def _evidence_descriptor(request: Pass218I24BeatRequest) -> dict[str, Any]:
        body = {
            "evidence_id": request.evidence_id,
            "evidence_type": request.evidence_type,
            "declared_epistemic_status": request.evidence_epistemic_status,
            "evidence_payload_hash72": request.evidence_payload_hash72,
            "retention_semantics": "NONVERBATIM_IDENTITY_ONLY",
            "epistemic_status_promoted": False,
            "external_truth_authority": False,
            "action_authority": False,
        }
        body["evidence_descriptor_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I24-EVIDENCE-DESCRIPTOR-V1"},
            body,
        )
        return body

    @staticmethod
    def _candidate_relations(
        hydrated_edges: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for edge in hydrated_edges:
            body: dict[str, Any] = {
                "source_token": str(edge["source_token"]),
                "target_token": str(edge["target_token"]),
                "source_id_hash72": str(edge["source_id_hash72"]),
                "target_id_hash72": str(edge["target_id_hash72"]),
                "relation_type": str(edge["relation_type"]),
                "status": int(edge["status"]),
                "provenance": str(edge["provenance"]),
                "upstream_hash72": str(edge["upstream_hash72"]),
                "i22_edge_hash72": str(edge["edge_hash72"]),
                "candidate_only": True,
                "relation_type_change_applied": False,
                "epistemic_change_applied": False,
                "truth_promotion": False,
            }
            if "exact_strength" in edge:
                strength = edge["exact_strength"]
                body["exact_strength"] = {
                    "numerator": int(strength["numerator"]),
                    "denominator": int(strength["denominator"]),
                }
            body["beat_relation_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I24-BEAT-RELATION-V1"},
                body,
            )
            records.append(body)
        records.sort(
            key=lambda item: (
                item["source_id_hash72"],
                item["relation_type"],
                item["target_id_hash72"],
                item["beat_relation_hash72"],
            )
        )
        return records

    @staticmethod
    def _contradiction_candidates(
        candidate_relations: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
        for relation in candidate_relations:
            key = (
                str(relation["source_id_hash72"]),
                str(relation["target_id_hash72"]),
            )
            grouped.setdefault(key, []).append(relation)

        contradictions: list[dict[str, Any]] = []
        for key in sorted(grouped):
            relations = grouped[key]
            statuses = sorted({int(item["status"]) for item in relations})
            if -1 not in statuses or 1 not in statuses:
                continue
            body = {
                "source_id_hash72": key[0],
                "target_id_hash72": key[1],
                "status_polarities": statuses,
                "candidate_contradiction_state": "MIXED_POLARITY_PRESENT",
                "authoritative_contradiction_change_applied": False,
                "relation_hashes": sorted(
                    str(item["beat_relation_hash72"]) for item in relations
                ),
            }
            body["contradiction_candidate_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I24-CONTRADICTION-CANDIDATE-V1"},
                body,
            )
            contradictions.append(body)
        return contradictions

    @staticmethod
    def _hydrated_neighborhood(state: Mapping[str, Any]) -> dict[str, Any]:
        nodes = [dict(item) for item in state.get("hydrated_nodes", [])]
        participation = [dict(item) for item in state.get("participation", [])]
        return {
            "contextual_state_hash72": state["contextual_state_hash72"],
            "hydrated_nodes": nodes,
            "participation": participation,
            "hydrated_node_count": int(state.get("hydrated_node_count", len(nodes))),
            "hydrated_edge_count": int(state.get("hydrated_edge_count", 0)),
            "attention_active_count": int(state.get("attention_active_count", 0)),
            "candidate_influential_count": int(
                state.get("candidate_influential_count", 0)
            ),
            "memory_scope_semantics": "LOCAL_CONTEXTUAL_PARTICIPATION_ONLY",
        }

    def assemble(self, request: Pass218I24BeatRequest) -> dict[str, Any]:
        validated = request.validated()
        try:
            i23_status = self._validated_i23_status()
            state = self._validated_i23_state(validated, i23_status)
            source_identity = self._source_identity(validated)
            evidence = self._evidence_descriptor(validated)
            candidate_relations = self._candidate_relations(
                state.get("hydrated_edges", [])
            )
            contradiction_changes = self._contradiction_candidates(
                candidate_relations
            )
            neighborhood = self._hydrated_neighborhood(state)
            active_context = dict(state["context_configuration"])
            attention_configuration = {
                "attention_tokens": list(
                    active_context.get("attention_tokens", [])
                ),
                "attention_radius": int(active_context.get("attention_radius", 0)),
                "max_hydrated_nodes": int(
                    active_context.get("max_hydrated_nodes", 0)
                ),
                "allowed_relation_families": list(
                    active_context.get("allowed_relation_families", [])
                ),
                "context_configuration_hash72": state[
                    "context_configuration_hash72"
                ],
            }
            curriculum_identity = {
                "curriculum_identity_hash72": validated.curriculum_identity_hash72,
                "curriculum_position": validated.curriculum_position,
                "identity_verification_scope": "FORMAT_AND_BEAT_BINDING_ONLY",
                "authoritative_curriculum_advance_invoked": False,
            }

            transition_core = {
                "predecessor_root": state["contextual_state_hash72"],
                "predecessor_root_semantics": "I23_REVISABLE_CONTEXTUAL_STATE_CANDIDATE",
                "admitted_predecessor_state": False,
                "curriculum_identity": curriculum_identity,
                "source_identity": source_identity,
                "active_context": active_context,
                "attention_configuration": attention_configuration,
                "hydrated_relational_neighborhood": neighborhood,
                "new_evidence_or_experience": evidence,
                "candidate_relations": candidate_relations,
                "relation_type_changes": [],
                "epistemic_status_changes": [],
                "salience_changes": [],
                "contradiction_changes": contradiction_changes,
                "optional_narrative_projection": None,
                "natural_language_projection_generated": False,
                "relation_change_application_invoked": False,
                "epistemic_change_application_invoked": False,
                "salience_change_application_invoked": False,
                "contradiction_change_application_invoked": False,
            }
            beat_id_hash72 = hash72_digest(
                {"domain": "HHS-P218-I24-BEAT-ID-V1"},
                transition_core,
            )
            successor_candidate_root = hash72_digest(
                {"domain": "HHS-P218-I24-SUCCESSOR-CANDIDATE-V1"},
                {
                    "predecessor_root": state["contextual_state_hash72"],
                    "beat_id_hash72": beat_id_hash72,
                    "evidence_descriptor_hash72": evidence[
                        "evidence_descriptor_hash72"
                    ],
                    "candidate_relation_hashes": [
                        item["beat_relation_hash72"]
                        for item in candidate_relations
                    ],
                    "contradiction_candidate_hashes": [
                        item["contradiction_candidate_hash72"]
                        for item in contradiction_changes
                    ],
                },
            )
            validation_receipt_body = {
                "beat_id_hash72": beat_id_hash72,
                "predecessor_root": state["contextual_state_hash72"],
                "successor_candidate_root": successor_candidate_root,
                "context_configuration_hash72": state[
                    "context_configuration_hash72"
                ],
                "source_identity_hash72": source_identity[
                    "source_identity_hash72"
                ],
                "evidence_descriptor_hash72": evidence[
                    "evidence_descriptor_hash72"
                ],
                "candidate_structure_validated": True,
                "hash216_continuation_verified": False,
                "vm81_authorization_verified": False,
                "canonical_mutation_permitted": False,
                "truth_promotion_permitted": False,
                "action_authority_permitted": False,
            }
            validation_receipt = {
                **validation_receipt_body,
                "validation_receipt_hash72": hash72_digest(
                    {"domain": "HHS-P218-I24-BEAT-VALIDATION-RECEIPT-V1"},
                    validation_receipt_body,
                ),
            }

            body = {
                "schema": PASS218_I24_NARRATIVE_BEAT_SCHEMA,
                "version": PASS218_I24_NARRATIVE_BEAT_VERSION,
                "beat_id": beat_id_hash72,
                **transition_core,
                "successor_candidate_root": successor_candidate_root,
                "successor_root_semantics": "REVISABLE_RELATIONAL_SUCCESSOR_CANDIDATE",
                "validation_receipt": validation_receipt,
                "i20_binding_hash72": state.get("i20_binding_hash72"),
                "i21_batch_hash72": state.get("i21_batch_hash72"),
                "i22_graph_hash72": state.get("i22_graph_hash72"),
                "i23_contextual_state_hash72": state["contextual_state_hash72"],
                "wordnet_asset_manifest_hash72": state.get(
                    "wordnet_asset_manifest_hash72"
                ),
                "narrative_beat_status": "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE",
                "narrative_beat_candidate_ready": True,
                "narrative_beat_integration_invoked": False,
                "perspective_hydration_invoked": False,
                "grounded_relational_manifold_ready": False,
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
            beat_hash72 = hash72_digest(
                {"domain": PASS218_I24_NARRATIVE_BEAT_SCHEMA},
                body,
            )
            result = {**body, "narrative_beat_hash72": beat_hash72}
            self.beat_count += 1
            self.last_beat_hash72 = beat_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I24NarrativeBeatError):
                raise
            raise Pass218I24NarrativeBeatError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i23 = self.i23_control.status()
        ready = (
            bool(i23.get("contextual_state_candidate_ready"))
            and i23.get("contextual_state_status")
            == "REVISABLE_CONTEXTUAL_STATE_CANDIDATE"
            and bool(i23.get("contextual_hydration_candidate_ready"))
            and not any(bool(i23.get(field)) for field in self._FORBIDDEN_I23_TRUE)
        )
        return {
            "schema": PASS218_I24_STATUS_SCHEMA,
            "version": PASS218_I24_NARRATIVE_BEAT_VERSION,
            "narrative_beat_candidate_ready": ready,
            "beat_count": self.beat_count,
            "last_beat_hash72": self.last_beat_hash72,
            "i24_error_code": self.last_error_code,
            "narrative_beat_status": "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE",
            "narrative_beat_integration_invoked": False,
            "perspective_hydration_invoked": False,
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


__all__ = [
    "I24_EPISTEMIC_STATUSES",
    "MAX_I24_CLASS_LENGTH",
    "MAX_I24_CURRICULUM_POSITION",
    "MAX_I24_ID_LENGTH",
    "PASS218_I24_NARRATIVE_BEAT_SCHEMA",
    "PASS218_I24_NARRATIVE_BEAT_VERSION",
    "PASS218_I24_STATUS_SCHEMA",
    "Pass218I24BeatRequest",
    "Pass218I24NarrativeBeatAssembler",
    "Pass218I24NarrativeBeatError",
]
