"""Replayable candidate source/Witness association for the existing Pass219 UQCEL.

This is an exact-byte, exact-integer SHA-256 *association*, not a signature,
Hash216 transition, parent-reference, credential, receipt mint or VM81 commit.
The inherited native UQCEL validator is still required for each replay.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping, Any

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_uqcel_witness_prevalidation_v1 import (
    UQCELWitnessPrevalidationError,
    prevalidate_staged_uqcel_witness,
)

SCHEMA = "HHS_ADMIN_SQL_UQCEL_SOURCE_ASSOCIATION_V1"
DOMAIN = "HHS-P220-ADMIN-SQL-UQCEL-CANDIDATE-ASSOCIATION-V1"


class UQCELSourceAssociationError(ValueError):
    pass


def _source_identity(staging: AdminStreamStaging, upload_id: str, owner: str) -> tuple[str, int]:
    record = staging.status(upload_id, owner)
    if record["state"] != "STAGED":
        raise UQCELSourceAssociationError("ASSOCIATION_SOURCE_NOT_STAGED")
    source = staging.read_staged(upload_id, owner)
    with source.open("rb") as stream:
        raw = stream.read(649)
    # Only preexisting exact VM81 frames reach this handoff. The ordinary
    # source upload and streaming egress are NOT limited to 648 bytes.
    if len(raw) != 648 or record["received_bytes"] != 648:
        raise UQCELSourceAssociationError("ASSOCIATION_TYPED_VM81_FRAME_REQUIRED")
    actual = sha256(raw).hexdigest()
    if actual != record["source_sha256"]:
        raise UQCELSourceAssociationError("ASSOCIATION_SOURCE_DIGEST_DRIFT")
    return actual, len(raw)


def _payload(upload_id: str, source_sha256: str, witness: Mapping[str, object]) -> bytes:
    # JSON canonicalization is only an identity representation; the native ABI
    # remains the mathematical authority. No floats may enter the payload.
    encoded = {
        "domain": DOMAIN,
        "upload_id": upload_id,
        "source_sha256": source_sha256,
        "witness": dict(witness),
    }
    return json.dumps(encoded, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def build_candidate_source_witness_association(
    staging: AdminStreamStaging,
    upload_id: str,
    authenticated_owner: str,
    *,
    witness: Mapping[str, object],
    native_validator=None,
) -> dict[str, Any]:
    """Build an untrusted association, only after real native math validation."""
    result = prevalidate_staged_uqcel_witness(
        staging, upload_id, authenticated_owner, witness=witness,
        native_validator=native_validator,
    )
    if result["uqcel_native_validation_succeeded"] is not True:
        raise UQCELSourceAssociationError("NATIVE_UQCEL_MATHEMATICAL_VALIDATION_REQUIRED")
    source_sha256, size = _source_identity(staging, upload_id, authenticated_owner)
    if source_sha256 != result["source_sha256"]:
        raise UQCELSourceAssociationError("SOURCE_CHANGED_AFTER_NATIVE_VALIDATION")
    witness_copy = {key: witness[key] for key in sorted(witness)}
    binding_sha256 = sha256(_payload(upload_id, source_sha256, witness_copy)).hexdigest()
    return {
        "schema": SCHEMA,
        "upload_id": upload_id,
        "source_sha256": source_sha256,
        "source_bytes": size,
        "witness": witness_copy,
        "candidate_association_sha256": binding_sha256,
        "native_uqcel_validated": True,
        "association_replay_required": True,
        "authenticated_owner_required_on_replay": True,
        "source_to_witness_candidate_association": True,
        "source_to_witness_authorized_provenance": False,
        "authorized_parent_hash216_bound": False,
        "signed_vm81_admission_performed": False,
        "canonical_hash216_admitted": False,
        "canonical_persistence_performed": False,
    }


def replay_candidate_source_witness_association(
    staging: AdminStreamStaging,
    authenticated_owner: str,
    association: Mapping[str, object],
    *,
    native_validator=None,
) -> dict[str, Any]:
    """Check exact association shape, owner, source content and native math again."""
    keys = {
        "schema", "upload_id", "source_sha256", "source_bytes", "witness",
        "candidate_association_sha256", "native_uqcel_validated",
        "association_replay_required", "authenticated_owner_required_on_replay",
        "source_to_witness_candidate_association",
        "source_to_witness_authorized_provenance", "authorized_parent_hash216_bound",
        "signed_vm81_admission_performed", "canonical_hash216_admitted",
        "canonical_persistence_performed",
    }
    if not isinstance(association, Mapping) or set(association) != keys:
        raise UQCELSourceAssociationError("ASSOCIATION_RECEIPT_SHAPE_INVALID")
    if association["schema"] != SCHEMA:
        raise UQCELSourceAssociationError("ASSOCIATION_SCHEMA_INVALID")
    for key in (
        "native_uqcel_validated", "association_replay_required",
        "authenticated_owner_required_on_replay", "source_to_witness_candidate_association",
    ):
        if association[key] is not True:
            raise UQCELSourceAssociationError("ASSOCIATION_RECEIPT_STATE_INVALID")
    for key in (
        "source_to_witness_authorized_provenance", "authorized_parent_hash216_bound",
        "signed_vm81_admission_performed", "canonical_hash216_admitted",
        "canonical_persistence_performed",
    ):
        if association[key] is not False:
            raise UQCELSourceAssociationError("ASSOCIATION_AUTHORITY_ESCALATION_FORBIDDEN")
    upload_id = association["upload_id"]
    witness = association["witness"]
    if not isinstance(upload_id, str) or not isinstance(witness, Mapping):
        raise UQCELSourceAssociationError("ASSOCIATION_INPUT_INVALID")
    expected = build_candidate_source_witness_association(
        staging, upload_id, authenticated_owner, witness=witness,
        native_validator=native_validator,
    )
    if dict(association) != expected:
        raise UQCELSourceAssociationError("ASSOCIATION_SOURCE_WITNESS_REPLAY_MISMATCH")
    return {
        "schema": "HHS_ADMIN_SQL_UQCEL_ASSOCIATION_REPLAY_V1",
        "upload_id": upload_id,
        "source_sha256": expected["source_sha256"],
        "candidate_association_sha256": expected["candidate_association_sha256"],
        "exact_source_witness_association_replayed": True,
        "native_uqcel_revalidated": True,
        "source_to_witness_authorized_provenance": False,
        "authorized_parent_hash216_bound": False,
        "signed_vm81_admission_performed": False,
        "canonical_hash216_admitted": False,
    }
