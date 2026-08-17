"""Compatibility binding for the frozen Pass 218 Iteration-6 receipt shape.

The validated Iteration-6 implementation assembles its final receipt as
``{"schema": RECEIPT_SCHEMA, **commit_payload, ...}``. Because the inherited
commit payload itself has a ``schema`` field, Python's ordered mapping expansion
preserves the later payload schema in the serialized receipt. Iteration 7 must
not rewrite already-validated Iteration-6 receipt bytes merely to normalize that
outer label.

This adapter admits exactly two outer labels: the intended receipt label and
the exact validated Iteration-6 payload label. All authoritative receipt fields,
commit Hash72, receipt Hash72, and Hash216 are still independently recomputed by
the Iteration-7 validator. The historical outer label is restored after
validation so restart preserves the original committed receipt byte-for-byte.
"""
from __future__ import annotations

from typing import Any, Mapping

from . import persistence as _base

_INTENDED_I6_RECEIPT_SCHEMA = "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1"
_VALIDATED_I6_OUTER_SCHEMA = "HHS-P218-I6-CANONICAL-COMMIT-PAYLOAD-V1"
_original_validate_commit_receipt = _base._validate_commit_receipt


def _validate_frozen_i6_commit_receipt(
    authorization_hash72: str,
    receipt: Mapping[str, Any],
    entries: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    outer_schema = receipt.get("schema")
    if outer_schema not in {
        _INTENDED_I6_RECEIPT_SCHEMA,
        _VALIDATED_I6_OUTER_SCHEMA,
    }:
        return _original_validate_commit_receipt(
            authorization_hash72,
            receipt,
            entries,
        )

    normalized = _base._copy(receipt)
    normalized["schema"] = _INTENDED_I6_RECEIPT_SCHEMA
    validated = _original_validate_commit_receipt(
        authorization_hash72,
        normalized,
        entries,
    )
    validated["schema"] = outer_schema
    return validated


# Install once. The marker prevents repeated package reloads from wrapping the
# validator recursively.
if not getattr(_base, "_P218_I7_FROZEN_I6_RECEIPT_COMPAT", False):
    _base._validate_commit_receipt = _validate_frozen_i6_commit_receipt
    _base._P218_I7_FROZEN_I6_RECEIPT_COMPAT = True

CHECKPOINT_SCHEMA = _base.CHECKPOINT_SCHEMA
DurableRestoreResult = _base.DurableRestoreResult
MANIFEST_SCHEMA = _base.MANIFEST_SCHEMA
PASS218_PERSISTENCE_VERSION = _base.PASS218_PERSISTENCE_VERSION
Pass218DurableCanonicalStore = _base.Pass218DurableCanonicalStore
Pass218PersistenceError = _base.Pass218PersistenceError
Pass218PersistenceStateError = _base.Pass218PersistenceStateError
Pass218PersistenceValidationError = _base.Pass218PersistenceValidationError
RESTORE_SCHEMA = _base.RESTORE_SCHEMA
restore_target_from_checkpoint = _base.restore_target_from_checkpoint
seal_checkpoint = _base.seal_checkpoint
seal_manifest = _base.seal_manifest
validate_checkpoint = _base.validate_checkpoint
validate_manifest = _base.validate_manifest

__all__ = [
    "CHECKPOINT_SCHEMA",
    "DurableRestoreResult",
    "MANIFEST_SCHEMA",
    "PASS218_PERSISTENCE_VERSION",
    "Pass218DurableCanonicalStore",
    "Pass218PersistenceError",
    "Pass218PersistenceStateError",
    "Pass218PersistenceValidationError",
    "RESTORE_SCHEMA",
    "restore_target_from_checkpoint",
    "seal_checkpoint",
    "seal_manifest",
    "validate_checkpoint",
    "validate_manifest",
]
