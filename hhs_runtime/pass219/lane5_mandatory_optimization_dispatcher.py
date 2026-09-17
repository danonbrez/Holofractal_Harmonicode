"""Production facade for the Pass 219 mandatory Lane 5 optimizer.

The implementation is kept in ``lane5_mandatory_optimization_dispatcher_impl``.
This facade supplies the mandatory persistent state root so stateful composition
reuse is available by default instead of requiring an opt-in constructor
argument. It also binds the repository's validated optimization-generalization
manifests into the production capability/status surface so newly proven
compatible optimizations cannot become invisible to the latency/composition
agent.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher_impl import (
    Lane5MandatoryOptimizationError,
    MANDATORY_CAPABILITY_ROLES,
    MANDATORY_LANE5_LINEAGE,
    Pass219Lane5MandatoryOptimizationDispatcher as _DispatcherImpl,
    SCHEMA,
)
from hhs_runtime.pass219.lane5_mandatory_optimization_registry import (
    build_mandatory_optimization_registry,
)

DEFAULT_STATE_ROOT_ENV = "HHS_PASS219_LANE5_STATE_ROOT"
DEFAULT_STATE_ROOT = Path(".hhs/pass219/lane5").resolve()


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

    def status(self) -> dict[str, Any]:
        result = dict(super().status())
        result["optimization_generalization_registry"] = (
            self.optimization_registry_snapshot()
        )
        result["manifest_proven_optimizations_visible"] = True
        return result

    def capability_snapshot(self) -> dict[str, Any]:
        result = dict(super().capability_snapshot())
        result["optimization_generalization_registry"] = (
            self.optimization_registry_snapshot()
        )
        result["manifest_proven_optimizations_visible"] = True
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
    "SCHEMA",
]
