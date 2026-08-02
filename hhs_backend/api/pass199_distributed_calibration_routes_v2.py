"""Bind the existing Pass 199 route definitions to the canonical V2 runtime."""
from __future__ import annotations

from hhs_backend.api import pass199_distributed_calibration_routes as _routes
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime import (
    PASS199_DISTRIBUTED_CALIBRATION_RUNTIME,
)

_routes.PASS199_DISTRIBUTED_CALIBRATION_FABRIC = PASS199_DISTRIBUTED_CALIBRATION_RUNTIME
router = _routes.router
