"""Pass 218 Iteration 36 manifest-bound vector/VM5184 staging ingress.

I36 begins only from the exact durable I35 receipt plus the exact CLOSED I3
transaction snapshot persisted by I35.  It validates that the snapshot still
carries the I35 manifest/curriculum/source lineage, invokes the frozen I4
ClosedTransactionVectorVM5184Adapter exactly once when no durable I36 state
already exists, and binds the resulting non-authoritative I4 CANDIDATE to the
same manifest lineage in a durable nonverbatim I36 receipt.

This layer does not invoke I5 promotion/admission, I30 canonical semantic
promotion, I31 purge, I32 source closure, curriculum/stage advance, VM81
commit authority, truth/action authority, canonical learning, model
activation, verbatim retention, or authoritative floating-point state.
"""
from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    PASS218_I35_COMPLETE_STATUS,
    PASS218_I35_RECEIPT_SCHEMA,
)
from hhs_runtime.pass218.staging import (
    PASS218_VECTOR_VM5184_STAGER_VERSION,
    ClosedTransactionVectorVM5184Adapter,
    Pass218VectorStageError,
)
from hhs_runtime.pass218.transaction import SourceTransaction, TransactionPhase

PASS218_I36_VERSION = "HHS-P218-I36-MANIFEST-BOUND-VECTOR-VM5184-STAGING-V1"
PASS218_I36_SCOPE = "PASS218_MANIFEST_BOUND_VECTOR_VM5184_STAGING_INGRESS"
PASS218_I36_RECEIPT_SCHEMA = "HHS-P218-I36-MANIFEST-BOUND-VECTOR-VM5184-STAGING-RECEIPT-V1"
PASS218_I36_STAGE_SCHEMA = "HHS-P218-I36-MANIFEST-BOUND-VECTOR-VM5184-STAGE-V1"
PASS218_I36_STATE_SCHEMA = "HHS-P218-I36-MANIFEST-BOUND-VECTOR-VM5184-STAGING-STATE-V1"
PASS218_I36_STATUS_SCHEMA = "HHS-P218-I36-MANIFEST-BOUND-VECTOR-VM5184-STAGING-STATUS-V1"
PASS218_I36_COMPLETE_STATUS = "MANIFEST_BOUND_VECTOR_VM5184_STAGING_INGRESS_COMPLETE"
PASS218_I36_PENDING_STATUS = "MANIFEST_BOUND_VECTOR_VM5184_STAGING_PENDING"


class Pass218I36StagingError(RuntimeError):
    pass


class Pass218I36BindingError(Pass218I36StagingError):
    pass


class Pass218I36StateError(Pass218I36StagingError):
    pass


class Pass218I36I4Error(Pass218I36StagingError):
    pass


