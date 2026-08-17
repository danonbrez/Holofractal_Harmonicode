"""Pass 218 Iteration 48 manifest-bound curriculum completion seal.

Consumes the exact durable frozen-I47 terminal curriculum-advance state, proves
that the authoritative I33 cursor has exhausted the exact manifest, re-verifies
that the I30 semantic generation and canonical root are unchanged, and seals
only durable completion proof/receipt metadata.  This boundary does not invoke
I33, ingest another source, advance a stage, mint Pass-219 handoff authority,
mutate VM81, perform canonical learning, promote truth, mint action authority,
activate a model, retain source payloads, or create authoritative float state.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.curriculum_advance_i33 import (
    PASS218_I33_COMPLETE_STATUS,
    _verify_advance_receipt,
)
from hhs_runtime.pass218.manifest_bound_i33_curriculum_advance_i47 import (
    PASS218_I47_COMPLETE_STATUS,
    _verify_proof as _verify_i47_proof,
    _verify_receipt as _verify_i47_receipt,
)

PASS218_I48_VERSION = "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-SEAL-V1"
PASS218_I48_SCOPE = "PASS218_MANIFEST_BOUND_CURRICULUM_COMPLETION_SEAL"
PASS218_I48_PROOF_SCHEMA = "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-PROOF-V1"
PASS218_I48_RECEIPT_SCHEMA = "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-RECEIPT-V1"
PASS218_I48_STATE_SCHEMA = "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-STATE-V1"
PASS218_I48_STATUS_SCHEMA = "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-STATUS-V1"
PASS218_I48_COMPLETE_STATUS = "MANIFEST_BOUND_CURRICULUM_COMPLETION_SEALED"
PASS218_I48_PENDING_STATUS = "MANIFEST_BOUND_CURRICULUM_COMPLETION_PENDING"


class Pass218I48CompletionError(RuntimeError):
    pass


class Pass218I48BindingError(Pass218I48CompletionError):
    pass


class Pass218I48StateError(Pass218I48CompletionError):
    pass


class _Lifecycle(Protocol):
    def require_ingestion_ready(self) -> None: ...


class _I47Store(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class _I30Store(Protocol):
    def active_generation(self) -> dict[str, Any] | None: ...
    def status(self) -> dict[str, Any]: ...


class _I33Advancer(Protocol):
    authority: Any
    store: Any
    advance_count: int


def _no_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I48BindingError("P218_I48_AUTHORITATIVE_FLOAT_FORBIDDEN")
    if isinstance(value, Mapping):
        for item in value.values():
            _no_float(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            _no_float(item)


def _bytes(value: Any) -> bytes:
    _no_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _copy(value: Any) -> Any:
    return json.loads(_bytes(value).decode("utf-8"))


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(_bytes(value) + b"\n")
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


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass218I48StateError("P218_I48_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I48StateError("P218_I48_STATE_OBJECT_REQUIRED")
    return value


def _h72(value: object, field: str) -> str:
    text = str(value or "")
    if not validate_hash72(text):
        raise Pass218I48StateError("P218_I48_HASH72_INVALID:" + field)
    return text


def _sha(value: object, field: str) -> str:
    text = str(value or "")
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise Pass218I48StateError("P218_I48_SHA256_INVALID:" + field)
    return text


def _hash216(value: object, field: str) -> str:
    text = str(value or "")
    if len(text) != 216 or any(not validate_hash72(text[i : i + 72]) for i in (0, 72, 144)):
        raise Pass218I48StateError("P218_I48_HASH216_INVALID:" + field)
    return text


def _require_flags(
    value: Mapping[str, Any],
    *,
    yes: tuple[str, ...],
    no: tuple[str, ...],
    code: str,
) -> None:
    if any(value.get(field) is not True for field in yes):
        raise Pass218I48StateError(code)
    if any(value.get(field) is not False for field in no):
        raise Pass218I48StateError(code)


def _bind_i47(
    raw_receipt: Mapping[str, Any], raw_proof: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = _verify_i47_receipt(raw_receipt)
    proof = _verify_i47_proof(raw_proof, receipt)
    if receipt.get("status") != PASS218_I47_COMPLETE_STATUS:
        raise Pass218I48BindingError("P218_I48_I47_TERMINAL_COMPLETION_REQUIRED")
    if receipt.get("curriculum_status") != PASS218_I33_COMPLETE_STATUS:
        raise Pass218I48BindingError("P218_I48_I47_CURRICULUM_NOT_COMPLETE")
    if receipt.get("next_expected_source_id") is not None:
        raise Pass218I48BindingError("P218_I48_I47_NEXT_SOURCE_STILL_PRESENT")
    if receipt.get("next_expected_stage") is not None:
        raise Pass218I48BindingError("P218_I48_I47_NEXT_STAGE_STILL_PRESENT")
    if receipt.get("stage_transition_required") is not False:
        raise Pass218I48BindingError("P218_I48_I47_STAGE_TRANSITION_STILL_REQUIRED")
    if int(receipt.get("next_expected_ordinal", -1)) != int(receipt.get("curriculum_position", -2)) + 1:
        raise Pass218I48BindingError("P218_I48_I47_CURSOR_INCREMENT_INVALID")
    if proof.get("i30_generation_sha256") != receipt.get("i30_generation_sha256"):
        raise Pass218I48BindingError("P218_I48_I47_I30_PROOF_MISMATCH")
    return _copy(receipt), _copy(proof)


def _bind_i33(
    i47: Mapping[str, Any], proof47: Mapping[str, Any], i33_advancer: _I33Advancer
) -> dict[str, Any]:
    authority = i33_advancer.authority
    if authority is None:
        raise Pass218I48BindingError("P218_I48_I33_AUTHORITATIVE_CURRICULUM_REQUIRED")
    authority.validated()
    authority_record = authority.record()
    if authority_record.get("authority_root_hash72") != proof47.get("i33_authority_root_hash72"):
        raise Pass218I48BindingError("P218_I48_I33_AUTHORITY_ROOT_MISMATCH")
    if authority.manifest.manifest_hash72 != proof47.get("i33_manifest_hash72"):
        raise Pass218I48BindingError("P218_I48_I33_MANIFEST_HASH_MISMATCH")
    if authority.manifest.curriculum_identity_hash72 != i47.get("curriculum_identity_hash72"):
        raise Pass218I48BindingError("P218_I48_I33_CURRICULUM_IDENTITY_MISMATCH")

    raw_advance = i33_advancer.store.last_receipt()
    if not isinstance(raw_advance, Mapping):
        raise Pass218I48BindingError("P218_I48_I33_TERMINAL_RECEIPT_REQUIRED")
    advance = _verify_advance_receipt(raw_advance)
    if advance.get("advance_receipt_hash72") != i47.get("i33_advance_receipt_hash72"):
        raise Pass218I48BindingError("P218_I48_I33_RECEIPT_I47_MISMATCH")
    if advance.get("advance_status") != PASS218_I33_COMPLETE_STATUS:
        raise Pass218I48BindingError("P218_I48_I33_TERMINAL_STATUS_REQUIRED")
    if advance.get("next_expected_source_id") is not None or advance.get("next_expected_stage") is not None:
        raise Pass218I48BindingError("P218_I48_I33_NEXT_EXPECTATION_NOT_EMPTY")
    if advance.get("stage_transition_required") is not False:
        raise Pass218I48BindingError("P218_I48_I33_STAGE_TRANSITION_NOT_CLOSED")

    cursor = i33_advancer.store.current_cursor(authority)
    if cursor.expected_source(authority.manifest) is not None:
        raise Pass218I48BindingError("P218_I48_I33_CURSOR_NOT_EXHAUSTED")
    source_count = len(authority.manifest.sources)
    if cursor.next_ordinal != source_count:
        raise Pass218I48BindingError("P218_I48_I33_CURSOR_SOURCE_COUNT_MISMATCH")
    if cursor.next_ordinal != int(i47.get("next_expected_ordinal", -1)):
        raise Pass218I48BindingError("P218_I48_I33_CURSOR_I47_ORDINAL_MISMATCH")
    if cursor.last_closure_hash72 != i47.get("i32_source_closure_hash72"):
        raise Pass218I48BindingError("P218_I48_I33_CURSOR_CLOSURE_MISMATCH")

    state = i33_advancer.store.state_record()
    if not isinstance(state, Mapping):
        raise Pass218I48BindingError("P218_I48_I33_DURABLE_STATE_REQUIRED")
    if state.get("last_advance_receipt_hash72") != advance.get("advance_receipt_hash72"):
        raise Pass218I48BindingError("P218_I48_I33_STATE_RECEIPT_MISMATCH")
    if int(state.get("advance_count", -1)) != source_count:
        raise Pass218I48BindingError("P218_I48_I33_STATE_ADVANCE_COUNT_MISMATCH")

    cursor_record = cursor.record()
    cursor_sha = sha256(_bytes(cursor_record)).hexdigest()
    if cursor_sha != advance.get("cursor_state_sha256") or cursor_sha != i47.get("i33_cursor_state_sha256"):
        raise Pass218I48BindingError("P218_I48_I33_CURSOR_SHA_MISMATCH")

    return {
        "i33_authority_root_hash72": authority_record["authority_root_hash72"],
        "i33_manifest_hash72": authority.manifest.manifest_hash72,
        "curriculum_identity_hash72": authority.manifest.curriculum_identity_hash72,
        "manifest_source_count": source_count,
        "completed_source_count": cursor.next_ordinal,
        "final_cursor": cursor_record,
        "final_cursor_sha256": cursor_sha,
        "final_closure_hash72": cursor.last_closure_hash72,
        "i33_advance_receipt_hash72": advance["advance_receipt_hash72"],
        "i33_transition_hash72": advance["transition_hash72"],
        "i33_advance_hash216": advance["advance_hash216"],
        "curriculum_status": advance["advance_status"],
    }


def _verify_i30(
    generation: Mapping[str, Any], status: Mapping[str, Any], i47: Mapping[str, Any], proof47: Mapping[str, Any]
) -> tuple[dict[str, Any], str]:
    value = _copy(dict(generation))
    digest = sha256(_bytes(value)).hexdigest()
    if digest != i47.get("i30_generation_sha256") or digest != proof47.get("i30_generation_sha256"):
        raise Pass218I48BindingError("P218_I48_I30_GENERATION_I47_MISMATCH")
    receipt = value.get("promotion_receipt")
    promoted = value.get("promoted_object")
    if not isinstance(receipt, Mapping) or not isinstance(promoted, Mapping):
        raise Pass218I48BindingError("P218_I48_I30_GENERATION_CONTENT_INVALID")
    if status.get("promotion_present") is not True:
        raise Pass218I48BindingError("P218_I48_I30_PROMOTION_REQUIRED")
    if status.get("canonical_root_hash72") != proof47.get("i30_canonical_root_hash72"):
        raise Pass218I48BindingError("P218_I48_I30_CANONICAL_ROOT_MISMATCH")
    if receipt.get("target_root_after_hash72") != proof47.get("i30_canonical_root_hash72"):
        raise Pass218I48BindingError("P218_I48_I30_RECEIPT_ROOT_MISMATCH")
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
            raise Pass218I48BindingError("P218_I48_I30_AUTHORITY_DRIFT:" + field)
    return value, digest


def _verify_receipt(value: Mapping[str, Any]) -> dict[str, Any]:
    record = _copy(dict(value))
    if record.get("schema") != PASS218_I48_RECEIPT_SCHEMA:
        raise Pass218I48StateError("P218_I48_RECEIPT_SCHEMA_INVALID")
    if record.get("status") != PASS218_I48_COMPLETE_STATUS:
        raise Pass218I48StateError("P218_I48_RECEIPT_STATUS_INVALID")
    if record.get("curriculum_status") != PASS218_I33_COMPLETE_STATUS:
        raise Pass218I48StateError("P218_I48_RECEIPT_CURRICULUM_STATUS_INVALID")
    for field in (
        "i47_receipt_hash72",
        "i33_advance_receipt_hash72",
        "final_closure_hash72",
        "curriculum_completion_proof_hash72",
        "i48_validation_hash72",
        "i48_receipt_hash72",
    ):
        _h72(record.get(field), field)
    for field in ("i30_generation_sha256", "final_cursor_sha256"):
        _sha(record.get(field), field)
    _hash216(record.get("i48_hash216"), "i48_hash216")
    if record.get("next_expected_source_id") is not None or record.get("next_expected_stage") is not None:
        raise Pass218I48StateError("P218_I48_RECEIPT_NEXT_EXPECTATION_PRESENT")
    if record.get("stage_transition_required") is not False:
        raise Pass218I48StateError("P218_I48_RECEIPT_STAGE_TRANSITION_PRESENT")
    _require_flags(
        record,
        yes=(
            "i47_manifest_bound_curriculum_advance_verified",
            "i33_terminal_completion_receipt_verified",
            "authoritative_manifest_exhausted",
            "final_cursor_exhausted",
            "final_cursor_source_count_matches_manifest",
            "no_next_expected_source_verified",
            "i30_semantic_generation_unchanged_at_completion",
            "i30_canonical_root_unchanged_at_completion",
            "restart_safe_completion_seal",
        ),
        no=(
            "i33_curriculum_advance_invoked",
            "next_source_ingress_invoked",
            "stage_advance_invoked",
            "stage_advance_permitted",
            "pass219_handoff_authority_minted",
            "vm81_authorization_invoked",
            "canonical_learning_commit_invoked",
            "truth_promotion",
            "action_authority_minted",
            "model_activation_invoked",
            "verbatim_corpus_source_retained",
            "physical_memory_erasure_claimed",
            "external_source_storage_erasure_claimed",
            "authoritative_float_weights_created",
        ),
        code="P218_I48_RECEIPT_AUTHORITY_DRIFT",
    )
    if int(record.get("manifest_source_count", -1)) < 0:
        raise Pass218I48StateError("P218_I48_RECEIPT_SOURCE_COUNT_INVALID")
    if record.get("completed_source_count") != record.get("manifest_source_count"):
        raise Pass218I48StateError("P218_I48_RECEIPT_SOURCE_COUNT_MISMATCH")
    body = {
        key: item
        for key, item in record.items()
        if key not in {"i48_receipt_hash72", "i48_hash216", "i48_hash216_semantics"}
    }
    expected = hash72_digest({"domain": PASS218_I48_RECEIPT_SCHEMA}, body)
    if expected != record.get("i48_receipt_hash72"):
        raise Pass218I48StateError("P218_I48_RECEIPT_HASH_MISMATCH")
    expected216 = str(record["i47_receipt_hash72"]) + str(record["i33_advance_receipt_hash72"]) + expected
    if record.get("i48_hash216") != expected216:
        raise Pass218I48StateError("P218_I48_HASH216_MISMATCH")
    return record


def _verify_proof(
    value: Mapping[str, Any], receipt: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    record = _copy(dict(value))
    if record.get("schema") != PASS218_I48_PROOF_SCHEMA:
        raise Pass218I48StateError("P218_I48_PROOF_SCHEMA_INVALID")
    if record.get("status") != PASS218_I48_COMPLETE_STATUS:
        raise Pass218I48StateError("P218_I48_PROOF_STATUS_INVALID")
    _h72(record.get("curriculum_completion_proof_hash72"), "curriculum_completion_proof_hash72")
    if record.get("completed_source_count") != record.get("manifest_source_count"):
        raise Pass218I48StateError("P218_I48_PROOF_SOURCE_COUNT_MISMATCH")
    _require_flags(
        record,
        yes=(
            "i47_manifest_bound_curriculum_advance_verified",
            "i33_terminal_completion_receipt_verified",
            "authoritative_manifest_exhausted",
            "final_cursor_exhausted",
            "final_cursor_source_count_matches_manifest",
            "no_next_expected_source_verified",
            "i30_semantic_generation_unchanged_at_completion",
            "i30_canonical_root_unchanged_at_completion",
            "restart_safe_completion_seal",
        ),
        no=(
            "source_payload_persisted",
            "i33_curriculum_advance_invoked",
            "next_source_ingress_invoked",
            "stage_advance_invoked",
            "pass219_handoff_authority_minted",
            "vm81_authorization_invoked",
            "canonical_learning_commit_invoked",
            "truth_promotion",
            "action_authority_minted",
            "model_activation_invoked",
            "verbatim_corpus_source_retained",
            "authoritative_float_weights_created",
        ),
        code="P218_I48_PROOF_AUTHORITY_DRIFT",
    )
    body = {key: item for key, item in record.items() if key != "curriculum_completion_proof_hash72"}
    expected = hash72_digest({"domain": PASS218_I48_PROOF_SCHEMA}, body)
    if expected != record.get("curriculum_completion_proof_hash72"):
        raise Pass218I48StateError("P218_I48_PROOF_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get("curriculum_completion_proof_hash72"):
        raise Pass218I48StateError("P218_I48_PROOF_RECEIPT_MISMATCH")
    return record


class Pass218I48CompletionStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_path = self.root / "receipt.json"
        self.proof_path = self.root / "proof.json"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _read(self.state_path)
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if state.get("schema") != PASS218_I48_STATE_SCHEMA:
            raise Pass218I48StateError("P218_I48_STATE_SCHEMA_INVALID")
        if hash72_digest({"domain": PASS218_I48_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I48StateError("P218_I48_STATE_ROOT_MISMATCH")
        receipt = _verify_receipt(_read(self.receipt_path))
        proof = _verify_proof(_read(self.proof_path), receipt)
        if state.get("active_i48_receipt_hash72") != receipt.get("i48_receipt_hash72"):
            raise Pass218I48StateError("P218_I48_STATE_RECEIPT_MISMATCH")
        if state.get("active_completion_proof_hash72") != proof.get("curriculum_completion_proof_hash72"):
            raise Pass218I48StateError("P218_I48_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        return None if receipt is None else _verify_proof(_read(self.proof_path), receipt)

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_receipt(receipt)
        checked_proof = _verify_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I48StateError("P218_I48_ACTIVE_BINDING_CONFLICT")
            return existing
        _write(self.receipt_path, checked)
        _write(self.proof_path, checked_proof)
        state_body = {
            "schema": PASS218_I48_STATE_SCHEMA,
            "version": PASS218_I48_VERSION,
            "status": PASS218_I48_COMPLETE_STATUS,
            "curriculum_status": PASS218_I33_COMPLETE_STATUS,
            "active_i48_receipt_hash72": checked["i48_receipt_hash72"],
            "active_completion_proof_hash72": checked_proof["curriculum_completion_proof_hash72"],
            "final_cursor_sha256": checked["final_cursor_sha256"],
            "manifest_source_count": checked["manifest_source_count"],
            "completed_source_count": checked["completed_source_count"],
        }
        _write(
            self.state_path,
            {
                **state_body,
                "state_root_hash72": hash72_digest(
                    {"domain": PASS218_I48_STATE_SCHEMA}, state_body
                ),
            },
        )
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I48StateError("P218_I48_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I48ManifestBoundCurriculumCompletionSeal:
    def __init__(
        self,
        *,
        lifecycle: _Lifecycle,
        i47_store: _I47Store,
        i30_store: _I30Store,
        i33_advancer: _I33Advancer,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.lifecycle = lifecycle
        self.i47_store = i47_store
        self.i30_store = i30_store
        self.i33_advancer = i33_advancer
        self.store = Pass218I48CompletionStore(state_root)
        self.seal_count = 0
        self.restart_adoption_count = 0
        self.last_error_code: str | None = None

    def _inputs(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
        raw_i47 = self.i47_store.active_record()
        raw_proof = self.i47_store.active_proof()
        if not isinstance(raw_i47, Mapping) or not isinstance(raw_proof, Mapping):
            raise Pass218I48BindingError("P218_I48_I47_TERMINAL_COMPLETION_REQUIRED")
        i47, proof47 = _bind_i47(raw_i47, raw_proof)
        i33 = _bind_i33(i47, proof47, self.i33_advancer)
        generation = self.i30_store.active_generation()
        if not isinstance(generation, Mapping):
            raise Pass218I48BindingError("P218_I48_I30_DURABLE_GENERATION_REQUIRED")
        generation_value, digest = _verify_i30(
            generation, self.i30_store.status(), i47, proof47
        )
        return i47, proof47, i33, generation_value, digest

    @staticmethod
    def _build(
        i47: Mapping[str, Any],
        proof47: Mapping[str, Any],
        i33: Mapping[str, Any],
        i30_sha: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        common = {
            "curriculum_status": PASS218_I33_COMPLETE_STATUS,
            "i47_receipt_hash72": i47["i47_receipt_hash72"],
            "i33_advance_receipt_hash72": i33["i33_advance_receipt_hash72"],
            "i33_transition_hash72": i33["i33_transition_hash72"],
            "i33_authority_root_hash72": i33["i33_authority_root_hash72"],
            "i33_manifest_hash72": i33["i33_manifest_hash72"],
            "curriculum_identity_hash72": i33["curriculum_identity_hash72"],
            "manifest_source_count": i33["manifest_source_count"],
            "completed_source_count": i33["completed_source_count"],
            "final_cursor_sha256": i33["final_cursor_sha256"],
            "final_closure_hash72": i33["final_closure_hash72"],
            "i30_generation_sha256": i30_sha,
            "i30_canonical_root_hash72": proof47["i30_canonical_root_hash72"],
            "next_expected_ordinal": i47["next_expected_ordinal"],
            "next_expected_source_id": None,
            "next_expected_stage": None,
            "stage_transition_required": False,
        }
        true_flags = {
            "i47_manifest_bound_curriculum_advance_verified": True,
            "i33_terminal_completion_receipt_verified": True,
            "authoritative_manifest_exhausted": True,
            "final_cursor_exhausted": True,
            "final_cursor_source_count_matches_manifest": True,
            "no_next_expected_source_verified": True,
            "i30_semantic_generation_unchanged_at_completion": True,
            "i30_canonical_root_unchanged_at_completion": True,
            "restart_safe_completion_seal": True,
        }
        false_flags = {
            "i33_curriculum_advance_invoked": False,
            "next_source_ingress_invoked": False,
            "stage_advance_invoked": False,
            "stage_advance_permitted": False,
            "pass219_handoff_authority_minted": False,
            "vm81_authorization_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "physical_memory_erasure_claimed": False,
            "external_source_storage_erasure_claimed": False,
            "authoritative_float_weights_created": False,
        }
        proof_body = {
            "schema": PASS218_I48_PROOF_SCHEMA,
            "version": PASS218_I48_VERSION,
            "scope": PASS218_I48_SCOPE,
            "status": PASS218_I48_COMPLETE_STATUS,
            **common,
            "source_payload_persisted": False,
            **true_flags,
            **false_flags,
        }
        proof_hash = hash72_digest({"domain": PASS218_I48_PROOF_SCHEMA}, proof_body)
        proof = {**proof_body, "curriculum_completion_proof_hash72": proof_hash}
        validation_hash = hash72_digest(
            {"domain": "HHS-P218-I48-CURRICULUM-COMPLETION-VALIDATION-V1"},
            {
                "i47_receipt_hash72": i47["i47_receipt_hash72"],
                "i33_advance_receipt_hash72": i33["i33_advance_receipt_hash72"],
                "i30_generation_sha256": i30_sha,
                "manifest_source_count": i33["manifest_source_count"],
                "completed_source_count": i33["completed_source_count"],
                "final_cursor_sha256": i33["final_cursor_sha256"],
            },
        )
        receipt_body = {
            "schema": PASS218_I48_RECEIPT_SCHEMA,
            "version": PASS218_I48_VERSION,
            "scope": PASS218_I48_SCOPE,
            "status": PASS218_I48_COMPLETE_STATUS,
            **common,
            "curriculum_completion_proof_hash72": proof_hash,
            "i48_validation_hash72": validation_hash,
            **true_flags,
            **false_flags,
        }
        receipt_hash = hash72_digest({"domain": PASS218_I48_RECEIPT_SCHEMA}, receipt_body)
        receipt = {
            **receipt_body,
            "i48_receipt_hash72": receipt_hash,
            "i48_hash216": str(i47["i47_receipt_hash72"])
            + str(i33["i33_advance_receipt_hash72"])
            + receipt_hash,
            "i48_hash216_semantics": [
                "I47_MANIFEST_BOUND_CURRICULUM_ADVANCE_RECEIPT",
                "I33_TERMINAL_CURRICULUM_ADVANCE_RECEIPT",
                "I48_CURRICULUM_COMPLETION_SEAL_RECEIPT",
            ],
        }
        return _verify_proof(proof), _verify_receipt(receipt)

    def seal(self) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i47, proof47, i33, before, before_sha = self._inputs()
            active = self.store.active_record()
            if active is not None:
                if active.get("i47_receipt_hash72") != i47.get("i47_receipt_hash72"):
                    raise Pass218I48StateError("P218_I48_ACTIVE_I47_BINDING_CONFLICT")
                if active.get("i33_advance_receipt_hash72") != i33.get("i33_advance_receipt_hash72"):
                    raise Pass218I48StateError("P218_I48_ACTIVE_I33_BINDING_CONFLICT")
                if active.get("i30_generation_sha256") != before_sha:
                    raise Pass218I48StateError("P218_I48_ACTIVE_I30_BINDING_CONFLICT")
                self.restart_adoption_count += 1
                return active
            advance_count_before = int(self.i33_advancer.advance_count)
            _, _, i33_after, after, after_sha = self._inputs()
            if int(self.i33_advancer.advance_count) != advance_count_before:
                raise Pass218I48StateError("P218_I48_I33_ADVANCE_OCCURRED_DURING_SEAL")
            if i33_after != i33:
                raise Pass218I48StateError("P218_I48_I33_TERMINAL_STATE_CHANGED_DURING_SEAL")
            if before != after or before_sha != after_sha:
                raise Pass218I48StateError("P218_I48_I30_CHANGED_DURING_SEAL")
            proof, receipt = self._build(i47, proof47, i33, before_sha)
            persisted = self.store.commit(receipt, proof)
            self.seal_count += 1
            self.last_error_code = None
            return persisted
        except Exception as exc:
            text = str(exc).strip()
            self.last_error_code = text.split(":", 1)[0] if text else exc.__class__.__name__
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        return {
            "schema": PASS218_I48_STATUS_SCHEMA,
            "version": PASS218_I48_VERSION,
            "status": PASS218_I48_COMPLETE_STATUS if active is not None else PASS218_I48_PENDING_STATUS,
            "curriculum_status": None if active is None else active["curriculum_status"],
            "active_i48_receipt_hash72": None if active is None else active["i48_receipt_hash72"],
            "active_completion_proof_hash72": None if active is None else active["curriculum_completion_proof_hash72"],
            "manifest_source_count": None if active is None else active["manifest_source_count"],
            "completed_source_count": None if active is None else active["completed_source_count"],
            "final_cursor_sha256": None if active is None else active["final_cursor_sha256"],
            "authoritative_manifest_exhausted": bool(active and active["authoritative_manifest_exhausted"]),
            "no_next_expected_source_verified": bool(active and active["no_next_expected_source_verified"]),
            "seal_count_current_process": self.seal_count,
            "restart_adoption_count_current_process": self.restart_adoption_count,
            "i33_curriculum_advance_invoked": False,
            "next_source_ingress_invoked": False,
            "stage_advance_invoked": False,
            "pass219_handoff_authority_minted": False,
            "vm81_authorization_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
            "i48_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I48_COMPLETE_STATUS",
    "PASS218_I48_PENDING_STATUS",
    "PASS218_I48_PROOF_SCHEMA",
    "PASS218_I48_RECEIPT_SCHEMA",
    "PASS218_I48_SCOPE",
    "PASS218_I48_STATE_SCHEMA",
    "PASS218_I48_STATUS_SCHEMA",
    "PASS218_I48_VERSION",
    "Pass218I48BindingError",
    "Pass218I48CompletionError",
    "Pass218I48CompletionStore",
    "Pass218I48ManifestBoundCurriculumCompletionSeal",
    "Pass218I48StateError",
    "_verify_proof",
    "_verify_receipt",
]
