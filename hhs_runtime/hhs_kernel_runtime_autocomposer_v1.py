"""
HHS Kernel Runtime Auto-Composer v1
===================================

Pass 043 derives runtime pipeline plans from the Pass 042 kernel-conformance
surface graph. Runtime behavior is composed from invariant ancestry rather than
hand-wired local policy.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_conformance_decision_v1 import evaluate_operation, evaluate_surface
from hhs_runtime.hhs_validation_residue_compactor_v1 import compact_validation_residue, evict_expanded_metadata, verify_residue_reconstruction
from hhs_runtime.hhs_conformance_decision_cache_v1 import get_or_build_decision

VERSION = "PASS_043_KERNEL_DERIVED_RUNTIME_AUTOCOMPOSITION_V1"
PLAN_SCHEMA = "HHS_KERNEL_RUNTIME_COMPOSITION_PLAN_V1"
PIPELINE_SCHEMA = "HHS_RUNTIME_PIPELINE_DERIVATION_V1"

REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED = "REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED"
REJECT_RUNTIME_PIPELINE_HANDWIRED_WITHOUT_DERIVATION = "REJECT_RUNTIME_PIPELINE_HANDWIRED_WITHOUT_DERIVATION"
REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT = "REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def _surface_index(surface_map: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(s.get("surface_id")): dict(s) for s in surface_map.get("surfaces", []) or []}


def derive_runtime_pipeline(surface: Mapping[str, Any], *, operation: str = "self_test") -> Dict[str, Any]:
    decision = evaluate_operation(surface, operation)
    if not decision.get("derivation_complete"):
        return {
            "schema": PIPELINE_SCHEMA,
            "version": VERSION,
            "surface_id": surface.get("surface_id"),
            "operation": operation,
            "status": REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED,
            "composition_allowed": False,
            "decision": decision,
            "reasons": decision.get("reasons", [REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED]),
        }
    pipeline = {
        "schema": PIPELINE_SCHEMA,
        "version": VERSION,
        "surface_id": surface.get("surface_id"),
        "surface_type": surface.get("surface_type"),
        "operation": operation,
        "invariant_ids": list(surface.get("invariant_ids", []) or []),
        "contract_schemas": list(surface.get("contract_schemas", []) or []),
        "guard_path": list(surface.get("guards", []) or []) or ["runtime_constraint_enforcement", "zero_bypass_runtime_interposer"],
        "validator_path": list(surface.get("validators", []) or []),
        "witness_path": list(surface.get("witness_schemas", []) or []),
        "enforcement_path": ["kernel_conformance_decision", "runtime_constraint_enforcement", "zero_bypass_runtime_interposer"],
        "execution_adapter": surface.get("symbol") or operation,
        "receipt_path": ["HHS_KERNEL_DERIVATION_WITNESS_V1", "HHS_HASH72_KERNEL_WITNESS_V1", "HHS_UNIFIED_LEDGER_RECEIPT_V1"],
        "persistence_policy": surface.get("persistence_policy", "NO_PERSISTENCE_MUTATION"),
        "mutation_policy": surface.get("mutation_policy", "NO_EXTERNAL_STATE_MUTATION"),
        "egress_policy": "COMPACT_RESIDUE_ONLY_AFTER_VALIDATION",
        "boundedness_policy": surface.get("boundedness_policy", "PASS_043_BOUNDED_METADATA_LIFECYCLE_V1"),
        "handwired": False,
        "composition_allowed": True,
        "decision": decision,
    }
    pipeline["pipeline_root_hash72"] = _hash72(PIPELINE_SCHEMA, pipeline)
    return pipeline


def validate_composition_plan(plan: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    if not plan.get("composition_allowed"):
        reasons.append(REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED)
    if plan.get("handwired") and not plan.get("kernel_derived_override"):
        reasons.append(REJECT_RUNTIME_PIPELINE_HANDWIRED_WITHOUT_DERIVATION)
    for field in ["invariant_ids", "contract_schemas", "validator_path", "witness_path", "enforcement_path"]:
        if not plan.get(field):
            reasons.append(f"REJECT_COMPOSITION_MISSING_{field.upper()}")
    return {
        "schema": "HHS_KERNEL_RUNTIME_COMPOSITION_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_KERNEL_DERIVED_RUNTIME_COMPOSITION" if not reasons else "REJECT_INVALID_RUNTIME_COMPOSITION",
        "reasons": reasons,
        "pipeline_root_hash72": plan.get("pipeline_root_hash72"),
    }


def build_composition_witness(plan: Mapping[str, Any]) -> Dict[str, Any]:
    witness = make_hash72_kernel_witness("HHS_KERNEL_RUNTIME_COMPOSITION_PLAN_V1", plan, width=72)
    return {
        "schema": "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
        "version": VERSION,
        "composition_root_hash72": witness.digest,
        "hash72_kernel_witness": witness.to_dict(),
    }


def compose_surface_pipeline(surface_id: str, *, operation: str = "self_test", surface_map: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    if surface_map is None:
        from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
        surface_map = build_surface_map()
    index = _surface_index(surface_map)
    surface = index.get(str(surface_id))
    if not surface:
        return {
            "schema": PLAN_SCHEMA,
            "version": VERSION,
            "surface_id": surface_id,
            "operation": operation,
            "status": REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED,
            "composition_allowed": False,
            "reasons": ["REJECT_UNKNOWN_SURFACE"],
        }
    pipeline = derive_runtime_pipeline(surface, operation=operation)
    decision = validate_composition_plan(pipeline)
    witness = build_composition_witness(pipeline)
    return {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "surface_id": surface_id,
        "operation": operation,
        "surface_map_root_hash72": surface_map.get("conformance_root_hash72"),
        "pipeline": pipeline,
        "decision": decision,
        "witness": witness,
        "composition_allowed": bool(decision.get("ok")),
    }


def execute_composed_preflight(surface_id: str, *, operation: str = "self_test", surface_map: Optional[Mapping[str, Any]] = None, cache: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    cache = cache if cache is not None else {}
    if surface_map is None:
        from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
        surface_map = build_surface_map()
    index = _surface_index(surface_map)
    surface = index.get(str(surface_id))
    if not surface:
        return {"schema": "HHS_COMPOSED_PREFLIGHT_DECISION_V1", "ok": False, "status": "REJECT_UNKNOWN_SURFACE"}
    cached = get_or_build_decision(surface, conformance_root_hash72=str(surface_map.get("conformance_root_hash72")), cache=cache)
    plan = compose_surface_pipeline(surface_id, operation=operation, surface_map=surface_map)
    residue = compact_validation_residue(plan, source_id=f"composition:{surface_id}:{operation}")
    residue = evict_expanded_metadata(residue)
    reconstruction = verify_residue_reconstruction(residue, plan)
    return {
        "schema": "HHS_COMPOSED_PREFLIGHT_DECISION_V1",
        "version": VERSION,
        "ok": plan.get("composition_allowed") and reconstruction.get("ok"),
        "surface_id": surface_id,
        "operation": operation,
        "cache": cached,
        "composition_plan": plan,
        "compact_residue": residue,
        "reconstruction": reconstruction,
        "expanded_metadata_persisted": False,
    }


def kernel_runtime_autocomposer_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map

    surface_map = build_surface_map()
    surfaces = surface_map.get("surfaces", [])
    service = next((s for s in surfaces if s.get("surface_id") == "service:kernel_conformance_surface_map.self_test"), surfaces[0])
    operation = (service.get("declared_operations") or [service.get("symbol") or "self_test"])[0]
    cache: Dict[str, Dict[str, Any]] = {}
    first = execute_composed_preflight(service["surface_id"], operation=operation, surface_map=surface_map, cache=cache)
    second = execute_composed_preflight(service["surface_id"], operation=operation, surface_map=surface_map, cache=cache)
    invalid = derive_runtime_pipeline({"surface_id": "service:underived", "surface_type": "SERVICE"}, operation="run")
    return {
        "schema": "HHS_KERNEL_RUNTIME_AUTOCOMPOSER_SELF_TEST_V1",
        "version": VERSION,
        "ok": first.get("ok") and second.get("ok") and second.get("cache", {}).get("cache_hit") and not invalid.get("composition_allowed"),
        "surface_count": surface_map.get("surface_count"),
        "surface_map_root_hash72": surface_map.get("conformance_root_hash72"),
        "first_preflight": first,
        "second_preflight": second,
        "invalid_pipeline": invalid,
    }


if __name__ == "__main__":
    print(kernel_runtime_autocomposer_self_test())
