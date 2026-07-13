"""
HHS Universal Data Flow Protocol Frame v1
=========================================

Pass 039 defines the HHS-UDFP frame as the universal multimodal flow wrapper for
HHFS-bound carriers.  A frame binds a carrier-native capsule to metadata,
transformation history, ECC, and witness roots without introducing sidecars,
duplicate payloads, or hidden computation lanes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path
from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import (
    ADMIT_HHFS_CARRIER_CAPSULE,
    CANONICAL_CAPSULE_FIELD_ORDER,
    _contains_float,
    _hash72,
    make_hhfs_carrier_capsule,
    commit_payload_view,
    validate_hhfs_carrier_capsule,
)
from hhs_runtime.hhs_metadata_enhancement_block_v1 import (
    ADMIT_METADATA_ENHANCEMENT_BLOCK,
    make_metadata_enhancement_block,
    validate_metadata_enhancement_block,
)
from hhs_runtime.hhs_genesis_severance_protocol_v1 import WITNESSED_CONTINUITY


VERSION = "PASS_039_UDFP_FRAME_V1"
UDFP_FRAME_SCHEMA = "HHS_UDFP_FRAME_V1"

REJECT_UDFP_FLOAT_CONSTANT = "REJECT_UDFP_FLOAT_CONSTANT"
REJECT_UDFP_INVALID_CARRIER_CAPSULE = "REJECT_UDFP_INVALID_CARRIER_CAPSULE"
REJECT_UDFP_INVALID_METADATA_BLOCK = "REJECT_UDFP_INVALID_METADATA_BLOCK"
REJECT_UDFP_FRAME_HASH_MISMATCH = "REJECT_UDFP_FRAME_HASH_MISMATCH"
REJECT_UDFP_PARALLEL_LANE = "REJECT_UDFP_PARALLEL_LANE"
ADMIT_UDFP_FRAME = "ADMIT_UDFP_FRAME"

CANONICAL_UDFP_FRAME_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "frame_index",
    "carrier_type",
    "modality_type",
    "phase_binding",
    "payload_commitment",
    "carrier_capsule_hash72",
    "metadata_enhancement_root",
    "transformation_trace_root",
    "error_correction_root",
    "root_witness_hash72",
    "previous_frame_root",
    "legacy_compatibility_required",
    "no_parallel_storage_required",
    "no_parallel_computation_required",
    "duplicate_payload_storage_allowed",
    "external_dependency_allowed",
    "hash_authority",
)



def _pass039_ledger_path():
    return runtime_artifact_path("hhs_pass039_hhfs_udfp_ledger.json")


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {"schema": "HHS_UDFP_FRAME_REJECTION_V1", "ok": False, "status": status, "reason": reason, "details": dict(details or {})}


def canonical_udfp_frame_fields(
    *,
    carrier_capsule: Mapping[str, Any],
    metadata_block: Mapping[str, Any],
    frame_index: int = 0,
    previous_frame_root: str = "GENESIS_FRAME_ROOT",
) -> Dict[str, Any]:
    capsule_fields = carrier_capsule.get("canonical_capsule_fields", {})
    metadata_fields = metadata_block.get("canonical_metadata_fields", {})
    return {
        "schema": UDFP_FRAME_SCHEMA,
        "version": VERSION,
        "frame_index": int(frame_index),
        "carrier_type": str(capsule_fields.get("carrier_type")),
        "modality_type": str(capsule_fields.get("modality_type")),
        "phase_binding": str(capsule_fields.get("phase_binding", WITNESSED_CONTINUITY)),
        "payload_commitment": str(capsule_fields.get("payload_commitment")),
        "carrier_capsule_hash72": str(carrier_capsule.get("capsule_hash72")),
        "metadata_enhancement_root": str(metadata_block.get("metadata_enhancement_root")),
        "transformation_trace_root": str(capsule_fields.get("transformation_trace_root")),
        "error_correction_root": str(capsule_fields.get("error_correction_root")),
        "root_witness_hash72": str(capsule_fields.get("root_witness_hash72")),
        "previous_frame_root": str(previous_frame_root),
        "legacy_compatibility_required": True,
        "no_parallel_storage_required": True,
        "no_parallel_computation_required": True,
        "duplicate_payload_storage_allowed": False,
        "external_dependency_allowed": False,
        "hash_authority": str(capsule_fields.get("hash_authority", "HASH72_U72_C_KERNEL")),
    }


@dataclass(frozen=True)
class HHSUDFPFrame:
    schema: str
    version: str
    canonical_frame_fields: Dict[str, Any]
    current_frame_root: str
    carrier_capsule: Dict[str, Any]
    metadata_block: Dict[str, Any]
    kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_udfp_frame(frame: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(frame):
        return _reject(REJECT_UDFP_FLOAT_CONSTANT, "UDFP frames must use exact symbolic/rational values, not floats.")
    carrier_capsule = frame.get("carrier_capsule")
    metadata_block = frame.get("metadata_block")
    if not isinstance(carrier_capsule, Mapping):
        return _reject(REJECT_UDFP_INVALID_CARRIER_CAPSULE, "UDFP frame requires an HHFS carrier capsule.")
    if not isinstance(metadata_block, Mapping):
        return _reject(REJECT_UDFP_INVALID_METADATA_BLOCK, "UDFP frame requires a metadata enhancement block.")

    capsule_validation = validate_hhfs_carrier_capsule(carrier_capsule)
    if capsule_validation.get("status") != ADMIT_HHFS_CARRIER_CAPSULE:
        return _reject(REJECT_UDFP_INVALID_CARRIER_CAPSULE, "Carrier capsule failed HHFS validation.", details=capsule_validation)
    metadata_validation = validate_metadata_enhancement_block(metadata_block)
    if metadata_validation.get("status") != ADMIT_METADATA_ENHANCEMENT_BLOCK:
        return _reject(REJECT_UDFP_INVALID_METADATA_BLOCK, "Metadata enhancement block failed validation.", details=metadata_validation)

    fields = frame.get("canonical_frame_fields", {})
    expected_fields = canonical_udfp_frame_fields(
        carrier_capsule=carrier_capsule,
        metadata_block=metadata_block,
        frame_index=int(fields.get("frame_index", 0) if isinstance(fields, Mapping) else 0),
        previous_frame_root=str(fields.get("previous_frame_root", "GENESIS_FRAME_ROOT") if isinstance(fields, Mapping) else "GENESIS_FRAME_ROOT"),
    )

    if expected_fields.get("metadata_enhancement_root") != carrier_capsule["canonical_capsule_fields"].get("metadata_enhancement_root"):
        return _reject(REJECT_UDFP_INVALID_METADATA_BLOCK, "Metadata root must match the carrier capsule metadata commitment.")

    if bool(expected_fields.get("duplicate_payload_storage_allowed")) or bool(expected_fields.get("external_dependency_allowed")):
        return _reject(REJECT_UDFP_PARALLEL_LANE, "UDFP frames forbid duplicate payload storage and external dependencies.")

    expected_root = _hash72("HHS_UDFP_FRAME_V1", {key: expected_fields.get(key) for key in CANONICAL_UDFP_FRAME_FIELD_ORDER}, width=72)
    supplied_root = frame.get("current_frame_root")
    if supplied_root and supplied_root != expected_root:
        return _reject(REJECT_UDFP_FRAME_HASH_MISMATCH, "UDFP current frame root does not match canonical frame fields.")

    record = {
        "schema": "HHS_UDFP_FRAME_VALIDATION_V1",
        "ok": True,
        "status": ADMIT_UDFP_FRAME,
        "admitted": True,
        "current_frame_root": expected_root,
        "carrier_type": expected_fields.get("carrier_type"),
        "modality_type": expected_fields.get("modality_type"),
        "payload_commitment": expected_fields.get("payload_commitment"),
        "legacy_compatibility_required": True,
        "no_parallel_storage": True,
        "no_parallel_computation": True,
    }
    kernel = make_hash72_kernel_witness("HHS_UDFP_FRAME_VALIDATION_V1", record, width=72).to_dict()
    ledger = append_payload("UDFP_FRAME_VALIDATION", "hhs_udfp_frame_v1.validate_udfp_frame", {**record, "kernel_digest72": kernel.get("digest")}, ledger_path=_pass039_ledger_path())
    record["kernel_witness"] = kernel
    record["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
    return record


def make_udfp_frame(
    *,
    carrier_capsule: Mapping[str, Any],
    metadata_block: Mapping[str, Any],
    frame_index: int = 0,
    previous_frame_root: str = "GENESIS_FRAME_ROOT",
) -> Dict[str, Any]:
    fields = canonical_udfp_frame_fields(
        carrier_capsule=carrier_capsule,
        metadata_block=metadata_block,
        frame_index=frame_index,
        previous_frame_root=previous_frame_root,
    )
    kernel = make_hash72_kernel_witness("HHS_UDFP_FRAME_V1", {key: fields.get(key) for key in CANONICAL_UDFP_FRAME_FIELD_ORDER}, width=72).to_dict()
    ledger = append_payload("UDFP_FRAME", "hhs_udfp_frame_v1.make_udfp_frame", {"canonical_frame_fields": fields, "current_frame_root": kernel.get("digest")}, ledger_path=_pass039_ledger_path())
    frame = HHSUDFPFrame(
        schema=UDFP_FRAME_SCHEMA,
        version=VERSION,
        canonical_frame_fields=fields,
        current_frame_root=str(kernel.get("digest")),
        carrier_capsule=dict(carrier_capsule),
        metadata_block=dict(metadata_block),
        kernel_witness=kernel,
        unified_ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
    ).to_dict()
    validation = validate_udfp_frame(frame)
    if not validation.get("ok"):
        raise ValueError(validation.get("status", "UDFP frame validation failed"))
    frame["validation"] = validation
    return frame


def udfp_frame_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload_commitment = commit_payload_view({"carrier": "png", "payload": "commitment-only-sample"})
    trace_root = _hash72("UDFP_SAMPLE_TRACE_ROOT", {"trace": ["capture"]}, width=72)
    metadata = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample"},
        resolution_profile={"width": "1024", "height": "1024"},
        semantic_checksums={"scene": "sample"},
        observer_witness_id="UDFP_SELF_TEST_OBSERVER",
        transformation_trace_root=trace_root,
    )
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=payload_commitment,
        metadata_enhancement_root=metadata["metadata_enhancement_root"],
        transformation_trace_root=trace_root,
        error_correction_root=_hash72("UDFP_SAMPLE_ECC", {"ecc": "bounded"}, width=72),
    )
    frame = make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)
    valid = validate_udfp_frame(frame)
    tampered = dict(frame)
    tampered["current_frame_root"] = "X" * 72
    mismatch = validate_udfp_frame(tampered)
    bad_capsule = dict(capsule)
    bad_fields = dict(bad_capsule["canonical_capsule_fields"])
    bad_fields["storage_lanes"] = [*bad_fields["storage_lanes"], "remote_resolver"]
    bad_capsule["canonical_capsule_fields"] = bad_fields
    invalid_capsule = validate_udfp_frame({**frame, "carrier_capsule": bad_capsule})
    ok = bool(
        valid.get("status") == ADMIT_UDFP_FRAME
        and mismatch.get("status") == REJECT_UDFP_FRAME_HASH_MISMATCH
        and invalid_capsule.get("status") == REJECT_UDFP_INVALID_CARRIER_CAPSULE
        and valid.get("unified_ledger", {}).get("verified") is True
    )
    return {
        "schema": "HHS_UDFP_FRAME_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "valid_status": valid.get("status"),
        "hash_mismatch_status": mismatch.get("status"),
        "invalid_capsule_status": invalid_capsule.get("status"),
        "current_frame_root": frame.get("current_frame_root"),
        "canonical_frame_field_count": len(CANONICAL_UDFP_FRAME_FIELD_ORDER),
        "ledger_verified": valid.get("unified_ledger", {}).get("verified") is True,
    }


if __name__ == "__main__":
    print(json.dumps(udfp_frame_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
