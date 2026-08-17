"""Pass 218 Iteration 32 durable source-closure boundary.

I32 consumes only an exact successful I31 verbatim-purge receipt.  It verifies
that receipt and its Hash72/Hash216/gate-root identities, binds the closed
source to declared curriculum metadata, and writes one durable source-closure
receipt.  It deliberately does not advance the curriculum cursor: the later
advancement gate must compare this closure against the authoritative manifest
and current cursor before any ordinal or stage transition is permitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from threading import RLock
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import HASH72_ALPHABET, hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGE_RECEIPT_SCHEMA,
    PASS218_I31_PURGED_STATUS,
    Pass218I31PurgeStore,
)

PASS218_I32_CLOSURE_VERSION = "HHS-P218-I32-SOURCE-CLOSURE-V1"
PASS218_I32_CLOSURE_RECEIPT_SCHEMA = "HHS-P218-I32-SOURCE-CLOSURE-RECEIPT-V1"
PASS218_I32_MANIFEST_SCHEMA = "HHS-P218-I32-SOURCE-CLOSURE-MANIFEST-V1"
PASS218_I32_STATUS_SCHEMA = "HHS-P218-I32-SOURCE-CLOSURE-STATUS-V1"
PASS218_I32_PENDING_STATUS = "SOURCE_CLOSURE_PENDING"
PASS218_I32_CLOSED_STATUS = "SOURCE_CLOSED_PENDING_CURRICULUM_ADVANCE"
PASS218_I32_CLOSURE_SCOPE = "PASS218_I31_PURGE_RECEIPTED_SOURCE_CLOSURE"


class Pass218I32ClosureError(RuntimeError):
    """Base fail-closed I32 error."""


class Pass218I32ClosureValidationError(Pass218I32ClosureError):
    pass


class Pass218I32ClosureStateError(Pass218I32ClosureError):
    pass


class Pass218I32LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...
    def status(self) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I32ClosureValidationError("P218_I32_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        and all(symbol in HASH72_ALPHABET for symbol in value)
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _require_hash72(value: object, code: str) -> str:
    text = str(value or "")
    if not validate_hash72(text):
        raise Pass218I32ClosureValidationError(code)
    return text


def _require_text(value: object, code: str) -> str:
    text = str(value or "").strip()
    if not text or len(text) > 4096:
        raise Pass218I32ClosureValidationError(code)
    return text


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".p218-i32-", suffix=".tmp", dir=str(path.parent))
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
        raise Pass218I32ClosureValidationError(
            "P218_I32_PERSISTED_RECORD_UNREADABLE:" + path.name
        ) from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218I32ClosureValidationError(
            "P218_I32_PERSISTED_RECORD_NONCANONICAL:" + path.name
        )
    return value


@dataclass(frozen=True)
class Pass218I32ClosureRequest:
    expected_i31_purge_receipt_hash72: str
    expected_i31_purge_validation_hash72: str
    expected_i31_purge_gate_root_hash72: str
    expected_i31_purge_hash216: str
    expected_i30_promotion_receipt_hash72: str
    expected_promoted_object_hash72: str
    expected_canonical_root_hash72: str
    source_id: str
    source_sha256: str
    source_authority: str
    rights_class: str
    curriculum_identity_hash72: str
    curriculum_position: int
    source_stage: int
    previous_closure_hash72: str | None = None
    closure_scope: str = PASS218_I32_CLOSURE_SCOPE

    def validated(self) -> "Pass218I32ClosureRequest":
        if self.closure_scope != PASS218_I32_CLOSURE_SCOPE:
            raise Pass218I32ClosureValidationError("P218_I32_CLOSURE_SCOPE_INVALID")
        if not _valid_sha256(self.source_sha256):
            raise Pass218I32ClosureValidationError("P218_I32_SOURCE_SHA256_INVALID")
        if isinstance(self.curriculum_position, bool) or int(self.curriculum_position) < 0:
            raise Pass218I32ClosureValidationError("P218_I32_CURRICULUM_POSITION_INVALID")
        if isinstance(self.source_stage, bool) or int(self.source_stage) not in range(0, 7):
            raise Pass218I32ClosureValidationError("P218_I32_SOURCE_STAGE_INVALID")
        previous = self.previous_closure_hash72
        if previous is not None:
            previous = _require_hash72(previous, "P218_I32_PREVIOUS_CLOSURE_HASH72_INVALID")
        return Pass218I32ClosureRequest(
            expected_i31_purge_receipt_hash72=_require_hash72(
                self.expected_i31_purge_receipt_hash72,
                "P218_I32_EXPECTED_I31_PURGE_RECEIPT_HASH72_INVALID",
            ),
            expected_i31_purge_validation_hash72=_require_hash72(
                self.expected_i31_purge_validation_hash72,
                "P218_I32_EXPECTED_I31_PURGE_VALIDATION_HASH72_INVALID",
            ),
            expected_i31_purge_gate_root_hash72=_require_hash72(
                self.expected_i31_purge_gate_root_hash72,
                "P218_I32_EXPECTED_I31_PURGE_GATE_ROOT_HASH72_INVALID",
            ),
            expected_i31_purge_hash216=(
                self.expected_i31_purge_hash216
                if _valid_hash216(self.expected_i31_purge_hash216)
                else (_ for _ in ()).throw(
                    Pass218I32ClosureValidationError(
                        "P218_I32_EXPECTED_I31_PURGE_HASH216_INVALID"
                    )
                )
            ),
            expected_i30_promotion_receipt_hash72=_require_hash72(
                self.expected_i30_promotion_receipt_hash72,
                "P218_I32_EXPECTED_I30_PROMOTION_RECEIPT_HASH72_INVALID",
            ),
            expected_promoted_object_hash72=_require_hash72(
                self.expected_promoted_object_hash72,
                "P218_I32_EXPECTED_PROMOTED_OBJECT_HASH72_INVALID",
            ),
            expected_canonical_root_hash72=_require_hash72(
                self.expected_canonical_root_hash72,
                "P218_I32_EXPECTED_CANONICAL_ROOT_HASH72_INVALID",
            ),
            source_id=_require_text(self.source_id, "P218_I32_SOURCE_ID_INVALID"),
            source_sha256=self.source_sha256,
            source_authority=_require_text(
                self.source_authority, "P218_I32_SOURCE_AUTHORITY_INVALID"
            ),
            rights_class=_require_text(self.rights_class, "P218_I32_RIGHTS_CLASS_INVALID"),
            curriculum_identity_hash72=_require_hash72(
                self.curriculum_identity_hash72,
                "P218_I32_CURRICULUM_IDENTITY_HASH72_INVALID",
            ),
            curriculum_position=int(self.curriculum_position),
            source_stage=int(self.source_stage),
            previous_closure_hash72=previous,
            closure_scope=self.closure_scope,
        )


class Pass218I32ClosureStore:
    """Durable one-source closure store; it never mutates the curriculum cursor."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.closures = self.root / "closures"
        self.manifest_path = self.root / "manifest.json"
        self._lock = RLock()

    def _active_locked(self) -> tuple[dict[str, Any], dict[str, Any]] | None:
        if not self.manifest_path.exists():
            return None
        manifest = _read_canonical_json(self.manifest_path)
        if manifest.get("schema") != PASS218_I32_MANIFEST_SCHEMA:
            raise Pass218I32ClosureValidationError("P218_I32_MANIFEST_SCHEMA_INVALID")
        record_name = str(manifest.get("active_record") or "")
        if not record_name or Path(record_name).name != record_name:
            raise Pass218I32ClosureValidationError("P218_I32_MANIFEST_RECORD_INVALID")
        record = _read_canonical_json(self.closures / record_name)
        raw = _canonical_bytes(record)
        if sha256(raw).hexdigest() != manifest.get("record_sha256"):
            raise Pass218I32ClosureValidationError("P218_I32_RECORD_SHA256_MISMATCH")
        if record.get("closure_status") != PASS218_I32_CLOSED_STATUS:
            raise Pass218I32ClosureValidationError("P218_I32_RECORD_STATUS_INVALID")
        if record.get("source_closure_hash72") != manifest.get("source_closure_hash72"):
            raise Pass218I32ClosureValidationError("P218_I32_MANIFEST_CLOSURE_MISMATCH")
        return manifest, record

    def active_record(self) -> dict[str, Any] | None:
        with self._lock:
            active = self._active_locked()
            return None if active is None else _copy(active[1])

    def status(self) -> dict[str, Any]:
        with self._lock:
            active = self._active_locked()
            if active is None:
                return {
                    "closure_record_present": False,
                    "closure_status": PASS218_I32_PENDING_STATUS,
                    "closure_invoked": False,
                    "source_closed": False,
                    "curriculum_advance_permitted": False,
                    "curriculum_cursor_advanced": False,
                }
            manifest, record = active
            return {
                "closure_record_present": True,
                "closure_status": manifest["closure_status"],
                "closure_invoked": True,
                "source_closed": True,
                "source_closure_hash72": record["source_closure_hash72"],
                "closure_chain_root_hash72": record["closure_chain_root_hash72"],
                "source_id_hash72": record["source_id_hash72"],
                "curriculum_identity_hash72": record["curriculum_identity_hash72"],
                "curriculum_position": record["curriculum_position"],
                "previous_closure_hash72": record["previous_closure_hash72"],
                "curriculum_advance_permitted": False,
                "curriculum_cursor_advanced": False,
            }

    def commit(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        record = _copy(receipt)
        if record.get("schema") != PASS218_I32_CLOSURE_RECEIPT_SCHEMA:
            raise Pass218I32ClosureValidationError("P218_I32_CLOSURE_RECEIPT_SCHEMA_INVALID")
        if record.get("closure_invoked") is not True or record.get("source_closed") is not True:
            raise Pass218I32ClosureValidationError("P218_I32_CLOSURE_FLAGS_REQUIRED")
        if record.get("curriculum_advance_permitted") is not False:
            raise Pass218I32ClosureValidationError("P218_I32_ADVANCE_MUST_REMAIN_CLOSED")
        with self._lock:
            active = self._active_locked()
            if active is not None:
                existing = active[1]
                if existing.get("source_closure_hash72") == record.get("source_closure_hash72"):
                    return _copy(existing)
                raise Pass218I32ClosureStateError("P218_I32_SOURCE_ALREADY_CLOSED")
            raw = _canonical_bytes(record)
            digest = sha256(raw).hexdigest()
            name = f"closure-{digest}.json"
            _atomic_write(self.closures / name, raw)
            manifest = {
                "schema": PASS218_I32_MANIFEST_SCHEMA,
                "version": PASS218_I32_CLOSURE_VERSION,
                "active_record": name,
                "record_sha256": digest,
                "closure_status": PASS218_I32_CLOSED_STATUS,
                "source_closure_hash72": record["source_closure_hash72"],
                "closure_chain_root_hash72": record["closure_chain_root_hash72"],
                "curriculum_advance_permitted": False,
                "curriculum_cursor_advanced": False,
            }
            _atomic_write(self.manifest_path, _canonical_bytes(manifest))
            verified = self._active_locked()
            if verified is None or verified[1] != record:
                raise Pass218I32ClosureStateError("P218_I32_CLOSURE_MANIFEST_VERIFY_FAILED")
            return _copy(record)


class Pass218I32SourceCloser:
    """Verify I31 purge authority and seal one source without advancing curriculum."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I32LifecycleProtocol,
        i31_store_root: str | os.PathLike[str],
        closure_store_root: str | os.PathLike[str],
    ) -> None:
        self.lifecycle = lifecycle
        self.i31_store = Pass218I31PurgeStore(i31_store_root)
        self.store = Pass218I32ClosureStore(closure_store_root)
        self.close_count = 0
        self.last_source_closure_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _verify_i31(self, request: Pass218I32ClosureRequest) -> dict[str, Any]:
        record = self.i31_store.active_record()
        if record is None:
            raise Pass218I32ClosureValidationError("P218_I32_I31_PURGE_RECEIPT_REQUIRED")
        if record.get("schema") != PASS218_I31_PURGE_RECEIPT_SCHEMA:
            raise Pass218I32ClosureValidationError("P218_I32_I31_SUCCESS_RECEIPT_REQUIRED")
        if record.get("purge_status") != PASS218_I31_PURGED_STATUS:
            raise Pass218I32ClosureValidationError("P218_I32_I31_PURGE_STATUS_INVALID")

        required_true = (
            "durable_nonverbatim_store_verified",
            "verbatim_purge_invoked",
            "purge_confirmation_verified",
            "purge_receipt_issued",
            "managed_buffers_absent_after",
        )
        if any(record.get(field) is not True for field in required_true):
            raise Pass218I32ClosureValidationError("P218_I32_I31_PURGE_PROOF_INCOMPLETE")
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
        if any(record.get(field) is not False for field in required_false):
            raise Pass218I32ClosureValidationError("P218_I32_I31_AUTHORITY_DRIFT")

        expected_pairs = (
            ("purge_receipt_hash72", request.expected_i31_purge_receipt_hash72),
            ("purge_validation_hash72", request.expected_i31_purge_validation_hash72),
            ("purge_gate_root_hash72", request.expected_i31_purge_gate_root_hash72),
            ("purge_hash216", request.expected_i31_purge_hash216),
            ("i30_promotion_receipt_hash72", request.expected_i30_promotion_receipt_hash72),
            ("promoted_object_hash72", request.expected_promoted_object_hash72),
            ("canonical_root_hash72", request.expected_canonical_root_hash72),
        )
        for field, expected in expected_pairs:
            if record.get(field) != expected:
                raise Pass218I32ClosureValidationError("P218_I32_I31_IDENTITY_MISMATCH:" + field)

        receipt_body = {
            key: value
            for key, value in record.items()
            if key not in {
                "purge_receipt_hash72",
                "purge_hash216",
                "purge_hash216_semantics",
                "purge_gate_root_hash72",
            }
        }
        computed_receipt = hash72_digest(
            {"domain": "HHS-P218-I31-VERBATIM-PURGE-RECEIPT-V1"}, receipt_body
        )
        if computed_receipt != record["purge_receipt_hash72"]:
            raise Pass218I32ClosureValidationError("P218_I32_I31_PURGE_RECEIPT_REDERIVE_MISMATCH")
        computed_hash216 = (
            str(record["i30_promotion_hash72"])
            + str(record["purge_validation_hash72"])
            + str(record["purge_receipt_hash72"])
        )
        if computed_hash216 != record["purge_hash216"] or not _valid_hash216(computed_hash216):
            raise Pass218I32ClosureValidationError("P218_I32_I31_PURGE_HASH216_REDERIVE_MISMATCH")
        computed_gate = hash72_digest(
            {"domain": "HHS-P218-I31-PURGE-GATE-ROOT-V1"},
            {
                "canonical_root_hash72": record["canonical_root_hash72"],
                "promoted_object_hash72": record["promoted_object_hash72"],
                "purge_validation_hash72": record["purge_validation_hash72"],
                "purge_receipt_hash72": record["purge_receipt_hash72"],
                "purge_hash216": record["purge_hash216"],
            },
        )
        if computed_gate != record["purge_gate_root_hash72"]:
            raise Pass218I32ClosureValidationError("P218_I32_I31_PURGE_GATE_REDERIVE_MISMATCH")
        return record

    def close(self, request: Pass218I32ClosureRequest) -> dict[str, Any]:
        validated = request.validated()
        self.lifecycle.require_ingestion_ready()
        existing = self.store.active_record()
        if existing is not None:
            same = (
                existing.get("i31_purge_receipt_hash72")
                == validated.expected_i31_purge_receipt_hash72
                and existing.get("source_sha256") == validated.source_sha256
                and existing.get("curriculum_identity_hash72")
                == validated.curriculum_identity_hash72
                and existing.get("curriculum_position") == validated.curriculum_position
                and existing.get("previous_closure_hash72") == validated.previous_closure_hash72
            )
            if same:
                return existing
            raise Pass218I32ClosureStateError("P218_I32_PREVIOUS_SOURCE_CLOSURE_CONFLICT")

        try:
            purge = self._verify_i31(validated)
            source_id_hash72 = hash72_digest(
                {"domain": "HHS-P218-I32-SOURCE-IDENTITY-V1"},
                {
                    "source_id": validated.source_id,
                    "source_sha256": validated.source_sha256,
                    "source_authority": validated.source_authority,
                    "rights_class": validated.rights_class,
                },
            )
            source_binding_hash72 = hash72_digest(
                {"domain": "HHS-P218-I32-SOURCE-CURRICULUM-BINDING-V1"},
                {
                    "source_id_hash72": source_id_hash72,
                    "curriculum_identity_hash72": validated.curriculum_identity_hash72,
                    "curriculum_position": validated.curriculum_position,
                    "source_stage": validated.source_stage,
                    "previous_closure_hash72": validated.previous_closure_hash72,
                    "i31_purge_receipt_hash72": purge["purge_receipt_hash72"],
                    "canonical_root_hash72": purge["canonical_root_hash72"],
                },
            )
            closure_validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I32-SOURCE-CLOSURE-VALIDATION-V1"},
                {
                    "i31_purge_receipt_hash72": purge["purge_receipt_hash72"],
                    "i31_purge_gate_root_hash72": purge["purge_gate_root_hash72"],
                    "i31_purge_hash216": purge["purge_hash216"],
                    "source_binding_hash72": source_binding_hash72,
                    "promoted_object_hash72": purge["promoted_object_hash72"],
                    "canonical_root_hash72": purge["canonical_root_hash72"],
                    "purge_confirmation_verified": True,
                    "durable_nonverbatim_store_verified": True,
                    "curriculum_cursor_advanced": False,
                },
            )
            closure_body = {
                "schema": PASS218_I32_CLOSURE_RECEIPT_SCHEMA,
                "version": PASS218_I32_CLOSURE_VERSION,
                "closure_scope": PASS218_I32_CLOSURE_SCOPE,
                "closure_status": PASS218_I32_CLOSED_STATUS,
                "i31_purge_receipt_hash72": purge["purge_receipt_hash72"],
                "i31_purge_validation_hash72": purge["purge_validation_hash72"],
                "i31_purge_gate_root_hash72": purge["purge_gate_root_hash72"],
                "i31_purge_hash216": purge["purge_hash216"],
                "i30_promotion_receipt_hash72": purge["i30_promotion_receipt_hash72"],
                "i29_validation_hash72": purge["i29_validation_hash72"],
                "validated_hash216": purge["validated_hash216"],
                "promoted_object_hash72": purge["promoted_object_hash72"],
                "canonical_root_hash72": purge["canonical_root_hash72"],
                "candidate_sha256": purge["candidate_sha256"],
                "source_id": validated.source_id,
                "source_id_hash72": source_id_hash72,
                "source_sha256": validated.source_sha256,
                "source_authority": validated.source_authority,
                "rights_class": validated.rights_class,
                "source_binding_hash72": source_binding_hash72,
                "curriculum_identity_hash72": validated.curriculum_identity_hash72,
                "curriculum_position": validated.curriculum_position,
                "source_stage": validated.source_stage,
                "previous_closure_hash72": validated.previous_closure_hash72,
                "closure_validation_hash72": closure_validation_hash72,
                "purge_confirmation_verified": True,
                "durable_nonverbatim_store_verified": True,
                "source_binding_requires_curriculum_match_before_advance": True,
                "closure_invoked": True,
                "source_closed": True,
                "curriculum_advance_permitted": False,
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
            source_closure_hash72 = hash72_digest(
                {"domain": "HHS-P218-I32-SOURCE-CLOSURE-RECEIPT-V1"}, closure_body
            )
            closure_hash216 = (
                purge["purge_receipt_hash72"]
                + closure_validation_hash72
                + source_closure_hash72
            )
            if not _valid_hash216(closure_hash216):
                raise Pass218I32ClosureValidationError("P218_I32_CLOSURE_HASH216_INVALID")
            closure_chain_root_hash72 = hash72_digest(
                {"domain": "HHS-P218-I32-CLOSURE-CHAIN-ROOT-V1"},
                {
                    "previous_closure_hash72": validated.previous_closure_hash72,
                    "source_closure_hash72": source_closure_hash72,
                    "canonical_root_hash72": purge["canonical_root_hash72"],
                    "curriculum_identity_hash72": validated.curriculum_identity_hash72,
                    "curriculum_position": validated.curriculum_position,
                    "source_stage": validated.source_stage,
                },
            )
            completed = {
                **closure_body,
                "source_closure_hash72": source_closure_hash72,
                "closure_hash216": closure_hash216,
                "closure_hash216_semantics": [
                    "I31_PURGE_RECEIPT",
                    "I32_CLOSURE_VALIDATION",
                    "I32_SOURCE_CLOSURE_RECEIPT",
                ],
                "closure_chain_root_hash72": closure_chain_root_hash72,
            }
            committed = self.store.commit(completed)
            self.close_count += 1
            self.last_source_closure_hash72 = source_closure_hash72
            self.last_error_code = None
            return committed
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I32ClosureError):
                raise
            raise Pass218I32ClosureError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        lifecycle = self.lifecycle.status()
        purge = self.i31_store.status()
        closure = self.store.status()
        return {
            "schema": PASS218_I32_STATUS_SCHEMA,
            "version": PASS218_I32_CLOSURE_VERSION,
            "closure_scope": PASS218_I32_CLOSURE_SCOPE,
            "writer_authority_ready": bool(
                lifecycle.get("ingestion_enabled")
                and lifecycle.get("ownership_writer_authority", True)
            ),
            "i31_purge_status": purge.get("purge_status"),
            "i31_purge_receipt_issued": bool(purge.get("purge_receipt_issued")),
            "close_count": self.close_count,
            "last_source_closure_hash72": self.last_source_closure_hash72,
            "i32_error_code": self.last_error_code,
            **closure,
            "curriculum_advance_permitted": False,
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


__all__ = [
    "PASS218_I32_CLOSED_STATUS",
    "PASS218_I32_CLOSURE_RECEIPT_SCHEMA",
    "PASS218_I32_CLOSURE_SCOPE",
    "PASS218_I32_CLOSURE_VERSION",
    "PASS218_I32_PENDING_STATUS",
    "PASS218_I32_STATUS_SCHEMA",
    "Pass218I32ClosureError",
    "Pass218I32ClosureRequest",
    "Pass218I32ClosureStateError",
    "Pass218I32ClosureStore",
    "Pass218I32ClosureValidationError",
    "Pass218I32SourceCloser",
]
