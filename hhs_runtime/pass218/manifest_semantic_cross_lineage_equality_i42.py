"""Pass 218 Iteration 42 manifest/semantic cross-lineage equality proof.

I42 begins only from the exact durable I41 learning-ingress receipt/candidate and
an independently supplied frozen-I29 validation request. The request is replayed
through frozen I29, then I42 proves equality only across the authoritative fields
that the two lineages genuinely share: curriculum identity and position plus the
nonverbatim source identity/checksum/authority/rights envelope.

I42 deliberately does not assert equality between unlike canonical and semantic
roots. It binds both roots, the exact I29 validation identity, the exact validated
Hash216, and a SHA-256 fingerprint of the transient typed I29 request into one
durable nonverbatim equality witness. The typed request itself is not persisted.

No I30 request, authority grant, semantic promotion, purge/closure, curriculum
advance, canonical learning, truth/action authority, model activation, source
retention, or authoritative floating-point state is created here.
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
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    PASS218_I29_VALIDATION_SCHEMA,
    Pass218I29ValidationRequest,
)
from hhs_runtime.pass218.manifest_bound_canonical_learning_ingress_i41 import (
    PASS218_I41_COMPLETE_STATUS,
    _verify_i41_candidate,
    _verify_i41_receipt,
)

PASS218_I42_VERSION = "HHS-P218-I42-MANIFEST-SEMANTIC-CROSS-LINEAGE-EQUALITY-V1"
PASS218_I42_SCOPE = "PASS218_MANIFEST_SEMANTIC_CROSS_LINEAGE_EQUALITY"
PASS218_I42_PROOF_SCHEMA = "HHS-P218-I42-MANIFEST-SEMANTIC-CROSS-LINEAGE-EQUALITY-PROOF-V1"
PASS218_I42_RECEIPT_SCHEMA = "HHS-P218-I42-MANIFEST-SEMANTIC-CROSS-LINEAGE-EQUALITY-RECEIPT-V1"
PASS218_I42_STATE_SCHEMA = "HHS-P218-I42-MANIFEST-SEMANTIC-CROSS-LINEAGE-EQUALITY-STATE-V1"
PASS218_I42_STATUS_SCHEMA = "HHS-P218-I42-MANIFEST-SEMANTIC-CROSS-LINEAGE-EQUALITY-STATUS-V1"
PASS218_I42_COMPLETE_STATUS = "MANIFEST_SEMANTIC_CROSS_LINEAGE_EQUALITY_PROVEN"
PASS218_I42_PENDING_STATUS = "MANIFEST_SEMANTIC_CROSS_LINEAGE_EQUALITY_PENDING"

_SHARED_IDENTITY_FIELDS = (
    "curriculum_identity_hash72",
    "curriculum_position",
    "source_id",
    "source_sha256",
    "source_authority",
    "rights_class",
)


class Pass218I42CrossLineageError(RuntimeError):
    pass


class Pass218I42BindingError(Pass218I42CrossLineageError):
    pass


class Pass218I42StateError(Pass218I42CrossLineageError):
    pass


class Pass218I42LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I42I41StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_candidate(self) -> dict[str, Any] | None: ...


class Pass218I42I29ValidatorProtocol(Protocol):
    def validate(self, request: Pass218I29ValidationRequest) -> dict[str, Any]: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I42BindingError("P218_I42_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        raise Pass218I42StateError("P218_I42_PATH_HASH72_INVALID")
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
        raise Pass218I42StateError("P218_I42_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I42StateError("P218_I42_STATE_OBJECT_REQUIRED")
    return value


def _request_record(request: Pass218I29ValidationRequest) -> dict[str, Any]:
    validated = request.validated()
    if not is_dataclass(validated):
        raise Pass218I42BindingError("P218_I42_I29_TYPED_REQUEST_REQUIRED")
    record = asdict(validated)
    if not isinstance(record, dict):
        raise Pass218I42BindingError("P218_I42_I29_REQUEST_RECORD_INVALID")
    return _copy(record)


def _request_identity(request: Pass218I29ValidationRequest) -> dict[str, Any]:
    validated = request.validated()
    beat = (
        validated.transition_request
        .differentiation_request
        .manifold_request
        .perspective_request
        .beat_request
    )
    identity = {
        "curriculum_identity_hash72": str(beat.curriculum_identity_hash72),
        "curriculum_position": int(beat.curriculum_position),
        "source_id": str(beat.source_id),
        "source_sha256": str(beat.source_checksum_sha256),
        "source_authority": str(beat.source_authority),
        "rights_class": str(beat.rights_class),
    }
    if not validate_hash72(identity["curriculum_identity_hash72"]):
        raise Pass218I42BindingError("P218_I42_REQUEST_CURRICULUM_HASH72_INVALID")
    if not _valid_sha256(identity["source_sha256"]):
        raise Pass218I42BindingError("P218_I42_REQUEST_SOURCE_SHA256_INVALID")
    if identity["curriculum_position"] < 0:
        raise Pass218I42BindingError("P218_I42_REQUEST_CURRICULUM_POSITION_INVALID")
    for field in ("source_id", "source_authority", "rights_class"):
        if not identity[field].strip():
            raise Pass218I42BindingError("P218_I42_REQUEST_IDENTITY_FIELD_EMPTY:" + field)
    return identity


def _verify_i29_result(result: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(result))
    if value.get("schema") != PASS218_I29_VALIDATION_SCHEMA:
        raise Pass218I42BindingError("P218_I42_I29_VALIDATION_SCHEMA_INVALID")
    if value.get("hash216_vm5184_validation_status") != (
        "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
    ):
        raise Pass218I42BindingError("P218_I42_I29_VALIDATION_STATUS_INVALID")
    if value.get("hash216_vm5184_validation_ready") is not True:
        raise Pass218I42BindingError("P218_I42_I29_VALIDATION_NOT_READY")
    for field in (
        "hash216_continuation_verified",
        "semantic_transition_validated",
        "vm5184_candidate_projection_verified",
        "candidate_semantic_binding_verified",
        "atomic_promotion_candidate_ready",
    ):
        if value.get(field) is not True:
            raise Pass218I42BindingError("P218_I42_I29_PROOF_INCOMPLETE:" + field)
    for field in (
        "atomic_promotion_authorized",
        "vm5184_authoritative_projection_invoked",
        "vm81_authorization_invoked",
        "atomic_promotion_invoked",
        "authoritative_semantic_compression_ready",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    ):
        if value.get(field) is not False:
            raise Pass218I42BindingError("P218_I42_I29_AUTHORITY_DRIFT:" + field)
    if not validate_hash72(str(value.get("hash216_vm5184_validation_hash72", ""))):
        raise Pass218I42BindingError("P218_I42_I29_VALIDATION_HASH72_INVALID")
    if not _valid_hash216(value.get("pass218_validated_hash216")):
        raise Pass218I42BindingError("P218_I42_I29_VALIDATED_HASH216_INVALID")
    segments = value.get("pass218_validated_hash216_segments")
    if not isinstance(segments, Mapping):
        raise Pass218I42BindingError("P218_I42_I29_HASH216_SEGMENTS_REQUIRED")
    for field in (
        "manifest_curriculum_hash72",
        "hydrated_transition_state_hash72",
        "validation_receipt_hash72",
    ):
        if not validate_hash72(str(segments.get(field, ""))):
            raise Pass218I42BindingError("P218_I42_I29_SEGMENT_INVALID:" + field)
    if value["pass218_validated_hash216"] != (
        str(segments["manifest_curriculum_hash72"])
        + str(segments["hydrated_transition_state_hash72"])
        + str(segments["validation_receipt_hash72"])
    ):
        raise Pass218I42BindingError("P218_I42_I29_HASH216_ORDER_INVALID")
    validation_receipt = value.get("validation_receipt")
    if not isinstance(validation_receipt, Mapping):
        raise Pass218I42BindingError("P218_I42_I29_VALIDATION_RECEIPT_REQUIRED")
    if validation_receipt.get("curriculum_hash72") != segments["manifest_curriculum_hash72"]:
        raise Pass218I42BindingError("P218_I42_I29_CURRICULUM_SEGMENT_RECEIPT_MISMATCH")
    witness = value.get("semantic_validation_witness")
    if not isinstance(witness, Mapping) or not validate_hash72(
        str(witness.get("semantic_witness_hash72", ""))
    ):
        raise Pass218I42BindingError("P218_I42_I29_SEMANTIC_WITNESS_INVALID")
    return value


def _verify_i42_proof(proof: Mapping[str, Any], receipt: Mapping[str, Any] | None = None) -> dict[str, Any]:
    value = _copy(dict(proof))
    if value.get("schema") != PASS218_I42_PROOF_SCHEMA:
        raise Pass218I42StateError("P218_I42_PROOF_SCHEMA_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I42StateError("P218_I42_TARGET_SCOPE_INVALID")
    for field in (
        "i41_receipt_hash72",
        "i41_learning_ingress_candidate_hash72",
        "i40_canonical_root_hash72",
        "i29_validation_hash72",
        "i29_curriculum_hash72",
        "i29_transition_state_hash72",
        "i29_validation_receipt_hash72",
        "i29_semantic_witness_hash72",
        "cross_lineage_equality_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I42StateError("P218_I42_PROOF_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i29_validated_hash216")):
        raise Pass218I42StateError("P218_I42_PROOF_HASH216_INVALID")
    if not _valid_sha256(value.get("i29_validation_request_sha256")):
        raise Pass218I42StateError("P218_I42_REQUEST_FINGERPRINT_INVALID")
    shared = value.get("shared_identity")
    if not isinstance(shared, Mapping) or any(field not in shared for field in _SHARED_IDENTITY_FIELDS):
        raise Pass218I42StateError("P218_I42_SHARED_IDENTITY_INCOMPLETE")
    required_true = (
        "i41_complete_receipt_bound",
        "i41_candidate_bound",
        "i29_independently_revalidated",
        "i29_validation_request_fingerprinted",
        "curriculum_identity_equal",
        "curriculum_position_equal",
        "source_id_equal",
        "source_sha256_equal",
        "source_authority_equal",
        "rights_class_equal",
        "i29_curriculum_segment_equal",
        "cross_lineage_shared_identity_equal",
        "canonical_and_semantic_roots_kept_distinct",
        "proof_non_authoritative",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I42StateError("P218_I42_PROOF_INCOMPLETE")
    required_false = (
        "i29_validation_request_persisted",
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "i30_request_synthesized",
        "i30_authority_grant_present",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I42StateError("P218_I42_PROOF_AUTHORITY_DRIFT")
    body = {key: item for key, item in value.items() if key != "cross_lineage_equality_hash72"}
    expected = hash72_digest({"domain": PASS218_I42_PROOF_SCHEMA}, body)
    if expected != value.get("cross_lineage_equality_hash72"):
        raise Pass218I42StateError("P218_I42_PROOF_HASH_MISMATCH")
    if receipt is not None and expected != receipt.get("cross_lineage_equality_hash72"):
        raise Pass218I42StateError("P218_I42_PROOF_RECEIPT_MISMATCH")
    return value


def _verify_i42_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I42_RECEIPT_SCHEMA:
        raise Pass218I42StateError("P218_I42_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I42_COMPLETE_STATUS:
        raise Pass218I42StateError("P218_I42_RECEIPT_STATUS_INVALID")
    if value.get("target_surface") != PASS218_I30_TARGET_SCOPE:
        raise Pass218I42StateError("P218_I42_RECEIPT_TARGET_INVALID")
    for field in (
        "i41_receipt_hash72",
        "cross_lineage_equality_hash72",
        "i29_validation_hash72",
        "i42_validation_hash72",
        "i42_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I42StateError("P218_I42_RECEIPT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i29_validated_hash216")) or not _valid_hash216(value.get("i42_hash216")):
        raise Pass218I42StateError("P218_I42_RECEIPT_HASH216_INVALID")
    if value["i42_hash216"] != (
        str(value["i41_receipt_hash72"])
        + str(value["i29_validation_hash72"])
        + str(value["i42_receipt_hash72"])
    ):
        raise Pass218I42StateError("P218_I42_HASH216_ORDER_INVALID")
    for field in (
        "cross_lineage_shared_identity_equal",
        "i29_independently_revalidated",
        "i30_exact_validation_identity_ready",
        "canonical_and_semantic_roots_kept_distinct",
    ):
        if value.get(field) is not True:
            raise Pass218I42StateError("P218_I42_RECEIPT_PROOF_INCOMPLETE:" + field)
    for field in (
        "i29_validation_request_persisted",
        "i30_request_synthesized",
        "i30_authority_grant_present",
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
    ):
        if value.get(field) is not False:
            raise Pass218I42StateError("P218_I42_RECEIPT_AUTHORITY_DRIFT:" + field)
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i42_receipt_hash72", "i42_hash216", "i42_hash216_semantics"}
    }
    expected = hash72_digest({"domain": PASS218_I42_RECEIPT_SCHEMA}, body)
    if expected != value.get("i42_receipt_hash72"):
        raise Pass218I42StateError("P218_I42_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I42CrossLineageEqualityStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.proof_root = self.root / "proofs"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I42_STATE_SCHEMA:
            raise Pass218I42StateError("P218_I42_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I42_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I42StateError("P218_I42_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        proof_path = self.root / str(state.get("active_proof_path", ""))
        if not receipt_path.is_file() or not proof_path.is_file():
            raise Pass218I42StateError("P218_I42_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i42_receipt(_load_json(receipt_path))
        proof = _verify_i42_proof(_load_json(proof_path), receipt)
        if receipt["i42_receipt_hash72"] != state.get("active_i42_receipt_hash72"):
            raise Pass218I42StateError("P218_I42_STATE_RECEIPT_MISMATCH")
        if proof["cross_lineage_equality_hash72"] != state.get("active_proof_hash72"):
            raise Pass218I42StateError("P218_I42_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i42_proof(_load_json(self.root / str(state["active_proof_path"])), receipt)

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i42_receipt(receipt)
        checked_proof = _verify_i42_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I42StateError("P218_I42_ACTIVE_BINDING_CONFLICT")
            return existing
        ordinal = int(checked_proof["shared_identity"]["curriculum_position"])
        receipt_name = _path_safe_hash72_name(str(checked["i42_receipt_hash72"]))
        proof_name = _path_safe_hash72_name(str(checked_proof["cross_lineage_equality_hash72"]))
        receipt_path = self.receipt_root / f"{ordinal:08d}-{receipt_name}.json"
        proof_path = self.proof_root / f"{proof_name}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(proof_path, checked_proof)
        state_body = {
            "schema": PASS218_I42_STATE_SCHEMA,
            "version": PASS218_I42_VERSION,
            "status": PASS218_I42_COMPLETE_STATUS,
            "i41_receipt_hash72": checked["i41_receipt_hash72"],
            "active_i42_receipt_hash72": checked["i42_receipt_hash72"],
            "active_proof_hash72": checked_proof["cross_lineage_equality_hash72"],
            "i29_validation_hash72": checked["i29_validation_hash72"],
            "i29_validation_request_sha256": checked["i29_validation_request_sha256"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_proof_path": proof_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest({"domain": PASS218_I42_STATE_SCHEMA}, state_body),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I42StateError("P218_I42_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I42ManifestSemanticCrossLineageEquality:
    def __init__(
        self,
        *,
        lifecycle: Pass218I42LifecycleProtocol,
        i41_store: Pass218I42I41StoreProtocol,
        i29_validator: Pass218I42I29ValidatorProtocol,
        state_root: str | os.PathLike[str],
        i41_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        i30_status_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i41_store = i41_store
        self.i29_validator = i29_validator
        self.store = Pass218I42CrossLineageEqualityStore(state_root)
        self.i41_status_provider = i41_status_provider
        self.i30_status_provider = i30_status_provider
        self.proof_count = 0
        self.i29_validation_count = 0
        self.i30_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_i41(self) -> tuple[dict[str, Any], dict[str, Any]]:
        receipt = self.i41_store.active_record()
        candidate = self.i41_store.active_candidate()
        if not isinstance(receipt, Mapping) or not isinstance(candidate, Mapping):
            raise Pass218I42BindingError("P218_I42_I41_COMPLETE_STATE_REQUIRED")
        checked = _verify_i41_receipt(receipt)
        checked_candidate = _verify_i41_candidate(candidate, checked)
        if checked.get("status") != PASS218_I41_COMPLETE_STATUS:
            raise Pass218I42BindingError("P218_I42_I41_COMPLETE_STATUS_REQUIRED")
        if checked_candidate.get("learning_ingress_candidate_hash72") != checked.get("learning_ingress_candidate_hash72"):
            raise Pass218I42BindingError("P218_I42_I41_CANDIDATE_MISMATCH")
        if self.i41_status_provider is not None:
            status = dict(self.i41_status_provider())
            if status.get("status") != PASS218_I41_COMPLETE_STATUS:
                raise Pass218I42BindingError("P218_I42_I41_STATUS_NOT_COMPLETE")
            if status.get("active_i41_receipt_hash72") != checked["i41_receipt_hash72"]:
                raise Pass218I42BindingError("P218_I42_I41_STATUS_RECEIPT_MISMATCH")
            if status.get("learning_ingress_candidate_hash72") != checked["learning_ingress_candidate_hash72"]:
                raise Pass218I42BindingError("P218_I42_I41_STATUS_CANDIDATE_MISMATCH")
        return checked, checked_candidate

    def _require_i30_preflight(self) -> None:
        if self.i30_status_provider is None:
            return
        status = dict(self.i30_status_provider())
        if status.get("target_scope") not in {None, PASS218_I30_TARGET_SCOPE}:
            raise Pass218I42BindingError("P218_I42_I30_TARGET_SCOPE_MISMATCH")
        if bool(status.get("promotion_present")) or bool(status.get("atomic_promotion_invoked")):
            raise Pass218I42BindingError("P218_I42_I30_PREVIOUS_PROMOTION_PENDING")

    @staticmethod
    def _prove_shared_identity(
        candidate: Mapping[str, Any],
        request_identity: Mapping[str, Any],
        i29: Mapping[str, Any],
    ) -> dict[str, bool]:
        binding = candidate.get("manifest_binding")
        if not isinstance(binding, Mapping):
            raise Pass218I42BindingError("P218_I42_I41_MANIFEST_BINDING_REQUIRED")
        comparisons = {
            "curriculum_identity_equal": binding.get("curriculum_identity_hash72") == request_identity["curriculum_identity_hash72"],
            "curriculum_position_equal": binding.get("curriculum_position") == request_identity["curriculum_position"],
            "source_id_equal": binding.get("source_id") == request_identity["source_id"],
            "source_sha256_equal": binding.get("source_sha256") == request_identity["source_sha256"],
            "source_authority_equal": binding.get("source_authority") == request_identity["source_authority"],
            "rights_class_equal": binding.get("rights_class") == request_identity["rights_class"],
        }
        for field, equal in comparisons.items():
            if not equal:
                raise Pass218I42BindingError("P218_I42_CROSS_LINEAGE_MISMATCH:" + field)
        segments = i29["pass218_validated_hash216_segments"]
        segment_equal = (
            segments["manifest_curriculum_hash72"]
            == request_identity["curriculum_identity_hash72"]
            == binding["curriculum_identity_hash72"]
        )
        if not segment_equal:
            raise Pass218I42BindingError("P218_I42_CROSS_LINEAGE_MISMATCH:i29_curriculum_segment_equal")
        return {**comparisons, "i29_curriculum_segment_equal": True}

    def _build(
        self,
        *,
        i41: Mapping[str, Any],
        candidate: Mapping[str, Any],
        request_identity: Mapping[str, Any],
        request_sha256: str,
        i29: Mapping[str, Any],
        comparisons: Mapping[str, bool],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        segments = i29["pass218_validated_hash216_segments"]
        witness = i29["semantic_validation_witness"]
        shared_identity = {field: _copy(request_identity[field]) for field in _SHARED_IDENTITY_FIELDS}
        proof_body = {
            "schema": PASS218_I42_PROOF_SCHEMA,
            "version": PASS218_I42_VERSION,
            "scope": PASS218_I42_SCOPE,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i41_receipt_hash72": i41["i41_receipt_hash72"],
            "i41_learning_ingress_candidate_hash72": candidate["learning_ingress_candidate_hash72"],
            "i40_receipt_hash72": i41["i40_receipt_hash72"],
            "i40_canonical_root_hash72": i41["i40_canonical_root_hash72"],
            "manifest_bound_commit_persistence_hash72": i41["manifest_bound_commit_persistence_hash72"],
            "shared_identity": shared_identity,
            "i29_validation_request_sha256": request_sha256,
            "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
            "i29_validated_hash216": i29["pass218_validated_hash216"],
            "i29_curriculum_hash72": segments["manifest_curriculum_hash72"],
            "i29_transition_state_hash72": segments["hydrated_transition_state_hash72"],
            "i29_validation_receipt_hash72": segments["validation_receipt_hash72"],
            "i29_semantic_witness_hash72": witness["semantic_witness_hash72"],
            "i41_complete_receipt_bound": True,
            "i41_candidate_bound": True,
            "i29_independently_revalidated": True,
            "i29_validation_request_fingerprinted": True,
            **dict(comparisons),
            "cross_lineage_shared_identity_equal": True,
            "canonical_and_semantic_roots_kept_distinct": True,
            "proof_non_authoritative": True,
            "i29_validation_request_persisted": False,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "i30_request_synthesized": False,
            "i30_authority_grant_present": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "curriculum_cursor_advanced": False,
            "stage_advance_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
        }
        proof_hash72 = hash72_digest({"domain": PASS218_I42_PROOF_SCHEMA}, proof_body)
        proof = {**proof_body, "cross_lineage_equality_hash72": proof_hash72}
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I42-CROSS-LINEAGE-VALIDATION-V1"},
            {
                "i41_receipt_hash72": i41["i41_receipt_hash72"],
                "i41_candidate_hash72": candidate["learning_ingress_candidate_hash72"],
                "i29_validation_request_sha256": request_sha256,
                "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
                "i29_validated_hash216": i29["pass218_validated_hash216"],
                "cross_lineage_equality_hash72": proof_hash72,
                "shared_identity_equal": True,
                "i30_invoked": False,
            },
        )
        body = {
            "schema": PASS218_I42_RECEIPT_SCHEMA,
            "version": PASS218_I42_VERSION,
            "scope": PASS218_I42_SCOPE,
            "status": PASS218_I42_COMPLETE_STATUS,
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "i41_receipt_hash72": i41["i41_receipt_hash72"],
            "cross_lineage_equality_hash72": proof_hash72,
            "i29_validation_request_sha256": request_sha256,
            "i29_validation_hash72": i29["hash216_vm5184_validation_hash72"],
            "i29_validated_hash216": i29["pass218_validated_hash216"],
            "i42_validation_hash72": validation_hash72,
            "cross_lineage_shared_identity_equal": True,
            "i29_independently_revalidated": True,
            "i30_exact_validation_identity_ready": True,
            "canonical_and_semantic_roots_kept_distinct": True,
            "i29_validation_request_persisted": False,
            "i30_request_synthesized": False,
            "i30_authority_grant_present": False,
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
        receipt_hash72 = hash72_digest({"domain": PASS218_I42_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i42_receipt_hash72": receipt_hash72,
            "i42_hash216": i41["i41_receipt_hash72"] + i29["hash216_vm5184_validation_hash72"] + receipt_hash72,
            "i42_hash216_semantics": [
                "I41_MANIFEST_BOUND_CANONICAL_LEARNING_INGRESS_RECEIPT",
                "I29_INDEPENDENT_HASH216_VM5184_VALIDATION_RESULT",
                "I42_CROSS_LINEAGE_EQUALITY_RECEIPT",
            ],
        }
        return _verify_i42_proof(proof), _verify_i42_receipt(receipt)

    def prove(self, validation_request: Pass218I29ValidationRequest) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i41, candidate = self._active_i41()
            self._require_i30_preflight()
            validated_request = validation_request.validated()
            request_record = _request_record(validated_request)
            request_sha256 = sha256(_canonical_bytes(request_record)).hexdigest()
            request_identity = _request_identity(validated_request)
            existing = self.store.active_record()
            if existing is not None:
                if existing["i41_receipt_hash72"] != i41["i41_receipt_hash72"]:
                    raise Pass218I42StateError("P218_I42_ACTIVE_I41_CONFLICT")
                if existing["i29_validation_request_sha256"] != request_sha256:
                    raise Pass218I42StateError("P218_I42_ACTIVE_REQUEST_CONFLICT")
                self.last_error_code = None
                return existing
            i29 = _verify_i29_result(self.i29_validator.validate(validated_request))
            self.i29_validation_count += 1
            comparisons = self._prove_shared_identity(candidate, request_identity, i29)
            proof, receipt = self._build(
                i41=i41,
                candidate=candidate,
                request_identity=request_identity,
                request_sha256=request_sha256,
                i29=i29,
                comparisons=comparisons,
            )
            persisted = self.store.commit(receipt, proof)
            self.proof_count += 1
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        predecessor_ready = False
        active_i41_receipt_hash72: str | None = None
        try:
            i41, _ = self._active_i41()
            predecessor_ready = True
            active_i41_receipt_hash72 = str(i41["i41_receipt_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I42_STATUS_SCHEMA,
            "version": PASS218_I42_VERSION,
            "status": PASS218_I42_COMPLETE_STATUS if active is not None else PASS218_I42_PENDING_STATUS,
            "predecessor_state_ready": predecessor_ready,
            "active_i41_receipt_hash72": active_i41_receipt_hash72,
            "active_i42_receipt_hash72": None if active is None else active["i42_receipt_hash72"],
            "i29_validation_hash72": None if active is None else active["i29_validation_hash72"],
            "i29_validated_hash216": None if active is None else active["i29_validated_hash216"],
            "i29_validation_request_sha256": None if active is None else active["i29_validation_request_sha256"],
            "target_surface": PASS218_I30_TARGET_SCOPE,
            "proof_count_current_process": self.proof_count,
            "i29_validation_count_current_process": self.i29_validation_count,
            "i30_invocation_count_current_process": self.i30_invocation_count,
            "cross_lineage_shared_identity_equal": active is not None,
            "i30_exact_validation_identity_ready": active is not None,
            "i30_request_synthesized": False,
            "i30_authority_grant_present": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I42_COMPLETE_STATUS",
    "PASS218_I42_PENDING_STATUS",
    "PASS218_I42_PROOF_SCHEMA",
    "PASS218_I42_RECEIPT_SCHEMA",
    "PASS218_I42_SCOPE",
    "PASS218_I42_STATE_SCHEMA",
    "PASS218_I42_STATUS_SCHEMA",
    "PASS218_I42_VERSION",
    "Pass218I42BindingError",
    "Pass218I42CrossLineageEqualityStore",
    "Pass218I42CrossLineageError",
    "Pass218I42ManifestSemanticCrossLineageEquality",
    "Pass218I42StateError",
]
