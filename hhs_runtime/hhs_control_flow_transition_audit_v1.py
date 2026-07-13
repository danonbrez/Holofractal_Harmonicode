"""
HHS Control-Flow Transition Audit v1
====================================

Pass 041 control-flow repair layer.

Previous IF/LOOP gates could lock scalar proxy audits while the actual branch or
loop step returned richer state transitions.  This module commits the complete
pre-state, post-state, result projection, and transition receipt before a gate
may be treated as locked.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_validation_residue_compressor_v1 import make_validation_residue_state_chain, validate_validation_residue_state_chain

VERSION = "PASS_041_CONTROL_FLOW_TRANSITION_AUDIT_V1"
TRANSITION_SCHEMA = "HHS_CONTROL_FLOW_TRANSITION_AUDIT_V1"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"
STATE_MACHINE = "u^72_hash72_multimodal_state_machine"

ADMIT_CONTROL_FLOW_TRANSITION_AUDIT = "ADMIT_CONTROL_FLOW_TRANSITION_AUDIT"
REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY = "REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY"
REJECT_CONTROL_FLOW_FLOAT_STATE = "REJECT_CONTROL_FLOW_FLOAT_STATE"
REJECT_CONTROL_FLOW_RAW_TRANSITION_CACHE = "REJECT_CONTROL_FLOW_RAW_TRANSITION_CACHE"
REJECT_CONTROL_FLOW_TRANSITION_HASH_MISMATCH = "REJECT_CONTROL_FLOW_TRANSITION_HASH_MISMATCH"
REJECT_CONTROL_FLOW_MISSING_RESIDUE_CHAIN = "REJECT_CONTROL_FLOW_MISSING_RESIDUE_CHAIN"

FORBIDDEN_TRANSITION_FIELDS = {
    "scalar_proxy_only",
    "raw_cache",
    "expansion_cache",
    "validation_expansion_cache",
    "unbounded_diagnostic_trace",
    "parallel_memory",
    "shadow_memory",
}

CANONICAL_TRANSITION_AUDIT_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "gate",
    "label",
    "transition_index",
    "decision",
    "pre_state_hash72",
    "post_state_hash72",
    "result_hash72",
    "condition_hash72",
    "variant_hash72",
    "transition_root_hash72",
    "scalar_proxy_used",
    "rich_transition_audited",
    "residue_chain_root_hash72",
    "state_machine",
    "hash_authority",
)


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {"schema": "HHS_CONTROL_FLOW_TRANSITION_AUDIT_REJECTION_V1", "version": VERSION, "ok": False, "status": status, "reason": reason, "details": dict(details or {})}


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_float(v) for v in value)
    return False


def _contains_forbidden_key(value: Any, forbidden: Iterable[str]) -> Optional[str]:
    forbidden_set = set(forbidden)
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in forbidden_set:
                return str(key)
            nested = _contains_forbidden_key(item, forbidden_set)
            if nested:
                return nested
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            nested = _contains_forbidden_key(item, forbidden_set)
            if nested:
                return nested
    return None


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    if isinstance(value, set):
        return sorted(_canonical(v) for v in value)
    return value


def _hash72(label: str, value: Any) -> str:
    return make_hash72_kernel_witness(label, _canonical(value), width=72).digest


def _canonical_subset(fields: Mapping[str, Any], order: Tuple[str, ...]) -> Dict[str, Any]:
    return {key: fields.get(key) for key in order}


@dataclass(frozen=True)
class HHSControlFlowTransitionAudit:
    schema: str
    version: str
    ok: bool
    status: str
    canonical_transition_fields: Dict[str, Any]
    residue_chain: Dict[str, Any]
    kernel_witness: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def make_control_flow_transition_audit(
    *,
    gate: str,
    label: str,
    transition_index: int,
    pre_state: Any,
    post_state: Any,
    result: Any,
    decision: str,
    condition: Optional[Any] = None,
    variant: Optional[Any] = None,
    source_receipt_hash72: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "gate": gate,
        "label": label,
        "transition_index": transition_index,
        "pre_state": pre_state,
        "post_state": post_state,
        "result": result,
        "decision": decision,
        "condition": condition,
        "variant": variant,
    }
    if _contains_float(payload):
        raise ValueError("control-flow transition audits reject floats; use exact rational/symbolic state projections")
    forbidden = _contains_forbidden_key(payload, FORBIDDEN_TRANSITION_FIELDS)
    if forbidden:
        raise ValueError(f"control-flow transition audit cannot retain raw/proxy-only field: {forbidden}")

    pre_hash = _hash72("HHS_CONTROL_FLOW_PRE_STATE_V1", pre_state)
    post_hash = _hash72("HHS_CONTROL_FLOW_POST_STATE_V1", post_state)
    result_hash = _hash72("HHS_CONTROL_FLOW_RESULT_V1", result)
    condition_hash = _hash72("HHS_CONTROL_FLOW_CONDITION_V1", condition if condition is not None else "NO_CONDITION")
    variant_hash = _hash72("HHS_CONTROL_FLOW_VARIANT_V1", variant if variant is not None else "NO_VARIANT")
    transition_core = {
        "gate": str(gate),
        "label": str(label),
        "transition_index": int(transition_index),
        "decision": str(decision),
        "pre_state_hash72": pre_hash,
        "post_state_hash72": post_hash,
        "result_hash72": result_hash,
        "condition_hash72": condition_hash,
        "variant_hash72": variant_hash,
    }
    transition_root = _hash72("HHS_CONTROL_FLOW_FULL_STATE_TRANSITION_V1", transition_core)
    residue_chain = make_validation_residue_state_chain([
        {
            "residue_class": "control_flow_transition_audit",
            "modality_type": "runtime_control_flow",
            "validation_surface": f"control_flow.{str(gate).lower()}",
            "validation_status": "full_state_transition_audited",
            "source_receipt_hash72": source_receipt_hash72 or transition_root,
            "transition_root_hash72": transition_root,
        }
    ], previous_state_root=pre_hash)
    residue_validation = validate_validation_residue_state_chain(residue_chain)
    if not residue_validation.get("ok"):
        raise ValueError("control-flow transition residue chain failed validation")

    fields = {
        "schema": TRANSITION_SCHEMA,
        "version": VERSION,
        **transition_core,
        "transition_root_hash72": transition_root,
        "scalar_proxy_used": False,
        "rich_transition_audited": True,
        "residue_chain_root_hash72": residue_chain.get("chain_root_hash72"),
        "state_machine": STATE_MACHINE,
        "hash_authority": HASH72_AUTHORITY,
    }
    canonical_fields = _canonical_subset(fields, CANONICAL_TRANSITION_AUDIT_FIELD_ORDER)
    kernel = make_hash72_kernel_witness("HHS_CONTROL_FLOW_TRANSITION_AUDIT_V1", canonical_fields, width=72).to_dict()
    audit = HHSControlFlowTransitionAudit(
        schema=TRANSITION_SCHEMA,
        version=VERSION,
        ok=True,
        status=ADMIT_CONTROL_FLOW_TRANSITION_AUDIT,
        canonical_transition_fields=canonical_fields,
        residue_chain=residue_chain,
        kernel_witness=kernel,
    ).to_dict()
    validation = validate_control_flow_transition_audit(audit)
    if not validation.get("ok"):
        raise ValueError(validation.get("status", "control-flow transition audit validation failed"))
    audit["validation"] = validation
    return audit


def validate_control_flow_transition_audit(audit: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(audit):
        return _reject(REJECT_CONTROL_FLOW_FLOAT_STATE, "Control-flow transition audits reject floats.")
    forbidden = _contains_forbidden_key(audit, FORBIDDEN_TRANSITION_FIELDS)
    if forbidden:
        return _reject(REJECT_CONTROL_FLOW_RAW_TRANSITION_CACHE, "Control-flow transition audit cannot retain raw cache or proxy-only fields.", details={"field": forbidden})
    fields = audit.get("canonical_transition_fields", {})
    if not isinstance(fields, Mapping):
        return _reject(REJECT_CONTROL_FLOW_TRANSITION_HASH_MISMATCH, "Missing canonical transition fields.")
    if bool(fields.get("scalar_proxy_used")) or not bool(fields.get("rich_transition_audited")):
        return _reject(REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY, "Control-flow gates cannot lock from scalar proxy audits alone.")
    expected_transition = _hash72(
        "HHS_CONTROL_FLOW_FULL_STATE_TRANSITION_V1",
        {
            "gate": fields.get("gate"),
            "label": fields.get("label"),
            "transition_index": fields.get("transition_index"),
            "decision": fields.get("decision"),
            "pre_state_hash72": fields.get("pre_state_hash72"),
            "post_state_hash72": fields.get("post_state_hash72"),
            "result_hash72": fields.get("result_hash72"),
            "condition_hash72": fields.get("condition_hash72"),
            "variant_hash72": fields.get("variant_hash72"),
        },
    )
    if str(fields.get("transition_root_hash72")) != expected_transition:
        return _reject(REJECT_CONTROL_FLOW_TRANSITION_HASH_MISMATCH, "Full-state transition root mismatch.")
    residue_chain = audit.get("residue_chain")
    if not isinstance(residue_chain, Mapping):
        return _reject(REJECT_CONTROL_FLOW_MISSING_RESIDUE_CHAIN, "Control-flow transition audit requires compressed residue chain.")
    residue_validation = validate_validation_residue_state_chain(residue_chain)
    if not residue_validation.get("ok"):
        return _reject(REJECT_CONTROL_FLOW_MISSING_RESIDUE_CHAIN, "Control-flow transition residue chain failed validation.", details={"status": residue_validation.get("status")})
    if str(fields.get("residue_chain_root_hash72")) != str(residue_chain.get("chain_root_hash72")):
        return _reject(REJECT_CONTROL_FLOW_TRANSITION_HASH_MISMATCH, "Residue chain root mismatch.")
    record = {
        "schema": "HHS_CONTROL_FLOW_TRANSITION_AUDIT_VALIDATION_V1",
        "version": VERSION,
        "ok": True,
        "status": ADMIT_CONTROL_FLOW_TRANSITION_AUDIT,
        "transition_root_hash72": fields.get("transition_root_hash72"),
        "residue_chain_root_hash72": fields.get("residue_chain_root_hash72"),
        "scalar_proxy_used": False,
        "rich_transition_audited": True,
        "state_machine": STATE_MACHINE,
    }
    record["kernel_witness"] = make_hash72_kernel_witness("HHS_CONTROL_FLOW_TRANSITION_AUDIT_VALIDATION_V1", record, width=72).to_dict()
    return record


def control_flow_transition_audit_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    audit = make_control_flow_transition_audit(
        gate="IF",
        label="SELF_TEST_IF",
        transition_index=0,
        pre_state={"condition": True, "branch": "THEN"},
        post_state={"result": {"value": "accepted", "state": {"x": 1}}},
        result={"value": "accepted", "state": {"x": 1}},
        decision="THEN_SELECTED",
        condition=True,
    )
    bad = dict(audit)
    bad["canonical_transition_fields"] = dict(audit["canonical_transition_fields"])
    bad["canonical_transition_fields"]["scalar_proxy_used"] = True
    rejected = validate_control_flow_transition_audit(bad)
    ok = bool(audit.get("status") == ADMIT_CONTROL_FLOW_TRANSITION_AUDIT and rejected.get("status") == REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY)
    return {
        "schema": "HHS_CONTROL_FLOW_TRANSITION_AUDIT_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "valid_status": audit.get("status"),
        "scalar_proxy_rejection_status": rejected.get("status"),
        "transition_root_hash72": audit.get("canonical_transition_fields", {}).get("transition_root_hash72"),
        "residue_chain_root_hash72": audit.get("canonical_transition_fields", {}).get("residue_chain_root_hash72"),
        "state_machine": STATE_MACHINE,
    }


if __name__ == "__main__":
    print(json.dumps(control_flow_transition_audit_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
