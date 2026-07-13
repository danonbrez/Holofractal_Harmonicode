"""
HHS Kernel Conformance Surface Map v1
=====================================

Pass 042 executable graph:

kernel invariant -> derived doctrine -> runtime surface -> contract schema ->
witness type -> validator -> admission/rejection code -> service/API/control-flow
binding.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_invariant_registry_v1 import build_default_invariant_registry
from hhs_runtime.hhs_kernel_conformance_decision_v1 import evaluate_surface
from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import build_ownership_declaration

VERSION = "PASS_042_KERNEL_DERIVED_CONFORMANCE_SURFACE_MAP_V1"
MAP_SCHEMA = "HHS_KERNEL_CONFORMANCE_SURFACE_MAP_V1"
SURFACE_SCHEMA = "HHS_RUNTIME_SURFACE_DERIVATION_V1"
EDGE_SCHEMA = "HHS_CONFORMANCE_EDGE_V1"
WITNESS_SCHEMA = "HHS_KERNEL_DERIVATION_WITNESS_V1"

SURFACE_TYPES = {
    "SERVICE", "API_ROUTE", "CONTROL_FLOW_GATE", "EXECUTOR", "PLUGIN_ADAPTER", "GUARD", "VALIDATOR",
    "CONTRACT_SCHEMA", "WITNESS_SCHEMA", "REJECTION_CODE", "PERSISTENCE_SURFACE", "CARRIER_SURFACE",
    "LEDGER_SURFACE", "CLOSURE_HARNESS", "GUI_RUNTIME_BRIDGE", "DOCUMENTED_NONEXECUTABLE",
}
RELATIONS = {
    "DERIVES", "REQUIRES", "VALIDATED_BY", "WITNESSED_BY", "GUARDED_BY", "REJECTED_BY", "PERSISTS_THROUGH",
    "EXECUTED_BY", "EXPOSED_AS", "SUMMARIZED_BY", "BOUNDED_BY", "RECONSTRUCTED_BY",
}

CONTROL_FLOW_SURFACES = [
    {
        "surface_id": "control_flow_gate:audited_if",
        "surface_type": "CONTROL_FLOW_GATE",
        "module": "hhs_control_flow_gates_v1",
        "symbol": "audited_if",
        "invariant_ids": ["HHS-I001", "HHS-I003", "HHS-I007"],
        "contract_schemas": ["HHS_AUDITED_IF_TRANSITION_CONTRACT_V1"],
        "witness_schemas": ["HHS_CONTROL_FLOW_TRANSITION_WITNESS_V1", "HHS_VALIDATION_RESIDUE_RECEIPT_V1"],
        "validators": ["validate_control_flow_transition_audit"],
        "guards": ["runtime_constraint_enforcement", "zero_bypass_runtime_interposer"],
        "rejection_codes": ["REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "PASS_041_CONTROL_FLOW_TRANSITION_AUDIT_V1",
        "declared_operations": ["audited_if"],
    },
    {
        "surface_id": "control_flow_gate:audited_loop",
        "surface_type": "CONTROL_FLOW_GATE",
        "module": "hhs_control_flow_gates_v1",
        "symbol": "audited_loop",
        "invariant_ids": ["HHS-I003", "HHS-I004", "HHS-I007"],
        "contract_schemas": ["HHS_AUDITED_LOOP_TRANSITION_CONTRACT_V1"],
        "witness_schemas": ["HHS_CONTROL_FLOW_TRANSITION_WITNESS_V1", "HHS_VALIDATION_RESIDUE_RECEIPT_V1"],
        "validators": ["validate_control_flow_transition_audit", "validate_bounded_recursive_closure"],
        "guards": ["runtime_constraint_enforcement", "zero_bypass_runtime_interposer"],
        "rejection_codes": ["REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY", "REJECT_UNBOUNDED_RECURSIVE_CLOSURE"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "PASS_041_CONTROL_FLOW_TRANSITION_AUDIT_V1",
        "declared_operations": ["audited_loop"],
    },
]

API_ROUTE_SURFACES = [
    ("GET /api/runtime/live/status", "live_runtime.status", ["HHS-I002", "HHS-I005", "HHS-I012", "HHS-I014"]),
    ("POST /api/runtime/live/tick", "live_runtime.tick", ["HHS-I002", "HHS-I005", "HHS-I006", "HHS-I012", "HHS-I014"]),
    ("GET /api/runtime/gui/projection/status", "gui_projection.status", ["HHS-I002", "HHS-I012", "HHS-I014"]),
    ("POST /api/runtime/gui/command", "gui_command.submit", ["HHS-I005", "HHS-I011", "HHS-I012", "HHS-I014"]),
    ("GET /api/runtime/gui/command/status/{command_id}", "gui_command.status", ["HHS-I006", "HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/gui/command/history", "gui_command.history", ["HHS-I006", "HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/gui/mutation/allowlist", "gui_mutation.allowlist", ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"]),
    ("GET /api/runtime/workspace/status", "workspace.status", ["HHS-I005", "HHS-I011", "HHS-I014"]),
    ("POST /api/runtime/workspace/command", "workspace.command", ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"]),
    ("POST /api/runtime/workspace/project", "workspace.project.create", ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/workspace/project/{project_id}", "workspace.project.get", ["HHS-I006", "HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/workspace/commands/history", "workspace.commands.history", ["HHS-I006", "HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/workspace/modality/adapters", "workspace.modality.adapters", ["HHS-I001", "HHS-I008", "HHS-I011", "HHS-I014", "HHS-I016"]),
    ("POST /api/runtime/workspace/modality/pipeline", "workspace.modality.pipeline", ["HHS-I001", "HHS-I005", "HHS-I006", "HHS-I008", "HHS-I010", "HHS-I011", "HHS-I014", "HHS-I016"]),
    ("GET /api/runtime/workspace/artifact/lineage/{lineage_id}", "workspace.artifact.lineage", ["HHS-I006", "HHS-I010", "HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/conformance/invariants", "conformance.invariants", ["HHS-I011", "HHS-I014", "HHS-I015"]),
    ("GET /api/runtime/conformance/surfaces", "conformance.surfaces", ["HHS-I011", "HHS-I014", "HHS-I015"]),
    ("GET /api/runtime/conformance/surfaces/{surface_id}", "conformance.surface_detail", ["HHS-I011", "HHS-I014"]),
    ("GET /api/runtime/conformance/invariants/{invariant_id}", "conformance.invariant_detail", ["HHS-I011", "HHS-I014"]),
    ("POST /api/runtime/conformance/evaluate", "conformance.evaluate", ["HHS-I011", "HHS-I014", "HHS-I015"]),
    ("GET /api/runtime/conformance/status", "conformance.status", ["HHS-I011", "HHS-I014", "HHS-I015"]),
]


def _list(values: Optional[Iterable[Any]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            out.append(text)
    return sorted(dict.fromkeys(out))


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def _surface_hash(surface: Mapping[str, Any]) -> str:
    payload = {k: surface.get(k) for k in sorted(surface) if not k.endswith("hash72") and k != "hash72_kernel_witness"}
    return _hash72("HHS_RUNTIME_SURFACE_DERIVATION_V1", payload)


def _canonical_surface(record: Mapping[str, Any]) -> Dict[str, Any]:
    surface = {
        "schema": SURFACE_SCHEMA,
        "version": VERSION,
        "surface_id": str(record.get("surface_id", "")),
        "surface_type": str(record.get("surface_type", "SERVICE")),
        "module": str(record.get("module", "")),
        "symbol": str(record.get("symbol", record.get("function", ""))),
        "invariant_ids": _list(record.get("invariant_ids")),
        "contract_schemas": _list(record.get("contract_schemas")),
        "witness_schemas": _list(record.get("witness_schemas")),
        "validators": _list(record.get("validators")),
        "guards": _list(record.get("guards")),
        "rejection_codes": _list(record.get("rejection_codes")),
        "mutation_policy": str(record.get("mutation_policy") or "NO_EXTERNAL_STATE_MUTATION"),
        "persistence_policy": str(record.get("persistence_policy") or "NO_PERSISTENCE_MUTATION"),
        "boundedness_policy": str(record.get("boundedness_policy") or "PASS_042_BOUNDED_CONFORMANCE_SUMMARY_V1"),
        "declared_operations": _list(record.get("declared_operations") or [record.get("symbol") or record.get("function", "")]),
        "kernel_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
    }
    decision = evaluate_surface(surface)
    surface["status"] = decision.get("status")
    surface["derivation_complete"] = bool(decision.get("derivation_complete"))
    surface["derivation_hash72"] = _surface_hash(surface)
    return surface


def _service_surfaces() -> List[Dict[str, Any]]:
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry

    registry = make_default_service_registry()
    surfaces: List[Dict[str, Any]] = []
    for service in registry.services():
        declaration = build_ownership_declaration(service)
        declaration["surface_type"] = "SERVICE"
        surfaces.append(_canonical_surface(declaration))
    return surfaces


def _api_route_surfaces() -> List[Dict[str, Any]]:
    surfaces: List[Dict[str, Any]] = []
    for route, symbol, invariants in API_ROUTE_SURFACES:
        surfaces.append(_canonical_surface({
            "surface_id": f"api_route:{route}",
            "surface_type": "API_ROUTE",
            "module": "hhs_backend.api.runtime_routes",
            "symbol": symbol,
            "invariant_ids": invariants,
            "contract_schemas": ["HHS_CONFORMANCE_API_ROUTE_CONTRACT_V1"],
            "witness_schemas": ["HHS_KERNEL_DERIVATION_WITNESS_V1", "HHS_SURFACE_REACHABILITY_WITNESS_V1"],
            "validators": ["validate_api_route_kernel_derivation"],
            "guards": ["runtime_constraint_enforcement", "io_gateway"],
            "rejection_codes": ["REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT", "REJECT_UNDERIVED_RUNTIME_SURFACE"],
            "mutation_policy": "NO_EXTERNAL_STATE_MUTATION" if route.startswith("GET") else "CONTROLLED_RUNTIME_MUTATION",
            "persistence_policy": "CONFORMANCE_EVALUATION_RECEIPT" if route.startswith("POST") else "NO_PERSISTENCE_MUTATION",
            "boundedness_policy": "PASS_042_BOUNDED_CONFORMANCE_SUMMARY_V1",
            "declared_operations": _list([
                symbol,
                symbol.split(".")[-1],
                "runtime.tick" if symbol == "live_runtime.tick" else "",
                "runtime.status" if symbol == "live_runtime.status" else "",
                "runtime.request_status_snapshot" if symbol == "live_runtime.status" else "",
                "runtime.pause" if symbol == "live_runtime.status" else "",
                "runtime.resume" if symbol == "live_runtime.status" else "",
                "runtime.refresh_projection" if symbol == "gui_projection.status" else "",
                "gui.command.submit" if symbol == "gui_command.submit" else "",
                "gui.command.status" if symbol == "gui_command.status" else "",
                "gui.command.history" if symbol == "gui_command.history" else "",
                "expanded_state_decay.sweep" if symbol == "gui_mutation.allowlist" else "",
                "semantic_cache.refresh_composition_index" if symbol == "gui_mutation.allowlist" else "",
            ]),
        }))
    return surfaces


def _control_flow_surfaces() -> List[Dict[str, Any]]:
    return [_canonical_surface(surface) for surface in CONTROL_FLOW_SURFACES]


def discover_runtime_surfaces() -> List[Dict[str, Any]]:
    return sorted(_service_surfaces() + _api_route_surfaces() + _control_flow_surfaces(), key=lambda item: item["surface_id"])


def derive_surface_conformance(surface: Mapping[str, Any]) -> Dict[str, Any]:
    return _canonical_surface(surface)


def resolve_surface_invariants(surface: Mapping[str, Any]) -> List[Dict[str, Any]]:
    registry = build_default_invariant_registry()
    out = []
    for iid in _list(surface.get("invariant_ids")):
        out.append(registry.get_invariant(iid))
    return out


def _edge_id(source_type: str, source_id: str, relation: str, target_type: str, target_id: str) -> str:
    return f"edge:{source_type}:{source_id}:{relation}:{target_type}:{target_id}"


def make_edge(source_type: str, source_id: str, relation: str, target_type: str, target_id: str, *, witness_required: bool = True, validator_required: bool = True) -> Dict[str, Any]:
    edge = {
        "schema": EDGE_SCHEMA,
        "version": VERSION,
        "edge_id": _edge_id(source_type, source_id, relation, target_type, target_id),
        "source_type": source_type,
        "source_id": source_id,
        "relation": relation,
        "target_type": target_type,
        "target_id": target_id,
        "witness_required": witness_required,
        "validator_required": validator_required,
    }
    edge["hash72"] = _hash72("HHS_CONFORMANCE_EDGE_V1", edge)
    return edge


def build_conformance_edges(surfaces: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    for surface in surfaces:
        sid = str(surface.get("surface_id"))
        stype = str(surface.get("surface_type", "SURFACE"))
        for iid in _list(surface.get("invariant_ids")):
            edges.append(make_edge("INVARIANT", iid, "DERIVES", stype, sid))
        for schema in _list(surface.get("contract_schemas")):
            edges.append(make_edge(stype, sid, "REQUIRES", "CONTRACT_SCHEMA", schema))
        for witness in _list(surface.get("witness_schemas")):
            edges.append(make_edge(stype, sid, "WITNESSED_BY", "WITNESS_SCHEMA", witness))
        for validator in _list(surface.get("validators")):
            edges.append(make_edge(stype, sid, "VALIDATED_BY", "VALIDATOR", validator))
        for guard in _list(surface.get("guards")):
            edges.append(make_edge(stype, sid, "GUARDED_BY", "GUARD", guard, validator_required=False))
        for code in _list(surface.get("rejection_codes")):
            edges.append(make_edge(stype, sid, "REJECTED_BY", "REJECTION_CODE", code, validator_required=False))
    return sorted(edges, key=lambda e: e["edge_id"])


def validate_surface_map(surface_map: Mapping[str, Any]) -> Dict[str, Any]:
    surfaces = list(surface_map.get("surfaces", []))
    reasons: List[str] = []
    seen = set()
    for surface in surfaces:
        sid = surface.get("surface_id")
        if sid in seen:
            reasons.append(f"duplicate_surface:{sid}")
        seen.add(sid)
        decision = evaluate_surface(surface)
        if not decision.get("derivation_complete"):
            reasons.append(f"{sid}:{decision.get('status')}")
    return {
        "schema": "HHS_KERNEL_CONFORMANCE_SURFACE_MAP_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_KERNEL_CONFORMANCE_SURFACE_MAP" if not reasons else "REJECT_KERNEL_CONFORMANCE_SURFACE_MAP",
        "surface_count": len(surfaces),
        "underived_surface_count": len([s for s in surfaces if not s.get("derivation_complete")]),
        "reasons": reasons,
    }


def find_underived_surfaces(surface_map: Optional[Mapping[str, Any]] = None) -> List[Dict[str, Any]]:
    smap = surface_map or build_surface_map()
    return [s for s in smap.get("surfaces", []) if not s.get("derivation_complete")]


def find_orphaned_invariants(surface_map: Optional[Mapping[str, Any]] = None) -> List[str]:
    smap = surface_map or build_surface_map()
    used = set()
    for surface in smap.get("surfaces", []):
        used.update(_list(surface.get("invariant_ids")))
    registry = build_default_invariant_registry()
    return [inv["invariant_id"] for inv in registry.list_invariants() if inv["invariant_id"] not in used]


def build_surface_map_witness(surface_map: Mapping[str, Any]) -> Dict[str, Any]:
    payload = {
        "schema": MAP_SCHEMA,
        "version": VERSION,
        "surface_count": surface_map.get("surface_count"),
        "edge_count": surface_map.get("conformance_edge_count"),
        "surfaces": surface_map.get("surfaces", []),
        "edges": surface_map.get("edges", []),
    }
    witness = make_hash72_kernel_witness("HHS_KERNEL_CONFORMANCE_SURFACE_MAP_V1", payload, width=72)
    return {
        "schema": "HHS_KERNEL_CONFORMANCE_SURFACE_MAP_WITNESS_V1",
        "version": VERSION,
        "conformance_root_hash72": witness.digest,
        "hash72_kernel_witness": witness.to_dict(),
    }


def build_surface_map() -> Dict[str, Any]:
    registry = build_default_invariant_registry()
    surfaces = discover_runtime_surfaces()
    edges = build_conformance_edges(surfaces)
    payload = {
        "schema": MAP_SCHEMA,
        "version": VERSION,
        "invariant_count": len(registry.list_invariants()),
        "surface_count": len(surfaces),
        "conformance_edge_count": len(edges),
        "surfaces": surfaces,
        "edges": edges,
        "underived_surfaces": [s.get("surface_id") for s in surfaces if not s.get("derivation_complete")],
        "orphaned_invariants": [],
        "bounded_summary_mode": "compact_roots_not_full_recompute",
    }
    payload["orphaned_invariants"] = find_orphaned_invariants(payload)
    payload["validation"] = validate_surface_map(payload)
    payload["witness"] = build_surface_map_witness(payload)
    payload["conformance_root_hash72"] = payload["witness"]["conformance_root_hash72"]
    return payload


def kernel_conformance_surface_map_self_test() -> Dict[str, Any]:
    surface_map = build_surface_map()
    underived = find_underived_surfaces(surface_map)
    return {
        "schema": "HHS_KERNEL_CONFORMANCE_SURFACE_MAP_SELF_TEST_V1",
        "ok": surface_map.get("validation", {}).get("ok") and len(underived) == 0,
        "surface_count": surface_map.get("surface_count"),
        "service_count": len([s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "SERVICE"]),
        "api_route_count": len([s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "API_ROUTE"]),
        "control_flow_gate_count": len([s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "CONTROL_FLOW_GATE"]),
        "conformance_edge_count": surface_map.get("conformance_edge_count"),
        "underived_surface_count": len(underived),
        "conformance_root_hash72": surface_map.get("conformance_root_hash72"),
    }


if __name__ == "__main__":
    print(kernel_conformance_surface_map_self_test())
