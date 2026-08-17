"""Pass 218 Iteration 40 manifest-bound atomic canonical commit and persistence.

I40 begins only from the exact durable I39 noncanonical prepare binding plus its
frozen I38/I37/I36 lineage. I39 intentionally persisted the serializable I6
prepare proof rather than the live ``PreparedCanonicalAdmission`` object. I40
therefore reconstructs that object by re-running frozen I6 ``prepare`` from the
same durable authorization and I4 candidate and requires the resulting record
to equal I39 bit-for-bit before canonical mutation is permitted.

Only then may frozen I6 perform its atomic canonical Pass-217/VM81 commit. The
committed target is immediately sealed by the frozen I7 compatibility-backed
durable store and restored as an independent restart proof. I40 stops before
canonical learning, truth/action authority, semantic promotion/purge/closure,
curriculum advancement, model activation, or authoritative floating-point
state.
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
    Pass218CanonicalCommitBoundary,
    Pass218CanonicalCommitError,
)
from hhs_runtime.pass218.manifest_bound_canonical_prepare_i39 import (
    DurableI38AuthorizationJournalView,
    PASS218_I39_COMPLETE_STATUS,
    PASS218_I39_RECEIPT_SCHEMA,
    _atomic_write_json,
    _copy,
    _load_json,
    _valid_hash216,
    _verify_i39_prepare,
    _verify_i39_receipt,
    _verify_predecessors,
)
# Use the frozen I7 compatibility surface deliberately. Frozen I6's validated
# receipt bytes retain the historical outer COMMIT-PAYLOAD schema because its
# commit payload expansion overwrites the intended receipt label. I7's frozen
# compatibility adapter admits exactly that historical label or the intended
# label while independently validating every authoritative receipt field/hash.
from hhs_runtime.pass218.persistence_compat import (
    PASS218_PERSISTENCE_VERSION,
    Pass218DurableCanonicalStore,
    Pass218PersistenceError,
)

PASS218_I40_VERSION = "HHS-P218-I40-MANIFEST-BOUND-CANONICAL-COMMIT-PERSISTENCE-V1"
PASS218_I40_SCOPE = "PASS218_MANIFEST_BOUND_CANONICAL_COMMIT_PERSISTENCE_INGRESS"
PASS218_I40_RECEIPT_SCHEMA = "HHS-P218-I40-MANIFEST-BOUND-CANONICAL-COMMIT-PERSISTENCE-RECEIPT-V1"
PASS218_I40_BINDING_SCHEMA = "HHS-P218-I40-MANIFEST-BOUND-CANONICAL-COMMIT-PERSISTENCE-V1"
PASS218_I40_STATE_SCHEMA = "HHS-P218-I40-MANIFEST-BOUND-CANONICAL-COMMIT-PERSISTENCE-STATE-V1"
PASS218_I40_STATUS_SCHEMA = "HHS-P218-I40-MANIFEST-BOUND-CANONICAL-COMMIT-PERSISTENCE-STATUS-V1"
PASS218_I40_COMPLETE_STATUS = "MANIFEST_BOUND_CANONICAL_COMMIT_PERSISTENCE_INGRESS_COMPLETE"
PASS218_I40_PENDING_STATUS = "MANIFEST_BOUND_CANONICAL_COMMIT_PERSISTENCE_PENDING"

_I6_INTENDED_RECEIPT_SCHEMA = "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1"
_I6_FROZEN_OUTER_SCHEMA = "HHS-P218-I6-CANONICAL-COMMIT-PAYLOAD-V1"


class Pass218I40CanonicalPersistenceError(RuntimeError):
    pass


class Pass218I40BindingError(Pass218I40CanonicalPersistenceError):
    pass


class Pass218I40StateError(Pass218I40CanonicalPersistenceError):
    pass


class Pass218I40I6Error(Pass218I40CanonicalPersistenceError):
    pass


class Pass218I40I7Error(Pass218I40CanonicalPersistenceError):
    pass


class Pass218I40LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I40I39StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_prepare(self) -> dict[str, Any] | None: ...


class Pass218I40I38StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_authorization_envelope(self) -> dict[str, Any] | None: ...


class Pass218I40I37StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class Pass218I40I36StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_stage(self) -> dict[str, Any] | None: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I40BindingError("P218_I40_AUTHORITATIVE_FLOAT_FORBIDDEN")
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


def _valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _verify_i6_commit_receipt(
    receipt: Mapping[str, Any],
    *,
    i39_receipt: Mapping[str, Any],
    i39_prepare: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind the frozen I6 receipt to I39 without rewriting historical bytes.

    The actual frozen I6 receipt has the validated historical outer payload
    label. The intended receipt label is also admitted because frozen I7's
    compatibility adapter admits exactly those two labels. ``admission_status``
    is intentionally *not* required as a top-level I6 receipt field: frozen I6
    commits it inside the receipt-hash payload, while frozen I7 independently
    proves the canonical admitted entry itself is ``VM81_ADMITTED``.
    """

    value = _copy(dict(receipt))
    if value.get("schema") not in {
        _I6_INTENDED_RECEIPT_SCHEMA,
        _I6_FROZEN_OUTER_SCHEMA,
    }:
        raise Pass218I40I6Error("P218_I40_I6_COMMIT_RECEIPT_SCHEMA_INVALID")
    if value.get("boundary_version") != PASS218_CANONICAL_COMMIT_VERSION:
        raise Pass218I40I6Error("P218_I40_I6_BOUNDARY_VERSION_INVALID")
    prepare_record = i39_prepare.get("i6_prepare_record")
    if not isinstance(prepare_record, Mapping):
        raise Pass218I40BindingError("P218_I40_I39_PREPARE_RECORD_MISSING")

    exact = {
        "authorization_hash72": i39_receipt["i5_authorization_hash72"],
        "prepare_hash72": i39_receipt["i6_prepare_hash72"],
        "candidate_entry_id_sha256": i39_receipt["i4_entry_id_sha256"],
        "admitted_entry_id_sha256": i39_receipt["i6_admitted_entry_id_sha256"],
        "projection_sha256": i39_receipt["i4_projection_sha256"],
        "target_root_before_hash72": i39_receipt["i6_target_root_before_hash72"],
        "vm81_snapshot_hash72": i39_receipt["i6_vm81_prepared_snapshot_hash72"],
        "vm81_state_hash72": i39_receipt["i6_vm81_prepared_state_hash72"],
        "vm81_receipts_root_hash72": i39_receipt["i6_vm81_prepare_receipts_root_hash72"],
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise Pass218I40I6Error("P218_I40_I6_COMMIT_BINDING_MISMATCH:" + field)

    for field in (
        "authorization_hash72",
        "prepare_hash72",
        "target_root_before_hash72",
        "target_root_after_hash72",
        "vm81_snapshot_hash72",
        "vm81_state_hash72",
        "vm81_receipts_root_hash72",
        "commit_hash72",
        "receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I40I6Error("P218_I40_I6_COMMIT_HASH72_INVALID:" + field)
    if not _valid_hash216(value.get("commit_hash216")):
        raise Pass218I40I6Error("P218_I40_I6_COMMIT_HASH216_INVALID")
    if value.get("commit_hash216") != (
        str(value["prepare_hash72"])
        + str(value["commit_hash72"])
        + str(value["receipt_hash72"])
    ):
        raise Pass218I40I6Error("P218_I40_I6_COMMIT_HASH216_ORDER_INVALID")

    for field in (
        "candidate_entry_id_sha256",
        "admitted_entry_id_sha256",
        "projection_sha256",
    ):
        if not _valid_sha256(value.get(field)):
            raise Pass218I40I6Error("P218_I40_I6_COMMIT_SHA256_INVALID:" + field)
    if value.get("state") != "CANONICAL_COMMITTED":
        raise Pass218I40I6Error("P218_I40_I6_COMMIT_STATE_INVALID")
    if value.get("vm81_commit_count") != THREADS:
        raise Pass218I40I6Error("P218_I40_I6_VM81_COMMIT_COUNT_INVALID")

    for field in (
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "authorization_consumed",
        "atomic_swap",
    ):
        if value.get(field) is not True:
            raise Pass218I40I6Error("P218_I40_I6_REQUIRED_COMMIT_FLAG_MISSING:" + field)
    for field in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "canonical_mutation_permitted",
        "failed_partial_commit_possible",
    ):
        if value.get(field) is not False:
            raise Pass218I40I6Error("P218_I40_I6_FORBIDDEN_AUTHORITY_DRIFT:" + field)
    return value


def _verify_i40_binding(
    envelope: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(envelope))
    if value.get("schema") != PASS218_I40_BINDING_SCHEMA:
        raise Pass218I40StateError("P218_I40_BINDING_SCHEMA_INVALID")
    body = {
        key: item
        for key, item in value.items()
        if key != "manifest_bound_commit_persistence_hash72"
    }
    expected = hash72_digest({"domain": PASS218_I40_BINDING_SCHEMA}, body)
    if expected != value.get("manifest_bound_commit_persistence_hash72"):
        raise Pass218I40StateError("P218_I40_BINDING_HASH_MISMATCH")
    if expected != receipt.get("manifest_bound_commit_persistence_hash72"):
        raise Pass218I40StateError("P218_I40_BINDING_RECEIPT_MISMATCH")
    if value.get("i39_receipt_hash72") != receipt.get("i39_receipt_hash72"):
        raise Pass218I40StateError("P218_I40_BINDING_I39_MISMATCH")
    return value


def _verify_i40_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I40_RECEIPT_SCHEMA:
        raise Pass218I40StateError("P218_I40_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I40_COMPLETE_STATUS:
        raise Pass218I40StateError("P218_I40_RECEIPT_STATUS_INVALID")
    for field in (
        "i39_receipt_hash72",
        "i6_prepare_hash72",
        "i6_commit_hash72",
        "i6_commit_receipt_hash72",
        "i6_target_root_before_hash72",
        "i6_target_root_after_hash72",
        "i7_checkpoint_hash72",
        "i7_checkpoint_validation_hash72",
        "i7_manifest_hash72",
        "i7_restore_hash72",
        "manifest_bound_commit_persistence_hash72",
        "i40_validation_hash72",
        "i40_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I40StateError("P218_I40_RECEIPT_HASH72_INVALID:" + field)
    for field in ("i6_commit_hash216", "i7_checkpoint_hash216", "i40_hash216"):
        if not _valid_hash216(value.get(field)):
            raise Pass218I40StateError("P218_I40_RECEIPT_HASH216_INVALID:" + field)
    if value.get("i40_hash216") != (
        str(value["i39_receipt_hash72"])
        + str(value["i7_checkpoint_hash72"])
        + str(value["i40_receipt_hash72"])
    ):
        raise Pass218I40StateError("P218_I40_HASH216_ORDER_INVALID")

    for field in (
        "i39_prepare_bound",
        "manifest_binding_propagated",
        "i6_prepare_reconstructed_exactly",
        "pass218_i6_canonical_commit_invoked",
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "i6_authorization_consumed",
        "i6_atomic_swap",
        "pass218_i7_durable_persistence_invoked",
        "i7_checkpoint_durable",
        "i7_restore_verified",
    ):
        if value.get(field) is not True:
            raise Pass218I40StateError("P218_I40_RECEIPT_REQUIRED_STATE_MISSING:" + field)
    for field in (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
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
    ):
        if value.get(field) is not False:
            raise Pass218I40StateError("P218_I40_RECEIPT_DOWNSTREAM_AUTHORITY_DRIFT:" + field)
    if value.get("i6_vm81_commit_count") != THREADS:
        raise Pass218I40StateError("P218_I40_RECEIPT_VM81_COUNT_INVALID")
    if value.get("i7_vm81_snapshot_bytes") != SNAPSHOT_BYTES:
        raise Pass218I40StateError("P218_I40_RECEIPT_VM81_LENGTH_INVALID")
    if not _valid_sha256(value.get("i7_checkpoint_sha256")):
        raise Pass218I40StateError("P218_I40_RECEIPT_CHECKPOINT_SHA256_INVALID")

    body = {
        key: item
        for key, item in value.items()
        if key not in {
            "i40_receipt_hash72",
            "i40_hash216",
            "i40_hash216_semantics",
        }
    }
    expected = hash72_digest({"domain": PASS218_I40_RECEIPT_SCHEMA}, body)
    if expected != value.get("i40_receipt_hash72"):
        raise Pass218I40StateError("P218_I40_RECEIPT_HASH_MISMATCH")
    return value


class Pass218I40ManifestBoundCanonicalPersistenceStore:
    """Durable I40 binding receipt plus frozen-I7 canonical checkpoint store."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.binding_root = self.root / "bindings"
        self.state_path = self.root / "state.json"
        self.i7_store = Pass218DurableCanonicalStore(
            self.root / "durable-canonical-i7"
        )

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I40_STATE_SCHEMA:
            raise Pass218I40StateError("P218_I40_STATE_SCHEMA_INVALID")
        state_body = {
            key: item for key, item in state.items() if key != "state_root_hash72"
        }
        expected = hash72_digest({"domain": PASS218_I40_STATE_SCHEMA}, state_body)
        if expected != state.get("state_root_hash72"):
            raise Pass218I40StateError("P218_I40_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        binding_path = self.root / str(state.get("active_binding_path", ""))
        if not receipt_path.is_file() or not binding_path.is_file():
            raise Pass218I40StateError("P218_I40_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i40_receipt(_load_json(receipt_path))
        if receipt["i40_receipt_hash72"] != state.get("active_i40_receipt_hash72"):
            raise Pass218I40StateError("P218_I40_STATE_RECEIPT_MISMATCH")
        binding = _verify_i40_binding(_load_json(binding_path), receipt)
        if binding["manifest_bound_commit_persistence_hash72"] != state.get(
            "active_binding_hash72"
        ):
            raise Pass218I40StateError("P218_I40_STATE_BINDING_MISMATCH")
        return receipt

    def active_binding(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i40_binding(
            _load_json(self.root / str(state["active_binding_path"])), receipt
        )

    def commit(
        self,
        receipt: Mapping[str, Any],
        binding: Mapping[str, Any],
    ) -> dict[str, Any]:
        checked = _verify_i40_receipt(receipt)
        checked_binding = _verify_i40_binding(binding, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_binding() != checked_binding:
                raise Pass218I40StateError("P218_I40_ACTIVE_BINDING_CONFLICT")
            return existing

        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_path = self.receipt_root / (
            f"{ordinal:08d}-{checked['i40_receipt_hash72']}.json"
        )
        binding_path = self.binding_root / (
            f"{checked['manifest_bound_commit_persistence_hash72']}.json"
        )
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(binding_path, checked_binding)
        state_body = {
            "schema": PASS218_I40_STATE_SCHEMA,
            "version": PASS218_I40_VERSION,
            "status": PASS218_I40_COMPLETE_STATUS,
            "i39_receipt_hash72": checked["i39_receipt_hash72"],
            "active_i40_receipt_hash72": checked["i40_receipt_hash72"],
            "active_binding_hash72": checked[
                "manifest_bound_commit_persistence_hash72"
            ],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_binding_path": binding_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest(
                {"domain": PASS218_I40_STATE_SCHEMA}, state_body
            ),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I40StateError("P218_I40_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I40ManifestBoundCanonicalCommitPersistence:
    def __init__(
        self,
        *,
        lifecycle: Pass218I40LifecycleProtocol,
        i39_store: Pass218I40I39StoreProtocol,
        i38_store: Pass218I40I38StoreProtocol,
        i37_store: Pass218I40I37StoreProtocol,
        i36_store: Pass218I40I36StoreProtocol,
        state_root: str | os.PathLike[str],
        i39_status_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i39_store = i39_store
        self.i38_store = i38_store
        self.i37_store = i37_store
        self.i36_store = i36_store
        self.store = Pass218I40ManifestBoundCanonicalPersistenceStore(state_root)
        self.i39_status_provider = i39_status_provider
        self.i6_prepare_reconstruction_count = 0
        self.i6_commit_invocation_count = 0
        self.i7_checkpoint_invocation_count = 0
        self.i7_restore_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: Exception) -> str:
        text = str(exc).strip()
        return text.split(":", 1)[0] if text else exc.__class__.__name__

    def _active_lineage(self) -> tuple[
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ]:
        i39_receipt = self.i39_store.active_record()
        i39_prepare = self.i39_store.active_prepare()
        i38_receipt = self.i38_store.active_record()
        i38_envelope = self.i38_store.active_authorization_envelope()
        i37_receipt = self.i37_store.active_record()
        i37_proof = self.i37_store.active_proof()
        i36_receipt = self.i36_store.active_record()
        i36_stage = self.i36_store.active_stage()
        values = (
            i39_receipt,
            i39_prepare,
            i38_receipt,
            i38_envelope,
            i37_receipt,
            i37_proof,
            i36_receipt,
            i36_stage,
        )
        if not all(isinstance(value, Mapping) for value in values):
            raise Pass218I40BindingError(
                "P218_I40_COMPLETE_PREDECESSOR_LINEAGE_REQUIRED"
            )

        checked_i39 = _verify_i39_receipt(i39_receipt)
        checked_i39_prepare = _verify_i39_prepare(i39_prepare, checked_i39)
        if (
            checked_i39.get("schema") != PASS218_I39_RECEIPT_SCHEMA
            or checked_i39.get("status") != PASS218_I39_COMPLETE_STATUS
        ):
            raise Pass218I40BindingError("P218_I40_I39_COMPLETE_STATE_REQUIRED")
        i38, authorization, i4_stage, _ = _verify_predecessors(
            i38_receipt=i38_receipt,
            authorization_envelope=i38_envelope,
            i37_receipt=i37_receipt,
            i37_proof_envelope=i37_proof,
            i36_receipt=i36_receipt,
            i36_stage_envelope=i36_stage,
        )
        if checked_i39["i38_receipt_hash72"] != i38["i38_receipt_hash72"]:
            raise Pass218I40BindingError("P218_I40_I39_I38_RECEIPT_MISMATCH")
        if checked_i39["manifest_binding"] != i38["manifest_binding"]:
            raise Pass218I40BindingError("P218_I40_MANIFEST_LINEAGE_MISMATCH")
        if (
            checked_i39["manifest_bound_i4_stage_hash72"]
            != i36_receipt["manifest_bound_i4_stage_hash72"]
        ):
            raise Pass218I40BindingError("P218_I40_I39_I36_STAGE_MISMATCH")

        if self.i39_status_provider is not None:
            status = dict(self.i39_status_provider())
            if status.get("status") != PASS218_I39_COMPLETE_STATUS:
                raise Pass218I40BindingError("P218_I40_I39_STATUS_NOT_COMPLETE")
            if (
                status.get("active_i39_receipt_hash72")
                != checked_i39["i39_receipt_hash72"]
            ):
                raise Pass218I40BindingError(
                    "P218_I40_I39_STATUS_RECEIPT_MISMATCH"
                )
        return checked_i39, checked_i39_prepare, i38, authorization, i4_stage

    def _build_binding_and_receipt(
        self,
        *,
        i39: Mapping[str, Any],
        i39_prepare: Mapping[str, Any],
        commit_receipt: Mapping[str, Any],
        checkpoint: Mapping[str, Any],
        manifest: Mapping[str, Any],
        restore_record: Mapping[str, Any],
        prepare_reconstructed: bool,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        commit = _verify_i6_commit_receipt(
            commit_receipt,
            i39_receipt=i39,
            i39_prepare=i39_prepare,
        )
        target_record = checkpoint.get("canonical_target_record")
        if not isinstance(target_record, Mapping):
            raise Pass218I40I7Error("P218_I40_I7_TARGET_RECORD_MISSING")
        if target_record.get("canonical_root_hash72") != commit[
            "target_root_after_hash72"
        ]:
            raise Pass218I40I7Error(
                "P218_I40_I7_CANONICAL_ROOT_BINDING_MISMATCH"
            )
        if checkpoint.get("vm81_snapshot_sha256") != commit["projection_sha256"]:
            raise Pass218I40I7Error(
                "P218_I40_I7_VM81_PROJECTION_BINDING_MISMATCH"
            )
        if manifest.get("canonical_root_hash72") != commit[
            "target_root_after_hash72"
        ]:
            raise Pass218I40I7Error("P218_I40_I7_MANIFEST_ROOT_BINDING_MISMATCH")
        if restore_record.get("canonical_root_hash72") != commit[
            "target_root_after_hash72"
        ]:
            raise Pass218I40I7Error("P218_I40_I7_RESTORE_ROOT_BINDING_MISMATCH")
        if restore_record.get("checkpoint_sha256") != checkpoint.get(
            "checkpoint_sha256"
        ):
            raise Pass218I40I7Error("P218_I40_I7_RESTORE_CHECKPOINT_MISMATCH")

        binding_body = {
            "schema": PASS218_I40_BINDING_SCHEMA,
            "version": PASS218_I40_VERSION,
            "i39_receipt_hash72": i39["i39_receipt_hash72"],
            "i39_hash216": i39["i39_hash216"],
            "manifest_bound_i6_prepare_hash72": i39[
                "manifest_bound_i6_prepare_hash72"
            ],
            "manifest_binding": _copy(i39["manifest_binding"]),
            "i6_commit_receipt": _copy(commit),
            "i7_checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "i7_checkpoint_hash72": checkpoint["checkpoint_hash72"],
            "i7_checkpoint_hash216": checkpoint["checkpoint_hash216"],
            "i7_manifest_hash72": manifest["manifest_hash72"],
            "i7_restore_hash72": restore_record["restore_hash72"],
            "i6_prepare_reconstructed_exactly": prepare_reconstructed,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
        }
        binding_hash72 = hash72_digest(
            {"domain": PASS218_I40_BINDING_SCHEMA}, binding_body
        )
        binding = {
            **binding_body,
            "manifest_bound_commit_persistence_hash72": binding_hash72,
        }
        validation_hash72 = hash72_digest(
            {
                "domain": "HHS-P218-I40-MANIFEST-BOUND-CANONICAL-COMMIT-PERSISTENCE-VALIDATION-V1"
            },
            {
                "i39_receipt_hash72": i39["i39_receipt_hash72"],
                "i6_prepare_hash72": commit["prepare_hash72"],
                "i6_commit_receipt_hash72": commit["receipt_hash72"],
                "i6_target_root_after_hash72": commit[
                    "target_root_after_hash72"
                ],
                "i7_checkpoint_hash72": checkpoint["checkpoint_hash72"],
                "i7_manifest_hash72": manifest["manifest_hash72"],
                "i7_restore_hash72": restore_record["restore_hash72"],
                "manifest_bound_commit_persistence_hash72": binding_hash72,
                "canonical_commit_durable": True,
                "restart_restore_exact": True,
            },
        )
        body = {
            "schema": PASS218_I40_RECEIPT_SCHEMA,
            "version": PASS218_I40_VERSION,
            "scope": PASS218_I40_SCOPE,
            "status": PASS218_I40_COMPLETE_STATUS,
            "i39_receipt_hash72": i39["i39_receipt_hash72"],
            "i39_hash216": i39["i39_hash216"],
            "manifest_bound_i6_prepare_hash72": i39[
                "manifest_bound_i6_prepare_hash72"
            ],
            "manifest_binding": _copy(i39["manifest_binding"]),
            "i5_authorization_hash72": i39["i5_authorization_hash72"],
            "i4_entry_id_sha256": i39["i4_entry_id_sha256"],
            "i4_projection_sha256": i39["i4_projection_sha256"],
            "i6_boundary_version": PASS218_CANONICAL_COMMIT_VERSION,
            "i6_prepare_hash72": commit["prepare_hash72"],
            "i6_commit_hash72": commit["commit_hash72"],
            "i6_commit_receipt_hash72": commit["receipt_hash72"],
            "i6_commit_hash216": commit["commit_hash216"],
            "i6_target_root_before_hash72": commit[
                "target_root_before_hash72"
            ],
            "i6_target_root_after_hash72": commit["target_root_after_hash72"],
            "i6_admitted_entry_id_sha256": commit["admitted_entry_id_sha256"],
            "i6_vm81_commit_count": commit["vm81_commit_count"],
            "i6_vm81_snapshot_hash72": commit["vm81_snapshot_hash72"],
            "i6_vm81_state_hash72": commit["vm81_state_hash72"],
            "i7_persistence_version": PASS218_PERSISTENCE_VERSION,
            "i7_checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "i7_checkpoint_hash72": checkpoint["checkpoint_hash72"],
            "i7_checkpoint_validation_hash72": checkpoint["validation_hash72"],
            "i7_checkpoint_hash216": checkpoint["checkpoint_hash216"],
            "i7_manifest_hash72": manifest["manifest_hash72"],
            "i7_generation_sequence": checkpoint["generation_sequence"],
            "i7_vm81_snapshot_bytes": SNAPSHOT_BYTES,
            "i7_restore_hash72": restore_record["restore_hash72"],
            "i7_restore_state": restore_record["state"],
            "manifest_bound_commit_persistence_hash72": binding_hash72,
            "i40_validation_hash72": validation_hash72,
            "i39_prepare_bound": True,
            "manifest_binding_propagated": True,
            "i6_prepare_reconstructed_exactly": prepare_reconstructed,
            "pass218_i6_canonical_commit_invoked": True,
            "canonical_vector_store_mutation_invoked": True,
            "canonical_vm81_commit_invoked": True,
            "i6_authorization_consumed": True,
            "i6_atomic_swap": True,
            "pass218_i7_durable_persistence_invoked": True,
            "i7_checkpoint_durable": True,
            "i7_restore_verified": True,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
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
        receipt_hash72 = hash72_digest({"domain": PASS218_I40_RECEIPT_SCHEMA}, body)
        receipt = {
            **body,
            "i40_receipt_hash72": receipt_hash72,
            "i40_hash216": (
                i39["i39_receipt_hash72"]
                + checkpoint["checkpoint_hash72"]
                + receipt_hash72
            ),
            "i40_hash216_semantics": [
                "I39_MANIFEST_BOUND_NONCANONICAL_PREPARE_RECEIPT",
                "I7_DURABLE_CANONICAL_CHECKPOINT",
                "I40_MANIFEST_BOUND_COMMIT_PERSISTENCE_RECEIPT",
            ],
        }
        return binding, _verify_i40_receipt(receipt)

    def commit_and_persist(self) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i39, i39_prepare, _, authorization, i4_stage = self._active_lineage()
            existing = self.store.active_record()
            if existing is not None:
                if existing["i39_receipt_hash72"] != i39["i39_receipt_hash72"]:
                    raise Pass218I40StateError("P218_I40_ACTIVE_I39_CONFLICT")
                self.last_error_code = None
                return existing

            # If frozen I7 durability already exists but the final I40 binding
            # write was interrupted, recover directly from I7 without repeating
            # the canonical I6 mutation.
            if self.store.i7_store.manifest_path.exists():
                try:
                    restored = self.store.i7_store.restore()
                    self.i7_restore_invocation_count += 1
                except Pass218PersistenceError as exc:
                    raise Pass218I40I7Error(
                        "P218_I40_I7_RECOVERY_FAILED:" + str(exc)
                    ) from exc
                commit_receipt = restored.target.committed_receipt(
                    str(authorization["authorization_hash72"])
                )
                if commit_receipt is None:
                    raise Pass218I40I7Error(
                        "P218_I40_I7_EXPECTED_COMMIT_RECEIPT_MISSING"
                    )
                binding, receipt = self._build_binding_and_receipt(
                    i39=i39,
                    i39_prepare=i39_prepare,
                    commit_receipt=commit_receipt,
                    checkpoint=restored.checkpoint,
                    manifest=restored.manifest,
                    restore_record=restored.to_record(),
                    prepare_reconstructed=True,
                )
                persisted = self.store.commit(receipt, binding)
                self.last_error_code = None
                return persisted

            journal = DurableI38AuthorizationJournalView(authorization)
            boundary = Pass218CanonicalCommitBoundary()
            try:
                prepared = boundary.prepare(
                    authorization=authorization,
                    staged_candidate=i4_stage,
                    authorization_journal=journal,
                )
                self.i6_prepare_reconstruction_count += 1
            except Pass218CanonicalCommitError as exc:
                raise Pass218I40I6Error(
                    "P218_I40_I6_PREPARE_RECONSTRUCTION_FAILED:" + str(exc)
                ) from exc
            if prepared.to_record() != i39_prepare.get("i6_prepare_record"):
                raise Pass218I40I6Error(
                    "P218_I40_I6_PREPARE_RECONSTRUCTION_MISMATCH"
                )

            try:
                commit_receipt = boundary.commit(
                    prepared,
                    authorization_journal=journal,
                )
                self.i6_commit_invocation_count += 1
            except Pass218CanonicalCommitError as exc:
                raise Pass218I40I6Error(
                    "P218_I40_I6_CANONICAL_COMMIT_FAILED:" + str(exc)
                ) from exc
            commit_receipt = _verify_i6_commit_receipt(
                commit_receipt,
                i39_receipt=i39,
                i39_prepare=i39_prepare,
            )

            try:
                checkpoint_result = self.store.i7_store.checkpoint(boundary.target)
                self.i7_checkpoint_invocation_count += 1
                restored = self.store.i7_store.restore()
                self.i7_restore_invocation_count += 1
            except Pass218PersistenceError as exc:
                raise Pass218I40I7Error(
                    "P218_I40_I7_PERSISTENCE_FAILED:" + str(exc)
                ) from exc
            if restored.target.root_hash72() != boundary.target.root_hash72():
                raise Pass218I40I7Error("P218_I40_I7_RESTORED_ROOT_MISMATCH")
            if restored.target.snapshot_bytes() != boundary.target.snapshot_bytes():
                raise Pass218I40I7Error(
                    "P218_I40_I7_RESTORED_VM81_IMAGE_MISMATCH"
                )
            restored_receipt = restored.target.committed_receipt(
                str(authorization["authorization_hash72"])
            )
            if restored_receipt != commit_receipt:
                raise Pass218I40I7Error(
                    "P218_I40_I7_RESTORED_COMMIT_RECEIPT_MISMATCH"
                )

            binding, receipt = self._build_binding_and_receipt(
                i39=i39,
                i39_prepare=i39_prepare,
                commit_receipt=commit_receipt,
                checkpoint=checkpoint_result["checkpoint"],
                manifest=checkpoint_result["manifest"],
                restore_record=restored.to_record(),
                prepare_reconstructed=True,
            )
            persisted = self.store.commit(receipt, binding)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        predecessor_ready = False
        active_i39_receipt_hash72: str | None = None
        try:
            i39, _, _, _, _ = self._active_lineage()
            predecessor_ready = True
            active_i39_receipt_hash72 = str(i39["i39_receipt_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I40_STATUS_SCHEMA,
            "version": PASS218_I40_VERSION,
            "status": (
                PASS218_I40_COMPLETE_STATUS
                if active is not None
                else PASS218_I40_PENDING_STATUS
            ),
            "predecessor_state_ready": predecessor_ready,
            "active_i39_receipt_hash72": active_i39_receipt_hash72,
            "active_i40_receipt_hash72": (
                None if active is None else active["i40_receipt_hash72"]
            ),
            "canonical_root_hash72": (
                None if active is None else active["i6_target_root_after_hash72"]
            ),
            "i7_checkpoint_sha256": (
                None if active is None else active["i7_checkpoint_sha256"]
            ),
            "i6_prepare_reconstruction_count_current_process": self.i6_prepare_reconstruction_count,
            "i6_commit_invocation_count_current_process": self.i6_commit_invocation_count,
            "i7_checkpoint_invocation_count_current_process": self.i7_checkpoint_invocation_count,
            "i7_restore_invocation_count_current_process": self.i7_restore_invocation_count,
            "canonical_vector_store_mutation_invoked": active is not None,
            "canonical_vm81_commit_invoked": active is not None,
            "pass218_i7_durable_persistence_invoked": active is not None,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I40_BINDING_SCHEMA",
    "PASS218_I40_COMPLETE_STATUS",
    "PASS218_I40_PENDING_STATUS",
    "PASS218_I40_RECEIPT_SCHEMA",
    "PASS218_I40_SCOPE",
    "PASS218_I40_STATE_SCHEMA",
    "PASS218_I40_STATUS_SCHEMA",
    "PASS218_I40_VERSION",
    "Pass218I40BindingError",
    "Pass218I40CanonicalPersistenceError",
    "Pass218I40I6Error",
    "Pass218I40I7Error",
    "Pass218I40ManifestBoundCanonicalCommitPersistence",
    "Pass218I40ManifestBoundCanonicalPersistenceStore",
    "Pass218I40StateError",
]
