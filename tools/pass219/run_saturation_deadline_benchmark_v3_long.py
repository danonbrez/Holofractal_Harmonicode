#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys

import run_saturation_deadline_benchmark_v3 as core

# Long-window production calibration. The short controller remains available as
# a fast developer smoke surface; this wrapper is the authoritative v3 run.
core.WINDOWS_NS = [5_000_000_000, 20_000_000_000, 60_000_000_000]
core.START_LEAD_NS = 8_000_000_000
core.GROUP_TIMEOUT_PAD_S = 35


def corrected_deadline(row: dict) -> bool:
    if int(row["target_total"]) == 0:
        return True
    return (
        int(row["completed"]) == int(row["target_worker"])
        and int(row["elapsed_ns"]) <= int(row["window_ns"])
    )


def rewrite_report(result: dict) -> str:
    curves = result["capacity_curves"]
    lines: list[str] = [
        "# Pass 219 — Saturation / Deadline / Warm-Cache Benchmark v3",
        "",
        f"Result: **{result['result']}**",
        "",
        "## Method",
        "",
        "- C is measured first as the cold plain Ubuntu/x86_64 control with no HHS symbols.",
        "- All CPUs exposed by the runner affinity mask are saturated with one pinned worker process per CPU.",
        "- Capacity windows are 5 s, 20 s, and 60 s; the 60 s result defines each source arm's sustained maximum workload for reverse cross-feed.",
        "- A deterministic 65,536-record × 648-byte virtual working set is prepared outside timed regions and cycled without allocating data proportional to completed operations.",
        "- C, B, and A-warm each define a 60 s capacity target. Every target is then supplied unchanged to C, B, and A-warm under the same 60 s deadline with zero safety headroom.",
        "- A-cold and A-warm retain identical VM81 import/export and per-record Lane 5 route validation. A-warm only replaces eligible optimizer/proof recomputation with repository-native replay-validated H36 cache/reference/memoization surfaces.",
        "- A warm construction occurs before the synchronized timer. Its measured fill duration must fit inside the 8 s pre-start runway; it is never charged to warm throughput.",
        "",
        "## Sustained capacity",
        "",
        "| arm | 5 s | 20 s | 60 s | records/s at 60 s |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ("C", "B", "A_warm", "A_cold"):
        rows = curves[arm]
        values = [int(row["normalized_capacity"]) for row in rows]
        rps = (values[-1] * 1_000_000_000) // int(rows[-1]["window_ns"])
        lines.append(
            f"| {arm} | {values[0]:,} | {values[1]:,} | {values[2]:,} | {rps:,} |"
        )

    warm = int(curves["A_warm"][-1]["normalized_capacity"])
    cold = int(curves["A_cold"][-1]["normalized_capacity"])
    ratio = Fraction(warm, max(1, cold))
    lines += [
        "",
        "## Warm optimization isolation",
        "",
        f"A-warm / A-cold 60 s capacity = `{ratio.numerator}/{ratio.denominator}` (~{float(ratio):.6f}×).",
        "",
        "## Reverse cross-feed deadline matrix",
        "",
        "Each row uses the source arm's sustained 60 s capacity as the exact target. PASS requires every worker to finish its exact partition within its own 60 s timed interval; otherwise the observed deficit is retained.",
        "",
        "| source target | target records | C | B | A-warm |",
        "|---|---:|---:|---:|---:|",
    ]
    matrix = result["cross_feed"]
    for source in ("C", "B", "A_warm"):
        target = int(matrix[source]["target_records"])
        cells: list[str] = []
        for consumer in ("C", "B", "A_warm"):
            row = matrix[source]["consumers"][consumer]
            cells.append(
                "PASS" if row["deadline_met"] else f"FAIL (-{int(row['deficit']):,})"
            )
        lines.append(
            f"| {source} | {target:,} | {cells[0]} | {cells[1]} | {cells[2]} |"
        )

    lines += [
        "",
        "## Isolation / correctness",
        "",
        f"- Workset digest shared by every arm: `{result['workset_digest64']}`.",
        f"- Worker CPUs: `{result['cpus']}`.",
        f"- Maximum observed A warm-fill duration: `{result['warm_fill_max_ns']}` ns, pre-start runway: `{core.START_LEAD_NS}` ns.",
        "- A-warm requires cache-hit, replay, branch-reference, memoized-composition, M-witness-validation, and Lane 5 receipt counters to equal completed operations.",
        "- B remains the immutable v1.1 ABI-only control; C contains no HHS feature.",
        "- Timing is observational only and grants no canonical VM81, Hash72, Hash216, or persistence authority.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit(
            f"usage: {sys.argv[0]} A_EXE B_EXE C_EXE RESULT.json REPORT.md"
        )
    result_path = Path(sys.argv[4])
    report_path = Path(sys.argv[5])

    rc = core.main()
    if rc != 0:
        return rc

    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("method", {}).get("capacity_windows_ns") != core.WINDOWS_NS:
        raise RuntimeError("PASS219_SATURATION_V3:LONG_WINDOW_CONFIGURATION_DRIFT")

    warm_fill_values: list[int] = []
    for arm in ("A_warm", "A_cold"):
        for group in result["capacity_curves"][arm]:
            for row in group["workers"]:
                warm_fill_values.append(int(row["warm_fill_ns"]))
    for source in ("C", "B", "A_warm"):
        group = result["cross_feed"][source]["consumers"]["A_warm"]
        for row in group["workers"]:
            warm_fill_values.append(int(row["warm_fill_ns"]))

    warm_fill_max = max(warm_fill_values, default=0)
    # Keep at least one full second between the largest measured warm-fill and
    # the synchronized timed start. If this fails, the benchmark is invalid;
    # increase the runway rather than charging construction to the warm path.
    if warm_fill_max + 1_000_000_000 >= core.START_LEAD_NS:
        raise RuntimeError(
            f"PASS219_SATURATION_V3:PRESTART_RUNWAY_TOO_SHORT:{warm_fill_max}"
        )

    # Correct deadline acceptance independently of the native batch-stop flag:
    # completion must equal the exact target partition AND the worker's timed
    # elapsed interval must not exceed the requested deadline.
    for source in ("C", "B", "A_warm"):
        source_row = result["cross_feed"][source]
        target = int(source_row["target_records"])
        for consumer in ("C", "B", "A_warm"):
            group = source_row["consumers"][consumer]
            flags = [corrected_deadline(row) for row in group["workers"]]
            met = all(flags) and int(group["completed"]) == target
            group["deadline_met"] = met
            group["deficit"] = max(0, target - int(group["completed"]))
            group["completion_fraction"] = core.exact_ratio(
                int(group["completed"]), target
            )

    result["method"]["prestart_runway_ns"] = core.START_LEAD_NS
    result["method"]["deadline_requires_elapsed_within_window"] = True
    result["method"]["long_window_authoritative"] = True
    result["warm_fill_max_ns"] = warm_fill_max
    result["warm_vs_cold_60s"] = result.pop("warm_vs_cold_30s")
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path.write_text(rewrite_report(result), encoding="utf-8")

    print(
        json.dumps(
            {
                "result": result["result"],
                "windows_ns": core.WINDOWS_NS,
                "worker_count": result["worker_count"],
                "source_targets": result["source_targets"],
                "warm_fill_max_ns": warm_fill_max,
                "warm_vs_cold_60s": result["warm_vs_cold_60s"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
