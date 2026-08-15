"""Pass 218 Iteration 37 manifest-bound frozen-I5 promotability-proof ingress.

I37 begins only from the exact durable I36 receipt, its exact manifest-bound
I4 CANDIDATE, and the exact CLOSED I3 transaction snapshot already bound by
I35/I36. It invokes only frozen I5 ``PromotionProofMembrane.prove`` and binds
the resulting non-authoritative promotability proof to the unchanged
manifest/curriculum/source lineage.

I37 does not create an I5 authority grant or promotion authorization, invoke
I6/canonical commit, I30 canonical semantic promotion, I31 purge, I32 source
closure, curriculum/stage advance, VM81 authority, truth/action authority,
canonical learning, model activation, verbatim retention, or authoritative
floating-point state.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    PASS218_I36_COMPLETE_STATUS,
    PASS218_I36_RECEIPT_SCHEMA,
    PASS218_I36_STAGE_SCHEMA,
)
from hhs_runtime.pass218.promotion import (
    PASS218_PROMOTION_MEMBRANE_VERSION,
    Pass218PromotionError,
    PromotionProof,
    PromotionProofMembrane,
)
from hhs_runtime.pass218.transaction import SourceTransaction, TransactionPhase

PASS218_I37_VERSION = "HHS-P218-I37-MANIFEST-BOUND-PROMOTION-ADMISSION-PROOF-V1"
PASS218_I37_SCOPE = "PASS218_MANIFEST_BOUND_PROMOTION_ADMISSION_PROOF_INGRESS"
PASS218_I37_RECEIPT_SCHEMA = (
    "HHS-P218-I37-MANIFEST-BOUND-PROMOTION-ADMISSION-PROOF-RECEIPT-V1"
)
PASS218_I37_PROOF_SCHEMA = (
    "HHS-P218-I37-MANIFEST-BOUND-PROMOTION-ADMISSION-PROOF-V1"
)
PASS218_I37_STATE_SCHEMA = (
    "HHS-P218-I37-MANIFEST-BOUND-PROMOTION-ADMISSION-PROOF-STATE-V1"
)
PASS218_I37_STATUS_SCHEMA = (
    "HHS-P218-I37-MANIFEST-BOUND-PROMOTION-ADMISSION-PROOF-STATUS-V1"
)
PASS218_I37_COMPLETE_STATUS = "MANIFEST_BOUND_PROMOTION_ADMISSION_PROOF_INGRESS_COMPLETE"
PASS218_I37_PENDING_STATUS = "MANIFEST_BOUND_PROMOTION_ADMISSION_PROOF_PENDING"


class Pass218I37ProofIngressError(RuntimeError):
    pass


class Pass218I37BindingError(Pass218I37ProofIngressError):
    pass


class Pass218I37StateError(Pass218I37ProofIngressError):
    pass


class Pass218I37I5Error(Pass218I37ProofIngressError):
    pass


class Pass218I37LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I37I36StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_stage(self) -> dict[str, Any] | None: ...


class Pass218I37I35StoreProtocol(Protocol):
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
        raise Pass218I37StateError("P218_I37_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I37StateError("P218_I37_STATE_OBJECT_REQUIRED")
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


def _verify_i36_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I36_RECEIPT_SCHEMA:
        raise Pass218I37BindingError("P218_I37_I36_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I36_COMPLETE_STATUS:
        raise Pass218I37BindingError("P218_I37_I36_NOT_COMPLETE")
    required_true = (
        "i35_receipt_bound",
        "manifest_binding_propagated",
        "closed_i3_snapshot_bound",
        "pass218_i4_staging_required",
        "pass218_i4_staging_invoked",
        "i4_stage_candidate_non_authoritative",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I37BindingError("P218_I37_I36_PROOF_INCOMPLETE")
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
        raise Pass218I37BindingError("P218_I37_I36_AUTHORITY_DRIFT")
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
        "i36_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I37BindingError("P218_I37_I36_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("i36_hash216")):
        raise Pass218I37BindingError("P218_I37_I36_HASH216_INVALID")
    if not _valid_hash216(value.get("i4_staging_hash216")):
        raise Pass218I37BindingError("P218_I37_I4_HASH216_INVALID")
    if not _valid_sha256(value.get("i4_entry_id_sha256")):
        raise Pass218I37BindingError("P218_I37_I4_ENTRY_ID_INVALID")
    if not _valid_sha256(value.get("i4_projection_sha256")):
        raise Pass218I37BindingError("P218_I37_I4_PROJECTION_SHA256_INVALID")
    if value.get("i4_vector_admission_status") != "CANDIDATE":
        raise Pass218I37BindingError("P218_I37_I4_NOT_CANDIDATE")
    if not isinstance(value.get("manifest_binding"), Mapping):
        raise Pass218I37BindingError("P218_I37_MANIFEST_BINDING_REQUIRED")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i36_receipt_hash72", "i36_hash216", "i36_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I36_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("i36_receipt_hash72"):
        raise Pass218I37BindingError("P218_I37_I36_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i35_receipt_hash72"])
        + str(value["i4_staging_hash72"])
        + str(value["i36_receipt_hash72"])
    )
    if expected_hash216 != value.get("i36_hash216"):
        raise Pass218I37BindingError("P218_I37_I36_HASH216_ORDER_INVALID")
    return value


def _verify_i36_stage(
    stage: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(stage))
    if value.get("schema") != PASS218_I36_STAGE_SCHEMA:
        raise Pass218I37BindingError("P218_I37_I36_STAGE_SCHEMA_INVALID")
    body = {
        key: item
        for key, item in value.items()
        if key != "manifest_bound_i4_stage_hash72"
    }
    expected = hash72_digest({"domain": PASS218_I36_STAGE_SCHEMA}, body)
    if expected != value.get("manifest_bound_i4_stage_hash72"):
        raise Pass218I37BindingError("P218_I37_I36_STAGE_HASH_MISMATCH")
    if expected != receipt.get("manifest_bound_i4_stage_hash72"):
        raise Pass218I37BindingError("P218_I37_I36_STAGE_RECEIPT_MISMATCH")
    for key in (
        "i35_receipt_hash72",
        "i34_ingress_receipt_hash72",
        "manifest_bound_semantic_hash72",
        "i3_transaction_id_hash72",
        "i3_transaction_snapshot_hash72",
    ):
        if value.get(key) != receipt.get(key):
            raise Pass218I37BindingError("P218_I37_I36_STAGE_LINEAGE_MISMATCH:" + key)
    if value.get("manifest_binding") != receipt.get("manifest_binding"):
        raise Pass218I37BindingError("P218_I37_I36_MANIFEST_BINDING_MISMATCH")
    i4 = value.get("i4_stage_candidate")
    if not isinstance(i4, Mapping):
        raise Pass218I37BindingError("P218_I37_I4_STAGE_REQUIRED")
    entry = i4.get("vector_entry")
    if not isinstance(entry, Mapping):
        raise Pass218I37BindingError("P218_I37_I4_VECTOR_ENTRY_REQUIRED")
    for stage_field, receipt_field in (
        ("transaction_id_hash72", "i3_transaction_id_hash72"),
        ("staging_hash72", "i4_staging_hash72"),
        ("validation_hash72", "i4_validation_hash72"),
        ("staging_hash216", "i4_staging_hash216"),
        ("vm5184_projection_hash72", "i4_projection_hash72"),
        ("vm5184_projection_sha256", "i4_projection_sha256"),
    ):
        if i4.get(stage_field) != receipt.get(receipt_field):
            raise Pass218I37BindingError("P218_I37_I4_RECEIPT_MISMATCH:" + stage_field)
    if entry.get("entry_id_sha256") != receipt.get("i4_entry_id_sha256"):
        raise Pass218I37BindingError("P218_I37_I4_ENTRY_ID_MISMATCH")
    if entry.get("admission_status") != "CANDIDATE":
        raise Pass218I37BindingError("P218_I37_I4_STAGE_NOT_CANDIDATE")
    return value


def _verify_snapshot(
    snapshot: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    copied = _copy(dict(snapshot))
    try:
        restored = SourceTransaction.restore(copied)
    except Exception as exc:
        raise Pass218I37BindingError("P218_I37_I3_SNAPSHOT_INVALID") from exc
    if restored.phase != TransactionPhase.CLOSED:
        raise Pass218I37BindingError("P218_I37_I3_SNAPSHOT_NOT_CLOSED")
    if copied.get("snapshot_hash72") != receipt.get("i3_transaction_snapshot_hash72"):
        raise Pass218I37BindingError("P218_I37_I3_SNAPSHOT_HASH_MISMATCH")
    if restored.transaction_id_hash72 != receipt.get("i3_transaction_id_hash72"):
        raise Pass218I37BindingError("P218_I37_I3_TRANSACTION_ID_MISMATCH")
    return copied


def _verify_i5_proof(
    proof: Mapping[str, Any],
    *,
    receipt: Mapping[str, Any],
    i4_stage: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(proof))
    try:
        PromotionProofMembrane.validate_proof_record(value)
    except Pass218PromotionError as exc:
        raise Pass218I37I5Error("P218_I37_I5_PROOF_INVALID:" + str(exc)) from exc
    entry = i4_stage["vector_entry"]
    for proof_field, expected in (
        ("transaction_id_hash72", receipt["i3_transaction_id_hash72"]),
        ("entry_id_sha256", receipt["i4_entry_id_sha256"]),
        ("staging_hash72", receipt["i4_staging_hash72"]),
        ("staging_validation_hash72", receipt["i4_validation_hash72"]),
        ("staging_hash216", receipt["i4_staging_hash216"]),
        ("projection_hash72", receipt["i4_projection_hash72"]),
        ("projection_sha256", receipt["i4_projection_sha256"]),
    ):
        if value.get(proof_field) != expected:
            raise Pass218I37I5Error("P218_I37_I5_PROOF_BINDING_MISMATCH:" + proof_field)
    expected_entry_sha = sha256(_canonical_bytes(entry)).hexdigest()
    if value.get("vector_entry_sha256") != expected_entry_sha:
        raise Pass218I37I5Error("P218_I37_I5_VECTOR_ENTRY_SHA256_MISMATCH")
    if value.get("promotable") is not True:
        raise Pass218I37I5Error("P218_I37_I5_NOT_PROMOTABLE")
    if value.get("explicit_authority_grant_present") is not False:
        raise Pass218I37I5Error("P218_I37_I5_GRANT_MUST_BE_ABSENT")
    if value.get("canonical_mutation_permitted") is not False:
        raise Pass218I37I5Error("P218_I37_I5_CANONICAL_MUTATION_MUST_BE_CLOSED")
    return value


def _build_manifest_bound_proof(
    i36_receipt: Mapping[str, Any],
    i5_proof: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        "schema": PASS218_I37_PROOF_SCHEMA,
        "version": PASS218_I37_VERSION,
        "i36_receipt_hash72": i36_receipt["i36_receipt_hash72"],
        "i36_hash216": i36_receipt["i36_hash216"],
        "manifest_bound_i4_stage_hash72": i36_receipt["manifest_bound_i4_stage_hash72"],
        "i35_receipt_hash72": i36_receipt["i35_receipt_hash72"],
        "i34_ingress_receipt_hash72": i36_receipt["i34_ingress_receipt_hash72"],
        "manifest_bound_semantic_hash72": i36_receipt["manifest_bound_semantic_hash72"],
        "manifest_binding": _copy(i36_receipt["manifest_binding"]),
        "i3_transaction_id_hash72": i36_receipt["i3_transaction_id_hash72"],
        "i3_transaction_snapshot_hash72": i36_receipt["i3_transaction_snapshot_hash72"],
        "i5_promotion_membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
        "i5_promotability_proof": _copy(dict(i5_proof)),
        "manifest_binding_propagated": True,
        "promotability_proof_non_authoritative": True,
        "explicit_authority_grant_present": False,
        "promotion_authorization_invoked": False,
        "canonical_mutation_permitted": False,
        "verbatim_source_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "canonical_vm81_commit_invoked": False,
        "canonical_learning_commit_invoked": False,
    }
    return {
        **body,
        "manifest_bound_i5_proof_hash72": hash72_digest(
            {"domain": PASS218_I37_PROOF_SCHEMA}, body
        ),
    }


def _verify_manifest_bound_proof(
    envelope: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(envelope))
    if value.get("schema") != PASS218_I37_PROOF_SCHEMA:
        raise Pass218I37StateError("P218_I37_PROOF_ENVELOPE_SCHEMA_INVALID")
    body = {key: item for key, item in value.items() if key != "manifest_bound_i5_proof_hash72"}
    expected = hash72_digest({"domain": PASS218_I37_PROOF_SCHEMA}, body)
    if expected != value.get("manifest_bound_i5_proof_hash72"):
        raise Pass218I37StateError("P218_I37_PROOF_ENVELOPE_HASH_MISMATCH")
    if expected != receipt.get("manifest_bound_i5_proof_hash72"):
        raise Pass218I37StateError("P218_I37_PROOF_RECEIPT_BINDING_MISMATCH")
    if value.get("i36_receipt_hash72") != receipt.get("i36_receipt_hash72"):
        raise Pass218I37StateError("P218_I37_PROOF_I36_RECEIPT_MISMATCH")
    if value.get("manifest_binding") != receipt.get("manifest_binding"):
        raise Pass218I37StateError("P218_I37_PROOF_MANIFEST_BINDING_MISMATCH")
    proof = value.get("i5_promotability_proof")
    if not isinstance(proof, Mapping) or proof.get("proof_hash72") != receipt.get("i5_proof_hash72"):
        raise Pass218I37StateError("P218_I37_PROOF_I5_HASH_MISMATCH")
    return value


def _verify_i37_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I37_RECEIPT_SCHEMA:
        raise Pass218I37StateError("P218_I37_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I37_COMPLETE_STATUS:
        raise Pass218I37StateError("P218_I37_RECEIPT_STATUS_INVALID")
    required_true = (
        "i36_receipt_bound",
        "manifest_binding_propagated",
        "closed_i3_snapshot_bound",
        "i4_candidate_bound",
        "pass218_i5_promotability_proof_required",
        "pass218_i5_promotability_proof_invoked",
        "i5_promotable",
        "promotability_proof_non_authoritative",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I37StateError("P218_I37_RECEIPT_PROOF_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "pass218_i5_promotion_invoked",
        "i5_explicit_authority_grant_present",
        "i5_promotion_authorization_invoked",
        "canonical_mutation_permitted",
        "pass218_i6_canonical_commit_invoked",
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
        raise Pass218I37StateError("P218_I37_RECEIPT_AUTHORITY_DRIFT")
    for field in (
        "i36_receipt_hash72",
        "manifest_bound_i4_stage_hash72",
        "i35_receipt_hash72",
        "i34_ingress_receipt_hash72",
        "manifest_bound_semantic_hash72",
        "i3_transaction_id_hash72",
        "i3_transaction_snapshot_hash72",
        "i4_staging_hash72",
        "i5_dependency_scope_hash72",
        "i5_proof_hash72",
        "i5_validation_hash72",
        "manifest_bound_i5_proof_hash72",
        "i37_validation_hash72",
        "i37_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I37StateError("P218_I37_RECEIPT_HASH72_INVALID:" + field)
    for field in ("i36_hash216", "i5_proof_hash216", "i37_hash216"):
        if not _valid_hash216(value.get(field)):
            raise Pass218I37StateError("P218_I37_RECEIPT_HASH216_INVALID:" + field)
    for field in (
        "i4_entry_id_sha256",
        "i4_projection_sha256",
        "i5_vector_entry_sha256",
    ):
        if not _valid_sha256(value.get(field)):
            raise Pass218I37StateError("P218_I37_RECEIPT_SHA256_INVALID:" + field)
    if not isinstance(value.get("manifest_binding"), Mapping):
        raise Pass218I37StateError("P218_I37_RECEIPT_MANIFEST_BINDING_REQUIRED")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i37_receipt_hash72", "i37_hash216", "i37_hash216_semantics"}
    }
    expected_receipt = hash72_digest({"domain": PASS218_I37_RECEIPT_SCHEMA}, body)
    if expected_receipt != value.get("i37_receipt_hash72"):
        raise Pass218I37StateError("P218_I37_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i36_receipt_hash72"])
        + str(value["i5_proof_hash72"])
        + str(value["i37_receipt_hash72"])
    )
    if expected_hash216 != value.get("i37_hash216"):
        raise Pass218I37StateError("P218_I37_HASH216_ORDER_INVALID")
    return value


class Pass218I37ManifestBoundPromotionProofStore:
    """Durable nonverbatim I37 proof envelope and binding receipt."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.proof_root = self.root / "proofs"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I37_STATE_SCHEMA:
            raise Pass218I37StateError("P218_I37_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I37_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I37StateError("P218_I37_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        proof_path = self.root / str(state.get("active_proof_path", ""))
        if not receipt_path.is_file() or not proof_path.is_file():
            raise Pass218I37StateError("P218_I37_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i37_receipt(_load_json(receipt_path))
        if receipt["i37_receipt_hash72"] != state.get("active_i37_receipt_hash72"):
            raise Pass218I37StateError("P218_I37_STATE_RECEIPT_MISMATCH")
        proof = _verify_manifest_bound_proof(_load_json(proof_path), receipt)
        if proof["manifest_bound_i5_proof_hash72"] != state.get("active_proof_hash72"):
            raise Pass218I37StateError("P218_I37_STATE_PROOF_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_manifest_bound_proof(
            _load_json(self.root / str(state["active_proof_path"])),
            receipt,
        )

    def commit(
        self,
        receipt: Mapping[str, Any],
        proof_envelope: Mapping[str, Any],
    ) -> dict[str, Any]:
        checked = _verify_i37_receipt(receipt)
        proof = _verify_manifest_bound_proof(proof_envelope, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked:
                raise Pass218I37StateError("P218_I37_ACTIVE_BINDING_CONFLICT")
            if self.active_proof() != proof:
                raise Pass218I37StateError("P218_I37_ACTIVE_PROOF_CONFLICT")
            return existing
        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_path = self.receipt_root / f"{ordinal:08d}-{checked['i37_receipt_hash72']}.json"
        proof_path = self.proof_root / f"{checked['manifest_bound_i5_proof_hash72']}.json"
        if receipt_path.exists():
            if _load_json(receipt_path) != checked:
                raise Pass218I37StateError("P218_I37_RECEIPT_CONFLICT")
        else:
            _atomic_write_json(receipt_path, checked)
        if proof_path.exists():
            if _load_json(proof_path) != proof:
                raise Pass218I37StateError("P218_I37_PROOF_CONFLICT")
        else:
            _atomic_write_json(proof_path, proof)
        state_body = {
            "schema": PASS218_I37_STATE_SCHEMA,
            "version": PASS218_I37_VERSION,
            "status": PASS218_I37_COMPLETE_STATUS,
            "i36_receipt_hash72": checked["i36_receipt_hash72"],
            "active_i37_receipt_hash72": checked["i37_receipt_hash72"],
            "active_proof_hash72": proof["manifest_bound_i5_proof_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_proof_path": proof_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest(
                {"domain": PASS218_I37_STATE_SCHEMA}, state_body
            ),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I37StateError("P218_I37_STATE_PERSIST_MISMATCH")
        return checked


class Pass218I37ManifestBoundPromotionAdmissionProof:
    """Bind exact frozen I36 state to frozen I5 promotability proof only."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I37LifecycleProtocol,
        i36_store: Pass218I37I36StoreProtocol,
        i35_store: Pass218I37I35StoreProtocol,
        state_root: str | os.PathLike[str],
        i36_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        proof_membrane: PromotionProofMembrane | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i36_store = i36_store
        self.i35_store = i35_store
        self.i36_status_provider = i36_status_provider
        self.membrane = proof_membrane or PromotionProofMembrane()
        self.store = Pass218I37ManifestBoundPromotionProofStore(state_root)
        self.i5_prove_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _active_i36(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        receipt = self.i36_store.active_record()
        stage = self.i36_store.active_stage()
        snapshot = self.i35_store.active_transaction_snapshot()
        if receipt is None or stage is None or snapshot is None:
            raise Pass218I37BindingError("P218_I37_I36_COMPLETE_STATE_REQUIRED")
        checked = _verify_i36_receipt(receipt)
        checked_stage = _verify_i36_stage(stage, checked)
        checked_snapshot = _verify_snapshot(snapshot, checked)
        if self.i36_status_provider is not None:
            status = dict(self.i36_status_provider())
            if status.get("status") != PASS218_I36_COMPLETE_STATUS:
                raise Pass218I37BindingError("P218_I37_I36_STATUS_NOT_COMPLETE")
            if status.get("active_i36_receipt_hash72") != checked["i36_receipt_hash72"]:
                raise Pass218I37BindingError("P218_I37_I36_STATUS_RECEIPT_MISMATCH")
            if status.get("manifest_bound_i4_stage_hash72") != checked["manifest_bound_i4_stage_hash72"]:
                raise Pass218I37BindingError("P218_I37_I36_STATUS_STAGE_MISMATCH")
        return checked, checked_stage, checked_snapshot

    def prove(self) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            i36, stage, snapshot = self._active_i36()
            existing = self.store.active_record()
            if existing is not None:
                if (
                    existing["i36_receipt_hash72"] != i36["i36_receipt_hash72"]
                    or existing["manifest_bound_i4_stage_hash72"] != i36["manifest_bound_i4_stage_hash72"]
                    or existing["i3_transaction_snapshot_hash72"] != i36["i3_transaction_snapshot_hash72"]
                    or existing["manifest_binding"] != i36["manifest_binding"]
                ):
                    raise Pass218I37StateError("P218_I37_ACTIVE_BINDING_CONFLICT")
                self.last_error_code = None
                return existing
            i4_stage = stage["i4_stage_candidate"]
            try:
                proof_obj = self.membrane.prove(
                    closed_transaction_snapshot=snapshot,
                    staged_candidate=i4_stage,
                )
                self.i5_prove_invocation_count += 1
            except Pass218PromotionError as exc:
                raise Pass218I37I5Error("P218_I37_I5_PROVE_FAILED:" + str(exc)) from exc
            if isinstance(proof_obj, PromotionProof):
                proof_record = proof_obj.to_record()
            elif isinstance(proof_obj, Mapping):
                proof_record = _copy(dict(proof_obj))
            else:
                raise Pass218I37I5Error("P218_I37_I5_PROOF_RECORD_REQUIRED")
            checked_proof = _verify_i5_proof(
                proof_record,
                receipt=i36,
                i4_stage=i4_stage,
            )
            envelope = _build_manifest_bound_proof(i36, checked_proof)
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I37-MANIFEST-BOUND-PROOF-VALIDATION-V1"},
                {
                    "i36_receipt_hash72": i36["i36_receipt_hash72"],
                    "manifest_bound_i4_stage_hash72": i36["manifest_bound_i4_stage_hash72"],
                    "i3_transaction_snapshot_hash72": i36["i3_transaction_snapshot_hash72"],
                    "i5_proof_hash72": checked_proof["proof_hash72"],
                    "manifest_bound_i5_proof_hash72": envelope["manifest_bound_i5_proof_hash72"],
                    "exact_i4_replay_proven": True,
                    "manifest_binding_propagated": True,
                    "explicit_authority_grant_present": False,
                    "promotion_authorization_invoked": False,
                    "canonical_mutation_permitted": False,
                },
            )
            body = {
                "schema": PASS218_I37_RECEIPT_SCHEMA,
                "version": PASS218_I37_VERSION,
                "scope": PASS218_I37_SCOPE,
                "status": PASS218_I37_COMPLETE_STATUS,
                "i36_receipt_hash72": i36["i36_receipt_hash72"],
                "i36_hash216": i36["i36_hash216"],
                "manifest_bound_i4_stage_hash72": i36["manifest_bound_i4_stage_hash72"],
                "i35_receipt_hash72": i36["i35_receipt_hash72"],
                "i34_ingress_receipt_hash72": i36["i34_ingress_receipt_hash72"],
                "manifest_bound_semantic_hash72": i36["manifest_bound_semantic_hash72"],
                "manifest_binding": _copy(i36["manifest_binding"]),
                "i3_transaction_id_hash72": i36["i3_transaction_id_hash72"],
                "i3_transaction_snapshot_hash72": i36["i3_transaction_snapshot_hash72"],
                "i4_entry_id_sha256": i36["i4_entry_id_sha256"],
                "i4_staging_hash72": i36["i4_staging_hash72"],
                "i4_projection_sha256": i36["i4_projection_sha256"],
                "i5_promotion_membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
                "i5_dependency_scope_hash72": checked_proof["dependency_scope_hash72"],
                "i5_vector_entry_sha256": checked_proof["vector_entry_sha256"],
                "i5_proof_hash72": checked_proof["proof_hash72"],
                "i5_validation_hash72": checked_proof["validation_hash72"],
                "i5_proof_hash216": checked_proof["proof_hash216"],
                "manifest_bound_i5_proof_hash72": envelope["manifest_bound_i5_proof_hash72"],
                "i37_validation_hash72": validation_hash72,
                "i36_receipt_bound": True,
                "manifest_binding_propagated": True,
                "closed_i3_snapshot_bound": True,
                "i4_candidate_bound": True,
                "pass218_i5_promotability_proof_required": True,
                "pass218_i5_promotability_proof_invoked": True,
                "i5_promotable": True,
                "promotability_proof_non_authoritative": True,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
                "pass218_i5_promotion_invoked": False,
                "i5_explicit_authority_grant_present": False,
                "i5_promotion_authorization_invoked": False,
                "canonical_mutation_permitted": False,
                "pass218_i6_canonical_commit_invoked": False,
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
            receipt_hash72 = hash72_digest({"domain": PASS218_I37_RECEIPT_SCHEMA}, body)
            receipt = {
                **body,
                "i37_receipt_hash72": receipt_hash72,
                "i37_hash216": i36["i36_receipt_hash72"] + checked_proof["proof_hash72"] + receipt_hash72,
                "i37_hash216_semantics": [
                    "I36_MANIFEST_BOUND_VECTOR_VM5184_STAGING_RECEIPT",
                    "I5_PROMOTABILITY_PROOF",
                    "I37_MANIFEST_BOUND_PROOF_BINDING_RECEIPT",
                ],
            }
            persisted = self.store.commit(receipt, envelope)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def active_proof(self) -> dict[str, Any] | None:
        return self.store.active_proof()

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i36_ready = False
        active_i36_receipt_hash72: str | None = None
        active_i36_stage_hash72: str | None = None
        try:
            i36, _, _ = self._active_i36()
            i36_ready = True
            active_i36_receipt_hash72 = str(i36["i36_receipt_hash72"])
            active_i36_stage_hash72 = str(i36["manifest_bound_i4_stage_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I37_STATUS_SCHEMA,
            "version": PASS218_I37_VERSION,
            "status": PASS218_I37_COMPLETE_STATUS if active is not None else PASS218_I37_PENDING_STATUS,
            "i36_complete_state_ready": i36_ready,
            "active_i36_receipt_hash72": active_i36_receipt_hash72,
            "active_i36_stage_hash72": active_i36_stage_hash72,
            "active_i37_receipt_hash72": None if active is None else active["i37_receipt_hash72"],
            "manifest_bound_i5_proof_hash72": None if active is None else active["manifest_bound_i5_proof_hash72"],
            "i5_proof_hash72": None if active is None else active["i5_proof_hash72"],
            "i5_prove_invocation_count_current_process": self.i5_prove_invocation_count,
            "pass218_i5_promotability_proof_invoked": active is not None or self.i5_prove_invocation_count > 0,
            "i5_promotable": active is not None,
            "promotability_proof_non_authoritative": active is not None,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
            "pass218_i5_promotion_invoked": False,
            "i5_explicit_authority_grant_present": False,
            "i5_promotion_authorization_invoked": False,
            "canonical_mutation_permitted": False,
            "pass218_i6_canonical_commit_invoked": False,
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
    "PASS218_I37_COMPLETE_STATUS",
    "PASS218_I37_PENDING_STATUS",
    "PASS218_I37_PROOF_SCHEMA",
    "PASS218_I37_RECEIPT_SCHEMA",
    "PASS218_I37_SCOPE",
    "PASS218_I37_STATE_SCHEMA",
    "PASS218_I37_STATUS_SCHEMA",
    "PASS218_I37_VERSION",
    "Pass218I37BindingError",
    "Pass218I37I5Error",
    "Pass218I37ManifestBoundPromotionAdmissionProof",
    "Pass218I37ManifestBoundPromotionProofStore",
    "Pass218I37ProofIngressError",
    "Pass218I37StateError",
]
