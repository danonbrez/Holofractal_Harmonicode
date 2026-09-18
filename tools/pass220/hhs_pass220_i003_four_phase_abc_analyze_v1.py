#!/usr/bin/env python3
"""Exact analyzer for Pass 220 I003 four-phase A:B:C max-hardware query calibration."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

PHASES = ("xy", "yx", "zw", "wz")
ARMS = ("A", "B", "C")
EXPECTED_SLOTS = {"xy": (0, 36), "yx": (36, 0), "zw": (18, 54), "wz": (54, 18)}
BASE_COUNTS = (8, 16, 32, 64, 128, 256, 512, 1024, 2048)


def frac_obj(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def rate(completed: int, elapsed_ns: int) -> Fraction:
    if completed <= 0 or elapsed_ns <= 0:
        raise SystemExit("non-positive completed/elapsed sample")
    return Fraction(completed * 1_000_000_000, elapsed_ns)


def analyze(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("result") != "PASS":
        raise SystemExit("native I003 benchmark result is not PASS")
    if tuple(result.get("phases", ())) != PHASES:
        raise SystemExit("four-phase coverage changed")
    if result.get("timing_observational_only") is not True:
        raise SystemExit("timing authority membrane regressed")
    for key in ("candidate_only",):
        if result.get(key) is not True:
            raise SystemExit(f"{key} must remain true")
    for key in ("canonical_vm81_mutation_authority", "canonical_hash72_authority", "canonical_hash216_authority"):
        if result.get(key) is not False:
            raise SystemExit(f"{key} must remain false")

    samples = result.get("samples")
    if not isinstance(samples, list) or not samples:
        raise SystemExit("missing calibration samples")

    grouped: dict[str, list[dict[str, Any]]] = {phase: [] for phase in PHASES}
    exact_samples = []
    totals = {arm: {"completed": 0, "elapsed": 0} for arm in ARMS}
    for sample in samples:
        phase = sample.get("phase")
        if phase not in EXPECTED_SLOTS:
            raise SystemExit("unknown phase sample")
        if (int(sample["phase_slot"]), int(sample["inverse_phase_slot"])) != EXPECTED_SLOTS[phase]:
            raise SystemExit(f"phase geometry mismatch for {phase}")
        order = "".join(sample.get("order", ()))
        if order not in {"ABC", "BCA", "CAB"}:
            raise SystemExit("arm order rotation invalid")
        if sample.get("same_dataset_verified") is not True:
            raise SystemExit("same-dataset invariant failed")
        arms = sample.get("arms")
        if not isinstance(arms, dict) or set(arms) != set(ARMS):
            raise SystemExit("incomplete A:B:C sample")
        grouped[phase].append(sample)

        if sample.get("all_arms_complete"):
            row = {
                "phase": phase,
                "candidate_count": int(sample["candidate_count"]),
                "ratios": {},
            }
            rates = {}
            for arm in ARMS:
                completed = int(arms[arm]["completed"])
                elapsed = int(arms[arm]["elapsed_ns"])
                rates[arm] = rate(completed, elapsed)
                totals[arm]["completed"] += completed
                totals[arm]["elapsed"] += elapsed
            row["ratios"] = {
                "ab": frac_obj(rates["A"] / rates["B"]),
                "ac": frac_obj(rates["A"] / rates["C"]),
                "bc": frac_obj(rates["B"] / rates["C"]),
            }
            exact_samples.append(row)

    phase_summary = {}
    for phase in PHASES:
        rows = grouped[phase]
        if not rows:
            raise SystemExit(f"missing phase {phase}")
        closed = [row for row in rows if row.get("all_arms_complete")]
        if not closed:
            raise SystemExit(f"phase {phase} has no closed calibration point")
        observed_max = max(int(row["candidate_count"]) for row in closed)
        declared_max = int(result["phase_max_hardware_closed_n"][phase])
        if observed_max != declared_max:
            raise SystemExit(f"phase {phase} max hardware N mismatch")
        base_seen = {int(row["candidate_count"]) for row in rows if int(row["candidate_count"]) in BASE_COUNTS}
        if 8 not in base_seen:
            raise SystemExit(f"phase {phase} missing base calibration")
        phase_summary[phase] = {
            "max_hardware_closed_n": declared_max,
            "sample_count": len(rows),
            "closed_sample_count": len(closed),
        }

    global_rates = {arm: rate(totals[arm]["completed"], totals[arm]["elapsed"]) for arm in ARMS}
    global_max = min(value["max_hardware_closed_n"] for value in phase_summary.values())
    if global_max != int(result["global_max_hardware_closed_n"]):
        raise SystemExit("global max hardware N mismatch")

    return {
        "schema": "HHS_PASS_220_I003_FOUR_PHASE_ABC_MAX_HARDWARE_ANALYSIS_V1",
        "four_phase_coverage": True,
        "same_dataset_verified": True,
        "global_max_hardware_closed_n": global_max,
        "phase_summary": phase_summary,
        "global": {
            "a_rate": frac_obj(global_rates["A"]),
            "b_rate": frac_obj(global_rates["B"]),
            "c_rate": frac_obj(global_rates["C"]),
            "ab_ratio": frac_obj(global_rates["A"] / global_rates["B"]),
            "ac_ratio": frac_obj(global_rates["A"] / global_rates["C"]),
            "bc_ratio": frac_obj(global_rates["B"] / global_rates["C"]),
        },
        "closed_samples": exact_samples,
        "timing_observational_only": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "result": "PASS",
    }


def write_report(result: dict[str, Any], path: Path) -> None:
    lines = [
        "# Pass 220 I003 — Four-phase A:B:C max-hardware query calibration",
        "",
        f"- Result: **{result['result']}**",
        f"- Global all-phase max closed N: **{result['global_max_hardware_closed_n']}**",
        "- Timing: observational only",
        "- Canonical mutation/Hash72/Hash216 authority: unchanged / false",
        "",
        "## Phase maxima",
        "",
    ]
    for phase in PHASES:
        item = result["phase_summary"][phase]
        lines.append(f"- {phase}: max closed N = {item['max_hardware_closed_n']} ({item['closed_sample_count']} closed samples)")
    g = result["global"]
    lines.extend([
        "",
        "## Exact aggregate ratios",
        "",
        f"- A:B = {g['ab_ratio']['numerator']}/{g['ab_ratio']['denominator']}",
        f"- A:C = {g['ac_ratio']['numerator']}/{g['ac_ratio']['denominator']}",
        f"- B:C = {g['bc_ratio']['numerator']}/{g['bc_ratio']['denominator']}",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("report")
    args = parser.parse_args()
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = analyze(source)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_report(result, Path(args.report))
    print(json.dumps({"result": result["result"], "global_max_hardware_closed_n": result["global_max_hardware_closed_n"], "global": result["global"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
