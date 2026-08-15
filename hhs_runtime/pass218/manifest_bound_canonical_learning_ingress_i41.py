"""Pass 218 Iteration 41 manifest-bound canonical learning ingress.

I41 begins only from the exact durable I40 canonical commit/persistence receipt
and binding. It does not synthesize the independent I27->I29 semantic lineage
required by frozen I30 and does not invoke I30. Instead it seals a durable,
nonverbatim admission candidate proving which exact I40 canonical root may be
presented to the later I30 semantic-promotion membrane once an independently
validated, source-consistent I29 lineage is available.

No truth/action authority, purge/closure authority, curriculum advancement,
model activation, canonical learning commit, or authoritative floating-point
state is created here.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.manifest_bound_canonical_commit_persistence_i40 import (
    PASS218_I40_COMPLETE_STATUS,
    _atomic_write_json,
    _copy,
    _load_json,
    _valid_hash216,
    _verify_i40_binding,
    _verify_i40_receipt,
)

PASS218_I41_VERSION = "HHS-P218-I41-MANIFEST-BOUND-CANONICAL-LEARNING-INGRESS-V1"
PASS218_I41_SCOPE = "PASS218_MANIFEST_BOUND_CANONICAL_LEARNING_INGRESS"
PASS218_I41_CANDIDATE_SCHEMA = "HHS-P218-I41-MANIFEST-BOUND-CANONICAL-LEARNING-INGRESS-CANDIDATE-V1"
PASS218_I41_RECEIPT_SCHEMA = "HHS-P218-I41-MANIFEST-BOUND-CANONICAL-LEARNING-INGRESS-RECEIPT-V1"
PASS218_I41_STATE_SCHEMA = "HHS-P218-I41-MANIFEST-BOUND-CANONICAL-LEARNING-INGRESS-STATE-V1"
PASS218_I41_STATUS_SCHEMA = "HHS-P218-I41-MANIFEST-BOUND-CANONICAL-LEARNING-INGRESS-STATUS-V1"
PASS218_I41_COMPLETE_STATUS = "MANIFEST_BOUND_CANONICAL_LEARNING_INGRESS_COMPLETE"
PASS218_I41_PENDING_STATUS = "MANIFEST_BOUND_CANONICAL_LEARNING_INGRESS_PENDING"


class Pass218I41CanonicalLearningIngressError(RuntimeError):
    pass


class Pass218I41BindingError(Pass218I41CanonicalLearningIngressError):
    pass


class Pass218I41StateError(Pass218I41CanonicalLearningIngressError):
    pass


class Pass218I41LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I41I40StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_binding(self) -> dict[str, Any] | None: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I41BindingError("P218_I41_AUTHORITATIVE_FLOAT_FORBIDDEN")
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


def _valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _verify_i41_candidate(candidate: Mapping[str, Any], receipt: Mapping[str, Any] | None = None) -> dict[str, Any]:
    value = _copy(dict(candidate))
    if value.get("schema") != PASS218_I41_CANDIDATE_SCHEMA:
        raise Pass218I41StateError("P218_I41_CANDIDATE_SCHEMA_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I41StateError("P218_I41_I30_TARGET_SCOPE_INVALID")
    for field in (
        "i40_receipt_hash72",
        "i40_canonical_root_hash72",
        "i40_i7_checkpoint_hash72",
        "i40_i6_commit_receipt_hash72",
        "manifest_bound_commit_persistence_hash72",
        "learning_ingress_candidate_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I41StateError("P218_I41_CANDIDATE_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i40_hash216")):
        raise Pass218I41StateError("P218_I41_I40_HASH216_INVALID")
    for field in ("i40_i7_checkpoint_sha256", "i40_i6_admitted_entry_id_sha256", "i40_i4_projection_sha256"):
        if not _valid_sha256(value.get(field)):
            raise Pass218I41StateError("P218_I41_CANDIDATE_SHA256_INVALID:" + field)
    required_true = (
        "i40_canonical_state_required",
        "manifest_binding_propagated",
        "i30_exact_i27_i29_lineage_required",
        "i30_independent_validation_required",
        "candidate_non_authoritative",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I41StateError("P218_I41_CANDIDATE_PROOF_INCOMPLETE")
    required_false = (
        "i30_request_synthesized",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I41StateError("P218_I41_CANDIDATE_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key != "learning_ingress_candidate_hash72"}
    expected = hash72_digest({"domain": PASS218_I41_CANDIDATE_SCHEMA}, body)
    if expected != value.get("learning_ingress_candidate_hash72"):
        raise Pass218I41StateError("P218_I41_CANDIDATE_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get("learning_ingress_candidate_hash72"):
        raise Pass218I41StateError("P218_I41_CANDIDATE_RECEIPT_MISMATCH")
    return value


def _verify_i41_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I41_RECEIPT_SCHEMA:
        raise Pass218I41StateError("P218_I41_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I41_COMPLETE_STATUS:
        raise Pass218I41StateError("P218_I41_RECEIPT_STATUS_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I41StateError("P218_I41_RECEIPT_TARGET_SCOPE_INVALID")
    for field in (
        "i40_receipt_hash72",
        "i40_canonical_root_hash72",
        "i40_i7_checkpoint_hash72",
        "manifest_bound_commit_persistence_hash72",
        "learning_ingress_candidate_hash72",
        "i41_validation_hash72",
        "i41_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I41StateError("P218_I41_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i41_hash216")):
        raise Pass218I41StateError("P218_I41_HASH216_INVALID")
    if value.get("i41_hash216") != (
        str(value["i40_receipt_hash72"])
        + str(value["learning_ingress_candidate_hash72"])
        + str(value["i41_receipt_hash72"])
    ):
        raise Pass218I41StateError("P218_I41_HASH216_ORDER_INVALID")
    required_true = (
        "i40_receipt_bound",
        "i40_durable_canonical_root_bound",
        "manifest_binding_propagated",
        "learning_ingress_candidate_persisted",
        "i30_exact_i27_i29_lineage_required",
        "i30_independent_validation_required",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I41StateError("P218_I41_RECEIPT_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "i30_request_synthesized",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I41StateError("P218_I41_RECEIPT_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key not in {"i41_receipt_hash72", "i41_hash216", "i41_hash216_semantics"}}
    expected = hash72_digest({"domain": PASS218_I41_RECEIPT_SCHEMA}, body)
    if expected != value.get("i41_receipt_hash72"):
        raise Pass218I41StateError("P218_I41_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I41CanonicalLearningIngressStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.candidate_root = self.root / "candidates"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I41_STATE_SCHEMA:
            raise Pass218I41StateError("P218_I41_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I41_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I41StateError("P218_I41_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        candidate_path = self.root / str(state.get("active_candidate_path", ""))
        if not receipt_path.is_file() or not candidate_path.is_file():
            raise Pass218I41StateError("P218_I41_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i41_receipt(_load_json(receipt_path))
        candidate = _verify_i41_candidate(_load_json(candidate_path), receipt)
        if receipt["i41_receipt_hash72"] != state.get("active_i41_receipt_hash72"):
            raise Pass218I41StateError("P218_I41_STATE_RECEIPT_MISMATCH")
        if candidate["learning_ingress_candidate_hash72"] != state.get("active_candidate_hash72"):
            raise Pass218I41StateError("P218_I41_STATE_CANDIDATE_MISMATCH")
        return receipt

    def active_candidate(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i41_candidate(
            _load_json(self.root / str(state["active_candidate_path"])), receipt
        )

    def commit(self, receipt: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i41_receipt(receipt)
        checked_candidate = _verify_i41_candidate(candidate, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_candidate() != checked_candidate:
                raise Pass218I41StateError("P218_I41_ACTIVE_BINDING_CONFLICT")
            return existing
        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_path = self.receipt_root / f"{ordinal:08d}-{checked['i41_receipt_hash72']}.json"
        candidate_path = self.candidate_root / f"{checked_candidate['learning_ingress_candidate_hash72']}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(candidate_path, checked_candidate)
        state_body = {
            "schema": PASS218_I41_STATE_SCHEMA,
            "version": PASS218_I41_VERSION,
            "status": PASS218_I41_COMPLETE_STATUS,
            "i40_receipt_hash72": checked["i40_receipt_hash72"],
            "active_i41_receipt_hash72": checked["i41_receipt_hash72"],
            "active_candidate_hash72": checked["learning_ingress_candidate_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_candidate_path": candidate_path.relative_to(self.root).as_posix(),
        }
        state = {**state_body, "state_root_hash72": hash72_digest({"domain": PASS218_I41_STATE_SCHEMA}, state_body)}
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I41StateError("P218_I41_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I41ManifestBoundCanonicalLearningIngress:
    def __init__(
        self,
        *,
        lifecycle: Pass218I41LifecycleProtocol,
        i40_store: Pass218I41I40StoreProtocol,
        state_root: str | os.PathLike[str],
        i40_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        i30_status_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i40_store = i40_store
        self.store = Pass218I41CanonicalLearningIngressStore(state_root)
        self.i40_status_provider = i40_status_provider
        self.i30_status_provider = i30_status_provider
        self.admission_count = 0
        self.i30_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_i40(self) -> tuple[dict[str, Any], dict[str, Any]]:
        receipt = self.i40_store.active_record()
        binding = self.i40_store.active_binding()
        if not isinstance(receipt, Mapping) or not isinstance(binding, Mapping):
            raise Pass218I41BindingError("P218_I41_I40_COMPLETE_STATE_REQUIRED")
        checked = _verify_i40_receipt(receipt)
        checked_binding = _verify_i40_binding(binding, checked)
        if checked.get("status") != PASS218_I40_COMPLETE_STATUS:
            raise Pass218I41BindingError("P218_I41_I40_COMPLETE_STATUS_REQUIRED")
        if checked_binding.get("manifest_bound_commit_persistence_hash72") != checked.get("manifest_bound_commit_persistence_hash72"):
            raise Pass218I41BindingError("P218_I41_I40_BINDING_MISMATCH")
        if self.i40_status_provider is not None:
            status = dict(self.i40_status_provider())
            if status.get("status") != PASS218_I40_COMPLETE_STATUS:
                raise Pass218I41BindingError("P218_I41_I40_STATUS_NOT_COMPLETE")
            if status.get("active_i40_receipt_hash72") != checked["i40_receipt_hash72"]:
                raise Pass218I41BindingError("P218_I41_I40_STATUS_RECEIPT_MISMATCH")
            if status.get("canonical_root_hash72") != checked["i6_target_root_after_hash72"]:
                raise Pass218I41BindingError("P218_I41_I40_STATUS_ROOT_MISMATCH")
        return checked, checked_binding

    def _require_i30_preflight(self) -> None:
        if self.i30_status_provider is None:
            return
        status = dict(self.i30_status_provider())
        if status.get("target_scope") not in {None, PASS218_I30_TARGET_SCOPE}:
            raise Pass218I41BindingError("P218_I41_I30_TARGET_SCOPE_MISMATCH")
        if bool(status.get("promotion_present")):
            raise Pass218I41BindingError("P218_I41_I30_PREVIOUS_PROMOTION_PENDING")
        if bool(status.get("atomic_promotion_invoked")):
            raise Pass218I41BindingError("P218_I41_I30_PREVIOUS_PROMOTION_PENDING")

    def _build(self, i40: Mapping[str, Any], binding: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        candidate_body = {
            "schema": PASS218_I41_CANDIDATE_SCHEMA,
            "version": PASS218_I41_VERSION,
            "scope": PASS218_I41_SCOPE,
            "i40_receipt_hash72": i40["i40_receipt_hash72"],
            "i40_hash216": i40["i40_hash216"],
            "manifest_bound_commit_persistence_hash72": i40["manifest_bound_commit_persistence_hash72"],
            "manifest_binding": _copy(i40["manifest_binding"]),
            "i40_canonical_root_hash72": i40["i6_target_root_after_hash72"],
            "i40_i7_checkpoint_sha256": i40["i7_checkpoint_sha256"],
            "i40_i7_checkpoint_hash72": i40["i7_checkpoint_hash72"],
            "i40_i6_commit_receipt_hash72": i40["i6_commit_receipt_hash72"],
            "i40_i6_admitted_entry_id_sha256": i40["i6_admitted_entry_id_sha256"],
            "i40_i4_projection_sha256": i40["i4_projection_sha256"],
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i40_canonical_state_required": True,
            "manifest_binding_propagated": True,
            "i30_exact_i27_i29_lineage_required": True,
            "i30_independent_validation_required": True,
            "candidate_non_authoritative": True,
            "i30_request_synthesized": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        candidate_hash72 = hash72_digest({"domain": PASS218_I41_CANDIDATE_SCHEMA}, candidate_body)
        candidate = {**candidate_body, "learning_ingress_candidate_hash72": candidate_hash72}
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I41-CANONICAL-LEARNING-INGRESS-VALIDATION-V1"},
            {
                "i40_receipt_hash72": i40["i40_receipt_hash72"],
                "i40_canonical_root_hash72": i40["i6_target_root_after_hash72"],
                "i40_i7_checkpoint_hash72": i40["i7_checkpoint_hash72"],
                "manifest_bound_commit_persistence_hash72": binding["manifest_bound_commit_persistence_hash72"],
                "learning_ingress_candidate_hash72": candidate_hash72,
                "target_surface": PASS218_I30_TARGET_SCOPE,
                "i30_invoked": False,
            },
        )
        body = {
            "schema": PASS218_I41_RECEIPT_SCHEMA,
            "version": PASS218_I41_VERSION,
            "scope": PASS218_I41_SCOPE,
            "status": PASS218_I41_COMPLETE_STATUS,
            "i40_receipt_hash72": i40["i40_receipt_hash72"],
            "i40_hash216": i40["i40_hash216"],
            "manifest_bound_commit_persistence_hash72": i40["manifest_bound_commit_persistence_hash72"],
            "manifest_binding": _copy(i40["manifest_binding"]),
            "i40_canonical_root_hash72": i40["i6_target_root_after_hash72"],
            "i40_i7_checkpoint_sha256": i40["i7_checkpoint_sha256"],
            "i40_i7_checkpoint_hash72": i40["i7_checkpoint_hash72"],
            "learning_ingress_candidate_hash72": candidate_hash72,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i41_validation_hash72": validation_hash72,
            "i40_receipt_bound": True,
            "i40_durable_canonical_root_bound": True,
            "manifest_binding_propagated": True,
            "learning_ingress_candidate_persisted": True,
            "i30_exact_i27_i29_lineage_required": True,
            "i30_independent_validation_required": True,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "i30_request_synthesized": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
        }
        receipt_hash72 = hash72_digest({"domain": PASS218_I41_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i41_receipt_hash72": receipt_hash72,
            "i41_hash216": i40["i40_receipt_hash72"] + candidate_hash72 + receipt_hash72,
            "i41_hash216_semantics": [
                "I40_DURABLE_CANONICAL_COMMIT_PERSISTENCE_RECEIPT",
                "I41_CANONICAL_LEARNING_INGRESS_CANDIDATE",
                "I41_CANONICAL_LEARNING_INGRESS_RECEIPT",
            ],
        }
        return _verify_i41_candidate(candidate), _verify_i41_receipt(receipt)

    def admit(self) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i40, binding = self._active_i40()
            existing = self.store.active_record()
            if existing is not None:
                if existing["i40_receipt_hash72"] != i40["i40_receipt_hash72"]:
                    raise Pass218I41StateError("P218_I41_ACTIVE_I40_CONFLICT")
                self.last_error_code = None
                return existing
            self._require_i30_preflight()
            candidate, receipt = self._build(i40, binding)
            persisted = self.store.commit(receipt, candidate)
            self.admission_count += 1
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        predecessor_ready = False
        active_i40_receipt_hash72: str | None = None
        canonical_root_hash72: str | None = None
        try:
            i40, _ = self._active_i40()
            predecessor_ready = True
            active_i40_receipt_hash72 = str(i40["i40_receipt_hash72"])
            canonical_root_hash72 = str(i40["i6_target_root_after_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I41_STATUS_SCHEMA,
            "version": PASS218_I41_VERSION,
            "status": PASS218_I41_COMPLETE_STATUS if active is not None else PASS218_I41_PENDING_STATUS,
            "predecessor_state_ready": predecessor_ready,
            "active_i40_receipt_hash72": active_i40_receipt_hash72,
            "active_i41_receipt_hash72": None if active is None else active["i41_receipt_hash72"],
            "canonical_root_hash72": canonical_root_hash72,
            "learning_ingress_candidate_hash72": None if active is None else active["learning_ingress_candidate_hash72"],
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "admission_count_current_process": self.admission_count,
            "i30_invocation_count_current_process": self.i30_invocation_count,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I41_CANDIDATE_SCHEMA",
    "PASS218_I41_COMPLETE_STATUS",
    "PASS218_I41_PENDING_STATUS",
    "PASS218_I41_RECEIPT_SCHEMA",
    "PASS218_I41_SCOPE",
    "PASS218_I41_STATE_SCHEMA",
    "PASS218_I41_STATUS_SCHEMA",
    "PASS218_I41_VERSION",
    "Pass218I41BindingError",
    "Pass218I41CanonicalLearningIngressError",
    "Pass218I41CanonicalLearningIngressStore",
    "Pass218I41ManifestBoundCanonicalLearningIngress",
    "Pass218I41StateError",
]
