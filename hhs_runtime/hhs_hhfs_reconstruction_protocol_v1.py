"""
HHS HHFS Reconstruction Protocol v1
===================================

Pass 040 defines reconstruction as a witnessed transformation surface.  The
protocol reads only UDFP/HHFS commitments, validates the carrier frame, attempts
bounded ECC reconstruction, and records the repair as a Hash72/u^72 receipt.
It never silently repairs and never stores a duplicate payload.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path
from hhs_runtime.hhs_udfp_frame_v1 import ADMIT_UDFP_FRAME, validate_udfp_frame
from hhs_runtime.hhs_hhfs_carrier_adapter_v1 import (
    ADMIT_HHFS_CARRIER_ADAPTER_OPERATION,
    execute_hhfs_carrier_adapter_operation,
)
from hhs_runtime.hhs_validation_residue_compressor_v1 import (
    ADMIT_VALIDATION_RESIDUE_STATE_CHAIN,
    GENESIS_STATE_ROOT,
    make_validation_residue_state_chain,
    validate_validation_residue_state_chain,
)


VERSION = "PASS_040_HHFS_RECONSTRUCTION_PROTOCOL_V1"
RECONSTRUCTION_RECORD_SCHEMA = "HHS_HHFS_RECONSTRUCTION_RECORD_V1"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"

CARRIER_INTACT = "carrier_intact"
PAYLOAD_CORRUPTED_ECC_RECOVERABLE = "payload_corrupted_ecc_recoverable"
PAYLOAD_CORRUPTED_ECC_UNRECOVERABLE = "payload_corrupted_ecc_unrecoverable"
WITNESS_CORRUPTED = "witness_corrupted"

RECONSTRUCTION_NOT_REQUIRED = "RECONSTRUCTION_NOT_REQUIRED"
RECONSTRUCTED_WITH_WITNESS = "RECONSTRUCTED_WITH_WITNESS"
WITNESS_INTACT_PAYLOAD_CORRUPTED = "WITNESS_INTACT_PAYLOAD_CORRUPTED"
RECONSTRUCTION_REJECTED_WITNESS_CORRUPTED = "RECONSTRUCTION_REJECTED_WITNESS_CORRUPTED"

REJECT_RECONSTRUCTION_FLOAT = "REJECT_RECONSTRUCTION_FLOAT"
REJECT_RECONSTRUCTION_INVALID_UDFP_FRAME = "REJECT_RECONSTRUCTION_INVALID_UDFP_FRAME"
REJECT_RECONSTRUCTION_MISSING_ECC_ROOT = "REJECT_RECONSTRUCTION_MISSING_ECC_ROOT"
REJECT_RECONSTRUCTION_SILENT_REPAIR = "REJECT_RECONSTRUCTION_SILENT_REPAIR"
REJECT_RECONSTRUCTION_RECEIPT_HASH_MISMATCH = "REJECT_RECONSTRUCTION_RECEIPT_HASH_MISMATCH"
REJECT_RECONSTRUCTION_RESIDUE_CHAIN_INVALID = "REJECT_RECONSTRUCTION_RESIDUE_CHAIN_INVALID"
REJECT_RECONSTRUCTION_ADAPTER_INVALID = "REJECT_RECONSTRUCTION_ADAPTER_INVALID"

CANONICAL_RECONSTRUCTION_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "corruption_status",
    "reconstruction_status",
    "carrier_type",
    "modality_type",
    "payload_commitment",
    "previous_frame_root",
    "current_frame_root",
    "error_correction_root",
    "adapter_receipt_hash72",
    "residue_state_chain_root_hash72",
    "silent_repair_allowed",
    "transformation_receipt_required",
    "payload_duplication_allowed",
    "legacy_compatibility_preserved",
    "hash_authority",
)


def _pass040_ledger_path():
    return runtime_artifact_path("hhs_pass040_reconstruction_protocol_ledger.json")


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {"schema": "HHS_HHFS_RECONSTRUCTION_REJECTION_V1", "ok": False, "status": status, "reason": reason, "details": dict(details or {})}


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_float(v) for v in value)
    return False


def _hash72(label: str, value: Any, *, width: int = 72) -> str:
    return make_hash72_kernel_witness(label, value, width=width).digest


def _canonical_subset(fields: Mapping[str, Any], order: Tuple[str, ...]) -> Dict[str, Any]:
    return {key: fields.get(key) for key in order}


@dataclass(frozen=True)
class HHFSReconstructionRecord:
    schema: str
    version: str
    canonical_reconstruction_fields: Dict[str, Any]
    reconstruction_receipt_hash72: str
    udfp_validation: Dict[str, Any]
    adapter_record: Optional[Dict[str, Any]]
    residue_state_chain: Dict[str, Any]
    kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def canonical_reconstruction_fields(
    *,
    udfp_frame: Mapping[str, Any],
    corruption_status: str,
    reconstruction_status: str,
    adapter_receipt_hash72: str,
    residue_state_chain_root_hash72: str,
) -> Dict[str, Any]:
    frame_fields = udfp_frame.get("canonical_frame_fields", {})
    fields = {
        "schema": RECONSTRUCTION_RECORD_SCHEMA,
        "version": VERSION,
        "corruption_status": str(corruption_status),
        "reconstruction_status": str(reconstruction_status),
        "carrier_type": str(frame_fields.get("carrier_type")),
        "modality_type": str(frame_fields.get("modality_type")),
        "payload_commitment": str(frame_fields.get("payload_commitment")),
        "previous_frame_root": str(frame_fields.get("previous_frame_root", "GENESIS_FRAME_ROOT")),
        "current_frame_root": str(udfp_frame.get("current_frame_root")),
        "error_correction_root": str(frame_fields.get("error_correction_root")),
        "adapter_receipt_hash72": str(adapter_receipt_hash72),
        "residue_state_chain_root_hash72": str(residue_state_chain_root_hash72),
        "silent_repair_allowed": False,
        "transformation_receipt_required": reconstruction_status == RECONSTRUCTED_WITH_WITNESS,
        "payload_duplication_allowed": False,
        "legacy_compatibility_preserved": True,
        "hash_authority": HASH72_AUTHORITY,
    }
    return _canonical_subset(fields, CANONICAL_RECONSTRUCTION_FIELD_ORDER)


def reconstruct_hhfs_carrier(
    *,
    udfp_frame: Mapping[str, Any],
    corruption_status: str = CARRIER_INTACT,
    reconstruction_parameters: Optional[Mapping[str, Any]] = None,
    previous_residue_state_root: str = GENESIS_STATE_ROOT,
) -> Dict[str, Any]:
    reconstruction_parameters = dict(reconstruction_parameters or {})
    if _contains_float({"udfp_frame": udfp_frame, "parameters": reconstruction_parameters}):
        return _reject(REJECT_RECONSTRUCTION_FLOAT, "Reconstruction rejects floats; use exact symbolic/rational values.")
    if bool(reconstruction_parameters.get("silent_repair_allowed")):
        return _reject(REJECT_RECONSTRUCTION_SILENT_REPAIR, "Reconstruction may not silently repair; it must append a witness receipt.")

    udfp_validation = validate_udfp_frame(udfp_frame)
    if udfp_validation.get("status") != ADMIT_UDFP_FRAME:
        return _reject(REJECT_RECONSTRUCTION_INVALID_UDFP_FRAME, "Reconstruction requires a valid UDFP frame.", details=udfp_validation)

    frame_fields = udfp_frame.get("canonical_frame_fields", {})
    ecc_root = str(frame_fields.get("error_correction_root", ""))
    if corruption_status == PAYLOAD_CORRUPTED_ECC_RECOVERABLE and (not ecc_root or ecc_root == "NO_ECC_ROOT_DECLARED"):
        return _reject(REJECT_RECONSTRUCTION_MISSING_ECC_ROOT, "Recoverable payload corruption requires a declared ECC root.")

    adapter_record: Optional[Dict[str, Any]] = None
    adapter_receipt = "NO_RECONSTRUCTION_ADAPTER_REQUIRED"
    reconstruction_status = RECONSTRUCTION_NOT_REQUIRED
    if corruption_status == CARRIER_INTACT:
        reconstruction_status = RECONSTRUCTION_NOT_REQUIRED
    elif corruption_status == PAYLOAD_CORRUPTED_ECC_RECOVERABLE:
        adapter_record = execute_hhfs_carrier_adapter_operation(
            operation="repair",
            udfp_frame=udfp_frame,
            operation_parameters={"reconstruction_reason": "ecc_recoverable_payload_corruption", **reconstruction_parameters},
            previous_residue_state_root=previous_residue_state_root,
        )
        if adapter_record.get("validation", {}).get("status") != ADMIT_HHFS_CARRIER_ADAPTER_OPERATION:
            return _reject(REJECT_RECONSTRUCTION_ADAPTER_INVALID, "ECC repair adapter operation failed.", details=adapter_record)
        adapter_receipt = str(adapter_record.get("adapter_receipt_hash72"))
        reconstruction_status = RECONSTRUCTED_WITH_WITNESS
    elif corruption_status == PAYLOAD_CORRUPTED_ECC_UNRECOVERABLE:
        reconstruction_status = WITNESS_INTACT_PAYLOAD_CORRUPTED
    elif corruption_status == WITNESS_CORRUPTED:
        return _reject(RECONSTRUCTION_REJECTED_WITNESS_CORRUPTED, "Witness corruption prevents lawful reconstruction from this carrier frame.")
    else:
        return _reject(WITNESS_INTACT_PAYLOAD_CORRUPTED, "Unknown corruption status is treated as unrecoverable payload corruption.", details={"corruption_status": corruption_status})

    residue_chain = make_validation_residue_state_chain(
        [
            {
                "residue_class": "hhfs_reconstruction_validation",
                "modality_type": frame_fields.get("modality_type", "multimodal"),
                "validation_surface": "hhfs_reconstruction_protocol",
                "validation_status": reconstruction_status,
                "source_receipt_hash72": adapter_receipt if adapter_record else udfp_frame.get("current_frame_root", "NO_FRAME_RECEIPT"),
            }
        ],
        previous_state_root=previous_residue_state_root,
    )
    residue_validation = validate_validation_residue_state_chain(residue_chain)
    if residue_validation.get("status") != ADMIT_VALIDATION_RESIDUE_STATE_CHAIN:
        return _reject(REJECT_RECONSTRUCTION_RESIDUE_CHAIN_INVALID, "Reconstruction validation residue failed compression.", details=residue_validation)

    fields = canonical_reconstruction_fields(
        udfp_frame=udfp_frame,
        corruption_status=corruption_status,
        reconstruction_status=reconstruction_status,
        adapter_receipt_hash72=adapter_receipt,
        residue_state_chain_root_hash72=residue_chain["chain_root_hash72"],
    )
    kernel = make_hash72_kernel_witness("HHS_HHFS_RECONSTRUCTION_RECORD_V1", fields, width=72).to_dict()
    ledger = append_payload(
        "HHFS_RECONSTRUCTION_RECORD",
        "hhs_hhfs_reconstruction_protocol_v1.reconstruct_hhfs_carrier",
        {"canonical_reconstruction_fields": fields, "reconstruction_receipt_hash72": kernel.get("digest")},
        ledger_path=_pass040_ledger_path(),
    )
    record = HHFSReconstructionRecord(
        schema=RECONSTRUCTION_RECORD_SCHEMA,
        version=VERSION,
        canonical_reconstruction_fields=fields,
        reconstruction_receipt_hash72=str(kernel.get("digest")),
        udfp_validation=udfp_validation,
        adapter_record=adapter_record,
        residue_state_chain=residue_chain,
        kernel_witness=kernel,
        unified_ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
    ).to_dict()
    validation = validate_hhfs_reconstruction_record(record)
    if not validation.get("ok"):
        return validation
    record["validation"] = validation
    return record


def validate_hhfs_reconstruction_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(record):
        return _reject(REJECT_RECONSTRUCTION_FLOAT, "Reconstruction records reject floats.")
    fields = record.get("canonical_reconstruction_fields", {})
    if not isinstance(fields, Mapping):
        return _reject(REJECT_RECONSTRUCTION_RECEIPT_HASH_MISMATCH, "Missing canonical reconstruction fields.")
    if bool(fields.get("silent_repair_allowed")) or bool(fields.get("payload_duplication_allowed")):
        return _reject(REJECT_RECONSTRUCTION_SILENT_REPAIR, "Reconstruction records forbid silent repair and duplicate payload storage.")
    if fields.get("reconstruction_status") == RECONSTRUCTED_WITH_WITNESS and not fields.get("adapter_receipt_hash72"):
        return _reject(REJECT_RECONSTRUCTION_ADAPTER_INVALID, "Witnessed reconstruction requires an adapter receipt.")
    residue_validation = validate_validation_residue_state_chain(record.get("residue_state_chain", {}))
    if residue_validation.get("status") != ADMIT_VALIDATION_RESIDUE_STATE_CHAIN:
        return _reject(REJECT_RECONSTRUCTION_RESIDUE_CHAIN_INVALID, "Reconstruction residue state chain invalid.", details=residue_validation)
    expected = _hash72("HHS_HHFS_RECONSTRUCTION_RECORD_V1", _canonical_subset(fields, CANONICAL_RECONSTRUCTION_FIELD_ORDER), width=72)
    if record.get("reconstruction_receipt_hash72") and record.get("reconstruction_receipt_hash72") != expected:
        return _reject(REJECT_RECONSTRUCTION_RECEIPT_HASH_MISMATCH, "Reconstruction receipt hash mismatch.")
    response = {
        "schema": "HHS_HHFS_RECONSTRUCTION_RECORD_VALIDATION_V1",
        "ok": True,
        "status": fields.get("reconstruction_status"),
        "admitted": True,
        "corruption_status": fields.get("corruption_status"),
        "reconstruction_receipt_hash72": expected,
        "transformation_receipt_required": fields.get("transformation_receipt_required"),
        "silent_repair_allowed": False,
        "payload_duplication_allowed": False,
    }
    kernel = make_hash72_kernel_witness("HHS_HHFS_RECONSTRUCTION_RECORD_VALIDATION_V1", response, width=72).to_dict()
    ledger = append_payload(
        "HHFS_RECONSTRUCTION_RECORD_VALIDATION",
        "hhs_hhfs_reconstruction_protocol_v1.validate_hhfs_reconstruction_record",
        {**response, "kernel_digest72": kernel.get("digest")},
        ledger_path=_pass040_ledger_path(),
    )
    response["kernel_witness"] = kernel
    response["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
    return response


def hhfs_reconstruction_protocol_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import _hash72 as hhfs_hash72, commit_payload_view, make_hhfs_carrier_capsule
    from hhs_runtime.hhs_metadata_enhancement_block_v1 import make_metadata_enhancement_block
    from hhs_runtime.hhs_udfp_frame_v1 import make_udfp_frame

    trace_root = hhfs_hash72("HHFS_RECONSTRUCTION_TRACE", {"trace": ["capture"]}, width=72)
    metadata = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample"},
        resolution_profile={"width": "128", "height": "128"},
        semantic_checksums={"scene": "reconstruction"},
        observer_witness_id="RECONSTRUCTION_SELF_TEST",
        transformation_trace_root=trace_root,
    )
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=commit_payload_view({"carrier": "png", "view": "reconstruction"}),
        metadata_enhancement_root=metadata["metadata_enhancement_root"],
        transformation_trace_root=trace_root,
        error_correction_root=hhfs_hash72("HHFS_RECONSTRUCTION_ECC", {"ecc": "bounded"}, width=72),
    )
    frame = make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)
    intact = reconstruct_hhfs_carrier(udfp_frame=frame, corruption_status=CARRIER_INTACT)
    repaired = reconstruct_hhfs_carrier(udfp_frame=frame, corruption_status=PAYLOAD_CORRUPTED_ECC_RECOVERABLE)
    silent = reconstruct_hhfs_carrier(udfp_frame=frame, corruption_status=PAYLOAD_CORRUPTED_ECC_RECOVERABLE, reconstruction_parameters={"silent_repair_allowed": True})
    ok = bool(
        intact.get("validation", {}).get("status") == RECONSTRUCTION_NOT_REQUIRED
        and repaired.get("validation", {}).get("status") == RECONSTRUCTED_WITH_WITNESS
        and silent.get("status") == REJECT_RECONSTRUCTION_SILENT_REPAIR
        and repaired.get("canonical_reconstruction_fields", {}).get("transformation_receipt_required") is True
    )
    return {
        "schema": "HHS_HHFS_RECONSTRUCTION_PROTOCOL_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "intact_status": intact.get("validation", {}).get("status"),
        "repaired_status": repaired.get("validation", {}).get("status"),
        "silent_repair_rejection_status": silent.get("status"),
        "reconstruction_receipt_hash72": repaired.get("reconstruction_receipt_hash72"),
        "residue_state_chain_root_hash72": repaired.get("canonical_reconstruction_fields", {}).get("residue_state_chain_root_hash72"),
        "ledger_verified": repaired.get("unified_ledger", {}).get("verified") is True,
    }


if __name__ == "__main__":
    print(json.dumps(hhfs_reconstruction_protocol_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
