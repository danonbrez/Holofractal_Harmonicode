"""
HHS Kernel Conformance Decision v1
==================================

Pass 042 decision engine for determining whether a runtime surface is derived
from kernel invariants, bound to contracts/witnesses/validators/rejection paths,
and therefore eligible for canonical runtime reachability.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_invariant_registry_v1 import build_default_invariant_registry

VERSION = "PASS_042_KERNEL_DERIVED_CONFORMANCE_SURFACE_MAP_V1"
DECISION_SCHEMA = "HHS_SURFACE_CONFORMANCE_DECISION_V1"
DERIVATION_WITNESS_SCHEMA = "HHS_KERNEL_DERIVATION_WITNESS_V1"

ADMIT_KERNEL_DERIVED_SURFACE = "ADMIT_KERNEL_DERIVED_SURFACE"
ADMIT_MULTI_INVARIANT_DERIVATION = "ADMIT_MULTI_INVARIANT_DERIVATION"
ADMIT_DOCUMENTED_NONEXECUTABLE_SURFACE = "ADMIT_DOCUMENTED_NONEXECUTABLE_SURFACE"
QUARANTINE_INCOMPLETE_DERIVATION = "QUARANTINE_INCOMPLETE_DERIVATION"
REJECT_UNDERIVED_RUNTIME_SURFACE = "REJECT_UNDERIVED_RUNTIME_SURFACE"
REJECT_UNKNOWN_INVARIANT = "REJECT_UNKNOWN_INVARIANT"
REJECT_MISSING_WITNESS_BINDING = "REJECT_MISSING_WITNESS_BINDING"
REJECT_MISSING_VALIDATOR_BINDING = "REJECT_MISSING_VALIDATOR_BINDING"
REJECT_MISSING_REJECTION_PATH = "REJECT_MISSING_REJECTION_PATH"
REJECT_CIRCULAR_DERIVATION = "REJECT_CIRCULAR_DERIVATION"
REJECT_AMBIGUOUS_INVARIANT_OWNERSHIP = "REJECT_AMBIGUOUS_INVARIANT_OWNERSHIP"
REJECT_SCHEMA_SURFACE_MISMATCH = "REJECT_SCHEMA_SURFACE_MISMATCH"
REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY = "REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY"
REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT = "REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT"

MUTATING_POLICIES = {"LEDGER_MUTATION", "PERSISTENT_MUTATION", "CARRIER_MUTATION", "CONTROLLED_RUNTIME_MUTATION"}
DOCUMENTED_STATUSES = {"DOCUMENTED_NONEXECUTABLE", "DOCUMENTED_ONLY"}


def _list(values: Optional[Iterable[Any]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            out.append(text)
    return sorted(dict.fromkeys(out))


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def classify_derivation_failure(surface: Mapping[str, Any], registry=None) -> List[str]:
    registry = registry or build_default_invariant_registry()
    reasons: List[str] = []
    invariant_ids = _list(surface.get("invariant_ids"))
    if surface.get("status") in DOCUMENTED_STATUSES or surface.get("surface_type") == "DOCUMENTED_NONEXECUTABLE":
        return reasons
    if not invariant_ids:
        reasons.append(REJECT_UNDERIVED_RUNTIME_SURFACE)
    for iid in invariant_ids:
        try:
            registry.get_invariant(iid)
            registry.resolve_invariant_dependencies(iid)
        except KeyError:
            reasons.append(f"{REJECT_UNKNOWN_INVARIANT}:{iid}")
        except Exception:
            reasons.append(f"{REJECT_CIRCULAR_DERIVATION}:{iid}")
    if not _list(surface.get("witness_schemas")):
        reasons.append(REJECT_MISSING_WITNESS_BINDING)
    if not _list(surface.get("validators")):
        reasons.append(REJECT_MISSING_VALIDATOR_BINDING)
    if not _list(surface.get("rejection_codes")):
        reasons.append(REJECT_MISSING_REJECTION_PATH)
    if not _list(surface.get("contract_schemas")) and not str(surface.get("contract_exempt_reason", "")).strip():
        reasons.append(REJECT_SCHEMA_SURFACE_MISMATCH)
    mutation_policy = str(surface.get("mutation_policy", "NO_EXTERNAL_STATE_MUTATION"))
    if mutation_policy in MUTATING_POLICIES and not str(surface.get("persistence_policy", "")).strip():
        reasons.append(REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY)
    return reasons


def emit_conformance_decision(surface: Mapping[str, Any], reasons: List[str], *, registry=None) -> Dict[str, Any]:
    invariant_ids = _list(surface.get("invariant_ids"))
    if surface.get("surface_type") == "DOCUMENTED_NONEXECUTABLE" or surface.get("status") in DOCUMENTED_STATUSES:
        status = ADMIT_DOCUMENTED_NONEXECUTABLE_SURFACE if not reasons else QUARANTINE_INCOMPLETE_DERIVATION
    elif reasons:
        fatal = [r for r in reasons if r.startswith("REJECT")]
        status = fatal[0].split(":")[0] if fatal else QUARANTINE_INCOMPLETE_DERIVATION
    elif len(invariant_ids) > 1:
        status = ADMIT_MULTI_INVARIANT_DERIVATION
    else:
        status = ADMIT_KERNEL_DERIVED_SURFACE
    payload = {
        "schema": DECISION_SCHEMA,
        "version": VERSION,
        "surface_id": surface.get("surface_id"),
        "surface_type": surface.get("surface_type"),
        "status": status,
        "derivation_complete": not reasons and status != QUARANTINE_INCOMPLETE_DERIVATION,
        "invariant_ids": invariant_ids,
        "reasons": reasons,
    }
    witness = make_hash72_kernel_witness("HHS_SURFACE_CONFORMANCE_DECISION_V1", payload, width=72)
    payload["derivation_root_hash72"] = witness.digest
    payload["hash72_kernel_witness"] = witness.to_dict()
    return payload


def evaluate_surface(surface: Mapping[str, Any], registry=None) -> Dict[str, Any]:
    reasons = classify_derivation_failure(surface, registry=registry)
    return emit_conformance_decision(surface, reasons, registry=registry)


def evaluate_registry(registry=None) -> Dict[str, Any]:
    registry = registry or build_default_invariant_registry()
    validation = registry.validate_invariant_registry()
    return {
        "schema": "HHS_KERNEL_CONFORMANCE_REGISTRY_DECISION_V1",
        "version": VERSION,
        "status": "ADMIT_KERNEL_INVARIANT_REGISTRY" if validation.get("ok") else "REJECT_INVALID_KERNEL_INVARIANT_REGISTRY",
        "ok": bool(validation.get("ok")),
        "invariant_count": validation.get("invariant_count"),
        "reasons": validation.get("reasons", []),
        "registry_root_hash72": validation.get("registry_root_hash72"),
    }


def evaluate_operation(surface: Mapping[str, Any], operation: str, *, registry=None) -> Dict[str, Any]:
    decision = evaluate_surface(surface, registry=registry)
    declared_ops = _list(surface.get("declared_operations") or [surface.get("symbol", ""), surface.get("function", "")])
    if operation and declared_ops and str(operation) not in declared_ops:
        decision = dict(decision)
        decision["status"] = REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT
        decision["derivation_complete"] = False
        decision.setdefault("reasons", []).append(REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT)
    return decision


def kernel_conformance_decision_self_test() -> Dict[str, Any]:
    registry = build_default_invariant_registry()
    admitted = evaluate_surface({
        "surface_id": "service:control_flow.transition_audit_self_test",
        "surface_type": "SERVICE",
        "invariant_ids": ["HHS-I001", "HHS-I003", "HHS-I007"],
        "contract_schemas": ["HHS_CONTROL_FLOW_TRANSITION_AUDIT_SELF_TEST_V1"],
        "witness_schemas": ["HHS_KERNEL_DERIVATION_WITNESS_V1", "HHS_CONTROL_FLOW_TRANSITION_WITNESS_V1"],
        "validators": ["validate_control_flow_transition_audit"],
        "rejection_codes": ["REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
    }, registry=registry)
    rejected = evaluate_surface({
        "surface_id": "service:underived.example",
        "surface_type": "SERVICE",
    }, registry=registry)
    return {
        "schema": "HHS_KERNEL_CONFORMANCE_DECISION_SELF_TEST_V1",
        "ok": admitted["derivation_complete"] and rejected["status"] == REJECT_UNDERIVED_RUNTIME_SURFACE,
        "admitted": admitted,
        "rejected": rejected,
    }


if __name__ == "__main__":
    print(kernel_conformance_decision_self_test())
