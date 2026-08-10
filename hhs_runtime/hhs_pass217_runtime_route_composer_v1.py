"""Pass 217 production-route binding for mandatory cumulative composition.

The Pass 042 conformance graph already defines API routes as kernel-derived
surfaces, but the production service-registry endpoints predate that declaration
set.  This module adds an additive, source-keyed binding for those live routes
without rebuilding the entire default service registry on every request.

The shared HHS IO ingress boundary calls this module before recording or reusing
a request.  A bound route therefore cannot reach its handler merely because an
IO receipt/cache path exists; it must first pass the inherited Pass 043 runtime
composer.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import derive_surface_conformance
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight


VERSION = "PASS_217_RUNTIME_ROUTE_COMPOSITION_BINDING_V1"
SCHEMA = "HHS_PASS217_RUNTIME_ROUTE_COMPOSITION_PREFLIGHT_V1"

SERVICE_ROUTE_BINDINGS: Dict[str, Dict[str, Any]] = {
    "api.runtime.services": {
        "route": "GET /api/runtime/services",
        "symbol": "runtime.services.list",
        "invariant_ids": ["HHS-I005", "HHS-I011", "HHS-I012", "HHS-I014"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
    },
    "api.runtime.services.status": {
        "route": "GET /api/runtime/services/status",
        "symbol": "runtime.services.status",
        "invariant_ids": ["HHS-I005", "HHS-I011", "HHS-I012", "HHS-I014"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
    },
    "api.runtime.services.dispatch": {
        "route": "POST /api/runtime/services/dispatch",
        "symbol": "runtime.services.dispatch",
        "invariant_ids": [
            "HHS-I005",
            "HHS-I006",
            "HHS-I011",
            "HHS-I012",
            "HHS-I013",
            "HHS-I014",
        ],
        "mutation_policy": "CONTROLLED_RUNTIME_MUTATION",
        "persistence_policy": "CANONICAL_MUTATION_RECEIPT",
    },
}


def is_bound_route_source(source: str) -> bool:
    return str(source) in SERVICE_ROUTE_BINDINGS


def build_bound_route_surface(source: str) -> Dict[str, Any]:
    """Build the Pass 042-compatible surface for one bound production route."""

    key = str(source)
    binding = SERVICE_ROUTE_BINDINGS.get(key)
    if binding is None:
        raise KeyError(key)
    route = str(binding["route"])
    symbol = str(binding["symbol"])
    surface = derive_surface_conformance(
        {
            "surface_id": f"api_route:{route}",
            "surface_type": "API_ROUTE",
            "module": "hhs_backend.api.runtime_routes",
            "symbol": symbol,
            "invariant_ids": list(binding["invariant_ids"]),
            "contract_schemas": [
                "HHS_CONFORMANCE_API_ROUTE_CONTRACT_V1",
                "HHS_PASS217_CUMULATIVE_EXECUTION_ROUTE_CONTRACT_V1",
            ],
            "witness_schemas": [
                "HHS_KERNEL_DERIVATION_WITNESS_V1",
                "HHS_SURFACE_REACHABILITY_WITNESS_V1",
                "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            ],
            "validators": [
                "validate_api_route_kernel_derivation",
                "validate_pass217_cumulative_route_composition",
            ],
            "guards": [
                "runtime_constraint_enforcement",
                "zero_bypass_runtime_interposer",
                "io_gateway",
                "kernel_runtime_autocomposer",
            ],
            "rejection_codes": [
                "REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT",
                "REJECT_UNDERIVED_RUNTIME_SURFACE",
                "REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION",
            ],
            "mutation_policy": binding["mutation_policy"],
            "persistence_policy": binding["persistence_policy"],
            "boundedness_policy": "PASS_043_BOUNDED_METADATA_LIFECYCLE_V1",
            "declared_operations": [symbol],
        }
    )
    return surface


def compose_bound_route_ingress(
    source: str,
    payload: Optional[Mapping[str, Any]] = None,
    *,
    cache: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """Return None for unbound sources; fail closed for bound route preflight."""

    key = str(source)
    binding = SERVICE_ROUTE_BINDINGS.get(key)
    if binding is None:
        return None
    surface = build_bound_route_surface(key)
    symbol = str(binding["symbol"])
    preflight = execute_surface_preflight(
        surface,
        operation=symbol,
        cache=cache,
    )
    pipeline = dict(
        (preflight.get("composition_plan") or {}).get("pipeline") or {}
    )
    witness = dict(
        (preflight.get("composition_plan") or {}).get("witness") or {}
    )
    decision = {
        "schema": SCHEMA,
        "version": VERSION,
        "ok": bool(preflight.get("ok")),
        "status": preflight.get("status"),
        "source": key,
        "route": binding["route"],
        "surface_id": surface.get("surface_id"),
        "operation": symbol,
        "request_payload_keys": sorted(str(k) for k in dict(payload or {})),
        "derivation_complete": bool(surface.get("derivation_complete")),
        "conformance_root_hash72": preflight.get("conformance_root_hash72"),
        "pipeline_root_hash72": pipeline.get("pipeline_root_hash72"),
        "composition_root_hash72": witness.get("composition_root_hash72"),
        "cache_hit": bool((preflight.get("cache") or {}).get("cache_hit")),
        "expanded_metadata_persisted": bool(
            preflight.get("expanded_metadata_persisted")
        ),
        "propagation_allowed": bool(preflight.get("ok")),
    }
    if not decision["ok"]:
        decision["reason"] = "REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION"
    return decision


def runtime_route_composer_self_test() -> Dict[str, Any]:
    cache: Dict[str, Dict[str, Any]] = {}
    first = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache=cache,
    )
    second = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache=cache,
    )
    dispatch = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example"},
        cache=cache,
    )
    return {
        "schema": "HHS_PASS217_RUNTIME_ROUTE_COMPOSER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(
            first
            and first.get("ok")
            and second
            and second.get("ok")
            and second.get("cache_hit")
            and dispatch
            and dispatch.get("ok")
            and compose_bound_route_ingress("unbound.source", {}, cache=cache) is None
        ),
        "first": first,
        "second": second,
        "dispatch": dispatch,
    }


if __name__ == "__main__":
    print(runtime_route_composer_self_test())
