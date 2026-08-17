"""Pass 218 Iteration 45 manifest-bound one-time I31 verbatim purge.

I45 consumes only the exact durable I44 manifest-bound I30 atomic promotion.
It derives the frozen-I31 purge request from durable I44/I30 identities, invokes
frozen I31 exactly once when the I31 store is empty, and proves the durable I30
semantic generation is byte-identical before and after purge.  If I31 already
committed the exact bound purge but I45 persistence was interrupted, restart
recovery adopts that receipt without invoking I31 again.

I45 does not invoke I32, advance curriculum, mutate VM81, perform canonical
learning, promote truth, mint action authority, activate a model, retain source
payload, or create floating-point authority.
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
)
from hhs_runtime.pass218.manifest_bound_i30_atomic_promotion_i44 import (
    PASS218_I44_COMPLETE_STATUS,
    PASS218_I44_PROMOTED_PENDING_I31_STATUS,
    _verify_i44_proof,
    _verify_i44_receipt,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGED_STATUS,
    PASS218_I31_PURGE_RECEIPT_SCHEMA,
    PASS218_I31_PURGE_SCOPE,
    PASS218_I31_QUARANTINE_SCHEMA,
    Pass218I31PurgeRequest,
)

PASS218_I45_VERSION = "HHS-P218-I45-MANIFEST-BOUND-I31-VERBATIM-PURGE-V1"
PASS218_I45_SCOPE = "PASS218_MANIFEST_BOUND_I31_VERBATIM_PURGE"
PASS218_I45_PROOF_SCHEMA = "HHS-P218-I45-MANIFEST-BOUND-I31-VERBATIM-PURGE-PROOF-V1"
PASS218_I45_RECEIPT_SCHEMA = "HHS-P218-I45-MANIFEST-BOUND-I31-VERBATIM-PURGE-RECEIPT-V1"
PASS218_I45_STATE_SCHEMA = "HHS-P218-I45-MANIFEST-BOUND-I31-VERBATIM-PURGE-STATE-V1"
PASS218_I45_STATUS_SCHEMA = "HHS-P218-I45-MANIFEST-BOUND-I31-VERBATIM-PURGE-STATUS-V1"
PASS218_I45_COMPLETE_STATUS = "MANIFEST_BOUND_I31_VERBATIM_PURGE_COMPLETE"
PASS218_I45_PENDING_STATUS = "MANIFEST_BOUND_I31_VERBATIM_PURGE_PENDING"
PASS218_I45_PURGED_PENDING_I32_STATUS = PASS218_I31_PURGED_STATUS


class Pass218I45PurgeError(RuntimeError):
    pass


class Pass218I45BindingError(Pass218I45PurgeError):
    pass


class Pass218I45StateError(Pass218I45PurgeError):
    pass


class Pass218I45LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I45I44StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class Pass218I45I31PurgerProtocol(Protocol):
    purge_count: int
    store: Any
    i30_store: Any
    managed_buffers: Any
    def purge(self, request: Pass218I31PurgeRequest) -> dict[str, Any]: ...
    def status(self) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I45BindingError("P218_I45_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        and all(symbol in "0123456789abcdef" for symbol in value)
    )


def _valid_hash216(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _path_safe_hash72_name(value: str) -> str:
    if not validate_hash72(value):
        raise Pass218I45StateError("P218_I45_PATH_HASH72_INVALID")
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
        raise Pass218I45StateError("P218_I45_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I45StateError("P218_I45_STATE_OBJECT_REQUIRED")
    return value


def _verify_i30_generation(
    generation: Mapping[str, Any],
    *,
    i44: Mapping[str, Any],
    i44_proof: Mapping[str, Any],
    i30_status: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    value = _copy(dict(generation))
    receipt_raw = value.get("promotion_receipt")
    promoted_raw = value.get("promoted_object")
    if not isinstance(receipt_raw, Mapping) or not isinstance(promoted_raw, Mapping):
        raise Pass218I45BindingError("P218_I45_I30_GENERATION_CONTENT_INVALID")
    receipt = _copy(dict(receipt_raw))
    promoted = _copy(dict(promoted_raw))
    if receipt.get("schema") != PASS218_I30_PROMOTION_RECEIPT_SCHEMA:
        raise Pass218I45BindingError("P218_I45_I30_RECEIPT_SCHEMA_INVALID")
    if promoted.get("schema") != PASS218_I30_PROMOTED_OBJECT_SCHEMA:
        raise Pass218I45BindingError("P218_I45_I30_PROMOTED_OBJECT_SCHEMA_INVALID")
    if receipt.get("promotion_status") != PASS218_I30_PENDING_PURGE_STATUS:
        raise Pass218I45BindingError("P218_I45_I30_PROMOTION_STATUS_INVALID")
    if receipt.get("purge_status") != "PENDING_VERBATIM_PURGE":
        raise Pass218I45BindingError("P218_I45_I30_PURGE_STATUS_INVALID")
    bindings = (
        (receipt.get("promotion_receipt_hash72"), i44.get("i30_promotion_receipt_hash72"), "P218_I45_I30_RECEIPT_I44_MISMATCH"),
        (receipt.get("promotion_receipt_hash72"), i44_proof.get("i30_promotion_receipt_hash72"), "P218_I45_I30_RECEIPT_PROOF_MISMATCH"),
        (receipt.get("promotion_hash72"), i44_proof.get("i30_promotion_hash72"), "P218_I45_I30_PROMOTION_HASH_MISMATCH"),
        (receipt.get("promotion_hash216"), i44_proof.get("i30_promotion_hash216"), "P218_I45_I30_PROMOTION_HASH216_MISMATCH"),
        (receipt.get("promoted_object_hash72"), i44.get("i30_promoted_object_hash72"), "P218_I45_I30_PROMOTED_OBJECT_I44_MISMATCH"),
        (receipt.get("promoted_object_hash72"), i44_proof.get("i30_promoted_object_hash72"), "P218_I45_I30_PROMOTED_OBJECT_PROOF_MISMATCH"),
        (receipt.get("candidate_sha256"), i44.get("i30_candidate_sha256"), "P218_I45_I30_CANDIDATE_I44_MISMATCH"),
        (receipt.get("target_root_after_hash72"), i44.get("i30_target_root_after_hash72"), "P218_I45_I30_ROOT_I44_MISMATCH"),
        (receipt.get("target_root_after_hash72"), i44_proof.get("i30_target_root_after_hash72"), "P218_I45_I30_ROOT_PROOF_MISMATCH"),
        (receipt.get("grant_hash72"), i44.get("i30_grant_hash72"), "P218_I45_I30_GRANT_I44_MISMATCH"),
    )
    for actual, expected, code in bindings:
        if actual != expected:
            raise Pass218I45BindingError(code)
    for field in (
        "promotion_receipt_hash72",
        "promotion_hash72",
        "promoted_object_hash72",
        "target_root_after_hash72",
        "i29_validation_hash72",
        "grant_hash72",
    ):
        if not validate_hash72(str(receipt.get(field, ""))):
            raise Pass218I45BindingError("P218_I45_I30_HASH72_INVALID:" + field)
    if not _valid_hash216(receipt.get("promotion_hash216")):
        raise Pass218I45BindingError("P218_I45_I30_HASH216_INVALID")
    if not _valid_sha256(receipt.get("candidate_sha256")):
        raise Pass218I45BindingError("P218_I45_I30_CANDIDATE_SHA256_INVALID")
    if promoted.get("promoted_object_hash72") != receipt["promoted_object_hash72"]:
        raise Pass218I45BindingError("P218_I45_PROMOTED_OBJECT_HASH_MISMATCH")
    if promoted.get("i29_validation_hash72") != receipt["i29_validation_hash72"]:
        raise Pass218I45BindingError("P218_I45_PROMOTED_I29_MISMATCH")
    if promoted.get("validated_hash216") != receipt.get("validated_hash216"):
        raise Pass218I45BindingError("P218_I45_PROMOTED_HASH216_MISMATCH")
    if promoted.get("purge_status") != "PENDING_VERBATIM_PURGE":
        raise Pass218I45BindingError("P218_I45_PROMOTED_PURGE_STATUS_INVALID")
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
            raise Pass218I45BindingError("P218_I45_PROMOTED_AUTHORITY_DRIFT:" + field)
    if i30_status.get("promotion_present") is not True:
        raise Pass218I45BindingError("P218_I45_I30_STATUS_PROMOTION_REQUIRED")
    if i30_status.get("promotion_status") != PASS218_I30_PENDING_PURGE_STATUS:
        raise Pass218I45BindingError("P218_I45_I30_STATUS_PROMOTION_INVALID")
    if i30_status.get("canonical_root_hash72") != receipt["target_root_after_hash72"]:
        raise Pass218I45BindingError("P218_I45_I30_STATUS_ROOT_MISMATCH")
    generation_sha256 = sha256(_canonical_bytes(value)).hexdigest()
    return receipt, promoted, generation_sha256


def _derive_i31_request(i30_receipt: Mapping[str, Any]) -> Pass218I31PurgeRequest:
    return Pass218I31PurgeRequest(
        expected_i30_promotion_receipt_hash72=str(i30_receipt["promotion_receipt_hash72"]),
        expected_i30_promotion_hash72=str(i30_receipt["promotion_hash72"]),
        expected_promoted_object_hash72=str(i30_receipt["promoted_object_hash72"]),
        expected_canonical_root_hash72=str(i30_receipt["target_root_after_hash72"]),
        expected_i29_validation_hash72=str(i30_receipt["i29_validation_hash72"]),
        purge_scope=PASS218_I31_PURGE_SCOPE,
    ).validated()


def _verify_i31_receipt(
    receipt: Mapping[str, Any],
    *,
    i30_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") == PASS218_I31_QUARANTINE_SCHEMA:
        raise Pass218I45StateError("P218_I45_I31_QUARANTINED")
    if value.get("schema") != PASS218_I31_PURGE_RECEIPT_SCHEMA:
        raise Pass218I45StateError("P218_I45_I31_RECEIPT_SCHEMA_INVALID")
    if value.get("purge_status") != PASS218_I31_PURGED_STATUS:
        raise Pass218I45StateError("P218_I45_I31_PURGE_STATUS_INVALID")
    expected = {
        "i30_promotion_receipt_hash72": i30_receipt["promotion_receipt_hash72"],
        "i30_promotion_hash72": i30_receipt["promotion_hash72"],
        "i29_validation_hash72": i30_receipt["i29_validation_hash72"],
        "validated_hash216": i30_receipt["validated_hash216"],
        "promoted_object_hash72": i30_receipt["promoted_object_hash72"],
        "canonical_root_hash72": i30_receipt["target_root_after_hash72"],
        "candidate_sha256": i30_receipt["candidate_sha256"],
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise Pass218I45BindingError("P218_I45_I31_BINDING_MISMATCH:" + field)
    for field in (
        "i30_promotion_receipt_hash72",
        "i30_promotion_hash72",
        "i29_validation_hash72",
        "promoted_object_hash72",
        "canonical_root_hash72",
        "durability_witness_hash72",
        "persisted_inventory_hash72",
        "purge_validation_hash72",
        "purge_receipt_hash72",
        "purge_gate_root_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I45StateError("P218_I45_I31_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("validated_hash216")):
        raise Pass218I45StateError("P218_I45_I31_VALIDATED_HASH216_INVALID")
    if not _valid_hash216(value.get("purge_hash216")):
        raise Pass218I45StateError("P218_I45_I31_PURGE_HASH216_INVALID")
    if value["purge_hash216"] != (
        str(value["i30_promotion_hash72"])
        + str(value["purge_validation_hash72"])
        + str(value["purge_receipt_hash72"])
    ):
        raise Pass218I45StateError("P218_I45_I31_PURGE_HASH216_ORDER_INVALID")
    if value.get("purge_scope") != PASS218_I31_PURGE_SCOPE:
        raise Pass218I45StateError("P218_I45_I31_PURGE_SCOPE_INVALID")
    required_true = (
        "durable_nonverbatim_store_verified",
        "verbatim_purge_invoked",
        "purge_confirmation_verified",
        "purge_receipt_issued",
        "managed_buffers_absent_after",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I45StateError("P218_I45_I31_RECEIPT_INCOMPLETE")
    required_false = (
        "quarantined",
        "curriculum_advance_permitted",
        "closure_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "physical_memory_erasure_claimed",
        "external_source_storage_erasure_claimed",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I45StateError("P218_I45_I31_AUTHORITY_DRIFT")
    if int(value.get("managed_buffer_count_after", -1)) != 0:
        raise Pass218I45StateError("P218_I45_I31_MANAGED_BUFFER_COUNT_NONZERO")
    return value


def _verify_i45_proof(
    proof: Mapping[str, Any],
    receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value = _copy(dict(proof))
    if value.get("schema") != PASS218_I45_PROOF_SCHEMA:
        raise Pass218I45StateError("P218_I45_PROOF_SCHEMA_INVALID")
    if value.get("status") != PASS218_I45_PURGED_PENDING_I32_STATUS:
        raise Pass218I45StateError("P218_I45_PROOF_STATUS_INVALID")
    for field in (
        "i44_receipt_hash72",
        "i44_promotion_proof_hash72",
        "i30_promotion_receipt_hash72",
        "i30_promoted_object_hash72",
        "i30_canonical_root_hash72",
        "i31_purge_receipt_hash72",
        "i31_purge_validation_hash72",
        "i31_purge_gate_root_hash72",
        "manifest_bound_i31_verbatim_purge_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I45StateError("P218_I45_PROOF_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i31_purge_hash216")):
        raise Pass218I45StateError("P218_I45_PROOF_HASH216_INVALID")
    if not _valid_sha256(value.get("i30_generation_sha256")):
        raise Pass218I45StateError("P218_I45_PROOF_I30_SHA256_INVALID")
    required_true = (
        "i44_complete_atomic_promotion_verified",
        "i31_purge_receipt_committed",
        "i31_exactly_once_or_restart_adoption_verified",
        "restart_does_not_require_duplicate_i31_invocation",
        "i30_semantic_generation_unchanged_across_purge",
        "i30_canonical_root_unchanged_across_purge",
        "managed_buffers_absent_after",
        "durable_nonverbatim_store_verified",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I45StateError("P218_I45_PROOF_INCOMPLETE")
    required_false = (
        "i31_purge_request_persisted",
        "source_payload_persisted",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "physical_memory_erasure_claimed",
        "external_source_storage_erasure_claimed",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I45StateError("P218_I45_PROOF_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key != "manifest_bound_i31_verbatim_purge_hash72"}
    expected = hash72_digest({"domain": PASS218_I45_PROOF_SCHEMA}, body)
    if expected != value.get("manifest_bound_i31_verbatim_purge_hash72"):
        raise Pass218I45StateError("P218_I45_PROOF_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get("manifest_bound_i31_verbatim_purge_hash72"):
        raise Pass218I45StateError("P218_I45_PROOF_RECEIPT_MISMATCH")
    return value


def _verify_i45_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I45_RECEIPT_SCHEMA:
        raise Pass218I45StateError("P218_I45_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I45_COMPLETE_STATUS:
        raise Pass218I45StateError("P218_I45_RECEIPT_STATUS_INVALID")
    if value.get("purge_status") != PASS218_I45_PURGED_PENDING_I32_STATUS:
        raise Pass218I45StateError("P218_I45_RECEIPT_PURGE_STATUS_INVALID")
    for field in (
        "i44_receipt_hash72",
        "manifest_bound_i31_verbatim_purge_hash72",
        "i30_promotion_receipt_hash72",
        "i30_promoted_object_hash72",
        "i30_canonical_root_hash72",
        "i31_purge_receipt_hash72",
        "i31_purge_gate_root_hash72",
        "i45_validation_hash72",
        "i45_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I45StateError("P218_I45_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i45_hash216")):
        raise Pass218I45StateError("P218_I45_RECEIPT_HASH216_INVALID")
    if value["i45_hash216"] != (
        str(value["i44_receipt_hash72"])
        + str(value["i31_purge_receipt_hash72"])
        + str(value["i45_receipt_hash72"])
    ):
        raise Pass218I45StateError("P218_I45_HASH216_ORDER_INVALID")
    if not _valid_sha256(value.get("i30_generation_sha256")):
        raise Pass218I45StateError("P218_I45_RECEIPT_I30_SHA256_INVALID")
    required_true = (
        "i44_complete_atomic_promotion_verified",
        "i31_verbatim_purge_invoked",
        "i31_purge_receipt_committed",
        "i30_semantic_generation_unchanged_across_purge",
        "managed_buffers_absent_after",
        "restart_safe_exact_purge_adoption",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I45StateError("P218_I45_RECEIPT_INCOMPLETE")
    required_false = (
        "i31_purge_request_persisted",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "physical_memory_erasure_claimed",
        "external_source_storage_erasure_claimed",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I45StateError("P218_I45_RECEIPT_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key not in {"i45_receipt_hash72", "i45_hash216", "i45_hash216_semantics"}}
    expected = hash72_digest({"domain": PASS218_I45_RECEIPT_SCHEMA}, body)
    if expected != value.get("i45_receipt_hash72"):
        raise Pass218I45StateError("P218_I45_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I45PurgeStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.proof_root = self.root / "proofs"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I45_STATE_SCHEMA:
            raise Pass218I45StateError("P218_I45_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I45_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I45StateError("P218_I45_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        proof_path = self.root / str(state.get("active_proof_path", ""))
        if not receipt_path.is_file() or not proof_path.is_file():
            raise Pass218I45StateError("P218_I45_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i45_receipt(_load_json(receipt_path))
        proof = _verify_i45_proof(_load_json(proof_path), receipt)
        if receipt["i45_receipt_hash72"] != state.get("active_i45_receipt_hash72"):
            raise Pass218I45StateError("P218_I45_STATE_RECEIPT_MISMATCH")
        if proof["manifest_bound_i31_verbatim_purge_hash72"] != state.get("active_proof_hash72"):
            raise Pass218I45StateError("P218_I45_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i45_proof(_load_json(self.root / str(state["active_proof_path"])), receipt)

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i45_receipt(receipt)
        checked_proof = _verify_i45_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I45StateError("P218_I45_ACTIVE_BINDING_CONFLICT")
            return existing
        receipt_name = _path_safe_hash72_name(str(checked["i45_receipt_hash72"]))
        proof_name = _path_safe_hash72_name(str(checked_proof["manifest_bound_i31_verbatim_purge_hash72"]))
        receipt_path = self.receipt_root / f"{receipt_name}.json"
        proof_path = self.proof_root / f"{proof_name}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(proof_path, checked_proof)
        state_body = {
            "schema": PASS218_I45_STATE_SCHEMA,
            "version": PASS218_I45_VERSION,
            "status": PASS218_I45_COMPLETE_STATUS,
            "purge_status": PASS218_I45_PURGED_PENDING_I32_STATUS,
            "i44_receipt_hash72": checked["i44_receipt_hash72"],
            "i30_promotion_receipt_hash72": checked["i30_promotion_receipt_hash72"],
            "i31_purge_receipt_hash72": checked["i31_purge_receipt_hash72"],
            "i30_generation_sha256": checked["i30_generation_sha256"],
            "active_i45_receipt_hash72": checked["i45_receipt_hash72"],
            "active_proof_hash72": checked_proof["manifest_bound_i31_verbatim_purge_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_proof_path": proof_path.relative_to(self.root).as_posix(),
        }
        state = {**state_body, "state_root_hash72": hash72_digest({"domain": PASS218_I45_STATE_SCHEMA}, state_body)}
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I45StateError("P218_I45_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I45ManifestBoundI31VerbatimPurge:
    def __init__(
        self,
        *,
        lifecycle: Pass218I45LifecycleProtocol,
        i44_store: Pass218I45I44StoreProtocol,
        i31_purger: Pass218I45I31PurgerProtocol,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.lifecycle = lifecycle
        self.i44_store = i44_store
        self.i31_purger = i31_purger
        self.store = Pass218I45PurgeStore(state_root)
        self.i31_invocation_count = 0
        self.restart_adoption_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_i44(self) -> tuple[dict[str, Any], dict[str, Any]]:
        receipt = self.i44_store.active_record()
        proof = self.i44_store.active_proof()
        if not isinstance(receipt, Mapping) or not isinstance(proof, Mapping):
            raise Pass218I45BindingError("P218_I45_I44_COMPLETE_PROMOTION_REQUIRED")
        checked = _verify_i44_receipt(receipt)
        checked_proof = _verify_i44_proof(proof, checked)
        if checked.get("status") != PASS218_I44_COMPLETE_STATUS:
            raise Pass218I45BindingError("P218_I45_I44_COMPLETE_STATUS_REQUIRED")
        if checked.get("promotion_status") != PASS218_I44_PROMOTED_PENDING_I31_STATUS:
            raise Pass218I45BindingError("P218_I45_I44_PENDING_I31_REQUIRED")
        return checked, checked_proof

    def _current_i30(
        self,
        *,
        i44: Mapping[str, Any],
        i44_proof: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
        generation = self.i31_purger.i30_store.active_generation()
        if not isinstance(generation, Mapping):
            raise Pass218I45BindingError("P218_I45_I30_DURABLE_GENERATION_REQUIRED")
        i30_status = self.i31_purger.i30_store.status()
        receipt, promoted, digest = _verify_i30_generation(
            generation,
            i44=i44,
            i44_proof=i44_proof,
            i30_status=i30_status,
        )
        return _copy(dict(generation)), receipt, promoted, digest

    @staticmethod
    def _build(
        *,
        i44: Mapping[str, Any],
        i44_proof: Mapping[str, Any],
        i30_receipt: Mapping[str, Any],
        i30_generation_sha256: str,
        i31_receipt: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        proof_body = {
            "schema": PASS218_I45_PROOF_SCHEMA,
            "version": PASS218_I45_VERSION,
            "scope": PASS218_I45_SCOPE,
            "status": PASS218_I45_PURGED_PENDING_I32_STATUS,
            "i44_receipt_hash72": i44["i44_receipt_hash72"],
            "i44_promotion_proof_hash72": i44["manifest_bound_i30_atomic_promotion_hash72"],
            "i30_promotion_receipt_hash72": i30_receipt["promotion_receipt_hash72"],
            "i30_promoted_object_hash72": i30_receipt["promoted_object_hash72"],
            "i30_canonical_root_hash72": i30_receipt["target_root_after_hash72"],
            "i30_generation_sha256": i30_generation_sha256,
            "i31_purge_receipt_hash72": i31_receipt["purge_receipt_hash72"],
            "i31_purge_validation_hash72": i31_receipt["purge_validation_hash72"],
            "i31_purge_gate_root_hash72": i31_receipt["purge_gate_root_hash72"],
            "i31_purge_hash216": i31_receipt["purge_hash216"],
            "i31_purge_mode": i31_receipt["purge_mode"],
            "managed_buffer_count_before": int(i31_receipt["managed_buffer_count_before"]),
            "managed_buffer_count_after": int(i31_receipt["managed_buffer_count_after"]),
            "i44_complete_atomic_promotion_verified": True,
            "i31_purge_receipt_committed": True,
            "i31_exactly_once_or_restart_adoption_verified": True,
            "restart_does_not_require_duplicate_i31_invocation": True,
            "i30_semantic_generation_unchanged_across_purge": True,
            "i30_canonical_root_unchanged_across_purge": True,
            "managed_buffers_absent_after": True,
            "durable_nonverbatim_store_verified": True,
            "i31_purge_request_persisted": False,
            "source_payload_persisted": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "physical_memory_erasure_claimed": False,
            "external_source_storage_erasure_claimed": False,
            "authoritative_float_weights_created": False,
        }
        proof_hash72 = hash72_digest({"domain": PASS218_I45_PROOF_SCHEMA}, proof_body)
        proof = {**proof_body, "manifest_bound_i31_verbatim_purge_hash72": proof_hash72}
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I45-VERBATIM-PURGE-VALIDATION-V1"},
            {
                "i44_receipt_hash72": i44["i44_receipt_hash72"],
                "i30_generation_sha256": i30_generation_sha256,
                "i31_purge_receipt_hash72": i31_receipt["purge_receipt_hash72"],
                "i31_purge_gate_root_hash72": i31_receipt["purge_gate_root_hash72"],
                "managed_buffers_absent_after": True,
                "pending_i32": True,
            },
        )
        body = {
            "schema": PASS218_I45_RECEIPT_SCHEMA,
            "version": PASS218_I45_VERSION,
            "scope": PASS218_I45_SCOPE,
            "status": PASS218_I45_COMPLETE_STATUS,
            "purge_status": PASS218_I45_PURGED_PENDING_I32_STATUS,
            "i44_receipt_hash72": i44["i44_receipt_hash72"],
            "manifest_bound_i31_verbatim_purge_hash72": proof_hash72,
            "i30_promotion_receipt_hash72": i30_receipt["promotion_receipt_hash72"],
            "i30_promoted_object_hash72": i30_receipt["promoted_object_hash72"],
            "i30_canonical_root_hash72": i30_receipt["target_root_after_hash72"],
            "i30_generation_sha256": i30_generation_sha256,
            "i31_purge_receipt_hash72": i31_receipt["purge_receipt_hash72"],
            "i31_purge_gate_root_hash72": i31_receipt["purge_gate_root_hash72"],
            "i31_purge_mode": i31_receipt["purge_mode"],
            "managed_buffer_count_before": int(i31_receipt["managed_buffer_count_before"]),
            "managed_buffer_count_after": int(i31_receipt["managed_buffer_count_after"]),
            "i45_validation_hash72": validation_hash72,
            "i44_complete_atomic_promotion_verified": True,
            "i31_verbatim_purge_invoked": True,
            "i31_purge_receipt_committed": True,
            "i30_semantic_generation_unchanged_across_purge": True,
            "managed_buffers_absent_after": True,
            "restart_safe_exact_purge_adoption": True,
            "i31_purge_request_persisted": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "physical_memory_erasure_claimed": False,
            "external_source_storage_erasure_claimed": False,
            "authoritative_float_weights_created": False,
        }
        receipt_hash72 = hash72_digest({"domain": PASS218_I45_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i45_receipt_hash72": receipt_hash72,
            "i45_hash216": i44["i44_receipt_hash72"] + i31_receipt["purge_receipt_hash72"] + receipt_hash72,
            "i45_hash216_semantics": [
                "I44_MANIFEST_BOUND_ATOMIC_PROMOTION_RECEIPT",
                "I31_VERBATIM_PURGE_RECEIPT",
                "I45_MANIFEST_BOUND_VERBATIM_PURGE_RECEIPT",
            ],
        }
        return _verify_i45_proof(proof), _verify_i45_receipt(receipt)

    def purge(self) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i44, i44_proof = self._active_i44()
            generation_before, i30_receipt, _, generation_sha256_before = self._current_i30(
                i44=i44,
                i44_proof=i44_proof,
            )
            request = _derive_i31_request(i30_receipt)
            existing_i45 = self.store.active_record()
            active_i31 = self.i31_purger.store.active_record()

            if existing_i45 is not None:
                if existing_i45["i44_receipt_hash72"] != i44["i44_receipt_hash72"]:
                    raise Pass218I45StateError("P218_I45_ACTIVE_I44_CONFLICT")
                if existing_i45["i30_generation_sha256"] != generation_sha256_before:
                    raise Pass218I45StateError("P218_I45_ACTIVE_I30_GENERATION_CONFLICT")
                if not isinstance(active_i31, Mapping):
                    raise Pass218I45StateError("P218_I45_ACTIVE_I31_RECEIPT_MISSING")
                checked_i31 = _verify_i31_receipt(active_i31, i30_receipt=i30_receipt)
                if checked_i31["purge_receipt_hash72"] != existing_i45["i31_purge_receipt_hash72"]:
                    raise Pass218I45StateError("P218_I45_ACTIVE_I31_RECEIPT_CONFLICT")
                self.last_error_code = None
                return existing_i45

            if isinstance(active_i31, Mapping):
                i31_receipt = _verify_i31_receipt(active_i31, i30_receipt=i30_receipt)
                self.restart_adoption_count += 1
            else:
                i31_status_before = self.i31_purger.status()
                if bool(i31_status_before.get("purge_record_present")):
                    raise Pass218I45StateError("P218_I45_I31_NONEMPTY_WITHOUT_RECORD")
                purge_count_before = int(self.i31_purger.purge_count)
                returned = self.i31_purger.purge(request)
                self.i31_invocation_count += 1
                if int(self.i31_purger.purge_count) != purge_count_before + 1:
                    raise Pass218I45StateError("P218_I45_I31_SINGLE_INVOCATION_NOT_PROVEN")
                active_i31 = self.i31_purger.store.active_record()
                if not isinstance(active_i31, Mapping):
                    raise Pass218I45StateError("P218_I45_I31_DURABLE_RECEIPT_MISSING")
                i31_receipt = _verify_i31_receipt(active_i31, i30_receipt=i30_receipt)
                if _copy(returned) != i31_receipt:
                    raise Pass218I45StateError("P218_I45_I31_RETURNED_DURABLE_RECEIPT_MISMATCH")

            generation_after, i30_receipt_after, _, generation_sha256_after = self._current_i30(
                i44=i44,
                i44_proof=i44_proof,
            )
            if generation_before != generation_after or generation_sha256_before != generation_sha256_after:
                raise Pass218I45StateError("P218_I45_I30_SEMANTIC_GENERATION_CHANGED_DURING_PURGE")
            if i30_receipt_after["target_root_after_hash72"] != i30_receipt["target_root_after_hash72"]:
                raise Pass218I45StateError("P218_I45_I30_CANONICAL_ROOT_CHANGED_DURING_PURGE")
            if int(self.i31_purger.managed_buffers.count()) != 0:
                raise Pass218I45StateError("P218_I45_MANAGED_BUFFERS_REMAIN_AFTER_PURGE")

            proof, receipt = self._build(
                i44=i44,
                i44_proof=i44_proof,
                i30_receipt=i30_receipt,
                i30_generation_sha256=generation_sha256_before,
                i31_receipt=i31_receipt,
            )
            persisted = self.store.commit(receipt, proof)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i44_ready = False
        active_i44_receipt_hash72: str | None = None
        try:
            i44, _ = self._active_i44()
            i44_ready = True
            active_i44_receipt_hash72 = str(i44["i44_receipt_hash72"])
        except Exception:
            pass
        i31 = self.i31_purger.status()
        return {
            "schema": PASS218_I45_STATUS_SCHEMA,
            "version": PASS218_I45_VERSION,
            "status": PASS218_I45_COMPLETE_STATUS if active is not None else PASS218_I45_PENDING_STATUS,
            "purge_status": None if active is None else PASS218_I45_PURGED_PENDING_I32_STATUS,
            "predecessor_i44_promotion_ready": i44_ready,
            "active_i44_receipt_hash72": active_i44_receipt_hash72,
            "active_i45_receipt_hash72": None if active is None else active["i45_receipt_hash72"],
            "active_i31_purge_receipt_hash72": None if active is None else active["i31_purge_receipt_hash72"],
            "i30_generation_sha256": None if active is None else active["i30_generation_sha256"],
            "i31_invocation_count_current_process": self.i31_invocation_count,
            "restart_adoption_count_current_process": self.restart_adoption_count,
            "i31_purge_receipt_present": bool(i31.get("purge_receipt_issued")),
            "i31_quarantined": bool(i31.get("quarantined")),
            "i31_verbatim_purge_invoked": active is not None,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "vm81_authorization_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "physical_memory_erasure_claimed": False,
            "external_source_storage_erasure_claimed": False,
            "authoritative_float_weights_created": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I45_COMPLETE_STATUS",
    "PASS218_I45_PENDING_STATUS",
    "PASS218_I45_PROOF_SCHEMA",
    "PASS218_I45_PURGED_PENDING_I32_STATUS",
    "PASS218_I45_RECEIPT_SCHEMA",
    "PASS218_I45_SCOPE",
    "PASS218_I45_STATE_SCHEMA",
    "PASS218_I45_STATUS_SCHEMA",
    "PASS218_I45_VERSION",
    "Pass218I45BindingError",
    "Pass218I45ManifestBoundI31VerbatimPurge",
    "Pass218I45PurgeError",
    "Pass218I45PurgeStore",
    "Pass218I45StateError",
]
