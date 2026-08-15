"""Pass 218 Iteration 25 governed perspective/context hydration candidates.

Iteration 25 consumes only the typed, revisable narrative-beat transition
candidates emitted by Iteration 24. It applies a separately versioned
perspective profile as a local organization/salience membrane while preserving
the underlying relation direction, relation type, exact status, provenance,
curriculum identity, context, and epistemic modality.

User-authored and explicitly accepted perspective rules may affect local
organization. Inferred perspective rules remain visible candidate annotations
until separately accepted/versioned. This iteration does not promote a
grounded relational manifold, formal/analogical typing, Hash216 continuation,
VM5184/VM81 authority, truth, action authority, or canonical learning.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest

PASS218_I25_PERSPECTIVE_CONTEXT_VERSION = "HHS-P218-I25-PERSPECTIVE-CONTEXT-V1"
PASS218_I25_PERSPECTIVE_CONTEXT_SCHEMA = (
    "HHS-P218-I25-PERSPECTIVE-CONTEXT-CANDIDATE-V1"
)
PASS218_I25_STATUS_SCHEMA = "HHS-P218-I25-PERSPECTIVE-CONTEXT-STATUS-V1"

MAX_I25_PROFILE_ID_LENGTH = 512
MAX_I25_PROFILE_VERSION_LENGTH = 128
MAX_I25_RULE_ID_LENGTH = 256
MAX_I25_RULES = 72
MAX_I25_SELECTOR_VALUES = 72
MAX_I25_SALIENCE_DELTA = 72

_SPACE = re.compile(r"\s+")

I25_PROFILE_ORIGINS = frozenset(
    {
        "USER_AUTHORED",
        "EXPLICITLY_ACCEPTED",
        "INFERRED_CANDIDATE",
    }
)


class Pass218I25PerspectiveContextError(RuntimeError):
    """Fail-closed Iteration 25 perspective/context hydration error."""


class Pass218I24NarrativeBeatControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def assemble(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...


def _normalize_id(value: str, *, code: str, max_length: int) -> str:
    normalized = _SPACE.sub(" ", str(value).strip())
    if not normalized:
        raise Pass218I25PerspectiveContextError(f"{code}_REQUIRED")
    if len(normalized) > max_length:
        raise Pass218I25PerspectiveContextError(f"{code}_TOO_LONG")
    return normalized


def _normalize_class(value: str, *, code: str) -> str:
    normalized = str(value).strip().upper()
    if not normalized:
        raise Pass218I25PerspectiveContextError(f"{code}_REQUIRED")
    if len(normalized) > 128:
        raise Pass218I25PerspectiveContextError(f"{code}_TOO_LONG")
    return normalized


def _normalize_token(value: str, *, code: str) -> str:
    normalized = _SPACE.sub(" ", str(value).strip().lower())
    if not normalized:
        raise Pass218I25PerspectiveContextError(f"{code}_REQUIRED")
    if len(normalized) > 256:
        raise Pass218I25PerspectiveContextError(f"{code}_TOO_LONG")
    return normalized


def _validated_hash72(value: str, *, code: str) -> str:
    digest = str(value)
    if not validate_hash72(digest):
        raise Pass218I25PerspectiveContextError(f"{code}_HASH72_INVALID")
    return digest


@dataclass(frozen=True)
class Pass218I25PerspectiveRule:
    rule_id: str
    rule_payload_hash72: str
    salience_delta: int
    relation_types: tuple[str, ...] = ()
    source_tokens: tuple[str, ...] = ()
    target_tokens: tuple[str, ...] = ()

    def validated(self) -> "Pass218I25PerspectiveRule":
        if isinstance(self.salience_delta, bool) or not isinstance(
            self.salience_delta, int
        ):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_SALIENCE_DELTA_INTEGER_REQUIRED"
            )
        if abs(self.salience_delta) > MAX_I25_SALIENCE_DELTA:
            raise Pass218I25PerspectiveContextError(
                "P218_I25_SALIENCE_DELTA_OUT_OF_RANGE"
            )
        relation_types = tuple(
            sorted(
                {
                    _normalize_class(value, code="P218_I25_RELATION_TYPE")
                    for value in self.relation_types
                }
            )
        )
        source_tokens = tuple(
            sorted(
                {
                    _normalize_token(value, code="P218_I25_SOURCE_TOKEN")
                    for value in self.source_tokens
                }
            )
        )
        target_tokens = tuple(
            sorted(
                {
                    _normalize_token(value, code="P218_I25_TARGET_TOKEN")
                    for value in self.target_tokens
                }
            )
        )
        for values in (relation_types, source_tokens, target_tokens):
            if len(values) > MAX_I25_SELECTOR_VALUES:
                raise Pass218I25PerspectiveContextError(
                    "P218_I25_RULE_SELECTOR_LIMIT"
                )
        return Pass218I25PerspectiveRule(
            rule_id=_normalize_id(
                self.rule_id,
                code="P218_I25_RULE_ID",
                max_length=MAX_I25_RULE_ID_LENGTH,
            ),
            rule_payload_hash72=_validated_hash72(
                self.rule_payload_hash72,
                code="P218_I25_RULE_PAYLOAD",
            ),
            salience_delta=self.salience_delta,
            relation_types=relation_types,
            source_tokens=source_tokens,
            target_tokens=target_tokens,
        )

    def record(self, *, applied_authority: bool) -> dict[str, Any]:
        body = {
            "rule_id": self.rule_id,
            "rule_payload_hash72": self.rule_payload_hash72,
            "salience_delta": self.salience_delta,
            "relation_types": list(self.relation_types),
            "source_tokens": list(self.source_tokens),
            "target_tokens": list(self.target_tokens),
            "applied_authority": applied_authority,
            "truth_authority": False,
            "action_authority": False,
        }
        body["perspective_rule_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I25-PERSPECTIVE-RULE-V1"}, body
        )
        return body


@dataclass(frozen=True)
class Pass218I25PerspectiveProfile:
    profile_id: str
    profile_version: str
    profile_origin: str
    rules: tuple[Pass218I25PerspectiveRule, ...] = ()

    def validated(self) -> "Pass218I25PerspectiveProfile":
        origin = _normalize_class(
            self.profile_origin,
            code="P218_I25_PROFILE_ORIGIN",
        )
        if origin not in I25_PROFILE_ORIGINS:
            raise Pass218I25PerspectiveContextError(
                "P218_I25_PROFILE_ORIGIN_UNSUPPORTED"
            )
        if len(self.rules) > MAX_I25_RULES:
            raise Pass218I25PerspectiveContextError("P218_I25_PROFILE_RULE_LIMIT")
        rules = tuple(
            sorted(
                (rule.validated() for rule in self.rules),
                key=lambda item: (item.rule_id, item.rule_payload_hash72),
            )
        )
        if len({rule.rule_id for rule in rules}) != len(rules):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_DUPLICATE_RULE_ID"
            )
        return Pass218I25PerspectiveProfile(
            profile_id=_normalize_id(
                self.profile_id,
                code="P218_I25_PROFILE_ID",
                max_length=MAX_I25_PROFILE_ID_LENGTH,
            ),
            profile_version=_normalize_id(
                self.profile_version,
                code="P218_I25_PROFILE_VERSION",
                max_length=MAX_I25_PROFILE_VERSION_LENGTH,
            ),
            profile_origin=origin,
            rules=rules,
        )

    @property
    def accepted_for_organization(self) -> bool:
        return self.profile_origin in {"USER_AUTHORED", "EXPLICITLY_ACCEPTED"}


@dataclass(frozen=True)
class Pass218I25PerspectiveRequest:
    beat_request: Pass218I24BeatRequest
    perspective_profile: Pass218I25PerspectiveProfile

    def validated(self) -> "Pass218I25PerspectiveRequest":
        return Pass218I25PerspectiveRequest(
            beat_request=self.beat_request.validated(),
            perspective_profile=self.perspective_profile.validated(),
        )


class Pass218I25PerspectiveContextHydrator:
    """Apply a versioned perspective as local organization, never authority."""

    _FORBIDDEN_I24_TRUE = (
        "narrative_beat_integration_invoked",
        "perspective_hydration_invoked",
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

    def __init__(self, i24_control: Pass218I24NarrativeBeatControlProtocol) -> None:
        self.i24_control = i24_control
        self.hydration_count = 0
        self.last_perspective_state_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _validated_i24_status(self) -> dict[str, Any]:
        status = self.i24_control.status()
        if not bool(status.get("narrative_beat_candidate_ready")):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_I24_NARRATIVE_BEAT_PROVIDER_REQUIRED"
            )
        if status.get("narrative_beat_status") != (
            "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE"
        ):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_I24_SEMANTICS_INVALID"
            )
        for field in self._FORBIDDEN_I24_TRUE:
            if bool(status.get(field)):
                raise Pass218I25PerspectiveContextError(
                    f"P218_I25_I24_SAFETY_DRIFT:{field}"
                )
        return status

    def _validated_i24_beat(
        self,
        request: Pass218I25PerspectiveRequest,
    ) -> dict[str, Any]:
        beat = self.i24_control.assemble(
            self._beat_payload(request.beat_request)
        )
        if beat.get("narrative_beat_status") != (
            "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE"
        ):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_I24_BEAT_SEMANTICS_INVALID"
            )
        for field in self._FORBIDDEN_I24_TRUE:
            if bool(beat.get(field)):
                raise Pass218I25PerspectiveContextError(
                    f"P218_I25_I24_BEAT_SAFETY_DRIFT:{field}"
                )
        beat_hash = str(beat.get("narrative_beat_hash72") or "")
        if not validate_hash72(beat_hash):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_I24_BEAT_HASH72_REQUIRED"
            )
        if bool(beat.get("admitted_predecessor_state")):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_I24_ADMITTED_PREDECESSOR_FORBIDDEN"
            )
        return beat

    @staticmethod
    def _beat_payload(request: Pass218I24BeatRequest) -> dict[str, Any]:
        return {
            "tokens": list(request.tokens),
            "context_id": request.context_id,
            "curriculum_identity_hash72": request.curriculum_identity_hash72,
            "curriculum_position": request.curriculum_position,
            "source_identity": {
                "source_id": request.source_id,
                "source_checksum_sha256": request.source_checksum_sha256,
                "source_authority": request.source_authority,
                "rights_class": request.rights_class,
            },
            "evidence": {
                "evidence_id": request.evidence_id,
                "evidence_type": request.evidence_type,
                "epistemic_status": request.evidence_epistemic_status,
                "payload_hash72": request.evidence_payload_hash72,
            },
            "attention_tokens": list(request.attention_tokens),
            "top_k": request.top_k,
            "attention_radius": request.attention_radius,
            "max_hydrated_nodes": request.max_hydrated_nodes,
            "allowed_relation_families": list(request.allowed_relation_families),
        }

    @staticmethod
    def _profile_record(profile: Pass218I25PerspectiveProfile) -> dict[str, Any]:
        applied = profile.accepted_for_organization
        rules = [rule.record(applied_authority=applied) for rule in profile.rules]
        body = {
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
            "profile_origin": profile.profile_origin,
            "accepted_for_organization": applied,
            "rules": rules,
            "separately_versioned_from_general_english_genesis": True,
            "general_english_genesis_mutated": False,
            "inferred_rules_require_separate_acceptance": True,
        }
        body["perspective_profile_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I25-PERSPECTIVE-PROFILE-V1"}, body
        )
        return body

    @staticmethod
    def _rule_matches(
        rule: Pass218I25PerspectiveRule,
        relation: Mapping[str, Any],
    ) -> bool:
        relation_type = str(relation.get("relation_type") or "").upper()
        source = str(relation.get("source_token") or "").lower()
        target = str(relation.get("target_token") or "").lower()
        if rule.relation_types and relation_type not in rule.relation_types:
            return False
        if rule.source_tokens and source not in rule.source_tokens:
            return False
        if rule.target_tokens and target not in rule.target_tokens:
            return False
        return True

    @classmethod
    def _hydrate_relations(
        cls,
        beat: Mapping[str, Any],
        profile: Pass218I25PerspectiveProfile,
        profile_record: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        hydrated: list[dict[str, Any]] = []
        rule_records = {
            rule.rule_id: record
            for rule, record in zip(profile.rules, profile_record["rules"])
        }
        for relation in beat.get("candidate_relations", []):
            base = dict(relation)
            applied_hashes: list[str] = []
            candidate_hashes: list[str] = []
            salience_delta = 0
            for rule in profile.rules:
                if not cls._rule_matches(rule, relation):
                    continue
                rule_hash = str(rule_records[rule.rule_id]["perspective_rule_hash72"])
                if profile.accepted_for_organization:
                    salience_delta += rule.salience_delta
                    applied_hashes.append(rule_hash)
                else:
                    candidate_hashes.append(rule_hash)
            body = {
                **base,
                "perspective_profile_hash72": profile_record[
                    "perspective_profile_hash72"
                ],
                "perspective_salience_delta": salience_delta,
                "applied_perspective_rule_hashes": sorted(applied_hashes),
                "candidate_perspective_rule_hashes": sorted(candidate_hashes),
                "relation_direction_preserved": True,
                "relation_type_preserved": True,
                "exact_status_preserved": True,
                "provenance_preserved": True,
                "truth_promotion": False,
            }
            body["perspective_relation_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I25-PERSPECTIVE-RELATION-V1"}, body
            )
            hydrated.append(body)
        hydrated.sort(
            key=lambda item: (
                -int(item["perspective_salience_delta"]),
                str(item["source_id_hash72"]),
                str(item["relation_type"]),
                str(item["target_id_hash72"]),
                str(item["perspective_relation_hash72"]),
            )
        )
        return hydrated

    def hydrate(self, request: Pass218I25PerspectiveRequest) -> dict[str, Any]:
        validated = request.validated()
        try:
            self._validated_i24_status()
            beat = self._validated_i24_beat(validated)
            profile = validated.perspective_profile
            profile_record = self._profile_record(profile)
            relations = self._hydrate_relations(beat, profile, profile_record)

            conservation = {
                "beat_identity_preserved": True,
                "curriculum_identity_preserved": True,
                "source_identity_preserved": True,
                "context_identity_preserved": True,
                "attention_configuration_preserved": True,
                "relation_direction_preserved": True,
                "relation_type_preserved": True,
                "exact_status_preserved": True,
                "epistemic_modality_preserved": True,
                "provenance_preserved": True,
                "curriculum_location_preserved": True,
                "authorization_not_widened": True,
                "validation_status_not_promoted": True,
            }
            perspective_state_core = {
                "i24_narrative_beat_hash72": beat["narrative_beat_hash72"],
                "i24_beat_id_hash72": beat["beat_id"],
                "i24_successor_candidate_root": beat["successor_candidate_root"],
                "perspective_profile": profile_record,
                "active_context": dict(beat["active_context"]),
                "attention_configuration": dict(beat["attention_configuration"]),
                "perspective_relations": relations,
                "candidate_relation_count": len(relations),
                "accepted_rule_count": (
                    len(profile.rules) if profile.accepted_for_organization else 0
                ),
                "inferred_candidate_rule_count": (
                    0 if profile.accepted_for_organization else len(profile.rules)
                ),
                "meaning_conservation": conservation,
            }
            perspective_state_hash72 = hash72_digest(
                {"domain": PASS218_I25_PERSPECTIVE_CONTEXT_SCHEMA},
                perspective_state_core,
            )
            receipt_body = {
                "i24_narrative_beat_hash72": beat["narrative_beat_hash72"],
                "perspective_profile_hash72": profile_record[
                    "perspective_profile_hash72"
                ],
                "perspective_state_hash72": perspective_state_hash72,
                "profile_authority_applied": profile.accepted_for_organization,
                "candidate_structure_validated": True,
                "meaning_conservation_validated": all(conservation.values()),
                "grounded_relational_manifold_promoted": False,
                "hash216_continuation_verified": False,
                "vm81_authorization_verified": False,
                "truth_promotion_permitted": False,
                "action_authority_permitted": False,
            }
            receipt = {
                **receipt_body,
                "perspective_validation_receipt_hash72": hash72_digest(
                    {"domain": "HHS-P218-I25-PERSPECTIVE-VALIDATION-RECEIPT-V1"},
                    receipt_body,
                ),
            }

            body = {
                "schema": PASS218_I25_PERSPECTIVE_CONTEXT_SCHEMA,
                "version": PASS218_I25_PERSPECTIVE_CONTEXT_VERSION,
                **perspective_state_core,
                "perspective_state_hash72": perspective_state_hash72,
                "validation_receipt": receipt,
                "i20_binding_hash72": beat.get("i20_binding_hash72"),
                "i21_batch_hash72": beat.get("i21_batch_hash72"),
                "i22_graph_hash72": beat.get("i22_graph_hash72"),
                "i23_contextual_state_hash72": beat.get(
                    "i23_contextual_state_hash72"
                ),
                "perspective_context_status": (
                    "REVISABLE_PERSPECTIVE_CONTEXT_HYDRATION_CANDIDATE"
                ),
                "perspective_context_candidate_ready": True,
                "perspective_hydration_invoked": True,
                "perspective_hydration_canonical": False,
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
            result_hash72 = hash72_digest(
                {"domain": "HHS-P218-I25-PERSPECTIVE-CONTEXT-RESULT-V1"},
                body,
            )
            result = {**body, "perspective_context_hash72": result_hash72}
            self.hydration_count += 1
            self.last_perspective_state_hash72 = result_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I25PerspectiveContextError):
                raise
            raise Pass218I25PerspectiveContextError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i24 = self.i24_control.status()
        ready = (
            bool(i24.get("narrative_beat_candidate_ready"))
            and i24.get("narrative_beat_status")
            == "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE"
            and not any(bool(i24.get(field)) for field in self._FORBIDDEN_I24_TRUE)
        )
        return {
            "schema": PASS218_I25_STATUS_SCHEMA,
            "version": PASS218_I25_PERSPECTIVE_CONTEXT_VERSION,
            "perspective_context_candidate_ready": ready,
            "hydration_count": self.hydration_count,
            "last_perspective_state_hash72": self.last_perspective_state_hash72,
            "i25_error_code": self.last_error_code,
            "perspective_context_status": (
                "REVISABLE_PERSPECTIVE_CONTEXT_HYDRATION_CANDIDATE"
            ),
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


__all__ = [
    "I25_PROFILE_ORIGINS",
    "MAX_I25_PROFILE_ID_LENGTH",
    "MAX_I25_PROFILE_VERSION_LENGTH",
    "MAX_I25_RULES",
    "MAX_I25_SALIENCE_DELTA",
    "PASS218_I25_PERSPECTIVE_CONTEXT_SCHEMA",
    "PASS218_I25_PERSPECTIVE_CONTEXT_VERSION",
    "PASS218_I25_STATUS_SCHEMA",
    "Pass218I25PerspectiveContextError",
    "Pass218I25PerspectiveContextHydrator",
    "Pass218I25PerspectiveProfile",
    "Pass218I25PerspectiveRequest",
    "Pass218I25PerspectiveRule",
]
