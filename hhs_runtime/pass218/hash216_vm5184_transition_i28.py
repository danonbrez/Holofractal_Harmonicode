"""Pass 218 Iteration 28 Hash216 / VM5184 transition candidate.

I28 consumes only the frozen I27 formal/analogical differentiation candidate.
It constructs an exact, non-promoted transition representation using the
inherited Pass 205 native 81 x 64-bit VM5184 continuation ABI and the Pass 218
three-segment Hash216 receipt form:

    H72(curriculum) || H72(hydrated transition state) || H72(prevalidation receipt)

This stage is construction, not semantic validation or canonical promotion.
VM81 mutation authority, truth promotion, atomic promotion, canonical learning,
model activation, verbatim retention, and authoritative floating point remain
closed.
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

PASS218_I28_TRANSITION_VERSION = "HHS-P218-I28-HASH216-VM5184-TRANSITION-V1"
PASS218_I28_TRANSITION_SCHEMA = "HHS-P218-I28-HASH216-VM5184-TRANSITION-CANDIDATE-V1"
PASS218_I28_STATUS_SCHEMA = "HHS-P218-I28-HASH216-VM5184-TRANSITION-STATUS-V1"
PASS218_I28_VM5184_MAPPING_VERSION = "HHS-P218-I28-VM5184-RELATION-CELL-MAP-V1"
VM5184_CELL_COUNT = 81
VM5184_BITS_PER_CELL = 64
VM5184_STATE_BITS = VM5184_CELL_COUNT * VM5184_BITS_PER_CELL
HASH216_SYMBOL_COUNT = 216


class Pass218I28TransitionError(RuntimeError):
    """Fail-closed Iteration 28 transition construction error."""


class Pass218I27DifferentiationControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def differentiate(self, request: Pass218I27DifferentiationRequest) -> dict[str, Any]: ...


class Pass218I28NativeBridgeProtocol(Protocol):
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
class Pass218I28TransitionRequest:
    differentiation_request: Pass218I27DifferentiationRequest

    def validated(self) -> "Pass218I28TransitionRequest":
        return Pass218I28TransitionRequest(
            differentiation_request=self.differentiation_request.validated(),
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


class Pass218I28Hash216VM5184Transition:
    """Construct exact I27 -> Hash216/VM5184 transition candidates."""

    _FORBIDDEN_I27_TRUE = (
        "formal_analogical_typing_canonical",
        "grounded_relational_manifold_ready",
        "grounded_relational_manifold_promoted",
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

    def __init__(
        self,
        i27_control: Pass218I27DifferentiationControlProtocol,
        native_bridge: Pass218I28NativeBridgeProtocol | None = None,
    ) -> None:
        self.i27_control = i27_control
        self._native_bridge_override = native_bridge
        self.transition_count = 0
        self.last_transition_hash72: str | None = None
        self.last_hash216_candidate: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _native_bridge(self) -> Pass218I28NativeBridgeProtocol:
        if self._native_bridge_override is not None:
            return self._native_bridge_override
        # Lazy import prevents native build/load work at application import time.
        from hhs_python.runtime.hhs_pass205_continuation_bridge import Pass205NativeBridge

        return Pass205NativeBridge

    def _validated_i27_status(self) -> dict[str, Any]:
        status = self.i27_control.status()
        if not bool(status.get("formal_analogical_differentiation_candidate_ready")):
            raise Pass218I28TransitionError("P218_I28_I27_PROVIDER_REQUIRED")
        if status.get("formal_analogical_differentiation_status") != (
            "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
        ):
            raise Pass218I28TransitionError("P218_I28_I27_SEMANTICS_INVALID")
        for field in self._FORBIDDEN_I27_TRUE:
            if bool(status.get(field)):
                raise Pass218I28TransitionError(f"P218_I28_I27_SAFETY_DRIFT:{field}")
        return status

    def _validated_i27_state(
        self,
        request: Pass218I27DifferentiationRequest,
    ) -> dict[str, Any]:
        state = self.i27_control.differentiate(request)
        if state.get("formal_analogical_differentiation_status") != (
            "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
        ):
            raise Pass218I28TransitionError("P218_I28_I27_STATE_SEMANTICS_INVALID")
        if not bool(state.get("formal_analogical_differentiation_candidate_ready")):
            raise Pass218I28TransitionError("P218_I28_I27_STATE_NOT_READY")
        if not bool(state.get("formal_analogical_typing_invoked")):
            raise Pass218I28TransitionError("P218_I28_I27_TYPING_REQUIRED")
        for field in self._FORBIDDEN_I27_TRUE:
            if bool(state.get(field)):
                raise Pass218I28TransitionError(
                    f"P218_I28_I27_STATE_SAFETY_DRIFT:{field}"
                )
        if not bool(state.get("differentiation_complete")) or int(
            state.get("unresolved_relation_count", -1)
        ) != 0:
            raise Pass218I28TransitionError(
                "P218_I28_UNRESOLVED_DIFFERENTIATION_BLOCKS_TRANSITION"
            )
        for field in (
            "formal_analogical_differentiation_hash72",
            "differentiation_state_hash72",
            "i26_grounded_relational_manifold_hash72",
            "i24_narrative_beat_hash72",
            "i25_perspective_context_hash72",
        ):
            if not validate_hash72(str(state.get(field) or "")):
                raise Pass218I28TransitionError(
                    f"P218_I28_I27_{field.upper()}_INVALID"
                )
        grounding = state.get("grounding_identity")
        if not isinstance(grounding, Mapping):
            raise Pass218I28TransitionError("P218_I28_GROUNDING_IDENTITY_REQUIRED")
        curriculum_hash72 = str(grounding.get("curriculum_identity_hash72") or "")
        if not validate_hash72(curriculum_hash72):
            raise Pass218I28TransitionError("P218_I28_CURRICULUM_HASH72_REQUIRED")
        relations = state.get("differentiated_relations")
        if not isinstance(relations, list):
            raise Pass218I28TransitionError("P218_I28_RELATIONS_LIST_REQUIRED")
        if int(state.get("relation_count", -1)) != len(relations):
            raise Pass218I28TransitionError("P218_I28_RELATION_COUNT_MISMATCH")
        if len(relations) > VM5184_CELL_COUNT:
            raise Pass218I28TransitionError("P218_I28_VM5184_CELL_CAPACITY_EXCEEDED")
        receipt = state.get("validation_receipt")
        if not isinstance(receipt, Mapping) or not validate_hash72(
            str(receipt.get("differentiation_validation_receipt_hash72") or "")
        ):
            raise Pass218I28TransitionError("P218_I28_I27_RECEIPT_REQUIRED")
        return state

    @staticmethod
    def _relation_word(relation: Mapping[str, Any], expected_rank: int) -> int:
        rank = relation.get("perspective_order_rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank != expected_rank:
            raise Pass218I28TransitionError("P218_I28_RELATION_ORDER_INVALID")
        if not bool(relation.get("relation_family_resolved")):
            raise Pass218I28TransitionError("P218_I28_RELATION_FAMILY_UNRESOLVED")
        status = relation.get("status")
        if isinstance(status, bool) or not isinstance(status, int) or status not in {-1, 0, 1}:
            raise Pass218I28TransitionError("P218_I28_RELATION_STATUS_INVALID")
        for field in (
            "source_id_hash72",
            "target_id_hash72",
            "grounded_relation_hash72",
            "differentiated_relation_hash72",
            "grounding_identity_hash72",
        ):
            if not validate_hash72(str(relation.get(field) or "")):
                raise Pass218I28TransitionError(
                    f"P218_I28_RELATION_{field.upper()}_INVALID"
                )
        exact_projection = {
            "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
            "perspective_order_rank": rank,
            "source_id_hash72": relation["source_id_hash72"],
            "target_id_hash72": relation["target_id_hash72"],
            "grounded_relation_hash72": relation["grounded_relation_hash72"],
            "differentiated_relation_hash72": relation[
                "differentiated_relation_hash72"
            ],
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
    def _vm5184_words(cls, relations: Sequence[Mapping[str, Any]]) -> list[int]:
        words = [0] * VM5184_CELL_COUNT
        for rank, relation in enumerate(relations, start=1):
            if not isinstance(relation, Mapping):
                raise Pass218I28TransitionError("P218_I28_RELATION_OBJECT_REQUIRED")
            words[rank - 1] = cls._relation_word(relation, rank)
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
                raise Pass218I28TransitionError(
                    f"P218_I28_PASS205_ABI_MISMATCH:{field}"
                )

    def construct(
        self,
        request: Pass218I28TransitionRequest,
    ) -> dict[str, Any]:
        validated = request.validated()
        try:
            self._validated_i27_status()
            state = self._validated_i27_state(validated.differentiation_request)
            bridge = self._native_bridge()
            abi = bridge.abi_status()
            self._validate_native_abi(abi)

            relations = state["differentiated_relations"]
            words = self._vm5184_words(relations)
            projection = bridge.project_full(words)
            if len(projection) != int(abi.get("projection_channels", -1)):
                raise Pass218I28TransitionError("P218_I28_PROJECTION_CHANNEL_COUNT_INVALID")
            if any(len(channel) != VM5184_CELL_COUNT for channel in projection):
                raise Pass218I28TransitionError("P218_I28_PROJECTION_CELL_COUNT_INVALID")

            vm_state_root216 = bridge.state_root(words)
            vm_projection_root216 = bridge.projection_root(projection)
            if not _valid_hash216(vm_state_root216) or not _valid_hash216(
                vm_projection_root216
            ):
                raise Pass218I28TransitionError("P218_I28_NATIVE_HASH216_INVALID")

            relation_hashes = [
                str(item["differentiated_relation_hash72"]) for item in relations
            ]
            native_content_root216 = bridge.hash216_bytes(
                _canonical_bytes(
                    {
                        "i27_differentiation_hash72": state[
                            "formal_analogical_differentiation_hash72"
                        ],
                        "relation_hashes": relation_hashes,
                    }
                )
            )
            native_delta_root216 = bridge.hash216_bytes(
                _canonical_bytes(
                    {
                        "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
                        "populated_cells": len(relations),
                        "state_words": words[: len(relations)],
                    }
                )
            )
            native_hydration_root216 = bridge.hash216_bytes(
                _canonical_bytes(state["grounding_identity"])
            )
            native_dependency_root216 = bridge.hash216_bytes(
                _canonical_bytes(
                    {
                        "i20_binding_hash72": state.get("i20_binding_hash72"),
                        "i21_batch_hash72": state.get("i21_batch_hash72"),
                        "i22_graph_hash72": state.get("i22_graph_hash72"),
                        "i23_contextual_state_hash72": state.get(
                            "i23_contextual_state_hash72"
                        ),
                        "i24_narrative_beat_hash72": state[
                            "i24_narrative_beat_hash72"
                        ],
                        "i25_perspective_context_hash72": state[
                            "i25_perspective_context_hash72"
                        ],
                        "i26_grounded_relational_manifold_hash72": state[
                            "i26_grounded_relational_manifold_hash72"
                        ],
                        "i27_differentiation_hash72": state[
                            "formal_analogical_differentiation_hash72"
                        ],
                    }
                )
            )
            native_learning_root216 = bridge.hash216_bytes(
                _canonical_bytes(state["relation_family_layers"])
            )
            native_parent_root216 = bridge.hash216_bytes(
                str(state["formal_analogical_differentiation_hash72"]).encode("ascii")
            )
            native_roots = (
                native_content_root216,
                native_delta_root216,
                native_hydration_root216,
                native_dependency_root216,
                native_learning_root216,
                native_parent_root216,
            )
            if not all(_valid_hash216(value) for value in native_roots):
                raise Pass218I28TransitionError("P218_I28_NATIVE_COMPONENT_ROOT_INVALID")

            i27_receipt_hash72 = str(
                state["validation_receipt"]["differentiation_validation_receipt_hash72"]
            )
            generation = int(
                validated.differentiation_request.manifold_request.perspective_request.beat_request.curriculum_position
            )
            native_token = bridge.build_token(
                parent_root=native_parent_root216,
                content_root=native_content_root216,
                delta_root=native_delta_root216,
                hydration_root=native_hydration_root216,
                dependency_root=native_dependency_root216,
                projection_root=vm_projection_root216,
                learning_root=native_learning_root216,
                parent_receipt=i27_receipt_hash72,
                generation=generation,
            )
            for field in (
                "parent_root216",
                "content_root216",
                "delta_root216",
                "hydration_root216",
                "dependency_root216",
                "projection_root216",
                "learning_root216",
                "continuation_root216",
            ):
                if not _valid_hash216(native_token.get(field)):
                    raise Pass218I28TransitionError(
                        f"P218_I28_NATIVE_TOKEN_{field.upper()}_INVALID"
                    )
            for field in ("parent_receipt_hash72", "receipt_hash72"):
                if not validate_hash72(str(native_token.get(field) or "")):
                    raise Pass218I28TransitionError(
                        f"P218_I28_NATIVE_TOKEN_{field.upper()}_INVALID"
                    )

            vm5184_candidate = {
                "mapping_version": PASS218_I28_VM5184_MAPPING_VERSION,
                "state_bits": VM5184_STATE_BITS,
                "cell_count": VM5184_CELL_COUNT,
                "bits_per_cell": VM5184_BITS_PER_CELL,
                "populated_relation_cells": len(relations),
                "zero_padded_cells": VM5184_CELL_COUNT - len(relations),
                "state_words": words,
                "native_state_root216": vm_state_root216,
                "native_projection_root216": vm_projection_root216,
                "native_projection_channels": len(projection),
                "native_abi_canonical_float_fields": int(
                    abi["canonical_float_fields"]
                ),
                "candidate_only": True,
                "authoritative_projection": False,
                "vm81_mutation_authority": False,
            }
            vm5184_candidate["vm5184_candidate_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I28-VM5184-CANDIDATE-V1"},
                vm5184_candidate,
            )

            transition_state = {
                "i27_differentiation_hash72": state[
                    "formal_analogical_differentiation_hash72"
                ],
                "i27_differentiation_state_hash72": state[
                    "differentiation_state_hash72"
                ],
                "grounding_identity_hash72": state["grounding_identity"][
                    "grounding_identity_hash72"
                ],
                "vm5184_candidate_hash72": vm5184_candidate[
                    "vm5184_candidate_hash72"
                ],
                "native_state_root216": vm_state_root216,
                "native_projection_root216": vm_projection_root216,
                "native_continuation_root216": native_token[
                    "continuation_root216"
                ],
                "relation_count": len(relations),
                "relation_hashes": relation_hashes,
                "candidate_only": True,
            }
            transition_state_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-HYDRATED-TRANSITION-STATE-V1"},
                transition_state,
            )
            prevalidation_body = {
                "i27_differentiation_hash72": state[
                    "formal_analogical_differentiation_hash72"
                ],
                "transition_state_hash72": transition_state_hash72,
                "native_continuation_root216": native_token[
                    "continuation_root216"
                ],
                "meaning_conservation_inherited": all(
                    bool(value) for value in state["meaning_conservation"].values()
                ),
                "structural_transition_constructed": True,
                "semantic_transition_validated": False,
                "hash216_continuation_verified": False,
                "vm5184_authoritative_projection_verified": False,
                "vm81_authorization_verified": False,
                "atomic_promotion_permitted": False,
                "truth_promotion_permitted": False,
                "action_authority_permitted": False,
            }
            prevalidation_receipt_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-PREVALIDATION-RECEIPT-V1"},
                prevalidation_body,
            )
            curriculum_hash72 = str(
                state["grounding_identity"]["curriculum_identity_hash72"]
            )
            pass218_hash216_candidate = (
                curriculum_hash72
                + transition_state_hash72
                + prevalidation_receipt_hash72
            )
            if not _valid_hash216(pass218_hash216_candidate):
                raise Pass218I28TransitionError(
                    "P218_I28_THREE_SEGMENT_HASH216_INVALID"
                )

            continuation_tuple = {
                "parent_hash72": state["formal_analogical_differentiation_hash72"],
                "next_hash72": transition_state_hash72,
                "receipt_hash72": prevalidation_receipt_hash72,
                "native_continuation_root216": native_token[
                    "continuation_root216"
                ],
                "continuation_constructed": True,
                "continuation_verified": False,
            }
            continuation_tuple["continuation_tuple_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I28-CONTINUATION-TUPLE-V1"},
                continuation_tuple,
            )

            conservation = {
                "i27_differentiation_identity_preserved": True,
                "grounding_identity_preserved": True,
                "curriculum_identity_preserved": True,
                "relation_order_preserved": True,
                "relation_direction_preserved": True,
                "relation_type_preserved": True,
                "relation_family_preserved": True,
                "exact_status_preserved": True,
                "exact_strength_preserved_where_present": True,
                "provenance_preserved": True,
                "perspective_order_preserved": True,
                "authorization_not_widened": True,
                "validation_status_not_promoted": True,
            }
            body = {
                "schema": PASS218_I28_TRANSITION_SCHEMA,
                "version": PASS218_I28_TRANSITION_VERSION,
                "i27_formal_analogical_differentiation_hash72": state[
                    "formal_analogical_differentiation_hash72"
                ],
                "i27_differentiation_state_hash72": state[
                    "differentiation_state_hash72"
                ],
                "grounding_identity": dict(state["grounding_identity"]),
                "vm5184_candidate": vm5184_candidate,
                "native_continuation_token": dict(native_token),
                "transition_state_hash72": transition_state_hash72,
                "prevalidation_receipt": {
                    **prevalidation_body,
                    "prevalidation_receipt_hash72": prevalidation_receipt_hash72,
                },
                "pass218_hash216_segments": {
                    "manifest_curriculum_hash72": curriculum_hash72,
                    "hydrated_transition_state_hash72": transition_state_hash72,
                    "prevalidation_receipt_hash72": prevalidation_receipt_hash72,
                },
                "pass218_hash216_candidate": pass218_hash216_candidate,
                "continuation_tuple": continuation_tuple,
                "transition_conservation": conservation,
                "relation_count": len(relations),
                "hash216_candidate_receipt_constructed": True,
                "native_vm5184_transition_constructed": True,
                "vm5184_candidate_projection_invoked": True,
                "hash216_continuation_constructed": True,
                "hash216_continuation_verified": False,
                "semantic_transition_validated": False,
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
                "hash216_vm5184_transition_status": (
                    "REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
                ),
                "hash216_vm5184_transition_candidate_ready": True,
            }
            transition_hash72 = hash72_digest(
                {"domain": "HHS-P218-I28-TRANSITION-RESULT-V1"},
                body,
            )
            result = {**body, "hash216_vm5184_transition_hash72": transition_hash72}
            self.transition_count += 1
            self.last_transition_hash72 = transition_hash72
            self.last_hash216_candidate = pass218_hash216_candidate
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I28TransitionError):
                raise
            raise Pass218I28TransitionError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i27 = self.i27_control.status()
        ready = (
            bool(i27.get("formal_analogical_differentiation_candidate_ready"))
            and i27.get("formal_analogical_differentiation_status")
            == "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
            and not any(bool(i27.get(field)) for field in self._FORBIDDEN_I27_TRUE)
        )
        return {
            "schema": PASS218_I28_STATUS_SCHEMA,
            "version": PASS218_I28_TRANSITION_VERSION,
            "hash216_vm5184_transition_candidate_ready": ready,
            "transition_count": self.transition_count,
            "last_transition_hash72": self.last_transition_hash72,
            "last_hash216_candidate": self.last_hash216_candidate,
            "i28_error_code": self.last_error_code,
            "vm5184_state_bits": VM5184_STATE_BITS,
            "vm5184_cell_count": VM5184_CELL_COUNT,
            "vm5184_bits_per_cell": VM5184_BITS_PER_CELL,
            "hash216_vm5184_transition_status": (
                "REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
            ),
            "hash216_continuation_verified": False,
            "semantic_transition_validated": False,
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
    "HASH216_SYMBOL_COUNT",
    "PASS218_I28_STATUS_SCHEMA",
    "PASS218_I28_TRANSITION_SCHEMA",
    "PASS218_I28_TRANSITION_VERSION",
    "PASS218_I28_VM5184_MAPPING_VERSION",
    "VM5184_BITS_PER_CELL",
    "VM5184_CELL_COUNT",
    "VM5184_STATE_BITS",
    "Pass218I28Hash216VM5184Transition",
    "Pass218I28TransitionError",
    "Pass218I28TransitionRequest",
]
