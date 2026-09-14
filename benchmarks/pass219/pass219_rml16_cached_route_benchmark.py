#!/usr/bin/env python3
"""Run the unchanged RML16 full-hydration harness through the RML16 route cache.

The baseline benchmark module remains frozen. This additive runner replaces only
its imported RML12 bundle constructor with the validated bounded deterministic
cache successor, then invokes the same main() and command-line parameters.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass219.reciprocal_route_cache import (
    build_and_select_reciprocal_route_cached,
    reciprocal_route_cache_info,
)

BASELINE = ROOT / "benchmarks" / "pass219" / "pass219_rml16_full_hydration_benchmark.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("hhs_pass219_rml16_baseline_for_cache", BASELINE)
    if spec is None or spec.loader is None:
        raise RuntimeError("RML16_BASELINE_BENCHMARK_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # The baseline functions resolve this name from their module globals at call
    # time. No other stage, semantic gate, workload, repeat count, or receipt
    # constructor is replaced.
    module.build_and_select_reciprocal_route = build_and_select_reciprocal_route_cached
    code = int(module.main())
    print(
        json.dumps(
            {
                "schema": "HHS_PASS219_RML16_CACHED_ROUTE_BENCHMARK_SUMMARY_V1",
                "baseline_harness_unchanged": True,
                "replacement_surface": "RML12_BUILD_AND_SELECT_RECIPROCAL_ROUTE_ONLY",
                "route_cache": reciprocal_route_cache_info(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
