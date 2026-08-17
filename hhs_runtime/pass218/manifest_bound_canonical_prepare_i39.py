"""Pass 218 Iteration 39 manifest-bound frozen-I6 canonical prepare ingress.

I39 begins only from the exact durable I38 promotion authorization, the exact
I37 promotability proof, and the exact manifest-bound I36 frozen-I4 stage. It
revalidates that lineage, exposes the persisted I5 authorization through a
read-only journal view, and invokes frozen I6 ``prepare`` exactly once.

Frozen I6 preparation proves the complete 5,184-bit projection through all 64
VM81 shadow lanes but does not mutate the canonical Pass-217 vector target or
canonical VM81 image. I39 deliberately stops before I6 ``commit`` and before
I7 durable canonical persistence so restartability never depends on an
unpersisted canonical mutation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES, THREADS
from hhs_runtime.pass218.commit_boundary import (
    PASS218_CANONICAL_COMMIT_VERSION,
    PROMOTION_SCOPE,
    Pass218CanonicalCommitBoundary,
    Pass218CanonicalCommitError,
)
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    PASS218_I37_COMPLETE_STATUS,
)
from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import (
    PASS218_I38_COMPLETE_STATUS,
    PASS218_I38_RECEIPT_SCHEMA,
)
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    PASS218_I36_COMPLETE_STATUS,
)
from hhs_runtime.pass218.promotion import (
    PASS218_PROMOTION_MEMBRANE_VERSION,
    Pass218PromotionError,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
)

PASS218_I39_VERSION = "HHS-P218-I39-MANIFEST-BOUND-CANONICAL-PREPARE-V1"
PASS218_I39_SCOPE = "PASS218_MANIFEST_BOUND_CANONICAL_PREPARE_INGRESS"
PASS218_I39_RECEIPT_SCHEMA = "HHS-P218-I39-MANIFEST-BOUND-CANONICAL-PREPARE-RECEIPT-V1"
PASS218_I39_PREPARE_SCHEMA = "HHS-P218-I39-MANIFEST-BOUND-CANONICAL-PREPARE-V1"
PASS218_I39_STATE_SCHEMA = "HHS-P218-I39-MANIFEST-BOUND-CANONICAL-PREPARE-STATE-V1"
PASS218_I39_STATUS_SCHEMA = "HHS-P218-I39-MANIFEST-BOUND-CANONICAL-PREPARE-STATUS-V1"
PASS218_I39_COMPLETE_STATUS = "MANIFEST_BOUND_CANONICAL_PREPARE_INGRESS_COMPLETE"
PASS218_I39_PENDING_STATUS = "MANIFEST_BOUND_CANONICAL_PREPARE_PENDING"


class Pass218I39CanonicalPrepareError(RuntimeError):
    pass


class Pass218I39BindingError(Pass218I39CanonicalPrepareError):
    pass


class Pass218I39StateError(Pass218I39CanonicalPrepareError):
    pass


class Pass218I39I6Error(Pass218I39CanonicalPrepareError):
    pass


class Pass218I39LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I39I38StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_authorization_envelope(self) -> dict[str, Any] | None: ...
    def active_authorization(self) -> dict[str, Any] | None: ...


class Pass218I39I37StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class Pass218I39I36StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_stage(self) -> dict[str, Any] | None: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I39BindingError("P218_I39_AUTHORITATIVE_FLOAT_FORBIDDEN")
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
        raise Pass218I39StateError("P218_I39_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I39StateError("P218_I39_STATE_OBJECT_REQUIRED")
    _reject_float(value)
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


def _validate_authorization_record(
    authorization: Mapping[str, Any],
    *,
    proof: Mapping[str, Any],
    grant: Mapping[str, Any],
) -> dict[str, Any]:
    """Purely validate the already-persisted frozen-I5 authorization."""
    record = _copy(dict(authorization))
    proof_record = _copy(dict(proof))
    grant_record = _copy(dict(grant))
    try:
        PromotionProofMembrane.validate_proof_record(proof_record)
        PromotionAuthorizationJournal._validate_grant(proof_record, grant_record)
    except Pass218PromotionError as exc:
        raise Pass218I39BindingError("P218_I39_I5_PROOF_OR_GRANT_INVALID:" + str(exc)) from exc
    if record.get("schema") != "HHS-P218-I5-PROMOTION-AUTHORIZATION-V1":
        raise Pass218I39BindingError("P218_I39_I5_AUTHORIZATION_SCHEMA_INVALID")
    expected_payload = {
        "schema": "HHS-P218-I5-PROMOTION-AUTHORIZATION-PAYLOAD-V1",
        "entry_id_sha256": proof_record["entry_id_sha256"],
        "proof_hash72": proof_record["proof_hash72"],
        "grant_hash72": grant_record["grant_hash72"],
        "staging_hash72": proof_record["staging_hash72"],
        "projection_sha256": proof_record["projection_sha256"],
        "target_scope": grant_record["target_scope"],
    }
    authorization_hash72 = hash72_digest(
        {"domain": "HHS-P218-I5-PROMOTION-AUTHORIZATION-V1"},
        expected_payload,
    )
    validation_payload = {
        "schema": "HHS-P218-I5-PROMOTION-AUTHORIZATION-VALIDATION-V1",
        "authorization_hash72": authorization_hash72,
        "proof_present": True,
        "grant_present": True,
        "candidate_binding_exact": True,
        "scope_exact": True,
        "canonical_mutation_permitted": True,
        "canonical_mutation_invoked": False,
    }
    validation_hash72 = hash72_digest(
        {"domain": "HHS-P218-I5-PROMOTION-AUTHORIZATION-VALIDATION-V1"},
        validation_payload,
    )
    authorization_hash216 = (
        proof_record["proof_hash72"]
        + grant_record["grant_hash72"]
        + validation_hash72
    )
    exact = {
        "authorization_hash72": authorization_hash72,
        "validation_hash72": validation_hash72,
        "authorization_hash216": authorization_hash216,
        "entry_id_sha256": proof_record["entry_id_sha256"],
        "proof_hash72": proof_record["proof_hash72"],
        "grant_hash72": grant_record["grant_hash72"],
        "staging_hash72": proof_record["staging_hash72"],
        "projection_sha256": proof_record["projection_sha256"],
        "target_scope": PROMOTION_SCOPE,
    }
    for field, expected in exact.items():
        if record.get(field) != expected:
            raise Pass218I39BindingError("P218_I39_I5_AUTHORIZATION_BINDING_MISMATCH:" + field)
    if record.get("state") != "AUTHORIZED_PENDING_CANONICAL_COMMIT":
        raise Pass218I39BindingError("P218_I39_I5_AUTHORIZATION_STATE_INVALID")
    if record.get("proof_required") is not True or record.get("grant_required") is not True:
        raise Pass218I39BindingError("P218_I39_I5_AUTHORIZATION_PROOF_GRANT_INVALID")
    if record.get("canonical_mutation_permitted") is not True:
        raise Pass218I39BindingError("P218_I39_I5_MUTATION_PERMISSION_MISSING")
    for field in (
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
    ):
        if record.get(field) is not False:
            raise Pass218I39BindingError("P218_I39_I5_AUTHORIZATION_DRIFT:" + field)
    if not _valid_hash216(record.get("authorization_hash216")):
        raise Pass218I39BindingError("P218_I39_I5_AUTHORIZATION_HASH216_INVALID")
    return record


class DurableI38AuthorizationJournalView:
    """Read-only I6 journal protocol over one exact durable I38 authorization."""

    def __init__(self, authorization: Mapping[str, Any]) -> None:
        self._authorization = _copy(dict(authorization))

    def get(self, authorization_hash72: str) -> dict[str, Any] | None:
        if authorization_hash72 != self._authorization.get("authorization_hash72"):
            return None
        return _copy(self._authorization)

    def mutation_precondition(
        self,
        authorization_hash72: str,
        *,
        entry_id_sha256: str,
        projection_sha256: str,
        target_scope: str = PROMOTION_SCOPE,
    ) -> bool:
        record = self._authorization
        return bool(
            record.get("authorization_hash72") == authorization_hash72
            and record.get("state") == "AUTHORIZED_PENDING_CANONICAL_COMMIT"
            and record.get("canonical_mutation_permitted") is True
            and record.get("entry_id_sha256") == entry_id_sha256
            and record.get("projection_sha256") == projection_sha256
            and record.get("target_scope") == target_scope
            and record.get("proof_required") is True
            and record.get("grant_required") is True
        )


def _verify_predecessors(
    *,
    i38_receipt: Mapping[str, Any],
    authorization_envelope: Mapping[str, Any],
    i37_receipt: Mapping[str, Any],
    i37_proof_envelope: Mapping[str, Any],
    i36_receipt: Mapping[str, Any],
    i36_stage_envelope: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    i38 = _copy(dict(i38_receipt))
    auth_envelope = _copy(dict(authorization_envelope))
    i37 = _copy(dict(i37_receipt))
    proof_envelope = _copy(dict(i37_proof_envelope))
    i36 = _copy(dict(i36_receipt))
    stage_envelope = _copy(dict(i36_stage_envelope))
    if i38.get("schema") != PASS218_I38_RECEIPT_SCHEMA or i38.get("status") != PASS218_I38_COMPLETE_STATUS:
        raise Pass218I39BindingError("P218_I39_I38_COMPLETE_STATE_REQUIRED")
    if i37.get("status") != PASS218_I37_COMPLETE_STATUS:
        raise Pass218I39BindingError("P218_I39_I37_COMPLETE_STATE_REQUIRED")
    if i36.get("status") != PASS218_I36_COMPLETE_STATUS:
        raise Pass218I39BindingError("P218_I39_I36_COMPLETE_STATE_REQUIRED")
    if i38.get("i37_receipt_hash72") != i37.get("i37_receipt_hash72"):
        raise Pass218I39BindingError("P218_I39_I38_I37_RECEIPT_MISMATCH")
    if i37.get("i36_receipt_hash72") != i36.get("i36_receipt_hash72"):
        raise Pass218I39BindingError("P218_I39_I37_I36_RECEIPT_MISMATCH")
    manifest = i38.get("manifest_binding")
    if not isinstance(manifest, Mapping):
        raise Pass218I39BindingError("P218_I39_MANIFEST_BINDING_REQUIRED")
    if i37.get("manifest_binding") != manifest or i36.get("manifest_binding") != manifest:
        raise Pass218I39BindingError("P218_I39_MANIFEST_LINEAGE_MISMATCH")
    if proof_envelope.get("manifest_binding") != manifest or stage_envelope.get("manifest_binding") != manifest:
        raise Pass218I39BindingError("P218_I39_ENVELOPE_MANIFEST_LINEAGE_MISMATCH")
    if auth_envelope.get("manifest_binding") != manifest:
        raise Pass218I39BindingError("P218_I39_AUTHORIZATION_MANIFEST_MISMATCH")
    proof = proof_envelope.get("i5_promotability_proof")
    grant = auth_envelope.get("i5_authority_grant")
    authorization = auth_envelope.get("i5_promotion_authorization")
    i4_stage = stage_envelope.get("i4_stage_candidate")
    if not all(isinstance(value, Mapping) for value in (proof, grant, authorization, i4_stage)):
        raise Pass218I39BindingError("P218_I39_REQUIRED_FROZEN_ARTIFACT_MISSING")
    if auth_envelope.get("manifest_bound_i5_authorization_hash72") != i38.get("manifest_bound_i5_authorization_hash72"):
        raise Pass218I39BindingError("P218_I39_I38_AUTHORIZATION_ENVELOPE_MISMATCH")
    if proof_envelope.get("manifest_bound_i5_proof_hash72") != i38.get("manifest_bound_i5_proof_hash72"):
        raise Pass218I39BindingError("P218_I39_I37_PROOF_ENVELOPE_MISMATCH")
    if stage_envelope.get("manifest_bound_i4_stage_hash72") != i36.get("manifest_bound_i4_stage_hash72"):
        raise Pass218I39BindingError("P218_I39_I36_STAGE_ENVELOPE_MISMATCH")
    if i38.get("i4_entry_id_sha256") != i36.get("i4_entry_id_sha256"):
        raise Pass218I39BindingError("P218_I39_I4_ENTRY_ID_MISMATCH")
    if i38.get("i4_projection_sha256") != i36.get("i4_projection_sha256"):
        raise Pass218I39BindingError("P218_I39_I4_PROJECTION_SHA256_MISMATCH")
    if authorization.get("staging_hash72") != i36.get("i4_staging_hash72"):
        raise Pass218I39BindingError("P218_I39_I4_STAGING_HASH_MISMATCH")
    checked_authorization = _validate_authorization_record(
        authorization,
        proof=proof,
        grant=grant,
    )
    if checked_authorization.get("authorization_hash72") != i38.get("i5_authorization_hash72"):
        raise Pass218I39BindingError("P218_I39_I38_AUTHORIZATION_HASH_MISMATCH")
    if checked_authorization.get("entry_id_sha256") != i4_stage.get("vector_entry", {}).get("entry_id_sha256"):
        raise Pass218I39BindingError("P218_I39_I4_AUTHORIZATION_ENTRY_MISMATCH")
    if checked_authorization.get("projection_sha256") != i4_stage.get("vm5184_projection_sha256"):
        raise Pass218I39BindingError("P218_I39_I4_AUTHORIZATION_PROJECTION_MISMATCH")
    return i38, checked_authorization, _copy(dict(i4_stage)), _copy(dict(proof))


def _verify_i6_prepare_record(
    record: Mapping[str, Any],
    *,
    i38: Mapping[str, Any],
    i36: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(record))
    if value.get("schema") != "HHS-P218-I6-CANONICAL-PREPARE-V1":
        raise Pass218I39I6Error("P218_I39_I6_PREPARE_SCHEMA_INVALID")
    if value.get("boundary_version") != PASS218_CANONICAL_COMMIT_VERSION:
        raise Pass218I39I6Error("P218_I39_I6_BOUNDARY_VERSION_INVALID")
    for field in (
        "authorization_hash72",
        "projection_hash72",
        "target_root_before_hash72",
        "vm81_prepared_snapshot_hash72",
        "vm81_prepared_state_hash72",
        "vm81_prepare_receipts_root_hash72",
        "prepare_hash72",
        "validation_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I39I6Error("P218_I39_I6_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("prepare_hash216")):
        raise Pass218I39I6Error("P218_I39_I6_PREPARE_HASH216_INVALID")
    if value.get("prepare_hash216") != (
        str(value["authorization_hash72"])
        + str(value["prepare_hash72"])
        + str(value["validation_hash72"])
    ):
        raise Pass218I39I6Error("P218_I39_I6_PREPARE_HASH216_ORDER_INVALID")
    if value.get("authorization_hash72") != i38.get("i5_authorization_hash72"):
        raise Pass218I39I6Error("P218_I39_I6_AUTHORIZATION_BINDING_MISMATCH")
    if value.get("candidate_entry_id_sha256") != i38.get("i4_entry_id_sha256"):
        raise Pass218I39I6Error("P218_I39_I6_ENTRY_BINDING_MISMATCH")
    if value.get("projection_sha256") != i38.get("i4_projection_sha256"):
        raise Pass218I39I6Error("P218_I39_I6_PROJECTION_BINDING_MISMATCH")
    if value.get("projection_hash72") != i36.get("i4_projection_hash72"):
        raise Pass218I39I6Error("P218_I39_I6_PROJECTION_HASH72_MISMATCH")
    if value.get("vm81_prepared_snapshot_hash72") != value.get("projection_hash72"):
        raise Pass218I39I6Error("P218_I39_I6_VM81_SHADOW_PROJECTION_MISMATCH")
    if value.get("vm81_prepare_commit_count") != THREADS:
        raise Pass218I39I6Error("P218_I39_I6_VM81_SHADOW_THREAD_COUNT_INVALID")
    if not _valid_sha256(value.get("admitted_entry_id_sha256")):
        raise Pass218I39I6Error("P218_I39_I6_ADMITTED_ENTRY_ID_INVALID")
    for field in (
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        if value.get(field) is not False:
            raise Pass218I39I6Error("P218_I39_I6_PREPARE_AUTHORITY_DRIFT:" + field)
    return value


def _verify_i39_prepare(envelope: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(envelope))
    if value.get("schema") != PASS218_I39_PREPARE_SCHEMA:
        raise Pass218I39StateError("P218_I39_PREPARE_ENVELOPE_SCHEMA_INVALID")
    body = {key: item for key, item in value.items() if key != "manifest_bound_i6_prepare_hash72"}
    expected = hash72_digest({"domain": PASS218_I39_PREPARE_SCHEMA}, body)
    if expected != value.get("manifest_bound_i6_prepare_hash72"):
        raise Pass218I39StateError("P218_I39_PREPARE_ENVELOPE_HASH_MISMATCH")
    if expected != receipt.get("manifest_bound_i6_prepare_hash72"):
        raise Pass218I39StateError("P218_I39_PREPARE_RECEIPT_MISMATCH")
    if value.get("i38_receipt_hash72") != receipt.get("i38_receipt_hash72"):
        raise Pass218I39StateError("P218_I39_PREPARE_I38_MISMATCH")
    return value


def _verify_i39_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I39_RECEIPT_SCHEMA:
        raise Pass218I39StateError("P218_I39_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I39_COMPLETE_STATUS:
        raise Pass218I39StateError("P218_I39_RECEIPT_STATUS_INVALID")
    for field in (
        "i38_receipt_hash72",
        "i5_authorization_hash72",
        "manifest_bound_i4_stage_hash72",
        "i6_prepare_hash72",
        "i6_validation_hash72",
        "i6_target_root_before_hash72",
        "i6_vm81_prepared_snapshot_hash72",
        "manifest_bound_i6_prepare_hash72",
        "i39_validation_hash72",
        "i39_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I39StateError("P218_I39_RECEIPT_HASH72_INVALID:" + field)
    for field in ("i38_hash216", "i6_prepare_hash216", "i39_hash216"):
        if not _valid_hash216(value.get(field)):
            raise Pass218I39StateError("P218_I39_RECEIPT_HASH216_INVALID:" + field)
    if value.get("i39_hash216") != (
        str(value["i38_receipt_hash72"])
        + str(value["i6_prepare_hash72"])
        + str(value["i39_receipt_hash72"])
    ):
        raise Pass218I39StateError("P218_I39_HASH216_ORDER_INVALID")
    required_true = (
        "i38_receipt_bound",
        "manifest_binding_propagated",
        "i36_stage_bound",
        "i37_proof_bound",
        "i5_authorization_bound",
        "pass218_i6_prepare_invoked",
        "i6_prepare_noncanonical",
        "i6_vm81_shadow_prepare_complete",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I39StateError("P218_I39_RECEIPT_PREPARE_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "pass218_i6_canonical_commit_invoked",
        "pass218_i7_durable_persistence_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I39StateError("P218_I39_RECEIPT_CANONICAL_DRIFT")
    if value.get("i6_vm81_shadow_commit_count") != THREADS:
        raise Pass218I39StateError("P218_I39_RECEIPT_VM81_SHADOW_COUNT_INVALID")
    if value.get("i6_projection_bytes") != SNAPSHOT_BYTES:
        raise Pass218I39StateError("P218_I39_RECEIPT_PROJECTION_LENGTH_INVALID")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i39_receipt_hash72", "i39_hash216", "i39_hash216_semantics"}
    }
    expected = hash72_digest({"domain": PASS218_I39_RECEIPT_SCHEMA}, body)
    if expected != value.get("i39_receipt_hash72"):
        raise Pass218I39StateError("P218_I39_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I39ManifestBoundCanonicalPrepareStore:
    """Durable nonverbatim I39 prepare record and binding receipt."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.prepare_root = self.root / "prepares"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I39_STATE_SCHEMA:
            raise Pass218I39StateError("P218_I39_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I39_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I39StateError("P218_I39_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        prepare_path = self.root / str(state.get("active_prepare_path", ""))
        if not receipt_path.is_file() or not prepare_path.is_file():
            raise Pass218I39StateError("P218_I39_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i39_receipt(_load_json(receipt_path))
        if receipt["i39_receipt_hash72"] != state.get("active_i39_receipt_hash72"):
            raise Pass218I39StateError("P218_I39_STATE_RECEIPT_MISMATCH")
        prepare = _verify_i39_prepare(_load_json(prepare_path), receipt)
        if prepare["manifest_bound_i6_prepare_hash72"] != state.get("active_prepare_hash72"):
            raise Pass218I39StateError("P218_I39_STATE_PREPARE_MISMATCH")
        return receipt

    def active_prepare(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i39_prepare(
            _load_json(self.root / str(state["active_prepare_path"])),
            receipt,
        )

    def commit(self, receipt: Mapping[str, Any], prepare_envelope: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_i39_receipt(receipt)
        prepare = _verify_i39_prepare(prepare_envelope, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_prepare() != prepare:
                raise Pass218I39StateError("P218_I39_ACTIVE_BINDING_CONFLICT")
            return existing
        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_path = self.receipt_root / f"{ordinal:08d}-{checked['i39_receipt_hash72']}.json"
        prepare_path = self.prepare_root / f"{checked['manifest_bound_i6_prepare_hash72']}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(prepare_path, prepare)
        state_body = {
            "schema": PASS218_I39_STATE_SCHEMA,
            "version": PASS218_I39_VERSION,
            "status": PASS218_I39_COMPLETE_STATUS,
            "i38_receipt_hash72": checked["i38_receipt_hash72"],
            "active_i39_receipt_hash72": checked["i39_receipt_hash72"],
            "active_prepare_hash72": checked["manifest_bound_i6_prepare_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_prepare_path": prepare_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest({"domain": PASS218_I39_STATE_SCHEMA}, state_body),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I39StateError("P218_I39_STATE_PERSIST_MISMATCH")
        return checked


class Pass218I39ManifestBoundCanonicalPrepare:
    """Bind exact frozen I38/I37/I36 state to frozen I6 prepare only."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I39LifecycleProtocol,
        i38_store: Pass218I39I38StoreProtocol,
        i37_store: Pass218I39I37StoreProtocol,
        i36_store: Pass218I39I36StoreProtocol,
        state_root: str | os.PathLike[str],
        i38_status_provider: Callable[[], Mapping[str, Any]] | None = None,
        i36_status_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i38_store = i38_store
        self.i37_store = i37_store
        self.i36_store = i36_store
        self.i38_status_provider = i38_status_provider
        self.i36_status_provider = i36_status_provider
        self.store = Pass218I39ManifestBoundCanonicalPrepareStore(state_root)
        self.i6_prepare_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _active_predecessors(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        i38 = self.i38_store.active_record()
        auth_envelope = self.i38_store.active_authorization_envelope()
        i37 = self.i37_store.active_record()
        proof_envelope = self.i37_store.active_proof()
        i36 = self.i36_store.active_record()
        stage_envelope = self.i36_store.active_stage()
        if any(value is None for value in (i38, auth_envelope, i37, proof_envelope, i36, stage_envelope)):
            raise Pass218I39BindingError("P218_I39_PREDECESSOR_COMPLETE_STATE_REQUIRED")
        assert i38 is not None and auth_envelope is not None
        assert i37 is not None and proof_envelope is not None
        assert i36 is not None and stage_envelope is not None
        if self.i38_status_provider is not None:
            status = dict(self.i38_status_provider())
            if status.get("status") != PASS218_I38_COMPLETE_STATUS:
                raise Pass218I39BindingError("P218_I39_I38_STATUS_NOT_COMPLETE")
            if status.get("active_i38_receipt_hash72") != i38.get("i38_receipt_hash72"):
                raise Pass218I39BindingError("P218_I39_I38_STATUS_RECEIPT_MISMATCH")
        if self.i36_status_provider is not None:
            status = dict(self.i36_status_provider())
            if status.get("status") != PASS218_I36_COMPLETE_STATUS:
                raise Pass218I39BindingError("P218_I39_I36_STATUS_NOT_COMPLETE")
            if status.get("active_i36_receipt_hash72") != i36.get("i36_receipt_hash72"):
                raise Pass218I39BindingError("P218_I39_I36_STATUS_RECEIPT_MISMATCH")
        return i38, auth_envelope, i37, proof_envelope, i36, stage_envelope

    def prepare(self) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            i38_raw, auth_envelope, i37, proof_envelope, i36, stage_envelope = self._active_predecessors()
            i38, authorization, i4_stage, proof = _verify_predecessors(
                i38_receipt=i38_raw,
                authorization_envelope=auth_envelope,
                i37_receipt=i37,
                i37_proof_envelope=proof_envelope,
                i36_receipt=i36,
                i36_stage_envelope=stage_envelope,
            )
            existing = self.store.active_record()
            if existing is not None:
                if (
                    existing["i38_receipt_hash72"] != i38["i38_receipt_hash72"]
                    or existing["manifest_bound_i4_stage_hash72"] != i36["manifest_bound_i4_stage_hash72"]
                    or existing["manifest_binding"] != i38["manifest_binding"]
                ):
                    raise Pass218I39StateError("P218_I39_ACTIVE_BINDING_CONFLICT")
                self.last_error_code = None
                return existing

            journal_view = DurableI38AuthorizationJournalView(authorization)
            boundary = Pass218CanonicalCommitBoundary()
            try:
                prepared = boundary.prepare(
                    authorization=authorization,
                    staged_candidate=i4_stage,
                    authorization_journal=journal_view,
                )
                self.i6_prepare_invocation_count += 1
            except Pass218CanonicalCommitError as exc:
                raise Pass218I39I6Error("P218_I39_I6_PREPARE_FAILED:" + str(exc)) from exc
            prepare_record = _verify_i6_prepare_record(
                prepared.to_record(),
                i38=i38,
                i36=i36,
            )
            if boundary.target.record()["canonical_entry_count"] != 0 or boundary.target.record()["canonical_commit_count"] != 0:
                raise Pass218I39I6Error("P218_I39_I6_PREPARE_MUTATED_CANONICAL_TARGET")

            prepare_body = {
                "schema": PASS218_I39_PREPARE_SCHEMA,
                "version": PASS218_I39_VERSION,
                "i38_receipt_hash72": i38["i38_receipt_hash72"],
                "i38_hash216": i38["i38_hash216"],
                "manifest_bound_i5_authorization_hash72": i38["manifest_bound_i5_authorization_hash72"],
                "i5_authorization_hash72": authorization["authorization_hash72"],
                "i37_receipt_hash72": i38["i37_receipt_hash72"],
                "i37_proof_hash72": proof["proof_hash72"],
                "i36_receipt_hash72": i36["i36_receipt_hash72"],
                "manifest_bound_i4_stage_hash72": i36["manifest_bound_i4_stage_hash72"],
                "manifest_binding": _copy(i38["manifest_binding"]),
                "i6_boundary_version": PASS218_CANONICAL_COMMIT_VERSION,
                "i6_prepare_record": prepare_record,
                "i6_prepare_noncanonical": True,
                "i6_commit_invoked": False,
                "i7_persistence_invoked": False,
                "verbatim_source_retained": False,
            }
            manifest_bound_prepare_hash72 = hash72_digest(
                {"domain": PASS218_I39_PREPARE_SCHEMA}, prepare_body
            )
            prepare_envelope = {
                **prepare_body,
                "manifest_bound_i6_prepare_hash72": manifest_bound_prepare_hash72,
            }
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I39-MANIFEST-BOUND-CANONICAL-PREPARE-VALIDATION-V1"},
                {
                    "i38_receipt_hash72": i38["i38_receipt_hash72"],
                    "i5_authorization_hash72": authorization["authorization_hash72"],
                    "manifest_bound_i4_stage_hash72": i36["manifest_bound_i4_stage_hash72"],
                    "i6_prepare_hash72": prepare_record["prepare_hash72"],
                    "manifest_bound_i6_prepare_hash72": manifest_bound_prepare_hash72,
                    "vm81_shadow_commit_count": prepare_record["vm81_prepare_commit_count"],
                    "canonical_target_unmutated": True,
                    "i6_commit_invoked": False,
                    "i7_persistence_invoked": False,
                },
            )
            body = {
                "schema": PASS218_I39_RECEIPT_SCHEMA,
                "version": PASS218_I39_VERSION,
                "scope": PASS218_I39_SCOPE,
                "status": PASS218_I39_COMPLETE_STATUS,
                "i38_receipt_hash72": i38["i38_receipt_hash72"],
                "i38_hash216": i38["i38_hash216"],
                "manifest_bound_i5_authorization_hash72": i38["manifest_bound_i5_authorization_hash72"],
                "i5_authorization_hash72": authorization["authorization_hash72"],
                "i37_receipt_hash72": i38["i37_receipt_hash72"],
                "i36_receipt_hash72": i36["i36_receipt_hash72"],
                "manifest_bound_i4_stage_hash72": i36["manifest_bound_i4_stage_hash72"],
                "manifest_binding": _copy(i38["manifest_binding"]),
                "i4_entry_id_sha256": i38["i4_entry_id_sha256"],
                "i4_projection_sha256": i38["i4_projection_sha256"],
                "i6_boundary_version": PASS218_CANONICAL_COMMIT_VERSION,
                "i6_prepare_hash72": prepare_record["prepare_hash72"],
                "i6_validation_hash72": prepare_record["validation_hash72"],
                "i6_prepare_hash216": prepare_record["prepare_hash216"],
                "i6_admitted_entry_id_sha256": prepare_record["admitted_entry_id_sha256"],
                "i6_projection_hash72": prepare_record["projection_hash72"],
                "i6_projection_bytes": SNAPSHOT_BYTES,
                "i6_target_root_before_hash72": prepare_record["target_root_before_hash72"],
                "i6_vm81_prepared_snapshot_hash72": prepare_record["vm81_prepared_snapshot_hash72"],
                "i6_vm81_prepared_state_hash72": prepare_record["vm81_prepared_state_hash72"],
                "i6_vm81_shadow_commit_count": prepare_record["vm81_prepare_commit_count"],
                "i6_vm81_prepare_receipts_root_hash72": prepare_record["vm81_prepare_receipts_root_hash72"],
                "manifest_bound_i6_prepare_hash72": manifest_bound_prepare_hash72,
                "i39_validation_hash72": validation_hash72,
                "i38_receipt_bound": True,
                "manifest_binding_propagated": True,
                "i36_stage_bound": True,
                "i37_proof_bound": True,
                "i5_authorization_bound": True,
                "pass218_i6_prepare_invoked": True,
                "i6_prepare_noncanonical": True,
                "i6_vm81_shadow_prepare_complete": True,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
                "pass218_i6_canonical_commit_invoked": False,
                "pass218_i7_durable_persistence_invoked": False,
                "pass218_i30_canonical_semantic_promotion_invoked": False,
                "pass218_i31_verbatim_purge_invoked": False,
                "pass218_i32_source_closure_invoked": False,
                "curriculum_cursor_advanced": False,
                "stage_advance_permitted": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "authoritative_vector_store_promotion": False,
                "canonical_vector_store_mutation_invoked": False,
                "canonical_vm81_commit_invoked": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
            receipt_hash72 = hash72_digest({"domain": PASS218_I39_RECEIPT_SCHEMA}, body)
            receipt = {
                **body,
                "i39_receipt_hash72": receipt_hash72,
                "i39_hash216": (
                    i38["i38_receipt_hash72"]
                    + prepare_record["prepare_hash72"]
                    + receipt_hash72
                ),
                "i39_hash216_semantics": [
                    "I38_MANIFEST_BOUND_PROMOTION_AUTHORIZATION_RECEIPT",
                    "I6_NONCANONICAL_VM81_PREPARE",
                    "I39_MANIFEST_BOUND_PREPARE_BINDING_RECEIPT",
                ],
            }
            persisted = self.store.commit(receipt, prepare_envelope)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        predecessor_ready = False
        active_i38_receipt_hash72: str | None = None
        active_i36_stage_hash72: str | None = None
        try:
            i38, _, _, _, i36, _ = self._active_predecessors()
            predecessor_ready = True
            active_i38_receipt_hash72 = str(i38["i38_receipt_hash72"])
            active_i36_stage_hash72 = str(i36["manifest_bound_i4_stage_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I39_STATUS_SCHEMA,
            "version": PASS218_I39_VERSION,
            "status": PASS218_I39_COMPLETE_STATUS if active is not None else PASS218_I39_PENDING_STATUS,
            "predecessor_state_ready": predecessor_ready,
            "active_i38_receipt_hash72": active_i38_receipt_hash72,
            "active_i36_stage_hash72": active_i36_stage_hash72,
            "active_i39_receipt_hash72": None if active is None else active["i39_receipt_hash72"],
            "manifest_bound_i6_prepare_hash72": None if active is None else active["manifest_bound_i6_prepare_hash72"],
            "i6_prepare_invocation_count_current_process": self.i6_prepare_invocation_count,
            "i6_prepare_noncanonical": None if active is None else active["i6_prepare_noncanonical"],
            "i6_vm81_shadow_commit_count": None if active is None else active["i6_vm81_shadow_commit_count"],
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "pass218_i6_canonical_commit_invoked": False,
            "pass218_i7_durable_persistence_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "DurableI38AuthorizationJournalView",
    "PASS218_I39_COMPLETE_STATUS",
    "PASS218_I39_PENDING_STATUS",
    "PASS218_I39_PREPARE_SCHEMA",
    "PASS218_I39_RECEIPT_SCHEMA",
    "PASS218_I39_SCOPE",
    "PASS218_I39_STATE_SCHEMA",
    "PASS218_I39_STATUS_SCHEMA",
    "PASS218_I39_VERSION",
    "Pass218I39BindingError",
    "Pass218I39CanonicalPrepareError",
    "Pass218I39I6Error",
    "Pass218I39ManifestBoundCanonicalPrepare",
    "Pass218I39ManifestBoundCanonicalPrepareStore",
    "Pass218I39StateError",
]
