"""Pass 218 Iteration 31 verbatim-purge confirmation and purge receipt.

I31 consumes only the durable I30 atomic semantic promotion. It verifies the
promoted object, candidate commit, generation, manifest, and retained-artifact
surface before closing the verbatim-purge gate. Runtime-managed transient
buffers are zeroized and cleared when present; when none remain, the gate emits
an explicit managed-buffer absence proof instead of pretending that bytes were
erased.

The receipt is limited to HHS-managed runtime surfaces. It never claims physical
RAM scrubbing, filesystem-cache erasure, or deletion of external source storage.
If an exact I30 promotion is bound but purge confirmation fails, I31 durably
quarantines the promotion and does not issue a purge receipt or permit silent
curriculum advancement.
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
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PENDING_PURGE_STATUS,
    PASS218_I30_PROMOTED_OBJECT_SCHEMA,
    PASS218_I30_PROMOTION_RECEIPT_SCHEMA,
    Pass218I30AtomicSemanticStore,
)

PASS218_I31_PURGE_VERSION = "HHS-P218-I31-VERBATIM-PURGE-RECEIPT-V1"
PASS218_I31_PURGE_RECEIPT_SCHEMA = "HHS-P218-I31-VERBATIM-PURGE-RECEIPT-V1"
PASS218_I31_QUARANTINE_SCHEMA = "HHS-P218-I31-PURGE-QUARANTINE-V1"
PASS218_I31_STATUS_SCHEMA = "HHS-P218-I31-VERBATIM-PURGE-STATUS-V1"
PASS218_I31_MANIFEST_SCHEMA = "HHS-P218-I31-PURGE-MANIFEST-V1"
PASS218_I31_PURGED_STATUS = "VERBATIM_PURGE_RECEIPTED_PENDING_CLOSURE"
PASS218_I31_QUARANTINED_STATUS = "QUARANTINED_PURGE_CONFIRMATION_FAILED"
PASS218_I31_PENDING_STATUS = "PENDING_VERBATIM_PURGE"
PASS218_I31_PURGE_SCOPE = "PASS218_I30_PROMOTED_SEMANTIC_VERBATIM_PURGE"


class Pass218I31PurgeError(RuntimeError):
    """Base fail-closed I31 error."""


class Pass218I31PurgeValidationError(Pass218I31PurgeError):
    pass


class Pass218I31PurgeStateError(Pass218I31PurgeError):
    pass


class Pass218I31PurgeConfirmationError(Pass218I31PurgeError):
    pass


class Pass218I31LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...
    def status(self) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I31PurgeValidationError("P218_I31_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        raise Pass218I31PurgeValidationError(code)
    return text


_FORBIDDEN_RETAINED_KEYS = frozenset(
    {
        "source_text",
        "source_bytes",
        "raw_source",
        "raw_source_text",
        "raw_bytes",
        "raw_text",
        "source_content",
        "raw_content",
        "verbatim_source",
        "verbatim_text",
        "verbatim_content",
        "source_passage",
        "source_excerpt",
        "paragraph_text",
        "full_text",
        "managed_buffer",
        "managed_buffer_b64",
        "retained_token_stream",
        "token_stream",
        "source_token_stream",
    }
)
_FALSE_RETENTION_FLAGS = frozenset(
    {
        "verbatim_source_retained",
        "verbatim_corpus_source_retained",
        "source_text_retained",
        "source_token_stream_retained",
    }
)


def _reject_retained_source_surface(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in _FORBIDDEN_RETAINED_KEYS and child not in (None, "", [], {}):
                raise Pass218I31PurgeConfirmationError(
                    "P218_I31_VERBATIM_RETAINED_FIELD:" + str(key)
                )
            if normalized in _FALSE_RETENTION_FLAGS and child is not False:
                raise Pass218I31PurgeConfirmationError(
                    "P218_I31_VERBATIM_RETENTION_FLAG:" + str(key)
                )
            _reject_retained_source_surface(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_retained_source_surface(child)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".p218-i31-", suffix=".tmp", dir=str(path.parent))
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
        raise Pass218I31PurgeConfirmationError(
            "P218_I31_PERSISTED_RECORD_UNREADABLE:" + path.name
        ) from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218I31PurgeConfirmationError(
            "P218_I31_PERSISTED_RECORD_NONCANONICAL:" + path.name
        )
    _reject_retained_source_surface(value)
    return value


@dataclass(frozen=True)
class Pass218I31PurgeRequest:
    expected_i30_promotion_receipt_hash72: str
    expected_i30_promotion_hash72: str
    expected_promoted_object_hash72: str
    expected_canonical_root_hash72: str
    expected_i29_validation_hash72: str
    purge_scope: str = PASS218_I31_PURGE_SCOPE

    def validated(self) -> "Pass218I31PurgeRequest":
        if self.purge_scope != PASS218_I31_PURGE_SCOPE:
            raise Pass218I31PurgeValidationError("P218_I31_PURGE_SCOPE_INVALID")
        return Pass218I31PurgeRequest(
            expected_i30_promotion_receipt_hash72=_require_hash72(
                self.expected_i30_promotion_receipt_hash72,
                "P218_I31_EXPECTED_PROMOTION_RECEIPT_HASH72_INVALID",
            ),
            expected_i30_promotion_hash72=_require_hash72(
                self.expected_i30_promotion_hash72,
                "P218_I31_EXPECTED_PROMOTION_HASH72_INVALID",
            ),
            expected_promoted_object_hash72=_require_hash72(
                self.expected_promoted_object_hash72,
                "P218_I31_EXPECTED_PROMOTED_OBJECT_HASH72_INVALID",
            ),
            expected_canonical_root_hash72=_require_hash72(
                self.expected_canonical_root_hash72,
                "P218_I31_EXPECTED_CANONICAL_ROOT_HASH72_INVALID",
            ),
            expected_i29_validation_hash72=_require_hash72(
                self.expected_i29_validation_hash72,
                "P218_I31_EXPECTED_I29_VALIDATION_HASH72_INVALID",
            ),
            purge_scope=self.purge_scope,
        )


class Pass218I31ManagedBufferRegistry:
    """Non-persistent registry for acquisition buffers owned by the runtime."""

    def __init__(self) -> None:
        self._buffers: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def register(
        self,
        buffer_id: str,
        *,
        promotion_receipt_hash72: str,
        source_sha256: str,
        buffer: bytearray,
    ) -> None:
        identity = str(buffer_id).strip()
        if not identity or "/" in identity or "\\" in identity:
            raise Pass218I31PurgeValidationError("P218_I31_BUFFER_ID_INVALID")
        _require_hash72(
            promotion_receipt_hash72,
            "P218_I31_BUFFER_PROMOTION_RECEIPT_HASH72_INVALID",
        )
        if not _valid_sha256(source_sha256):
            raise Pass218I31PurgeValidationError("P218_I31_BUFFER_SOURCE_SHA256_INVALID")
        if not isinstance(buffer, bytearray):
            raise Pass218I31PurgeValidationError("P218_I31_MANAGED_BUFFER_TYPE_INVALID")
        with self._lock:
            if identity in self._buffers:
                raise Pass218I31PurgeStateError("P218_I31_MANAGED_BUFFER_DUPLICATE")
            self._buffers[identity] = {
                "promotion_receipt_hash72": promotion_receipt_hash72,
                "source_sha256": source_sha256,
                "buffer": buffer,
            }

    def count(self) -> int:
        with self._lock:
            return len(self._buffers)

    def purge_bound(self, promotion_receipt_hash72: str) -> dict[str, Any]:
        with self._lock:
            conflicting = [
                key
                for key, row in self._buffers.items()
                if row["promotion_receipt_hash72"] != promotion_receipt_hash72
            ]
            if conflicting:
                raise Pass218I31PurgeConfirmationError(
                    "P218_I31_MANAGED_BUFFER_BINDING_CONFLICT"
                )
            count_before = len(self._buffers)
            witnesses: list[dict[str, Any]] = []
            for buffer_id in sorted(self._buffers):
                row = self._buffers[buffer_id]
                managed = row["buffer"]
                byte_count = len(managed)
                for index in range(byte_count):
                    managed[index] = 0
                zeroized = all(value == 0 for value in managed)
                zeroized_sha256 = sha256(bytes(managed)).hexdigest()
                managed.clear()
                cleared = len(managed) == 0
                witnesses.append(
                    {
                        "buffer_id_hash72": hash72_digest(
                            {"domain": "HHS-P218-I31-MANAGED-BUFFER-ID-V1"},
                            {
                                "buffer_id": buffer_id,
                                "source_sha256": row["source_sha256"],
                                "promotion_receipt_hash72": promotion_receipt_hash72,
                            },
                        ),
                        "source_sha256": row["source_sha256"],
                        "source_byte_count": byte_count,
                        "managed_buffer_zeroized": zeroized,
                        "zeroized_buffer_sha256": zeroized_sha256,
                        "managed_buffer_cleared": cleared,
                        "managed_buffer_length_after": len(managed),
                    }
                )
            self._buffers.clear()
            if any(
                witness["managed_buffer_zeroized"] is not True
                or witness["managed_buffer_cleared"] is not True
                for witness in witnesses
            ):
                raise Pass218I31PurgeConfirmationError("P218_I31_MANAGED_BUFFER_PURGE_FAILED")
            return {
                "managed_buffer_count_before": count_before,
                "managed_buffer_count_after": len(self._buffers),
                "managed_buffers_absent_before": count_before == 0,
                "managed_buffers_absent_after": len(self._buffers) == 0,
                "managed_buffer_witnesses": witnesses,
            }


class Pass218I31PurgeStore:
    """Durable terminal record for I31 success or fail-closed quarantine."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipts = self.root / "receipts"
        self.quarantine = self.root / "quarantine"
        self.manifest_path = self.root / "manifest.json"
        self._lock = RLock()

    def _active_locked(self) -> tuple[dict[str, Any], dict[str, Any]] | None:
        if not self.manifest_path.exists():
            return None
        manifest = _read_canonical_json(self.manifest_path)
        if manifest.get("schema") != PASS218_I31_MANIFEST_SCHEMA:
            raise Pass218I31PurgeConfirmationError("P218_I31_MANIFEST_SCHEMA_INVALID")
        record_name = str(manifest.get("active_record") or "")
        if not record_name or Path(record_name).name != record_name:
            raise Pass218I31PurgeConfirmationError("P218_I31_MANIFEST_RECORD_INVALID")
        kind = manifest.get("record_kind")
        directory = self.receipts if kind == "PURGE_RECEIPT" else self.quarantine
        record_path = directory / record_name
        record = _read_canonical_json(record_path)
        raw = _canonical_bytes(record)
        if sha256(raw).hexdigest() != manifest.get("record_sha256"):
            raise Pass218I31PurgeConfirmationError("P218_I31_RECORD_SHA256_MISMATCH")
        if record.get("purge_status") != manifest.get("purge_status"):
            raise Pass218I31PurgeConfirmationError("P218_I31_MANIFEST_STATUS_MISMATCH")
        return manifest, record

    def status(self) -> dict[str, Any]:
        with self._lock:
            active = self._active_locked()
            if active is None:
                return {
                    "purge_record_present": False,
                    "purge_status": PASS218_I31_PENDING_STATUS,
                    "purge_receipt_issued": False,
                    "quarantined": False,
                    "curriculum_advance_permitted": False,
                }
            manifest, record = active
            return {
                "purge_record_present": True,
                "purge_status": manifest["purge_status"],
                "purge_receipt_issued": bool(record.get("purge_receipt_issued")),
                "quarantined": bool(record.get("quarantined")),
                "i30_promotion_receipt_hash72": record.get(
                    "i30_promotion_receipt_hash72"
                ),
                "promoted_object_hash72": record.get("promoted_object_hash72"),
                "purge_receipt_hash72": record.get("purge_receipt_hash72"),
                "quarantine_hash72": record.get("quarantine_hash72"),
                "purge_gate_root_hash72": record.get("purge_gate_root_hash72"),
                "curriculum_advance_permitted": False,
            }

    def active_record(self) -> dict[str, Any] | None:
        with self._lock:
            active = self._active_locked()
            return None if active is None else _copy(active[1])

    def commit_success(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        record = _copy(receipt)
        if record.get("schema") != PASS218_I31_PURGE_RECEIPT_SCHEMA:
            raise Pass218I31PurgeValidationError("P218_I31_PURGE_RECEIPT_SCHEMA_INVALID")
        if record.get("purge_receipt_issued") is not True:
            raise Pass218I31PurgeValidationError("P218_I31_PURGE_RECEIPT_FLAG_REQUIRED")
        with self._lock:
            active = self._active_locked()
            if active is not None:
                existing = active[1]
                if (
                    existing.get("schema") == PASS218_I31_PURGE_RECEIPT_SCHEMA
                    and existing.get("i30_promotion_receipt_hash72")
                    == record.get("i30_promotion_receipt_hash72")
                    and existing.get("purge_receipt_hash72")
                    == record.get("purge_receipt_hash72")
                ):
                    return _copy(existing)
                raise Pass218I31PurgeStateError("P218_I31_PURGE_STORE_ALREADY_TERMINAL")
            raw = _canonical_bytes(record)
            digest = sha256(raw).hexdigest()
            name = f"purge-{digest}.json"
            _atomic_write(self.receipts / name, raw)
            manifest = {
                "schema": PASS218_I31_MANIFEST_SCHEMA,
                "version": PASS218_I31_PURGE_VERSION,
                "record_kind": "PURGE_RECEIPT",
                "active_record": name,
                "record_sha256": digest,
                "purge_status": PASS218_I31_PURGED_STATUS,
                "i30_promotion_receipt_hash72": record[
                    "i30_promotion_receipt_hash72"
                ],
                "purge_receipt_hash72": record["purge_receipt_hash72"],
                "purge_gate_root_hash72": record["purge_gate_root_hash72"],
                "curriculum_advance_permitted": False,
            }
            _atomic_write(self.manifest_path, _canonical_bytes(manifest))
            verified = self._active_locked()
            if verified is None or verified[1] != record:
                raise Pass218I31PurgeStateError("P218_I31_PURGE_MANIFEST_VERIFY_FAILED")
            return _copy(record)

    def commit_quarantine(self, record: Mapping[str, Any]) -> dict[str, Any]:
        quarantine_record = _copy(record)
        if quarantine_record.get("schema") != PASS218_I31_QUARANTINE_SCHEMA:
            raise Pass218I31PurgeValidationError("P218_I31_QUARANTINE_SCHEMA_INVALID")
        with self._lock:
            active = self._active_locked()
            if active is not None:
                existing = active[1]
                if (
                    existing.get("schema") == PASS218_I31_QUARANTINE_SCHEMA
                    and existing.get("i30_promotion_receipt_hash72")
                    == quarantine_record.get("i30_promotion_receipt_hash72")
                ):
                    return _copy(existing)
                raise Pass218I31PurgeStateError("P218_I31_PURGE_STORE_ALREADY_TERMINAL")
            raw = _canonical_bytes(quarantine_record)
            digest = sha256(raw).hexdigest()
            name = f"quarantine-{digest}.json"
            _atomic_write(self.quarantine / name, raw)
            manifest = {
                "schema": PASS218_I31_MANIFEST_SCHEMA,
                "version": PASS218_I31_PURGE_VERSION,
                "record_kind": "QUARANTINE",
                "active_record": name,
                "record_sha256": digest,
                "purge_status": PASS218_I31_QUARANTINED_STATUS,
                "i30_promotion_receipt_hash72": quarantine_record[
                    "i30_promotion_receipt_hash72"
                ],
                "purge_receipt_hash72": None,
                "purge_gate_root_hash72": None,
                "curriculum_advance_permitted": False,
            }
            _atomic_write(self.manifest_path, _canonical_bytes(manifest))
            verified = self._active_locked()
            if verified is None or verified[1] != quarantine_record:
                raise Pass218I31PurgeStateError("P218_I31_QUARANTINE_MANIFEST_VERIFY_FAILED")
            return _copy(quarantine_record)


class Pass218I31VerbatimPurger:
    """Verify frozen I30 durability, purge managed buffers, then receipt or quarantine."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I31LifecycleProtocol,
        i30_store_root: str | os.PathLike[str],
        purge_store_root: str | os.PathLike[str],
        managed_buffers: Pass218I31ManagedBufferRegistry | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i30_store = Pass218I30AtomicSemanticStore(i30_store_root)
        self.store = Pass218I31PurgeStore(purge_store_root)
        self.managed_buffers = managed_buffers or Pass218I31ManagedBufferRegistry()
        self.purge_count = 0
        self.last_purge_receipt_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _verify_i30_persistence(
        self,
        request: Pass218I31PurgeRequest,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        status = self.i30_store.status()
        active = self.i30_store.active_generation()
        if active is None or status.get("promotion_present") is not True:
            raise Pass218I31PurgeValidationError("P218_I31_I30_PROMOTION_REQUIRED")
        receipt = active.get("promotion_receipt")
        promoted = active.get("promoted_object")
        if not isinstance(receipt, Mapping) or not isinstance(promoted, Mapping):
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_GENERATION_CONTENT_INVALID")
        if receipt.get("schema") != PASS218_I30_PROMOTION_RECEIPT_SCHEMA:
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_RECEIPT_SCHEMA_INVALID")
        if receipt.get("promotion_status") != PASS218_I30_PENDING_PURGE_STATUS:
            raise Pass218I31PurgeValidationError("P218_I31_I30_PROMOTION_STATUS_INVALID")
        if receipt.get("purge_status") != PASS218_I31_PENDING_STATUS:
            raise Pass218I31PurgeValidationError("P218_I31_I30_PURGE_NOT_PENDING")
        if receipt.get("purge_receipt_issued") is not False:
            raise Pass218I31PurgeValidationError("P218_I31_I30_PURGE_RECEIPT_ALREADY_ISSUED")
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
        if any(receipt.get(field) is not True for field in required_true):
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_DURABILITY_INCOMPLETE")
        required_false = (
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
        if any(receipt.get(field) is not False for field in required_false):
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_AUTHORITY_DRIFT")

        if receipt.get("promotion_receipt_hash72") != request.expected_i30_promotion_receipt_hash72:
            raise Pass218I31PurgeValidationError("P218_I31_EXPECTED_PROMOTION_RECEIPT_MISMATCH")
        if receipt.get("promotion_hash72") != request.expected_i30_promotion_hash72:
            raise Pass218I31PurgeValidationError("P218_I31_EXPECTED_PROMOTION_HASH_MISMATCH")
        if receipt.get("promoted_object_hash72") != request.expected_promoted_object_hash72:
            raise Pass218I31PurgeValidationError("P218_I31_EXPECTED_PROMOTED_OBJECT_MISMATCH")
        if receipt.get("target_root_after_hash72") != request.expected_canonical_root_hash72:
            raise Pass218I31PurgeValidationError("P218_I31_EXPECTED_CANONICAL_ROOT_MISMATCH")
        if receipt.get("i29_validation_hash72") != request.expected_i29_validation_hash72:
            raise Pass218I31PurgeValidationError("P218_I31_EXPECTED_I29_VALIDATION_MISMATCH")
        if status.get("canonical_root_hash72") != request.expected_canonical_root_hash72:
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_CANONICAL_ROOT_MISMATCH")

        if promoted.get("schema") != PASS218_I30_PROMOTED_OBJECT_SCHEMA:
            raise Pass218I31PurgeConfirmationError("P218_I31_PROMOTED_OBJECT_SCHEMA_INVALID")
        promoted_body = {
            key: value
            for key, value in promoted.items()
            if key != "promoted_object_hash72"
        }
        promoted_hash72 = hash72_digest(
            {"domain": "HHS-P218-I30-PROMOTED-SEMANTIC-OBJECT-V1"}, promoted_body
        )
        if promoted_hash72 != request.expected_promoted_object_hash72:
            raise Pass218I31PurgeConfirmationError("P218_I31_PROMOTED_OBJECT_HASH_MISMATCH")
        _reject_retained_source_surface(active)

        candidate_name = str(receipt.get("candidate_filename") or "")
        if not candidate_name or Path(candidate_name).name != candidate_name:
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_CANDIDATE_NAME_INVALID")
        candidate_path = self.i30_store.candidates / candidate_name
        if not candidate_path.is_file():
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_CANDIDATE_MISSING")
        raw_candidate = candidate_path.read_bytes()
        if sha256(raw_candidate).hexdigest() != receipt.get("candidate_sha256"):
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_CANDIDATE_SHA256_MISMATCH")
        candidate = _read_canonical_json(candidate_path)
        if candidate.get("promoted_object_hash72") != request.expected_promoted_object_hash72:
            raise Pass218I31PurgeConfirmationError("P218_I31_I30_CANDIDATE_OBJECT_MISMATCH")

        allowed_files: list[str] = []
        for path in sorted(self.i30_store.root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(self.i30_store.root).as_posix()
            parts = Path(relative).parts
            allowed = (
                relative == "manifest.json"
                or (
                    len(parts) == 2
                    and parts[0] in {"candidates", "generations"}
                    and parts[1].endswith(".json")
                )
            )
            if not allowed:
                raise Pass218I31PurgeConfirmationError(
                    "P218_I31_UNEXPECTED_I30_PERSISTED_FILE"
                )
            _read_canonical_json(path)
            allowed_files.append(relative)

        inventory_hash72 = hash72_digest(
            {"domain": "HHS-P218-I31-I30-PERSISTED-INVENTORY-V1"}, allowed_files
        )
        durability_witness_hash72 = hash72_digest(
            {"domain": "HHS-P218-I31-I30-DURABILITY-WITNESS-V1"},
            {
                "i30_promotion_receipt_hash72": receipt["promotion_receipt_hash72"],
                "i30_promotion_hash72": receipt["promotion_hash72"],
                "promoted_object_hash72": receipt["promoted_object_hash72"],
                "canonical_root_hash72": status["canonical_root_hash72"],
                "candidate_sha256": receipt["candidate_sha256"],
                "persisted_inventory_hash72": inventory_hash72,
                "candidate_commit_verified": True,
                "atomic_manifest_swap_verified": True,
                "durable_nonverbatim_store_verified": True,
            },
        )
        return _copy(receipt), _copy(promoted), {
            "persisted_inventory": allowed_files,
            "persisted_inventory_hash72": inventory_hash72,
            "durability_witness_hash72": durability_witness_hash72,
        }

    def _quarantine(
        self,
        *,
        receipt: Mapping[str, Any],
        reason_code: str,
        buffer_result: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        body = {
            "schema": PASS218_I31_QUARANTINE_SCHEMA,
            "version": PASS218_I31_PURGE_VERSION,
            "purge_status": PASS218_I31_QUARANTINED_STATUS,
            "i30_promotion_receipt_hash72": receipt["promotion_receipt_hash72"],
            "i30_promotion_hash72": receipt["promotion_hash72"],
            "promoted_object_hash72": receipt["promoted_object_hash72"],
            "canonical_root_hash72": receipt["target_root_after_hash72"],
            "reason_code": reason_code,
            "managed_buffer_result": _copy(buffer_result) if buffer_result is not None else None,
            "verbatim_purge_invoked": True,
            "purge_confirmation_verified": False,
            "purge_receipt_issued": False,
            "quarantined": True,
            "curriculum_advance_permitted": False,
            "closure_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "physical_memory_erasure_claimed": False,
            "external_source_storage_erasure_claimed": False,
            "authoritative_float_weights_created": False,
        }
        body["quarantine_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I31-PURGE-QUARANTINE-V1"}, body
        )
        return self.store.commit_quarantine(body)

    def purge(
        self,
        request: Pass218I31PurgeRequest,
        *,
        force_confirmation_failure: bool = False,
    ) -> dict[str, Any]:
        validated = request.validated()
        self.lifecycle.require_ingestion_ready()

        existing = self.store.active_record()
        if existing is not None:
            if existing.get("schema") == PASS218_I31_PURGE_RECEIPT_SCHEMA:
                if (
                    existing.get("i30_promotion_receipt_hash72")
                    == validated.expected_i30_promotion_receipt_hash72
                    and existing.get("promoted_object_hash72")
                    == validated.expected_promoted_object_hash72
                    and existing.get("canonical_root_hash72")
                    == validated.expected_canonical_root_hash72
                ):
                    return _copy(existing)
                raise Pass218I31PurgeStateError("P218_I31_PREVIOUS_PURGE_RECEIPT_CONFLICT")
            raise Pass218I31PurgeStateError(
                "P218_I31_QUARANTINED_REQUIRES_EXPLICIT_RECOVERY"
            )

        receipt, promoted, durability = self._verify_i30_persistence(validated)
        buffer_result: dict[str, Any] | None = None
        try:
            buffer_result = self.managed_buffers.purge_bound(
                validated.expected_i30_promotion_receipt_hash72
            )
            if buffer_result["managed_buffers_absent_after"] is not True:
                raise Pass218I31PurgeConfirmationError(
                    "P218_I31_MANAGED_BUFFER_ABSENCE_NOT_CONFIRMED"
                )
            if force_confirmation_failure:
                raise Pass218I31PurgeConfirmationError(
                    "P218_I31_INJECTED_PURGE_CONFIRMATION_FAILURE"
                )

            purge_mode = (
                "MANAGED_BUFFER_ABSENCE_PROOF"
                if buffer_result["managed_buffer_count_before"] == 0
                else "MANAGED_BUFFER_ZEROIZE_AND_CLEAR"
            )
            purge_validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I31-PURGE-VALIDATION-V1"},
                {
                    "i30_promotion_receipt_hash72": receipt[
                        "promotion_receipt_hash72"
                    ],
                    "promoted_object_hash72": promoted["promoted_object_hash72"],
                    "durability_witness_hash72": durability[
                        "durability_witness_hash72"
                    ],
                    "persisted_inventory_hash72": durability[
                        "persisted_inventory_hash72"
                    ],
                    "purge_mode": purge_mode,
                    "managed_buffer_count_before": buffer_result[
                        "managed_buffer_count_before"
                    ],
                    "managed_buffer_count_after": buffer_result[
                        "managed_buffer_count_after"
                    ],
                    "managed_buffers_absent_after": True,
                    "durable_nonverbatim_store_verified": True,
                    "physical_memory_erasure_claimed": False,
                },
            )
            receipt_body = {
                "schema": PASS218_I31_PURGE_RECEIPT_SCHEMA,
                "version": PASS218_I31_PURGE_VERSION,
                "purge_scope": PASS218_I31_PURGE_SCOPE,
                "purge_status": PASS218_I31_PURGED_STATUS,
                "i30_promotion_receipt_hash72": receipt[
                    "promotion_receipt_hash72"
                ],
                "i30_promotion_hash72": receipt["promotion_hash72"],
                "i29_validation_hash72": receipt["i29_validation_hash72"],
                "validated_hash216": receipt["validated_hash216"],
                "promoted_object_hash72": promoted["promoted_object_hash72"],
                "canonical_root_hash72": receipt["target_root_after_hash72"],
                "candidate_sha256": receipt["candidate_sha256"],
                "durability_witness_hash72": durability[
                    "durability_witness_hash72"
                ],
                "persisted_inventory_hash72": durability[
                    "persisted_inventory_hash72"
                ],
                "purge_validation_hash72": purge_validation_hash72,
                "purge_mode": purge_mode,
                "managed_buffer_count_before": buffer_result[
                    "managed_buffer_count_before"
                ],
                "managed_buffer_count_after": buffer_result[
                    "managed_buffer_count_after"
                ],
                "managed_buffers_absent_before": buffer_result[
                    "managed_buffers_absent_before"
                ],
                "managed_buffers_absent_after": True,
                "managed_buffer_zeroization_performed": (
                    buffer_result["managed_buffer_count_before"] > 0
                ),
                "managed_buffer_witnesses": buffer_result["managed_buffer_witnesses"],
                "durable_nonverbatim_store_verified": True,
                "verbatim_purge_invoked": True,
                "purge_confirmation_verified": True,
                "purge_receipt_issued": True,
                "quarantined": False,
                "curriculum_advance_permitted": False,
                "closure_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "physical_memory_erasure_claimed": False,
                "external_source_storage_erasure_claimed": False,
                "authoritative_float_weights_created": False,
            }
            purge_receipt_hash72 = hash72_digest(
                {"domain": "HHS-P218-I31-VERBATIM-PURGE-RECEIPT-V1"}, receipt_body
            )
            purge_hash216 = (
                receipt["promotion_hash72"]
                + purge_validation_hash72
                + purge_receipt_hash72
            )
            if not _valid_hash216(purge_hash216):
                raise Pass218I31PurgeConfirmationError("P218_I31_PURGE_HASH216_INVALID")
            purge_gate_root_hash72 = hash72_digest(
                {"domain": "HHS-P218-I31-PURGE-GATE-ROOT-V1"},
                {
                    "canonical_root_hash72": receipt["target_root_after_hash72"],
                    "promoted_object_hash72": promoted["promoted_object_hash72"],
                    "purge_validation_hash72": purge_validation_hash72,
                    "purge_receipt_hash72": purge_receipt_hash72,
                    "purge_hash216": purge_hash216,
                },
            )
            completed = {
                **receipt_body,
                "purge_receipt_hash72": purge_receipt_hash72,
                "purge_hash216": purge_hash216,
                "purge_hash216_semantics": [
                    "I30_ATOMIC_PROMOTION",
                    "I31_PURGE_VALIDATION",
                    "I31_PURGE_RECEIPT",
                ],
                "purge_gate_root_hash72": purge_gate_root_hash72,
            }
            committed = self.store.commit_success(completed)
            self.purge_count += 1
            self.last_purge_receipt_hash72 = purge_receipt_hash72
            self.last_error_code = None
            return committed
        except Exception as exc:
            code = self._error_code(exc)
            self.last_error_code = code
            self._quarantine(
                receipt=receipt,
                reason_code=code,
                buffer_result=buffer_result,
            )
            if isinstance(exc, Pass218I31PurgeError):
                raise
            raise Pass218I31PurgeError(code) from exc

    def status(self) -> dict[str, Any]:
        lifecycle = self.lifecycle.status()
        i30 = self.i30_store.status()
        purge = self.store.status()
        return {
            "schema": PASS218_I31_STATUS_SCHEMA,
            "version": PASS218_I31_PURGE_VERSION,
            "purge_scope": PASS218_I31_PURGE_SCOPE,
            "writer_authority_ready": bool(
                lifecycle.get("ingestion_enabled")
                and lifecycle.get("ownership_writer_authority", True)
            ),
            "i30_promotion_present": bool(i30.get("promotion_present")),
            "i30_canonical_root_hash72": i30.get("canonical_root_hash72"),
            "purge_count": self.purge_count,
            "last_purge_receipt_hash72": self.last_purge_receipt_hash72,
            "i31_error_code": self.last_error_code,
            **purge,
            "verbatim_purge_invoked": purge.get("purge_status")
            in {PASS218_I31_PURGED_STATUS, PASS218_I31_QUARANTINED_STATUS},
            "purge_confirmation_verified": purge.get("purge_status")
            == PASS218_I31_PURGED_STATUS,
            "curriculum_advance_permitted": False,
            "closure_invoked": False,
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
    "PASS218_I31_PENDING_STATUS",
    "PASS218_I31_PURGE_RECEIPT_SCHEMA",
    "PASS218_I31_PURGE_SCOPE",
    "PASS218_I31_PURGE_VERSION",
    "PASS218_I31_PURGED_STATUS",
    "PASS218_I31_QUARANTINED_STATUS",
    "PASS218_I31_STATUS_SCHEMA",
    "Pass218I31ManagedBufferRegistry",
    "Pass218I31PurgeConfirmationError",
    "Pass218I31PurgeError",
    "Pass218I31PurgeRequest",
    "Pass218I31PurgeStateError",
    "Pass218I31PurgeStore",
    "Pass218I31PurgeValidationError",
    "Pass218I31VerbatimPurger",
]
