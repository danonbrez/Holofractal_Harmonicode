"""Read-only exact typed VM81 frame recognition for staged sources.

A staged source is normally arbitrary bytes, not a canonical VM81 frame.
Only a source *already encoded in the inherited Pass219 exact 81-word
BigInt/phase-qudit format* can be decoded as a typed frame here. Nothing
derives a parent Hash216 reference, creates UQCEL arithmetic witnesses, or
calls signed environmental admission.
"""
from __future__ import annotations

from hashlib import sha256

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    VM81_FRAME_BYTES,
    VM81RNABigIntExecutionBindingProbeError,
    raw_le_to_words,
    unpack_vm81_binding_words,
    words_to_raw_le,
)


def inspect_exact_typed_vm81_source(
    staging: AdminStreamStaging, upload_id: str, owner: str,
) -> dict[str, object]:
    record = staging.status(upload_id, owner)
    if record["state"] != "STAGED":
        raise ValueError("TYPED_VM81_SOURCE_NOT_STAGED")
    path = staging.read_staged(upload_id, owner)
    # This check recognizes an existing native frame, it never restricts
    # permissible general IDE files or the larger streaming upload service.
    if record["received_bytes"] != VM81_FRAME_BYTES:
        return {
            "schema": "HHS_ADMIN_TYPED_VM81_SOURCE_INSPECTION_V1",
            "upload_id": upload_id,
            "source_sha256": record["source_sha256"],
            "typed_frame_recognized": False,
            "reason": "SOURCE_NOT_AN_EXISTING_648_BYTE_VM81_FRAME",
            "canonical_hash216_admitted": False,
            "signed_vm81_admission_performed": False,
        }
    with path.open("rb") as stream:
        raw = stream.read(VM81_FRAME_BYTES + 1)
    if len(raw) != VM81_FRAME_BYTES or sha256(raw).hexdigest() != record["source_sha256"]:
        raise ValueError("TYPED_VM81_STAGED_SOURCE_DRIFT")
    try:
        words = raw_le_to_words(raw)
        typed = unpack_vm81_binding_words(words)
        if words_to_raw_le(words) != raw:
            raise ValueError("TYPED_VM81_FRAME_REENCODE_DRIFT")
    except VM81RNABigIntExecutionBindingProbeError:
        return {
            "schema": "HHS_ADMIN_TYPED_VM81_SOURCE_INSPECTION_V1",
            "upload_id": upload_id,
            "source_sha256": record["source_sha256"],
            "typed_frame_recognized": False,
            "reason": "INHERITED_VM81_TYPED_DECODER_REJECTED",
            "canonical_hash216_admitted": False,
            "signed_vm81_admission_performed": False,
        }
    return {
        "schema": "HHS_ADMIN_TYPED_VM81_SOURCE_INSPECTION_V1",
        "upload_id": upload_id,
        "source_sha256": record["source_sha256"],
        "typed_frame_recognized": True,
        "vm81_frame_bytes": VM81_FRAME_BYTES,
        "bigint": str(typed["bigint"]),
        "glyph_count": len(typed["glyph_stream"]),
        "metadata": typed["metadata"],
        "frame_reencoded_exact": True,
        "authorized_parent_hash216_bound": False,
        "uqcel_math_witness_bound": False,
        "canonical_hash216_admitted": False,
        "signed_vm81_admission_performed": False,
        "next_gate": "AUTHORIZED_UQCEL_WITNESS_AND_HASH216_PARENT",
    }
