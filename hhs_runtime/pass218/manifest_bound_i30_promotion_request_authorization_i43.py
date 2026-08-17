"""Pass 218 Iteration 43 manifest-bound I30 promotion-request authorization.

I43 begins only from the exact durable I42 cross-lineage equality receipt/proof
and a caller-supplied transient frozen-I30 ``Pass218I30PromotionRequest``.  The
request is validated under the frozen I30 type, its embedded I29 request must
fingerprint exactly to the durable I42 request identity, and frozen I29 is
independently replayed again before any authority is sealed.

The separate caller-supplied I30 grant is bound only to that exact revalidated
candidate.  I43 derives the exact Hash72 grant that frozen I30 would derive, then
persists a non-executing authorization receipt.  The transient I29/I30 request is
not persisted and the I30 promoter is never called here.

Completion therefore means AUTHORIZED_PENDING_I30_INVOCATION.  I43 performs no
VM5184 authoritative projection, semantic-store mutation, purge/closure,
curriculum advance, canonical learning, truth/action authority, model activation,
source retention, or authoritative floating-point state creation.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_TARGET_SCOPE,
    Pass218I30PromotionRequest,
)
from hhs_runtime.pass218.manifest_semantic_cross_lineage_equality_i42 import (
    PASS218_I42_COMPLETE_STATUS,
    _request_record as _i42_request_record,
    _verify_i29_result,
    _verify_i42_proof,
    _verify_i42_receipt,
)

PASS218_I43_VERSION = "HHS-P218-I43-MANIFEST-BOUND-I30-PROMOTION-REQUEST-AUTHORIZATION-V1"
PASS218_I43_SCOPE = "PASS218_MANIFEST_BOUND_I30_PROMOTION_REQUEST_AUTHORIZATION"
PASS218_I43_PROOF_SCHEMA = "HHS-P218-I43-MANIFEST-BOUND-I30-PROMOTION-REQUEST-AUTHORIZATION-PROOF-V1"
PASS218_I43_RECEIPT_SCHEMA = "HHS-P218-I43-MANIFEST-BOUND-I30-PROMOTION-REQUEST-AUTHORIZATION-RECEIPT-V1"
PASS218_I43_STATE_SCHEMA = "HHS-P218-I43-MANIFEST-BOUND-I30-PROMOTION-REQUEST-AUTHORIZATION-STATE-V1"
PASS218_I43_STATUS_SCHEMA = "HHS-P218-I43-MANIFEST-BOUND-I30-PROMOTION-REQUEST-AUTHORIZATION-STATUS-V1"
PASS218_I43_COMPLETE_STATUS = "MANIFEST_BOUND_I30_PROMOTION_REQUEST_AUTHORIZATION_COMPLETE"
PASS218_I43_PENDING_STATUS = "MANIFEST_BOUND_I30_PROMOTION_REQUEST_AUTHORIZATION_PENDING"
PASS218_I43_AUTHORIZED_PENDING_STATUS = "AUTHORIZED_PENDING_I30_INVOCATION"
_I30_GRANT_DOMAIN = "HHS-P218-I30-PROMOTION-AUTHORITY-GRANT-V1"


class Pass218I43AuthorizationError(RuntimeError):
    pass


class Pass218I43BindingError(Pass218I43AuthorizationError):
    pass


class Pass218I43StateError(Pass218I43AuthorizationError):
    pass


class Pass218I43LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I43I42StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class Pass218I43I29ValidatorProtocol(Protocol):
    def validate(self, request: Any) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I43BindingError("P218_I43_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        raise Pass218I43StateError("P218_I43_PATH_HASH72_INVALID")
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
        raise Pass218I43StateError("P218_I43_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I43StateError("P218_I43_STATE_OBJECT_REQUIRED")
    return value


def _i30_request_record(request: Pass218I30PromotionRequest) -> dict[str, Any]:
    validated = request.validated()
    if not is_dataclass(validated):
        raise Pass218I43BindingError("P218_I43_I30_TYPED_REQUEST_REQUIRED")
    record = asdict(validated)
    if not isinstance(record, dict):
        raise Pass218I43BindingError("P218_I43_I30_REQUEST_RECORD_INVALID")
    return _copy(record)


def _i29_request_sha256(request: Pass218I30PromotionRequest) -> str:
    record = _i42_request_record(request.validation_request)
    return sha256(_canonical_bytes(record)).hexdigest()


def _i30_request_sha256(request: Pass218I30PromotionRequest) -> str:
    return sha256(_canonical_bytes(_i30_request_record(request))).hexdigest()


def _derive_exact_i30_grant(
    request: Pass218I30PromotionRequest,
    i29: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    witness = i29.get("semantic_validation_witness")
    if not isinstance(witness, Mapping):
        raise Pass218I43BindingError("P218_I43_I29_SEMANTIC_WITNESS_REQUIRED")
    semantic_witness_hash72 = str(witness.get("semantic_witness_hash72") or "")
    if not validate_hash72(semantic_witness_hash72):
        raise Pass218I43BindingError("P218_I43_I29_SEMANTIC_WITNESS_INVALID")
    grant_body = {
        "grantor_authority_hash72": request.grantor_authority_hash72,
        "grant_sequence": request.grant_sequence,
        "target_scope": request.target_scope,
        "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
        "validated_hash216": i29["pass218_validated_hash216"],
        "semantic_witness_hash72": semantic_witness_hash72,
        "explicit_authority_grant_present": True,
        "grant_authorizes_only_exact_validated_candidate": True,
        "truth_promotion": False,
        "action_authority_minted": False,
        "learning_authority_granted": False,
    }
    grant_hash72 = hash72_digest({"domain": _I30_GRANT_DOMAIN}, grant_body)
    return grant_body, grant_hash72


def _verify_i43_proof(
    proof: Mapping[str, Any],
    receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value = _copy(dict(proof))
    if value.get("schema") != PASS218_I43_PROOF_SCHEMA:
        raise Pass218I43StateError("P218_I43_PROOF_SCHEMA_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I43StateError("P218_I43_TARGET_SCOPE_INVALID")
    if value.get("authorization_status") != PASS218_I43_AUTHORIZED_PENDING_STATUS:
        raise Pass218I43StateError("P218_I43_AUTHORIZATION_STATUS_INVALID")
    for field in (
        "i42_receipt_hash72",
        "i42_cross_lineage_equality_hash72",
        "i29_validation_hash72",
        "i29_semantic_witness_hash72",
        "grantor_authority_hash72",
        "i30_grant_hash72",
        "manifest_bound_i30_request_authorization_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I43StateError("P218_I43_PROOF_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i42_hash216")):
        raise Pass218I43StateError("P218_I43_I42_HASH216_INVALID")
    if not _valid_hash216(value.get("i29_validated_hash216")):
        raise Pass218I43StateError("P218_I43_I29_HASH216_INVALID")
    for field in ("i29_validation_request_sha256", "i30_promotion_request_sha256"):
        if not _valid_sha256(value.get(field)):
            raise Pass218I43StateError("P218_I43_PROOF_SHA256_INVALID:" + field)
    sequence = value.get("grant_sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        raise Pass218I43StateError("P218_I43_GRANT_SEQUENCE_INVALID")
    required_true = (
        "i42_receipt_bound",
        "i42_cross_lineage_proof_bound",
        "i29_request_fingerprint_matches_i42",
        "i29_independently_revalidated",
        "i29_validation_identity_matches_i42",
        "i29_validated_hash216_matches_i42",
        "i29_semantic_witness_matches_i42",
        "i30_typed_request_validated",
        "i30_explicit_authority_grant_present",
        "i30_grant_authorizes_only_exact_validated_candidate",
        "i30_grant_hash_matches_frozen_i30_derivation",
        "i30_promotion_request_authorized",
        "authorized_pending_i30_invocation",
        "proof_non_executing",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I43StateError("P218_I43_PROOF_INCOMPLETE")
    required_false = (
        "i29_validation_request_persisted",
        "i30_promotion_request_persisted",
        "source_payload_persisted",
        "vm5184_authoritative_projection_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I43StateError("P218_I43_PROOF_AUTHORITY_DRIFT")
    body = {
        key: item
        for key, item in value.items()
        if key != "manifest_bound_i30_request_authorization_hash72"
    }
    expected = hash72_digest({"domain": PASS218_I43_PROOF_SCHEMA}, body)
    if expected != value.get("manifest_bound_i30_request_authorization_hash72"):
        raise Pass218I43StateError("P218_I43_PROOF_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get(
        "manifest_bound_i30_request_authorization_hash72"
    ):
        raise Pass218I43StateError("P218_I43_PROOF_RECEIPT_MISMATCH")
    return value


def _verify_i43_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I43_RECEIPT_SCHEMA:
        raise Pass218I43StateError("P218_I43_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I43_COMPLETE_STATUS:
        raise Pass218I43StateError("P218_I43_RECEIPT_STATUS_INVALID")
    if value.get("authorization_status") != PASS218_I43_AUTHORIZED_PENDING_STATUS:
        raise Pass218I43StateError("P218_I43_RECEIPT_AUTHORIZATION_STATUS_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I43StateError("P218_I43_RECEIPT_TARGET_INVALID")
    for field in (
        "i42_receipt_hash72",
        "i42_cross_lineage_equality_hash72",
        "i29_validation_hash72",
        "grantor_authority_hash72",
        "i30_grant_hash72",
        "manifest_bound_i30_request_authorization_hash72",
        "i43_validation_hash72",
        "i43_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I43StateError("P218_I43_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i29_validated_hash216")):
        raise Pass218I43StateError("P218_I43_RECEIPT_I29_HASH216_INVALID")
    if not _valid_hash216(value.get("i43_hash216")):
        raise Pass218I43StateError("P218_I43_RECEIPT_HASH216_INVALID")
    if value["i43_hash216"] != (
        str(value["i42_receipt_hash72"])
        + str(value["i30_grant_hash72"])
        + str(value["i43_receipt_hash72"])
    ):
        raise Pass218I43StateError("P218_I43_HASH216_ORDER_INVALID")
    for field in ("i29_validation_request_sha256", "i30_promotion_request_sha256"):
        if not _valid_sha256(value.get(field)):
            raise Pass218I43StateError("P218_I43_RECEIPT_SHA256_INVALID:" + field)
    required_true = (
        "i42_exact_request_identity_bound",
        "i29_independently_revalidated",
        "i30_explicit_authority_grant_present",
        "i30_grant_hash_matches_frozen_i30_derivation",
        "i30_promotion_request_authorized",
        "authorized_pending_i30_invocation",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I43StateError("P218_I43_RECEIPT_AUTHORIZATION_INCOMPLETE")
    required_false = (
        "i29_validation_request_persisted",
        "i30_promotion_request_persisted",
        "vm5184_authoritative_projection_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I43StateError("P218_I43_RECEIPT_AUTHORITY_DRIFT")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i43_receipt_hash72", "i43_hash216", "i43_hash216_semantics"}
    }
    expected = hash72_digest({"domain": PASS218_I43_RECEIPT_SCHEMA}, body)
    if expected != value.get("i43_receipt_hash72"):
        raise Pass218I43StateError("P218_I43_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I43AuthorizationStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.proof_root = self.root / "proofs"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I43_STATE_SCHEMA:
            raise Pass218I43StateError("P218_I43_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        expected = hash72_digest({"domain": PASS218_I43_STATE_SCHEMA}, body)
        if expected != state.get("state_root_hash72"):
            raise Pass218I43StateError("P218_I43_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        proof_path = self.root / str(state.get("active_proof_path", ""))
        if not receipt_path.is_file() or not proof_path.is_file():
            raise Pass218I43StateError("P218_I43_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i43_receipt(_load_json(receipt_path))
        proof = _verify_i43_proof(_load_json(proof_path), receipt)
        if receipt["i43_receipt_hash72"] != state.get("active_i43_receipt_hash72"):
            raise Pass218I43StateError("P218_I43_STATE_RECEIPT_MISMATCH")
        if proof["manifest_bound_i30_request_authorization_hash72"] != state.get(
            "active_proof_hash72"
        ):
            raise Pass218I43StateError("P218_I43_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i43_proof(
            _load_json(self.root / str(state["active_proof_path"])),
            receipt,
        )

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i43_receipt(receipt)
        checked_proof = _verify_i43_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I43StateError("P218_I43_ACTIVE_BINDING_CONFLICT")
            return existing
        sequence = int(checked["grant_sequence"])
        receipt_name = _path_safe_hash72_name(str(checked["i43_receipt_hash72"]))
        proof_name = _path_safe_hash72_name(
            str(checked_proof["manifest_bound_i30_request_authorization_hash72"])
        )
        receipt_path = self.receipt_root / f"{sequence:08d}-{receipt_name}.json"
        proof_path = self.proof_root / f"{proof_name}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(proof_path, checked_proof)
        state_body = {
            "schema": PASS218_I43_STATE_SCHEMA,
            "version": PASS218_I43_VERSION,
            "status": PASS218_I43_COMPLETE_STATUS,
            "authorization_status": PASS218_I43_AUTHORIZED_PENDING_STATUS,
            "i42_receipt_hash72": checked["i42_receipt_hash72"],
            "active_i43_receipt_hash72": checked["i43_receipt_hash72"],
            "active_proof_hash72": checked_proof[
                "manifest_bound_i30_request_authorization_hash72"
            ],
            "i29_validation_request_sha256": checked["i29_validation_request_sha256"],
            "i30_promotion_request_sha256": checked["i30_promotion_request_sha256"],
            "i30_grant_hash72": checked["i30_grant_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_proof_path": proof_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest({"domain": PASS218_I43_STATE_SCHEMA}, state_body),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I43StateError("P218_I43_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I43ManifestBoundI30PromotionRequestAuthorization:
    def __init__(
        self,
        *,
        lifecycle: Pass218I43LifecycleProtocol,
        i42_store: Pass218I43I42StoreProtocol,
        i29_validator: Pass218I43I29ValidatorProtocol,
        state_root: str | os.PathLike[str],
        i42_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        i30_status_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i42_store = i42_store
        self.i29_validator = i29_validator
        self.store = Pass218I43AuthorizationStore(state_root)
        self.i42_status_provider = i42_status_provider
        self.i30_status_provider = i30_status_provider
        self.authorization_count = 0
        self.i29_validation_count = 0
        self.i30_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_i42(self) -> tuple[dict[str, Any], dict[str, Any]]:
        receipt = self.i42_store.active_record()
        proof = self.i42_store.active_proof()
        if not isinstance(receipt, Mapping) or not isinstance(proof, Mapping):
            raise Pass218I43BindingError("P218_I43_I42_COMPLETE_STATE_REQUIRED")
        checked = _verify_i42_receipt(receipt)
        checked_proof = _verify_i42_proof(proof, checked)
        if checked.get("status") != PASS218_I42_COMPLETE_STATUS:
            raise Pass218I43BindingError("P218_I43_I42_COMPLETE_STATUS_REQUIRED")
        if self.i42_status_provider is not None:
            status = dict(self.i42_status_provider())
            if status.get("status") != PASS218_I42_COMPLETE_STATUS:
                raise Pass218I43BindingError("P218_I43_I42_STATUS_NOT_COMPLETE")
            if status.get("active_i42_receipt_hash72") != checked["i42_receipt_hash72"]:
                raise Pass218I43BindingError("P218_I43_I42_STATUS_RECEIPT_MISMATCH")
            if status.get("i29_validation_request_sha256") != checked[
                "i29_validation_request_sha256"
            ]:
                raise Pass218I43BindingError("P218_I43_I42_STATUS_REQUEST_MISMATCH")
        return checked, checked_proof

    def _require_i30_preflight(self) -> None:
        if self.i30_status_provider is None:
            return
        status = dict(self.i30_status_provider())
        if status.get("target_scope") not in {None, PASS218_I30_TARGET_SCOPE}:
            raise Pass218I43BindingError("P218_I43_I30_TARGET_SCOPE_MISMATCH")
        if bool(status.get("promotion_present")) or bool(status.get("atomic_promotion_invoked")):
            raise Pass218I43BindingError("P218_I43_I30_PREVIOUS_PROMOTION_PENDING")

    @staticmethod
    def _verify_replayed_i29(
        *,
        i42: Mapping[str, Any],
        i42_proof: Mapping[str, Any],
        request: Pass218I30PromotionRequest,
        i29: Mapping[str, Any],
    ) -> None:
        validation_hash72 = str(i29["hash216_vm5184_validation_hash72"])
        validated_hash216 = str(i29["pass218_validated_hash216"])
        if validation_hash72 != i42["i29_validation_hash72"]:
            raise Pass218I43BindingError("P218_I43_I29_VALIDATION_HASH_I42_MISMATCH")
        if validation_hash72 != i42_proof["i29_validation_hash72"]:
            raise Pass218I43BindingError("P218_I43_I29_VALIDATION_HASH_PROOF_MISMATCH")
        if validation_hash72 != request.expected_i29_validation_hash72:
            raise Pass218I43BindingError("P218_I43_I30_EXPECTED_I29_VALIDATION_MISMATCH")
        if validated_hash216 != i42["i29_validated_hash216"]:
            raise Pass218I43BindingError("P218_I43_I29_HASH216_I42_MISMATCH")
        if validated_hash216 != i42_proof["i29_validated_hash216"]:
            raise Pass218I43BindingError("P218_I43_I29_HASH216_PROOF_MISMATCH")
        if validated_hash216 != request.expected_validated_hash216:
            raise Pass218I43BindingError("P218_I43_I30_EXPECTED_HASH216_MISMATCH")
        segments = i29["pass218_validated_hash216_segments"]
        if segments["manifest_curriculum_hash72"] != i42_proof["i29_curriculum_hash72"]:
            raise Pass218I43BindingError("P218_I43_I29_CURRICULUM_SEGMENT_MISMATCH")
        if segments["hydrated_transition_state_hash72"] != i42_proof[
            "i29_transition_state_hash72"
        ]:
            raise Pass218I43BindingError("P218_I43_I29_TRANSITION_SEGMENT_MISMATCH")
        if segments["validation_receipt_hash72"] != i42_proof[
            "i29_validation_receipt_hash72"
        ]:
            raise Pass218I43BindingError("P218_I43_I29_RECEIPT_SEGMENT_MISMATCH")
        witness = i29["semantic_validation_witness"]
        if witness["semantic_witness_hash72"] != i42_proof["i29_semantic_witness_hash72"]:
            raise Pass218I43BindingError("P218_I43_I29_SEMANTIC_WITNESS_MISMATCH")

    def _build(
        self,
        *,
        i42: Mapping[str, Any],
        i42_proof: Mapping[str, Any],
        request: Pass218I30PromotionRequest,
        i29_request_sha256: str,
        i30_request_sha256: str,
        i29: Mapping[str, Any],
        grant_body: Mapping[str, Any],
        grant_hash72: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        proof_body = {
            "schema": PASS218_I43_PROOF_SCHEMA,
            "version": PASS218_I43_VERSION,
            "scope": PASS218_I43_SCOPE,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "authorization_status": PASS218_I43_AUTHORIZED_PENDING_STATUS,
            "i42_receipt_hash72": i42["i42_receipt_hash72"],
            "i42_cross_lineage_equality_hash72": i42[
                "cross_lineage_equality_hash72"
            ],
            "i42_hash216": i42["i42_hash216"],
            "i29_validation_request_sha256": i29_request_sha256,
            "i30_promotion_request_sha256": i30_request_sha256,
            "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
            "i29_validated_hash216": i29["pass218_validated_hash216"],
            "i29_semantic_witness_hash72": i29["semantic_validation_witness"][
                "semantic_witness_hash72"
            ],
            "grantor_authority_hash72": request.grantor_authority_hash72,
            "grant_sequence": request.grant_sequence,
            "i30_grant_hash72": grant_hash72,
            "grant_body": _copy(dict(grant_body)),
            "shared_identity": _copy(i42_proof["shared_identity"]),
            "i42_receipt_bound": True,
            "i42_cross_lineage_proof_bound": True,
            "i29_request_fingerprint_matches_i42": True,
            "i29_independently_revalidated": True,
            "i29_validation_identity_matches_i42": True,
            "i29_validated_hash216_matches_i42": True,
            "i29_semantic_witness_matches_i42": True,
            "i30_typed_request_validated": True,
            "i30_explicit_authority_grant_present": True,
            "i30_grant_authorizes_only_exact_validated_candidate": True,
            "i30_grant_hash_matches_frozen_i30_derivation": True,
            "i30_promotion_request_authorized": True,
            "authorized_pending_i30_invocation": True,
            "proof_non_executing": True,
            "i29_validation_request_persisted": False,
            "i30_promotion_request_persisted": False,
            "source_payload_persisted": False,
            "vm5184_authoritative_projection_invoked": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        proof_hash72 = hash72_digest({"domain": PASS218_I43_PROOF_SCHEMA}, proof_body)
        proof = {
            **proof_body,
            "manifest_bound_i30_request_authorization_hash72": proof_hash72,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I43-I30-PROMOTION-REQUEST-AUTHORIZATION-VALIDATION-V1"},
            {
                "i42_receipt_hash72": i42["i42_receipt_hash72"],
                "i42_cross_lineage_equality_hash72": i42[
                    "cross_lineage_equality_hash72"
                ],
                "i29_validation_request_sha256": i29_request_sha256,
                "i30_promotion_request_sha256": i30_request_sha256,
                "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
                "i29_validated_hash216": i29["pass218_validated_hash216"],
                "i30_grant_hash72": grant_hash72,
                "authorized_pending_i30_invocation": True,
                "i30_invoked": False,
            },
        )
        body = {
            "schema": PASS218_I43_RECEIPT_SCHEMA,
            "version": PASS218_I43_VERSION,
            "scope": PASS218_I43_SCOPE,
            "status": PASS218_I43_COMPLETE_STATUS,
            "authorization_status": PASS218_I43_AUTHORIZED_PENDING_STATUS,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i42_receipt_hash72": i42["i42_receipt_hash72"],
            "i42_cross_lineage_equality_hash72": i42[
                "cross_lineage_equality_hash72"
            ],
            "manifest_bound_i30_request_authorization_hash72": proof_hash72,
            "i29_validation_request_sha256": i29_request_sha256,
            "i30_promotion_request_sha256": i30_request_sha256,
            "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
            "i29_validated_hash216": i29["pass218_validated_hash216"],
            "grantor_authority_hash72": request.grantor_authority_hash72,
            "grant_sequence": request.grant_sequence,
            "i30_grant_hash72": grant_hash72,
            "i43_validation_hash72": validation_hash72,
            "i42_exact_request_identity_bound": True,
            "i29_independently_revalidated": True,
            "i30_explicit_authority_grant_present": True,
            "i30_grant_hash_matches_frozen_i30_derivation": True,
            "i30_promotion_request_authorized": True,
            "authorized_pending_i30_invocation": True,
            "i29_validation_request_persisted": False,
            "i30_promotion_request_persisted": False,
            "vm5184_authoritative_projection_invoked": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        receipt_hash72 = hash72_digest({"domain": PASS218_I43_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i43_receipt_hash72": receipt_hash72,
            "i43_hash216": i42["i42_receipt_hash72"] + grant_hash72 + receipt_hash72,
            "i43_hash216_semantics": [
                "I42_MANIFEST_SEMANTIC_CROSS_LINEAGE_EQUALITY_RECEIPT",
                "I30_EXACT_PROMOTION_AUTHORITY_GRANT",
                "I43_NON_EXECUTING_PROMOTION_REQUEST_AUTHORIZATION_RECEIPT",
            ],
        }
        return _verify_i43_proof(proof), _verify_i43_receipt(receipt)

    def authorize(self, promotion_request: Pass218I30PromotionRequest) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i42, i42_proof = self._active_i42()
            self._require_i30_preflight()
            request = promotion_request.validated()
            if request.target_scope != PASS218_I30_TARGET_SCOPE:
                raise Pass218I43BindingError("P218_I43_I30_TARGET_SCOPE_INVALID")
            i29_request_sha256 = _i29_request_sha256(request)
            if i29_request_sha256 != i42["i29_validation_request_sha256"]:
                raise Pass218I43BindingError("P218_I43_I29_REQUEST_FINGERPRINT_MISMATCH")
            if i29_request_sha256 != i42_proof["i29_validation_request_sha256"]:
                raise Pass218I43BindingError("P218_I43_I29_REQUEST_PROOF_FINGERPRINT_MISMATCH")
            i30_request_sha256 = _i30_request_sha256(request)
            existing = self.store.active_record()
            if existing is not None:
                if existing["i42_receipt_hash72"] != i42["i42_receipt_hash72"]:
                    raise Pass218I43StateError("P218_I43_ACTIVE_I42_CONFLICT")
                if existing["i29_validation_request_sha256"] != i29_request_sha256:
                    raise Pass218I43StateError("P218_I43_ACTIVE_I29_REQUEST_CONFLICT")
                if existing["i30_promotion_request_sha256"] != i30_request_sha256:
                    raise Pass218I43StateError("P218_I43_ACTIVE_I30_REQUEST_CONFLICT")
                self.last_error_code = None
                return existing
            i29 = _verify_i29_result(self.i29_validator.validate(request.validation_request))
            self.i29_validation_count += 1
            self._verify_replayed_i29(
                i42=i42,
                i42_proof=i42_proof,
                request=request,
                i29=i29,
            )
            grant_body, grant_hash72 = _derive_exact_i30_grant(request, i29)
            proof, receipt = self._build(
                i42=i42,
                i42_proof=i42_proof,
                request=request,
                i29_request_sha256=i29_request_sha256,
                i30_request_sha256=i30_request_sha256,
                i29=i29,
                grant_body=grant_body,
                grant_hash72=grant_hash72,
            )
            persisted = self.store.commit(receipt, proof)
            self.authorization_count += 1
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        predecessor_ready = False
        active_i42_receipt_hash72: str | None = None
        try:
            i42, _ = self._active_i42()
            predecessor_ready = True
            active_i42_receipt_hash72 = str(i42["i42_receipt_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I43_STATUS_SCHEMA,
            "version": PASS218_I43_VERSION,
            "status": PASS218_I43_COMPLETE_STATUS if active is not None else PASS218_I43_PENDING_STATUS,
            "authorization_status": (
                PASS218_I43_AUTHORIZED_PENDING_STATUS if active is not None else "NOT_AUTHORIZED"
            ),
            "predecessor_state_ready": predecessor_ready,
            "active_i42_receipt_hash72": active_i42_receipt_hash72,
            "active_i43_receipt_hash72": None if active is None else active["i43_receipt_hash72"],
            "i29_validation_request_sha256": None if active is None else active["i29_validation_request_sha256"],
            "i30_promotion_request_sha256": None if active is None else active["i30_promotion_request_sha256"],
            "i29_validation_hash72": None if active is None else active["i29_validation_hash72"],
            "i29_validated_hash216": None if active is None else active["i29_validated_hash216"],
            "i30_grant_hash72": None if active is None else active["i30_grant_hash72"],
            "grantor_authority_hash72": None if active is None else active["grantor_authority_hash72"],
            "grant_sequence": None if active is None else active["grant_sequence"],
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "authorization_count_current_process": self.authorization_count,
            "i29_validation_count_current_process": self.i29_validation_count,
            "i30_invocation_count_current_process": self.i30_invocation_count,
            "i30_promotion_request_authorized": active is not None,
            "authorized_pending_i30_invocation": active is not None,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "vm5184_authoritative_projection_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I43_AUTHORIZED_PENDING_STATUS",
    "PASS218_I43_COMPLETE_STATUS",
    "PASS218_I43_PENDING_STATUS",
    "PASS218_I43_PROOF_SCHEMA",
    "PASS218_I43_RECEIPT_SCHEMA",
    "PASS218_I43_SCOPE",
    "PASS218_I43_STATE_SCHEMA",
    "PASS218_I43_STATUS_SCHEMA",
    "PASS218_I43_VERSION",
    "Pass218I43AuthorizationError",
    "Pass218I43AuthorizationStore",
    "Pass218I43BindingError",
    "Pass218I43ManifestBoundI30PromotionRequestAuthorization",
    "Pass218I43StateError",
]