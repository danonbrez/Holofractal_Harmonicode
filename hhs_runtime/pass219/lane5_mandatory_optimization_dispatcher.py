"""Production facade for the Pass 219 mandatory Lane 5 optimizer.

The implementation is kept in ``lane5_mandatory_optimization_dispatcher_impl``.
This facade supplies the mandatory persistent state root so stateful composition
reuse is available by default instead of requiring an opt-in constructor
argument. It also binds the repository's validated optimization-generalization
manifests into the production capability/status surface so newly proven
compatible optimizations cannot become invisible to the latency/composition
agent.

RML20 is also bound here as a typed native transport capability. It requires an
exact 648-byte VM5184 carrier plus a frozen RML17 address/direction coordinate;
it is therefore visible to the production agent without being guessed onto
Hash216-only requests that do not carry those typed inputs.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher_impl import (
    Lane5MandatoryOptimizationError,
    MANDATORY_CAPABILITY_ROLES as _BASE_MANDATORY_CAPABILITY_ROLES,
    MANDATORY_LANE5_LINEAGE as _BASE_MANDATORY_LANE5_LINEAGE,
    Pass219Lane5MandatoryOptimizationDispatcher as _DispatcherImpl,
    SCHEMA,
)
from hhs_runtime.pass219.lane5_mandatory_optimization_registry import (
    build_mandatory_optimization_registry,
)
from hhs_runtime.pass219.rml20_rna_vm5184_cell_wall_bridge import (
    RML20NativeBridgeError,
    route_rml17_candidate_through_rna_vm5184,
)

DEFAULT_STATE_ROOT_ENV = "HHS_PASS219_LANE5_STATE_ROOT"
DEFAULT_STATE_ROOT = Path(".hhs/pass219/lane5").resolve()
RML20_CAPABILITY_ID = "RML20_RNA_VM5184_CELL_WALL_BRIDGE"

MANDATORY_LANE5_LINEAGE = _BASE_MANDATORY_LANE5_LINEAGE + (
    RML20_CAPABILITY_ID,
)
MANDATORY_CAPABILITY_ROLES = dict(_BASE_MANDATORY_CAPABILITY_ROLES)
MANDATORY_CAPABILITY_ROLES[RML20_CAPABILITY_ID] = (
    "EXACT_RML17_RNA_VM5184_TRANSPORT"
)


class Pass219Lane5MandatoryOptimizationDispatcher(_DispatcherImpl):
    """Mandatory dispatcher with persistent composition memory enabled by default."""

    def __init__(
        self,
        *,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
        state_root: str | Path | None = None,
        vector_key: bytes | None = None,
    ) -> None:
        resolved_state_root = Path(
            state_root
            or os.getenv(DEFAULT_STATE_ROOT_ENV)
            or DEFAULT_STATE_ROOT
        ).resolve()
        super().__init__(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
            state_root=resolved_state_root,
            vector_key=vector_key,
        )

    @staticmethod
    def optimization_registry_snapshot() -> dict[str, Any]:
        """Validate and expose all repository-declared optimization obligations."""
        return build_mandatory_optimization_registry()

    @staticmethod
    def _inject_rml20_surface(result: dict[str, Any]) -> dict[str, Any]:
        result["mandatory_lineage"] = list(MANDATORY_LANE5_LINEAGE)
        result["mandatory_capability_roles"] = dict(MANDATORY_CAPABILITY_ROLES)
        result["rml20_rna_vm5184_transport"] = "LAZY_MANDATORY"
        result["rml20_typed_inputs"] = [
            "exact_648_byte_vm5184_carrier",
            "rml17_source_address",
            "reciprocal_transport_direction",
        ]
        return result

    def status(self) -> dict[str, Any]:
        result = self._inject_rml20_surface(dict(super().status()))
        result["optimization_generalization_registry"] = (
            self.optimization_registry_snapshot()
        )
        result["manifest_proven_optimizations_visible"] = True
        return result

    def capability_snapshot(self) -> dict[str, Any]:
        result = self._inject_rml20_surface(dict(super().capability_snapshot()))
        result["optimization_generalization_registry"] = (
            self.optimization_registry_snapshot()
        )
        result["manifest_proven_optimizations_visible"] = True
        return result

    def search_hash216(self, **kwargs: Any) -> dict[str, Any]:
        """Preserve Hash216 compatibility while declaring typed RML20 availability."""
        result = dict(super().search_hash216(**kwargs))
        available = list(result.get("optimization_available", ()))
        if RML20_CAPABILITY_ID not in available:
            available.append(RML20_CAPABILITY_ID)
        result["optimization_available"] = available
        typed = list(result.get("typed_optimizers_require_typed_inputs", ()))
        if RML20_CAPABILITY_ID not in typed:
            typed.append(RML20_CAPABILITY_ID)
        result["typed_optimizers_require_typed_inputs"] = typed
        return result

    def route_rml20_candidate(
        self,
        raw_frame_le: bytes | bytearray | memoryview,
        source_address: int,
        direction: str,
        *,
        library_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """Run the proven RML20 RML17->RNA/VM5184 exact transport bridge."""
        try:
            result = dict(
                route_rml17_candidate_through_rna_vm5184(
                    raw_frame_le,
                    source_address,
                    direction,
                    library_path=library_path,
                )
            )
        except RML20NativeBridgeError as exc:
            raise Lane5MandatoryOptimizationError(
                f"RML20_MANDATORY_TRANSPORT_UNAVAILABLE:{exc}"
            ) from exc

        authority = dict(result.get("authority", {}))
        required_false = (
            "canonical_vm81_mutation_authority",
            "canonical_hash72_mint_authority",
            "canonical_hash216_persistence_authority",
            "canonical_persistence_authority",
            "floating_point_authority",
        )
        if authority.get("candidate_only") is not True:
            raise Lane5MandatoryOptimizationError("RML20_CANDIDATE_ONLY_BOUNDARY_DRIFT")
        if authority.get("exact_integer_only") is not True:
            raise Lane5MandatoryOptimizationError("RML20_EXACT_INTEGER_BOUNDARY_DRIFT")
        if any(authority.get(key) is not False for key in required_false):
            raise Lane5MandatoryOptimizationError("RML20_CANONICAL_AUTHORITY_ESCALATION")
        if not all(dict(result.get("parity", {})).values()):
            raise Lane5MandatoryOptimizationError("RML20_RML17_NATIVE_PARITY_DRIFT")

        result["mandatory_optimization_dispatch"] = True
        result["optimization_selected"] = RML20_CAPABILITY_ID
        result["fresh_recomputation_forced"] = False
        return result


# Explicit name for the production latency-search/composition role.
Pass219Lane5LatencyCompositionAgent = Pass219Lane5MandatoryOptimizationDispatcher


__all__ = [
    "DEFAULT_STATE_ROOT",
    "DEFAULT_STATE_ROOT_ENV",
    "Lane5MandatoryOptimizationError",
    "MANDATORY_CAPABILITY_ROLES",
    "MANDATORY_LANE5_LINEAGE",
    "Pass219Lane5LatencyCompositionAgent",
    "Pass219Lane5MandatoryOptimizationDispatcher",
    "RML20_CAPABILITY_ID",
    "SCHEMA",
]
