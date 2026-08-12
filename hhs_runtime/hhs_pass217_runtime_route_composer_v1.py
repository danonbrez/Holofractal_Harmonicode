"""Pass 217 production-route binding for mandatory cumulative composition.

The shared HHS IO ingress boundary calls this module before recording or reusing
a request. A bound route therefore cannot reach its handler merely because an IO
receipt/cache path exists; it must first pass the inherited Pass 043 runtime
composer and the currently connected inherited optimization-authority slice.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import derive_surface_conformance
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass217_checkpoint13_interruption_recovery_v1 import (
    build_checkpoint13_inherited_authority_reachability,
)
from hhs_runtime.hhs_pass217_surface_bindings_v1 import (
    SERVICE_ROUTE_BINDINGS,
    service_route_surface_declaration,
)

VERSION = "PASS_217_RUNTIME_ROUTE_COMPOSITION_BINDING_V1"
SCHEMA = "HHS_PASS217_RUNTIME_ROUTE_COMPOSITION_PREFLIGHT_V1"


def is_bound_route_source(source: str) -> bool:
    return str(source) in SERVICE_ROUTE_BINDINGS


def build_bound_route_surface(source: str) -> Dict[str, Any]:
    return derive_surface_conformance(service_route_surface_declaration(source))


def _compact_authority_reachability(record: Mapping[str, Any]) -> Dict[str, Any]:
    summary = {
        "schema": "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_SUMMARY_V1",
        "admitted": bool(record.get("admitted")),
        "status": record.get("status"),
        "required_authority_count": record.get("required_authority_count"),
        "accepted_state_counts": dict(record.get("accepted_state_counts") or {}),
        "reachability_root_hash72": record.get("reachability_root_hash72"),
        "checkpoint_scope": list(record.get("checkpoint_scope") or []),
        "decisions": [
            {
                "authority_id": row.get("authority_id"),
                "state": row.get("state"),
                "accepted": bool(row.get("accepted")),
                "reasons": list(row.get("reasons") or []),
                "witness_root": (row.get("proof") or {}).get("witness_root"),
                "traversal_witness": (row.get("proof") or {}).get("traversal_witness"),
                "mechanically_proven": (row.get("proof") or {}).get("mechanically_proven"),
                "predicate": (row.get("proof") or {}).get("predicate"),
                "observed_facts": dict((row.get("proof") or {}).get("observed_facts") or {}),
            }
            for row in record.get("decisions", []) or []
        ],
        "blockers": list(record.get("blockers") or []),
        "optional_available_forbidden": True,
    }
    for key in (
        "continuation_applicability_facts", "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts", "content_reuse_applicability_facts",
        "checkpoint8_applicability_facts", "checkpoint9_applicability_facts",
        "checkpoint10_applicability_facts", "checkpoint11_applicability_facts",
        "checkpoint12_applicability_facts", "checkpoint13_applicability_facts",
    ):
        summary[key] = dict(record.get(key) or {})
    for key in (
        "checkpoint6_native_callable_map", "checkpoint7_authority_map",
        "checkpoint8_authority_map", "checkpoint9_authority_map",
        "checkpoint10_authority_map", "checkpoint11_authority_map",
        "checkpoint12_authority_map", "checkpoint13_authority_map",
    ):
        summary[key] = {str(k): dict(v) for k, v in dict(record.get(key) or {}).items()}
    return summary


def compose_bound_route_ingress(
    source: str,
    payload: Optional[Mapping[str, Any]] = None,
    *,
    cache: Optional[Dict[str, Dict[str, Any]]] = None,
    semantic_cache: Any = None,
    retrieval_runtime: Any = None,
    pattern_repo_root: Any = None,
    source_reuse_service: Any = None,
    projection_service: Any = None,
    delta_compiled_tensor: Any = None,
    parametric_template: Any = None,
    parametric_base_entry: Any = None,
    parametric_opening_boundary: Any = None,
    parametric_validation_key: Optional[bytes] = None,
    compiled_rom_store: Any = None,
    physical_recovery_runtime: Any = None,
    physical_protected_payload: Any = None,
    receipt_vector_index: Any = None,
    receipt_vector_receipt: Any = None,
    sql_context_db: Any = None,
    encrypted_vector_store: Any = None,
    snapshot_reuse_runtime: Any = None,
    multimodal_alignment_service: Any = None,
    bounded_learning_service: Any = None,
    moving_tensor_state: Any = None,
    moving_tensor_root_key: Optional[bytes] = None,
    moving_tensor_trusted_anchor: Any = None,
    native_dispatch_authority: Any = None,
    interruption_recovery_database_path: str | Path | None = None,
    interruption_recovery_ledger_key: Optional[bytes] = None,
    interruption_recovery_anchor_state_root_hash216: Optional[str] = None,
    interruption_recovery_anchor_receipt_hash72: Optional[str] = None,
    interruption_recovery_protected_store: Any = None,
    interruption_recovery_native_kernel: Any = None,
    interruption_recovery_tensor_state: Any = None,
) -> Optional[Dict[str, Any]]:
    key = str(source)
    binding = SERVICE_ROUTE_BINDINGS.get(key)
    if binding is None:
        return None
    payload_dict = dict(payload or {})
    surface = build_bound_route_surface(key)
    symbol = str(binding["symbol"])
    preflight = execute_surface_preflight(surface, operation=symbol, cache=cache)
    authority_record = None
    if preflight.get("ok"):
        authority_record = build_checkpoint13_inherited_authority_reachability(
            preflight, surface, payload_dict,
            semantic_cache=semantic_cache,
            retrieval_runtime=retrieval_runtime,
            pattern_repo_root=pattern_repo_root,
            source_reuse_service=source_reuse_service,
            projection_service=projection_service,
            delta_compiled_tensor=delta_compiled_tensor,
            parametric_template=parametric_template,
            parametric_base_entry=parametric_base_entry,
            parametric_opening_boundary=parametric_opening_boundary,
            parametric_validation_key=parametric_validation_key,
            compiled_rom_store=compiled_rom_store,
            physical_recovery_runtime=physical_recovery_runtime,
            physical_protected_payload=physical_protected_payload,
            receipt_vector_index=receipt_vector_index,
            receipt_vector_receipt=receipt_vector_receipt,
            sql_context_db=sql_context_db,
            encrypted_vector_store=encrypted_vector_store,
            snapshot_reuse_runtime=snapshot_reuse_runtime,
            multimodal_alignment_service=multimodal_alignment_service,
            bounded_learning_service=bounded_learning_service,
            moving_tensor_state=moving_tensor_state,
            moving_tensor_root_key=moving_tensor_root_key,
            moving_tensor_trusted_anchor=moving_tensor_trusted_anchor,
            native_dispatch_authority=native_dispatch_authority,
            interruption_recovery_database_path=interruption_recovery_database_path,
            interruption_recovery_ledger_key=interruption_recovery_ledger_key,
            interruption_recovery_anchor_state_root_hash216=interruption_recovery_anchor_state_root_hash216,
            interruption_recovery_anchor_receipt_hash72=interruption_recovery_anchor_receipt_hash72,
            interruption_recovery_protected_store=interruption_recovery_protected_store,
            interruption_recovery_native_kernel=interruption_recovery_native_kernel,
            interruption_recovery_tensor_state=interruption_recovery_tensor_state,
        )
    authority_summary = _compact_authority_reachability(authority_record) if authority_record is not None else None
    pipeline = dict((preflight.get("composition_plan") or {}).get("pipeline") or {})
    witness = dict((preflight.get("composition_plan") or {}).get("witness") or {})
    admitted = bool(preflight.get("ok")) and bool(authority_record and authority_record.get("admitted"))
    decision = {
        "schema": SCHEMA,
        "version": VERSION,
        "ok": admitted,
        "status": "ADMIT_RUNTIME_ROUTE_CUMULATIVE_EXECUTION" if admitted else "REJECT_RUNTIME_ROUTE_CUMULATIVE_EXECUTION",
        "source": key,
        "route": binding["route"],
        "surface_id": surface.get("surface_id"),
        "operation": symbol,
        "request_payload_keys": sorted(str(k) for k in payload_dict),
        "derivation_complete": bool(surface.get("derivation_complete")),
        "conformance_root_hash72": preflight.get("conformance_root_hash72"),
        "pipeline_root_hash72": pipeline.get("pipeline_root_hash72"),
        "composition_root_hash72": witness.get("composition_root_hash72"),
        "cache_hit": bool((preflight.get("cache") or {}).get("cache_hit")),
        "expanded_metadata_persisted": bool(preflight.get("expanded_metadata_persisted")),
        "kernel_runtime_composition_admitted": bool(preflight.get("ok")),
        "inherited_execution_authority_reachability": authority_summary,
        "propagation_allowed": admitted,
    }
    if not preflight.get("ok"):
        decision["reason"] = "REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION"
    elif not admitted:
        decision["reason"] = "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY"
    return decision


def runtime_route_composer_self_test() -> Dict[str, Any]:
    cache: Dict[str, Dict[str, Any]] = {}
    first = compose_bound_route_ingress("api.runtime.services", {"method": "GET"}, cache=cache)
    second = compose_bound_route_ingress("api.runtime.services", {"method": "GET"}, cache=cache)
    dispatch = compose_bound_route_ingress("api.runtime.services.dispatch", {"service": "example"}, cache=cache)
    return {
        "schema": "HHS_PASS217_RUNTIME_ROUTE_COMPOSER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(first and first.get("ok") and second and second.get("ok") and second.get("cache_hit") and dispatch and dispatch.get("ok") and compose_bound_route_ingress("unbound.source", {}, cache=cache) is None),
        "first": first,
        "second": second,
        "dispatch": dispatch,
    }


if __name__ == "__main__":
    print(runtime_route_composer_self_test())
