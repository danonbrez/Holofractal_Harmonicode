"""Canonical Pass 217 production service-route declarations.

This module is intentionally dependency-light so both the Pass 042 global
surface-map discovery path and the Pass 217 runtime-route composer consume the
same declarations without a circular import.  These are declarations only;
runtime admission still requires kernel autocomposition plus cumulative
execution-authority reachability.
"""
from __future__ import annotations

from typing import Any, Dict, List

VERSION = "PASS_217_CUMULATIVE_SERVICE_ROUTE_BINDINGS_V1"

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


def service_route_surface_declaration(source: str) -> Dict[str, Any]:
    key = str(source)
    binding = SERVICE_ROUTE_BINDINGS.get(key)
    if binding is None:
        raise KeyError(key)
    route = str(binding["route"])
    symbol = str(binding["symbol"])
    return {
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
            "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1",
        ],
        "validators": [
            "validate_api_route_kernel_derivation",
            "validate_pass217_cumulative_route_composition",
            "validate_authority_reachability",
        ],
        "guards": [
            "runtime_constraint_enforcement",
            "zero_bypass_runtime_interposer",
            "io_gateway",
            "kernel_runtime_autocomposer",
            "cumulative_execution_authority_reachability",
        ],
        "rejection_codes": [
            "REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
            "REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION",
            "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY",
        ],
        "mutation_policy": str(binding["mutation_policy"]),
        "persistence_policy": str(binding["persistence_policy"]),
        "boundedness_policy": "PASS_043_BOUNDED_METADATA_LIFECYCLE_V1",
        "declared_operations": [symbol],
        "pass217_binding_source": key,
    }


def service_route_surface_declarations() -> List[Dict[str, Any]]:
    return [
        service_route_surface_declaration(source)
        for source in sorted(SERVICE_ROUTE_BINDINGS)
    ]


__all__ = [
    "VERSION",
    "SERVICE_ROUTE_BINDINGS",
    "service_route_surface_declaration",
    "service_route_surface_declarations",
]
