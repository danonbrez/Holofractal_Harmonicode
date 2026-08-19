from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

SCHEMA = "HHS_PASS_219B_ANDROID_WEBGPU_FOLD7_TUNING_V1"
TARGET_CODE = "SM-F966U"


def _fraction_obj(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _require_int(obj: dict[str, Any], key: str) -> int:
    value = obj[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def analyze(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("schema") != SCHEMA:
        raise ValueError("unexpected schema")
    target = raw.get("targetDevice") or {}
    if target.get("code") != TARGET_CODE:
        raise ValueError("unexpected target device code")
    if raw.get("claimBoundary", {}).get("authoritativeStateChanged") is not False:
        raise ValueError("benchmark must remain observational")
    results = raw.get("results") or []
    if not results or not all(item.get("exactSelectedSampleEquality") is True for item in results):
        raise ValueError("selected-sample equality must hold for every scaling result")
    factorization = raw.get("factorization") or []
    if not factorization or not all(item.get("exactSelectedSampleEquality") is True for item in factorization):
        raise ValueError("selected-sample equality must hold for every factorization result")

    by_m = {int(item["materializedCombinations"]): item for item in results}
    if 729 not in by_m or 6561 not in by_m:
        raise ValueError("M=729 and M=6561 points are required")
    p1, p2 = by_m[729], by_m[6561]
    t1 = _require_int(p1, "gpuMedianNs")
    t2 = _require_int(p2, "gpuMedianNs")
    if t1 <= 0 or t2 <= t1:
        raise ValueError("large-slice GPU timing must be positive and increasing")

    b = Fraction(t2 - t1, 6561 - 729)
    a = Fraction(t1, 1) - b * 729
    c = a / b if b != 0 else Fraction(0, 1)
    predicted_m1 = a + b

    dense = raw.get("dense") or {}
    flat = raw.get("flatBaseline") or {}
    dense_gpu = _require_int(dense, "gpuMedianNs")
    flat_gpu = _require_int(flat, "gpuMedianNs")
    tuning_gain = Fraction(flat_gpu, dense_gpu) if dense_gpu > 0 else Fraction(0, 1)

    f81 = [item for item in factorization if int(item.get("M", -1)) == 81]
    if len(f81) < 3:
        raise ValueError("equal-volume M=81 factorization sweep is incomplete")
    f_times = [_require_int(item, "gpuMedianNs") for item in f81]
    if any(value <= 0 for value in f_times):
        raise ValueError("factorization GPU timings must be positive")
    f_min, f_max = min(f_times), max(f_times)
    factorization_ratio = Fraction(f_max, f_min)

    observed = []
    for item in results:
        m = int(item["materializedCombinations"])
        gpu = _require_int(item, "gpuMedianNs")
        observed.append({
            "M": m,
            "gpu_median_ns": gpu,
            "ideal_reduction": item["idealReduction"],
            "batch_factor": int(item["batchFactor"]),
        })

    return {
        "schema": "HHS_PASS_219B_I4_FOLD7_TUNING_ANALYSIS_V1",
        "target_device": target,
        "adapter_info": raw.get("adapterInfo", {}),
        "chosen": raw.get("chosen", {}),
        "limits": raw.get("limits", {}),
        "features": raw.get("features", {}),
        "dense_tuned_gpu_ns": dense_gpu,
        "dense_flat_baseline_gpu_ns": flat_gpu,
        "tuned_vs_flat_speedup": _fraction_obj(tuning_gain),
        "large_slice_affine_fit": {
            "equation": "T(M)=a+b*M",
            "point_M1": 729,
            "point_M2": 6561,
            "a_ns": _fraction_obj(a),
            "b_ns_per_materialized_combination": _fraction_obj(b),
            "c_overhead_equivalent_combinations": _fraction_obj(c),
            "predicted_M1_gpu_ns": _fraction_obj(predicted_m1),
        },
        "equal_volume_factorization_M81": {
            "case_count": len(f81),
            "min_gpu_ns": f_min,
            "max_gpu_ns": f_max,
            "max_over_min": _fraction_obj(factorization_ratio),
        },
        "observed_scaling": observed,
        "all_selected_samples_equal": True,
        "authoritative_state_changed": False,
    }


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: analyze_pass219b_fold7_tuning.py INPUT.json [OUTPUT.json]", file=sys.stderr)
        return 2
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = analyze(raw)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
