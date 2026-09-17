#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import json
import pathlib
import sys

ARMS = ("A", "B", "C")
PHASES = ("xy", "yx", "zw", "wz")


def ratio_dict(value: Fraction) -> dict:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "basis_points_floor": (value.numerator * 10000) // value.denominator,
    }


def aggregate(rows: list[dict]) -> dict:
    totals = {a: {"completed": 0, "elapsed_ns": 0} for a in ARMS}
    for row in rows:
        a = row["arm"]
        totals[a]["completed"] += int(row["completed"])
        totals[a]["elapsed_ns"] += int(row["elapsed_ns"])
    rates = {
        a: Fraction(totals[a]["completed"] * 1_000_000_000, totals[a]["elapsed_ns"])
        for a in ARMS
    }
    return {
        "totals": totals,
        "rates": {a: {"numerator": rates[a].numerator, "denominator": rates[a].denominator} for a in ARMS},
        "A_over_B": ratio_dict(rates["A"] / rates["B"]),
        "A_over_C": ratio_dict(rates["A"] / rates["C"]),
        "B_over_C": ratio_dict(rates["B"] / rates["C"]),
    }


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit(f"usage: {sys.argv[0]} INPUT.jsonl RESULT.json REPORT.md")
    input_path = pathlib.Path(sys.argv[1])
    result_path = pathlib.Path(sys.argv[2])
    report_path = pathlib.Path(sys.argv[3])
    rows = [json.loads(line) for line in input_path.read_text().splitlines() if line.strip()]
    meta = next(row for row in rows if row.get("type") == "meta")
    terminal = next(row for row in rows if row.get("type") == "result")
    arms = [row for row in rows if row.get("type") == "arm"]

    if terminal.get("result") != "PASS" or terminal.get("triplet_samples") != 36:
        raise RuntimeError("native triplet benchmark did not complete all 36 samples")
    if len(arms) != 108:
        raise RuntimeError(f"expected 108 arm rows, got {len(arms)}")

    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in arms:
        grouped[row["sample_id"]][row["arm"]] = row
    if len(grouped) != 36:
        raise RuntimeError(f"expected 36 sample groups, got {len(grouped)}")

    ranks = set()
    phases = set()
    for sample_id, trio in grouped.items():
        if set(trio) != set(ARMS):
            raise RuntimeError(f"incomplete trio {sample_id}: {sorted(trio)}")
        a, b, c = trio["A"], trio["B"], trio["C"]
        if not (a["completed"] == b["completed"] == c["completed"] == a["target_count"]):
            raise RuntimeError(f"count mismatch {sample_id}")
        if not (a["payload_digest"] == b["payload_digest"] == c["payload_digest"]):
            raise RuntimeError(f"payload mismatch {sample_id}")
        if not (a["input_digest"] == b["input_digest"] == c["input_digest"] == a["payload_digest"]):
            raise RuntimeError(f"input/output digest mismatch {sample_id}")
        if not (a["aggregate_abi_linked"] and a["pass219_features_linked"] and a["lane5_called"] and a["h36_hash216_m_called"]):
            raise RuntimeError(f"A is not full stack in {sample_id}")
        if b["aggregate_abi_linked"] or b["pass219_features_linked"] or b["lane5_called"] or b["h36_hash216_m_called"]:
            raise RuntimeError(f"B isolation failure in {sample_id}")
        if c["hhs_headers"] or c["hhs_objects_linked"] or c["hhs_runtime_calls"] or c["lane5_called"]:
            raise RuntimeError(f"C HHS contamination in {sample_id}")
        ranks.add(int(a["rank"]))
        phases.add(a["phase"])

    if ranks != set(range(1, 10)) or phases != set(PHASES):
        raise RuntimeError("difficulty/phase coverage incomplete")

    global_summary = aggregate(arms)
    phase_summary = {phase: aggregate([r for r in arms if r["phase"] == phase]) for phase in PHASES}
    rank_summary = {str(rank): aggregate([r for r in arms if int(r["rank"]) == rank]) for rank in range(1, 10)}

    result = {
        "schema": "HHS_PASS219_ISOLATED_STACK_BENCHMARK_V2_RESULT",
        "result": "PASS",
        "dataset_sha256": meta["dataset_sha256"],
        "triplet_samples": 36,
        "difficulty_ranks_seen": list(range(1, 10)),
        "four_phase_coverage": True,
        "same_dataset_verified": True,
        "isolation": {
            "A_full_aggregate_lane5_m_stack": True,
            "B_immutable_v1_1_base_abi_only": True,
            "C_plain_x86_64_ubuntu_no_hhs": True,
            "common_compiler_optimization_is_control_variable": True,
        },
        "global": global_summary,
        "phase_summary": phase_summary,
        "rank_summary": rank_summary,
        "physical_energy_measured": False,
    }
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    g = global_summary
    report = [
        "# Pass 219 — Isolated Full Stack vs Base ABI vs Plain x86_64 Benchmark v2",
        "",
        "## Isolation",
        "",
        "- A: aggregate exact ABI public serialization + Lane 5 route/admission + direct H36/Hash216 M proof.",
        "- B: immutable exact v1.1 base ABI VM81 import/export only; no aggregate or Pass 219 optimization object linked.",
        "- C: standalone libc/native x86_64 copy/verify path; no HHS header, object, runtime call, receipt, or feature.",
        "- Dataset generation and file loading are outside timed regions.",
        "- All three binaries are compiled with the same ordinary compiler optimization flags as an environmental control.",
        "",
        "## Global exact normalization",
        "",
        "| ratio | exact | basis-point floor |",
        "|---|---:|---:|",
    ]
    for label, key in (("A:B", "A_over_B"), ("A:C", "A_over_C"), ("B:C", "B_over_C")):
        r = g[key]
        report.append(f"| {label} | `{r['numerator']}/{r['denominator']}` | {r['basis_points_floor']} |")
    report.extend([
        "",
        "## Global totals",
        "",
        "| arm | completed records | elapsed ns | exact records/s |",
        "|---|---:|---:|---:|",
    ])
    for arm in ARMS:
        t = g["totals"][arm]
        r = g["rates"][arm]
        report.append(f"| {arm} | {t['completed']} | {t['elapsed_ns']} | `{r['numerator']}/{r['denominator']}` |")
    report.extend([
        "",
        "## Per-phase normalization",
        "",
        "| phase | A:B bp | A:C bp | B:C bp |",
        "|---|---:|---:|---:|",
    ])
    for phase in PHASES:
        p = phase_summary[phase]
        report.append(
            f"| {phase} | {p['A_over_B']['basis_points_floor']} | "
            f"{p['A_over_C']['basis_points_floor']} | {p['B_over_C']['basis_points_floor']} |"
        )
    report.extend([
        "",
        "These ratios are performance measurements for this dataset and runner only. They do not grant physical-energy semantics or canonical authority to any benchmark arm.",
        "",
    ])
    report_path.write_text("\n".join(report))
    print(json.dumps({
        "result": "PASS",
        "triplet_samples": 36,
        "dataset_sha256": meta["dataset_sha256"],
        "A_over_B": g["A_over_B"],
        "A_over_C": g["A_over_C"],
        "B_over_C": g["B_over_C"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
