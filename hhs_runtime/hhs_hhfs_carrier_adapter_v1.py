"""
HHS HHFS Carrier Adapter v1
===========================

Pass 040 treats carrier read/write/extract/embed/repair operations as witnessed
adapter transitions, not loose IO helpers.  A bound carrier operation must be
derivable from HHFS/UDFP invariants, validate the UDFP frame, and emit a
Hash72/u^72 previous->state->receipt record.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path
from hhs_runtime.hhs_udfp_frame_v1 import ADMIT_UDFP_FRAME, validate_udfp_frame
from hhs_runtime.hhs_transformation_permanence_validator_v1 import (
    ADMIT_WITNESSED_CONTINUITY,
    make_transformation_record,
    validate_hhs_derivation,
)
from hhs_runtime.hhs_genesis_severance_protocol_v1 import WITNESSED_CONTINUITY
from hhs_runtime.hhs_validation_residue_compressor_v1 import (
    ADMIT_VALIDATION_RESIDUE_STATE_CHAIN,
    GENESIS_STATE_ROOT,
    make_validation_residue_state_chain,
    validate_validation_residue_state_chain,
)


VERSION = "PASS_040_HHFS_CARRIER_ADAPTER_V1"
ADAPTER_RECORD_SCHEMA = "HHS_HHFS_CARRIER_ADAPTER_RECORD_V1"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"

OBSERVATION_OPERATIONS = {"read", "observe", "verify", "extract"}
MUTATION_OPERATIONS = {"write", "embed", "repair", "reconstruct", "convert"}
ALLOWED_OPERATIONS = OBSERVATION_OPERATIONS | MUTATION_OPERATIONS

ADMIT_HHFS_CARRIER_ADAPTER_OPERATION = "ADMIT_HHFS_CARRIER_ADAPTER_OPERATION"
REJECT_HHFS_ADAPTER_FLOAT = "REJECT_HHFS_ADAPTER_FLOAT"
REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION = "REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION"
REJECT_HHFS_ADAPTER_INVALID_UDFP_FRAME = "REJECT_HHFS_ADAPTER_INVALID_UDFP_FRAME"
REJECT_HHFS_ADAPTER_MISSING_TRANSFORMATION_RECORD = "REJECT_HHFS_ADAPTER_MISSING_TRANSFORMATION_RECORD"
REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH = "REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH"
REJECT_HHFS_ADAPTER_RESIDUE_CHAIN_INVALID = "REJECT_HHFS_ADAPTER_RESIDUE_CHAIN_INVALID"

CANONICAL_ADAPTER_RECORD_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "operation",
    "operation_class",
    "carrier_type",
    "modality_type",
    "payload_commitment",
    "previous_frame_root",
    "current_frame_root",
    "adapter_state_root_hash72",
    "transformation_trace_required",
    "transformation_record_hash72",
    "residue_state_chain_root_hash72",
    "legacy_compatibility_preserved",
    "no_parallel_storage",
    "no_parallel_computation",
    "hash_authority",
)


def _pass040_ledger_path():
    return runtime_artifact_path("hhs_pass040_carrier_adapter_ledger.json")


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {"schema": "HHS_HHFS_CARRIER_ADAPTER_REJECTION_V1", "ok": False, "status": status, "reason": reason, "details": dict(details or {})}


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
class HHFSCarrierAdapterRecord:
    schema: str
    version: str
    canonical_adapter_fields: Dict[str, Any]
    adapter_receipt_hash72: str
    udfp_validation: Dict[str, Any]
    residue_state_chain: Dict[str, Any]
    transformation_validation: Optional[Dict[str, Any]]
    kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _operation_class(operation: str) -> str:
    return "observation" if operation in OBSERVATION_OPERATIONS else "mutation"


def canonical_adapter_record_fields(
    *,
    operation: str,
    udfp_frame: Mapping[str, Any],
    residue_state_chain_root_hash72: str,
    transformation_record_hash72: str = "NO_TRANSFORMATION_RECORD_REQUIRED",
) -> Dict[str, Any]:
    operation = str(operation).strip().lower()
    frame_fields = udfp_frame.get("canonical_frame_fields", {})
    current_frame_root = str(udfp_frame.get("current_frame_root", frame_fields.get("current_frame_root", "NO_FRAME_ROOT")))
    previous_frame_root = str(frame_fields.get("previous_frame_root", "GENESIS_FRAME_ROOT"))
    state_basis = {
        "operation": operation,
        "operation_class": _operation_class(operation),
        "previous_frame_root": previous_frame_root,
        "current_frame_root": current_frame_root,
        "payload_commitment": str(frame_fields.get("payload_commitment")),
        "residue_state_chain_root_hash72": str(residue_state_chain_root_hash72),
    }
    state_root = _hash72("HHS_HHFS_CARRIER_ADAPTER_STATE_V1", state_basis, width=72)
    fields = {
        "schema": ADAPTER_RECORD_SCHEMA,
        "version": VERSION,
        "operation": operation,
        "operation_class": _operation_class(operation),
        "carrier_type": str(frame_fields.get("carrier_type")),
        "modality_type": str(frame_fields.get("modality_type")),
        "payload_commitment": str(frame_fields.get("payload_commitment")),
        "previous_frame_root": previous_frame_root,
        "current_frame_root": current_frame_root,
        "adapter_state_root_hash72": state_root,
        "transformation_trace_required": operation in MUTATION_OPERATIONS,
        "transformation_record_hash72": str(transformation_record_hash72),
        "residue_state_chain_root_hash72": str(residue_state_chain_root_hash72),
        "legacy_compatibility_preserved": True,
        "no_parallel_storage": True,
        "no_parallel_computation": True,
        "hash_authority": HASH72_AUTHORITY,
    }
    return _canonical_subset(fields, CANONICAL_ADAPTER_RECORD_FIELD_ORDER)


def execute_hhfs_carrier_adapter_operation(
    *,
    operation: str,
    udfp_frame: Mapping[str, Any],
    operation_parameters: Optional[Mapping[str, Any]] = None,
    previous_residue_state_root: str = GENESIS_STATE_ROOT,
) -> Dict[str, Any]:
    operation = str(operation).strip().lower()
    operation_parameters = dict(operation_parameters or {})
    if _contains_float({"operation_parameters": operation_parameters, "udfp_frame": udfp_frame}):
        return _reject(REJECT_HHFS_ADAPTER_FLOAT, "Carrier adapter operations reject floats; use exact symbolic/rational values.")
    if operation not in ALLOWED_OPERATIONS:
        return _reject(REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION, "Unsupported HHFS carrier adapter operation.", details={"operation": operation})

    udfp_validation = validate_udfp_frame(udfp_frame)
    if udfp_validation.get("status") != ADMIT_UDFP_FRAME:
        return _reject(REJECT_HHFS_ADAPTER_INVALID_UDFP_FRAME, "Carrier adapter requires a valid UDFP frame.", details=udfp_validation)

    frame_fields = udfp_frame.get("canonical_frame_fields", {})
    transformation_validation: Optional[Dict[str, Any]] = None
    transformation_record_hash72 = "NO_TRANSFORMATION_RECORD_REQUIRED"

    if operation in MUTATION_OPERATIONS:
        trace_record = operation_parameters.get("transformation_record")
        if not isinstance(trace_record, Mapping):
            trace_record = make_transformation_record(
                source_commitment=str(frame_fields.get("payload_commitment")),
                operation_type=f"carrier_adapter.{operation}",
                operation_parameters=operation_parameters,
            )
        transformation_record_hash72 = _hash72("HHS_HHFS_ADAPTER_TRANSFORMATION_RECORD_V1", trace_record, width=72)
        source = {"schema": "HHS_HHFS_ADAPTER_SOURCE_V1", "is_hhs_encoded": True, "commitment": frame_fields.get("payload_commitment")}
        output = {
            "schema": "HHS_HHFS_ADAPTER_OUTPUT_V1",
            "phase": WITNESSED_CONTINUITY,
            "claims_continuity_with_source": True,
            "transformation_trace": [trace_record],
        }
        transformation_validation = validate_hhs_derivation(source=source, output=output, operation={"operation_type": f"carrier_adapter.{operation}"})
        if transformation_validation.get("status") != ADMIT_WITNESSED_CONTINUITY:
            return _reject(REJECT_HHFS_ADAPTER_MISSING_TRANSFORMATION_RECORD, "Mutating carrier adapter operations require permanent transformation records.", details=transformation_validation)

    residue_chain = make_validation_residue_state_chain(
        [
            {
                "residue_class": "hhfs_carrier_adapter_validation",
                "modality_type": frame_fields.get("modality_type", "multimodal"),
                "validation_surface": f"hhfs_carrier_adapter.{operation}",
                "validation_status": "admitted",
                "source_receipt_hash72": udfp_validation.get("current_frame_root", udfp_frame.get("current_frame_root", "NO_FRAME_RECEIPT")),
            }
        ],
        previous_state_root=previous_residue_state_root,
    )
    residue_validation = validate_validation_residue_state_chain(residue_chain)
    if residue_validation.get("status") != ADMIT_VALIDATION_RESIDUE_STATE_CHAIN:
        return _reject(REJECT_HHFS_ADAPTER_RESIDUE_CHAIN_INVALID, "Adapter validation residue failed previous/state/receipt compression.", details=residue_validation)

    fields = canonical_adapter_record_fields(
        operation=operation,
        udfp_frame=udfp_frame,
        residue_state_chain_root_hash72=residue_chain["chain_root_hash72"],
        transformation_record_hash72=transformation_record_hash72,
    )
    kernel = make_hash72_kernel_witness("HHS_HHFS_CARRIER_ADAPTER_RECORD_V1", fields, width=72).to_dict()
    ledger = append_payload(
        "HHFS_CARRIER_ADAPTER_OPERATION",
        f"hhs_hhfs_carrier_adapter_v1.{operation}",
        {"canonical_adapter_fields": fields, "adapter_receipt_hash72": kernel.get("digest")},
        ledger_path=_pass040_ledger_path(),
    )
    record = HHFSCarrierAdapterRecord(
        schema=ADAPTER_RECORD_SCHEMA,
        version=VERSION,
        canonical_adapter_fields=fields,
        adapter_receipt_hash72=str(kernel.get("digest")),
        udfp_validation=udfp_validation,
        residue_state_chain=residue_chain,
        transformation_validation=transformation_validation,
        kernel_witness=kernel,
        unified_ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
    ).to_dict()
    validation = validate_hhfs_carrier_adapter_record(record)
    if not validation.get("ok"):
        return validation
    record["validation"] = validation
    return record


def validate_hhfs_carrier_adapter_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(record):
        return _reject(REJECT_HHFS_ADAPTER_FLOAT, "Carrier adapter records reject floats.")
    fields = record.get("canonical_adapter_fields", {})
    if not isinstance(fields, Mapping):
        return _reject(REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH, "Missing canonical adapter fields.")
    if fields.get("operation") not in ALLOWED_OPERATIONS:
        return _reject(REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION, "Unsupported operation in adapter record.")
    if not bool(fields.get("legacy_compatibility_preserved")) or not bool(fields.get("no_parallel_storage")) or not bool(fields.get("no_parallel_computation")):
        return _reject(REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH, "Adapter records must preserve legacy compatibility and no-parallel-lane policy.")
    if fields.get("operation") in MUTATION_OPERATIONS and fields.get("transformation_record_hash72") == "NO_TRANSFORMATION_RECORD_REQUIRED":
        return _reject(REJECT_HHFS_ADAPTER_MISSING_TRANSFORMATION_RECORD, "Mutating adapter record is missing transformation record hash.")
    residue_validation = validate_validation_residue_state_chain(record.get("residue_state_chain", {}))
    if residue_validation.get("status") != ADMIT_VALIDATION_RESIDUE_STATE_CHAIN:
        return _reject(REJECT_HHFS_ADAPTER_RESIDUE_CHAIN_INVALID, "Adapter residue state chain is invalid.", details=residue_validation)
    expected = _hash72("HHS_HHFS_CARRIER_ADAPTER_RECORD_V1", _canonical_subset(fields, CANONICAL_ADAPTER_RECORD_FIELD_ORDER), width=72)
    if record.get("adapter_receipt_hash72") and record.get("adapter_receipt_hash72") != expected:
        return _reject(REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH, "Adapter receipt hash mismatch.")
    response = {
        "schema": "HHS_HHFS_CARRIER_ADAPTER_RECORD_VALIDATION_V1",
        "ok": True,
        "status": ADMIT_HHFS_CARRIER_ADAPTER_OPERATION,
        "admitted": True,
        "operation": fields.get("operation"),
        "operation_class": fields.get("operation_class"),
        "adapter_receipt_hash72": expected,
        "residue_state_chain_root_hash72": fields.get("residue_state_chain_root_hash72"),
        "legacy_compatibility_preserved": True,
        "no_parallel_storage": True,
        "no_parallel_computation": True,
    }
    kernel = make_hash72_kernel_witness("HHS_HHFS_CARRIER_ADAPTER_RECORD_VALIDATION_V1", response, width=72).to_dict()
    ledger = append_payload(
        "HHFS_CARRIER_ADAPTER_RECORD_VALIDATION",
        "hhs_hhfs_carrier_adapter_v1.validate_hhfs_carrier_adapter_record",
        {**response, "kernel_digest72": kernel.get("digest")},
        ledger_path=_pass040_ledger_path(),
    )
    response["kernel_witness"] = kernel
    response["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
    return response


def hhfs_carrier_adapter_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import _hash72 as hhfs_hash72, commit_payload_view, make_hhfs_carrier_capsule
    from hhs_runtime.hhs_metadata_enhancement_block_v1 import make_metadata_enhancement_block
    from hhs_runtime.hhs_udfp_frame_v1 import make_udfp_frame

    trace_root = hhfs_hash72("HHFS_ADAPTER_SAMPLE_TRACE", {"trace": ["capture"]}, width=72)
    metadata = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample"},
        resolution_profile={"width": "64", "height": "64"},
        semantic_checksums={"scene": "adapter"},
        observer_witness_id="ADAPTER_SELF_TEST",
        transformation_trace_root=trace_root,
    )
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=commit_payload_view({"carrier": "png", "view": "adapter"}),
        metadata_enhancement_root=metadata["metadata_enhancement_root"],
        transformation_trace_root=trace_root,
        error_correction_root=hhfs_hash72("HHFS_ADAPTER_ECC", {"ecc": "bounded"}, width=72),
    )
    frame = make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)
    read_record = execute_hhfs_carrier_adapter_operation(operation="read", udfp_frame=frame)
    repair_record = execute_hhfs_carrier_adapter_operation(operation="repair", udfp_frame=frame, operation_parameters={"reason": "self_test_reconstruction"})
    invalid = execute_hhfs_carrier_adapter_operation(operation="erase", udfp_frame=frame)
    ok = bool(
        read_record.get("validation", {}).get("status") == ADMIT_HHFS_CARRIER_ADAPTER_OPERATION
        and repair_record.get("validation", {}).get("status") == ADMIT_HHFS_CARRIER_ADAPTER_OPERATION
        and invalid.get("status") == REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION
        and repair_record.get("canonical_adapter_fields", {}).get("transformation_trace_required") is True
    )
    return {
        "schema": "HHS_HHFS_CARRIER_ADAPTER_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "read_status": read_record.get("validation", {}).get("status"),
        "repair_status": repair_record.get("validation", {}).get("status"),
        "invalid_status": invalid.get("status"),
        "adapter_receipt_hash72": repair_record.get("adapter_receipt_hash72"),
        "residue_state_chain_root_hash72": repair_record.get("canonical_adapter_fields", {}).get("residue_state_chain_root_hash72"),
        "ledger_verified": repair_record.get("unified_ledger", {}).get("verified") is True,
    }


if __name__ == "__main__":
    print(json.dumps(hhfs_carrier_adapter_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
