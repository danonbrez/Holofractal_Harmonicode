import csv
import json
import statistics
import subprocess
import time
from pathlib import Path

OUT = Path("bench_results")
EXE = "./build/hhs_vm81"


def percentile(values, p):
    values = sorted(values)
    k = (len(values) - 1) * p
    a = int(k)
    b = min(a + 1, len(values) - 1)
    return values[a] + (values[b] - values[a]) * (k - a)


workloads = {
    "cli_1_step": ["--no-trace", "--steps", "1"],
    "cli_full_demo": ["--no-trace", "--steps", "128"],
    "cli_verify": ["--no-trace", "--verify"],
    "cli_halt_on_orbit_verify": ["--no-trace", "--halt-on-orbit", "--verify"],
}

rows = []
for name, args in workloads.items():
    cmd = [EXE, *args]
    for _ in range(20):
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    samples = []
    for _ in range(500):
        t0 = time.perf_counter_ns()
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        samples.append(time.perf_counter_ns() - t0)
    rows.append(
        {
            "workload": name,
            "runs": len(samples),
            "median_us": statistics.median(samples) / 1e3,
            "mean_us": statistics.mean(samples) / 1e3,
            "stdev_us": statistics.pstdev(samples) / 1e3,
            "min_us": min(samples) / 1e3,
            "p95_us": percentile(samples, 0.95) / 1e3,
            "p99_us": percentile(samples, 0.99) / 1e3,
            "max_us": max(samples) / 1e3,
            "median_runs_per_s": 1e9 / statistics.median(samples),
        }
    )

with (OUT / "process.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
(OUT / "process.json").write_text(json.dumps(rows, indent=2))

builds = []
for opt in ("O0", "O2", "O3"):
    samples = []
    for i in range(30):
        path = Path(f"build/tmp_{opt}_{i}")
        t0 = time.perf_counter_ns()
        subprocess.run(
            [
                "gcc",
                f"-{opt}",
                "-std=c11",
                "hhs_runtime/HARMONICODE_VM_RUNTIME.c",
                "-lm",
                "-o",
                str(path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        samples.append(time.perf_counter_ns() - t0)
        path.unlink()
    builds.append(
        {
            "optimization": opt,
            "runs": len(samples),
            "median_ms": statistics.median(samples) / 1e6,
            "mean_ms": statistics.mean(samples) / 1e6,
            "p95_ms": percentile(samples, 0.95) / 1e6,
            "min_ms": min(samples) / 1e6,
            "max_ms": max(samples) / 1e6,
        }
    )

with (OUT / "build.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=builds[0].keys())
    writer.writeheader()
    writer.writerows(builds)
(OUT / "build.json").write_text(json.dumps(builds, indent=2))

micro = list(csv.DictReader((OUT / "microbench.csv").open()))
md = {row["name"]: row for row in micro}
pd = {row["workload"]: row for row in rows}
bd = {row["optimization"]: row for row in builds}
summary = {
    "build_O2_median_ms": float(bd["O2"]["median_ms"]),
    "cli_full_demo_median_us": float(pd["cli_full_demo"]["median_us"]),
    "cli_full_demo_p95_us": float(pd["cli_full_demo"]["p95_us"]),
    "cli_verify_median_us": float(pd["cli_verify"]["median_us"]),
    "inprocess_full_demo_median_ns": float(md["full_demo_13_steps"]["median_ns"]),
    "vm81_step_median_ns": float(md["vm81_step_demo"]["median_ns"]),
    "sweep81_median_ns": float(md["sweep81"]["median_ns"]),
    "project_hash72_median_ns": float(md["project_hash72"]["median_ns"]),
    "receipt_hash_median_ns": float(md["compose_receipt_hash"]["median_ns"]),
    "orbit_scan_8192_median_ns": float(md["orbit_scan_8192"]["median_ns"]),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
