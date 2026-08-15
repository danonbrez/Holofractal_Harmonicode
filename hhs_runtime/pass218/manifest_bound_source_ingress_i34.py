"""Pass 218 Iteration 34 authoritative manifest-bound source ingress.

I34 binds transient source bytes to the exact inherited I1 curriculum manifest
and current I33 cursor *before* semantic construction.  It persists only
nonverbatim source/curriculum metadata and receipts.  It does not advance the
curriculum cursor, cross an acceptance-gated stage boundary, invoke I3 source
transactions, construct semantic candidates, promote learning, or mint any
VM81/truth/action authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.curriculum import CurriculumCursor
from hhs_runtime.pass218.curriculum_advance_i33 import (
    Pass218I33CurriculumAdvanceStore,
    Pass218I33CurriculumAuthority,
)

PASS218_I34_INGRESS_VERSION = "HHS-P218-I34-MANIFEST-BOUND-SOURCE-INGRESS-V1"
PASS218_I34_INGRESS_SCOPE = "PASS218_AUTHORITATIVE_MANIFEST_BOUND_SOURCE_INGRESS"
PASS218_I34_RECEIPT_SCHEMA = "HHS-P218-I34-MANIFEST-SOURCE-INGRESS-RECEIPT-V1"
PASS218_I34_STATE_SCHEMA = "HHS-P218-I34-MANIFEST-SOURCE-INGRESS-STATE-V1"
PASS218_I34_STATUS_SCHEMA = "HHS-P218-I34-MANIFEST-SOURCE-INGRESS-STATUS-V1"
PASS218_I34_READY_STATUS = "MANIFEST_BOUND_SOURCE_READY_FOR_SEMANTIC_INGRESS"
PASS218_I34_STAGE_GATE_STATUS = "MANIFEST_SOURCE_INGRESS_BLOCKED_PENDING_STAGE_ACCEPTANCE"
PASS218_I34_COMPLETE_STATUS = "MANIFEST_SOURCE_INGRESS_BLOCKED_CURRICULUM_COMPLETE"


class Pass218I34IngressError(RuntimeError):
    pass


class Pass218I34AuthorityError(Pass218I34IngressError):
    pass


class Pass218I34BindingError(Pass218I34IngressError):
    pass


class Pass218I34StateError(Pass218I34IngressError):
    pass


class Pass218I34LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...
    def status(self) -> Mapping[str, Any]: ...


class Pass218I34I33StoreProtocol(Protocol):
    def ensure_authority(self, authority: Pass218I33CurriculumAuthority) -> Mapping[str, Any]: ...
    def current_cursor(self, authority: Pass218I33CurriculumAuthority) -> CurriculumCursor: ...
    def last_receipt(self) -> Mapping[str, Any] | None: ...


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256_hex(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


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
        raise Pass218I34StateError("P218_I34_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I34StateError("P218_I34_STATE_OBJECT_REQUIRED")
    return value


def _valid_hash216(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _verify_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(receipt)
    if value.get("schema") != PASS218_I34_RECEIPT_SCHEMA:
        raise Pass218I34StateError("P218_I34_RECEIPT_SCHEMA_INVALID")
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
        raise Pass218I34StateError("P218_I34_RECEIPT_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "physical_memory_erasure_claimed",
        "external_request_buffer_erasure_claimed",
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
        raise Pass218I34StateError("P218_I34_RECEIPT_AUTHORITY_DRIFT")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"ingress_receipt_hash72", "ingress_hash216", "ingress_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I34_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("ingress_receipt_hash72"):
        raise Pass218I34StateError("P218_I34_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["curriculum_identity_hash72"])
        + str(value["ingress_validation_hash72"])
        + str(value["ingress_receipt_hash72"])
    )
    if expected_hash216 != value.get("ingress_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I34StateError("P218_I34_HASH216_INVALID")
    return value


class Pass218I34ManifestSourceIngressStore:
    """Durable nonverbatim receipt store for one source at the current cursor."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I34_STATE_SCHEMA:
            raise Pass218I34StateError("P218_I34_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        expected_root = hash72_digest({"domain": PASS218_I34_STATE_SCHEMA}, body)
        if expected_root != state.get("state_root_hash72"):
            raise Pass218I34StateError("P218_I34_STATE_ROOT_MISMATCH")
        relative = state.get("active_receipt_path")
        if not isinstance(relative, str):
            raise Pass218I34StateError("P218_I34_RECEIPT_PATH_REQUIRED")
        receipt_path = self.root / relative
        if not receipt_path.is_file():
            raise Pass218I34StateError("P218_I34_RECEIPT_MISSING")
        receipt = _verify_receipt(_load_json(receipt_path))
        if receipt["ingress_receipt_hash72"] != state.get("active_ingress_receipt_hash72"):
            raise Pass218I34StateError("P218_I34_STATE_RECEIPT_MISMATCH")
        return receipt

    def commit(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_receipt(receipt)
        existing = self.active_record()
        if existing is not None:
            if existing != checked:
                raise Pass218I34StateError("P218_I34_ACTIVE_BINDING_CONFLICT")
            return existing
        ordinal = int(checked["curriculum_position"])
        name = f"{ordinal:08d}-{checked['ingress_receipt_hash72']}.json"
        receipt_path = self.receipt_root / name
        if receipt_path.exists():
            persisted = _load_json(receipt_path)
            if persisted != checked:
                raise Pass218I34StateError("P218_I34_RECEIPT_CONFLICT")
        else:
            _atomic_write_json(receipt_path, checked)
        relative = receipt_path.relative_to(self.root).as_posix()
        state_body = {
            "schema": PASS218_I34_STATE_SCHEMA,
            "version": PASS218_I34_INGRESS_VERSION,
            "authority_root_hash72": checked["authority_root_hash72"],
            "manifest_hash72": checked["manifest_hash72"],
            "curriculum_identity_hash72": checked["curriculum_identity_hash72"],
            "curriculum_position": checked["curriculum_position"],
            "source_id": checked["source_id"],
            "source_sha256": checked["source_sha256"],
            "active_receipt_path": relative,
            "active_ingress_receipt_hash72": checked["ingress_receipt_hash72"],
            "binding_status": PASS218_I34_READY_STATUS,
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest({"domain": PASS218_I34_STATE_SCHEMA}, state_body),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I34StateError("P218_I34_STATE_PERSIST_MISMATCH")
        return checked


@dataclass(frozen=True)
class Pass218I34ExpectedSource:
    authority_root_hash72: str
    manifest_hash72: str
    curriculum_identity_hash72: str
    cursor: CurriculumCursor
    source: Mapping[str, Any]
    previous_advance_receipt_hash72: str | None


class Pass218I34ManifestBoundSourceIngress:
    """Bind transient source bytes to the current authoritative curriculum slot."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I34LifecycleProtocol,
        authority: Pass218I33CurriculumAuthority | None,
        i33_store_root: str | os.PathLike[str],
        ingress_store_root: str | os.PathLike[str],
        i33_store: Pass218I34I33StoreProtocol | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.authority = None if authority is None else authority.validated()
        self.i33_store: Pass218I34I33StoreProtocol = (
            i33_store if i33_store is not None else Pass218I33CurriculumAdvanceStore(i33_store_root)
        )
        self.store = Pass218I34ManifestSourceIngressStore(ingress_store_root)
        self.bind_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _expected(self) -> Pass218I34ExpectedSource:
        authority = self.authority
        if authority is None:
            raise Pass218I34AuthorityError("P218_I34_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED")
        authority_record = dict(self.i33_store.ensure_authority(authority))
        cursor = self.i33_store.current_cursor(authority)
        previous = self.i33_store.last_receipt()
        if previous is not None and previous.get("stage_transition_required") is True:
            if previous.get("stage_advance_permitted") is not True:
                raise Pass218I34BindingError("P218_I34_STAGE_ACCEPTANCE_REQUIRED")
        expected = cursor.expected_source(authority.manifest)
        if expected is None:
            raise Pass218I34BindingError("P218_I34_CURRICULUM_COMPLETE")
        if int(expected["ordinal"]) != cursor.next_ordinal:
            raise Pass218I34BindingError("P218_I34_CURSOR_ORDINAL_MISMATCH")
        return Pass218I34ExpectedSource(
            authority_root_hash72=str(authority_record["authority_root_hash72"]),
            manifest_hash72=authority.manifest.manifest_hash72,
            curriculum_identity_hash72=authority.manifest.curriculum_identity_hash72,
            cursor=cursor,
            source=dict(expected),
            previous_advance_receipt_hash72=(
                None if previous is None else str(previous.get("advance_receipt_hash72"))
            ),
        )

    def bind(self, *, source_id: str, source_bytes: bytes) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            expected = self._expected()
            source = expected.source
            if source_id != source["source_id"]:
                raise Pass218I34BindingError("P218_I34_UNEXPECTED_SOURCE_ID")
            managed = bytearray(source_bytes)
            byte_count = len(managed)
            try:
                observed_sha256 = sha256(bytes(managed)).hexdigest()
                if observed_sha256 != source["checksum_sha256"]:
                    raise Pass218I34BindingError("P218_I34_SOURCE_CHECKSUM_MISMATCH")
                source_identity_hash72 = hash72_digest(
                    {"domain": "HHS-P218-I34-SOURCE-IDENTITY-V1"},
                    {
                        "source_id": source["source_id"],
                        "source_sha256": observed_sha256,
                        "source_stage": int(source["stage"]),
                        "rights_class": source["rights_class"],
                        "source_authority": source["source_authority"],
                        "media_type": source["media_type"],
                    },
                )
                cursor_state_sha256 = _sha256_hex(expected.cursor.record())
                binding_hash72 = hash72_digest(
                    {"domain": "HHS-P218-I34-MANIFEST-SOURCE-BINDING-V1"},
                    {
                        "authority_root_hash72": expected.authority_root_hash72,
                        "manifest_hash72": expected.manifest_hash72,
                        "curriculum_identity_hash72": expected.curriculum_identity_hash72,
                        "cursor_state_sha256": cursor_state_sha256,
                        "curriculum_position": expected.cursor.next_ordinal,
                        "previous_closure_hash72": expected.cursor.last_closure_hash72,
                        "previous_advance_receipt_hash72": expected.previous_advance_receipt_hash72,
                        "source_identity_hash72": source_identity_hash72,
                    },
                )
            finally:
                for index in range(len(managed)):
                    managed[index] = 0
                managed_zeroized = all(value == 0 for value in managed)
                managed.clear()
                managed_cleared = len(managed) == 0
            if not managed_zeroized or not managed_cleared:
                raise Pass218I34BindingError("P218_I34_MANAGED_BUFFER_PURGE_FAILED")
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I34-INGRESS-VALIDATION-V1"},
                {
                    "binding_hash72": binding_hash72,
                    "source_sha256": observed_sha256,
                    "source_byte_count": byte_count,
                    "manifest_match_verified": True,
                    "cursor_match_verified": True,
                    "source_checksum_verified": True,
                    "managed_ingress_buffer_zeroized": True,
                    "managed_ingress_buffer_cleared": True,
                    "source_payload_persisted": False,
                },
            )
            body = {
                "schema": PASS218_I34_RECEIPT_SCHEMA,
                "version": PASS218_I34_INGRESS_VERSION,
                "scope": PASS218_I34_INGRESS_SCOPE,
                "binding_status": PASS218_I34_READY_STATUS,
                "authority_root_hash72": expected.authority_root_hash72,
                "manifest_hash72": expected.manifest_hash72,
                "curriculum_identity_hash72": expected.curriculum_identity_hash72,
                "cursor_state_sha256": cursor_state_sha256,
                "curriculum_position": expected.cursor.next_ordinal,
                "source_id": source["source_id"],
                "source_sha256": observed_sha256,
                "source_stage": int(source["stage"]),
                "source_stage_name": source["stage_name"],
                "rights_class": source["rights_class"],
                "source_authority": source["source_authority"],
                "media_type": source["media_type"],
                "source_byte_count": byte_count,
                "previous_closure_hash72": expected.cursor.last_closure_hash72,
                "previous_advance_receipt_hash72": expected.previous_advance_receipt_hash72,
                "source_identity_hash72": source_identity_hash72,
                "source_binding_hash72": binding_hash72,
                "ingress_validation_hash72": validation_hash72,
                "manifest_match_verified": True,
                "cursor_match_verified": True,
                "source_checksum_verified": True,
                "source_metadata_bound": True,
                "previous_closure_bound": True,
                "managed_ingress_buffer_zeroized": True,
                "managed_ingress_buffer_cleared": True,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
                "physical_memory_erasure_claimed": False,
                "external_request_buffer_erasure_claimed": False,
                "manifest_bound_source_ready": True,
                "i3_source_transaction_required": True,
                "i3_source_transaction_invoked": False,
                "semantic_construction_invoked": False,
                "curriculum_cursor_advanced": False,
                "stage_advance_permitted": False,
                "vm81_authorization_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
            receipt_hash72 = hash72_digest({"domain": PASS218_I34_RECEIPT_SCHEMA}, body)
            receipt = {
                **body,
                "ingress_receipt_hash72": receipt_hash72,
                "ingress_hash216": expected.curriculum_identity_hash72 + validation_hash72 + receipt_hash72,
                "ingress_hash216_semantics": [
                    "AUTHORITATIVE_CURRICULUM_IDENTITY",
                    "MANIFEST_SOURCE_INGRESS_VALIDATION",
                    "MANIFEST_BOUND_SOURCE_INGRESS_RECEIPT",
                ],
            }
            persisted = self.store.commit(receipt)
            self.bind_count += 1
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        authority_configured = self.authority is not None
        expected_source: Mapping[str, Any] | None = None
        gate_status: str | None = None
        cursor: CurriculumCursor | None = None
        if authority_configured:
            try:
                expected = self._expected()
                expected_source = expected.source
                cursor = expected.cursor
            except Pass218I34BindingError as exc:
                if str(exc) == "P218_I34_STAGE_ACCEPTANCE_REQUIRED":
                    gate_status = PASS218_I34_STAGE_GATE_STATUS
                elif str(exc) == "P218_I34_CURRICULUM_COMPLETE":
                    gate_status = PASS218_I34_COMPLETE_STATUS
                else:
                    gate_status = str(exc)
            except Exception as exc:
                gate_status = self._error_code(exc)
        binding_current = False
        if active is not None and cursor is not None:
            binding_current = (
                active["curriculum_identity_hash72"] == self.authority.manifest.curriculum_identity_hash72
                and int(active["curriculum_position"]) == cursor.next_ordinal
                and active["previous_closure_hash72"] == cursor.last_closure_hash72
            )
        return {
            "schema": PASS218_I34_STATUS_SCHEMA,
            "version": PASS218_I34_INGRESS_VERSION,
            "authority_configured": authority_configured,
            "binding_status": (
                active["binding_status"] if active is not None and binding_current else gate_status
            ),
            "manifest_hash72": (
                None if self.authority is None else self.authority.manifest.manifest_hash72
            ),
            "curriculum_identity_hash72": (
                None if self.authority is None else self.authority.manifest.curriculum_identity_hash72
            ),
            "current_cursor": None if cursor is None else cursor.record(),
            "expected_source_id": None if expected_source is None else expected_source["source_id"],
            "expected_source_stage": None if expected_source is None else expected_source["stage"],
            "active_ingress_receipt_hash72": (
                None if active is None else active["ingress_receipt_hash72"]
            ),
            "manifest_bound_source_ready": active is not None and binding_current,
            "binding_current": binding_current,
            "bind_count": self.bind_count,
            "last_error_code": self.last_error_code,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "i3_source_transaction_invoked": False,
            "semantic_construction_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "PASS218_I34_COMPLETE_STATUS",
    "PASS218_I34_INGRESS_SCOPE",
    "PASS218_I34_INGRESS_VERSION",
    "PASS218_I34_READY_STATUS",
    "PASS218_I34_RECEIPT_SCHEMA",
    "PASS218_I34_STAGE_GATE_STATUS",
    "PASS218_I34_STATE_SCHEMA",
    "PASS218_I34_STATUS_SCHEMA",
    "Pass218I34AuthorityError",
    "Pass218I34BindingError",
    "Pass218I34IngressError",
    "Pass218I34ManifestBoundSourceIngress",
    "Pass218I34ManifestSourceIngressStore",
    "Pass218I34StateError",
]
