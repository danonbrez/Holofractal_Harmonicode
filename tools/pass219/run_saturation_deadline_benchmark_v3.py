#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

SCHEMA = "HHS_PASS219_SATURATION_DEADLINE_CONTROLLER_V3"
WINDOWS_NS = [2_000_000_000, 10_000_000_000, 30_000_000_000]
START_LEAD_NS = 2_000_000_000
GROUP_TIMEOUT_PAD_S = 25


def fail(message: str) -> None:
    raise RuntimeError(f"PASS219_SATURATION_V3:{message}")


def exact_ratio(numerator: int, denominator: int) -> dict[str, int]:
    if denominator <= 0:
        return {"numerator": 0, "denominator": 1}
    value = Fraction(numerator, denominator)
    return {"numerator": value.numerator, "denominator": value.denominator}


def affinity_cpus() -> list[int]:
    if hasattr(os, "sched_getaffinity"):
        cpus = sorted(int(cpu) for cpu in os.sched_getaffinity(0))
    else:
        count = os.cpu_count() or 1
        cpus = list(range(count))
    if not cpus:
        fail("NO_AFFINITY_CPUS")
    return cpus


def parse_worker_output(stdout: str, stderr: str, expected_arm: str) -> dict[str, Any]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        fail(f"NO_OUTPUT:{expected_arm}:{stderr[-500:]}")
    try:
        row = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        fail(f"BAD_JSON:{expected_arm}:{exc}:{lines[-1][-500:]}")
    if row.get("schema") != "HHS_PASS219_SATURATION_DEADLINE_V3":
        fail(f"BAD_SCHEMA:{expected_arm}:{row.get('schema')}")
    if row.get("arm") != expected_arm:
        fail(f"BAD_ARM:{expected_arm}:{row.get('arm')}")
    return row


def run_group(
    *,
    executable: Path,
    arm: str,
    window_ns: int,
    target_total: int,
    cpus: list[int],
    a_mode: str | None = None,
) -> dict[str, Any]:
    if window_ns <= 0:
        fail("NONPOSITIVE_WINDOW")
    if target_total < 0:
        fail("NEGATIVE_TARGET")

    start_ns = time.monotonic_ns() + START_LEAD_NS
    workers = len(cpus)
    procs: list[tuple[int, subprocess.Popen[str]]] = []
    for worker_id, cpu in enumerate(cpus):
        env = os.environ.copy()
        if a_mode is not None:
            env["HHS_SAT_V3_A_MODE"] = a_mode
        command = [
            "taskset",
            "-c",
            str(cpu),
            str(executable),
            str(window_ns),
            str(start_ns),
            str(worker_id),
            str(workers),
            str(target_total),
        ]
        procs.append(
            (
                worker_id,
                subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                ),
            )
        )

    rows: list[dict[str, Any]] = []
    timeout_s = START_LEAD_NS / 1_000_000_000 + window_ns / 1_000_000_000 + GROUP_TIMEOUT_PAD_S
    for worker_id, proc in procs:
        try:
            stdout, stderr = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            fail(f"WORKER_TIMEOUT:{arm}:{worker_id}:{stderr[-500:]}")
        if proc.returncode != 0:
            fail(f"WORKER_FAILED:{arm}:{worker_id}:rc={proc.returncode}:{stderr[-1000:]}")
        row = parse_worker_output(stdout, stderr, arm)
        if int(row["worker_id"]) != worker_id:
            fail(f"WORKER_ID_DRIFT:{arm}:{worker_id}:{row['worker_id']}")
        if int(row["worker_count"]) != workers:
            fail(f"WORKER_COUNT_DRIFT:{arm}")
        if int(row["window_ns"]) != window_ns or int(row["start_ns"]) != start_ns:
            fail(f"TIMING_ARGUMENT_DRIFT:{arm}:{worker_id}")
        if int(row["target_total"]) != target_total:
            fail(f"TARGET_DRIFT:{arm}:{worker_id}")
        rows.append(row)

    workset_digests = {int(row["workset_digest64"]) for row in rows}
    workset_bytes = {int(row["workset_bytes"]) for row in rows}
    if len(workset_digests) != 1 or len(workset_bytes) != 1:
        fail(f"WORKSET_DRIFT_WITHIN_GROUP:{arm}")

    completed = sum(int(row["completed"]) for row in rows)
    normalized_capacity = 0
    for row in rows:
        elapsed = int(row["elapsed_ns"])
        done = int(row["completed"])
        if elapsed <= 0:
            fail(f"ZERO_ELAPSED:{arm}:{row['worker_id']}")
        normalized_capacity += (done * window_ns) // elapsed

    target_mode = target_total != 0
    deadline_met = all(bool(row["deadline_met"]) for row in rows) if target_mode else True
    if target_mode:
        expected_worker_total = sum(int(row["target_worker"]) for row in rows)
        if expected_worker_total != target_total:
            fail(f"TARGET_PARTITION_DRIFT:{arm}:{expected_worker_total}!={target_total}")
        if deadline_met and completed != target_total:
            fail(f"FALSE_DEADLINE_PASS:{arm}:{completed}!={target_total}")
        normalized_capacity = completed

    if arm == "A_warm":
        for row in rows:
            done = int(row["completed"])
            if row.get("warm_cache_proved") is not True:
                fail("A_WARM_CACHE_NOT_PROVED")
            for key in ("cache_hits", "branch_resolves", "memoized_compositions", "m_validations", "route_receipts"):
                if int(row.get(key, -1)) != done:
                    fail(f"A_WARM_COUNTER_DRIFT:{key}")
            if int(row.get("fresh_selections", -1)) != 0 or int(row.get("m_binds", -1)) != 0:
                fail("A_WARM_RECOMPUTE_LEAK")
    elif arm == "A_cold":
        for row in rows:
            done = int(row["completed"])
            if int(row.get("fresh_selections", -1)) != done:
                fail("A_COLD_SELECTION_COUNT_DRIFT")
            if int(row.get("m_binds", -1)) != done or int(row.get("m_validations", -1)) != done:
                fail("A_COLD_M_COUNT_DRIFT")
    elif arm == "B":
        for row in rows:
            if row.get("aggregate_abi_linked") is not False or row.get("pass219_features_linked") is not False:
                fail("B_ISOLATION_FLAG_FAILED")
    elif arm == "C":
        for row in rows:
            if row.get("hhs_present") is not False:
                fail("C_HHS_FLAG_FAILED")

    return {
        "arm": arm,
        "window_ns": window_ns,
        "target_total": target_total,
        "worker_count": workers,
        "cpus": cpus,
        "start_ns": start_ns,
        "completed": completed,
        "normalized_capacity": normalized_capacity,
        "deadline_met": deadline_met,
        "completion_fraction": exact_ratio(completed, target_total if target_total else normalized_capacity),
        "deficit": max(0, target_total - completed) if target_mode else 0,
        "workset_digest64": next(iter(workset_digests)),
        "workset_bytes": next(iter(workset_bytes)),
        "workers": rows,
    }


