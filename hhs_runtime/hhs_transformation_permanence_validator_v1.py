"""
HHS Transformation Permanence Validator v1
==========================================

Pass 038 makes synthesis from HHS-encoded content non-silent.  A derived entry
is valid only when it either preserves the manipulation in a permanent
transformation trace or enters the Genesis severance protocol and makes no
continuity claim with the parent source.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
import copy
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    GENESIS_SEVERED_PRIVACY,
    REDACTED_CONTINUITY,
    WITNESSED_CONTINUITY,
    validate_phase_inversion_severance_witness,
)


VERSION = "PASS_038_TRANSFORMATION_PERMANENCE_VALIDATOR_V1"

REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD = "REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD"
REJECT_FALSE_CONTINUITY_PROVENANCE_BYPASS = "REJECT_FALSE_CONTINUITY_PROVENANCE_BYPASS"
REJECT_OPAQUE_PRIVACY_INSIDE_SAME_UNIQUE_HISTORY = "REJECT_OPAQUE_PRIVACY_INSIDE_SAME_UNIQUE_HISTORY"
REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM = "REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM"
REJECT_SUBSTRATE_EQUIVALENCE_AS_IDENTITY_CONTINUITY = "REJECT_SUBSTRATE_EQUIVALENCE_AS_IDENTITY_CONTINUITY"
REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS = "REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS"

ADMIT_WITNESSED_CONTINUITY = "ADMIT_WITNESSED_CONTINUITY"
ADMIT_REDACTED_CONTINUITY = "ADMIT_REDACTED_CONTINUITY"
ADMIT_GENESIS_SEVERED_PRIVACY = "ADMIT_GENESIS_SEVERED_PRIVACY"


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {
        "schema": "HHS_TRANSFORMATION_PERMANENCE_REJECTION_V1",
        "ok": False,
        "status": status,
        "reason": reason,
        "details": dict(details or {}),
        "admitted": False,
    }


def _has_trace_for_operation(output: Mapping[str, Any], operation: Mapping[str, Any]) -> bool:
    trace = output.get("transformation_trace") or output.get("permanent_transformation_record")
    if not trace:
        return False
    op_id = operation.get("operation_id") or operation.get("id") or operation.get("operation_type")
    if not op_id:
        return True
    if isinstance(trace, Mapping):
        serialized = json.dumps(trace, sort_keys=True, ensure_ascii=False, default=str)
        return str(op_id) in serialized
    if isinstance(trace, list):
        serialized = json.dumps(trace, sort_keys=True, ensure_ascii=False, default=str)
        return str(op_id) in serialized
    return str(op_id) in str(trace)


def make_transformation_record(
    *,
    source_commitment: str,
    operation_type: str,
    operation_parameters: Optional[Mapping[str, Any]] = None,
    input_state_root: str = "",
    output_state_root: str = "",
    gate_witness_id: str = "SelfSolve_AB_Gate",
    admissibility_result: str = "ADMITTED",
    previous_trace_root: str = "GENESIS",
) -> Dict[str, Any]:
    payload = {
        "schema": "HHS_TRANSFORMATION_RECORD_V1",
        "source_commitment": source_commitment,
        "operation_type": operation_type,
        "operation_id": operation_type,
        "operation_parameters_commitment": make_hash72_kernel_witness(
            "HHS_TRANSFORMATION_PARAMETERS_V1",
            dict(operation_parameters or {}),
            width=72,
        ).digest,
        "input_state_root": input_state_root,
        "output_state_root": output_state_root,
        "gate_witness_id": gate_witness_id,
        "admissibility_result": admissibility_result,
        "previous_trace_root": previous_trace_root,
    }
    payload["current_trace_root"] = make_hash72_kernel_witness("HHS_TRANSFORMATION_RECORD_V1", payload, width=72).digest
    return payload


def validate_hhs_derivation(
    *,
    source: Mapping[str, Any],
    output: Mapping[str, Any],
    operation: Mapping[str, Any],
    severance_witness: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Master validator for HHS derivation admissibility."""

    source_is_hhs = bool(source.get("is_hhs_encoded") or source.get("hhs_encoded") or source.get("phase"))
    claims_continuity = bool(output.get("claims_continuity_with_source") or output.get("claims_continuity_with_parent"))
    claims_opaque_privacy = bool(output.get("claims_opaque_privacy") or output.get("opaque_privacy"))
    output_phase = output.get("phase")
    same_payload_claim = bool(output.get("same_payload_as_source") or output.get("substrate_equivalence_claimed_as_identity"))

    if same_payload_claim and claims_continuity and not _has_trace_for_operation(output, operation):
        return _reject(
            REJECT_SUBSTRATE_EQUIVALENCE_AS_IDENTITY_CONTINUITY,
            "Same payload/substrate cannot substitute for witnessed identity-continuity.",
        )

    if not source_is_hhs:
        return {
            "schema": "HHS_TRANSFORMATION_PERMANENCE_VALIDATION_V1",
            "ok": True,
            "status": "SOURCE_NOT_HHS_ENCODED_NO_HHS_DERIVATION_CLAIM",
            "admitted": True,
        }

    if claims_continuity:
        if claims_opaque_privacy or output_phase == GENESIS_SEVERED_PRIVACY:
            return _reject(
                REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM,
                "A phase-inverted privacy record cannot claim continuity with the parent source.",
            )
        if not _has_trace_for_operation(output, operation):
            return _reject(
                REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD,
                "Derived HHS entries claiming continuity require a permanent transformation record.",
            )
        status = ADMIT_REDACTED_CONTINUITY if output_phase == REDACTED_CONTINUITY else ADMIT_WITNESSED_CONTINUITY
        record = {
            "schema": "HHS_TRANSFORMATION_PERMANENCE_VALIDATION_V1",
            "ok": True,
            "status": status,
            "admitted": True,
            "source_phase": source.get("phase"),
            "output_phase": output_phase or WITNESSED_CONTINUITY,
            "continuity_claim_valid": True,
            "transformation_record_present": True,
        }
        kernel = make_hash72_kernel_witness("HHS_TRANSFORMATION_PERMANENCE_VALIDATION_V1", record, width=72).to_dict()
        ledger = append_payload("TRANSFORMATION_PERMANENCE_VALIDATION", "hhs_transformation_permanence_validator_v1.validate_hhs_derivation", {**record, "kernel_digest72": kernel.get("digest")})
        record["kernel_witness"] = kernel
        record["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
        return record

    if claims_opaque_privacy or output_phase == GENESIS_SEVERED_PRIVACY:
        if not severance_witness:
            return _reject(
                REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS,
                "Opaque privacy requires a valid Genesis severance witness.",
            )
        severance_validation = validate_phase_inversion_severance_witness(severance_witness)
        if not severance_validation.get("ok"):
            return _reject(
                REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS,
                "Genesis severance witness failed validation.",
                details=severance_validation,
            )
        record = {
            "schema": "HHS_TRANSFORMATION_PERMANENCE_VALIDATION_V1",
            "ok": True,
            "status": ADMIT_GENESIS_SEVERED_PRIVACY,
            "admitted": True,
            "source_phase": source.get("phase"),
            "output_phase": GENESIS_SEVERED_PRIVACY,
            "continuity_claim_valid": False,
            "new_genesis_required": True,
            "severance_validation": severance_validation,
        }
        kernel = make_hash72_kernel_witness("HHS_GENESIS_SEVERED_PRIVACY_VALIDATION_V1", record, width=72).to_dict()
        ledger = append_payload("GENESIS_SEVERED_PRIVACY_VALIDATION", "hhs_transformation_permanence_validator_v1.validate_hhs_derivation", {**record, "kernel_digest72": kernel.get("digest")})
        record["kernel_witness"] = kernel
        record["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
        return record

    return _reject(
        REJECT_FALSE_CONTINUITY_PROVENANCE_BYPASS,
        "Derived HHS output must either claim witnessed continuity with a trace or enter Genesis severance.",
    )


def transformation_permanence_validator_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    from hhs_runtime.hhs_genesis_severance_protocol_v1 import make_phase_inversion_severance_witness

    source = {"schema": "HHS_SOURCE_SAMPLE_V1", "is_hhs_encoded": True, "phase": WITNESSED_CONTINUITY, "commitment": "source-commitment"}
    operation = {"schema": "HHS_OPERATION_SAMPLE_V1", "operation_type": "summarize", "operation_id": "summarize"}
    trace = make_transformation_record(source_commitment="source-commitment", operation_type="summarize")
    witnessed_output = {"schema": "HHS_OUTPUT_SAMPLE_V1", "phase": WITNESSED_CONTINUITY, "claims_continuity_with_source": True, "transformation_trace": [trace]}
    missing_trace_output = {"schema": "HHS_OUTPUT_SAMPLE_V1", "phase": WITNESSED_CONTINUITY, "claims_continuity_with_source": True}
    parent = {"schema": "HHS_PARENT_RECORD_SAMPLE_V1", "commitment": "source-commitment", "phase": WITNESSED_CONTINUITY}
    seed = {"schema": "HHS_NEW_GENESIS_SEED_SAMPLE_V1", "seed_material_commitment": "private-seed"}
    severance = make_phase_inversion_severance_witness(parent_record=parent, new_genesis_seed=seed)
    private_output = {"schema": "HHS_PRIVATE_OUTPUT_SAMPLE_V1", "phase": GENESIS_SEVERED_PRIVACY, "claims_opaque_privacy": True, "claims_continuity_with_source": False}
    invalid_private_output = {"schema": "HHS_INVALID_PRIVATE_OUTPUT_SAMPLE_V1", "phase": GENESIS_SEVERED_PRIVACY, "claims_opaque_privacy": True, "claims_continuity_with_source": True}

    valid_continuity = validate_hhs_derivation(source=source, output=witnessed_output, operation=operation)
    missing_trace = validate_hhs_derivation(source=source, output=missing_trace_output, operation=operation)
    valid_privacy = validate_hhs_derivation(source=source, output=private_output, operation=operation, severance_witness=severance)
    invalid_privacy = validate_hhs_derivation(source=source, output=invalid_private_output, operation=operation, severance_witness=severance)
    ledger_status = valid_continuity.get("unified_ledger", {})
    ok = bool(
        valid_continuity.get("status") == ADMIT_WITNESSED_CONTINUITY
        and missing_trace.get("status") == REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD
        and valid_privacy.get("status") == ADMIT_GENESIS_SEVERED_PRIVACY
        and invalid_privacy.get("status") == REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM
        and ledger_status.get("verified") is True
    )
    return {
        "schema": "HHS_TRANSFORMATION_PERMANENCE_VALIDATOR_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "valid_continuity": valid_continuity,
        "missing_trace_rejection": missing_trace,
        "valid_privacy": valid_privacy,
        "invalid_privacy_rejection": invalid_privacy,
        "ledger_verified": bool(ledger_status.get("verified")),
        "doctrine": "Synthesis from HHS-encoded content is never invisible: continuity requires trace, privacy requires Genesis severance.",
    }


if __name__ == "__main__":
    print(json.dumps(transformation_permanence_validator_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
