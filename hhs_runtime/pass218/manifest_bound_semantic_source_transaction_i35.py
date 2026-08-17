"""Pass 218 Iteration 35 manifest-bound semantic/source-transaction ingress.

I35 consumes the exact frozen I34 manifest-bound ingress receipt, binds that
authority/lineage envelope to an already-materialized frozen-I2 narrative
hydration candidate, and only then invokes the frozen I3 SourceTransaction
membrane.  I35 persists a nonverbatim binding receipt plus the closed I3
transaction snapshot required for deterministic continuation.  It does not
promote learning, advance curriculum/stage authority, invoke VM81 authority,
or enter the later I31/I32 purge/closure stages.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    PASS218_I34_READY_STATUS,
    PASS218_I34_RECEIPT_SCHEMA,
    Pass218I34ManifestSourceIngressStore,
)
from hhs_runtime.pass218.transaction import (
    DeterministicStructuralStore,
    Pass218TransactionError,
    SourceTransaction,
    TransactionPhase,
)

PASS218_I35_VERSION = "HHS-P218-I35-MANIFEST-BOUND-SEMANTIC-SOURCE-TRANSACTION-V1"
PASS218_I35_SCOPE = "PASS218_MANIFEST_BOUND_SEMANTIC_SOURCE_TRANSACTION_INGRESS"
PASS218_I35_RECEIPT_SCHEMA = "HHS-P218-I35-MANIFEST-SEMANTIC-SOURCE-TRANSACTION-RECEIPT-V1"
PASS218_I35_STATE_SCHEMA = "HHS-P218-I35-MANIFEST-SEMANTIC-SOURCE-TRANSACTION-STATE-V1"
PASS218_I35_STATUS_SCHEMA = "HHS-P218-I35-MANIFEST-SEMANTIC-SOURCE-TRANSACTION-STATUS-V1"
PASS218_I35_COMPLETE_STATUS = "MANIFEST_BOUND_SEMANTIC_SOURCE_TRANSACTION_INGRESS_COMPLETE"
PASS218_I35_PENDING_STATUS = "MANIFEST_BOUND_SEMANTIC_SOURCE_TRANSACTION_PENDING"

_I2_CANDIDATE_SCHEMA = "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1"
_PROTECTED_CANDIDATE_FIELDS = frozenset({
    "manifest_binding",
    "manifest_bound_semantic_hash72",
    "manifest_bound_semantic_candidate",
    "i34_ingress_receipt_hash72",
    "semantic_construction_invoked",
    "i3_source_transaction_required",
    "i3_source_transaction_invoked",
    "authority_root_hash72",
    "manifest_hash72",
    "curriculum_identity_hash72",
    "curriculum_position",
    "source_stage",
    "source_stage_name",
    "rights_class",
    "source_authority",
    "previous_closure_hash72",
    "previous_advance_receipt_hash72",
    "source_identity_hash72",
    "source_binding_hash72",
    "ingress_receipt_hash72",
    "ingress_hash216",
})
_BINDING_FIELDS = (
    "authority_root_hash72",
    "manifest_hash72",
    "curriculum_identity_hash72",
    "curriculum_position",
    "source_id",
    "source_sha256",
    "source_stage",
    "source_stage_name",
    "rights_class",
    "source_authority",
    "media_type",
    "source_byte_count",
    "previous_closure_hash72",
    "previous_advance_receipt_hash72",
    "source_identity_hash72",
    "source_binding_hash72",
    "ingress_validation_hash72",
    "ingress_receipt_hash72",
    "ingress_hash216",
)


class Pass218I35IngressError(RuntimeError):
    pass


class Pass218I35BindingError(Pass218I35IngressError):
    pass


class Pass218I35StateError(Pass218I35IngressError):
    pass


class Pass218I35TransactionError(Pass218I35IngressError):
    pass


class Pass218I35LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...
    def status(self) -> Mapping[str, Any]: ...


class Pass218I35I34StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...


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
        raise Pass218I35StateError("P218_I35_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I35StateError("P218_I35_STATE_OBJECT_REQUIRED")
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


def _candidate_record(candidate: Any) -> dict[str, Any]:
    if hasattr(candidate, "to_record"):
        value = candidate.to_record()
    elif isinstance(candidate, Mapping):
        value = dict(candidate)
    else:
        raise Pass218I35BindingError("P218_I35_SEMANTIC_CANDIDATE_TYPE_UNSUPPORTED")
    copied = _copy(value)
    if not isinstance(copied, dict):
        raise Pass218I35BindingError("P218_I35_SEMANTIC_CANDIDATE_OBJECT_REQUIRED")
    return copied


def _verify_i34_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I34_RECEIPT_SCHEMA:
        raise Pass218I35BindingError("P218_I35_I34_RECEIPT_SCHEMA_INVALID")
    if value.get("binding_status") != PASS218_I34_READY_STATUS:
        raise Pass218I35BindingError("P218_I35_I34_BINDING_NOT_READY")
    required_true = (
        "manifest_match_verified",
        "cursor_match_verified",
        "source_checksum_verified",
        "source_metadata_bound",
        "previous_closure_bound",
        "managed_ingress_buffer_zeroized",
        "managed_ingress_buffer_cleared",
        "manifest_bound_source_ready",
        "i3_source_transaction_required",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I35BindingError("P218_I35_I34_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "i3_source_transaction_invoked",
        "semantic_construction_invoked",
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
        raise Pass218I35BindingError("P218_I35_I34_AUTHORITY_DRIFT")
    for field in (
        "authority_root_hash72",
        "manifest_hash72",
        "curriculum_identity_hash72",
        "source_identity_hash72",
        "source_binding_hash72",
        "ingress_validation_hash72",
        "ingress_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I35BindingError("P218_I35_I34_HASH72_INVALID:" + field)
    if not _valid_sha256(value.get("source_sha256")):
        raise Pass218I35BindingError("P218_I35_I34_SOURCE_SHA256_INVALID")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"ingress_receipt_hash72", "ingress_hash216", "ingress_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I34_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("ingress_receipt_hash72"):
        raise Pass218I35BindingError("P218_I35_I34_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["curriculum_identity_hash72"])
        + str(value["ingress_validation_hash72"])
        + str(value["ingress_receipt_hash72"])
    )
    if expected_hash216 != value.get("ingress_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I35BindingError("P218_I35_I34_HASH216_INVALID")
    return value


def _manifest_binding(i34_receipt: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in _BINDING_FIELDS if field not in i34_receipt]
    if missing:
        raise Pass218I35BindingError(
            "P218_I35_I34_BINDING_FIELD_MISSING:" + ",".join(sorted(missing))
        )
    return {field: _copy(i34_receipt[field]) for field in _BINDING_FIELDS}


def _verify_base_i2_candidate(
    candidate: Mapping[str, Any],
    *,
    ingress: Mapping[str, Any],
    manifest_genesis_seed_hash72: str,
    observed_source_sha256: str,
    observed_source_byte_count: int,
) -> None:
    if candidate.get("schema") != _I2_CANDIDATE_SCHEMA:
        raise Pass218I35BindingError("P218_I35_I2_CANDIDATE_SCHEMA_REQUIRED")
    forbidden = sorted(_PROTECTED_CANDIDATE_FIELDS.intersection(candidate))
    if forbidden:
        raise Pass218I35BindingError(
            "P218_I35_REQUEST_CANNOT_SUPPLY_MANIFEST_BINDING:" + ",".join(forbidden)
        )
    if candidate.get("source_id") != ingress.get("source_id"):
        raise Pass218I35BindingError("P218_I35_CANDIDATE_SOURCE_ID_MISMATCH")
    if candidate.get("source_sha256") != ingress.get("source_sha256"):
        raise Pass218I35BindingError("P218_I35_CANDIDATE_SOURCE_SHA256_MISMATCH")
    if observed_source_sha256 != ingress.get("source_sha256"):
        raise Pass218I35BindingError("P218_I35_TRANSIENT_SOURCE_SHA256_MISMATCH")
    if observed_source_byte_count != int(ingress.get("source_byte_count", -1)):
        raise Pass218I35BindingError("P218_I35_TRANSIENT_SOURCE_LENGTH_MISMATCH")
    if not str(candidate.get("source_epistemic_class", "")).strip():
        raise Pass218I35BindingError("P218_I35_CANDIDATE_EPISTEMIC_CLASS_REQUIRED")
    if candidate.get("genesis_seed_hash72") != manifest_genesis_seed_hash72:
        raise Pass218I35BindingError("P218_I35_CANDIDATE_GENESIS_IDENTITY_MISMATCH")
    for field in (
        "genesis_seed_hash72",
        "grammar_rule_set_hash72",
        "hydration_hash72",
        "validation_hash72",
    ):
        if not validate_hash72(str(candidate.get(field, ""))):
            raise Pass218I35BindingError("P218_I35_CANDIDATE_HASH72_INVALID:" + field)
    candidate_hash216 = candidate.get("hash216")
    expected_hash216 = (
        str(candidate["genesis_seed_hash72"])
        + str(candidate["hydration_hash72"])
        + str(candidate["validation_hash72"])
    )
    if candidate_hash216 != expected_hash216 or not _valid_hash216(candidate_hash216):
        raise Pass218I35BindingError("P218_I35_CANDIDATE_HASH216_INVALID")
    if not isinstance(candidate.get("beats"), list) or not candidate["beats"]:
        raise Pass218I35BindingError("P218_I35_CANDIDATE_STRUCTURAL_BEATS_REQUIRED")
    for flag in (
        "verbatim_source_retained",
        "source_text_retained",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
        "authoritative_float_weights",
    ):
        if candidate.get(flag) is not False:
            raise Pass218I35BindingError("P218_I35_CANDIDATE_AUTHORITY_FLAG_INVALID:" + flag)


def _build_manifest_bound_candidate(
    base_candidate: Mapping[str, Any],
    ingress: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    binding = _manifest_binding(ingress)
    semantic_body = {
        "schema": "HHS-P218-I35-MANIFEST-BOUND-SEMANTIC-CANDIDATE-V1",
        "i34_ingress_receipt_hash72": ingress["ingress_receipt_hash72"],
        "i2_candidate_hash216": base_candidate["hash216"],
        "i2_hydration_hash72": base_candidate["hydration_hash72"],
        "i2_validation_hash72": base_candidate["validation_hash72"],
        "manifest_binding": binding,
        "semantic_construction_invoked": True,
        "i3_source_transaction_required": True,
        "i3_source_transaction_invoked": False,
        "verbatim_source_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "vm81_authorization_invoked": False,
        "authoritative_float_weights_created": False,
    }
    semantic_hash72 = hash72_digest(
        {"domain": "HHS-P218-I35-MANIFEST-BOUND-SEMANTIC-CANDIDATE-V1"},
        semantic_body,
    )
    enriched = {
        **_copy(dict(base_candidate)),
        "manifest_binding": binding,
        "manifest_bound_semantic_hash72": semantic_hash72,
        "manifest_bound_semantic_candidate": True,
        "i34_ingress_receipt_hash72": ingress["ingress_receipt_hash72"],
        "semantic_construction_invoked": True,
        "i3_source_transaction_required": True,
        "i3_source_transaction_invoked": False,
    }
    return enriched, binding, semantic_hash72


def _verify_i35_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I35_RECEIPT_SCHEMA:
        raise Pass218I35StateError("P218_I35_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I35_COMPLETE_STATUS:
        raise Pass218I35StateError("P218_I35_RECEIPT_STATUS_INVALID")
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
        raise Pass218I35StateError("P218_I35_RECEIPT_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "physical_memory_erasure_claimed",
        "external_request_buffer_erasure_claimed",
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
        raise Pass218I35StateError("P218_I35_RECEIPT_AUTHORITY_DRIFT")
    for field in (
        "i34_ingress_receipt_hash72",
        "manifest_bound_semantic_hash72",
        "i2_hydration_hash72",
        "i2_validation_hash72",
        "i3_transaction_id_hash72",
        "i3_structural_record_hash72",
        "i3_purge_receipt_hash72",
        "i3_memory_root_hash72",
        "i3_closure_hash72",
        "i3_transaction_snapshot_hash72",
        "i35_validation_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I35StateError("P218_I35_RECEIPT_HASH72_INVALID:" + field)
    if not validate_hash72(str(value.get("manifest_genesis_seed_hash72", ""))):
        raise Pass218I35StateError("P218_I35_MANIFEST_GENESIS_HASH72_INVALID")
    if not _valid_hash216(value.get("i2_candidate_hash216")):
        raise Pass218I35StateError("P218_I35_I2_HASH216_INVALID")
    if not _valid_hash216(value.get("i3_transaction_hash216")):
        raise Pass218I35StateError("P218_I35_I3_HASH216_INVALID")
    binding = value.get("manifest_binding")
    if not isinstance(binding, Mapping):
        raise Pass218I35StateError("P218_I35_MANIFEST_BINDING_REQUIRED")
    if binding.get("ingress_receipt_hash72") != value.get("i34_ingress_receipt_hash72"):
        raise Pass218I35StateError("P218_I35_MANIFEST_BINDING_RECEIPT_MISMATCH")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i35_receipt_hash72", "i35_hash216", "i35_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I35_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("i35_receipt_hash72"):
        raise Pass218I35StateError("P218_I35_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i34_ingress_receipt_hash72"])
        + str(value["manifest_bound_semantic_hash72"])
        + str(value["i35_receipt_hash72"])
    )
    if expected_hash216 != value.get("i35_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I35StateError("P218_I35_HASH216_INVALID")
    return value


class Pass218I35ManifestSemanticTransactionStore:
    """Durable nonverbatim I35 receipt plus closed-I3 restart snapshot."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.transaction_root = self.root / "transactions"
        self.state_path = self.root / "state.json"

    @staticmethod
    def _verify_snapshot(
        snapshot: Mapping[str, Any],
        receipt: Mapping[str, Any],
    ) -> dict[str, Any]:
        copied = _copy(dict(snapshot))
        restored = SourceTransaction.restore(
            copied,
            store=DeterministicStructuralStore(),
        )
        if restored.phase != TransactionPhase.CLOSED:
            raise Pass218I35StateError("P218_I35_I3_SNAPSHOT_NOT_CLOSED")
        if restored.transaction_id_hash72 != receipt["i3_transaction_id_hash72"]:
            raise Pass218I35StateError("P218_I35_I3_TRANSACTION_ID_MISMATCH")
        if copied.get("snapshot_hash72") != receipt["i3_transaction_snapshot_hash72"]:
            raise Pass218I35StateError("P218_I35_I3_SNAPSHOT_HASH_MISMATCH")
        candidate = restored.candidate_record
        if candidate.get("manifest_bound_semantic_hash72") != receipt["manifest_bound_semantic_hash72"]:
            raise Pass218I35StateError("P218_I35_SEMANTIC_SNAPSHOT_BINDING_MISMATCH")
        if candidate.get("manifest_binding") != receipt["manifest_binding"]:
            raise Pass218I35StateError("P218_I35_MANIFEST_SNAPSHOT_BINDING_MISMATCH")
        if candidate.get("genesis_seed_hash72") != receipt["manifest_genesis_seed_hash72"]:
            raise Pass218I35StateError("P218_I35_GENESIS_SNAPSHOT_BINDING_MISMATCH")
        closure = restored.closure_receipt
        if not isinstance(closure, Mapping):
            raise Pass218I35StateError("P218_I35_I3_CLOSURE_MISSING")
        for snapshot_field, receipt_field in (
            ("closure_hash72", "i3_closure_hash72"),
            ("structural_record_hash72", "i3_structural_record_hash72"),
            ("purge_receipt_hash72", "i3_purge_receipt_hash72"),
            ("memory_root_hash72", "i3_memory_root_hash72"),
            ("transaction_hash216", "i3_transaction_hash216"),
        ):
            if closure.get(snapshot_field) != receipt.get(receipt_field):
                raise Pass218I35StateError(
                    "P218_I35_I3_CLOSURE_BINDING_MISMATCH:" + snapshot_field
                )
        return copied

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I35_STATE_SCHEMA:
            raise Pass218I35StateError("P218_I35_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        expected_root = hash72_digest({"domain": PASS218_I35_STATE_SCHEMA}, body)
        if expected_root != state.get("state_root_hash72"):
            raise Pass218I35StateError("P218_I35_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        transaction_path = self.root / str(state.get("active_transaction_path", ""))
        if not receipt_path.is_file() or not transaction_path.is_file():
            raise Pass218I35StateError("P218_I35_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i35_receipt(_load_json(receipt_path))
        if receipt["i35_receipt_hash72"] != state.get("active_i35_receipt_hash72"):
            raise Pass218I35StateError("P218_I35_STATE_RECEIPT_MISMATCH")
        snapshot = self._verify_snapshot(_load_json(transaction_path), receipt)
        if snapshot["snapshot_hash72"] != state.get("active_transaction_snapshot_hash72"):
            raise Pass218I35StateError("P218_I35_STATE_TRANSACTION_MISMATCH")
        return receipt

    def active_transaction_snapshot(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        transaction_path = self.root / str(state["active_transaction_path"])
        return self._verify_snapshot(_load_json(transaction_path), receipt)

    def commit(
        self,
        receipt: Mapping[str, Any],
        transaction_snapshot: Mapping[str, Any],
    ) -> dict[str, Any]:
        checked = _verify_i35_receipt(receipt)
        snapshot = self._verify_snapshot(transaction_snapshot, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked:
                raise Pass218I35StateError("P218_I35_ACTIVE_BINDING_CONFLICT")
            persisted_snapshot = self.active_transaction_snapshot()
            if persisted_snapshot != snapshot:
                raise Pass218I35StateError("P218_I35_ACTIVE_TRANSACTION_CONFLICT")
            return existing

        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_name = f"{ordinal:08d}-{checked['i35_receipt_hash72']}.json"
        transaction_name = f"{checked['i3_transaction_id_hash72']}.json"
        receipt_path = self.receipt_root / receipt_name
        transaction_path = self.transaction_root / transaction_name

        if receipt_path.exists():
            if _load_json(receipt_path) != checked:
                raise Pass218I35StateError("P218_I35_RECEIPT_CONFLICT")
        else:
            _atomic_write_json(receipt_path, checked)
        if transaction_path.exists():
            if _load_json(transaction_path) != snapshot:
                raise Pass218I35StateError("P218_I35_TRANSACTION_SNAPSHOT_CONFLICT")
        else:
            _atomic_write_json(transaction_path, snapshot)

        state_body = {
            "schema": PASS218_I35_STATE_SCHEMA,
            "version": PASS218_I35_VERSION,
            "status": PASS218_I35_COMPLETE_STATUS,
            "i34_ingress_receipt_hash72": checked["i34_ingress_receipt_hash72"],
            "manifest_bound_semantic_hash72": checked["manifest_bound_semantic_hash72"],
            "i3_transaction_id_hash72": checked["i3_transaction_id_hash72"],
            "active_i35_receipt_hash72": checked["i35_receipt_hash72"],
            "active_transaction_snapshot_hash72": snapshot["snapshot_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_transaction_path": transaction_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest(
                {"domain": PASS218_I35_STATE_SCHEMA},
                state_body,
            ),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I35StateError("P218_I35_STATE_PERSIST_MISMATCH")
        return checked


class Pass218I35ManifestBoundSemanticSourceTransaction:
    """Bind frozen-I2 semantics to frozen I34 authority before one I3 transaction."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I35LifecycleProtocol,
        i34_store_root: str | os.PathLike[str],
        transaction_store_root: str | os.PathLike[str],
        manifest_genesis_seed_hash72: str | None,
        i34_store: Pass218I35I34StoreProtocol | None = None,
        i34_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        structural_store: DeterministicStructuralStore | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i34_store = (
            i34_store
            if i34_store is not None
            else Pass218I34ManifestSourceIngressStore(i34_store_root)
        )
        self.i34_status_provider = i34_status_provider
        self.manifest_genesis_seed_hash72 = manifest_genesis_seed_hash72
        self.structural_store = structural_store or DeterministicStructuralStore()
        self.store = Pass218I35ManifestSemanticTransactionStore(transaction_store_root)
        self.semantic_construction_count = 0
        self.i3_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _active_i34(self) -> dict[str, Any]:
        receipt = self.i34_store.active_record()
        if receipt is None:
            raise Pass218I35BindingError("P218_I35_I34_BINDING_REQUIRED")
        checked = _verify_i34_receipt(receipt)
        if self.i34_status_provider is not None:
            status = dict(self.i34_status_provider())
            if (
                status.get("manifest_bound_source_ready") is not True
                or status.get("binding_current") is not True
            ):
                raise Pass218I35BindingError("P218_I35_I34_BINDING_NOT_CURRENT")
            if status.get("active_ingress_receipt_hash72") != checked["ingress_receipt_hash72"]:
                raise Pass218I35BindingError("P218_I35_I34_STATUS_RECEIPT_MISMATCH")
        return checked

    def ingest(
        self,
        *,
        semantic_candidate: Any,
        source_bytes: bytes,
    ) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            genesis = self.manifest_genesis_seed_hash72
            if genesis is None:
                raise Pass218I35BindingError(
                    "P218_I35_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED"
                )
            if not validate_hash72(genesis):
                raise Pass218I35BindingError("P218_I35_MANIFEST_GENESIS_HASH72_INVALID")

            ingress = self._active_i34()
            observed_source_sha256 = sha256(source_bytes).hexdigest()
            base_candidate = _candidate_record(semantic_candidate)
            _verify_base_i2_candidate(
                base_candidate,
                ingress=ingress,
                manifest_genesis_seed_hash72=genesis,
                observed_source_sha256=observed_source_sha256,
                observed_source_byte_count=len(source_bytes),
            )
            enriched, binding, semantic_hash72 = _build_manifest_bound_candidate(
                base_candidate,
                ingress,
            )
            self.semantic_construction_count += 1

            existing = self.store.active_record()
            if existing is not None:
                if (
                    existing["i34_ingress_receipt_hash72"] != ingress["ingress_receipt_hash72"]
                    or existing["manifest_bound_semantic_hash72"] != semantic_hash72
                    or existing["i2_candidate_hash216"] != base_candidate["hash216"]
                    or existing["manifest_binding"] != binding
                ):
                    raise Pass218I35StateError("P218_I35_ACTIVE_BINDING_CONFLICT")
                self.last_error_code = None
                return existing

            try:
                transaction = SourceTransaction.begin(
                    enriched,
                    source_bytes,
                    store=self.structural_store,
                )
                self.i3_invocation_count += 1
                closure = transaction.commit_and_purge()
            except Pass218TransactionError as exc:
                raise Pass218I35TransactionError(
                    "P218_I35_I3_TRANSACTION_FAILED:" + str(exc)
                ) from exc

            if transaction.phase != TransactionPhase.CLOSED:
                raise Pass218I35TransactionError("P218_I35_I3_TRANSACTION_NOT_CLOSED")
            purge = transaction.purge_receipt
            if not isinstance(purge, Mapping):
                raise Pass218I35TransactionError("P218_I35_I3_PURGE_RECEIPT_MISSING")
            if (
                closure.get("managed_buffer_zeroized") is not True
                or closure.get("managed_buffer_cleared") is not True
                or purge.get("managed_buffer_zeroized") is not True
                or purge.get("managed_buffer_cleared") is not True
            ):
                raise Pass218I35TransactionError("P218_I35_I3_MANAGED_BUFFER_PURGE_INVALID")

            snapshot = transaction.snapshot()
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I35-SOURCE-TRANSACTION-VALIDATION-V1"},
                {
                    "i34_ingress_receipt_hash72": ingress["ingress_receipt_hash72"],
                    "manifest_bound_semantic_hash72": semantic_hash72,
                    "i2_candidate_hash216": base_candidate["hash216"],
                    "i3_transaction_id_hash72": transaction.transaction_id_hash72,
                    "i3_structural_record_hash72": closure["structural_record_hash72"],
                    "i3_purge_receipt_hash72": closure["purge_receipt_hash72"],
                    "i3_closure_hash72": closure["closure_hash72"],
                    "i3_transaction_hash216": closure["transaction_hash216"],
                    "i3_transaction_snapshot_hash72": snapshot["snapshot_hash72"],
                    "manifest_binding_propagated": True,
                    "semantic_construction_invoked": True,
                    "i3_source_transaction_invoked": True,
                    "later_pass218_authority_invoked": False,
                },
            )
            body = {
                "schema": PASS218_I35_RECEIPT_SCHEMA,
                "version": PASS218_I35_VERSION,
                "scope": PASS218_I35_SCOPE,
                "status": PASS218_I35_COMPLETE_STATUS,
                "i34_ingress_receipt_hash72": ingress["ingress_receipt_hash72"],
                "manifest_binding": binding,
                "manifest_genesis_seed_hash72": genesis,
                "manifest_bound_semantic_hash72": semantic_hash72,
                "i2_candidate_hash216": base_candidate["hash216"],
                "i2_hydration_hash72": base_candidate["hydration_hash72"],
                "i2_validation_hash72": base_candidate["validation_hash72"],
                "i3_transaction_id_hash72": transaction.transaction_id_hash72,
                "i3_structural_record_hash72": closure["structural_record_hash72"],
                "i3_purge_receipt_hash72": closure["purge_receipt_hash72"],
                "i3_memory_root_hash72": closure["memory_root_hash72"],
                "i3_closure_hash72": closure["closure_hash72"],
                "i3_transaction_hash216": closure["transaction_hash216"],
                "i3_transaction_snapshot_hash72": snapshot["snapshot_hash72"],
                "i35_validation_hash72": validation_hash72,
                "i34_ingress_bound": True,
                "manifest_binding_propagated": True,
                "semantic_construction_invoked": True,
                "semantic_candidate_nonverbatim": True,
                "i3_source_transaction_required": True,
                "i3_source_transaction_invoked": True,
                "i3_transaction_closed": True,
                "i3_managed_buffer_zeroized": True,
                "i3_managed_buffer_cleared": True,
                "structural_candidate_admitted_non_authoritatively": True,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
                "physical_memory_erasure_claimed": False,
                "external_request_buffer_erasure_claimed": False,
                "pass218_i4_staging_invoked": False,
                "pass218_i5_promotion_invoked": False,
                "pass218_i30_canonical_semantic_promotion_invoked": False,
                "pass218_i31_verbatim_purge_invoked": False,
                "pass218_i32_source_closure_invoked": False,
                "curriculum_cursor_advanced": False,
                "stage_advance_permitted": False,
                "vm81_authorization_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
            receipt_hash72 = hash72_digest({"domain": PASS218_I35_RECEIPT_SCHEMA}, body)
            receipt = {
                **body,
                "i35_receipt_hash72": receipt_hash72,
                "i35_hash216": ingress["ingress_receipt_hash72"] + semantic_hash72 + receipt_hash72,
                "i35_hash216_semantics": [
                    "I34_MANIFEST_BOUND_SOURCE_INGRESS_RECEIPT",
                    "MANIFEST_BOUND_I2_SEMANTIC_CANDIDATE",
                    "I35_I3_SOURCE_TRANSACTION_BINDING_RECEIPT",
                ],
            }
            persisted = self.store.commit(receipt, snapshot)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def closed_transaction_snapshot(self) -> dict[str, Any] | None:
        return self.store.active_transaction_snapshot()

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i34_ready = False
        i34_current = False
        active_i34_receipt_hash72: str | None = None
        try:
            ingress = self._active_i34()
            i34_ready = True
            i34_current = True
            active_i34_receipt_hash72 = str(ingress["ingress_receipt_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I35_STATUS_SCHEMA,
            "version": PASS218_I35_VERSION,
            "status": PASS218_I35_COMPLETE_STATUS if active is not None else PASS218_I35_PENDING_STATUS,
            "authoritative_curriculum_configured": self.manifest_genesis_seed_hash72 is not None,
            "manifest_genesis_seed_hash72": self.manifest_genesis_seed_hash72,
            "i34_manifest_bound_source_ready": i34_ready,
            "i34_binding_current": i34_current,
            "active_i34_ingress_receipt_hash72": active_i34_receipt_hash72,
            "active_i35_receipt_hash72": None if active is None else active["i35_receipt_hash72"],
            "manifest_bound_semantic_hash72": (
                None if active is None else active["manifest_bound_semantic_hash72"]
            ),
            "i3_transaction_id_hash72": (
                None if active is None else active["i3_transaction_id_hash72"]
            ),
            "i3_transaction_snapshot_hash72": (
                None if active is None else active["i3_transaction_snapshot_hash72"]
            ),
            "semantic_construction_count_current_process": self.semantic_construction_count,
            "i3_invocation_count_current_process": self.i3_invocation_count,
            "semantic_construction_invoked": active is not None or self.semantic_construction_count > 0,
            "i3_source_transaction_invoked": active is not None or self.i3_invocation_count > 0,
            "i3_transaction_closed": active is not None,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "pass218_i4_staging_invoked": False,
            "pass218_i5_promotion_invoked": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I35_COMPLETE_STATUS",
    "PASS218_I35_PENDING_STATUS",
    "PASS218_I35_RECEIPT_SCHEMA",
    "PASS218_I35_SCOPE",
    "PASS218_I35_STATE_SCHEMA",
    "PASS218_I35_STATUS_SCHEMA",
    "PASS218_I35_VERSION",
    "Pass218I35BindingError",
    "Pass218I35IngressError",
    "Pass218I35ManifestBoundSemanticSourceTransaction",
    "Pass218I35ManifestSemanticTransactionStore",
    "Pass218I35StateError",
    "Pass218I35TransactionError",
]