def markdown_report(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Pass 219 — Saturation / Deadline / Warm-Cache Benchmark v3")
    lines.append("")
    lines.append(f"Result: **{result['result']}**")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- C is measured first on a cold plain Ubuntu/x86_64 binary with no HHS symbols.")
    lines.append("- All available runner CPUs are pinned one worker per CPU.")
    lines.append("- Capacity windows are 2 s, 10 s, and 30 s; there is no fixed conservative dataset size.")
    lines.append("- A deterministic 65,536-record / 648-byte virtual working set is prepared outside timed regions and cycled without allocating data proportional to completed operations.")
    lines.append("- The final 30 s capacity of C, B, and A-warm becomes an exact workload target that is cross-fed to every consumer under the same 30 s deadline.")
    lines.append("- A-cold and A-warm retain identical VM81 import/export and per-record Lane 5 route validation. A-warm replaces eligible optimizer/proof recomputation with existing replay-validated H36 cache/reference/memoization surfaces.")
    lines.append("")
    lines.append("## Sustained capacity")
    lines.append("")
    lines.append("| arm | 2 s | 10 s | 30 s | records/s at 30 s |")
    lines.append("|---|---:|---:|---:|---:|")
    curves = result["capacity_curves"]
    for arm in ("C", "B", "A_warm", "A_cold"):
        rows = curves[arm]
        values = [int(row["normalized_capacity"]) for row in rows]
        rps = (values[-1] * 1_000_000_000) // int(rows[-1]["window_ns"])
        lines.append(f"| {arm} | {values[0]:,} | {values[1]:,} | {values[2]:,} | {rps:,} |")
    lines.append("")
    lines.append("## Warm optimization isolation")
    lines.append("")
    warm = int(curves["A_warm"][-1]["normalized_capacity"])
    cold = int(curves["A_cold"][-1]["normalized_capacity"])
    ratio = Fraction(warm, max(1, cold))
    lines.append(f"A-warm / A-cold 30 s capacity = `{ratio.numerator}/{ratio.denominator}` (~{float(ratio):.4f}x).")
    lines.append("")
    lines.append("## Reverse cross-feed deadline matrix")
    lines.append("")
    lines.append("Each row uses the source arm's maximum normalized 30 s capacity as the exact target. `PASS` means the consumer completed the full source target inside the same 30 s deadline; `FAIL` records the observed deficit.")
    lines.append("")
    lines.append("| source target | target records | C | B | A-warm |")
    lines.append("|---|---:|---:|---:|---:|")
    matrix = result["cross_feed"]
    for source in ("C", "B", "A_warm"):
        target = int(matrix[source]["target_records"])
        cells: list[str] = []
        for consumer in ("C", "B", "A_warm"):
            row = matrix[source]["consumers"][consumer]
            if row["deadline_met"]:
                cells.append("PASS")
            else:
                cells.append(f"FAIL (-{int(row['deficit']):,})")
        lines.append(f"| {source} | {target:,} | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")
    lines.append("## Isolation / correctness")
    lines.append("")
    lines.append(f"- Workset digest shared by all arms: `{result['workset_digest64']}`")
    lines.append(f"- Worker CPUs: `{result['cpus']}`")
    lines.append("- A-warm requires cache hit, exact replay, branch-reference resolution, memoized composition, and M-witness validation counters to equal completed operations.")
    lines.append("- B is the immutable v1.1 ABI-only binary; C has no HHS header/object/runtime feature.")
    lines.append("- Timing is observational only; no timing result gains canonical VM81, Hash72, Hash216, or persistence authority.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit(
            f"usage: {sys.argv[0]} A_EXE B_EXE C_EXE RESULT.json REPORT.md"
        )
    a_exe = Path(sys.argv[1]).resolve()
    b_exe = Path(sys.argv[2]).resolve()
    c_exe = Path(sys.argv[3]).resolve()
    result_path = Path(sys.argv[4])
    report_path = Path(sys.argv[5])
    for path in (a_exe, b_exe, c_exe):
        if not path.is_file():
            fail(f"MISSING_EXECUTABLE:{path}")

    cpus = affinity_cpus()
    capacity_curves: dict[str, list[dict[str, Any]]] = {
        "C": [], "B": [], "A_warm": [], "A_cold": []
    }
    workset_digest: int | None = None
    workset_bytes: int | None = None

    arm_specs = [
        ("C", c_exe, None),
        ("B", b_exe, None),
        ("A_warm", a_exe, "warm"),
        ("A_cold", a_exe, "cold"),
    ]

    # C runs first by contract and defines the first saturation envelope.
    for arm, exe, a_mode in arm_specs:
        for window_ns in WINDOWS_NS:
            row = run_group(
                executable=exe,
                arm=arm,
                window_ns=window_ns,
                target_total=0,
                cpus=cpus,
                a_mode=a_mode,
            )
            capacity_curves[arm].append(row)
            if workset_digest is None:
                workset_digest = int(row["workset_digest64"])
                workset_bytes = int(row["workset_bytes"])
            elif int(row["workset_digest64"]) != workset_digest or int(row["workset_bytes"]) != workset_bytes:
                fail(f"GLOBAL_WORKSET_DRIFT:{arm}:{window_ns}")
            print(json.dumps({
                "phase": "capacity",
                "arm": arm,
                "window_ns": window_ns,
                "completed": row["completed"],
                "normalized_capacity": row["normalized_capacity"],
            }, sort_keys=True), flush=True)

    final_window = WINDOWS_NS[-1]
    source_targets = {
        arm: int(capacity_curves[arm][-1]["normalized_capacity"])
        for arm in ("C", "B", "A_warm")
    }
    if any(value <= 0 for value in source_targets.values()):
        fail(f"ZERO_SOURCE_TARGET:{source_targets}")

    cross_feed: dict[str, Any] = {}
    for source in ("C", "B", "A_warm"):
        target = source_targets[source]
        consumers: dict[str, Any] = {}
        # C is always run first so every reverse workload is first grounded in
        # the plain-runner control before B/A consume the identical target.
        for consumer, exe, a_mode in (
            ("C", c_exe, None),
            ("B", b_exe, None),
            ("A_warm", a_exe, "warm"),
        ):
            row = run_group(
                executable=exe,
                arm=consumer,
                window_ns=final_window,
                target_total=target,
                cpus=cpus,
                a_mode=a_mode,
            )
            if int(row["workset_digest64"]) != workset_digest:
                fail(f"CROSS_FEED_WORKSET_DRIFT:{source}:{consumer}")
            consumers[consumer] = row
            print(json.dumps({
                "phase": "cross_feed",
                "source": source,
                "consumer": consumer,
                "target": target,
                "completed": row["completed"],
                "deadline_met": row["deadline_met"],
                "deficit": row["deficit"],
            }, sort_keys=True), flush=True)
        cross_feed[source] = {
            "target_records": target,
            "consumers": consumers,
        }

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "result": "PASS",
        "method": {
            "capacity_windows_ns": WINDOWS_NS,
            "final_deadline_ns": final_window,
            "c_measured_first": True,
            "reverse_cross_feed": True,
            "all_available_cpus": True,
            "cpu_pinning": True,
            "no_target_headroom": True,
            "virtual_workset": True,
            "timing_is_canonical": False,
        },
        "cpus": cpus,
        "worker_count": len(cpus),
        "workset_digest64": workset_digest,
        "workset_bytes": workset_bytes,
        "capacity_curves": capacity_curves,
        "source_targets": source_targets,
        "cross_feed": cross_feed,
        "warm_vs_cold_30s": exact_ratio(
            source_targets["A_warm"],
            int(capacity_curves["A_cold"][-1]["normalized_capacity"]),
        ),
        "authority": {
            "canonical_vm81_mutation": False,
            "canonical_hash72": False,
            "canonical_hash216": False,
            "canonical_persistence": False,
            "timing_authority": False,
        },
    }

    result_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(markdown_report(result), encoding="utf-8")
    print(json.dumps({
        "result": result["result"],
        "workers": result["worker_count"],
        "source_targets": source_targets,
        "warm_vs_cold_30s": result["warm_vs_cold_30s"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
