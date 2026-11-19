"""Pure inherited native UQCEL witness prevalidation for a staged typed VM81 source.

This boundary validates explicitly supplied exact integer mathematical input
using the existing Pass219 UQCEL C ABI. It does not claim that the witness
is bound to the source, that a parent Hash216 reference is authorized, or that
the signed environmental VM81 mutator has run.
"""
from __future__ import annotations

from typing import Mapping

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_typed_vm81_source_v1 import inspect_exact_typed_vm81_source


class UQCELWitnessPrevalidationError(ValueError):
    pass


_INTEGER_FIELDS = ("P", "p", "q", "delta", "A", "B", "cell81", "left_basis8", "right_basis8")
_BIGUINT_FIELDS = frozenset(("P", "p", "q", "delta", "A", "B"))


def prevalidate_staged_uqcel_witness(
    staging: AdminStreamStaging,
    upload_id: str,
    authenticated_owner: str,
    *,
    witness: Mapping[str, object],
    native_validator=None,
) -> dict[str, object]:
    """Validate typed arithmetic separately from source and Hash216 authorization."""
    frame = inspect_exact_typed_vm81_source(staging, upload_id, authenticated_owner)
    if frame["typed_frame_recognized"] is not True:
        raise UQCELWitnessPrevalidationError("EXISTING_TYPED_VM81_FRAME_REQUIRED")
    if not isinstance(witness, Mapping) or set(witness) != set(_INTEGER_FIELDS) | {"previous_hash72"}:
        raise UQCELWitnessPrevalidationError("EXACT_UQCEL_WITNESS_SHAPE_REQUIRED")
    values = {}
    for name in _INTEGER_FIELDS:
        value = witness[name]
        if type(value) is not int:
            raise UQCELWitnessPrevalidationError("EXACT_UQCEL_INTEGER_REQUIRED:" + name)
        if name in _BIGUINT_FIELDS and value < 0:
            raise UQCELWitnessPrevalidationError("EXACT_UQCEL_NONNEGATIVE_REQUIRED:" + name)
        if name in ("cell81",) and not 0 <= value < 81:
            raise UQCELWitnessPrevalidationError("EXACT_UQCEL_CELL81_RANGE")
        if name in ("left_basis8", "right_basis8") and not 0 <= value < 8:
            raise UQCELWitnessPrevalidationError("EXACT_UQCEL_BASIS8_RANGE")
        values[name] = value
    previous = witness["previous_hash72"]
    if not isinstance(previous, str) or len(previous) != 72 or not previous.isascii():
        raise UQCELWitnessPrevalidationError("EXACT_UQCEL_PREVIOUS_HASH72_REQUIRED")
    if native_validator is None:
        from hhs_python.runtime.hhs_uqcel_ctypes_bridge import HHSUQCELRuntimeBridge
        native_validator = HHSUQCELRuntimeBridge.validate
    result = native_validator(**values, previous_hash72=previous)
    if not isinstance(result, dict) or type(result.get("status")) is not int or not isinstance(result.get("admission"), dict):
        raise UQCELWitnessPrevalidationError("NATIVE_UQCEL_VALIDATION_RECEIPT_INVALID")
    admission = result["admission"]
    if type(admission.get("decision")) is not int:
        raise UQCELWitnessPrevalidationError("NATIVE_UQCEL_DECISION_MISSING")
    return {
        "schema": "HHS_ADMIN_SQL_UQCEL_WITNESS_PREVALIDATION_V1",
        "upload_id": upload_id,
        "source_sha256": frame["source_sha256"],
        "typed_frame_recognized": True,
        "uqcel_native_status": result["status"],
        "uqcel_native_decision": admission["decision"],
        "uqcel_native_validation_succeeded": (
            result["status"] == 0 and admission["decision"] == 1
            and admission.get("source_hash_match") is True
        ),
        "uqcel_native_source_hash_match": admission.get("source_hash_match") is True,
        "source_to_witness_provenance_bound": False,
        "authorized_parent_hash216_bound": False,
        "signed_vm81_admission_performed": False,
        "canonical_hash216_admitted": False,
        "next_gate": "SOURCE_BOUND_WITNESS_AND_AUTHORIZED_CURRENT_PARENT_HASH216",
    }
