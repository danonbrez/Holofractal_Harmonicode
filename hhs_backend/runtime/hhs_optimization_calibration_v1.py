"""Shared exact optimization defaults recovered from validated HHS calibration evidence.

This module is intentionally integer-only.  It does not perform similarity,
timing, ranking, or admission itself; it only provides the calibrated bounds
that the authoritative exact runtimes consume.
"""
from __future__ import annotations

import os
from typing import Final

SCHEMA: Final = "HHS_OPTIMIZATION_CALIBRATION_PROFILE_V1"
CLASSIFICATION: Final = "HHS_VALIDATED_EXACT_OPTIMIZATION_DEFAULTS"

PASS205_RETRIEVAL_TOP_K: Final[int] = 32
PASS207_CACHE_BYTES: Final[int] = 512 * 1024 * 1024
PASS207_CACHE_ENTRIES: Final[int] = 512
PASS208_MAX_BRANCHES: Final[int] = 256

CALIBRATION_VECTOR_OBJECTS: Final[int] = 2048
CALIBRATION_VECTOR_QUERY_LIMIT: Final[int] = 512
CALIBRATION_CONTINUATION_TICKS: Final[int] = 360
CALIBRATION_CONTINUATION_SEEDS: Final[tuple[int, ...]] = (
    1,
    5,
    7,
    41,
    64,
    72,
    81,
    144,
    216,
    243,
    5040,
    5184,
    1259713,
)

LEGACY_ADVISORY_ONLY_MODULES: Final[tuple[str, ...]] = (
    "hhs_runtime.hhs_receipt_vector_index_v1",
    "hhs_runtime.python.hhs_receipt_vector_cache_v1",
    "hhs_runtime.python.hhs_predictive_sandbox_engine_v1",
)


def positive_int_env(name: str, default: int) -> int:
    """Resolve one positive integer runtime setting without float coercion."""
    raw = os.environ.get(name)
    value = int(default) if raw is None or not raw.strip() else int(raw, 10)
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def calibrated_profile() -> dict[str, object]:
    """Return the repository-visible calibrated profile using exact values only."""
    return {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "authoritative_float_allowed": False,
        "pass205_retrieval_top_k": PASS205_RETRIEVAL_TOP_K,
        "pass207_cache_bytes": PASS207_CACHE_BYTES,
        "pass207_cache_entries": PASS207_CACHE_ENTRIES,
        "pass208_max_branches": PASS208_MAX_BRANCHES,
        "calibration_vector_objects": CALIBRATION_VECTOR_OBJECTS,
        "calibration_vector_query_limit": CALIBRATION_VECTOR_QUERY_LIMIT,
        "calibration_continuation_ticks": CALIBRATION_CONTINUATION_TICKS,
        "calibration_continuation_seeds": list(CALIBRATION_CONTINUATION_SEEDS),
        "legacy_advisory_only_modules": list(LEGACY_ADVISORY_ONLY_MODULES),
    }
