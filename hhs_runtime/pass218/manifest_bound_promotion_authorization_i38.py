"""Pass 218 Iteration 38 manifest-bound frozen-I5 authority/authorization ingress.

I38 begins only from the exact durable I37 promotability receipt and proof
envelope. It derives the grantor from the already-propagated curriculum
authority root, creates the frozen I5 PromotionAuthorityGrant, and invokes the
frozen I5 PromotionAuthorizationJournal exactly once for the exact candidate.

The result is AUTHORIZED_PENDING_CANONICAL_COMMIT. I38 does not invoke I6,
mutate the Pass-217 vector store, commit VM81 state, perform canonical learning,
promote truth, mint action authority, advance curriculum state, retain verbatim
source, or create authoritative floating-point state.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    PASS218_I37_COMPLETE_STATUS,
    PASS218_I37_PROOF_SCHEMA,
    PASS218_I37_RECEIPT_SCHEMA,
)
from hhs_runtime.pass218.promotion import (
    PASS218_PROMOTION_MEMBRANE_VERSION,
    PROMOTION_SCOPE,
    Pass218PromotionError,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
)

PASS218_I38_VERSION = "HHS-P218-I38-MANIFEST-BOUND-PROMOTION-AUTHORIZATION-V1"
PASS218_I38_SCOPE = "PASS218_MANIFEST_BOUND_PROMOTION_AUTHORITY_AUTHORIZATION_INGRESS"
PASS218_I38_RECEIPT_SCHEMA = "HHS-P218-I38-MANIFEST-BOUND-PROMOTION-AUTHORIZATION-RECEIPT-V1"
PASS218_I38_ENVELOPE_SCHEMA = "HHS-P218-I38-MANIFEST-BOUND-PROMOTION-AUTHORIZATION-V1"
PASS218_I38_STATE_SCHEMA = "HHS-P218-I38-MANIFEST-BOUND-PROMOTION-AUTHORIZATION-STATE-V1"
PASS218_I38_STATUS_SCHEMA = "HHS-P218-I38-MANIFEST-BOUND-PROMOTION-AUTHORIZATION-STATUS-V1"
PASS218_I38_COMPLETE_STATUS = "MANIFEST_BOUND_PROMOTION_AUTHORIZATION_INGRESS_COMPLETE"
PASS218_I38_PENDING_STATUS = "MANIFEST_BOUND_PROMOTION_AUTHORIZATION_PENDING"


class Pass218I38AuthorizationIngressError(RuntimeError):
    pass


class Pass218I38BindingError(Pass218I38AuthorizationIngressError):
    pass


class Pass218I38StateError(Pass218I38AuthorizationIngressError):
    pass


class Pass218I38I5Error(Pass218I38AuthorizationIngressError):
    pass


class Pass218I38LifecycleProtocol(Protocol):
    def require_ingestion_ready(self) -> None: ...


class Pass218I38I37StoreProtocol(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


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
        raise Pass218I38StateError("P218_I38_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I38StateError("P218_I38_STATE_OBJECT_REQUIRED")
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


def _verify_i37_state(
    receipt: Mapping[str, Any],
    proof_envelope: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    checked = _copy(dict(receipt))
    envelope = _copy(dict(proof_envelope))
    if checked.get("schema") != PASS218_I37_RECEIPT_SCHEMA:
        raise Pass218I38BindingError("P218_I38_I37_RECEIPT_SCHEMA_INVALID")
    if checked.get("status") != PASS218_I37_COMPLETE_STATUS:
        raise Pass218I38BindingError("P218_I38_I37_NOT_COMPLETE")
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
    if any(checked.get(field) is not True for field in required_true):
        raise Pass218I38BindingError("P218_I38_I37_PROOF_INCOMPLETE")
    required_false = (
        "pass218_i5_promotion_invoked",
        "i5_explicit_authority_grant_present",
        "i5_promotion_authorization_invoked",
        "canonical_mutation_permitted",
        "pass218_i6_canonical_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )
    if any(checked.get(field) is not False for field in required_false):
        raise Pass218I38BindingError("P218_I38_I37_AUTHORITY_DRIFT")
    for field in (
        "i37_receipt_hash72",
        "manifest_bound_i5_proof_hash72",
        "i5_proof_hash72",
        "i5_validation_hash72",
        "i36_receipt_hash72",
    ):
        if not validate_hash72(str(checked.get(field, ""))):
            raise Pass218I38BindingError("P218_I38_I37_HASH72_INVALID:" + field)
    for field in ("i37_hash216", "i5_proof_hash216"):
        if not _valid_hash216(checked.get(field)):
            raise Pass218I38BindingError("P218_I38_I37_HASH216_INVALID:" + field)
    for field in ("i4_entry_id_sha256", "i4_projection_sha256"):
        if not _valid_sha256(checked.get(field)):
            raise Pass218I38BindingError("P218_I38_I37_SHA256_INVALID:" + field)
    manifest = checked.get("manifest_binding")
    if not isinstance(manifest, Mapping):
        raise Pass218I38BindingError("P218_I38_MANIFEST_BINDING_REQUIRED")
    authority_root = manifest.get("authority_root_hash72")
    if not validate_hash72(str(authority_root or "")):
        raise Pass218I38BindingError("P218_I38_AUTHORITY_ROOT_INVALID")
    ordinal = manifest.get("curriculum_position")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 0:
        raise Pass218I38BindingError("P218_I38_CURRICULUM_POSITION_INVALID")

    if envelope.get("schema") != PASS218_I37_PROOF_SCHEMA:
        raise Pass218I38BindingError("P218_I38_I37_PROOF_ENVELOPE_SCHEMA_INVALID")
    body = {
        key: item
        for key, item in envelope.items()
        if key != "manifest_bound_i5_proof_hash72"
    }
    expected_envelope = hash72_digest({"domain": PASS218_I37_PROOF_SCHEMA}, body)
    if expected_envelope != envelope.get("manifest_bound_i5_proof_hash72"):
        raise Pass218I38BindingError("P218_I38_I37_PROOF_ENVELOPE_HASH_MISMATCH")
    if expected_envelope != checked.get("manifest_bound_i5_proof_hash72"):
        raise Pass218I38BindingError("P218_I38_I37_PROOF_RECEIPT_MISMATCH")
    if envelope.get("i36_receipt_hash72") != checked.get("i36_receipt_hash72"):
        raise Pass218I38BindingError("P218_I38_I37_LINEAGE_MISMATCH")
    if envelope.get("manifest_binding") != manifest:
        raise Pass218I38BindingError("P218_I38_I37_MANIFEST_BINDING_MISMATCH")
    proof = envelope.get("i5_promotability_proof")
    if not isinstance(proof, Mapping):
        raise Pass218I38BindingError("P218_I38_I5_PROOF_REQUIRED")
    proof_record = _copy(dict(proof))
    try:
        PromotionProofMembrane.validate_proof_record(proof_record)
    except Pass218PromotionError as exc:
        raise Pass218I38I5Error("P218_I38_I5_PROOF_INVALID:" + str(exc)) from exc
    if proof_record.get("proof_hash72") != checked.get("i5_proof_hash72"):
        raise Pass218I38BindingError("P218_I38_I5_PROOF_HASH_MISMATCH")
    if proof_record.get("entry_id_sha256") != checked.get("i4_entry_id_sha256"):
        raise Pass218I38BindingError("P218_I38_I5_ENTRY_ID_MISMATCH")
    if proof_record.get("projection_sha256") != checked.get("i4_projection_sha256"):
        raise Pass218I38BindingError("P218_I38_I5_PROJECTION_MISMATCH")
    return checked, envelope, proof_record


def _verify_i38_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    value = _copy(dict(receipt))
    if value.get("schema") != PASS218_I38_RECEIPT_SCHEMA:
        raise Pass218I38StateError("P218_I38_RECEIPT_SCHEMA_INVALID")
    if value.get("status") != PASS218_I38_COMPLETE_STATUS:
        raise Pass218I38StateError("P218_I38_RECEIPT_STATUS_INVALID")
    required_true = (
        "i37_receipt_bound",
        "manifest_binding_propagated",
        "i5_promotability_proof_bound",
        "pass218_i5_promotion_invoked",
        "i5_explicit_authority_grant_present",
        "i5_promotion_authorization_invoked",
        "i5_authorized_pending_canonical_commit",
        "canonical_mutation_permitted",
    )
    if any(value.get(field) is not True for field in required_true):
        raise Pass218I38StateError("P218_I38_RECEIPT_AUTHORIZATION_INCOMPLETE")
    required_false = (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
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
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    )
    if any(value.get(field) is not False for field in required_false):
        raise Pass218I38StateError("P218_I38_RECEIPT_CANONICAL_DRIFT")
    for field in (
        "i37_receipt_hash72",
        "manifest_bound_i5_proof_hash72",
        "i5_proof_hash72",
        "i5_grantor_authority_hash72",
        "i5_grant_hash72",
        "i5_grant_validation_hash72",
        "i5_authorization_hash72",
        "i5_authorization_validation_hash72",
        "manifest_bound_i5_authorization_hash72",
        "i38_validation_hash72",
        "i38_receipt_hash72",
    ):
        if not validate_hash72(str(value.get(field, ""))):
            raise Pass218I38StateError("P218_I38_RECEIPT_HASH72_INVALID:" + field)
    for field in (
        "i37_hash216",
        "i5_proof_hash216",
        "i5_grant_hash216",
        "i5_authorization_hash216",
        "i38_hash216",
    ):
        if not _valid_hash216(value.get(field)):
            raise Pass218I38StateError("P218_I38_RECEIPT_HASH216_INVALID:" + field)
    for field in ("i4_entry_id_sha256", "i4_projection_sha256"):
        if not _valid_sha256(value.get(field)):
            raise Pass218I38StateError("P218_I38_RECEIPT_SHA256_INVALID:" + field)
    if not isinstance(value.get("manifest_binding"), Mapping):
        raise Pass218I38StateError("P218_I38_RECEIPT_MANIFEST_BINDING_REQUIRED")
    body = {
        key: item
        for key, item in value.items()
        if key not in {"i38_receipt_hash72", "i38_hash216", "i38_hash216_semantics"}
    }
    expected = hash72_digest({"domain": PASS218_I38_RECEIPT_SCHEMA}, body)
    if expected != value.get("i38_receipt_hash72"):
        raise Pass218I38StateError("P218_I38_RECEIPT_HASH_MISMATCH")
    expected_hash216 = (
        str(value["i37_receipt_hash72"])
        + str(value["i5_authorization_hash72"])
        + str(value["i38_receipt_hash72"])
    )
    if expected_hash216 != value.get("i38_hash216"):
        raise Pass218I38StateError("P218_I38_HASH216_ORDER_INVALID")
    return value


def _verify_i38_envelope(
    envelope: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    value = _copy(dict(envelope))
    if value.get("schema") != PASS218_I38_ENVELOPE_SCHEMA:
        raise Pass218I38StateError("P218_I38_ENVELOPE_SCHEMA_INVALID")
    body = {
        key: item
        for key, item in value.items()
        if key != "manifest_bound_i5_authorization_hash72"
    }
    expected = hash72_digest({"domain": PASS218_I38_ENVELOPE_SCHEMA}, body)
    if expected != value.get("manifest_bound_i5_authorization_hash72"):
        raise Pass218I38StateError("P218_I38_ENVELOPE_HASH_MISMATCH")
    if expected != receipt.get("manifest_bound_i5_authorization_hash72"):
        raise Pass218I38StateError("P218_I38_ENVELOPE_RECEIPT_MISMATCH")
    if value.get("i37_receipt_hash72") != receipt.get("i37_receipt_hash72"):
        raise Pass218I38StateError("P218_I38_ENVELOPE_I37_MISMATCH")
    grant = value.get("i5_authority_grant")
    authorization = value.get("i5_promotion_authorization")
    if not isinstance(grant, Mapping) or not isinstance(authorization, Mapping):
        raise Pass218I38StateError("P218_I38_ENVELOPE_AUTHORIZATION_RECORDS_REQUIRED")
    if grant.get("grant_hash72") != receipt.get("i5_grant_hash72"):
        raise Pass218I38StateError("P218_I38_ENVELOPE_GRANT_MISMATCH")
    if authorization.get("authorization_hash72") != receipt.get("i5_authorization_hash72"):
        raise Pass218I38StateError("P218_I38_ENVELOPE_AUTHORIZATION_MISMATCH")
    return value


class Pass218I38ManifestBoundPromotionAuthorizationStore:
    """Durable nonverbatim I38 grant, authorization, and binding receipt."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_root = self.root / "receipts"
        self.authorization_root = self.root / "authorizations"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _load_json(self.state_path)
        if state.get("schema") != PASS218_I38_STATE_SCHEMA:
            raise Pass218I38StateError("P218_I38_STATE_SCHEMA_INVALID")
        body = {key: item for key, item in state.items() if key != "state_root_hash72"}
        if hash72_digest({"domain": PASS218_I38_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I38StateError("P218_I38_STATE_ROOT_MISMATCH")
        receipt_path = self.root / str(state.get("active_receipt_path", ""))
        authorization_path = self.root / str(state.get("active_authorization_path", ""))
        if not receipt_path.is_file() or not authorization_path.is_file():
            raise Pass218I38StateError("P218_I38_ACTIVE_ARTIFACT_MISSING")
        receipt = _verify_i38_receipt(_load_json(receipt_path))
        if receipt["i38_receipt_hash72"] != state.get("active_i38_receipt_hash72"):
            raise Pass218I38StateError("P218_I38_STATE_RECEIPT_MISMATCH")
        envelope = _verify_i38_envelope(_load_json(authorization_path), receipt)
        if envelope["manifest_bound_i5_authorization_hash72"] != state.get("active_authorization_hash72"):
            raise Pass218I38StateError("P218_I38_STATE_AUTHORIZATION_MISMATCH")
        return receipt

    def active_authorization_envelope(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        if receipt is None:
            return None
        state = _load_json(self.state_path)
        return _verify_i38_envelope(
            _load_json(self.root / str(state["active_authorization_path"])),
            receipt,
        )

    def active_authorization(self) -> dict[str, Any] | None:
        envelope = self.active_authorization_envelope()
        return None if envelope is None else _copy(envelope["i5_promotion_authorization"])

    def active_grant(self) -> dict[str, Any] | None:
        envelope = self.active_authorization_envelope()
        return None if envelope is None else _copy(envelope["i5_authority_grant"])

    def commit(
        self,
        receipt: Mapping[str, Any],
        authorization_envelope: Mapping[str, Any],
    ) -> dict[str, Any]:
        checked = _verify_i38_receipt(receipt)
        envelope = _verify_i38_envelope(authorization_envelope, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked:
                raise Pass218I38StateError("P218_I38_ACTIVE_BINDING_CONFLICT")
            if self.active_authorization_envelope() != envelope:
                raise Pass218I38StateError("P218_I38_ACTIVE_AUTHORIZATION_CONFLICT")
            return existing
        ordinal = int(checked["manifest_binding"]["curriculum_position"])
        receipt_path = self.receipt_root / f"{ordinal:08d}-{checked['i38_receipt_hash72']}.json"
        authorization_path = self.authorization_root / f"{checked['manifest_bound_i5_authorization_hash72']}.json"
        _atomic_write_json(receipt_path, checked)
        _atomic_write_json(authorization_path, envelope)
        state_body = {
            "schema": PASS218_I38_STATE_SCHEMA,
            "version": PASS218_I38_VERSION,
            "status": PASS218_I38_COMPLETE_STATUS,
            "i37_receipt_hash72": checked["i37_receipt_hash72"],
            "active_i38_receipt_hash72": checked["i38_receipt_hash72"],
            "active_authorization_hash72": envelope["manifest_bound_i5_authorization_hash72"],
            "active_receipt_path": receipt_path.relative_to(self.root).as_posix(),
            "active_authorization_path": authorization_path.relative_to(self.root).as_posix(),
        }
        state = {
            **state_body,
            "state_root_hash72": hash72_digest({"domain": PASS218_I38_STATE_SCHEMA}, state_body),
        }
        _atomic_write_json(self.state_path, state)
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I38StateError("P218_I38_STATE_PERSIST_MISMATCH")
        return checked


class Pass218I38ManifestBoundPromotionAuthorization:
    """Bind exact frozen I37 proof to frozen I5 grant+authorization only."""

    def __init__(
        self,
        *,
        lifecycle: Pass218I38LifecycleProtocol,
        i37_store: Pass218I38I37StoreProtocol,
        state_root: str | os.PathLike[str],
        i37_status_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.i37_store = i37_store
        self.i37_status_provider = i37_status_provider
        self.store = Pass218I38ManifestBoundPromotionAuthorizationStore(state_root)
        self.i5_grant_invocation_count = 0
        self.i5_authorize_invocation_count = 0
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def _active_i37(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        receipt = self.i37_store.active_record()
        proof = self.i37_store.active_proof()
        if receipt is None or proof is None:
            raise Pass218I38BindingError("P218_I38_I37_COMPLETE_STATE_REQUIRED")
        checked, envelope, proof_record = _verify_i37_state(receipt, proof)
        if self.i37_status_provider is not None:
            status = dict(self.i37_status_provider())
            if status.get("status") != PASS218_I37_COMPLETE_STATUS:
                raise Pass218I38BindingError("P218_I38_I37_STATUS_NOT_COMPLETE")
            if status.get("active_i37_receipt_hash72") != checked["i37_receipt_hash72"]:
                raise Pass218I38BindingError("P218_I38_I37_STATUS_RECEIPT_MISMATCH")
            if status.get("manifest_bound_i5_proof_hash72") != checked["manifest_bound_i5_proof_hash72"]:
                raise Pass218I38BindingError("P218_I38_I37_STATUS_PROOF_MISMATCH")
        return checked, envelope, proof_record

    def authorize(self) -> dict[str, Any]:
        self.lifecycle.require_ingestion_ready()
        try:
            i37, _, proof = self._active_i37()
            existing = self.store.active_record()
            if existing is not None:
                if (
                    existing["i37_receipt_hash72"] != i37["i37_receipt_hash72"]
                    or existing["manifest_bound_i5_proof_hash72"] != i37["manifest_bound_i5_proof_hash72"]
                    or existing["manifest_binding"] != i37["manifest_binding"]
                ):
                    raise Pass218I38StateError("P218_I38_ACTIVE_BINDING_CONFLICT")
                self.last_error_code = None
                return existing

            authority_root = str(i37["manifest_binding"]["authority_root_hash72"])
            grant_sequence = int(i37["manifest_binding"]["curriculum_position"])
            try:
                grant = PromotionAuthorityGrant.bind(
                    proof,
                    grantor_authority_hash72=authority_root,
                    grant_sequence=grant_sequence,
                    target_scope=PROMOTION_SCOPE,
                )
                self.i5_grant_invocation_count += 1
                journal = PromotionAuthorizationJournal()
                authorization = journal.authorize(proof, grant)
                self.i5_authorize_invocation_count += 1
            except Pass218PromotionError as exc:
                raise Pass218I38I5Error("P218_I38_I5_AUTHORIZATION_FAILED:" + str(exc)) from exc

            grant_record = grant.to_record()
            if authorization.get("state") != "AUTHORIZED_PENDING_CANONICAL_COMMIT":
                raise Pass218I38I5Error("P218_I38_I5_AUTHORIZATION_STATE_INVALID")
            if authorization.get("canonical_mutation_permitted") is not True:
                raise Pass218I38I5Error("P218_I38_I5_MUTATION_PERMISSION_MISSING")
            if any(
                authorization.get(field) is not False
                for field in (
                    "canonical_vector_store_mutation_invoked",
                    "canonical_vm81_commit_invoked",
                    "canonical_learning_commit_invoked",
                    "truth_promotion",
                    "action_authority_minted",
                    "verbatim_source_retained",
                )
            ):
                raise Pass218I38I5Error("P218_I38_I5_AUTHORIZATION_CANONICAL_DRIFT")

            envelope_body = {
                "schema": PASS218_I38_ENVELOPE_SCHEMA,
                "version": PASS218_I38_VERSION,
                "i37_receipt_hash72": i37["i37_receipt_hash72"],
                "i37_hash216": i37["i37_hash216"],
                "manifest_bound_i5_proof_hash72": i37["manifest_bound_i5_proof_hash72"],
                "manifest_binding": _copy(i37["manifest_binding"]),
                "i5_promotion_membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
                "i5_authority_grant": _copy(grant_record),
                "i5_promotion_authorization": _copy(authorization),
                "grantor_derived_from_manifest_authority_root": True,
                "grant_sequence_derived_from_curriculum_position": True,
                "canonical_commit_invoked": False,
                "verbatim_source_retained": False,
            }
            manifest_bound_authorization_hash72 = hash72_digest(
                {"domain": PASS218_I38_ENVELOPE_SCHEMA}, envelope_body
            )
            authorization_envelope = {
                **envelope_body,
                "manifest_bound_i5_authorization_hash72": manifest_bound_authorization_hash72,
            }
            validation_hash72 = hash72_digest(
                {"domain": "HHS-P218-I38-MANIFEST-BOUND-AUTHORIZATION-VALIDATION-V1"},
                {
                    "i37_receipt_hash72": i37["i37_receipt_hash72"],
                    "i5_proof_hash72": i37["i5_proof_hash72"],
                    "i5_grant_hash72": grant_record["grant_hash72"],
                    "i5_authorization_hash72": authorization["authorization_hash72"],
                    "manifest_bound_i5_authorization_hash72": manifest_bound_authorization_hash72,
                    "grantor_exact": True,
                    "candidate_exact": True,
                    "scope_exact": True,
                    "canonical_mutation_permitted": True,
                    "canonical_mutation_invoked": False,
                },
            )
            body = {
                "schema": PASS218_I38_RECEIPT_SCHEMA,
                "version": PASS218_I38_VERSION,
                "scope": PASS218_I38_SCOPE,
                "status": PASS218_I38_COMPLETE_STATUS,
                "i37_receipt_hash72": i37["i37_receipt_hash72"],
                "i37_hash216": i37["i37_hash216"],
                "manifest_bound_i5_proof_hash72": i37["manifest_bound_i5_proof_hash72"],
                "i5_proof_hash72": i37["i5_proof_hash72"],
                "i5_proof_hash216": i37["i5_proof_hash216"],
                "manifest_binding": _copy(i37["manifest_binding"]),
                "i4_entry_id_sha256": i37["i4_entry_id_sha256"],
                "i4_projection_sha256": i37["i4_projection_sha256"],
                "i5_promotion_membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
                "i5_grantor_authority_hash72": grant_record["grantor_authority_hash72"],
                "i5_grant_sequence": grant_record["grant_sequence"],
                "i5_target_scope": grant_record["target_scope"],
                "i5_grant_hash72": grant_record["grant_hash72"],
                "i5_grant_validation_hash72": grant_record["validation_hash72"],
                "i5_grant_hash216": grant_record["grant_hash216"],
                "i5_authorization_hash72": authorization["authorization_hash72"],
                "i5_authorization_validation_hash72": authorization["validation_hash72"],
                "i5_authorization_hash216": authorization["authorization_hash216"],
                "manifest_bound_i5_authorization_hash72": manifest_bound_authorization_hash72,
                "i38_validation_hash72": validation_hash72,
                "i37_receipt_bound": True,
                "manifest_binding_propagated": True,
                "i5_promotability_proof_bound": True,
                "pass218_i5_promotion_invoked": True,
                "i5_explicit_authority_grant_present": True,
                "i5_promotion_authorization_invoked": True,
                "i5_authorized_pending_canonical_commit": True,
                "canonical_mutation_permitted": True,
                "source_payload_persisted": False,
                "verbatim_corpus_source_retained": False,
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
                "canonical_vector_store_mutation_invoked": False,
                "canonical_vm81_commit_invoked": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "authoritative_float_weights_created": False,
            }
            receipt_hash72 = hash72_digest({"domain": PASS218_I38_RECEIPT_SCHEMA}, body)
            receipt = {
                **body,
                "i38_receipt_hash72": receipt_hash72,
                "i38_hash216": (
                    i37["i37_receipt_hash72"]
                    + authorization["authorization_hash72"]
                    + receipt_hash72
                ),
                "i38_hash216_semantics": [
                    "I37_MANIFEST_BOUND_PROMOTABILITY_PROOF_RECEIPT",
                    "I5_EXPLICIT_PROMOTION_AUTHORIZATION",
                    "I38_MANIFEST_BOUND_AUTHORIZATION_BINDING_RECEIPT",
                ],
            }
            persisted = self.store.commit(receipt, authorization_envelope)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            raise

    def active_authorization(self) -> dict[str, Any] | None:
        return self.store.active_authorization()

    def active_grant(self) -> dict[str, Any] | None:
        return self.store.active_grant()

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i37_ready = False
        active_i37_receipt_hash72: str | None = None
        active_i37_proof_hash72: str | None = None
        try:
            i37, _, _ = self._active_i37()
            i37_ready = True
            active_i37_receipt_hash72 = str(i37["i37_receipt_hash72"])
            active_i37_proof_hash72 = str(i37["manifest_bound_i5_proof_hash72"])
        except Exception:
            pass
        return {
            "schema": PASS218_I38_STATUS_SCHEMA,
            "version": PASS218_I38_VERSION,
            "status": PASS218_I38_COMPLETE_STATUS if active is not None else PASS218_I38_PENDING_STATUS,
            "i37_complete_state_ready": i37_ready,
            "active_i37_receipt_hash72": active_i37_receipt_hash72,
            "active_i37_proof_hash72": active_i37_proof_hash72,
            "active_i38_receipt_hash72": None if active is None else active["i38_receipt_hash72"],
            "manifest_bound_i5_authorization_hash72": None if active is None else active["manifest_bound_i5_authorization_hash72"],
            "i5_authorization_hash72": None if active is None else active["i5_authorization_hash72"],
            "i5_grant_invocation_count_current_process": self.i5_grant_invocation_count,
            "i5_authorize_invocation_count_current_process": self.i5_authorize_invocation_count,
            "pass218_i5_promotion_invoked": active is not None or self.i5_grant_invocation_count > 0,
            "i5_explicit_authority_grant_present": active is not None,
            "i5_promotion_authorization_invoked": active is not None or self.i5_authorize_invocation_count > 0,
            "i5_authorized_pending_canonical_commit": active is not None,
            "canonical_mutation_permitted": active is not None,
            "source_payload_persisted": False,
            "verbatim_corpus_source_retained": False,
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
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
            "last_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I38_COMPLETE_STATUS",
    "PASS218_I38_ENVELOPE_SCHEMA",
    "PASS218_I38_PENDING_STATUS",
    "PASS218_I38_RECEIPT_SCHEMA",
    "PASS218_I38_SCOPE",
    "PASS218_I38_STATE_SCHEMA",
    "PASS218_I38_STATUS_SCHEMA",
    "PASS218_I38_VERSION",
    "Pass218I38AuthorizationIngressError",
    "Pass218I38BindingError",
    "Pass218I38I5Error",
    "Pass218I38ManifestBoundPromotionAuthorization",
    "Pass218I38ManifestBoundPromotionAuthorizationStore",
    "Pass218I38StateError",
]
