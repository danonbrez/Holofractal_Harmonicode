from __future__ import annotations

import json
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

SCHEMA = "HHS_PASS_219B_ANDROID_WEBGPU_FUSED_DEPTH2_V1"
Q = 81 * 81


def frac_decimal(value: Fraction, digits: int = 9) -> str:
    getcontext().prec = max(30, digits + 12)
    result = Decimal(value.numerator) / Decimal(value.denominator)
    return f"{result:.{digits}f}"


def fit_affine(points: list[tuple[int, int]]) -> tuple[Fraction, Fraction, Fraction]:
    if len(points) < 2:
        raise ValueError("at least two timestamped points are required")
    n = Fraction(len(points), 1)
    sx = sum((Fraction(x, 1) for x, _ in points), Fraction(0, 1))
    sy = sum((Fraction(y, 1) for _, y in points), Fraction(0, 1))
    sxx = sum((Fraction(x * x, 1) for x, _ in points), Fraction(0, 1))
    sxy = sum((Fraction(x * y, 1) for x, y in points), Fraction(0, 1))
    denom = n * sxx - sx * sx
    if denom == 0:
        raise ValueError("degenerate materialized-combination series")
    b = (n * sxy - sx * sy) / denom
    a = (sy - b * sx) / n
    mean = sy / n
    ss_res = sum(((Fraction(y, 1) - (a + b * x)) ** 2 for x, y in points), Fraction(0, 1))
    ss_tot = sum(((Fraction(y, 1) - mean) ** 2 for _, y in points), Fraction(0, 1))
    r2 = Fraction(1, 1) if ss_tot == 0 else Fraction(1, 1) - ss_res / ss_tot
    return a, b, r2


def main(path: str) -> int:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("schema") != SCHEMA:
        raise SystemExit(f"unexpected schema: {raw.get('schema')!r}")
    if raw.get("potentialPhaseCombinations") != Q:
        raise SystemExit("depth-2 potential combination invariant failed")
    rows = raw.get("results") or []
    if not rows:
        raise SystemExit("no benchmark rows")
    if not all(row.get("exactSelectedSampleEquality") is True for row in rows):
        raise SystemExit("selected/dense sample equality failed")

    points: list[tuple[int, int]] = []
    for row in rows:
        m = int(row["materializedCombinations"])
        gpu = row.get("gpuMedianNs")
        if gpu is not None:
            points.append((m, int(gpu)))

    report: dict[str, object] = {
        "schema": "HHS_PASS_219B_I3_DEPTH2_SCALING_ANALYSIS_V1",
        "source_schema": SCHEMA,
        "potential_combinations": Q,
        "all_selected_sample_equal": True,
        "hardware_gpu_measured": bool(raw.get("claimBoundary", {}).get("hardwareGpuMeasured")),
    }

    if len(points) >= 2:
        a, b, r2 = fit_affine(points)
        c = a / b if b != 0 else None
        report["affine_fit"] = {
            "formula": "T(M)=a+b*M",
            "a_ns_fraction": f"{a.numerator}/{a.denominator}",
            "b_ns_per_combination_fraction": f"{b.numerator}/{b.denominator}",
            "a_ns_decimal": frac_decimal(a, 6),
            "b_ns_per_combination_decimal": frac_decimal(b, 6),
            "r2_fraction": f"{r2.numerator}/{r2.denominator}",
            "r2_decimal": frac_decimal(r2, 12),
            "overhead_equivalent_combinations_fraction": None if c is None else f"{c.numerator}/{c.denominator}",
            "overhead_equivalent_combinations_decimal": None if c is None else frac_decimal(c, 9),
        }
        predictions = []
        if c is not None:
            for row in rows:
                m = int(row["materializedCombinations"])
                predicted = (Fraction(Q, 1) + c) / (Fraction(m, 1) + c)
                observed = Fraction(str(row["observedSpeedup"]))
                predictions.append({
                    "s1": int(row["s1"]),
                    "s2": int(row["s2"]),
                    "M": m,
                    "predicted_speedup": frac_decimal(predicted, 9),
                    "observed_speedup": frac_decimal(observed, 9),
                })
        report["predictions"] = predictions
    else:
        report["affine_fit"] = None
        report["note"] = "GPU timestamp-query unavailable; wall data retained but no GPU affine fit emitted."

    out_path = Path(path).with_name(Path(path).stem + "_analysis.json")
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"analysis_path={out_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: analyze_pass219b_depth2_android.py RESULT.json")
    raise SystemExit(main(sys.argv[1]))
