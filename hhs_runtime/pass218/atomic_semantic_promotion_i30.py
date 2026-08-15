"""Pass 218 Iteration 30 atomic promotion of a validated I29 semantic transition.

I30 is the contract's atomic-promotion stage. It consumes only an exact I29
validated candidate plus an explicit caller-supplied authority grant, re-derives
the VM5184/native projection, constructs a nonverbatim promoted semantic object,
proves grounded and perspective round trips, commits a content-sealed candidate,
verifies the prospective canonical root, and only then atomically replaces the
semantic-store manifest.

The promoted object remains pending the separate verbatim-purge stage. I30 does
not issue a purge receipt, advance the curriculum, invoke VM81 mutation, perform
canonical learning, mint truth/action authority, activate a model, or create
floating-point authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from threading import RLock
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET, validate_hash72
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    PASS218_I28_VM5184_MAPPING_VERSION,
    VM5184_BITS_PER_CELL,
    VM5184_CELL_COUNT,
    VM5184_STATE_BITS,
)
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    PASS218_I29_VALIDATION_SCHEMA,
    Pass218I29ValidationRequest,
)

PASS218_I30_PROMOTION_VERSION = "HHS-P218-I30-ATOMIC-SEMANTIC-PROMOTION-V1"
PASS218_I30_PROMOTED_OBJECT_SCHEMA = "HHS-P218-I30-PROMOTED-SEMANTIC-OBJECT-V1"
PASS218_I30_PROMOTION_RECEIPT_SCHEMA = "HHS-P218-I30-ATOMIC-PROMOTION-RECEIPT-V1"
PASS218_I30_STATUS_SCHEMA = "HHS-P218-I30-ATOMIC-SEMANTIC-PROMOTION-STATUS-V1"
PASS218_I30_TARGET_SCOPE = "PASS218_VALIDATED_HASH216_VM5184_SEMANTIC_PROMOTION"
PASS218_I30_PENDING_PURGE_STATUS = "ATOMICALLY_PROMOTED_PENDING_VERBATIM_PURGE"
PASS218_I30_EMPTY_ROOT_DOMAIN = "HHS-P218-I30-EMPTY-SEMANTIC-STORE-V1"

_MANIFEST_SCHEMA = "HHS-P218-I30-ATOMIC-SEMANTIC-MANIFEST-V1"
_CANDIDATE_SCHEMA = "HHS-P218-I30-PROMOTION-CANDIDATE-COMMIT-V1"
_GENERATION_SCHEMA = "HHS-P218-I30-PROMOTED-GENERATION-V1"


class Pass218I30PromotionError(RuntimeError):
    """Fail-closed I30 promotion error."""


class Pass218I30PromotionValidationError(Pass218I30PromotionError):
    pass


class Pass218I30PromotionStateError(Pass218I30PromotionError):
    pass


class Pass218I29ValidationControlProtocol(Protocol):
    def validate(self, request: Pass218I29ValidationRequest) -> dict[str, Any]: ...


class Pass218I27DifferentiationControlProtocol(Protocol):
    def differentiate(self, request: Any) -> dict[str, Any]: ...


class Pass218I30NativeBridgeProtocol(Protocol):
    @staticmethod
    def abi_status() -> dict[str, object]: ...
    @staticmethod
    def state_root(words: Sequence[int]) -> str: ...
    @staticmethod
    def project_full(words: Sequence[int]) -> list[list[int]]: ...
    @staticmethod
    def projection_root(channels: Sequence[Sequence[int]]) -> str: ...


class Pass218I30LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...
    def status(self) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I30PromotionValidationError("P218_I30_AUTHORITATIVE_FLOAT_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _reject_float(child)


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _copy(value: Any) -> Any:
    return json.loads(_canonical_bytes(value).decode("utf-8"))


def _valid_hash216(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(symbol in HASH72_ALPHABET for symbol in value)
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(symbol in "0123456789abcdef" for symbol in value)
    )


def _require_hash72(value: object, code: str) -> str:
    text = str(value or "")
    if not validate_hash72(text):
        raise Pass218I30PromotionValidationError(code)
    return text


_FORBIDDEN_RETAINED_KEYS = {
    "source_text",
    "source_bytes",
    "raw_source",
    "raw_source_text",
    "verbatim_source",
    "verbatim_text",
    "source_passage",
    "source_excerpt",
    "paragraph_text",
    "full_text",
    "managed_buffer",
    "managed_buffer_b64",
    "retained_token_stream",
    "token_stream",
}


def _reject_retained_source_surface(value: Any) -> None:
    """Reject raw/verbatim source-bearing fields from the promoted authority."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in _FORBIDDEN_RETAINED_KEYS and child not in (None, "", [], {}):
                raise Pass218I30PromotionValidationError(
                    "P218_I30_SOURCE_RETENTION_FIELD_FORBIDDEN:" + str(key)
                )
            if normalized in {
                "verbatim_source_retained",
                "verbatim_corpus_source_retained",
                "source_token_stream_retained",
            } and child is not False:
                raise Pass218I30PromotionValidationError(
                    "P218_I30_VERBATIM_RETENTION_FORBIDDEN:" + str(key)
                )
            _reject_retained_source_surface(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_retained_source_surface(child)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".p218-i30-", suffix=".tmp", dir=str(path.parent))
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        try:
            directory_fd = os.open(str(path.parent), os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _read_canonical_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise Pass218I30PromotionValidationError(
            "P218_I30_PERSISTED_RECORD_UNREADABLE:" + path.name
        ) from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218I30PromotionValidationError(
            "P218_I30_PERSISTED_RECORD_NONCANONICAL:" + path.name
        )
    _reject_retained_source_surface(value)
    return value


@dataclass(frozen=True)
class Pass218I30PromotionRequest:
    validation_request: Pass218I29ValidationRequest
    grantor_authority_hash72: str
    grant_sequence: int
    expected_i29_validation_hash72: str
    expected_validated_hash216: str
    target_scope: str = PASS218_I30_TARGET_SCOPE

    def validated(self) -> "Pass218I30PromotionRequest":
        validation_request = self.validation_request.validated()
        grantor = _require_hash72(
            self.grantor_authority_hash72,
            "P218_I30_GRANTOR_AUTHORITY_HASH72_INVALID",
        )
        expected_validation = _require_hash72(
            self.expected_i29_validation_hash72,
            "P218_I30_EXPECTED_I29_VALIDATION_HASH72_INVALID",
        )
        if (
            not isinstance(self.grant_sequence, int)
            or isinstance(self.grant_sequence, bool)
            or self.grant_sequence < 0
        ):
            raise Pass218I30PromotionValidationError("P218_I30_GRANT_SEQUENCE_INVALID")
        if not _valid_hash216(self.expected_validated_hash216):
            raise Pass218I30PromotionValidationError("P218_I30_EXPECTED_VALIDATED_HASH216_INVALID")
        if self.target_scope != PASS218_I30_TARGET_SCOPE:
            raise Pass218I30PromotionValidationError("P218_I30_GRANT_SCOPE_INVALID")
        return Pass218I30PromotionRequest(
            validation_request=validation_request,
            grantor_authority_hash72=grantor,
            grant_sequence=self.grant_sequence,
            expected_i29_validation_hash72=expected_validation,
            expected_validated_hash216=self.expected_validated_hash216,
            target_scope=self.target_scope,
        )


def _normalized_relation(relation: Mapping[str, Any], rank: int) -> dict[str, Any]:
    required_hash72 = (
        "source_id_hash72",
        "target_id_hash72",
        "grounded_relation_hash72",
        "differentiated_relation_hash72",
        "grounding_identity_hash72",
    )
    for field in required_hash72:
        _require_hash72(relation.get(field), "P218_I30_RELATION_HASH72_INVALID:" + field)
    if relation.get("perspective_order_rank") != rank:
        raise Pass218I30PromotionValidationError("P218_I30_RELATION_ORDER_INVALID")
    status = relation.get("status")
    if isinstance(status, bool) or not isinstance(status, int) or status not in {-1, 0, 1}:
        raise Pass218I30PromotionValidationError("P218_I30_RELATION_STATUS_INVALID")

    fields = (
        "source_id_hash72",
        "target_id_hash72",
        "grounded_relation_hash72",
        "differentiated_relation_hash72",
        "grounding_identity_hash72",
        "perspective_order_rank",
        "relation_type",
        "upstream_relation_type",
        "relation_family_candidate",
        "differentiation_mode",
        "differentiation_basis",
        "status",
        "exact_strength",
        "provenance",
        "epistemic_status",
        "evidence_epistemic_status",
        "modality",
        "uncertainty",
        "negation_scope",
        "temporal_order",
        "causal_order",
        "authorization_status",
        "validation_status",
        "relation_family_resolved",
        "formal_relation_type_assigned",
        "analogical_relation_type_assigned",
        "association_relation_type_assigned",
        "similarity_relation_type_assigned",
        "symbolization_relation_type_assigned",
        "causal_relation_type_assigned",
        "counterfactual_relation_type_assigned",
        "empirical_observation_relation_type_assigned",
        "formal_entailment_verified",
        "causality_verified",
        "empirical_observation_verified",
        "logical_contradiction_verified",
        "upstream_relation_type_preserved",
        "relation_direction_preserved",
        "exact_status_preserved",
        "provenance_preserved",
        "perspective_order_preserved",
    )
    result = {field: _copy(relation[field]) for field in fields if field in relation}
    result["source_text_retained"] = False
    result["source_token_stream_retained"] = False
    _reject_retained_source_surface(result)
    return result


def _expected_relation_word(relation: Mapping[str, Any], expected_rank: int) -> int:
    if relation.get("perspective_order_rank") != expected_rank:
        raise Pass218I30PromotionValidationError("P218_I30_RELATION_ORDER_INVALID")
    projection = {
        "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
        "perspective_order_rank": expected_rank,
        "source_id_hash72": relation["source_id_hash72"],
        "target_id_hash72": relation["target_id_hash72"],
        "grounded_relation_hash72": relation["grounded_relation_hash72"],
        "differentiated_relation_hash72": relation["differentiated_relation_hash72"],
        "relation_type": relation.get("relation_type"),
        "relation_family_candidate": relation.get("relation_family_candidate"),
        "differentiation_mode": relation.get("differentiation_mode"),
        "status": relation.get("status"),
        "exact_strength": relation.get("exact_strength"),
        "provenance": relation.get("provenance"),
        "grounding_identity_hash72": relation["grounding_identity_hash72"],
    }
    return int.from_bytes(sha256(_canonical_bytes(projection)).digest()[:8], "big")


def _expected_words(relations: Sequence[Mapping[str, Any]]) -> list[int]:
    if len(relations) > VM5184_CELL_COUNT:
        raise Pass218I30PromotionValidationError("P218_I30_VM5184_CAPACITY_EXCEEDED")
    words = [0] * VM5184_CELL_COUNT
    for rank, relation in enumerate(relations, start=1):
        words[rank - 1] = _expected_relation_word(relation, rank)
    return words


def _profile_projection(profile: Mapping[str, Any]) -> dict[str, Any]:
    rules = profile.get("rules", [])
    rule_rows: list[dict[str, Any]] = []
    if isinstance(rules, list):
        for row in rules:
            if not isinstance(row, Mapping):
                continue
            projected = {
                key: _copy(row[key])
                for key in (
                    "rule_id",
                    "rule_payload_hash72",
                    "perspective_rule_hash72",
                    "salience_delta",
                    "applied_authority",
                )
                if key in row
            }
            rule_rows.append(projected)
    result = {
        key: _copy(profile[key])
        for key in (
            "profile_id",
            "profile_version",
            "profile_origin",
            "accepted_for_organization",
            "separately_versioned_from_general_english_genesis",
            "general_english_genesis_mutated",
            "inferred_rules_require_separate_acceptance",
            "perspective_profile_hash72",
        )
        if key in profile
    }
    result["rule_witnesses"] = rule_rows
    result["source_token_stream_retained"] = False
    return result


def _semantic_packages(i27: Mapping[str, Any], i29: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    relations_raw = i27.get("differentiated_relations")
    if not isinstance(relations_raw, list):
        raise Pass218I30PromotionValidationError("P218_I30_I27_RELATIONS_REQUIRED")
    normalized = [
        _normalized_relation(relation, rank)
        for rank, relation in enumerate(relations_raw, start=1)
        if isinstance(relation, Mapping)
    ]
    if len(normalized) != len(relations_raw):
        raise Pass218I30PromotionValidationError("P218_I30_I27_RELATION_OBJECT_REQUIRED")

    witness = i29.get("semantic_validation_witness")
    if not isinstance(witness, Mapping):
        raise Pass218I30PromotionValidationError("P218_I30_I29_SEMANTIC_WITNESS_REQUIRED")
    expected_hashes = [row["differentiated_relation_hash72"] for row in normalized]
    if witness.get("differentiated_relation_hashes") != expected_hashes:
        raise Pass218I30PromotionValidationError("P218_I30_SEMANTIC_WITNESS_RELATION_MISMATCH")

    grounding = i27.get("grounding_identity")
    if not isinstance(grounding, Mapping):
        raise Pass218I30PromotionValidationError("P218_I30_GROUNDING_IDENTITY_REQUIRED")
    _reject_retained_source_surface(grounding)

    grounded_graph = {
        "i27_formal_analogical_differentiation_hash72": i27[
            "formal_analogical_differentiation_hash72"
        ],
        "i27_differentiation_state_hash72": i27["differentiation_state_hash72"],
        "i26_grounded_relational_manifold_hash72": i27[
            "i26_grounded_relational_manifold_hash72"
        ],
        "grounding_identity": _copy(grounding),
        "relation_taxonomy": _copy(i27.get("relation_taxonomy", {})),
        "relation_family_layers": _copy(i27.get("relation_family_layers", [])),
        "relations": normalized,
        "relation_count": len(normalized),
        "resolved_relation_count": int(i27.get("resolved_relation_count", -1)),
        "unresolved_relation_count": int(i27.get("unresolved_relation_count", -1)),
        "meaning_conservation": _copy(i27.get("meaning_conservation", {})),
        "upstream_semantic_roots": {
            key: i27.get(key)
            for key in (
                "i20_binding_hash72",
                "i21_batch_hash72",
                "i22_graph_hash72",
                "i23_contextual_state_hash72",
                "i24_narrative_beat_hash72",
                "i25_perspective_context_hash72",
                "i26_grounded_relational_manifold_hash72",
            )
        },
        "source_text_retained": False,
        "source_token_stream_retained": False,
    }

    active_context = i27.get("active_context", {})
    attention = i27.get("attention_configuration", {})
    if not isinstance(active_context, Mapping) or not isinstance(attention, Mapping):
        raise Pass218I30PromotionValidationError("P218_I30_PERSPECTIVE_CONTEXT_REQUIRED")
    profile = i27.get("perspective_profile", {})
    if not isinstance(profile, Mapping):
        raise Pass218I30PromotionValidationError("P218_I30_PERSPECTIVE_PROFILE_REQUIRED")
    perspective_context = {
        "i24_narrative_beat_hash72": i27["i24_narrative_beat_hash72"],
        "i25_perspective_context_hash72": i27["i25_perspective_context_hash72"],
        "perspective_profile": _profile_projection(profile),
        "active_context_hash72": hash72_digest(
            {"domain": "HHS-P218-I30-ACTIVE-CONTEXT-WITNESS-V1"}, active_context
        ),
        "attention_configuration_hash72": hash72_digest(
            {"domain": "HHS-P218-I30-ATTENTION-CONFIGURATION-WITNESS-V1"}, attention
        ),
        "perspective_order_sequence": [row["perspective_order_rank"] for row in normalized],
        "relation_family_sequence": [row.get("relation_family_candidate") for row in normalized],
        "relation_type_sequence": [row.get("relation_type") for row in normalized],
        "status_sequence": [row.get("status") for row in normalized],
        "source_text_retained": False,
        "source_token_stream_retained": False,
    }
    _reject_retained_source_surface(grounded_graph)
    _reject_retained_source_surface(perspective_context)
    return grounded_graph, perspective_context


class Pass218I30AtomicSemanticStore:
    """Content-sealed candidate/generation store with one atomic manifest swap."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.candidates = self.root / "candidates"
        self.generations = self.root / "generations"
        self.manifest_path = self.root / "manifest.json"
        self._lock = RLock()

    @staticmethod
    def empty_root_hash72() -> str:
        return hash72_digest({"domain": PASS218_I30_EMPTY_ROOT_DOMAIN}, {"empty": True})

    def _active_locked(self) -> tuple[dict[str, Any], dict[str, Any]] | None:
        if not self.manifest_path.exists():
            return None
        manifest = _read_canonical_json(self.manifest_path)
        if manifest.get("schema") != _MANIFEST_SCHEMA:
            raise Pass218I30PromotionValidationError("P218_I30_MANIFEST_SCHEMA_INVALID")
        generation_name = str(manifest.get("active_generation") or "")
        if not generation_name or Path(generation_name).name != generation_name:
            raise Pass218I30PromotionValidationError("P218_I30_MANIFEST_GENERATION_INVALID")
        generation_path = self.generations / generation_name
        generation = _read_canonical_json(generation_path)
        raw = _canonical_bytes(generation)
        if sha256(raw).hexdigest() != manifest.get("generation_sha256"):
            raise Pass218I30PromotionValidationError("P218_I30_GENERATION_SHA256_MISMATCH")
        if generation.get("schema") != _GENERATION_SCHEMA:
            raise Pass218I30PromotionValidationError("P218_I30_GENERATION_SCHEMA_INVALID")
        receipt = generation.get("promotion_receipt")
        promoted = generation.get("promoted_object")
        if not isinstance(receipt, Mapping) or not isinstance(promoted, Mapping):
            raise Pass218I30PromotionValidationError("P218_I30_GENERATION_CONTENT_INVALID")
        if receipt.get("target_root_after_hash72") != manifest.get("canonical_root_hash72"):
            raise Pass218I30PromotionValidationError("P218_I30_MANIFEST_ROOT_MISMATCH")
        if promoted.get("promoted_object_hash72") != manifest.get("promoted_object_hash72"):
            raise Pass218I30PromotionValidationError("P218_I30_MANIFEST_OBJECT_MISMATCH")
        return manifest, generation

    def status(self) -> dict[str, Any]:
        with self._lock:
            active = self._active_locked()
            if active is None:
                return {
                    "canonical_root_hash72": self.empty_root_hash72(),
                    "promotion_present": False,
                    "promotion_status": "EMPTY",
                    "purge_status": "NOT_APPLICABLE",
                }
            manifest, generation = active
            receipt = generation["promotion_receipt"]
            return {
                "canonical_root_hash72": manifest["canonical_root_hash72"],
                "promotion_present": True,
                "promotion_status": receipt["promotion_status"],
                "purge_status": receipt["purge_status"],
                "i29_validation_hash72": receipt["i29_validation_hash72"],
                "promoted_object_hash72": receipt["promoted_object_hash72"],
                "promotion_receipt_hash72": receipt["promotion_receipt_hash72"],
                "grant_hash72": receipt["grant_hash72"],
            }

    def active_generation(self) -> dict[str, Any] | None:
        with self._lock:
            active = self._active_locked()
            return None if active is None else _copy(active[1])

    def commit_candidate(self, candidate: Mapping[str, Any]) -> tuple[str, str]:
        record = _copy(candidate)
        _reject_retained_source_surface(record)
        if record.get("schema") != _CANDIDATE_SCHEMA:
            raise Pass218I30PromotionValidationError("P218_I30_CANDIDATE_SCHEMA_INVALID")
        raw = _canonical_bytes(record)
        digest = sha256(raw).hexdigest()
        filename = f"candidate-{digest}.json"
        path = self.candidates / filename
        if path.exists():
            if path.read_bytes() != raw:
                raise Pass218I30PromotionStateError("P218_I30_CANDIDATE_CONTENT_CONFLICT")
        else:
            _atomic_write(path, raw)
        reread = _read_canonical_json(path)
        if _canonical_bytes(reread) != raw:
            raise Pass218I30PromotionValidationError("P218_I30_CANDIDATE_VERIFY_FAILED")
        return filename, digest

    def atomic_promote(
        self,
        *,
        promoted_object: Mapping[str, Any],
        candidate_filename: str,
        candidate_sha256: str,
        grant_hash72: str,
        i29_validation_hash72: str,
        validated_hash216: str,
        target_root_before_hash72: str,
        target_root_after_hash72: str,
        root_verification_hash72: str,
        promotion_hash72: str,
        promotion_receipt_hash72: str,
        promotion_hash216: str,
        fail_before_atomic_swap: bool = False,
    ) -> dict[str, Any]:
        with self._lock:
            active = self._active_locked()
            if active is not None:
                manifest, generation = active
                receipt = generation["promotion_receipt"]
                if (
                    receipt.get("i29_validation_hash72") == i29_validation_hash72
                    and receipt.get("grant_hash72") == grant_hash72
                    and receipt.get("promoted_object_hash72")
                    == promoted_object.get("promoted_object_hash72")
                ):
                    return _copy(receipt)
                raise Pass218I30PromotionStateError(
                    "P218_I30_PREVIOUS_PROMOTION_PENDING_PURGE"
                )
            if target_root_before_hash72 != self.empty_root_hash72():
                raise Pass218I30PromotionStateError("P218_I30_TARGET_ROOT_CHANGED_AFTER_PREPARE")

            receipt = {
                "schema": PASS218_I30_PROMOTION_RECEIPT_SCHEMA,
                "version": PASS218_I30_PROMOTION_VERSION,
                "i29_validation_hash72": i29_validation_hash72,
                "validated_hash216": validated_hash216,
                "promoted_object_hash72": promoted_object["promoted_object_hash72"],
                "candidate_filename": candidate_filename,
                "candidate_sha256": candidate_sha256,
                "grant_hash72": grant_hash72,
                "target_root_before_hash72": target_root_before_hash72,
                "target_root_after_hash72": target_root_after_hash72,
                "root_verification_hash72": root_verification_hash72,
                "promotion_hash72": promotion_hash72,
                "promotion_receipt_hash72": promotion_receipt_hash72,
                "promotion_hash216": promotion_hash216,
                "promotion_status": PASS218_I30_PENDING_PURGE_STATUS,
                "candidate_commit_verified": True,
                "prospective_root_verified": True,
                "formal_semantic_round_trip_verified": True,
                "grounded_round_trip_verified": True,
                "perspective_round_trip_verified": True,
                "vm5184_authoritative_projection_invoked": True,
                "vm5184_authoritative_state_committed": True,
                "vm81_authorization_invoked": False,
                "atomic_promotion_authorized": True,
                "atomic_promotion_invoked": True,
                "atomic_manifest_swap": True,
                "failed_partial_promotion_possible": False,
                "purge_status": "PENDING_VERBATIM_PURGE",
                "verbatim_purge_invoked": False,
                "purge_receipt_issued": False,
                "curriculum_advance_permitted": False,
                "closure_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
            _reject_retained_source_surface(receipt)
            generation = {
                "schema": _GENERATION_SCHEMA,
                "version": PASS218_I30_PROMOTION_VERSION,
                "promoted_object": _copy(promoted_object),
                "promotion_receipt": receipt,
            }
            raw_generation = _canonical_bytes(generation)
            generation_sha256 = sha256(raw_generation).hexdigest()
            generation_name = f"promotion-{generation_sha256}.json"
            generation_path = self.generations / generation_name
            if not generation_path.exists():
                _atomic_write(generation_path, raw_generation)
            elif generation_path.read_bytes() != raw_generation:
                raise Pass218I30PromotionStateError("P218_I30_GENERATION_CONTENT_CONFLICT")

            manifest = {
                "schema": _MANIFEST_SCHEMA,
                "version": PASS218_I30_PROMOTION_VERSION,
                "active_generation": generation_name,
                "generation_sha256": generation_sha256,
                "canonical_root_hash72": target_root_after_hash72,
                "promoted_object_hash72": promoted_object["promoted_object_hash72"],
                "i29_validation_hash72": i29_validation_hash72,
                "promotion_receipt_hash72": promotion_receipt_hash72,
                "purge_status": "PENDING_VERBATIM_PURGE",
                "curriculum_advance_permitted": False,
            }
            if fail_before_atomic_swap:
                raise Pass218I30PromotionStateError(
                    "P218_I30_INJECTED_FAILURE_BEFORE_ATOMIC_PROMOTION"
                )
            _atomic_write(self.manifest_path, _canonical_bytes(manifest))
            verified = self._active_locked()
            if verified is None or verified[0] != manifest:
                raise Pass218I30PromotionStateError("P218_I30_ATOMIC_MANIFEST_VERIFY_FAILED")
            return _copy(receipt)


class Pass218I30AtomicSemanticPromoter:
    """Validate, authorize, round-trip, candidate-commit, verify, atomically promote."""

    def __init__(
        self,
        i29_control: Pass218I29ValidationControlProtocol,
        i27_control: Pass218I27DifferentiationControlProtocol,
        *,
        lifecycle: Pass218I30LifecycleProtocol,
        store_root: str | os.PathLike[str],
        native_bridge: Pass218I30NativeBridgeProtocol | None = None,
    ) -> None:
        self.i29_control = i29_control
        self.i27_control = i27_control
        self.lifecycle = lifecycle
        self.store = Pass218I30AtomicSemanticStore(store_root)
        self._native_bridge_override = native_bridge
        self.promotion_count = 0
        self.last_promotion_receipt_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _native_bridge(self) -> Pass218I30NativeBridgeProtocol:
        if self._native_bridge_override is not None:
            return self._native_bridge_override
        from hhs_python.runtime.hhs_pass205_continuation_bridge import Pass205NativeBridge

        return Pass205NativeBridge

    @staticmethod
    def decode_grounded(promoted_object: Mapping[str, Any]) -> dict[str, Any]:
        payload = promoted_object.get("semantic_payload")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("grounded_graph"), Mapping):
            raise Pass218I30PromotionValidationError("P218_I30_PROMOTED_GROUNDED_GRAPH_MISSING")
        return _copy(payload["grounded_graph"])

    @staticmethod
    def decode_perspective(promoted_object: Mapping[str, Any]) -> dict[str, Any]:
        payload = promoted_object.get("semantic_payload")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("perspective_context"), Mapping):
            raise Pass218I30PromotionValidationError("P218_I30_PROMOTED_PERSPECTIVE_CONTEXT_MISSING")
        return _copy(payload["perspective_context"])

    def promote(
        self,
        request: Pass218I30PromotionRequest,
        *,
        fail_before_atomic_swap: bool = False,
    ) -> dict[str, Any]:
        validated = request.validated()
        try:
            self.lifecycle.require_ingestion_ready()
            i29 = self.i29_control.validate(validated.validation_request)
            if i29.get("schema") != PASS218_I29_VALIDATION_SCHEMA:
                raise Pass218I30PromotionValidationError("P218_I30_I29_SCHEMA_INVALID")
            if i29.get("hash216_vm5184_validation_status") != (
                "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
            ):
                raise Pass218I30PromotionValidationError("P218_I30_I29_STATUS_INVALID")
            required_true = (
                "hash216_continuation_verified",
                "semantic_transition_validated",
                "vm5184_candidate_projection_verified",
                "candidate_semantic_binding_verified",
                "atomic_promotion_candidate_ready",
            )
            if any(i29.get(field) is not True for field in required_true):
                raise Pass218I30PromotionValidationError("P218_I30_I29_VALIDATION_INCOMPLETE")
            required_false = (
                "formal_semantic_round_trip_verified",
                "atomic_promotion_authorized",
                "vm5184_authoritative_projection_invoked",
                "vm81_authorization_invoked",
                "atomic_promotion_invoked",
                "truth_promotion",
                "action_authority_minted",
                "canonical_learning_commit_invoked",
                "model_activation_invoked",
                "verbatim_corpus_source_retained",
                "authoritative_float_weights_created",
            )
            if any(bool(i29.get(field)) for field in required_false):
                raise Pass218I30PromotionValidationError("P218_I30_I29_AUTHORITY_DRIFT")

            i29_hash72 = _require_hash72(
                i29.get("hash216_vm5184_validation_hash72"),
                "P218_I30_I29_VALIDATION_HASH72_INVALID",
            )
            validated_hash216 = str(i29.get("pass218_validated_hash216") or "")
            if i29_hash72 != validated.expected_i29_validation_hash72:
                raise Pass218I30PromotionValidationError("P218_I30_EXPECTED_I29_VALIDATION_MISMATCH")
            if validated_hash216 != validated.expected_validated_hash216:
                raise Pass218I30PromotionValidationError("P218_I30_EXPECTED_VALIDATED_HASH216_MISMATCH")

            i27 = self.i27_control.differentiate(
                validated.validation_request.transition_request.differentiation_request
            )
            if i27.get("formal_analogical_differentiation_hash72") != i29.get(
                "i27_formal_analogical_differentiation_hash72"
            ):
                raise Pass218I30PromotionValidationError("P218_I30_I27_IDENTITY_MISMATCH")
            relations = i27.get("differentiated_relations")
            if not isinstance(relations, list):
                raise Pass218I30PromotionValidationError("P218_I30_I27_RELATIONS_REQUIRED")
            words = _expected_words(relations)
            bridge = self._native_bridge()
            abi = bridge.abi_status()
            expected_abi = {
                "state_bits": VM5184_STATE_BITS,
                "cell_count": VM5184_CELL_COUNT,
                "bits_per_cell": VM5184_BITS_PER_CELL,
                "canonical_float_fields": 0,
            }
            for field, expected in expected_abi.items():
                if int(abi.get(field, -1)) != expected:
                    raise Pass218I30PromotionValidationError("P218_I30_PASS205_ABI_MISMATCH:" + field)
            projection = bridge.project_full(words)
            state_root216 = bridge.state_root(words)
            projection_root216 = bridge.projection_root(projection)
            native_validation = i29.get("native_validation")
            if not isinstance(native_validation, Mapping):
                raise Pass218I30PromotionValidationError("P218_I30_I29_NATIVE_VALIDATION_REQUIRED")
            if state_root216 != native_validation.get("state_root216"):
                raise Pass218I30PromotionValidationError("P218_I30_NATIVE_STATE_ROOT_MISMATCH")
            if projection_root216 != native_validation.get("projection_root216"):
                raise Pass218I30PromotionValidationError("P218_I30_NATIVE_PROJECTION_ROOT_MISMATCH")
            if not _valid_hash216(state_root216) or not _valid_hash216(projection_root216):
                raise Pass218I30PromotionValidationError("P218_I30_NATIVE_ROOT_FORMAT_INVALID")

            grounded_graph, perspective_context = _semantic_packages(i27, i29)
            witness = i29["semantic_validation_witness"]
            semantic_witness_hash72 = _require_hash72(
                witness.get("semantic_witness_hash72"),
                "P218_I30_SEMANTIC_WITNESS_HASH72_INVALID",
            )
            grant_body = {
                "grantor_authority_hash72": validated.grantor_authority_hash72,
                "grant_sequence": validated.grant_sequence,
                "target_scope": validated.target_scope,
                "i29_validation_hash72": i29_hash72,
                "validated_hash216": validated_hash216,
                "semantic_witness_hash72": semantic_witness_hash72,
                "explicit_authority_grant_present": True,
                "grant_authorizes_only_exact_validated_candidate": True,
                "truth_promotion": False,
                "action_authority_minted": False,
                "learning_authority_granted": False,
            }
            grant_hash72 = hash72_digest(
                {"domain": "HHS-P218-I30-PROMOTION-AUTHORITY-GRANT-V1"}, grant_body
            )

            promoted_body = {
                "schema": PASS218_I30_PROMOTED_OBJECT_SCHEMA,
                "version": PASS218_I30_PROMOTION_VERSION,
                "i29_validation_hash72": i29_hash72,
                "i28_transition_hash72": i29["i28_hash216_vm5184_transition_hash72"],
                "validated_hash216": validated_hash216,
                "validation_receipt_hash72": i29["validation_receipt"][
                    "validation_receipt_hash72"
                ],
                "semantic_witness_hash72": semantic_witness_hash72,
                "grant_hash72": grant_hash72,
                "semantic_payload": {
                    "grounded_graph": grounded_graph,
                    "perspective_context": perspective_context,
                },
                "vm5184_authority": {
                    "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
                    "state_bits": VM5184_STATE_BITS,
                    "cell_count": VM5184_CELL_COUNT,
                    "bits_per_cell": VM5184_BITS_PER_CELL,
                    "state_words": words,
                    "populated_relation_cells": len(relations),
                    "zero_padded_cells": VM5184_CELL_COUNT - len(relations),
                    "native_state_root216": state_root216,
                    "native_projection_root216": projection_root216,
                    "native_continuation_root216": native_validation[
                        "continuation_root216"
                    ],
                    "authoritative_projection": True,
                    "vm81_mutation": False,
                    "canonical_float_fields": 0,
                },
                "retained_artifact_allowlist": [
                    "checksums_and_identity_metadata",
                    "typed_relational_graph",
                    "lexical_relation_identifiers",
                    "context_and_perspective_hash_witnesses",
                    "relation_taxonomy_and_status",
                    "vm5184_exact_state",
                    "validation_and_lineage_receipts",
                ],
                "source_text_retained": False,
                "source_token_stream_retained": False,
                "verbatim_corpus_source_retained": False,
                "purge_status": "PENDING_VERBATIM_PURGE",
                "curriculum_advance_permitted": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
            _reject_retained_source_surface(promoted_body)
            promoted_hash72 = hash72_digest(
                {"domain": "HHS-P218-I30-PROMOTED-SEMANTIC-OBJECT-V1"}, promoted_body
            )
            promoted_object = {**promoted_body, "promoted_object_hash72": promoted_hash72}

            if self.decode_grounded(promoted_object) != grounded_graph:
                raise Pass218I30PromotionValidationError("P218_I30_GROUNDED_ROUND_TRIP_FAILED")
            if self.decode_perspective(promoted_object) != perspective_context:
                raise Pass218I30PromotionValidationError("P218_I30_PERSPECTIVE_ROUND_TRIP_FAILED")

            target_before = self.store.status()["canonical_root_hash72"]
            active = self.store.active_generation()
            if active is not None:
                receipt = active["promotion_receipt"]
                if (
                    receipt.get("i29_validation_hash72") == i29_hash72
                    and receipt.get("grant_hash72") == grant_hash72
                    and receipt.get("promoted_object_hash72") == promoted_hash72
                ):
                    return _copy(receipt)
                raise Pass218I30PromotionStateError("P218_I30_PREVIOUS_PROMOTION_PENDING_PURGE")

            candidate_body = {
                "schema": _CANDIDATE_SCHEMA,
                "version": PASS218_I30_PROMOTION_VERSION,
                "i29_validation_hash72": i29_hash72,
                "validated_hash216": validated_hash216,
                "promoted_object_hash72": promoted_hash72,
                "promoted_object": promoted_object,
                "grant": {**grant_body, "grant_hash72": grant_hash72},
                "target_root_before_hash72": target_before,
                "formal_semantic_round_trip_verified": True,
                "grounded_round_trip_verified": True,
                "perspective_round_trip_verified": True,
                "vm5184_projection_rederived": True,
                "candidate_only": True,
                "atomic_promotion_invoked": False,
                "verbatim_corpus_source_retained": False,
            }
            candidate_filename, candidate_sha256 = self.store.commit_candidate(candidate_body)
            candidate_commit_hash72 = hash72_digest(
                {"domain": "HHS-P218-I30-CANDIDATE-COMMIT-V1"},
                {
                    "candidate_filename": candidate_filename,
                    "candidate_sha256": candidate_sha256,
                    "i29_validation_hash72": i29_hash72,
                    "promoted_object_hash72": promoted_hash72,
                    "grant_hash72": grant_hash72,
                    "target_root_before_hash72": target_before,
                },
            )
            target_after = hash72_digest(
                {"domain": "HHS-P218-I30-CANONICAL-SEMANTIC-ROOT-V1"},
                {
                    "previous_root_hash72": target_before,
                    "promoted_object_hash72": promoted_hash72,
                    "i29_validation_hash72": i29_hash72,
                    "validated_hash216": validated_hash216,
                    "grant_hash72": grant_hash72,
                    "candidate_sha256": candidate_sha256,
                },
            )
            root_verification_hash72 = hash72_digest(
                {"domain": "HHS-P218-I30-ROOT-VERIFICATION-V1"},
                {
                    "candidate_commit_hash72": candidate_commit_hash72,
                    "target_root_before_hash72": target_before,
                    "prospective_target_root_hash72": target_after,
                    "promoted_object_hash72": promoted_hash72,
                    "native_state_root216": state_root216,
                    "native_projection_root216": projection_root216,
                    "candidate_commit_reloaded_exact": True,
                    "formal_semantic_round_trip_verified": True,
                },
            )
            promotion_hash72 = hash72_digest(
                {"domain": "HHS-P218-I30-ATOMIC-PROMOTION-V1"},
                {
                    "candidate_commit_hash72": candidate_commit_hash72,
                    "root_verification_hash72": root_verification_hash72,
                    "target_root_after_hash72": target_after,
                    "grant_hash72": grant_hash72,
                    "atomic_manifest_swap": True,
                    "purge_deferred_to_next_stage": True,
                },
            )
            promotion_receipt_hash72 = hash72_digest(
                {"domain": "HHS-P218-I30-ATOMIC-PROMOTION-RECEIPT-V1"},
                {
                    "promotion_hash72": promotion_hash72,
                    "target_root_after_hash72": target_after,
                    "promoted_object_hash72": promoted_hash72,
                    "formal_semantic_round_trip_verified": True,
                    "atomic_promotion_invoked": True,
                    "purge_status": "PENDING_VERBATIM_PURGE",
                    "curriculum_advance_permitted": False,
                    "truth_promotion": False,
                    "action_authority_minted": False,
                },
            )
            promotion_hash216 = (
                candidate_commit_hash72 + root_verification_hash72 + promotion_receipt_hash72
            )
            if not _valid_hash216(promotion_hash216):
                raise Pass218I30PromotionValidationError("P218_I30_PROMOTION_HASH216_INVALID")

            receipt = self.store.atomic_promote(
                promoted_object=promoted_object,
                candidate_filename=candidate_filename,
                candidate_sha256=candidate_sha256,
                grant_hash72=grant_hash72,
                i29_validation_hash72=i29_hash72,
                validated_hash216=validated_hash216,
                target_root_before_hash72=target_before,
                target_root_after_hash72=target_after,
                root_verification_hash72=root_verification_hash72,
                promotion_hash72=promotion_hash72,
                promotion_receipt_hash72=promotion_receipt_hash72,
                promotion_hash216=promotion_hash216,
                fail_before_atomic_swap=fail_before_atomic_swap,
            )
            self.promotion_count += 1
            self.last_promotion_receipt_hash72 = receipt["promotion_receipt_hash72"]
            self.last_error_code = None
            return receipt
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I30PromotionError):
                raise
            raise Pass218I30PromotionError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        store = self.store.status()
        lifecycle = self.lifecycle.status()
        return {
            "schema": PASS218_I30_STATUS_SCHEMA,
            "version": PASS218_I30_PROMOTION_VERSION,
            "target_scope": PASS218_I30_TARGET_SCOPE,
            "writer_authority_ready": bool(
                lifecycle.get("ingestion_enabled")
                and lifecycle.get("ownership_writer_authority", True)
            ),
            "promotion_count": self.promotion_count,
            "last_promotion_receipt_hash72": self.last_promotion_receipt_hash72,
            "i30_error_code": self.last_error_code,
            **store,
            "formal_semantic_round_trip_verified": bool(store.get("promotion_present")),
            "atomic_promotion_authorized": bool(store.get("promotion_present")),
            "atomic_promotion_invoked": bool(store.get("promotion_present")),
            "vm5184_authoritative_projection_invoked": bool(store.get("promotion_present")),
            "vm81_authorization_invoked": False,
            "verbatim_purge_invoked": False,
            "purge_receipt_issued": False,
            "curriculum_advance_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "PASS218_I30_PENDING_PURGE_STATUS",
    "PASS218_I30_PROMOTED_OBJECT_SCHEMA",
    "PASS218_I30_PROMOTION_RECEIPT_SCHEMA",
    "PASS218_I30_PROMOTION_VERSION",
    "PASS218_I30_STATUS_SCHEMA",
    "PASS218_I30_TARGET_SCOPE",
    "Pass218I30AtomicSemanticPromoter",
    "Pass218I30AtomicSemanticStore",
    "Pass218I30PromotionError",
    "Pass218I30PromotionRequest",
    "Pass218I30PromotionStateError",
    "Pass218I30PromotionValidationError",
]
