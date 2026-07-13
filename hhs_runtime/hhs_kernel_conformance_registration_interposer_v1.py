"""
HHS Kernel Conformance Registration Interposer v1
=================================================

Intercepts service-registration metadata and prevents unknown/underived runtime
surfaces from becoming active.  Known legacy services are migrated through a
canonical derivation resolver; unknown services must carry explicit invariant
ownership and bindings.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_runtime.hhs_kernel_conformance_decision_v1 import evaluate_surface
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_042_KERNEL_DERIVED_CONFORMANCE_SURFACE_MAP_V1"
OWNERSHIP_SCHEMA = "HHS_INVARIANT_OWNERSHIP_DECLARATION_V1"


def _list(values: Optional[Iterable[Any]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            out.append(text)
    return sorted(dict.fromkeys(out))


def _contracts_for(name: str, service_type: str, function: str) -> List[str]:
    stem = name.upper().replace(".", "_").replace("-", "_")
    if function:
        return [f"HHS_{stem}_CONTRACT_V1"]
    return [f"HHS_{service_type.upper()}_SERVICE_CONTRACT_V1"]


def infer_invariant_ids(name: str, service_type: str, module: str = "") -> List[str]:
    text = f"{name} {service_type} {module}".lower()
    ids = {"HHS-I011", "HHS-I014"}
    if any(x in text for x in ["authority", "hash72", "c_bridge", "kernel"]):
        ids.update(["HHS-I002", "HHS-I005", "HHS-I012"])
    if any(x in text for x in ["service", "dispatch", "plugin", "executor", "adapter", "runtime_contract"]):
        ids.update(["HHS-I005", "HHS-I008", "HHS-I012"])
    if any(x in text for x in ["ledger", "receipt", "persistence", "state_store"]):
        ids.update(["HHS-I006", "HHS-I013"])
    if any(x in text for x in ["closure", "harness", "bounded"]):
        ids.update(["HHS-I004", "HHS-I007", "HHS-I015"])
    if any(x in text for x in ["control_flow", "transition", "audited"]):
        ids.update(["HHS-I001", "HHS-I003", "HHS-I007"])
    if any(x in text for x in ["residue", "validation"]):
        ids.update(["HHS-I007", "HHS-I008", "HHS-I016"])
    if any(x in text for x in ["autocomposer", "autocomposition", "composition", "pipeline", "lifecycle", "decay", "performance", "cache", "compactor", "rebuilder", "invalidation", "dependency_index", "semantic_runtime_query"]):
        ids.update(["HHS-I007", "HHS-I008", "HHS-I011", "HHS-I014", "HHS-I015", "HHS-I016"])
    if any(x in text for x in ["hhfs", "carrier", "udfp", "metadata", "reconstruction"]):
        ids.update(["HHS-I009", "HHS-I010", "HHS-I013"])
    if any(x in text for x in ["modality", "adapter", "projection", "artifact", "lineage", "cross_modal", "transformation_plan", "capability_map"]):
        ids.update(["HHS-I001", "HHS-I005", "HHS-I008", "HHS-I010", "HHS-I011", "HHS-I014", "HHS-I016"])
    if any(x in text for x in ["canonical_observer", "capability", "provider", "fabric", "fallback", "invocation", "policy_gate", "execution_proposal", "result_ingress"]):
        ids.update(["HHS-I001", "HHS-I005", "HHS-I008", "HHS-I010", "HHS-I011", "HHS-I012", "HHS-I014", "HHS-I016", "HHS-I017"])
    if any(x in text for x in ["document", "pdf", "ocr", "page_geometry", "image_region", "structure_fusion", "perception_receipt", "document_reconstruction"]):
        ids.update(["HHS-I001", "HHS-I002", "HHS-I005", "HHS-I008", "HHS-I010", "HHS-I011", "HHS-I012", "HHS-I014", "HHS-I016", "HHS-I017"])
    if any(x in text for x in ["phase", "genesis", "severance", "permanence"]):
        ids.update(["HHS-I001", "HHS-I011", "HHS-I013"])
    if any(x in text for x in ["constraint", "interposer", "zero_bypass", "admissibility"]):
        ids.update(["HHS-I005", "HHS-I011", "HHS-I012"])
    if any(x in text for x in ["io_gateway", "dataflow", "semantic_memory"]):
        ids.update(["HHS-I001", "HHS-I005", "HHS-I006"])
    if any(x in text for x in ["conformance", "invariant_registry"]):
        ids.update(["HHS-I011", "HHS-I014", "HHS-I015"])
    # Unknown names/types must not be silently canonized.
    known_markers = ["hhs_", "self_test", "runtime", "authority", "ledger", "srcg", "hash72", "hhfs", "control_flow", "closure", "service", "plugin", "constraint", "conformance", "invariant", "semantic", "composition", "pipeline", "cache", "rebuild", "query", "dependency", "invalidation", "modality", "adapter", "projection", "artifact", "lineage", "cross_modal", "transformation", "capability", "provider", "observer", "fabric", "invocation", "fallback", "document", "pdf", "ocr", "perception", "fusion", "geometry", "region"]
    if not any(marker in text for marker in known_markers):
        return []
    return sorted(ids)


def build_ownership_declaration(spec: Mapping[str, Any]) -> Dict[str, Any]:
    name = str(spec.get("name", ""))
    service_type = str(spec.get("service_type", "runtime"))
    module = str(spec.get("module", ""))
    function = str(spec.get("function", ""))
    invariant_ids = _list(spec.get("invariant_ids")) or infer_invariant_ids(name, service_type, module)
    contract_schemas = _list(spec.get("contract_schemas")) or _contracts_for(name, service_type, function)
    witness_schemas = _list(spec.get("witness_schemas")) or ["HHS_KERNEL_DERIVATION_WITNESS_V1", "HHS_HASH72_KERNEL_WITNESS_V1"]
    validators = _list(spec.get("validators")) or [f"validate_{name.replace('.', '_')}_kernel_derivation"]
    rejection_codes = _list(spec.get("rejection_codes")) or ["REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT", "REJECT_UNDERIVED_RUNTIME_SURFACE"]
    mutation_policy = str(spec.get("mutation_policy") or "NO_EXTERNAL_STATE_MUTATION")
    if any(x in service_type for x in ["ledger", "persistence"]) or any(x in name for x in ["reconstruction", "carrier_adapter"]):
        mutation_policy = str(spec.get("mutation_policy") or "CONTROLLED_RUNTIME_MUTATION")
    persistence_policy = str(spec.get("persistence_policy") or ("CANONICAL_LEDGER_RECEIPT" if mutation_policy != "NO_EXTERNAL_STATE_MUTATION" else "NO_PERSISTENCE_MUTATION"))
    boundedness_policy = str(spec.get("boundedness_policy") or "PASS_042_BOUNDED_CONFORMANCE_SUMMARY_V1")
    declaration = {
        "schema": OWNERSHIP_SCHEMA,
        "version": VERSION,
        "surface_id": f"service:{name}",
        "surface_type": "SERVICE",
        "service_name": name,
        "service_type": service_type,
        "module": module,
        "symbol": function,
        "invariant_ids": invariant_ids,
        "contract_schemas": contract_schemas,
        "witness_schemas": witness_schemas,
        "validators": validators,
        "guards": _list(spec.get("guards")) or ["kernel_conformance_registration_interposer", "zero_bypass_runtime_interposer"],
        "rejection_codes": rejection_codes,
        "mutation_policy": mutation_policy,
        "persistence_policy": persistence_policy,
        "boundedness_policy": boundedness_policy,
        "declared_operations": _list(spec.get("declared_operations")) or [function or name],
        "kernel_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
    }
    witness = make_hash72_kernel_witness("HHS_INVARIANT_OWNERSHIP_DECLARATION_V1", declaration, width=72)
    declaration["ownership_hash72"] = witness.digest
    return declaration


def interpose_service_registration(spec: Mapping[str, Any]) -> Dict[str, Any]:
    declaration = build_ownership_declaration(spec)
    decision = evaluate_surface(declaration)
    return {
        "schema": "HHS_SERVICE_REGISTRATION_CONFORMANCE_INTERPOSITION_V1",
        "version": VERSION,
        "ok": bool(decision.get("derivation_complete")),
        "service_name": spec.get("name"),
        "declaration": declaration,
        "decision": decision,
    }


def kernel_conformance_registration_self_test() -> Dict[str, Any]:
    admitted = interpose_service_registration({
        "name": "control_flow.transition_audit_self_test",
        "module": "hhs_runtime.hhs_control_flow_transition_audit_v1",
        "function": "control_flow_transition_audit_self_test",
        "service_type": "control_flow",
    })
    rejected = interpose_service_registration({
        "name": "external.unknown_surface",
        "module": "external.unknown",
        "function": "run",
        "service_type": "external",
        "invariant_ids": [],
        "contract_schemas": [],
        "witness_schemas": [],
        "validators": [],
        "rejection_codes": [],
    })
    return {
        "schema": "HHS_KERNEL_CONFORMANCE_REGISTRATION_SELF_TEST_V1",
        "ok": admitted.get("ok") and not rejected.get("ok"),
        "admitted": admitted,
        "rejected": rejected,
    }


if __name__ == "__main__":
    print(kernel_conformance_registration_self_test())
