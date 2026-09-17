"""Compatibility facade for Pass 219 non-agentic allegorical warm hydration.

The implementation body is preserved verbatim in the legacy module.  The
public default Lane 5 search factory is intentionally overridden here so old
callers cannot silently fall back to the obsolete 1.37-only production
binding.  All proven Lane 5 optimization surfaces are reachable through the
mandatory dispatcher.
"""
from __future__ import annotations

from hhs_runtime.hhs_pass219_nonagentic_allegorical_warm_hydration_legacy_v1 import *  # noqa: F401,F403
from hhs_runtime.hhs_pass219_nonagentic_allegorical_warm_hydration_legacy_v1 import (
    __all__ as _LEGACY_ALL,
)
from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    Pass219Lane5MandatoryOptimizationDispatcher,
)


def default_lane5_search(
    *,
    backend: str = "CPU_REFERENCE",
    state_root: str | None = None,
) -> Pass219Lane5MandatoryOptimizationDispatcher:
    """Return the mandatory accumulated Lane 5 optimization dispatcher."""
    return Pass219Lane5MandatoryOptimizationDispatcher(
        backend=backend,
        state_root=state_root,
    )


__all__ = [name for name in _LEGACY_ALL if name != "default_lane5_search"] + [
    "default_lane5_search",
]
