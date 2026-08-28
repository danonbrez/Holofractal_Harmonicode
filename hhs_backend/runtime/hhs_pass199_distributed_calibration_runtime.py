"""Canonical production projection for the repaired Pass 199 runtime."""
from __future__ import annotations

from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v3 import (
    PRODUCTION_VERSION,
    REPAIR_SCHEMA,
    Pass199DistributedCalibrationRuntime,
)


PASS199_DISTRIBUTED_CALIBRATION_RUNTIME = Pass199DistributedCalibrationRuntime()

__all__ = [
    "PRODUCTION_VERSION",
    "REPAIR_SCHEMA",
    "Pass199DistributedCalibrationRuntime",
    "PASS199_DISTRIBUTED_CALIBRATION_RUNTIME",
]
