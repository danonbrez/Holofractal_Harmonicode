"""Pass 219 Lane 5 1.59 Linux/API zero-bypass interposition.

This is the public control-plane redirect. It does not create another execution
authority and it does not translate payload data. Any request that can reach a
runtime execution surface is first given a Lane-5-scoped interposition receipt.
Canonical VM81 mutation remains downstream of the native 1.59 secure gateway.
"""
from __future__ import annotations

from typing import Any, Mapping

from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import (
    guarded_surface_propagation,
    interpose_runtime_surface,
)

SCHEMA = "HHS_PASS219_LANE5_LINUX_API_INTERPOSER_1_59"
VERSION = "1.59"
NATIVE_GATEWAY = "hhs_exact_pass219_lane5_gateway_admit_raw5184"
CANONICAL_ADMISSION_COMPAT_ALIAS = "hhs_exact_pass219_vm81_environment_admit_signed"

_REQUIRED_SURFACES = frozenset(
    {
        "io.ingress",
        "service_registry.dispatch",
        "authorized_execution.call",
        "plugin_adapter.invocation",
        "srcg.selfsolve",
        "semantic_memory.write",
        "vector_cache.write",
        "persistence.write",
        "api.egress",
        "websocket.broadcast",
    }
)


class Lane5LinuxAPIInterpositionError(RuntimeError):
    pass


def native_gateway_status() -> dict[str, Any]:
    """Read the native 1.59 descriptor when the compiled ABI is available."""
    from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactRuntimeBridge

    if not HHSExactRuntimeBridge.lane5_zero_bypass_validate():
        raise Lane5LinuxAPIInterpositionError("HHS_LANE5_NATIVE_GATEWAY_INVALID")
    descriptor = HHSExactRuntimeBridge.lane5_zero_bypass_descriptor()
    required = {
        "single_production_mutation_path": 1,
        "linux_api_redirect_required": 1,
        "cpp_rna_cell_wall_required": 1,
        "lane5_bios_required": 1,
        "pqc_environmental_firewall_required": 1,
        "four_lane_hydration_required": 1,
        "constraint_forced_execution": 1,
        "policy_choice_authority": 0,
        "hash216_composition_compute_fabric": 1,
        "validated_scoped_reuse_only": 1,
        "hash216_memory_carries_forward": 1,
        "floating_point_canonical_authority": 0,
        "hash216_cache_commit_bypass_allowed": 0,
        "legacy_direct_runtime_bypass_allowed": 0,
    }
    if any(descriptor.get(key) != value for key, value in required.items()):
        raise Lane5LinuxAPIInterpositionError("HHS_LANE5_NATIVE_GATEWAY_DRIFT")
    return {
        "schema": "HHS_PASS219_LANE5_NATIVE_GATEWAY_STATUS_1_59",
        "valid": True,
        "gateway": NATIVE_GATEWAY,
        "descriptor": descriptor,
    }


def interpose_linux_api_request(
    *,
    operation_id: str,
    surface: str = "authorized_execution.call",
    payload: Mapping[str, Any] | None = None,
    request_class: str = "canonical_full_witness_chain",
) -> dict[str, Any]:
    """Redirect one public/runtime request into the Lane 5 governed path."""
    if surface not in _REQUIRED_SURFACES:
        raise Lane5LinuxAPIInterpositionError(
            f"HHS_LANE5_UNREGISTERED_RUNTIME_SURFACE:{surface}"
        )
    request_payload = {
        "schema": "HHS_PASS219_LANE5_LINUX_API_REQUEST_1_59",
        "operation_id": str(operation_id),
        "surface": surface,
        "payload": dict(payload or {}),
        "required_native_gateway": NATIVE_GATEWAY,
        "rna_cpp_cell_wall_required": True,
        "pqc_environmental_firewall_required": True,
        "four_lane_hydration_required": True,
        "constraint_forced_execution": True,
        "policy_choice_authority": False,
        "hash216_validated_scoped_reuse_only": True,
    }
    interposition = interpose_runtime_surface(
        surface=surface,
        request_class=request_class,
        payload=request_payload,
    )
    token = interposition.get("interposition_token")
    propagation = guarded_surface_propagation(
        surface=surface,
        attempted_operation=f"lane5_redirect:{operation_id}",
        payload=request_payload,
        interposition_token=token if isinstance(token, Mapping) else None,
    )
    allowed = bool(
        interposition.get("propagation_allowed")
        and propagation.get("propagation_allowed")
    )
    if not allowed:
        raise Lane5LinuxAPIInterpositionError(
            f"HHS_LANE5_ZERO_BYPASS_REJECTED:{operation_id}"
        )
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "operation_id": str(operation_id),
        "surface": surface,
        "redirected": True,
        "propagation_allowed": True,
        "native_gateway": NATIVE_GATEWAY,
        "canonical_admission_compat_alias": CANONICAL_ADMISSION_COMPAT_ALIAS,
        "lane5_bios_required": True,
        "rna_cpp_cell_wall_required": True,
        "pqc_environmental_firewall_required": True,
        "four_lane_hydration_required": True,
        "constraint_forced_execution": True,
        "policy_choice_authority": False,
        "hash216_validated_scoped_reuse_only": True,
        "hash216_cache_is_commit_authority": False,
        "floating_point_canonical_authority": False,
        "interposition_token_digest72": (token or {}).get("token_digest72"),
        "propagation_receipt_digest72": (
            propagation.get("kernel_witness") or {}
        ).get("digest72"),
    }


__all__ = [
    "CANONICAL_ADMISSION_COMPAT_ALIAS",
    "Lane5LinuxAPIInterpositionError",
    "NATIVE_GATEWAY",
    "SCHEMA",
    "VERSION",
    "interpose_linux_api_request",
    "native_gateway_status",
]
