"""Pass 218 Iteration 29 validation of the frozen I28 Hash216/VM5184 candidate.

I29 is a validation gate only. It independently re-derives the I28 relation-cell
mapping and native Pass205 roots from the frozen I27 semantic state, verifies
the three-segment Hash216 construction, verifies parent/next/receipt continuity,
and emits a real validation-receipt segment.

This module does not perform atomic promotion, authoritative VM5184 projection,
VM81 authorization, canonical learning, truth promotion, model activation,
verbatim retention, or authoritative floating-point work.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET, validate_hash72
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    Pass218I27DifferentiationRequest,
)
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    HASH216_SYMBOL_COUNT,
    PASS218_I28_TRANSITION_SCHEMA,
    PASS218_I28_VM5184_MAPPING_VERSION,
    VM5184_BITS_PER_CELL,
    VM5184_CELL_COUNT,
    VM5184_STATE_BITS,
    Pass218I28TransitionRequest,
)

PASS218_I29_VALIDATION_VERSION = "HHS-P218-I29-HASH216-VM5184-VALIDATION-V1"
PASS218_I29_VALIDATION_SCHEMA = "HHS-P218-I29-HASH216-VM5184-VALIDATED-CANDIDATE-V1"
PASS218_I29_STATUS_SCHEMA = "HHS-P218-I29-HASH216-VM5184-VALIDATION-STATUS-V1"


class Pass218I29ValidationError(RuntimeError):
    """Fail-closed Iteration 29 validation error."""


class Pass218I28TransitionControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def construct(self, request: Pass218I28TransitionRequest) -> dict[str, Any]: ...


class Pass218I27DifferentiationControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def differentiate(self, request: Pass218I27DifferentiationRequest) -> dict[str, Any]: ...


class Pass218I29NativeBridgeProtocol(Protocol):
    @staticmethod
    def abi_status() -> dict[str, object]: ...
    @staticmethod
    def state_root(words: Sequence[int]) -> str: ...
    @staticmethod
    def project_full(words: Sequence[int]) -> list[list[int]]: ...
    @staticmethod
    def projection_root(channels: Sequence[Sequence[int]]) -> str: ...
    @staticmethod
    def hash216_bytes(payload: bytes) -> str: ...
    @staticmethod
    def build_token(**kwargs: Any) -> dict[str, object]: ...


@dataclass(frozen=True)
class Pass218I29ValidationRequest:
    transition_request: Pass218I28TransitionRequest

    def validated(self) -> "Pass218I29ValidationRequest":
        return Pass218I29ValidationRequest(
            transition_request=self.transition_request.validated(),
        )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _valid_hash216(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == HASH216_SYMBOL_COUNT
        and all(symbol in HASH72_ALPHABET for symbol in value)
    )


def _require_hash72(value: object, code: str) -> str:
    text = str(value or "")
    if not validate_hash72(text):
        raise Pass218I29ValidationError(code)
    return text


class Pass218I29Hash216VM5184Validator:
    """Independently validate the I28 transition candidate without promoting it."""

    _FORBIDDEN_I28_TRUE = (
        "hash216_continuation_verified",
        "semantic_transition_validated",
        "vm5184_authoritative_projection_invoked",
        "vm81_authorization_invoked",
        "atomic_promotion_invoked",
        "authoritative_semantic_compression_ready",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )

    def __init__(
        self,
        i28_control: Pass218I28TransitionControlProtocol,
        i27_control: Pass218I27DifferentiationControlProtocol,
        native_bridge: Pass218I29NativeBridgeProtocol | None = None,
    ) -> None:
        self.i28_control = i28_control
        self.i27_control = i27_control
        self._native_bridge_override = native_bridge
        self.validation_count = 0
        self.last_validation_hash72: str | None = None
        self.last_validated_hash216: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _native_bridge(self) -> Pass218I29NativeBridgeProtocol:
        if self._native_bridge_override is not None:
            return self._native_bridge_override
        from hhs_python.runtime.hhs_pass205_continuation_bridge import Pass205NativeBridge

        return Pass205NativeBridge

    def _validated_i28_status(self) -> None:
        status = self.i28_control.status()
        if not bool(status.get("hash216_vm5184_transition_candidate_ready")):
            raise Pass218I29ValidationError("P218_I29_I28_PROVIDER_REQUIRED")
        if status.get("hash216_vm5184_transition_status") != (
            "REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
        ):
            raise Pass218I29ValidationError("P218_I29_I28_STATUS_INVALID")
        for field in self._FORBIDDEN_I28_TRUE:
            if bool(status.get(field)):
                raise Pass218I29ValidationError(f"P218_I29_I28_STATUS_SAFETY_DRIFT:{field}")

    def _validated_i28_candidate(
        self,
        request: Pass218I28TransitionRequest,
    ) -> dict[str, Any]:
        state = self.i28_control.construct(request)
        if state.get("schema") != PASS218_I28_TRANSITION_SCHEMA:
            raise Pass218I29ValidationError("P218_I29_I28_SCHEMA_INVALID")
        if state.get("hash216_vm5184_transition_status") != (
            "REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
        ):
            raise Pass218I29ValidationError("P218_I29_I28_CANDIDATE_STATUS_INVALID")
        if not bool(state.get("hash216_vm5184_transition_candidate_ready")):
            raise Pass218I29ValidationError("P218_I29_I28_CANDIDATE_NOT_READY")
        for field in self._FORBIDDEN_I28_TRUE:
            if bool(state.get(field)):
                raise Pass218I29ValidationError(f"P218_I29_I28_SAFETY_DRIFT:{field}")
        _require_hash72(
            state.get("hash216_vm5184_transition_hash72"),
            "P218_I29_I28_TRANSITION_HASH72_INVALID",
        )
        return state

    def _validated_i27_state(
        self,
        request: Pass218I27DifferentiationRequest,
    ) -> dict[str, Any]:
        status = self.i27_control.status()
        if status.get("formal_analogical_differentiation_status") != (
            "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
        ):
            raise Pass218I29ValidationError("P218_I29_I27_STATUS_INVALID")
        state = self.i27_control.differentiate(request)
        if state.get("formal_analogical_differentiation_status") != (
            "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
        ):
            raise Pass218I29ValidationError("P218_I29_I27_STATE_INVALID")
        if not bool(state.get("differentiation_complete")):
            raise Pass218I29ValidationError("P218_I29_I27_DIFFERENTIATION_INCOMPLETE")
        if int(state.get("unresolved_relation_count", -1)) != 0:
            raise Pass218I29ValidationError("P218_I29_I27_UNRESOLVED_RELATIONS")
        relations = state.get("differentiated_relations")
        if not isinstance(relations, list):
            raise Pass218I29ValidationError("P218_I29_I27_RELATIONS_REQUIRED")
        if int(state.get("relation_count", -1)) != len(relations):
            raise Pass218I29ValidationError("P218_I29_I27_RELATION_COUNT_MISMATCH")
        return state

    @staticmethod
    def _expected_relation_word(relation: Mapping[str, Any], expected_rank: int) -> int:
        if relation.get("perspective_order_rank") != expected_rank:
            raise Pass218I29ValidationError("P218_I29_RELATION_ORDER_INVALID")
        if not bool(relation.get("relation_family_resolved")):
            raise Pass218I29ValidationError("P218_I29_RELATION_FAMILY_UNRESOLVED")
        status = relation.get("status")
        if isinstance(status, bool) or not isinstance(status, int) or status not in {-1, 0, 1}:
            raise Pass218I29ValidationError("P218_I29_RELATION_STATUS_INVALID")
        for field in (
            "source_id_hash72",
            "target_id_hash72",
            "grounded_relation_hash72",
            "differentiated_relation_hash72",
            "grounding_identity_hash72",
        ):
            _require_hash72(
                relation.get(field),
                f"P218_I29_RELATION_{field.upper()}_INVALID",
            )
        exact_projection = {
            "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
            "perspective_order_rank": expected_rank,
            "source_id_hash72": relation["source_id_hash72"],
            "target_id_hash72": relation["target_id_hash72"],
            "grounded_relation_hash72": relation["grounded_relation_hash72"],
            "differentiated_relation_hash72": relation["differentiated_relation_hash72"],
            "relation_type": relation.get("relation_type"),
            "relation_family_candidate": relation.get("relation_family_candidate"),
            "differentiation_mode": relation.get("differentiation_mode"),
            "status": status,
            "exact_strength": relation.get("exact_strength"),
            "provenance": relation.get("provenance"),
            "grounding_identity_hash72": relation["grounding_identity_hash72"],
        }
        return int.from_bytes(sha256(_canonical_bytes(exact_projection)).digest()[:8], "big")

    @classmethod
    def _expected_words(cls, relations: Sequence[Mapping[str, Any]]) -> list[int]:
        if len(relations) > VM5184_CELL_COUNT:
            raise Pass218I29ValidationError("P218_I29_VM5184_CAPACITY_EXCEEDED")
        words = [0] * VM5184_CELL_COUNT
        for rank, relation in enumerate(relations, start=1):
            if not isinstance(relation, Mapping):
                raise Pass218I29ValidationError("P218_I29_RELATION_OBJECT_REQUIRED")
            words[rank - 1] = cls._expected_relation_word(relation, rank)
        return words

    @staticmethod
    def _validate_native_abi(abi: Mapping[str, object]) -> None:
        expected = {
            "state_bits": VM5184_STATE_BITS,
            "cell_count": VM5184_CELL_COUNT,
            "bits_per_cell": VM5184_BITS_PER_CELL,
            "canonical_float_fields": 0,
        }
        for field, value in expected.items():
            if int(abi.get(field, -1)) != value:
                raise Pass218I29ValidationError(f"P218_I29_PASS205_ABI_MISMATCH:{field}")

    @staticmethod
    def _recompute_i28_hash(candidate: Mapping[str, Any]) -> str:
        body = dict(candidate)
        body.pop("hash216_vm5184_transition_hash72", None)
        return hash72_digest({"domain": "HHS-P218-I28-TRANSITION-RESULT-V1"}, body)

    def validate(
        self,
        request: Pass218I29ValidationRequest,
    ) -> dict[str, Any]:
        validated = request.validated()
        try:
            self._validated_i28_status()
            i28 = self._validated_i28_candidate(validated.transition_request)
            i27 = self._validated_i27_state(
                validated.transition_request.differentiation_request
            )

            if i28.get("i27_formal_analogical_differentiation_hash72") != i27.get(
                "formal_analogical_differentiation_hash72"
            ):
                raise Pass218I29ValidationError("P218_I29_I27_PARENT_IDENTITY_MISMATCH")
            if i28.get("i27_differentiation_state_hash72") != i27.get(
                "differentiation_state_hash72"
            ):
                raise Pass218I29ValidationError("P218_I29_I27_STATE_IDENTITY_MISMATCH")

            relations = i27["differentiated_relations"]
            expected_relation_hashes = [
                str(item["differentiated_relation_hash72"]) for item in relations
            ]
            expected_words = self._expected_words(relations)

            vm = i28.get("vm5184_candidate")
            if not isinstance(vm, Mapping):
                raise Pass218I29ValidationError("P218_I29_VM5184_CANDIDATE_REQUIRED")
            if vm.get("mapping_version") != PASS218_I28_VM5184_MAPPING_VERSION:
                raise Pass218I29ValidationError("P218_I29_VM5184_MAPPING_VERSION_MISMATCH")
            if int(vm.get("state_bits", -1)) != VM5184_STATE_BITS:
                raise Pass218I29ValidationError("P218_I29_VM5184_STATE_BITS_INVALID")
            if int(vm.get("cell_count", -1)) != VM5184_CELL_COUNT:
                raise Pass218I29ValidationError("P218_I29_VM5184_CELL_COUNT_INVALID")
            if int(vm.get("bits_per_cell", -1)) != VM5184_BITS_PER_CELL:
                raise Pass218I29ValidationError("P218_I29_VM5184_BITS_PER_CELL_INVALID")
            if vm.get("state_words") != expected_words:
                raise Pass218I29ValidationError("P218_I29_VM5184_RELATION_CELL_BINDING_MISMATCH")
            if int(vm.get("populated_relation_cells", -1)) != len(relations):
                raise Pass218I29ValidationError("P218_I29_VM5184_POPULATED_COUNT_MISMATCH")
            if int(vm.get("zero_padded_cells", -1)) != VM5184_CELL_COUNT - len(relations):
                raise Pass218I29ValidationError("P218_I29_VM5184_ZERO_PADDING_MISMATCH")
            if any(expected_words[len(relations):]):
                raise Pass218I29ValidationError("P218_I29_VM5184_NONZERO_PADDING")
            if not bool(vm.get("candidate_only")) or bool(vm.get("authoritative_projection")):
                raise Pass218I29ValidationError("P218_I29_VM5184_AUTHORITY_DRIFT")

            bridge = self._native_bridge()
            abi = bridge.abi_status()
            self._validate_native_abi(abi)
            projection = bridge.project_full(expected_words)
            if len(projection) != int(abi.get("projection_channels", -1)):
                raise Pass218I29ValidationError("P218_I29_NATIVE_PROJECTION_CHANNELS_INVALID")
            if any(len(channel) != VM5184_CELL_COUNT for channel in projection):
                raise Pass218I29ValidationError("P218_I29_NATIVE_PROJECTION_SHAPE_INVALID")
            expected_state_root216 = bridge.state_root(expected_words)
            expected_projection_root216 = bridge.projection_root(projection)
            if vm.get("native_state_root216") != expected_state_root216:
                raise Pass218I29ValidationError("P218_I29_NATIVE_STATE_ROOT_MISMATCH")
            if vm.get("native_projection_root216") != expected_projection_root216:
                raise Pass218I29ValidationError("P218_I29_NATIVE_PROJECTION_ROOT_MISMATCH")
            if not _valid_hash216(expected_state_root216) or not _valid_hash216(
                expected_projection_root216
            ):
                raise Pass218I29ValidationError("P218_I29_NATIVE_ROOT_FORMAT_INVALID")

            grounding = i27.get("grounding_identity")
            if not isinstance(grounding, Mapping):
                raise Pass218I29ValidationError("P218_I29_GROUNDING_IDENTITY_REQUIRED")
            curriculum_hash72 = _require_hash72(
                grounding.get("curriculum_identity_hash72"),
                "P218_I29_CURRICULUM_HASH72_INVALID",
            )
            expected_content_root216 = bridge.hash216_bytes(
                _canonical_bytes(
                    {
                        "i27_differentiation_hash72": i27[
                            "formal_analogical_differentiation_hash72"
                        ],
                        "relation_hashes": expected_relation_hashes,
                    }
                )
            )
            expected_delta_root216 = bridge.hash216_bytes(
                _canonical_bytes(
                    {
                        "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
                        "populated_cells": len(relations),
                        "state_words": expected_words[: len(relations)],
                    }
                )
            )
            expected_hydration_root216 = bridge.hash216_bytes(_canonical_bytes(grounding))
            expected_dependency_root216 = bridge.hash216_bytes(
                _canonical_bytes(
                    {
                        "i20_binding_hash72": i27.get("i20_binding_hash72"),
                        "i21_batch_hash72": i27.get("i21_batch_hash72"),
                        "i22_graph_hash72": i27.get("i22_graph_hash72"),
                        "i23_contextual_state_hash72": i27.get("i23_contextual_state_hash72"),
                        "i24_narrative_beat_hash72": i27["i24_narrative_beat_hash72"],
                        "i25_perspective_context_hash72": i27[
                            "i25_perspective_context_hash72"
                        ],
                        "i26_grounded_relational_manifold_hash72": i27[
                            "i26_grounded_relational_manifold_hash72"
                        ],
                        "i27_differentiation_hash72": i27[
                            "formal_analogical_differentiation_hash72"
                        ],
                    }
                )
            )
            expected_learning_root216 = bridge.hash216_bytes(
                _canonical_bytes(i27["relation_family_layers"])
            )
            expected_parent_root216 = bridge.hash216_bytes(
                str(i27["formal_analogical_differentiation_hash72"]).encode("ascii")
            )
            i27_receipt_hash72 = _require_hash72(
                i27.get("validation_receipt", {}).get(
                    "differentiation_validation_receipt_hash72"
                ),
                "P218_I29_I27_RECEIPT_HASH72_INVALID",
            )
            generation = int(
                validated.transition_request.differentiation_request.manifold_request.perspective_request.beat_request.curriculum_position
            )
            expected_token = bridge.build_token(
                parent_root=expected_parent_root216,
                content_root=expected_content_root216,
                delta_root=expected_delta_root216,
                hydration_root=expected_hydration_root216,
                dependency_root=expected_dependency_root216,
                projection_root=expected_projection_root216,
                learning_root=expected_learning_root216,
                parent_receipt=i27_receipt_hash72,
                generation=generation,
            )
            token = i28.get("native_continuation_token")
            if not isinstance(token, Mapping):
                raise Pass218I29ValidationError("P218_I29_NATIVE_TOKEN_REQUIRED")
            if dict(token) != expected_token:
                raise Pass218I29ValidationError("P218_I29_NATIVE_TOKEN_MISMATCH")

            vm_hash_body = dict(vm)
            actual_vm_hash72 = vm_hash_body.pop("vm5184_candidate_hash72", None)
            expected_vm_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-VM5184-CANDIDATE-V1"},
                vm_hash_body,
            )
            if actual_vm_hash72 != expected_vm_hash72:
                raise Pass218I29ValidationError("P218_I29_VM5184_CANDIDATE_HASH_MISMATCH")

            transition_state = {
                "i27_differentiation_hash72": i27[
                    "formal_analogical_differentiation_hash72"
                ],
                "i27_differentiation_state_hash72": i27["differentiation_state_hash72"],
                "grounding_identity_hash72": grounding["grounding_identity_hash72"],
                "vm5184_candidate_hash72": expected_vm_hash72,
                "native_state_root216": expected_state_root216,
                "native_projection_root216": expected_projection_root216,
                "native_continuation_root216": expected_token["continuation_root216"],
                "relation_count": len(relations),
                "relation_hashes": expected_relation_hashes,
                "candidate_only": True,
            }
            expected_transition_state_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-HYDRATED-TRANSITION-STATE-V1"},
                transition_state,
            )
            if i28.get("transition_state_hash72") != expected_transition_state_hash72:
                raise Pass218I29ValidationError("P218_I29_TRANSITION_STATE_HASH_MISMATCH")

            prevalidation = i28.get("prevalidation_receipt")
            if not isinstance(prevalidation, Mapping):
                raise Pass218I29ValidationError("P218_I29_PREVALIDATION_RECEIPT_REQUIRED")
            prevalidation_body = dict(prevalidation)
            actual_prevalidation_hash72 = prevalidation_body.pop(
                "prevalidation_receipt_hash72", None
            )
            expected_prevalidation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-PREVALIDATION-RECEIPT-V1"},
                prevalidation_body,
            )
            if actual_prevalidation_hash72 != expected_prevalidation_hash72:
                raise Pass218I29ValidationError("P218_I29_PREVALIDATION_RECEIPT_TAMPERED")
            if bool(prevalidation.get("semantic_transition_validated")):
                raise Pass218I29ValidationError("P218_I29_PREVALIDATION_ALREADY_PROMOTED")

            segments = i28.get("pass218_hash216_segments")
            if not isinstance(segments, Mapping):
                raise Pass218I29ValidationError("P218_I29_HASH216_SEGMENTS_REQUIRED")
            if segments.get("manifest_curriculum_hash72") != curriculum_hash72:
                raise Pass218I29ValidationError("P218_I29_HASH216_CURRICULUM_SEGMENT_MISMATCH")
            if segments.get("hydrated_transition_state_hash72") != (
                expected_transition_state_hash72
            ):
                raise Pass218I29ValidationError("P218_I29_HASH216_STATE_SEGMENT_MISMATCH")
            if segments.get("prevalidation_receipt_hash72") != (
                expected_prevalidation_hash72
            ):
                raise Pass218I29ValidationError("P218_I29_HASH216_PREVALIDATION_SEGMENT_MISMATCH")
            candidate_hash216 = str(i28.get("pass218_hash216_candidate") or "")
            if candidate_hash216 != (
                curriculum_hash72
                + expected_transition_state_hash72
                + expected_prevalidation_hash72
            ):
                raise Pass218I29ValidationError("P218_I29_HASH216_CANDIDATE_MISMATCH")
            if not _valid_hash216(candidate_hash216):
                raise Pass218I29ValidationError("P218_I29_HASH216_CANDIDATE_INVALID")

            continuation = i28.get("continuation_tuple")
            if not isinstance(continuation, Mapping):
                raise Pass218I29ValidationError("P218_I29_CONTINUATION_TUPLE_REQUIRED")
            continuation_body = dict(continuation)
            actual_continuation_hash72 = continuation_body.pop(
                "continuation_tuple_hash72", None
            )
            expected_continuation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-CONTINUATION-TUPLE-V1"},
                continuation_body,
            )
            if actual_continuation_hash72 != expected_continuation_hash72:
                raise Pass218I29ValidationError("P218_I29_CONTINUATION_TUPLE_TAMPERED")
            if continuation.get("parent_hash72") != i27[
                "formal_analogical_differentiation_hash72"
            ]:
                raise Pass218I29ValidationError("P218_I29_CONTINUATION_PARENT_MISMATCH")
            if continuation.get("next_hash72") != expected_transition_state_hash72:
                raise Pass218I29ValidationError("P218_I29_CONTINUATION_NEXT_MISMATCH")
            if continuation.get("receipt_hash72") != expected_prevalidation_hash72:
                raise Pass218I29ValidationError("P218_I29_CONTINUATION_RECEIPT_MISMATCH")
            if continuation.get("native_continuation_root216") != expected_token[
                "continuation_root216"
            ]:
                raise Pass218I29ValidationError("P218_I29_NATIVE_CONTINUATION_ROOT_MISMATCH")
            if not bool(continuation.get("continuation_constructed")) or bool(
                continuation.get("continuation_verified")
            ):
                raise Pass218I29ValidationError("P218_I29_CONTINUATION_STATE_INVALID")

            conservation = i28.get("transition_conservation")
            if not isinstance(conservation, Mapping) or not conservation:
                raise Pass218I29ValidationError("P218_I29_TRANSITION_CONSERVATION_REQUIRED")
            if not all(bool(value) for value in conservation.values()):
                raise Pass218I29ValidationError("P218_I29_TRANSITION_CONSERVATION_FAILED")

            expected_i28_hash72 = self._recompute_i28_hash(i28)
            if i28.get("hash216_vm5184_transition_hash72") != expected_i28_hash72:
                raise Pass218I29ValidationError("P218_I29_I28_RESULT_HASH_TAMPERED")

            validation_body = {
                "i28_transition_hash72": expected_i28_hash72,
                "i27_parent_hash72": i27["formal_analogical_differentiation_hash72"],
                "curriculum_hash72": curriculum_hash72,
                "transition_state_hash72": expected_transition_state_hash72,
                "native_state_root216": expected_state_root216,
                "native_projection_root216": expected_projection_root216,
                "native_continuation_root216": expected_token["continuation_root216"],
                "relation_count": len(relations),
                "relation_cell_binding_verified": True,
                "relation_order_verified": True,
                "relation_direction_and_type_binding_verified": True,
                "exact_status_and_strength_binding_verified": True,
                "provenance_binding_verified": True,
                "perspective_order_binding_verified": True,
                "hash216_parent_next_receipt_continuity_verified": True,
                "native_projection_rederived": True,
                "candidate_semantic_binding_verified": True,
                "promoted_semantic_round_trip_verified": False,
                "authoritative_projection_invoked": False,
                "vm81_authorization_invoked": False,
                "atomic_promotion_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
            validation_receipt_hash72 = hash72_digest(
                {"domain": "HHS-P218-I29-VALIDATION-RECEIPT-V1"},
                validation_body,
            )
            validated_hash216 = (
                curriculum_hash72
                + expected_transition_state_hash72
                + validation_receipt_hash72
            )
            if not _valid_hash216(validated_hash216):
                raise Pass218I29ValidationError("P218_I29_VALIDATED_HASH216_INVALID")

            semantic_witness = {
                "relation_count": len(relations),
                "differentiated_relation_hashes": expected_relation_hashes,
                "relation_family_sequence": [
                    item.get("relation_family_candidate") for item in relations
                ],
                "relation_type_sequence": [item.get("relation_type") for item in relations],
                "status_sequence": [item.get("status") for item in relations],
                "perspective_order_sequence": [
                    item.get("perspective_order_rank") for item in relations
                ],
                "source_target_binding_hash72": hash72_digest(
                    {"domain": "HHS-P218-I29-SOURCE-TARGET-BINDING-V1"},
                    [
                        {
                            "source_id_hash72": item["source_id_hash72"],
                            "target_id_hash72": item["target_id_hash72"],
                            "grounded_relation_hash72": item["grounded_relation_hash72"],
                        }
                        for item in relations
                    ],
                ),
            }
            semantic_witness_hash72 = hash72_digest(
                {"domain": "HHS-P218-I29-SEMANTIC-WITNESS-V1"},
                semantic_witness,
            )

            body = {
                "schema": PASS218_I29_VALIDATION_SCHEMA,
                "version": PASS218_I29_VALIDATION_VERSION,
                "i28_hash216_vm5184_transition_hash72": expected_i28_hash72,
                "i27_formal_analogical_differentiation_hash72": i27[
                    "formal_analogical_differentiation_hash72"
                ],
                "transition_state_hash72": expected_transition_state_hash72,
                "validation_receipt": {
                    **validation_body,
                    "validation_receipt_hash72": validation_receipt_hash72,
                },
                "pass218_validated_hash216_segments": {
                    "manifest_curriculum_hash72": curriculum_hash72,
                    "hydrated_transition_state_hash72": expected_transition_state_hash72,
                    "validation_receipt_hash72": validation_receipt_hash72,
                },
                "pass218_validated_hash216": validated_hash216,
                "semantic_validation_witness": {
                    **semantic_witness,
                    "semantic_witness_hash72": semantic_witness_hash72,
                },
                "native_validation": {
                    "state_root216": expected_state_root216,
                    "projection_root216": expected_projection_root216,
                    "continuation_root216": expected_token["continuation_root216"],
                    "projection_channels": len(projection),
                    "canonical_float_fields": int(abi["canonical_float_fields"]),
                    "candidate_projection_rederived": True,
                    "authoritative_projection": False,
                },
                "relation_count": len(relations),
                "hash216_continuation_verified": True,
                "semantic_transition_validated": True,
                "vm5184_candidate_projection_verified": True,
                "candidate_semantic_binding_verified": True,
                "formal_semantic_round_trip_verified": False,
                "atomic_promotion_candidate_ready": True,
                "atomic_promotion_authorized": False,
                "vm5184_authoritative_projection_invoked": False,
                "vm81_authorization_invoked": False,
                "atomic_promotion_invoked": False,
                "authoritative_semantic_compression_ready": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
                "hash216_vm5184_validation_status": (
                    "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
                ),
                "hash216_vm5184_validation_ready": True,
            }
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I29-VALIDATION-RESULT-V1"},
                body,
            )
            result = {
                **body,
                "hash216_vm5184_validation_hash72": validation_hash72,
            }
            self.validation_count += 1
            self.last_validation_hash72 = validation_hash72
            self.last_validated_hash216 = validated_hash216
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I29ValidationError):
                raise
            raise Pass218I29ValidationError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i28 = self.i28_control.status()
        ready = (
            bool(i28.get("hash216_vm5184_transition_candidate_ready"))
            and i28.get("hash216_vm5184_transition_status")
            == "REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
            and not any(bool(i28.get(field)) for field in self._FORBIDDEN_I28_TRUE)
        )
        return {
            "schema": PASS218_I29_STATUS_SCHEMA,
            "version": PASS218_I29_VALIDATION_VERSION,
            "hash216_vm5184_validation_ready": ready,
            "validation_count": self.validation_count,
            "last_validation_hash72": self.last_validation_hash72,
            "last_validated_hash216": self.last_validated_hash216,
            "i29_error_code": self.last_error_code,
            "hash216_vm5184_validation_status": (
                "VALIDATION_AVAILABLE_FOR_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
            ),
            "hash216_continuation_verified": False,
            "semantic_transition_validated": False,
            "vm5184_candidate_projection_verified": False,
            "formal_semantic_round_trip_verified": False,
            "atomic_promotion_candidate_ready": False,
            "atomic_promotion_authorized": False,
            "vm5184_authoritative_projection_invoked": False,
            "vm81_authorization_invoked": False,
            "atomic_promotion_invoked": False,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "PASS218_I29_STATUS_SCHEMA",
    "PASS218_I29_VALIDATION_SCHEMA",
    "PASS218_I29_VALIDATION_VERSION",
    "Pass218I29Hash216VM5184Validator",
    "Pass218I29ValidationError",
    "Pass218I29ValidationRequest",
]
