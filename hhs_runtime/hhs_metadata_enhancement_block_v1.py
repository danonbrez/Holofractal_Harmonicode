"""
HHS Metadata Enhancement Block v1
=================================

Pass 039 defines metadata as a carrier-compatible witness enhancement layer,
not a duplicate payload lane.  The block binds capture context, modality,
resolution, semantic checksums, transformation history, and HHS invariants into
Hash72/u^72 commitments.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path
from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import (
    CARRIER_PROFILES,
    CLOSURE_CONSTANT_Q,
    DEFAULT_ROOT_MARKER,
    HASH72_AUTHORITY,
    RESONATOR_CONSTANT_Q,
    _contains_float,
    _hash72,
)
from hhs_runtime.hhs_genesis_severance_protocol_v1 import WITNESSED_CONTINUITY


VERSION = "PASS_039_METADATA_ENHANCEMENT_BLOCK_V1"
METADATA_BLOCK_SCHEMA = "HHS_METADATA_ENHANCEMENT_BLOCK_V1"

FORBIDDEN_METADATA_PAYLOAD_FIELDS = {
    "payload",
    "raw_payload",
    "payload_copy",
    "duplicate_payload",
    "embedded_payload",
    "parallel_archive_payload",
}

REJECT_METADATA_FLOAT_CONSTANT = "REJECT_METADATA_FLOAT_CONSTANT"
REJECT_METADATA_UNSUPPORTED_CARRIER = "REJECT_METADATA_UNSUPPORTED_CARRIER"
REJECT_METADATA_DUPLICATE_PAYLOAD = "REJECT_METADATA_DUPLICATE_PAYLOAD"
REJECT_METADATA_TRANSFORMATION_TRACE_REQUIRED = "REJECT_METADATA_TRANSFORMATION_TRACE_REQUIRED"
REJECT_METADATA_HASH_MISMATCH = "REJECT_METADATA_HASH_MISMATCH"
ADMIT_METADATA_ENHANCEMENT_BLOCK = "ADMIT_METADATA_ENHANCEMENT_BLOCK"

CANONICAL_METADATA_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "carrier_type",
    "modality_type",
    "carrier_native_witness_lane",
    "capture_context_commitment",
    "resolution_profile_commitment",
    "semantic_checksums",
    "observer_witness_id",
    "transformation_trace_root",
    "phase_binding",
    "metadata_payload_policy",
    "root_marker_declared",
    "resonator_constant_q",
    "closure_constant_q",
    "ring",
    "extended_ring",
    "loshu_anchor",
    "parity_required",
    "delta_e_required",
    "omega_required",
    "hash_authority",
)



def _pass039_ledger_path():
    return runtime_artifact_path("hhs_pass039_hhfs_udfp_ledger.json")


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {"schema": "HHS_METADATA_ENHANCEMENT_BLOCK_REJECTION_V1", "ok": False, "status": status, "reason": reason, "details": dict(details or {})}


def _semantic_checksum_map(values: Optional[Mapping[str, Any]]) -> Dict[str, str]:
    checksums: Dict[str, str] = {}
    for key, value in sorted((values or {}).items()):
        if _contains_float(value):
            raise ValueError("metadata semantic checksums cannot contain floats")
        checksums[str(key)] = _hash72(f"HHS_METADATA_SEMANTIC_CHECKSUM::{key}", value, width=72)
    return checksums


def canonical_metadata_fields(
    *,
    carrier_type: str,
    modality_type: str,
    capture_context: Mapping[str, Any],
    resolution_profile: Mapping[str, Any],
    semantic_checksums: Optional[Mapping[str, Any]],
    observer_witness_id: str,
    transformation_trace_root: str,
    phase_binding: str = WITNESSED_CONTINUITY,
    root_marker_declared: str = DEFAULT_ROOT_MARKER,
) -> Dict[str, Any]:
    carrier_type = str(carrier_type).lower().strip()
    if carrier_type not in CARRIER_PROFILES:
        raise ValueError(f"unsupported carrier_type: {carrier_type}")
    if _contains_float(capture_context) or _contains_float(resolution_profile):
        raise ValueError("metadata enhancement block requires exact symbolic/rational values; floats are rejected")
    fields = {
        "schema": METADATA_BLOCK_SCHEMA,
        "version": VERSION,
        "carrier_type": carrier_type,
        "modality_type": str(modality_type),
        "carrier_native_witness_lane": CARRIER_PROFILES[carrier_type]["native_witness_lane"],
        "capture_context_commitment": _hash72("HHS_METADATA_CAPTURE_CONTEXT_V1", dict(capture_context), width=72),
        "resolution_profile_commitment": _hash72("HHS_METADATA_RESOLUTION_PROFILE_V1", dict(resolution_profile), width=72),
        "semantic_checksums": _semantic_checksum_map(semantic_checksums),
        "observer_witness_id": str(observer_witness_id),
        "transformation_trace_root": str(transformation_trace_root),
        "phase_binding": str(phase_binding),
        "metadata_payload_policy": "commitments_only_no_duplicate_payload",
        "root_marker_declared": str(root_marker_declared),
        "resonator_constant_q": RESONATOR_CONSTANT_Q,
        "closure_constant_q": CLOSURE_CONSTANT_Q,
        "ring": "u^72",
        "extended_ring": "u^216",
        "loshu_anchor": 5,
        "parity_required": "Psi=0",
        "delta_e_required": "Delta_e=0",
        "omega_required": True,
        "hash_authority": HASH72_AUTHORITY,
    }
    return {key: fields[key] for key in CANONICAL_METADATA_FIELD_ORDER}


@dataclass(frozen=True)
class HHSMetadataEnhancementBlock:
    schema: str
    version: str
    canonical_metadata_fields: Dict[str, Any]
    metadata_enhancement_root: str
    kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_metadata_enhancement_block(block: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(block):
        return _reject(REJECT_METADATA_FLOAT_CONSTANT, "Metadata enhancement blocks must not contain floats.")
    for forbidden in FORBIDDEN_METADATA_PAYLOAD_FIELDS:
        if forbidden in block:
            return _reject(REJECT_METADATA_DUPLICATE_PAYLOAD, "Metadata enhancement stores commitments and witnesses, never duplicate payloads.", details={"field": forbidden})
    fields = block.get("canonical_metadata_fields", block)
    if not isinstance(fields, Mapping):
        return _reject(REJECT_METADATA_UNSUPPORTED_CARRIER, "Metadata enhancement canonical fields are missing or invalid.")
    for forbidden in FORBIDDEN_METADATA_PAYLOAD_FIELDS:
        if forbidden in fields:
            return _reject(REJECT_METADATA_DUPLICATE_PAYLOAD, "Metadata canonical fields cannot contain payload copies.", details={"field": forbidden})
    carrier_type = str(fields.get("carrier_type", "")).lower().strip()
    if carrier_type not in CARRIER_PROFILES:
        return _reject(REJECT_METADATA_UNSUPPORTED_CARRIER, "Carrier profile is not HHFS-declared.", details={"carrier_type": carrier_type})
    if not fields.get("transformation_trace_root"):
        return _reject(REJECT_METADATA_TRANSFORMATION_TRACE_REQUIRED, "Metadata enhancement requires a transformation trace root.")
    expected_root = _hash72("HHS_METADATA_ENHANCEMENT_BLOCK_V1", {key: fields.get(key) for key in CANONICAL_METADATA_FIELD_ORDER}, width=72)
    supplied_root = block.get("metadata_enhancement_root")
    if supplied_root and supplied_root != expected_root:
        return _reject(REJECT_METADATA_HASH_MISMATCH, "Metadata enhancement root does not match canonical fields.")
    record = {
        "schema": "HHS_METADATA_ENHANCEMENT_BLOCK_VALIDATION_V1",
        "ok": True,
        "status": ADMIT_METADATA_ENHANCEMENT_BLOCK,
        "admitted": True,
        "carrier_type": carrier_type,
        "modality_type": fields.get("modality_type"),
        "metadata_enhancement_root": expected_root,
        "payload_policy": fields.get("metadata_payload_policy"),
        "transformation_trace_required": True,
    }
    kernel = make_hash72_kernel_witness("HHS_METADATA_ENHANCEMENT_BLOCK_VALIDATION_V1", record, width=72).to_dict()
    ledger = append_payload("METADATA_ENHANCEMENT_BLOCK_VALIDATION", "hhs_metadata_enhancement_block_v1.validate_metadata_enhancement_block", {**record, "kernel_digest72": kernel.get("digest")}, ledger_path=_pass039_ledger_path())
    record["kernel_witness"] = kernel
    record["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
    return record


def make_metadata_enhancement_block(**kwargs: Any) -> Dict[str, Any]:
    fields = canonical_metadata_fields(**kwargs)
    kernel = make_hash72_kernel_witness("HHS_METADATA_ENHANCEMENT_BLOCK_V1", fields, width=72).to_dict()
    ledger = append_payload("METADATA_ENHANCEMENT_BLOCK", "hhs_metadata_enhancement_block_v1.make_metadata_enhancement_block", {"canonical_metadata_fields": fields, "metadata_enhancement_root": kernel.get("digest")}, ledger_path=_pass039_ledger_path())
    block = HHSMetadataEnhancementBlock(
        schema=METADATA_BLOCK_SCHEMA,
        version=VERSION,
        canonical_metadata_fields=fields,
        metadata_enhancement_root=str(kernel.get("digest")),
        kernel_witness=kernel,
        unified_ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
    ).to_dict()
    validation = validate_metadata_enhancement_block(block)
    if not validation.get("ok"):
        raise ValueError(validation.get("status", "metadata enhancement validation failed"))
    block["validation"] = validation
    return block


def metadata_enhancement_block_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    trace_root = _hash72("HHS_METADATA_SAMPLE_TRACE_ROOT", {"trace": ["capture"]}, width=72)
    block = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample", "epoch_marker": DEFAULT_ROOT_MARKER},
        resolution_profile={"width": "1024", "height": "1024", "unit": "px"},
        semantic_checksums={"scene": "sample-image-state"},
        observer_witness_id="SELF_TEST_OBSERVER",
        transformation_trace_root=trace_root,
    )
    valid = validate_metadata_enhancement_block(block)
    duplicate = validate_metadata_enhancement_block({**block, "raw_payload": "forbidden"})
    missing_trace_fields = dict(block["canonical_metadata_fields"])
    missing_trace_fields["transformation_trace_root"] = ""
    missing_trace = validate_metadata_enhancement_block({"canonical_metadata_fields": missing_trace_fields})
    ok = bool(
        valid.get("status") == ADMIT_METADATA_ENHANCEMENT_BLOCK
        and duplicate.get("status") == REJECT_METADATA_DUPLICATE_PAYLOAD
        and missing_trace.get("status") == REJECT_METADATA_TRANSFORMATION_TRACE_REQUIRED
        and valid.get("unified_ledger", {}).get("verified") is True
    )
    return {
        "schema": "HHS_METADATA_ENHANCEMENT_BLOCK_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "valid_status": valid.get("status"),
        "duplicate_rejection_status": duplicate.get("status"),
        "missing_trace_rejection_status": missing_trace.get("status"),
        "metadata_enhancement_root": block.get("metadata_enhancement_root"),
        "canonical_metadata_field_count": len(CANONICAL_METADATA_FIELD_ORDER),
        "ledger_verified": valid.get("unified_ledger", {}).get("verified") is True,
    }


if __name__ == "__main__":
    print(json.dumps(metadata_enhancement_block_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
