"""Pass 218 Iteration 33 authoritative curriculum advancement.

This boundary consumes one durable I32 source closure and advances the inherited
Iteration-1 curriculum cursor only after proving exact agreement with an
authoritative manifest/cursor pair.  It does not create curriculum authority,
advance acceptance-gated stages, or widen VM81/truth/action/learning authority.
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
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumManifest,
    CurriculumSource,
    CurriculumStage,
    Pass218CurriculumOrderError,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSED_STATUS,
    PASS218_I32_CLOSURE_RECEIPT_SCHEMA,
    Pass218I32ClosureStore,
)

PASS218_I33_ADVANCE_VERSION = "HHS-P218-I33-AUTHORITATIVE-CURRICULUM-ADVANCE-V1"
PASS218_I33_ADVANCE_SCOPE = "PASS218_I32_CLOSED_SOURCE_AUTHORITATIVE_CURRICULUM_ADVANCE"
PASS218_I33_AUTHORITY_SCHEMA = "HHS-P218-I33-CURRICULUM-AUTHORITY-V1"
PASS218_I33_ADVANCE_RECEIPT_SCHEMA = "HHS-P218-I33-CURRICULUM-ADVANCE-RECEIPT-V1"
PASS218_I33_STATE_SCHEMA = "HHS-P218-I33-CURRICULUM-STATE-V1"
PASS218_I33_STATUS_SCHEMA = "HHS-P218-I33-CURRICULUM-STATUS-V1"
PASS218_I33_PENDING_STATUS = "SOURCE_CLOSED_PENDING_CURRICULUM_ADVANCE"
PASS218_I33_ADVANCED_STATUS = "CURRICULUM_ADVANCED_PENDING_NEXT_SOURCE"
PASS218_I33_STAGE_GATE_STATUS = "CURRICULUM_ADVANCED_PENDING_STAGE_ACCEPTANCE"
PASS218_I33_COMPLETE_STATUS = "CURRICULUM_ADVANCED_CURRICULUM_COMPLETE"
PASS218_I33_DEFAULT_COMPILER_VERSION = "HHS-P218-CURRICULUM-I1-V1"


class Pass218I33CurriculumAdvanceError(RuntimeError):
    pass


class Pass218I33CurriculumAuthorityError(Pass218I33CurriculumAdvanceError):
    pass


class Pass218I33CurriculumBindingError(Pass218I33CurriculumAdvanceError):
    pass


class Pass218I33CurriculumStateError(Pass218I33CurriculumAdvanceError):
    pass


class Pass218I33LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...
    def status(self) -> Mapping[str, Any]: ...


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
        raise Pass218I33CurriculumStateError("P218_I33_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I33CurriculumStateError("P218_I33_STATE_OBJECT_REQUIRED")
    return value


def _valid_hash216(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 216:
        return False
    return all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))


def _manifest_record(manifest: CurriculumManifest) -> dict[str, Any]:
    record = manifest.record()
    if record.get("schema") != "HHS-P218-CURRICULUM-MANIFEST-I1-V1":
        raise Pass218I33CurriculumAuthorityError("P218_I33_MANIFEST_SCHEMA_INVALID")
    if not validate_hash72(manifest.manifest_hash72):
        raise Pass218I33CurriculumAuthorityError("P218_I33_MANIFEST_HASH72_INVALID")
    if not validate_hash72(manifest.curriculum_identity_hash72):
        raise Pass218I33CurriculumAuthorityError("P218_I33_CURRICULUM_IDENTITY_INVALID")
    return record


def restore_default_manifest(payload: Mapping[str, Any]) -> CurriculumManifest:
    """Rebuild an I1 default-compiler manifest and require exact record equality."""
    if payload.get("schema") != "HHS-P218-CURRICULUM-MANIFEST-I1-V1":
        raise Pass218I33CurriculumAuthorityError("P218_I33_MANIFEST_SCHEMA_INVALID")
    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list):
        raise Pass218I33CurriculumAuthorityError("P218_I33_MANIFEST_SOURCES_REQUIRED")
    sources: list[CurriculumSource] = []
    for raw in raw_sources:
        if not isinstance(raw, Mapping):
            raise Pass218I33CurriculumAuthorityError("P218_I33_MANIFEST_SOURCE_INVALID")
        try:
            stage = CurriculumStage(int(raw["stage"]))
            source = CurriculumSource(
                source_id=str(raw["source_id"]),
                stage=stage,
                locator=str(raw["locator"]),
                checksum_sha256=str(raw["checksum_sha256"]),
                rights_class=str(raw["rights_class"]),
                source_authority=str(raw["source_authority"]),
                media_type=str(raw.get("media_type") or "application/octet-stream"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise Pass218I33CurriculumAuthorityError(
                "P218_I33_MANIFEST_SOURCE_INVALID"
            ) from exc
        sources.append(source)
    rebuilt = build_curriculum_manifest(
        str(payload.get("genesis_seed_hash72") or ""),
        sources,
        compiler_version=PASS218_I33_DEFAULT_COMPILER_VERSION,
    )
    if rebuilt.record() != dict(payload):
        raise Pass218I33CurriculumAuthorityError("P218_I33_MANIFEST_REDERIVE_MISMATCH")
    return rebuilt


@dataclass(frozen=True)
class Pass218I33CurriculumAuthority:
    manifest: CurriculumManifest
    initial_cursor: CurriculumCursor

    def validated(self) -> "Pass218I33CurriculumAuthority":
        _manifest_record(self.manifest)
        self.initial_cursor.expected_source(self.manifest)
        if self.initial_cursor.next_ordinal > len(self.manifest.sources):
            raise Pass218I33CurriculumAuthorityError("P218_I33_CURSOR_ORDINAL_OUT_OF_RANGE")
        return self

    def record(self) -> dict[str, Any]:
        self.validated()
        body = {
            "schema": PASS218_I33_AUTHORITY_SCHEMA,
            "version": PASS218_I33_ADVANCE_VERSION,
            "manifest": self.manifest.record(),
            "initial_cursor": self.initial_cursor.record(),
            "compiler_version": PASS218_I33_DEFAULT_COMPILER_VERSION,
            "authority_source": "PRECONFIGURED_READ_ONLY_CURRICULUM_AUTHORITY",
        }
        return {
            **body,
            "authority_root_hash72": hash72_digest(
                {"domain": PASS218_I33_AUTHORITY_SCHEMA}, body
            ),
        }

    @classmethod
    def restore(cls, payload: Mapping[str, Any]) -> "Pass218I33CurriculumAuthority":
        if payload.get("schema") != PASS218_I33_AUTHORITY_SCHEMA:
            raise Pass218I33CurriculumAuthorityError("P218_I33_AUTHORITY_SCHEMA_INVALID")
        if payload.get("version") != PASS218_I33_ADVANCE_VERSION:
            raise Pass218I33CurriculumAuthorityError("P218_I33_AUTHORITY_VERSION_INVALID")
        if payload.get("compiler_version") != PASS218_I33_DEFAULT_COMPILER_VERSION:
            raise Pass218I33CurriculumAuthorityError("P218_I33_COMPILER_VERSION_INVALID")
        manifest_raw = payload.get("manifest")
        cursor_raw = payload.get("initial_cursor")
        if not isinstance(manifest_raw, Mapping) or not isinstance(cursor_raw, Mapping):
            raise Pass218I33CurriculumAuthorityError("P218_I33_AUTHORITY_PAYLOAD_INVALID")
        authority = cls(
            manifest=restore_default_manifest(manifest_raw),
            initial_cursor=CurriculumCursor.restore(cursor_raw),
        ).validated()
        expected = authority.record()
        if dict(payload) != expected:
            raise Pass218I33CurriculumAuthorityError("P218_I33_AUTHORITY_ROOT_MISMATCH")
        return authority


class Pass218I33CurriculumAdvanceStore:
    """Durable authority snapshot plus atomic current-cursor pointer."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.authority_path = self.root / "authority.json"
        self.state_path = self.root / "state.json"
        self.receipt_root = self.root / "receipts"

    def ensure_authority(self, authority: Pass218I33CurriculumAuthority) -> dict[str, Any]:
        record = authority.record()
        if self.authority_path.exists():
            existing = _load_json(self.authority_path)
            Pass218I33CurriculumAuthority.restore(existing)
            if existing != record:
                raise Pass218I33CurriculumStateError("P218_I33_AUTHORITY_CONFLICT")
            return existing
        _atomic_write_json(self.authority_path, record)
        persisted = _load_json(self.authority_path)
        if persisted != record:
            raise Pass218I33CurriculumStateError("P218_I33_AUTHORITY_PERSIST_MISMATCH")
        return persisted

    def authority_record(self) -> dict[str, Any] | None:
        if not self.authority_path.exists():
            return None
        value = _load_json(self.authority_path)
        Pass218I33CurriculumAuthority.restore(value)
        return value

    def state_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        value = _load_json(self.state_path)
        if value.get("schema") != PASS218_I33_STATE_SCHEMA:
            raise Pass218I33CurriculumStateError("P218_I33_STATE_SCHEMA_INVALID")
        cursor_raw = value.get("current_cursor")
        if not isinstance(cursor_raw, Mapping):
            raise Pass218I33CurriculumStateError("P218_I33_STATE_CURSOR_REQUIRED")
        CurriculumCursor.restore(cursor_raw)
        if not validate_hash72(str(value.get("state_root_hash72") or "")):
            raise Pass218I33CurriculumStateError("P218_I33_STATE_ROOT_INVALID")
        body = {key: item for key, item in value.items() if key != "state_root_hash72"}
        expected_root = hash72_digest({"domain": PASS218_I33_STATE_SCHEMA}, body)
        if expected_root != value["state_root_hash72"]:
            raise Pass218I33CurriculumStateError("P218_I33_STATE_ROOT_MISMATCH")
        return value

    def current_cursor(self, authority: Pass218I33CurriculumAuthority) -> CurriculumCursor:
        state = self.state_record()
        if state is None:
            return authority.initial_cursor
        if state.get("authority_root_hash72") != authority.record()["authority_root_hash72"]:
            raise Pass218I33CurriculumStateError("P218_I33_STATE_AUTHORITY_MISMATCH")
        return CurriculumCursor.restore(state["current_cursor"])

    def last_receipt(self) -> dict[str, Any] | None:
        state = self.state_record()
        if state is None or state.get("last_receipt_path") is None:
            return None
        path = self.root / str(state["last_receipt_path"])
        if not path.is_file():
            raise Pass218I33CurriculumStateError("P218_I33_LAST_RECEIPT_MISSING")
        receipt = _load_json(path)
        _verify_advance_receipt(receipt)
        if receipt.get("advance_receipt_hash72") != state.get("last_advance_receipt_hash72"):
            raise Pass218I33CurriculumStateError("P218_I33_LAST_RECEIPT_STATE_MISMATCH")
        return receipt

    def commit_advance(
        self,
        *,
        authority: Pass218I33CurriculumAuthority,
        previous_cursor: CurriculumCursor,
        next_cursor: CurriculumCursor,
        receipt: Mapping[str, Any],
    ) -> dict[str, Any]:
        checked = _verify_advance_receipt(dict(receipt))
        authority_record = self.ensure_authority(authority)
        ordinal = int(checked["ordinal"])
        receipt_name = f"{ordinal:08d}-{checked['advance_receipt_hash72']}.json"
        receipt_path = self.receipt_root / receipt_name
        if receipt_path.exists():
            existing = _load_json(receipt_path)
            if existing != checked:
                raise Pass218I33CurriculumStateError("P218_I33_RECEIPT_CONFLICT")
        else:
            _atomic_write_json(receipt_path, checked)
        relative = receipt_path.relative_to(self.root).as_posix()
        state_body = {
            "schema": PASS218_I33_STATE_SCHEMA,
            "version": PASS218_I33_ADVANCE_VERSION,
            "authority_root_hash72": authority_record["authority_root_hash72"],
            "manifest_hash72": authority.manifest.manifest_hash72,
            "curriculum_identity_hash72": authority.manifest.curriculum_identity_hash72,
            "previous_cursor": previous_cursor.record(),
            "current_cursor": next_cursor.record(),
            "last_receipt_path": relative,
            "last_advance_receipt_hash72": checked["advance_receipt_hash72"],
            "last_transition_hash72": checked["transition_hash72"],
            "advance_count": next_cursor.next_ordinal - authority.initial_cursor.next_ordinal,
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest(
                {"domain": PASS218_I33_STATE_SCHEMA}, state_body
            ),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.state_record()
        if persisted != state:
            raise Pass218I33CurriculumStateError("P218_I33_STATE_PERSIST_MISMATCH")
        return checked

    def status(self) -> dict[str, Any]:
        authority = self.authority_record()
        state = self.state_record()
        receipt = self.last_receipt() if state is not None else None
        return {
            "authority_configured": authority is not None,
            "authority_root_hash72": None if authority is None else authority["authority_root_hash72"],
            "manifest_hash72": None if authority is None else authority["manifest"]["manifest_hash72"],
            "curriculum_identity_hash72": (
                None if authority is None else authority["manifest"]["curriculum_identity_hash72"]
            ),
            "current_cursor": None if state is None else state["current_cursor"],
            "state_root_hash72": None if state is None else state["state_root_hash72"],
            "last_advance_receipt_hash72": (
                None if receipt is None else receipt["advance_receipt_hash72"]
            ),
            "advance_status": PASS218_I33_PENDING_STATUS if receipt is None else receipt["advance_status"],
            "curriculum_cursor_advanced": receipt is not None,
        }


def _verify_i32_closure(record: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(record)
    if value.get("schema") != PASS218_I32_CLOSURE_RECEIPT_SCHEMA:
        raise Pass218I33CurriculumBindingError("P218_I33_I32_CLOSURE_SCHEMA_INVALID")
    if value.get("closure_status") != PASS218_I32_CLOSED_STATUS:
        raise Pass218I33CurriculumBindingError("P218_I33_I32_SOURCE_NOT_CLOSED")
    required_true = (
        "closure_invoked",
        "source_closed",
        "purge_confirmation_verified",
        "durable_nonverbatim_store_verified",
        "source_binding_requires_curriculum_match_before_advance",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_CLOSURE_PROOF_INCOMPLETE")
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
        raise Pass218I33CurriculumBindingError("P218_I33_I32_AUTHORITY_DRIFT")

    source_id_hash72 = hash72_digest(
        {"domain": "HHS-P218-I32-SOURCE-IDENTITY-V1"},
        {
            "source_id": value["source_id"],
            "source_sha256": value["source_sha256"],
            "source_authority": value["source_authority"],
            "rights_class": value["rights_class"],
        },
    )
    if source_id_hash72 != value.get("source_id_hash72"):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_SOURCE_ID_REDERIVE_MISMATCH")
    source_binding_hash72 = hash72_digest(
        {"domain": "HHS-P218-I32-SOURCE-CURRICULUM-BINDING-V1"},
        {
            "source_id_hash72": source_id_hash72,
            "curriculum_identity_hash72": value["curriculum_identity_hash72"],
            "curriculum_position": value["curriculum_position"],
            "source_stage": value["source_stage"],
            "previous_closure_hash72": value["previous_closure_hash72"],
            "i31_purge_receipt_hash72": value["i31_purge_receipt_hash72"],
            "canonical_root_hash72": value["canonical_root_hash72"],
        },
    )
    if source_binding_hash72 != value.get("source_binding_hash72"):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_SOURCE_BINDING_REDERIVE_MISMATCH")
    closure_validation_hash72 = hash72_digest(
        {"domain": "HHS-P218-I32-SOURCE-CLOSURE-VALIDATION-V1"},
        {
            "i31_purge_receipt_hash72": value["i31_purge_receipt_hash72"],
            "i31_purge_gate_root_hash72": value["i31_purge_gate_root_hash72"],
            "i31_purge_hash216": value["i31_purge_hash216"],
            "source_binding_hash72": source_binding_hash72,
            "promoted_object_hash72": value["promoted_object_hash72"],
            "canonical_root_hash72": value["canonical_root_hash72"],
            "purge_confirmation_verified": True,
            "durable_nonverbatim_store_verified": True,
            "curriculum_cursor_advanced": False,
        },
    )
    if closure_validation_hash72 != value.get("closure_validation_hash72"):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_CLOSURE_VALIDATION_REDERIVE_MISMATCH")
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
    source_closure_hash72 = hash72_digest(
        {"domain": "HHS-P218-I32-SOURCE-CLOSURE-RECEIPT-V1"}, closure_body
    )
    if source_closure_hash72 != value.get("source_closure_hash72"):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_CLOSURE_REDERIVE_MISMATCH")
    closure_hash216 = (
        str(value["i31_purge_receipt_hash72"])
        + closure_validation_hash72
        + source_closure_hash72
    )
    if closure_hash216 != value.get("closure_hash216") or not _valid_hash216(closure_hash216):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_HASH216_REDERIVE_MISMATCH")
    closure_chain_root_hash72 = hash72_digest(
        {"domain": "HHS-P218-I32-CLOSURE-CHAIN-ROOT-V1"},
        {
            "previous_closure_hash72": value["previous_closure_hash72"],
            "source_closure_hash72": source_closure_hash72,
            "canonical_root_hash72": value["canonical_root_hash72"],
            "curriculum_identity_hash72": value["curriculum_identity_hash72"],
            "curriculum_position": value["curriculum_position"],
            "source_stage": value["source_stage"],
        },
    )
    if closure_chain_root_hash72 != value.get("closure_chain_root_hash72"):
        raise Pass218I33CurriculumBindingError("P218_I33_I32_CHAIN_ROOT_REDERIVE_MISMATCH")
    validated_hash216 = value.get("validated_hash216")
    if not _valid_hash216(validated_hash216):
        raise Pass218I33CurriculumBindingError("P218_I33_VALIDATED_HASH216_INVALID")
    if str(validated_hash216)[:72] != value["curriculum_identity_hash72"]:
        raise Pass218I33CurriculumBindingError("P218_I33_UPSTREAM_CURRICULUM_IDENTITY_MISMATCH")
    return value


def _verify_advance_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(receipt)
    if value.get("schema") != PASS218_I33_ADVANCE_RECEIPT_SCHEMA:
        raise Pass218I33CurriculumStateError("P218_I33_RECEIPT_SCHEMA_INVALID")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"advance_receipt_hash72", "advance_hash216", "advance_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I33_ADVANCE_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("advance_receipt_hash72"):
        raise Pass218I33CurriculumStateError("P218_I33_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i32_source_closure_hash72"])
        + str(value["transition_hash72"])
        + str(value["advance_receipt_hash72"])
    )
    if expected_hash216 != value.get("advance_hash216") or not _valid_hash216(expected_hash216):
        raise Pass218I33CurriculumStateError("P218_I33_ADVANCE_HASH216_INVALID")
    next_cursor = value.get("next_cursor")
    if not isinstance(next_cursor, Mapping):
        raise Pass218I33CurriculumStateError("P218_I33_RECEIPT_CURSOR_REQUIRED")
    cursor = CurriculumCursor.restore(next_cursor)
    if _sha256_hex(cursor.record()) != value.get("cursor_state_sha256"):
        raise Pass218I33CurriculumStateError("P218_I33_CURSOR_STATE_SHA_MISMATCH")
    return value


class Pass218I33CurriculumAdvancer:
    """Advance the exact configured I1 cursor after validating one I32 closure."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I33LifecycleProtocol,
        i32_store_root: str | os.PathLike[str],
        advance_store_root: str | os.PathLike[str],
        authority: Pass218I33CurriculumAuthority | None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i32_store = Pass218I32ClosureStore(i32_store_root)
        self.store = Pass218I33CurriculumAdvanceStore(advance_store_root)
        self.authority = None if authority is None else authority.validated()
        self.advance_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _require_authority(self) -> Pass218I33CurriculumAuthority:
        if self.authority is None:
            raise Pass218I33CurriculumAuthorityError("P218_I33_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED")
        self.store.ensure_authority(self.authority)
        return self.authority

    @staticmethod
    def _match_closure(
        *,
        closure: Mapping[str, Any],
        authority: Pass218I33CurriculumAuthority,
        cursor: CurriculumCursor,
    ) -> Mapping[str, Any]:
        manifest = authority.manifest
        expected = cursor.expected_source(manifest)
        if expected is None:
            raise Pass218I33CurriculumBindingError("P218_I33_CURRICULUM_ALREADY_COMPLETE")
        checks = (
            ("curriculum_identity_hash72", closure["curriculum_identity_hash72"], manifest.curriculum_identity_hash72),
            ("curriculum_position", int(closure["curriculum_position"]), cursor.next_ordinal),
            ("source_id", closure["source_id"], expected["source_id"]),
            ("source_sha256", closure["source_sha256"], expected["checksum_sha256"]),
            ("source_stage", int(closure["source_stage"]), int(expected["stage"])),
            ("rights_class", closure["rights_class"], expected["rights_class"]),
            ("source_authority", closure["source_authority"], expected["source_authority"]),
            ("previous_closure_hash72", closure["previous_closure_hash72"], cursor.last_closure_hash72),
        )
        for field, actual, wanted in checks:
            if actual != wanted:
                raise Pass218I33CurriculumBindingError("P218_I33_AUTHORITATIVE_CURRICULUM_MISMATCH:" + field)
        if int(expected["ordinal"]) != cursor.next_ordinal:
            raise Pass218I33CurriculumBindingError("P218_I33_AUTHORITATIVE_CURRICULUM_MISMATCH:ordinal")
        return expected

    def advance(self) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            authority = self._require_authority()
            closure_raw = self.i32_store.active_record()
            if closure_raw is None:
                raise Pass218I33CurriculumBindingError("P218_I33_I32_CLOSURE_REQUIRED")
            closure = _verify_i32_closure(closure_raw)
            existing = self.store.last_receipt()
            if existing is not None:
                if (
                    existing.get("i32_source_closure_hash72") == closure["source_closure_hash72"]
                    and existing.get("curriculum_identity_hash72") == authority.manifest.curriculum_identity_hash72
                ):
                    self.last_error_code = None
                    return existing
                raise Pass218I33CurriculumStateError("P218_I33_PREVIOUS_ADVANCE_CONFLICT")

            cursor = self.store.current_cursor(authority)
            expected = self._match_closure(closure=closure, authority=authority, cursor=cursor)
            try:
                next_cursor, i1_receipt = cursor.advance(
                    authority.manifest,
                    source_id=str(closure["source_id"]),
                    closure_hash72=str(closure["source_closure_hash72"]),
                )
            except (Pass218CurriculumOrderError, ValueError) as exc:
                raise Pass218I33CurriculumBindingError("P218_I33_I1_CURSOR_ADVANCE_REJECTED:" + str(exc)) from exc

            if i1_receipt["ordinal"] != cursor.next_ordinal:
                raise Pass218I33CurriculumBindingError("P218_I33_I1_RECEIPT_ORDINAL_MISMATCH")
            if i1_receipt["source_checksum_sha256"] != closure["source_sha256"]:
                raise Pass218I33CurriculumBindingError("P218_I33_I1_RECEIPT_CHECKSUM_MISMATCH")
            if i1_receipt["previous_closure_hash72"] != closure["previous_closure_hash72"]:
                raise Pass218I33CurriculumBindingError("P218_I33_I1_RECEIPT_PREVIOUS_CLOSURE_MISMATCH")

            next_expected = next_cursor.expected_source(authority.manifest)
            current_stage = int(expected["stage"])
            next_stage = None if next_expected is None else int(next_expected["stage"])
            stage_transition_required = bool(next_stage is not None and next_stage > current_stage)
            if next_expected is None:
                advance_status = PASS218_I33_COMPLETE_STATUS
            elif stage_transition_required:
                advance_status = PASS218_I33_STAGE_GATE_STATUS
            else:
                advance_status = PASS218_I33_ADVANCED_STATUS

            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I33-CURRICULUM-ADVANCE-VALIDATION-V1"},
                {
                    "authority_root_hash72": authority.record()["authority_root_hash72"],
                    "manifest_hash72": authority.manifest.manifest_hash72,
                    "curriculum_identity_hash72": authority.manifest.curriculum_identity_hash72,
                    "cursor_before": cursor.record(),
                    "expected_source": dict(expected),
                    "i32_source_closure_hash72": closure["source_closure_hash72"],
                    "i32_closure_chain_root_hash72": closure["closure_chain_root_hash72"],
                    "upstream_curriculum_segment_hash72": str(closure["validated_hash216"])[:72],
                    "i1_transition_hash72": i1_receipt["transition_hash72"],
                },
            )
            receipt_body = {
                "schema": PASS218_I33_ADVANCE_RECEIPT_SCHEMA,
                "version": PASS218_I33_ADVANCE_VERSION,
                "advance_scope": PASS218_I33_ADVANCE_SCOPE,
                "advance_status": advance_status,
                "authority_root_hash72": authority.record()["authority_root_hash72"],
                "manifest_hash72": authority.manifest.manifest_hash72,
                "curriculum_identity_hash72": authority.manifest.curriculum_identity_hash72,
                "ordinal": cursor.next_ordinal,
                "source_id": closure["source_id"],
                "source_stage": current_stage,
                "source_sha256": closure["source_sha256"],
                "source_authority": closure["source_authority"],
                "rights_class": closure["rights_class"],
                "previous_closure_hash72": cursor.last_closure_hash72,
                "i32_source_closure_hash72": closure["source_closure_hash72"],
                "i32_closure_chain_root_hash72": closure["closure_chain_root_hash72"],
                "i32_closure_hash216": closure["closure_hash216"],
                "i33_advance_validation_hash72": validation_hash72,
                "transition_hash72": i1_receipt["transition_hash72"],
                "cursor_state_sha256": i1_receipt["cursor_state_sha256"],
                "next_cursor": next_cursor.record(),
                "next_expected_ordinal": next_cursor.next_ordinal,
                "next_expected_source_id": None if next_expected is None else next_expected["source_id"],
                "next_expected_stage": next_stage,
                "stage_transition_required": stage_transition_required,
                "source_binding_matches_authoritative_manifest": True,
                "upstream_semantic_curriculum_binding_verified": True,
                "curriculum_advance_permitted": True,
                "curriculum_cursor_advanced": True,
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
            advance_receipt_hash72 = hash72_digest(
                {"domain": PASS218_I33_ADVANCE_RECEIPT_SCHEMA}, receipt_body
            )
            advance_hash216 = (
                str(closure["source_closure_hash72"])
                + str(i1_receipt["transition_hash72"])
                + advance_receipt_hash72
            )
            completed = {
                **receipt_body,
                "advance_receipt_hash72": advance_receipt_hash72,
                "advance_hash216": advance_hash216,
                "advance_hash216_semantics": [
                    "I32_SOURCE_CLOSURE_RECEIPT",
                    "I1_CURRICULUM_CURSOR_TRANSITION",
                    "I33_AUTHORITATIVE_ADVANCE_RECEIPT",
                ],
            }
            committed = self.store.commit_advance(
                authority=authority,
                previous_cursor=cursor,
                next_cursor=next_cursor,
                receipt=completed,
            )
            self.advance_count += 1
            self.last_error_code = None
            return committed
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I33CurriculumAdvanceError):
                raise
            raise Pass218I33CurriculumAdvanceError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        lifecycle = self.lifecycle.status()
        store_status = self.store.status()
        configured = self.authority is not None
        configured_record = None if self.authority is None else self.authority.record()
        return {
            "schema": PASS218_I33_STATUS_SCHEMA,
            "version": PASS218_I33_ADVANCE_VERSION,
            "advance_scope": PASS218_I33_ADVANCE_SCOPE,
            "writer_authority_ready": bool(
                lifecycle.get("ingestion_enabled")
                and lifecycle.get("ownership_writer_authority", True)
            ),
            "authoritative_curriculum_ready": configured,
            "configured_authority_root_hash72": (
                None if configured_record is None else configured_record["authority_root_hash72"]
            ),
            "advance_count_runtime": self.advance_count,
            "i33_error_code": self.last_error_code,
            **store_status,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "PASS218_I33_ADVANCED_STATUS",
    "PASS218_I33_ADVANCE_RECEIPT_SCHEMA",
    "PASS218_I33_ADVANCE_SCOPE",
    "PASS218_I33_ADVANCE_VERSION",
    "PASS218_I33_AUTHORITY_SCHEMA",
    "PASS218_I33_COMPLETE_STATUS",
    "PASS218_I33_DEFAULT_COMPILER_VERSION",
    "PASS218_I33_PENDING_STATUS",
    "PASS218_I33_STAGE_GATE_STATUS",
    "PASS218_I33_STATE_SCHEMA",
    "PASS218_I33_STATUS_SCHEMA",
    "Pass218I33CurriculumAdvanceError",
    "Pass218I33CurriculumAdvanceStore",
    "Pass218I33CurriculumAdvancer",
    "Pass218I33CurriculumAuthority",
    "Pass218I33CurriculumAuthorityError",
    "Pass218I33CurriculumBindingError",
    "Pass218I33CurriculumStateError",
    "restore_default_manifest",
]
