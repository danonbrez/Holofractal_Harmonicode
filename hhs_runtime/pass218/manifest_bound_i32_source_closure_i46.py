"""Pass 218 Iteration 46 manifest-bound one-time I32 source closure.

I46 consumes only the exact durable I45/I31 purge state. It walks the already
frozen manifest/semantic equality chain back through I44/I43/I42 to the exact
I34 nonverbatim source ingress receipt, derives the frozen-I32 closure request
internally, invokes frozen I32 exactly once when its closure store is empty, or
restart-adopts the exact already committed closure without a duplicate call.

The frozen I30 semantic generation and canonical root are verified byte-exact
before and after closure. I46 persists only nonverbatim identities, proof, and
receipt material. It does not persist an I32 request or source payload, invoke
I33, advance curriculum/stage, mutate VM81, perform canonical learning, promote
truth, mint action authority, activate a model, retain verbatim source content,
or create authoritative floating-point state.
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
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    PASS218_I34_READY_STATUS,
    PASS218_I34_RECEIPT_SCHEMA,
    _verify_receipt as _verify_i34_receipt,
)
from hhs_runtime.pass218.manifest_semantic_cross_lineage_equality_i42 import (
    PASS218_I42_COMPLETE_STATUS,
    _verify_i42_proof,
    _verify_i42_receipt,
)
from hhs_runtime.pass218.manifest_bound_i30_promotion_request_authorization_i43 import (
    PASS218_I43_COMPLETE_STATUS,
    _verify_i43_receipt,
)
from hhs_runtime.pass218.manifest_bound_i30_atomic_promotion_i44 import (
    PASS218_I44_COMPLETE_STATUS,
    _verify_i44_receipt,
)
from hhs_runtime.pass218.manifest_bound_i31_verbatim_purge_i45 import (
    PASS218_I45_COMPLETE_STATUS,
    PASS218_I45_PURGED_PENDING_I32_STATUS,
    _verify_i45_proof,
    _verify_i45_receipt,
)
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSED_STATUS,
    PASS218_I32_CLOSURE_RECEIPT_SCHEMA,
    PASS218_I32_CLOSURE_SCOPE,
    Pass218I32ClosureRequest,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGED_STATUS,
    PASS218_I31_PURGE_RECEIPT_SCHEMA,
)

PASS218_I46_VERSION = "HHS-P218-I46-MANIFEST-BOUND-I32-SOURCE-CLOSURE-V1"
PASS218_I46_SCOPE = "PASS218_MANIFEST_BOUND_I32_SOURCE_CLOSURE"
PASS218_I46_PROOF_SCHEMA = "HHS-P218-I46-MANIFEST-BOUND-I32-SOURCE-CLOSURE-PROOF-V1"
PASS218_I46_RECEIPT_SCHEMA = "HHS-P218-I46-MANIFEST-BOUND-I32-SOURCE-CLOSURE-RECEIPT-V1"
PASS218_I46_STATE_SCHEMA = "HHS-P218-I46-MANIFEST-BOUND-I32-SOURCE-CLOSURE-STATE-V1"
PASS218_I46_STATUS_SCHEMA = "HHS-P218-I46-MANIFEST-BOUND-I32-SOURCE-CLOSURE-STATUS-V1"
PASS218_I46_COMPLETE_STATUS = "MANIFEST_BOUND_I32_SOURCE_CLOSURE_COMPLETE"
PASS218_I46_PENDING_STATUS = "MANIFEST_BOUND_I32_SOURCE_CLOSURE_PENDING"
PASS218_I46_CLOSED_PENDING_I33_STATUS = PASS218_I32_CLOSED_STATUS

_SHARED_IDENTITY_FIELDS = (
    "curriculum_identity_hash72",
    "curriculum_position",
    "source_id",
    "source_sha256",
    "source_authority",
    "rights_class",
)


class Pass218I46ClosureError(RuntimeError):
    pass


class Pass218I46BindingError(Pass218I46ClosureError):
    pass


class Pass218I46StateError(Pass218I46ClosureError):
    pass


class Pass218I46LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I46RecordStoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...


class Pass218I46ProofStoreProtocol(Pass218I46RecordStoreProtocol, Protocol):
    def active_proof(self) -> dict[str, Any] | None: ...


class Pass218I46I30StoreProtocol(Protocol):
    def active_generation(self) -> dict[str, Any] | None: ...
    def status(self) -> dict[str, Any]: ...


class Pass218I46I32CloserProtocol(Protocol):
    close_count: int
    store: Any
    i31_store: Any
    def close(self, request: Pass218I32ClosureRequest) -> dict[str, Any]: ...
    def status(self) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I46BindingError("P218_I46_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        raise Pass218I46StateError("P218_I46_PATH_HASH72_INVALID")
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
        raise Pass218I46StateError("P218_I46_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I46StateError("P218_I46_STATE_OBJECT_REQUIRED")
    return value


def _verify_i30_generation(
    generation: Mapping[str, Any],
    *,
    i45: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    value = _copy(dict(generation))
    receipt_raw = value.get("promotion_receipt")
    promoted_raw = value.get("promoted_object")
    if not isinstance(receipt_raw, Mapping) or not isinstance(promoted_raw, Mapping):
        raise Pass218I46BindingError("P218_I46_I30_GENERATION_CONTENT_INVALID")
    receipt = _copy(dict(receipt_raw))
    promoted = _copy(dict(promoted_raw))
    if receipt.get("schema") != PASS218_I30_PROMOTION_RECEIPT_SCHEMA:
        raise Pass218I46BindingError("P218_I46_I30_RECEIPT_SCHEMA_INVALID")
    if promoted.get("schema") != PASS218_I30_PROMOTED_OBJECT_SCHEMA:
        raise Pass218I46BindingError("P218_I46_I30_PROMOTED_OBJECT_SCHEMA_INVALID")
    if receipt.get("promotion_status") != PASS218_I30_PENDING_PURGE_STATUS:
        raise Pass218I46BindingError("P218_I46_I30_PROMOTION_STATUS_INVALID")
    expected = (
        ("promotion_receipt_hash72", "i30_promotion_receipt_hash72"),
        ("promoted_object_hash72", "i30_promoted_object_hash72"),
        ("target_root_after_hash72", "i30_canonical_root_hash72"),
    )
    for receipt_field, i45_field in expected:
        if receipt.get(receipt_field) != i45.get(i45_field):
            raise Pass218I46BindingError("P218_I46_I30_I45_MISMATCH:" + receipt_field)
    if promoted.get("promoted_object_hash72") != receipt.get("promoted_object_hash72"):
        raise Pass218I46BindingError("P218_I46_PROMOTED_OBJECT_HASH_MISMATCH")
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
            raise Pass218I46BindingError("P218_I46_PROMOTED_AUTHORITY_DRIFT:" + field)
    digest = sha256(_canonical_bytes(value)).hexdigest()
    if digest != i45.get("i30_generation_sha256"):
        raise Pass218I46BindingError("P218_I46_I30_GENERATION_I45_MISMATCH")
    return receipt, promoted, digest


def _verify_i31_receipt(
    receipt: Mapping[str, Any],
    *,
    i45: Mapping[str, Any],
    i45_proof: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I31_PURGE_RECEIPT_SCHEMA:
        raise Pass218I46BindingError("P218_I46_I31_RECEIPT_SCHEMA_INVALID")
    if value.get("purge_status") != PASS218_I31_PURGED_STATUS:
        raise Pass218I46BindingError("P218_I46_I31_PURGE_STATUS_INVALID")
    expected = (
        ("purge_receipt_hash72", i45.get("i31_purge_receipt_hash72")),
        ("purge_receipt_hash72", i45_proof.get("i31_purge_receipt_hash72")),
        ("purge_validation_hash72", i45_proof.get("i31_purge_validation_hash72")),
        ("purge_gate_root_hash72", i45.get("i31_purge_gate_root_hash72")),
        ("purge_gate_root_hash72", i45_proof.get("i31_purge_gate_root_hash72")),
        ("purge_hash216", i45_proof.get("i31_purge_hash216")),
        ("i30_promotion_receipt_hash72", i45.get("i30_promotion_receipt_hash72")),
        ("promoted_object_hash72", i45.get("i30_promoted_object_hash72")),
        ("canonical_root_hash72", i45.get("i30_canonical_root_hash72")),
    )
    for field, expected_value in expected:
        if value.get(field) != expected_value:
            raise Pass218I46BindingError("P218_I46_I31_I45_MISMATCH:" + field)
    if not _valid_hash216(value.get("purge_hash216")):
        raise Pass218I46BindingError("P218_I46_I31_PURGE_HASH216_INVALID")
    required_true = (
        "durable_nonverbatim_store_verified",
        "verbatim_purge_invoked",
        "purge_confirmation_verified",
        "purge_receipt_issued",
        "managed_buffers_absent_after",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I46BindingError("P218_I46_I31_PROOF_INCOMPLETE")
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
        raise Pass218I46BindingError("P218_I46_I31_AUTHORITY_DRIFT")
    return value


def _derive_i32_request(
    *,
    i31: Mapping[str, Any],
    i34: Mapping[str, Any],
) -> Pass218I32ClosureRequest:
    return Pass218I32ClosureRequest(
        expected_i31_purge_receipt_hash72=str(i31["purge_receipt_hash72"]),
        expected_i31_purge_validation_hash72=str(i31["purge_validation_hash72"]),
        expected_i31_purge_gate_root_hash72=str(i31["purge_gate_root_hash72"]),
        expected_i31_purge_hash216=str(i31["purge_hash216"]),
        expected_i30_promotion_receipt_hash72=str(i31["i30_promotion_receipt_hash72"]),
        expected_promoted_object_hash72=str(i31["promoted_object_hash72"]),
        expected_canonical_root_hash72=str(i31["canonical_root_hash72"]),
        source_id=str(i34["source_id"]),
        source_sha256=str(i34["source_sha256"]),
        source_authority=str(i34["source_authority"]),
        rights_class=str(i34["rights_class"]),
        curriculum_identity_hash72=str(i34["curriculum_identity_hash72"]),
        curriculum_position=int(i34["curriculum_position"]),
        source_stage=int(i34["source_stage"]),
        previous_closure_hash72=(
            None if i34.get("previous_closure_hash72") is None
            else str(i34["previous_closure_hash72"])
        ),
        closure_scope=PASS218_I32_CLOSURE_SCOPE,
    ).validated()


def _verify_i32_receipt(
    receipt: Mapping[str, Any],
    *,
    request: Pass218I32ClosureRequest,
    i31: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I32_CLOSURE_RECEIPT_SCHEMA:
        raise Pass218I46StateError("P218_I46_I32_RECEIPT_SCHEMA_INVALID")
    if value.get("closure_status") != PASS218_I32_CLOSED_STATUS:
        raise Pass218I46StateError("P218_I46_I32_CLOSURE_STATUS_INVALID")
    expected = {
        "i31_purge_receipt_hash72": i31["purge_receipt_hash72"],
        "i31_purge_validation_hash72": i31["purge_validation_hash72"],
        "i31_purge_gate_root_hash72": i31["purge_gate_root_hash72"],
        "i31_purge_hash216": i31["purge_hash216"],
        "i30_promotion_receipt_hash72": i31["i30_promotion_receipt_hash72"],
        "promoted_object_hash72": i31["promoted_object_hash72"],
        "canonical_root_hash72": i31["canonical_root_hash72"],
        "source_id": request.source_id,
        "source_sha256": request.source_sha256,
        "source_authority": request.source_authority,
        "rights_class": request.rights_class,
        "curriculum_identity_hash72": request.curriculum_identity_hash72,
        "curriculum_position": request.curriculum_position,
        "source_stage": request.source_stage,
        "previous_closure_hash72": request.previous_closure_hash72,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise Pass218I46BindingError("P218_I46_I32_BINDING_MISMATCH:" + field)
    required_true = (
        "purge_confirmation_verified",
        "durable_nonverbatim_store_verified",
        "source_binding_requires_curriculum_match_before_advance",
        "closure_invoked",
        "source_closed",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I46StateError("P218_I46_I32_PROOF_INCOMPLETE")
    required_false = (
        "curriculum_advance_permitted",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
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
        raise Pass218I46StateError("P218_I46_I32_AUTHORITY_DRIFT")
    closure_body = {
        key: item
        for key, item in value.items()
        if key not in {
            "source_closure_hash72",
            "closure_hash216",
            "closure_hash216_semantics",
            "closure_chain_root_hash72",
        }
    }
    expected_closure = hash72_digest(
        {"domain": "HHS-P218-I32-SOURCE-CLOSURE-RECEIPT-V1"}, closure_body
    )
    if expected_closure != value.get("source_closure_hash72"):
        raise Pass218I46StateError("P218_I46_I32_SOURCE_CLOSURE_HASH_MISMATCH")
    expected_hash216 = (
        str(i31["purge_receipt_hash72"])
        + str(value["closure_validation_hash72"])
        + str(value["source_closure_hash72"])
    )
    if expected_hash216 != value.get("closure_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I46StateError("P218_I46_I32_CLOSURE_HASH216_INVALID")
    expected_chain_root = hash72_digest(
        {"domain": "HHS-P218-I32-CLOSURE-CHAIN-ROOT-V1"},
        {
            "previous_closure_hash72": request.previous_closure_hash72,
            "source_closure_hash72": value["source_closure_hash72"],
            "canonical_root_hash72": i31["canonical_root_hash72"],
            "curriculum_identity_hash72": request.curriculum_identity_hash72,
            "curriculum_position": request.curriculum_position,
            "source_stage": request.source_stage,
        },
    )
    if expected_chain_root != value.get("closure_chain_root_hash72"):
        raise Pass218I46StateError("P218_I46_I32_CHAIN_ROOT_MISMATCH")
    return value


def _verify_i46_proof(
    proof: Mapping[str, Any],
    receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value = _copy(dict(proof))
    if value.get("schema") != PASS218_I46_PROOF_SCHEMA:
        raise Pass218I46StateError("P218_I46_PROOF_SCHEMA_INVALID")
    if value.get("status") != PASS218_I46_CLOSED_PENDING_I33_STATUS:
        raise Pass218I46StateError("P218_I46_PROOF_STATUS_INVALID")
    for field in (
        "i45_receipt_hash72",
        "i31_purge_receipt_hash72",
        "i42_receipt_hash72",
        "i34_ingress_receipt_hash72",
        "i30_promotion_receipt_hash72",
        "i30_promoted_object_hash72",
        "i30_canonical_root_hash72",
        "i32_source_closure_hash72",
        "i32_closure_chain_root_hash72",
        "manifest_bound_i32_source_closure_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I46StateError("P218_I46_PROOF_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i32_closure_hash216")):
        raise Pass218I46StateError("P218_I46_PROOF_HASH216_INVALID")
    if not _valid_sha256(value.get("i30_generation_sha256")):
        raise Pass218I46StateError("P218_I46_PROOF_I30_SHA256_INVALID")
    required_true = (
        "i45_complete_purge_verified",
        "manifest_cross_lineage_identity_verified",
        "i34_nonverbatim_source_binding_verified",
        "i32_closure_receipt_committed",
        "i32_exactly_once_or_restart_adoption_verified",
        "restart_does_not_require_duplicate_i32_invocation",
        "i30_semantic_generation_unchanged_across_closure",
        "i30_canonical_root_unchanged_across_closure",
        "nonverbatim_source_transaction_durably_closed",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I46StateError("P218_I46_PROOF_INCOMPLETE")
    required_false = (
        "i32_closure_request_persisted",
        "source_payload_persisted",
        "pass218_i33_curriculum_advance_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
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
        raise Pass218I46StateError("P218_I46_PROOF_AUTHORITY_DRIFT")
    body = {
        key: item
        for key, item in value.items()
        if key != "manifest_bound_i32_source_closure_hash72"
    }
    expected = hash72_digest({"domain": PASS218_I46_PROOF_SCHEMA}, body)
    if expected != value.get("manifest_bound_i32_source_closure_hash72"):
        raise Pass218I46StateError("P218_I46_PROOF_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get("manifest_bound_i32_source_closure_hash72"):
        raise Pass218I46StateError("P218_I46_PROOF_RECEIPT_MISMATCH")
    return value


def _verify_i46_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I46_RECEIPT_SCHEMA:
        raise Pass218I46StateError("P218_I46_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I46_COMPLETE_STATUS:
        raise Pass218I46StateError("P218_I46_RECEIPT_STATUS_INVALID")
    if value.get("closure_status") != PASS218_I46_CLOSED_PENDING_I33_STATUS:
        raise Pass218I46StateError("P218_I46_RECEIPT_CLOSURE_STATUS_INVALID")
    for field in (
        "i45_receipt_hash72",
        "i31_purge_receipt_hash72",
        "i34_ingress_receipt_hash72",
        "i32_source_closure_hash72",
        "i32_closure_chain_root_hash72",
        "manifest_bound_i32_source_closure_hash72",
        "i46_validation_hash72",
        "i46_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I46StateError("P218_I46_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i46_hash216")):
        raise Pass218I46StateError("P218_I46_RECEIPT_HASH216_INVALID")
    if value["i46_hash216"] != (
        str(value["i45_receipt_hash72"])
        + str(value["i32_source_closure_hash72"])
        + str(value["i46_receipt_hash72"])
    ):
        raise Pass218I46StateError("P218_I46_HASH216_ORDER_INVALID")
    if not _valid_sha256(value.get("i30_generation_sha256")):
        raise Pass218I46StateError("P218_I46_RECEIPT_I30_SHA256_INVALID")
    required_true = (
        "i45_complete_purge_verified",
        "manifest_cross_lineage_identity_verified",
        "i32_source_closure_invoked",
        "i32_closure_receipt_committed",
        "i30_semantic_generation_unchanged_across_closure",
        "nonverbatim_source_transaction_durably_closed",
        "restart_safe_exact_closure_adoption",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I46StateError("P218_I46_RECEIPT_INCOMPLETE")
    required_false = (
        "i32_closure_request_persisted",
        "pass218_i33_curriculum_advance_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
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
        raise Pass218I46StateError("P218_I46_RECEIPT_AUTHORITY_DRIFT")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i46_receipt_hash72", "i46_hash216", "i46_hash216_semantics"}
    }
    expected = hash72_digest({"domain": PASS218_I46_RECEIPT_SCHEMA}, body)
    if expected != value.get("i46_receipt_hash72"):
        raise Pass218I46StateError("P218_I46_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I46ClosureStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.proof_root = self.root / "proofs"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I46_STATE_SCHEMA:
            raise Pass218I46StateError("P218_I46_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I46_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I46StateError("P218_I46_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        proof_path = self.root / str(state.get("active_proof_path", ""))
        if not receipt_path.is_file() or not proof_path.is_file():
            raise Pass218I46StateError("P218_I46_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i46_receipt(_load_json(receipt_path))
        proof = _verify_i46_proof(_load_json(proof_path), receipt)
        if receipt["i46_receipt_hash72"] != state.get("active_i46_receipt_hash72"):
            raise Pass218I46StateError("P218_I46_STATE_RECEIPT_MISMATCH")
        if proof["manifest_bound_i32_source_closure_hash72"] != state.get("active_proof_hash72"):
            raise Pass218I46StateError("P218_I46_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i46_proof(
            _load_json(self.root / str(state["active_proof_path"])), receipt
        )

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i46_receipt(receipt)
        checked_proof = _verify_i46_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I46StateError("P218_I46_ACTIVE_BINDING_CONFLICT")
            return existing
        receipt_name = _path_safe_hash72_name(str(checked["i46_receipt_hash72"]))
        proof_name = _path_safe_hash72_name(
            str(checked_proof["manifest_bound_i32_source_closure_hash72"])
        )
        receipt_path = self.receipt_root / f"{receipt_name}.json"
        proof_path = self.proof_root / f"{proof_name}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(proof_path, checked_proof)
        state_body = {
            "schema": PASS218_I46_STATE_SCHEMA,
            "version": PASS218_I46_VERSION,
            "status": PASS218_I46_COMPLETE_STATUS,
            "closure_status": PASS218_I46_CLOSED_PENDING_I33_STATUS,
            "i45_receipt_hash72": checked["i45_receipt_hash72"],
            "i31_purge_receipt_hash72": checked["i31_purge_receipt_hash72"],
            "i34_ingress_receipt_hash72": checked["i34_ingress_receipt_hash72"],
            "i32_source_closure_hash72": checked["i32_source_closure_hash72"],
            "i30_generation_sha256": checked["i30_generation_sha256"],
            "active_i46_receipt_hash72": checked["i46_receipt_hash72"],
            "active_proof_hash72": checked_proof["manifest_bound_i32_source_closure_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_proof_path": proof_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest({"domain": PASS218_I46_STATE_SCHEMA}, state_body),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I46StateError("P218_I46_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I46ManifestBoundI32SourceClosure:
    def __init__(
        self,
        *,
        lifecycle: Pass218I46LifecycleProtocol,
        i45_store: Pass218I46ProofStoreProtocol,
        i44_store: Pass218I46RecordStoreProtocol,
        i43_store: Pass218I46RecordStoreProtocol,
        i42_store: Pass218I46ProofStoreProtocol,
        i34_store: Pass218I46RecordStoreProtocol,
        i30_store: Pass218I46I30StoreProtocol,
        i32_closer: Pass218I46I32CloserProtocol,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.lifecycle = lifecycle
        self.i45_store = i45_store
        self.i44_store = i44_store
        self.i43_store = i43_store
        self.i42_store = i42_store
        self.i34_store = i34_store
        self.i30_store = i30_store
        self.i32_closer = i32_closer
        self.store = Pass218I46ClosureStore(state_root)
        self.i32_invocation_count = 0
        self.restart_adoption_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_chain(
        self,
    ) -> tuple[
        dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any],
        dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
    ]:
        i45_raw = self.i45_store.active_record()
        i45_proof_raw = self.i45_store.active_proof()
        if not isinstance(i45_raw, Mapping) or not isinstance(i45_proof_raw, Mapping):
            raise Pass218I46BindingError("P218_I46_I45_COMPLETE_PURGE_REQUIRED")
        i45 = _verify_i45_receipt(i45_raw)
        i45_proof = _verify_i45_proof(i45_proof_raw, i45)
        if i45.get("status") != PASS218_I45_COMPLETE_STATUS:
            raise Pass218I46BindingError("P218_I46_I45_COMPLETE_STATUS_REQUIRED")
        if i45.get("purge_status") != PASS218_I45_PURGED_PENDING_I32_STATUS:
            raise Pass218I46BindingError("P218_I46_I45_PENDING_I32_REQUIRED")

        i44_raw = self.i44_store.active_record()
        if not isinstance(i44_raw, Mapping):
            raise Pass218I46BindingError("P218_I46_I44_RECEIPT_REQUIRED")
        i44 = _verify_i44_receipt(i44_raw)
        if i44.get("status") != PASS218_I44_COMPLETE_STATUS:
            raise Pass218I46BindingError("P218_I46_I44_COMPLETE_STATUS_REQUIRED")
        if i44.get("i44_receipt_hash72") != i45.get("i44_receipt_hash72"):
            raise Pass218I46BindingError("P218_I46_I44_I45_CHAIN_MISMATCH")

        i43_raw = self.i43_store.active_record()
        if not isinstance(i43_raw, Mapping):
            raise Pass218I46BindingError("P218_I46_I43_RECEIPT_REQUIRED")
        i43 = _verify_i43_receipt(i43_raw)
        if i43.get("status") != PASS218_I43_COMPLETE_STATUS:
            raise Pass218I46BindingError("P218_I46_I43_COMPLETE_STATUS_REQUIRED")
        if i43.get("i43_receipt_hash72") != i44.get("i43_receipt_hash72"):
            raise Pass218I46BindingError("P218_I46_I43_I44_CHAIN_MISMATCH")

        i42_raw = self.i42_store.active_record()
        i42_proof_raw = self.i42_store.active_proof()
        if not isinstance(i42_raw, Mapping) or not isinstance(i42_proof_raw, Mapping):
            raise Pass218I46BindingError("P218_I46_I42_EQUALITY_PROOF_REQUIRED")
        i42 = _verify_i42_receipt(i42_raw)
        i42_proof = _verify_i42_proof(i42_proof_raw, i42)
        if i42.get("status") != PASS218_I42_COMPLETE_STATUS:
            raise Pass218I46BindingError("P218_I46_I42_COMPLETE_STATUS_REQUIRED")
        if i42.get("i42_receipt_hash72") != i43.get("i42_receipt_hash72"):
            raise Pass218I46BindingError("P218_I46_I42_I43_CHAIN_MISMATCH")

        i34_raw = self.i34_store.active_record()
        if not isinstance(i34_raw, Mapping):
            raise Pass218I46BindingError("P218_I46_I34_SOURCE_BINDING_REQUIRED")
        i34 = _verify_i34_receipt(i34_raw)
        if i34.get("schema") != PASS218_I34_RECEIPT_SCHEMA:
            raise Pass218I46BindingError("P218_I46_I34_RECEIPT_SCHEMA_INVALID")
        if i34.get("binding_status") != PASS218_I34_READY_STATUS:
            raise Pass218I46BindingError("P218_I46_I34_SOURCE_NOT_READY")
        shared = i42_proof.get("shared_identity")
        if not isinstance(shared, Mapping):
            raise Pass218I46BindingError("P218_I46_I42_SHARED_IDENTITY_REQUIRED")
        for field in _SHARED_IDENTITY_FIELDS:
            if shared.get(field) != i34.get(field):
                raise Pass218I46BindingError("P218_I46_I34_I42_IDENTITY_MISMATCH:" + field)
        return i45, i45_proof, i44, i43, i42, i42_proof, i34, _copy(dict(shared))

    def _current_i30(self, *, i45: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
        generation = self.i30_store.active_generation()
        if not isinstance(generation, Mapping):
            raise Pass218I46BindingError("P218_I46_I30_DURABLE_GENERATION_REQUIRED")
        status = self.i30_store.status()
        receipt, _, digest = _verify_i30_generation(generation, i45=i45)
        if status.get("promotion_present") is not True:
            raise Pass218I46BindingError("P218_I46_I30_STATUS_PROMOTION_REQUIRED")
        if status.get("canonical_root_hash72") != receipt["target_root_after_hash72"]:
            raise Pass218I46BindingError("P218_I46_I30_STATUS_ROOT_MISMATCH")
        return _copy(dict(generation)), digest

    @staticmethod
    def _build(
        *,
        i45: Mapping[str, Any],
        i42: Mapping[str, Any],
        i34: Mapping[str, Any],
        i31: Mapping[str, Any],
        i32: Mapping[str, Any],
        i30_generation_sha256: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        proof_body = {
            "schema": PASS218_I46_PROOF_SCHEMA,
            "version": PASS218_I46_VERSION,
            "scope": PASS218_I46_SCOPE,
            "status": PASS218_I46_CLOSED_PENDING_I33_STATUS,
            "i45_receipt_hash72": i45["i45_receipt_hash72"],
            "i31_purge_receipt_hash72": i31["purge_receipt_hash72"],
            "i42_receipt_hash72": i42["i42_receipt_hash72"],
            "i34_ingress_receipt_hash72": i34["ingress_receipt_hash72"],
            "curriculum_identity_hash72": i34["curriculum_identity_hash72"],
            "curriculum_position": i34["curriculum_position"],
            "source_id_hash72": i32["source_id_hash72"],
            "source_sha256": i34["source_sha256"],
            "source_stage": i34["source_stage"],
            "previous_closure_hash72": i34["previous_closure_hash72"],
            "i30_promotion_receipt_hash72": i45["i30_promotion_receipt_hash72"],
            "i30_promoted_object_hash72": i45["i30_promoted_object_hash72"],
            "i30_canonical_root_hash72": i45["i30_canonical_root_hash72"],
            "i30_generation_sha256": i30_generation_sha256,
            "i32_source_closure_hash72": i32["source_closure_hash72"],
            "i32_closure_chain_root_hash72": i32["closure_chain_root_hash72"],
            "i32_closure_hash216": i32["closure_hash216"],
            "i45_complete_purge_verified": True,
            "manifest_cross_lineage_identity_verified": True,
            "i34_nonverbatim_source_binding_verified": True,
            "i32_closure_receipt_committed": True,
            "i32_exactly_once_or_restart_adoption_verified": True,
            "restart_does_not_require_duplicate_i32_invocation": True,
            "i30_semantic_generation_unchanged_across_closure": True,
            "i30_canonical_root_unchanged_across_closure": True,
            "nonverbatim_source_transaction_durably_closed": True,
            "i32_closure_request_persisted": False,
            "source_payload_persisted": False,
            "pass218_i33_curriculum_advance_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
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
        proof_hash72 = hash72_digest({"domain": PASS218_I46_PROOF_SCHEMA}, proof_body)
        proof = {**proof_body, "manifest_bound_i32_source_closure_hash72": proof_hash72}
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I46-SOURCE-CLOSURE-VALIDATION-V1"},
            {
                "i45_receipt_hash72": i45["i45_receipt_hash72"],
                "i31_purge_receipt_hash72": i31["purge_receipt_hash72"],
                "i34_ingress_receipt_hash72": i34["ingress_receipt_hash72"],
                "i32_source_closure_hash72": i32["source_closure_hash72"],
                "i30_generation_sha256": i30_generation_sha256,
                "pending_i33": True,
            },
        )
        body = {
            "schema": PASS218_I46_RECEIPT_SCHEMA,
            "version": PASS218_I46_VERSION,
            "scope": PASS218_I46_SCOPE,
            "status": PASS218_I46_COMPLETE_STATUS,
            "closure_status": PASS218_I46_CLOSED_PENDING_I33_STATUS,
            "i45_receipt_hash72": i45["i45_receipt_hash72"],
            "i31_purge_receipt_hash72": i31["purge_receipt_hash72"],
            "i34_ingress_receipt_hash72": i34["ingress_receipt_hash72"],
            "curriculum_identity_hash72": i34["curriculum_identity_hash72"],
            "curriculum_position": i34["curriculum_position"],
            "source_id": i34["source_id"],
            "source_sha256": i34["source_sha256"],
            "source_stage": i34["source_stage"],
            "previous_closure_hash72": i34["previous_closure_hash72"],
            "i30_generation_sha256": i30_generation_sha256,
            "i32_source_closure_hash72": i32["source_closure_hash72"],
            "i32_closure_chain_root_hash72": i32["closure_chain_root_hash72"],
            "manifest_bound_i32_source_closure_hash72": proof_hash72,
            "i46_validation_hash72": validation_hash72,
            "i45_complete_purge_verified": True,
            "manifest_cross_lineage_identity_verified": True,
            "i32_source_closure_invoked": True,
            "i32_closure_receipt_committed": True,
            "i30_semantic_generation_unchanged_across_closure": True,
            "nonverbatim_source_transaction_durably_closed": True,
            "restart_safe_exact_closure_adoption": True,
            "i32_closure_request_persisted": False,
            "pass218_i33_curriculum_advance_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
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
        receipt_hash72 = hash72_digest({"domain": PASS218_I46_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i46_receipt_hash72": receipt_hash72,
            "i46_hash216": i45["i45_receipt_hash72"] + i32["source_closure_hash72"] + receipt_hash72,
            "i46_hash216_semantics": [
                "I45_MANIFEST_BOUND_VERBATIM_PURGE_RECEIPT",
                "I32_SOURCE_CLOSURE_RECEIPT",
                "I46_MANIFEST_BOUND_SOURCE_CLOSURE_RECEIPT",
            ],
        }
        return _verify_i46_proof(proof), _verify_i46_receipt(receipt)

    def close(self) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i45, i45_proof, _, _, i42, _, i34, _ = self._active_chain()
            generation_before, generation_sha256_before = self._current_i30(i45=i45)
            i31_raw = self.i32_closer.i31_store.active_record()
            if not isinstance(i31_raw, Mapping):
                raise Pass218I46BindingError("P218_I46_I31_PURGE_RECEIPT_REQUIRED")
            i31 = _verify_i31_receipt(i31_raw, i45=i45, i45_proof=i45_proof)
            request = _derive_i32_request(i31=i31, i34=i34)
            existing_i46 = self.store.active_record()
            active_i32 = self.i32_closer.store.active_record()

            if existing_i46 is not None:
                if existing_i46["i45_receipt_hash72"] != i45["i45_receipt_hash72"]:
                    raise Pass218I46StateError("P218_I46_ACTIVE_I45_CONFLICT")
                if existing_i46["i30_generation_sha256"] != generation_sha256_before:
                    raise Pass218I46StateError("P218_I46_ACTIVE_I30_GENERATION_CONFLICT")
                if not isinstance(active_i32, Mapping):
                    raise Pass218I46StateError("P218_I46_ACTIVE_I32_RECEIPT_MISSING")
                checked_i32 = _verify_i32_receipt(active_i32, request=request, i31=i31)
                if checked_i32["source_closure_hash72"] != existing_i46["i32_source_closure_hash72"]:
                    raise Pass218I46StateError("P218_I46_ACTIVE_I32_RECEIPT_CONFLICT")
                self.last_error_code = None
                return existing_i46

            if isinstance(active_i32, Mapping):
                i32 = _verify_i32_receipt(active_i32, request=request, i31=i31)
                self.restart_adoption_count += 1
            else:
                status_before = self.i32_closer.status()
                if bool(status_before.get("closure_record_present")):
                    raise Pass218I46StateError("P218_I46_I32_NONEMPTY_WITHOUT_RECORD")
                close_count_before = int(self.i32_closer.close_count)
                returned = self.i32_closer.close(request)
                self.i32_invocation_count += 1
                if int(self.i32_closer.close_count) != close_count_before + 1:
                    raise Pass218I46StateError("P218_I46_I32_SINGLE_INVOCATION_NOT_PROVEN")
                active_i32 = self.i32_closer.store.active_record()
                if not isinstance(active_i32, Mapping):
                    raise Pass218I46StateError("P218_I46_I32_DURABLE_RECEIPT_MISSING")
                i32 = _verify_i32_receipt(active_i32, request=request, i31=i31)
                if _copy(returned) != i32:
                    raise Pass218I46StateError("P218_I46_I32_RETURNED_DURABLE_RECEIPT_MISMATCH")

            generation_after, generation_sha256_after = self._current_i30(i45=i45)
            if generation_before != generation_after or generation_sha256_before != generation_sha256_after:
                raise Pass218I46StateError("P218_I46_I30_SEMANTIC_GENERATION_CHANGED_DURING_CLOSURE")
            if i32.get("canonical_root_hash72") != i45.get("i30_canonical_root_hash72"):
                raise Pass218I46StateError("P218_I46_I30_CANONICAL_ROOT_CHANGED_DURING_CLOSURE")

            proof, receipt = self._build(
                i45=i45,
                i42=i42,
                i34=i34,
                i31=i31,
                i32=i32,
                i30_generation_sha256=generation_sha256_before,
            )
            persisted = self.store.commit(receipt, proof)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i45_ready = False
        active_i45_receipt_hash72: str | None = None
        try:
            i45, *_ = self._active_chain()
            i45_ready = True
            active_i45_receipt_hash72 = str(i45["i45_receipt_hash72"])
        except Exception:
            pass
        i32 = self.i32_closer.status()
        return {
            "schema": PASS218_I46_STATUS_SCHEMA,
            "version": PASS218_I46_VERSION,
            "status": PASS218_I46_COMPLETE_STATUS if active is not None else PASS218_I46_PENDING_STATUS,
            "closure_status": None if active is None else PASS218_I46_CLOSED_PENDING_I33_STATUS,
            "predecessor_i45_purge_ready": i45_ready,
            "active_i45_receipt_hash72": active_i45_receipt_hash72,
            "active_i46_receipt_hash72": None if active is None else active["i46_receipt_hash72"],
            "active_i32_source_closure_hash72": None if active is None else active["i32_source_closure_hash72"],
            "i30_generation_sha256": None if active is None else active["i30_generation_sha256"],
            "i32_invocation_count_current_process": self.i32_invocation_count,
            "restart_adoption_count_current_process": self.restart_adoption_count,
            "i32_closure_record_present": bool(i32.get("closure_record_present")),
            "i32_source_closed": bool(i32.get("source_closed")),
            "nonverbatim_source_transaction_durably_closed": active is not None,
            "i32_closure_request_persisted": False,
            "pass218_i33_curriculum_advance_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
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
    "PASS218_I46_CLOSED_PENDING_I33_STATUS",
    "PASS218_I46_COMPLETE_STATUS",
    "PASS218_I46_PENDING_STATUS",
    "PASS218_I46_PROOF_SCHEMA",
    "PASS218_I46_RECEIPT_SCHEMA",
    "PASS218_I46_SCOPE",
    "PASS218_I46_STATE_SCHEMA",
    "PASS218_I46_STATUS_SCHEMA",
    "PASS218_I46_VERSION",
    "Pass218I46BindingError",
    "Pass218I46ClosureError",
    "Pass218I46ClosureStore",
    "Pass218I46ManifestBoundI32SourceClosure",
    "Pass218I46StateError",
]
