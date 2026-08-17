"""Pass 218 Iteration 44 manifest-bound one-time I30 atomic promotion.

I44 begins only from the exact durable I43 non-executing authorization and a
transient frozen-I30 ``Pass218I30PromotionRequest`` whose fingerprints and grant
identity equal that authorization.  If the frozen I30 semantic store is empty,
I44 invokes frozen I30 exactly once and then verifies its durable generation.  If
a process stopped after the I30 atomic manifest swap but before the I44 receipt
was persisted, restart recovery adopts the exact already-authorized durable I30
promotion without calling I30 again.

The durable I44 proof is execution-path independent: fresh execution and restart
adoption of the same exact I30 promotion seal the same identity.  Completion is
ATOMIC_PROMOTION_COMMITTED_PENDING_I31.  I44 does not invoke I31/I32, advance the
curriculum, mutate VM81, perform canonical learning, promote truth, mint action
authority, activate a model, retain source payload, or create floating-point
authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PENDING_PURGE_STATUS,
    PASS218_I30_PROMOTED_OBJECT_SCHEMA,
    PASS218_I30_PROMOTION_RECEIPT_SCHEMA,
    PASS218_I30_TARGET_SCOPE,
    Pass218I30PromotionRequest,
)
from hhs_runtime.pass218.manifest_bound_i30_promotion_request_authorization_i43 import (
    PASS218_I43_AUTHORIZED_PENDING_STATUS,
    PASS218_I43_COMPLETE_STATUS,
    _i29_request_sha256,
    _i30_request_sha256,
    _verify_i43_proof,
    _verify_i43_receipt,
)

PASS218_I44_VERSION = "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-V1"
PASS218_I44_SCOPE = "PASS218_MANIFEST_BOUND_I30_ATOMIC_PROMOTION"
PASS218_I44_PROOF_SCHEMA = "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-PROOF-V1"
PASS218_I44_RECEIPT_SCHEMA = "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-RECEIPT-V1"
PASS218_I44_STATE_SCHEMA = "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-STATE-V1"
PASS218_I44_STATUS_SCHEMA = "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-STATUS-V1"
PASS218_I44_COMPLETE_STATUS = "MANIFEST_BOUND_I30_ATOMIC_PROMOTION_COMPLETE"
PASS218_I44_PENDING_STATUS = "MANIFEST_BOUND_I30_ATOMIC_PROMOTION_PENDING"
PASS218_I44_PROMOTED_PENDING_I31_STATUS = "ATOMIC_PROMOTION_COMMITTED_PENDING_I31"


class Pass218I44PromotionError(RuntimeError):
    pass


class Pass218I44BindingError(Pass218I44PromotionError):
    pass


class Pass218I44StateError(Pass218I44PromotionError):
    pass


class Pass218I44LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I44I43StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class Pass218I44I30PromoterProtocol(Protocol):
    promotion_count: int
    store: Any
    def promote(self, request: Pass218I30PromotionRequest) -> dict[str, Any]: ...
    def status(self) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I44BindingError("P218_I44_AUTHORITATIVE_FLOAT_FORBIDDEN")
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


def _valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _valid_hash216(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _path_safe_hash72_name(value: str) -> str:
    if not validate_hash72(value):
        raise Pass218I44StateError("P218_I44_PATH_HASH72_INVALID")
    return sha256(value.encode("utf-8")).hexdigest()


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(_canonical_bytes(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    try:
        directory_fd = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass218I44StateError("P218_I44_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I44StateError("P218_I44_STATE_OBJECT_REQUIRED")
    return value


def _verify_i30_receipt(
    receipt: Mapping[str, Any],
    *,
    i43: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I30_PROMOTION_RECEIPT_SCHEMA:
        raise Pass218I44BindingError("P218_I44_I30_RECEIPT_SCHEMA_INVALID")
    if value.get("promotion_status") != PASS218_I30_PENDING_PURGE_STATUS:
        raise Pass218I44BindingError("P218_I44_I30_PROMOTION_STATUS_INVALID")
    if value.get("purge_status") != "PENDING_VERBATIM_PURGE":
        raise Pass218I44BindingError("P218_I44_I30_PURGE_STATUS_INVALID")
    if value.get("i29_validation_hash72") != i43.get("i29_validation_hash72"):
        raise Pass218I44BindingError("P218_I44_I30_I29_VALIDATION_MISMATCH")
    if value.get("validated_hash216") != i43.get("i29_validated_hash216"):
        raise Pass218I44BindingError("P218_I44_I30_VALIDATED_HASH216_MISMATCH")
    if value.get("grant_hash72") != i43.get("i30_grant_hash72"):
        raise Pass218I44BindingError("P218_I44_I30_GRANT_HASH_MISMATCH")
    for field in (
        "i29_validation_hash72",
        "promoted_object_hash72",
        "grant_hash72",
        "target_root_before_hash72",
        "target_root_after_hash72",
        "root_verification_hash72",
        "promotion_hash72",
        "promotion_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I44BindingError("P218_I44_I30_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("validated_hash216")):
        raise Pass218I44BindingError("P218_I44_I30_VALIDATED_HASH216_INVALID")
    if not _valid_hash216(value.get("promotion_hash216")):
        raise Pass218I44BindingError("P218_I44_I30_PROMOTION_HASH216_INVALID")
    if not _valid_sha256(value.get("candidate_sha256")):
        raise Pass218I44BindingError("P218_I44_I30_CANDIDATE_SHA256_INVALID")
    required_true = (
        "candidate_commit_verified",
        "prospective_root_verified",
        "formal_semantic_round_trip_verified",
        "grounded_round_trip_verified",
        "perspective_round_trip_verified",
        "vm5184_authoritative_projection_invoked",
        "vm5184_authoritative_state_committed",
        "atomic_promotion_authorized",
        "atomic_promotion_invoked",
        "atomic_manifest_swap",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I44BindingError("P218_I44_I30_PROMOTION_INCOMPLETE")
    required_false = (
        "failed_partial_promotion_possible",
        "vm81_authorization_invoked",
        "verbatim_purge_invoked",
        "purge_receipt_issued",
        "curriculum_advance_permitted",
        "closure_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I44BindingError("P218_I44_I30_DOWNSTREAM_AUTHORITY_DRIFT")
    return value


def _verify_active_i30_generation(
    generation: Mapping[str, Any],
    *,
    i43: Mapping[str, Any],
    i30_status: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    value = _copy(dict(generation))
    receipt_raw = value.get("promotion_receipt")
    promoted_raw = value.get("promoted_object")
    if not isinstance(receipt_raw, Mapping) or not isinstance(promoted_raw, Mapping):
        raise Pass218I44BindingError("P218_I44_I30_GENERATION_CONTENT_INVALID")
    receipt = _verify_i30_receipt(receipt_raw, i43=i43)
    promoted = _copy(dict(promoted_raw))
    if promoted.get("schema") != PASS218_I30_PROMOTED_OBJECT_SCHEMA:
        raise Pass218I44BindingError("P218_I44_I30_PROMOTED_OBJECT_SCHEMA_INVALID")
    if promoted.get("promoted_object_hash72") != receipt["promoted_object_hash72"]:
        raise Pass218I44BindingError("P218_I44_I30_PROMOTED_OBJECT_HASH_MISMATCH")
    if promoted.get("i29_validation_hash72") != receipt["i29_validation_hash72"]:
        raise Pass218I44BindingError("P218_I44_I30_PROMOTED_I29_HASH_MISMATCH")
    if promoted.get("validated_hash216") != receipt["validated_hash216"]:
        raise Pass218I44BindingError("P218_I44_I30_PROMOTED_HASH216_MISMATCH")
    if promoted.get("grant_hash72") != receipt["grant_hash72"]:
        raise Pass218I44BindingError("P218_I44_I30_PROMOTED_GRANT_MISMATCH")
    if promoted.get("purge_status") != "PENDING_VERBATIM_PURGE":
        raise Pass218I44BindingError("P218_I44_I30_PROMOTED_PURGE_STATUS_INVALID")
    for field in (
        "source_text_retained",
        "source_token_stream_retained",
        "verbatim_corpus_source_retained",
        "curriculum_advance_permitted",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    ):
        if promoted.get(field) is not False:
            raise Pass218I44BindingError("P218_I44_I30_PROMOTED_AUTHORITY_DRIFT:" + field)
    vm = promoted.get("vm5184_authority")
    if not isinstance(vm, Mapping):
        raise Pass218I44BindingError("P218_I44_VM5184_AUTHORITY_REQUIRED")
    if vm.get("authoritative_projection") is not True or vm.get("vm81_mutation") is not False:
        raise Pass218I44BindingError("P218_I44_VM5184_AUTHORITY_INVALID")
    if vm.get("canonical_float_fields") != 0:
        raise Pass218I44BindingError("P218_I44_VM5184_FLOAT_AUTHORITY_INVALID")
    if i30_status.get("promotion_present") is not True:
        raise Pass218I44BindingError("P218_I44_I30_STATUS_PROMOTION_REQUIRED")
    if i30_status.get("promotion_status") != PASS218_I30_PENDING_PURGE_STATUS:
        raise Pass218I44BindingError("P218_I44_I30_STATUS_PROMOTION_MISMATCH")
    if i30_status.get("canonical_root_hash72") != receipt["target_root_after_hash72"]:
        raise Pass218I44BindingError("P218_I44_I30_STATUS_ROOT_MISMATCH")
    if i30_status.get("promotion_receipt_hash72") != receipt["promotion_receipt_hash72"]:
        raise Pass218I44BindingError("P218_I44_I30_STATUS_RECEIPT_MISMATCH")
    if i30_status.get("grant_hash72") != receipt["grant_hash72"]:
        raise Pass218I44BindingError("P218_I44_I30_STATUS_GRANT_MISMATCH")
    return receipt, promoted


def _verify_i44_proof(
    proof: Mapping[str, Any],
    receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value = _copy(dict(proof))
    if value.get("schema") != PASS218_I44_PROOF_SCHEMA:
        raise Pass218I44StateError("P218_I44_PROOF_SCHEMA_INVALID")
    if value.get("status") != PASS218_I44_PROMOTED_PENDING_I31_STATUS:
        raise Pass218I44StateError("P218_I44_PROOF_STATUS_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I44StateError("P218_I44_PROOF_TARGET_INVALID")
    for field in (
        "i43_receipt_hash72",
        "i43_authorization_proof_hash72",
        "i30_grant_hash72",
        "i30_promotion_receipt_hash72",
        "i30_promotion_hash72",
        "i30_promoted_object_hash72",
        "i30_target_root_before_hash72",
        "i30_target_root_after_hash72",
        "i30_root_verification_hash72",
        "manifest_bound_i30_atomic_promotion_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I44StateError("P218_I44_PROOF_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i30_promotion_hash216")):
        raise Pass218I44StateError("P218_I44_PROOF_HASH216_INVALID")
    for field in (
        "i29_validation_request_sha256",
        "i30_promotion_request_sha256",
        "i30_candidate_sha256",
    ):
        if not _valid_sha256(value.get(field)):
            raise Pass218I44StateError("P218_I44_PROOF_SHA256_INVALID:" + field)
    required_true = (
        "i43_authorization_consumed",
        "i30_request_fingerprint_matches_i43",
        "i29_request_fingerprint_matches_i43",
        "i30_grant_identity_matches_i43",
        "i30_atomic_promotion_committed",
        "i30_atomic_manifest_swap_verified",
        "i30_durable_generation_verified",
        "i30_canonical_root_verified",
        "vm5184_authoritative_projection_verified",
        "vm5184_authoritative_state_committed",
        "i30_exactly_once_or_restart_adoption_verified",
        "restart_does_not_require_duplicate_i30_invocation",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I44StateError("P218_I44_PROOF_INCOMPLETE")
    required_false = (
        "i30_promotion_request_persisted",
        "source_payload_persisted",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I44StateError("P218_I44_PROOF_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key != "manifest_bound_i30_atomic_promotion_hash72"}
    expected = hash72_digest({"domain": PASS218_I44_PROOF_SCHEMA}, body)
    if expected != value.get("manifest_bound_i30_atomic_promotion_hash72"):
        raise Pass218I44StateError("P218_I44_PROOF_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get("manifest_bound_i30_atomic_promotion_hash72"):
        raise Pass218I44StateError("P218_I44_PROOF_RECEIPT_MISMATCH")
    return value


def _verify_i44_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I44_RECEIPT_SCHEMA:
        raise Pass218I44StateError("P218_I44_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I44_COMPLETE_STATUS:
        raise Pass218I44StateError("P218_I44_RECEIPT_STATUS_INVALID")
    if value.get("promotion_status") != PASS218_I44_PROMOTED_PENDING_I31_STATUS:
        raise Pass218I44StateError("P218_I44_RECEIPT_PROMOTION_STATUS_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I44StateError("P218_I44_RECEIPT_TARGET_INVALID")
    for field in (
        "i43_receipt_hash72",
        "i43_authorization_proof_hash72",
        "i30_grant_hash72",
        "i30_promotion_receipt_hash72",
        "i30_promoted_object_hash72",
        "i30_target_root_after_hash72",
        "manifest_bound_i30_atomic_promotion_hash72",
        "i44_validation_hash72",
        "i44_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I44StateError("P218_I44_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i44_hash216")):
        raise Pass218I44StateError("P218_I44_RECEIPT_HASH216_INVALID")
    if value["i44_hash216"] != (
        str(value["i43_receipt_hash72"])
        + str(value["i30_promotion_receipt_hash72"])
        + str(value["i44_receipt_hash72"])
    ):
        raise Pass218I44StateError("P218_I44_HASH216_ORDER_INVALID")
    for field in ("i29_validation_request_sha256", "i30_promotion_request_sha256", "i30_candidate_sha256"):
        if not _valid_sha256(value.get(field)):
            raise Pass218I44StateError("P218_I44_RECEIPT_SHA256_INVALID:" + field)
    required_true = (
        "i43_authorization_consumed",
        "i30_atomic_promotion_committed",
        "i30_durable_generation_verified",
        "i30_canonical_root_verified",
        "vm5184_authoritative_projection_invoked",
        "vm5184_authoritative_state_committed",
        "restart_safe_exact_promotion_adoption",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I44StateError("P218_I44_RECEIPT_INCOMPLETE")
    required_false = (
        "i30_promotion_request_persisted",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I44StateError("P218_I44_RECEIPT_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key not in {"i44_receipt_hash72", "i44_hash216", "i44_hash216_semantics"}}
    expected = hash72_digest({"domain": PASS218_I44_RECEIPT_SCHEMA}, body)
    if expected != value.get("i44_receipt_hash72"):
        raise Pass218I44StateError("P218_I44_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I44PromotionStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.proof_root = self.root / "proofs"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I44_STATE_SCHEMA:
            raise Pass218I44StateError("P218_I44_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I44_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I44StateError("P218_I44_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        proof_path = self.root / str(state.get("active_proof_path", ""))
        if not receipt_path.is_file() or not proof_path.is_file():
            raise Pass218I44StateError("P218_I44_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i44_receipt(_load_json(receipt_path))
        proof = _verify_i44_proof(_load_json(proof_path), receipt)
        if receipt["i44_receipt_hash72"] != state.get("active_i44_receipt_hash72"):
            raise Pass218I44StateError("P218_I44_STATE_RECEIPT_MISMATCH")
        if proof["manifest_bound_i30_atomic_promotion_hash72"] != state.get("active_proof_hash72"):
            raise Pass218I44StateError("P218_I44_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i44_proof(_load_json(self.root / str(state["active_proof_path"])), receipt)

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i44_receipt(receipt)
        checked_proof = _verify_i44_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I44StateError("P218_I44_ACTIVE_BINDING_CONFLICT")
            return existing
        receipt_name = _path_safe_hash72_name(str(checked["i44_receipt_hash72"]))
        proof_name = _path_safe_hash72_name(str(checked_proof["manifest_bound_i30_atomic_promotion_hash72"]))
        receipt_path = self.receipt_root / f"{receipt_name}.json"
        proof_path = self.proof_root / f"{proof_name}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(proof_path, checked_proof)
        state_body = {
            "schema": PASS218_I44_STATE_SCHEMA,
            "version": PASS218_I44_VERSION,
            "status": PASS218_I44_COMPLETE_STATUS,
            "promotion_status": PASS218_I44_PROMOTED_PENDING_I31_STATUS,
            "i43_receipt_hash72": checked["i43_receipt_hash72"],
            "i30_promotion_request_sha256": checked["i30_promotion_request_sha256"],
            "i30_promotion_receipt_hash72": checked["i30_promotion_receipt_hash72"],
            "i30_target_root_after_hash72": checked["i30_target_root_after_hash72"],
            "active_i44_receipt_hash72": checked["i44_receipt_hash72"],
            "active_proof_hash72": checked_proof["manifest_bound_i30_atomic_promotion_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_proof_path": proof_path.relative_to(self.root).as_posix(),
        }
        state = {**state_body, "state_root_hash72": hash72_digest({"domain": PASS218_I44_STATE_SCHEMA}, state_body)}
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I44StateError("P218_I44_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I44ManifestBoundI30AtomicPromotion:
    def __init__(
        self,
        *,
        lifecycle: Pass218I44LifecycleProtocol,
        i43_store: Pass218I44I43StoreProtocol,
        i30_promoter: Pass218I44I30PromoterProtocol,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.lifecycle = lifecycle
        self.i43_store = i43_store
        self.i30_promoter = i30_promoter
        self.store = Pass218I44PromotionStore(state_root)
        self.i30_invocation_count = 0
        self.restart_adoption_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_i43(self) -> tuple[dict[str, Any], dict[str, Any]]:
        receipt = self.i43_store.active_record()
        proof = self.i43_store.active_proof()
        if not isinstance(receipt, Mapping) or not isinstance(proof, Mapping):
            raise Pass218I44BindingError("P218_I44_I43_COMPLETE_AUTHORIZATION_REQUIRED")
        checked = _verify_i43_receipt(receipt)
        checked_proof = _verify_i43_proof(proof, checked)
        if checked.get("status") != PASS218_I43_COMPLETE_STATUS:
            raise Pass218I44BindingError("P218_I44_I43_COMPLETE_STATUS_REQUIRED")
        if checked.get("authorization_status") != PASS218_I43_AUTHORIZED_PENDING_STATUS:
            raise Pass218I44BindingError("P218_I44_I43_AUTHORIZATION_REQUIRED")
        return checked, checked_proof

    @staticmethod
    def _verify_request(
        request: Pass218I30PromotionRequest,
        *,
        i43: Mapping[str, Any],
        i43_proof: Mapping[str, Any],
    ) -> tuple[Pass218I30PromotionRequest, str, str]:
        validated = request.validated()
        i29_sha = _i29_request_sha256(validated)
        i30_sha = _i30_request_sha256(validated)
        if i29_sha != i43.get("i29_validation_request_sha256") or i29_sha != i43_proof.get("i29_validation_request_sha256"):
            raise Pass218I44BindingError("P218_I44_I29_REQUEST_FINGERPRINT_MISMATCH")
        if i30_sha != i43.get("i30_promotion_request_sha256") or i30_sha != i43_proof.get("i30_promotion_request_sha256"):
            raise Pass218I44BindingError("P218_I44_I30_REQUEST_FINGERPRINT_MISMATCH")
        if validated.grantor_authority_hash72 != i43.get("grantor_authority_hash72"):
            raise Pass218I44BindingError("P218_I44_GRANTOR_MISMATCH")
        if validated.grant_sequence != i43.get("grant_sequence"):
            raise Pass218I44BindingError("P218_I44_GRANT_SEQUENCE_MISMATCH")
        if validated.expected_i29_validation_hash72 != i43.get("i29_validation_hash72"):
            raise Pass218I44BindingError("P218_I44_EXPECTED_I29_VALIDATION_MISMATCH")
        if validated.expected_validated_hash216 != i43.get("i29_validated_hash216"):
            raise Pass218I44BindingError("P218_I44_EXPECTED_HASH216_MISMATCH")
        if validated.target_scope != PASS218_I30_TARGET_SCOPE:
            raise Pass218I44BindingError("P218_I44_I30_TARGET_SCOPE_INVALID")
        if i43.get("i30_grant_hash72") != i43_proof.get("i30_grant_hash72"):
            raise Pass218I44BindingError("P218_I44_I43_GRANT_PROOF_MISMATCH")
        return validated, i29_sha, i30_sha

    @staticmethod
    def _build(
        *,
        i43: Mapping[str, Any],
        i43_proof: Mapping[str, Any],
        i29_sha: str,
        i30_sha: str,
        i30_receipt: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        proof_body = {
            "schema": PASS218_I44_PROOF_SCHEMA,
            "version": PASS218_I44_VERSION,
            "scope": PASS218_I44_SCOPE,
            "status": PASS218_I44_PROMOTED_PENDING_I31_STATUS,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i43_receipt_hash72": i43["i43_receipt_hash72"],
            "i43_authorization_proof_hash72": i43["manifest_bound_i30_request_authorization_hash72"],
            "i29_validation_request_sha256": i29_sha,
            "i30_promotion_request_sha256": i30_sha,
            "i30_grant_hash72": i30_receipt["grant_hash72"],
            "i30_promotion_receipt_hash72": i30_receipt["promotion_receipt_hash72"],
            "i30_promotion_hash72": i30_receipt["promotion_hash72"],
            "i30_promotion_hash216": i30_receipt["promotion_hash216"],
            "i30_promoted_object_hash72": i30_receipt["promoted_object_hash72"],
            "i30_candidate_sha256": i30_receipt["candidate_sha256"],
            "i30_target_root_before_hash72": i30_receipt["target_root_before_hash72"],
            "i30_target_root_after_hash72": i30_receipt["target_root_after_hash72"],
            "i30_root_verification_hash72": i30_receipt["root_verification_hash72"],
            "shared_identity": _copy(i43_proof.get("shared_identity", {})),
            "i43_authorization_consumed": True,
            "i30_request_fingerprint_matches_i43": True,
            "i29_request_fingerprint_matches_i43": True,
            "i30_grant_identity_matches_i43": True,
            "i30_atomic_promotion_committed": True,
            "i30_atomic_manifest_swap_verified": True,
            "i30_durable_generation_verified": True,
            "i30_canonical_root_verified": True,
            "vm5184_authoritative_projection_verified": True,
            "vm5184_authoritative_state_committed": True,
            "i30_exactly_once_or_restart_adoption_verified": True,
            "restart_does_not_require_duplicate_i30_invocation": True,
            "i30_promotion_request_persisted": False,
            "source_payload_persisted": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        proof_hash72 = hash72_digest({"domain": PASS218_I44_PROOF_SCHEMA}, proof_body)
        proof = {**proof_body, "manifest_bound_i30_atomic_promotion_hash72": proof_hash72}
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I44-ATOMIC-PROMOTION-VALIDATION-V1"},
            {
                "i43_receipt_hash72": i43["i43_receipt_hash72"],
                "i30_promotion_request_sha256": i30_sha,
                "i30_grant_hash72": i30_receipt["grant_hash72"],
                "i30_promotion_receipt_hash72": i30_receipt["promotion_receipt_hash72"],
                "i30_target_root_after_hash72": i30_receipt["target_root_after_hash72"],
                "atomic_promotion_committed": True,
                "pending_i31": True,
            },
        )
        body = {
            "schema": PASS218_I44_RECEIPT_SCHEMA,
            "version": PASS218_I44_VERSION,
            "scope": PASS218_I44_SCOPE,
            "status": PASS218_I44_COMPLETE_STATUS,
            "promotion_status": PASS218_I44_PROMOTED_PENDING_I31_STATUS,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i43_receipt_hash72": i43["i43_receipt_hash72"],
            "i43_authorization_proof_hash72": i43["manifest_bound_i30_request_authorization_hash72"],
            "manifest_bound_i30_atomic_promotion_hash72": proof_hash72,
            "i29_validation_request_sha256": i29_sha,
            "i30_promotion_request_sha256": i30_sha,
            "i30_grant_hash72": i30_receipt["grant_hash72"],
            "i30_promotion_receipt_hash72": i30_receipt["promotion_receipt_hash72"],
            "i30_promoted_object_hash72": i30_receipt["promoted_object_hash72"],
            "i30_candidate_sha256": i30_receipt["candidate_sha256"],
            "i30_target_root_after_hash72": i30_receipt["target_root_after_hash72"],
            "i44_validation_hash72": validation_hash72,
            "i43_authorization_consumed": True,
            "i30_atomic_promotion_committed": True,
            "i30_durable_generation_verified": True,
            "i30_canonical_root_verified": True,
            "vm5184_authoritative_projection_invoked": True,
            "vm5184_authoritative_state_committed": True,
            "restart_safe_exact_promotion_adoption": True,
            "i30_promotion_request_persisted": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        receipt_hash72 = hash72_digest({"domain": PASS218_I44_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i44_receipt_hash72": receipt_hash72,
            "i44_hash216": i43["i43_receipt_hash72"] + i30_receipt["promotion_receipt_hash72"] + receipt_hash72,
            "i44_hash216_semantics": [
                "I43_EXACT_I30_PROMOTION_REQUEST_AUTHORIZATION_RECEIPT",
                "I30_ATOMIC_SEMANTIC_PROMOTION_RECEIPT",
                "I44_MANIFEST_BOUND_ATOMIC_PROMOTION_RECEIPT",
            ],
        }
        return _verify_i44_proof(proof), _verify_i44_receipt(receipt)

    def promote(self, promotion_request: Pass218I30PromotionRequest) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i43, i43_proof = self._active_i43()
            request, i29_sha, i30_sha = self._verify_request(
                promotion_request,
                i43=i43,
                i43_proof=i43_proof,
            )
            existing_i44 = self.store.active_record()
            active_generation = self.i30_promoter.store.active_generation()
            if existing_i44 is not None:
                if existing_i44["i43_receipt_hash72"] != i43["i43_receipt_hash72"]:
                    raise Pass218I44StateError("P218_I44_ACTIVE_I43_CONFLICT")
                if existing_i44["i30_promotion_request_sha256"] != i30_sha:
                    raise Pass218I44StateError("P218_I44_ACTIVE_REQUEST_CONFLICT")
                if not isinstance(active_generation, Mapping):
                    raise Pass218I44StateError("P218_I44_ACTIVE_I30_GENERATION_MISSING")
                active_receipt, _ = _verify_active_i30_generation(
                    active_generation,
                    i43=i43,
                    i30_status=self.i30_promoter.status(),
                )
                if active_receipt["promotion_receipt_hash72"] != existing_i44["i30_promotion_receipt_hash72"]:
                    raise Pass218I44StateError("P218_I44_ACTIVE_I30_RECEIPT_CONFLICT")
                self.last_error_code = None
                return existing_i44

            if isinstance(active_generation, Mapping):
                i30_receipt, _ = _verify_active_i30_generation(
                    active_generation,
                    i43=i43,
                    i30_status=self.i30_promoter.status(),
                )
                self.restart_adoption_count += 1
            else:
                status_before = self.i30_promoter.status()
                if bool(status_before.get("promotion_present")) or bool(status_before.get("atomic_promotion_invoked")):
                    raise Pass218I44StateError("P218_I44_I30_NONEMPTY_WITHOUT_GENERATION")
                promotion_count_before = int(self.i30_promoter.promotion_count)
                returned = self.i30_promoter.promote(request)
                self.i30_invocation_count += 1
                if int(self.i30_promoter.promotion_count) != promotion_count_before + 1:
                    raise Pass218I44StateError("P218_I44_I30_SINGLE_INVOCATION_NOT_PROVEN")
                active_generation = self.i30_promoter.store.active_generation()
                if not isinstance(active_generation, Mapping):
                    raise Pass218I44StateError("P218_I44_I30_DURABLE_GENERATION_MISSING")
                i30_receipt, _ = _verify_active_i30_generation(
                    active_generation,
                    i43=i43,
                    i30_status=self.i30_promoter.status(),
                )
                if _copy(returned) != i30_receipt:
                    raise Pass218I44StateError("P218_I44_I30_RETURNED_DURABLE_RECEIPT_MISMATCH")

            proof, receipt = self._build(
                i43=i43,
                i43_proof=i43_proof,
                i29_sha=i29_sha,
                i30_sha=i30_sha,
                i30_receipt=i30_receipt,
            )
            persisted = self.store.commit(receipt, proof)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i43_ready = False
        active_i43_receipt_hash72: str | None = None
        try:
            i43, _ = self._active_i43()
            i43_ready = True
            active_i43_receipt_hash72 = str(i43["i43_receipt_hash72"])
        except Exception:
            pass
        i30 = self.i30_promoter.status()
        return {
            "schema": PASS218_I44_STATUS_SCHEMA,
            "version": PASS218_I44_VERSION,
            "status": PASS218_I44_COMPLETE_STATUS if active is not None else PASS218_I44_PENDING_STATUS,
            "promotion_status": None if active is None else PASS218_I44_PROMOTED_PENDING_I31_STATUS,
            "predecessor_i43_authorization_ready": i43_ready,
            "active_i43_receipt_hash72": active_i43_receipt_hash72,
            "active_i44_receipt_hash72": None if active is None else active["i44_receipt_hash72"],
            "active_i30_promotion_receipt_hash72": None if active is None else active["i30_promotion_receipt_hash72"],
            "i30_promotion_request_sha256": None if active is None else active["i30_promotion_request_sha256"],
            "i30_canonical_root_hash72": i30.get("canonical_root_hash72"),
            "i30_promotion_present": bool(i30.get("promotion_present")),
            "i30_invocation_count_current_process": self.i30_invocation_count,
            "restart_adoption_count_current_process": self.restart_adoption_count,
            "i30_atomic_promotion_committed": active is not None,
            "vm5184_authoritative_projection_invoked": active is not None,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I44_COMPLETE_STATUS",
    "PASS218_I44_PENDING_STATUS",
    "PASS218_I44_PROMOTED_PENDING_I31_STATUS",
    "PASS218_I44_PROOF_SCHEMA",
    "PASS218_I44_RECEIPT_SCHEMA",
    "PASS218_I44_SCOPE",
    "PASS218_I44_STATE_SCHEMA",
    "PASS218_I44_STATUS_SCHEMA",
    "PASS218_I44_VERSION",
    "Pass218I44BindingError",
    "Pass218I44ManifestBoundI30AtomicPromotion",
    "Pass218I44PromotionError",
    "Pass218I44PromotionStore",
    "Pass218I44StateError",
]