"""Pass 215 Iteration 4 serialized-evidence validator v2.

The v1 execution semantics remain authoritative.  This wrapper canonicalizes
named mapping sets back into contract order before invoking the v1 validator so
JSON writers using sort_keys=True cannot create a false validation failure.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as v1
from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v1 import *  # noqa: F401,F403

SERIALIZED_VALIDATION_VERSION = "2.0.0-serialization-order-hardening"


def validate_execution_evidence(evidence: Mapping[str, Any]) -> None:
    normalized = deepcopy(dict(evidence))
    for field, order in (
        ("frozen_workload_modes", v1.FROZEN_MODES),
        ("frozen_profile_comparisons", v1.FROZEN_COMPARISONS),
        ("pass214_stage_dispositions", v1.PASS214_STAGES),
    ):
        value = normalized.get(field)
        if isinstance(value, Mapping) and set(value) == set(order):
            normalized[field] = {key: value[key] for key in order}
    optimizations = normalized.get("optimization_class_dispositions")
    if isinstance(optimizations, Mapping) and set(optimizations) == set(v1.FROZEN_OPTIMIZATION_CLASSES):
        normalized["optimization_class_dispositions"] = {
            key: optimizations[key] for key in v1.FROZEN_OPTIMIZATION_CLASSES
        }
    v1.validate_execution_evidence(normalized)


def validate_serialized_round_trip(evidence: Mapping[str, Any]) -> None:
    """Alias documenting the v2 purpose for tests and CLI surfaces."""
    validate_execution_evidence(evidence)


__all__ = list(v1.__all__) + [
    "SERIALIZED_VALIDATION_VERSION",
    "validate_execution_evidence",
    "validate_serialized_round_trip",
]
