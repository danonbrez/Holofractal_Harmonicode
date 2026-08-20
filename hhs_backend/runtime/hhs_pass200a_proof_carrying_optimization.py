"""Canonical production projection for repaired Pass 200A shadow optimization."""
from __future__ import annotations

from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization_v2 import (
    BUNDLE_SCHEMA,
    CLASSIFICATION,
    CONTRACT,
    DEFAULT_HOLDOUTS,
    DEFAULT_SHADOW_CONFIG,
    ENVELOPE_SCHEMA,
    EVENT_SCHEMA,
    NONPRODUCTION_CLASSIFICATION,
    OPERATION_ID,
    PASS200A_LEGACY_SINGLETON,
    PRODUCTION_TOTALS,
    REPAIR_CLASSIFICATION,
    REPAIR_SCHEMA,
    SHADOW_PLAN_SCHEMA,
    SHADOW_RUN_SCHEMA,
    VERSION,
    Pass200AError,
    Pass200AProofCarryingOptimizationAuthority,
)

# V1 historically constructed its singleton at import time.  Repair-forward the
# same object in place so every existing reference sees the corrected V2 class;
# never create a second default-state authority for the same SQLite/Pass199 root.
if not isinstance(PASS200A_LEGACY_SINGLETON, Pass200AProofCarryingOptimizationAuthority):
    PASS200A_LEGACY_SINGLETON.__class__ = Pass200AProofCarryingOptimizationAuthority

PASS200A_OPTIMIZATION_AUTHORITY = PASS200A_LEGACY_SINGLETON

__all__ = [
    "BUNDLE_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "DEFAULT_HOLDOUTS",
    "DEFAULT_SHADOW_CONFIG",
    "ENVELOPE_SCHEMA",
    "EVENT_SCHEMA",
    "NONPRODUCTION_CLASSIFICATION",
    "OPERATION_ID",
    "PASS200A_OPTIMIZATION_AUTHORITY",
    "PRODUCTION_TOTALS",
    "REPAIR_CLASSIFICATION",
    "REPAIR_SCHEMA",
    "Pass200AError",
    "Pass200AProofCarryingOptimizationAuthority",
    "SHADOW_PLAN_SCHEMA",
    "SHADOW_RUN_SCHEMA",
    "VERSION",
]