class Pass218I36LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I36I35StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_transaction_snapshot(self) -> dict[str, Any] | None: ...


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _copy(value: Any) -> Any:
    if value is None:
        return None
    return json.loads(_canonical_bytes(value).decode("utf-8"))


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
        raise Pass218I36StateError("P218_I36_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I36StateError("P218_I36_STATE_OBJECT_REQUIRED")
    return value


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


def _verify_i35_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I35_RECEIPT_SCHEMA:
        raise Pass218I36BindingError("P218_I36_I35_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I35_COMPLETE_STATUS:
        raise Pass218I36BindingError("P218_I36_I35_NOT_COMPLETE")
    required_true = (
        "i34_ingress_bound",
        "manifest_binding_propagated",
        "semantic_construction_invoked",
        "semantic_candidate_nonverbatim",
        "i3_source_transaction_required",
        "i3_source_transaction_invoked",
        "i3_transaction_closed",
        "i3_managed_buffer_zeroized",
        "i3_managed_buffer_cleared",
        "structural_candidate_admitted_non_authoritatively",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I36BindingError("P218_I36_I35_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "pass218_i4_staging_invoked",
        "pass218_i5_promotion_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I36BindingError("P218_I36_I35_AUTHORITY_DRIFT")
    for field in (
        "i34_ingress_receipt_hash72",
        "manifest_genesis_seed_hash72",
        "manifest_bound_semantic_hash72",
        "i3_transaction_id_hash72",
        "i3_structural_record_hash72",
        "i3_purge_receipt_hash72",
        "i3_memory_root_hash72",
        "i3_closure_hash72",
        "i3_transaction_snapshot_hash72",
        "i35_validation_hash72",
        "i35_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I36BindingError("P218_I36_I35_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i2_candidate_hash216")):
        raise Pass218I36BindingError("P218_I36_I35_I2_HASH216_INVALID")
    if not _valid_hash216(value.get("i3_transaction_hash216")):
        raise Pass218I36BindingError("P218_I36_I35_I3_HASH216_INVALID")
    binding = value.get("manifest_binding")
    if not isinstance(binding, Mapping):
        raise Pass218I36BindingError("P218_I36_MANIFEST_BINDING_REQUIRED")
    if binding.get("ingress_receipt_hash72") != value.get("i34_ingress_receipt_hash72"):
        raise Pass218I36BindingError("P218_I36_I35_BINDING_RECEIPT_MISMATCH")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i35_receipt_hash72", "i35_hash216", "i35_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I35_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("i35_receipt_hash72"):
        raise Pass218I36BindingError("P218_I36_I35_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i34_ingress_receipt_hash72"])
        + str(value["manifest_bound_semantic_hash72"])
        + str(value["i35_receipt_hash72"])
    )
    if expected_hash216 != value.get("i35_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I36BindingError("P218_I36_I35_HASH216_INVALID")
    return value


def _verify_i35_snapshot(
    snapshot: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    copied = _copy(dict(snapshot))
    try:
        restored = SourceTransaction.restore(copied)
    except Exception as exc:
        raise Pass218I36BindingError("P218_I36_I35_SNAPSHOT_INVALID") from exc
    if restored.phase != TransactionPhase.CLOSED:
        raise Pass218I36BindingError("P218_I36_I35_SNAPSHOT_NOT_CLOSED")
    if restored.transaction_id_hash72 != receipt["i3_transaction_id_hash72"]:
        raise Pass218I36BindingError("P218_I36_I35_TRANSACTION_ID_MISMATCH")
    if copied.get("snapshot_hash72") != receipt["i3_transaction_snapshot_hash72"]:
        raise Pass218I36BindingError("P218_I36_I35_SNAPSHOT_HASH_MISMATCH")
    candidate = restored.candidate_record
    if candidate.get("manifest_bound_semantic_hash72") != receipt["manifest_bound_semantic_hash72"]:
        raise Pass218I36BindingError("P218_I36_SEMANTIC_BINDING_MISMATCH")
    if candidate.get("manifest_binding") != receipt["manifest_binding"]:
        raise Pass218I36BindingError("P218_I36_MANIFEST_BINDING_MISMATCH")
    if candidate.get("genesis_seed_hash72") != receipt["manifest_genesis_seed_hash72"]:
        raise Pass218I36BindingError("P218_I36_GENESIS_BINDING_MISMATCH")
    closure = restored.closure_receipt
    if not isinstance(closure, Mapping):
        raise Pass218I36BindingError("P218_I36_I3_CLOSURE_MISSING")
    for snapshot_field, receipt_field in (
        ("closure_hash72", "i3_closure_hash72"),
        ("structural_record_hash72", "i3_structural_record_hash72"),
        ("purge_receipt_hash72", "i3_purge_receipt_hash72"),
        ("memory_root_hash72", "i3_memory_root_hash72"),
        ("transaction_hash216", "i3_transaction_hash216"),
    ):
        if closure.get(snapshot_field) != receipt.get(receipt_field):
            raise Pass218I36BindingError(
                "P218_I36_I3_CLOSURE_BINDING_MISMATCH:" + snapshot_field
            )
    for flag in (
        "verbatim_source_retained",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
    ):
        if closure.get(flag) is not False:
            raise Pass218I36BindingError("P218_I36_I3_AUTHORITY_FLAG_INVALID:" + flag)
    return copied


def _verify_i4_stage(
    stage: Mapping[str, Any],
    *,
    i35_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(stage))
    if value.get("schema") != "HHS-P218-I4-VECTOR-VM5184-STAGE-CANDIDATE-V1":
        raise Pass218I36I4Error("P218_I36_I4_STAGE_SCHEMA_INVALID")
    if value.get("stager_version") != PASS218_VECTOR_VM5184_STAGER_VERSION:
        raise Pass218I36I4Error("P218_I36_I4_STAGER_VERSION_INVALID")
    for stage_field, receipt_field in (
        ("transaction_id_hash72", "i3_transaction_id_hash72"),
        ("transaction_hash216", "i3_transaction_hash216"),
        ("structural_record_hash72", "i3_structural_record_hash72"),
        ("purge_receipt_hash72", "i3_purge_receipt_hash72"),
    ):
        if value.get(stage_field) != i35_receipt.get(receipt_field):
            raise Pass218I36I4Error("P218_I36_I4_TRANSACTION_BINDING_MISMATCH:" + stage_field)
    for field in (
        "transaction_id_hash72",
        "structural_record_hash72",
        "purge_receipt_hash72",
        "vm5184_projection_hash72",
        "staging_hash72",
        "validation_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I36I4Error("P218_I36_I4_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("transaction_hash216")):
        raise Pass218I36I4Error("P218_I36_I4_TRANSACTION_HASH216_INVALID")
    if not _valid_hash216(value.get("staging_hash216")):
        raise Pass218I36I4Error("P218_I36_I4_STAGING_HASH216_INVALID")
    expected_hash216 = (
        str(i35_receipt["i3_closure_hash72"])
        + str(value["staging_hash72"])
        + str(value["validation_hash72"])
    )
    if value.get("staging_hash216") != expected_hash216:
        raise Pass218I36I4Error("P218_I36_I4_STAGING_HASH216_ORDER_INVALID")
    if value.get("hash216_semantics") != [
        "CLOSED_SOURCE_TRANSACTION",
        "VECTOR_VM5184_STAGE_CANDIDATE",
        "STAGING_VALIDATION_RECEIPT",
    ]:
        raise Pass218I36I4Error("P218_I36_I4_HASH216_SEMANTICS_INVALID")
    entry = value.get("vector_entry")
    if not isinstance(entry, Mapping):
        raise Pass218I36I4Error("P218_I36_I4_VECTOR_ENTRY_REQUIRED")
    if entry.get("schema") != "HHS_PASS_217_VECTOR_STORE_ENTRY_V1":
        raise Pass218I36I4Error("P218_I36_I4_VECTOR_ENTRY_SCHEMA_INVALID")
    if entry.get("admission_status") != "CANDIDATE":
        raise Pass218I36I4Error("P218_I36_I4_VECTOR_ENTRY_NOT_CANDIDATE")
    if not _valid_sha256(entry.get("entry_id_sha256")):
        raise Pass218I36I4Error("P218_I36_I4_VECTOR_ENTRY_ID_INVALID")
    try:
        projection = b64decode(str(value.get("vm5184_projection_b64", "")), validate=True)
    except Exception as exc:
        raise Pass218I36I4Error("P218_I36_I4_PROJECTION_B64_INVALID") from exc
    if len(projection) != SNAPSHOT_BYTES or value.get("vm5184_projection_bytes") != SNAPSHOT_BYTES:
        raise Pass218I36I4Error("P218_I36_I4_VM5184_LENGTH_INVALID")
    if sha256(projection).hexdigest() != value.get("vm5184_projection_sha256"):
        raise Pass218I36I4Error("P218_I36_I4_PROJECTION_SHA256_MISMATCH")
    if hash72_digest(b"", projection) != value.get("vm5184_projection_hash72"):
        raise Pass218I36I4Error("P218_I36_I4_PROJECTION_HASH72_MISMATCH")
    forward = list(entry.get("forward_support", []))
    inverse = list(entry.get("inverse_support", []))
    if (
        forward != sorted(set(forward))
        or inverse != sorted(set(inverse))
        or set(forward).intersection(inverse)
        or sorted(forward + inverse) != list(range(COORDINATES))
    ):
        raise Pass218I36I4Error("P218_I36_I4_SUPPORT_PARTITION_INVALID")
    if value.get("vm5184_projection_popcount") != len(forward):
        raise Pass218I36I4Error("P218_I36_I4_POPCOUNT_INVALID")
    for flag in (
        "verbatim_source_retained",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "authoritative_float_weights",
    ):
        if value.get(flag) is not False:
            raise Pass218I36I4Error("P218_I36_I4_AUTHORITY_FLAG_INVALID:" + flag)
    return value


def _build_manifest_bound_stage(
    i35_receipt: Mapping[str, Any],
    i4_stage: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        "schema": PASS218_I36_STAGE_SCHEMA,
        "version": PASS218_I36_VERSION,
        "i35_receipt_hash72": i35_receipt["i35_receipt_hash72"],
        "i35_hash216": i35_receipt["i35_hash216"],
        "i34_ingress_receipt_hash72": i35_receipt["i34_ingress_receipt_hash72"],
        "manifest_bound_semantic_hash72": i35_receipt["manifest_bound_semantic_hash72"],
        "manifest_binding": _copy(i35_receipt["manifest_binding"]),
        "i3_transaction_id_hash72": i35_receipt["i3_transaction_id_hash72"],
        "i3_transaction_snapshot_hash72": i35_receipt["i3_transaction_snapshot_hash72"],
        "i4_stage_candidate": _copy(dict(i4_stage)),
        "manifest_binding_propagated": True,
        "i4_stage_candidate_non_authoritative": True,
        "verbatim_source_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "canonical_vm81_commit_invoked": False,
        "canonical_learning_commit_invoked": False,
        "authoritative_float_weights_created": False,
    }
    return {
        **body,
        "manifest_bound_i4_stage_hash72": hash72_digest(
            {"domain": PASS218_I36_STAGE_SCHEMA}, body
        ),
    }


def _verify_manifest_bound_stage(
    stage: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(stage))
    if value.get("schema") != PASS218_I36_STAGE_SCHEMA:
        raise Pass218I36StateError("P218_I36_STAGE_SCHEMA_INVALID")
    body = {key: item for key, item in value.items() if key != "manifest_bound_i4_stage_hash72"}
    expected = hash72_digest({"domain": PASS218_I36_STAGE_SCHEMA}, body)
    if expected != value.get("manifest_bound_i4_stage_hash72"):
        raise Pass218I36StateError("P218_I36_STAGE_HASH_MISMATCH")
    if expected != receipt.get("manifest_bound_i4_stage_hash72"):
        raise Pass218I36StateError("P218_I36_STAGE_RECEIPT_BINDING_MISMATCH")
    if value.get("i35_receipt_hash72") != receipt.get("i35_receipt_hash72"):
        raise Pass218I36StateError("P218_I36_STAGE_I35_RECEIPT_MISMATCH")
    if value.get("manifest_binding") != receipt.get("manifest_binding"):
        raise Pass218I36StateError("P218_I36_STAGE_MANIFEST_BINDING_MISMATCH")
    return value


def _verify_i36_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I36_RECEIPT_SCHEMA:
        raise Pass218I36StateError("P218_I36_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I36_COMPLETE_STATUS:
        raise Pass218I36StateError("P218_I36_RECEIPT_STATUS_INVALID")
    required_true = (
        "i35_receipt_bound",
        "manifest_binding_propagated",
        "closed_i3_snapshot_bound",
        "pass218_i4_staging_required",
        "pass218_i4_staging_invoked",
        "i4_stage_candidate_non_authoritative",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I36StateError("P218_I36_RECEIPT_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "pass218_i5_promotion_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I36StateError("P218_I36_RECEIPT_AUTHORITY_DRIFT")
    for field in (
        "i35_receipt_hash72",
        "i34_ingress_receipt_hash72",
        "manifest_bound_semantic_hash72",
        "i3_transaction_id_hash72",
        "i3_transaction_snapshot_hash72",
        "manifest_bound_i4_stage_hash72",
        "i4_staging_hash72",
        "i4_validation_hash72",
        "i4_projection_hash72",
        "i36_validation_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I36StateError("P218_I36_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i35_hash216")):
        raise Pass218I36StateError("P218_I36_I35_HASH216_INVALID")
    if not _valid_hash216(value.get("i4_staging_hash216")):
        raise Pass218I36StateError("P218_I36_I4_HASH216_INVALID")
    if not _valid_sha256(value.get("i4_entry_id_sha256")):
        raise Pass218I36StateError("P218_I36_I4_ENTRY_ID_INVALID")
    if not _valid_sha256(value.get("i4_projection_sha256")):
        raise Pass218I36StateError("P218_I36_I4_PROJECTION_SHA256_INVALID")
    if value.get("i4_projection_bytes") != SNAPSHOT_BYTES:
        raise Pass218I36StateError("P218_I36_I4_PROJECTION_LENGTH_INVALID")
    if value.get("i4_vector_admission_status") != "CANDIDATE":
        raise Pass218I36StateError("P218_I36_I4_ADMISSION_STATUS_INVALID")
    if not isinstance(value.get("manifest_binding"), Mapping):
        raise Pass218I36StateError("P218_I36_RECEIPT_MANIFEST_BINDING_REQUIRED")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i36_receipt_hash72", "i36_hash216", "i36_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I36_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("i36_receipt_hash72"):
        raise Pass218I36StateError("P218_I36_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i35_receipt_hash72"])
        + str(value["i4_staging_hash72"])
        + str(value["i36_receipt_hash72"])
    )
    if expected_hash216 != value.get("i36_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I36StateError("P218_I36_HASH216_INVALID")
    return value


class Pass218I36ManifestBoundVectorStageStore:
    """Durable nonverbatim I36 binding receipt and manifest-bound I4 candidate."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.stage_root = self.root / "stages"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I36_STATE_SCHEMA:
            raise Pass218I36StateError("P218_I36_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I36_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I36StateError("P218_I36_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        stage_path = self.root / str(state.get("active_stage_path", ""))
        if not receipt_path.is_file() or not stage_path.is_file():
            raise Pass218I36StateError("P218_I36_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i36_receipt(_load_json(receipt_path))
        if receipt["i36_receipt_hash72"] != state.get("active_i36_receipt_hash72"):
            raise Pass218I36StateError("P218_I36_STATE_RECEIPT_MISMATCH")
        stage = _verify_manifest_bound_stage(_load_json(stage_path), receipt)
        if stage["manifest_bound_i4_stage_hash72"] != state.get("active_stage_hash72"):
            raise Pass218I36StateError("P218_I36_STATE_STAGE_MISMATCH")
        return receipt

    def active_stage(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_manifest_bound_stage(
            _load_json(self.root / str(state["active_stage_path"])),
            receipt,
        )

    def commit(
        self,
        receipt: Mapping[str, Any],
        manifest_bound_stage: Mapping[str, Any],
    ) -> dict[str, Any]:
        checked = _verify_i36_receipt(receipt)
        stage = _verify_manifest_bound_stage(manifest_bound_stage, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked:
                raise Pass218I36StateError("P218_I36_ACTIVE_BINDING_CONFLICT")
            if self.active_stage() != stage:
                raise Pass218I36StateError("P218_I36_ACTIVE_STAGE_CONFLICT")
            return existing
        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_path = self.receipt_root / f"{ordinal:08d}-{checked['i36_receipt_hash72']}.json"
        stage_path = self.stage_root / f"{checked['manifest_bound_i4_stage_hash72']}.json"
        if receipt_path.exists():
            if _load_json(receipt_path) != checked:
                raise Pass218I36StateError("P218_I36_RECEIPT_CONFLICT")
        else:
            _atomic_write_json(receipt_path, checked)
        if stage_path.exists():
            if _load_json(stage_path) != stage:
                raise Pass218I36StateError("P218_I36_STAGE_CONFLICT")
        else:
            _atomic_write_json(stage_path, stage)
        state_body = {
            "schema": PASS218_I36_STATE_SCHEMA,
            "version": PASS218_I36_VERSION,
            "status": PASS218_I36_COMPLETE_STATUS,
            "i35_receipt_hash72": checked["i35_receipt_hash72"],
            "active_i36_receipt_hash72": checked["i36_receipt_hash72"],
            "active_stage_hash72": stage["manifest_bound_i4_stage_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_stage_path": stage_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest(
                {"domain": PASS218_I36_STATE_SCHEMA}, state_body
            ),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I36StateError("P218_I36_STATE_PERSIST_MISMATCH")
        return checked


class Pass218I36ManifestBoundVectorVM5184Staging:
    """Bind exact frozen I35 state to frozen I4 non-authoritative staging."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I36LifecycleProtocol,
        i35_store: Pass218I36I35StoreProtocol,
        state_root: str | os.PathLike[str],
        i35_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        i4_adapter: ClosedTransactionVectorVM5184Adapter | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i35_store = i35_store
        self.i35_status_provider = i35_status_provider
        self.adapter = i4_adapter or ClosedTransactionVectorVM5184Adapter()
        self.store = Pass218I36ManifestBoundVectorStageStore(state_root)
        self.i4_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _active_i35(self) -> tuple[dict[str, Any], dict[str, Any]]:
        receipt = self.i35_store.active_record()
        snapshot = self.i35_store.active_transaction_snapshot()
        if receipt is None or snapshot is None:
            raise Pass218I36BindingError("P218_I36_I35_COMPLETE_STATE_REQUIRED")
        checked = _verify_i35_receipt(receipt)
        checked_snapshot = _verify_i35_snapshot(snapshot, checked)
        if self.i35_status_provider is not None:
            status = dict(self.i35_status_provider())
            if status.get("status") != PASS218_I35_COMPLETE_STATUS:
                raise Pass218I36BindingError("P218_I36_I35_STATUS_NOT_COMPLETE")
            if status.get("active_i35_receipt_hash72") != checked["i35_receipt_hash72"]:
                raise Pass218I36BindingError("P218_I36_I35_STATUS_RECEIPT_MISMATCH")
            if status.get("i3_transaction_snapshot_hash72") != checked["i3_transaction_snapshot_hash72"]:
                raise Pass218I36BindingError("P218_I36_I35_STATUS_SNAPSHOT_MISMATCH")
        return checked, checked_snapshot

    def stage(self) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            i35, snapshot = self._active_i35()
            existing = self.store.active_record()
            if existing is not None:
                if (
                    existing["i35_receipt_hash72"] != i35["i35_receipt_hash72"]
                    or existing["i3_transaction_snapshot_hash72"] != i35["i3_transaction_snapshot_hash72"]
                    or existing["manifest_binding"] != i35["manifest_binding"]
                ):
                    raise Pass218I36StateError("P218_I36_ACTIVE_BINDING_CONFLICT")
                self.last_error_code = None
                return existing
            try:
                i4_stage = self.adapter.stage(snapshot)
                self.i4_invocation_count += 1
            except Pass218VectorStageError as exc:
                raise Pass218I36I4Error("P218_I36_I4_STAGE_FAILED:" + str(exc)) from exc
            checked_i4 = _verify_i4_stage(i4_stage, i35_receipt=i35)
            manifest_bound_stage = _build_manifest_bound_stage(i35, checked_i4)
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I36-MANIFEST-BOUND-STAGING-VALIDATION-V1"},
                {
                    "i35_receipt_hash72": i35["i35_receipt_hash72"],
                    "i3_transaction_snapshot_hash72": i35["i3_transaction_snapshot_hash72"],
                    "manifest_bound_i4_stage_hash72": manifest_bound_stage["manifest_bound_i4_stage_hash72"],
                    "i4_staging_hash72": checked_i4["staging_hash72"],
                    "i4_validation_hash72": checked_i4["validation_hash72"],
                    "i4_entry_id_sha256": checked_i4["vector_entry"]["entry_id_sha256"],
                    "manifest_binding_propagated": True,
                    "i4_stage_candidate_non_authoritative": True,
                    "later_pass218_authority_invoked": False,
                },
            )
            body = {
                "schema": PASS218_I36_RECEIPT_SCHEMA,
                "version": PASS218_I36_VERSION,
                "scope": PASS218_I36_SCOPE,
                "status": PASS218_I36_COMPLETE_STATUS,
                "i35_receipt_hash72": i35["i35_receipt_hash72"],
                "i35_hash216": i35["i35_hash216"],
                "i34_ingress_receipt_hash72": i35["i34_ingress_receipt_hash72"],
                "manifest_bound_semantic_hash72": i35["manifest_bound_semantic_hash72"],
                "manifest_binding": _copy(i35["manifest_binding"]),
                "i3_transaction_id_hash72": i35["i3_transaction_id_hash72"],
                "i3_transaction_snapshot_hash72": i35["i3_transaction_snapshot_hash72"],
                "manifest_bound_i4_stage_hash72": manifest_bound_stage["manifest_bound_i4_stage_hash72"],
                "i4_stager_version": checked_i4["stager_version"],
                "i4_entry_id_sha256": checked_i4["vector_entry"]["entry_id_sha256"],
                "i4_staging_hash72": checked_i4["staging_hash72"],
                "i4_validation_hash72": checked_i4["validation_hash72"],
                "i4_staging_hash216": checked_i4["staging_hash216"],
                "i4_projection_hash72": checked_i4["vm5184_projection_hash72"],
                "i4_projection_sha256": checked_i4["vm5184_projection_sha256"],
                "i4_projection_bytes": checked_i4["vm5184_projection_bytes"],
                "i4_vector_admission_status": checked_i4["vector_entry"]["admission_status"],
                "i36_validation_hash72": validation_hash72,
                "i35_receipt_bound": True,
                "manifest_binding_propagated": True,
                "closed_i3_snapshot_bound": True,
                "pass218_i4_staging_required": True,
                "pass218_i4_staging_invoked": True,
                "i4_stage_candidate_non_authoritative": True,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
                "pass218_i5_promotion_invoked": False,
                "pass218_i30_canonical_semantic_promotion_invoked": False,
                "pass218_i31_verbatim_purge_invoked": False,
                "pass218_i32_source_closure_invoked": False,
                "curriculum_cursor_advanced": False,
                "stage_advance_permitted": False,
                "vm81_authorization_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "authoritative_vector_store_promotion": False,
                "canonical_vm81_commit_invoked": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
            receipt_hash72 = hash72_digest({"domain": PASS218_I36_RECEIPT_SCHEMA}, body)
            receipt = {
                **body,
                "i36_receipt_hash72": receipt_hash72,
                "i36_hash216": i35["i35_receipt_hash72"] + checked_i4["staging_hash72"] + receipt_hash72,
                "i36_hash216_semantics": [
                    "I35_MANIFEST_BOUND_SEMANTIC_SOURCE_TRANSACTION_RECEIPT",
                    "I4_VECTOR_VM5184_STAGE_CANDIDATE",
                    "I36_MANIFEST_BOUND_STAGING_BINDING_RECEIPT",
                ],
            }
            persisted = self.store.commit(receipt, manifest_bound_stage)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def active_stage(self) -> dict[str, Any] | None:
        return self.store.active_stage()

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i35_ready = False
        active_i35_receipt_hash72: str | None = None
        i35_snapshot_hash72: str | None = None
        try:
            i35, _ = self._active_i35()
            i35_ready = True
            active_i35_receipt_hash72 = str(i35["i35_receipt_hash72"])
            i35_snapshot_hash72 = str(i35["i3_transaction_snapshot_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I36_STATUS_SCHEMA,
            "version": PASS218_I36_VERSION,
            "status": PASS218_I36_COMPLETE_STATUS if active is not None else PASS218_I36_PENDING_STATUS,
            "i35_complete_state_ready": i35_ready,
            "active_i35_receipt_hash72": active_i35_receipt_hash72,
            "i35_transaction_snapshot_hash72": i35_snapshot_hash72,
            "active_i36_receipt_hash72": None if active is None else active["i36_receipt_hash72"],
            "manifest_bound_i4_stage_hash72": None if active is None else active["manifest_bound_i4_stage_hash72"],
            "i4_entry_id_sha256": None if active is None else active["i4_entry_id_sha256"],
            "i4_invocation_count_current_process": self.i4_invocation_count,
            "pass218_i4_staging_invoked": active is not None or self.i4_invocation_count > 0,
            "i4_stage_candidate_non_authoritative": active is not None,
            "i4_vector_admission_status": None if active is None else active["i4_vector_admission_status"],
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "pass218_i5_promotion_invoked": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I36_COMPLETE_STATUS",
    "PASS218_I36_PENDING_STATUS",
    "PASS218_I36_RECEIPT_SCHEMA",
    "PASS218_I36_SCOPE",
    "PASS218_I36_STAGE_SCHEMA",
    "PASS218_I36_STATE_SCHEMA",
    "PASS218_I36_STATUS_SCHEMA",
    "PASS218_I36_VERSION",
    "Pass218I36BindingError",
    "Pass218I36I4Error",
    "Pass218I36ManifestBoundVectorStageStore",
    "Pass218I36ManifestBoundVectorVM5184Staging",
    "Pass218I36StagingError",
    "Pass218I36StateError",
]
