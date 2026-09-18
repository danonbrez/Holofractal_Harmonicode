from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
from typing import Any

RAW_SCHEMA = "HHS_PASS219_RAW_LINUX_SERIAL_ABI_CAPACITY_V1"
CALIBRATION_SCHEMA = "HHS_PASS219_LANE5_RAW_LINUX_SERIAL_ABI_CALIBRATION_V1"
CAPACITY_UNIT = "RAW_LINUX_SERIAL_ABI_BYTES"
MEASURED_MAXIMUM = "MEASURED_MAXIMUM"
MEASURED_LOWER_BOUND = "MEASURED_LOWER_BOUND"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest(label: str, value: Any) -> str:
    return sha256(label.encode("ascii") + b"\0" + canonical_bytes(value)).hexdigest()


def cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--compiler-id", required=True)
    parser.add_argument("--benchmark-id", default="RAW_LINUX_SERIAL_ABI_CAPACITY_V1")
    parser.add_argument("--ceiling-source", default="CALLER_SUPPLIED_PROBE_CEILING")
    parser.add_argument(
        "--ceiling-is-environment-limit",
        action="store_true",
        help="Assert that probe_ceiling_bytes is the Linux/cgroup environment hard byte limit.",
    )
    args = parser.parse_args()

    raw = json.loads(args.raw_result.read_text(encoding="utf-8"))
    if raw.get("schema") != RAW_SCHEMA:
        raise SystemExit("raw benchmark schema mismatch")
    if raw.get("capacity_unit") != CAPACITY_UNIT:
        raise SystemExit("raw benchmark capacity unit mismatch")

    for key in (
        "hhs_present",
        "vm81_services_present",
        "lane5_present",
        "rna_services_present",
        "hash72_present",
        "hash216_present",
        "pqc_present",
    ):
        if raw.get(key) is not False:
            raise SystemExit(f"raw benchmark contamination: {key}")

    failed_boundary = bool(raw.get("failed_boundary_observed"))
    ceiling_reached = bool(raw.get("probe_ceiling_reached"))
    first_failed_bytes = int(raw.get("first_failed_bytes") or 0)
    if failed_boundary:
        if first_failed_bytes <= int(raw["max_serial_abi_bytes"]):
            raise SystemExit("failed boundary must be above max successful bytes")
        classification = MEASURED_MAXIMUM
        production_accepted = True
    elif ceiling_reached and args.ceiling_is_environment_limit:
        classification = MEASURED_MAXIMUM
        production_accepted = True
    else:
        classification = MEASURED_LOWER_BOUND
        production_accepted = False

    libc_name, libc_version = platform.libc_ver()
    uname = platform.uname()
    environment = {
        "system": uname.system,
        "release": uname.release,
        "machine": uname.machine,
        "processor": cpu_model(),
        "logical_cpu_count": os.cpu_count() or 1,
    }
    body = {
        "classification": classification,
        "capacity_unit": CAPACITY_UNIT,
        "max_serial_abi_bytes": int(raw["max_serial_abi_bytes"]),
        "probe_ceiling_bytes": int(raw["probe_ceiling_bytes"]),
        "page_size": int(raw["page_size"]),
        "probe_attempts": int(raw["probe_attempts"]),
        "first_failed_bytes": first_failed_bytes,
        "failed_boundary_observed": failed_boundary,
        "probe_ceiling_reached": ceiling_reached,
        "ceiling_source": str(args.ceiling_source),
        "ceiling_is_environment_limit": bool(args.ceiling_is_environment_limit),
        "benchmark_window_ns": int(raw["benchmark_window_ns"]),
        "benchmark_id": str(args.benchmark_id),
        "kernel_id": f"{uname.system} {uname.release} {uname.version}",
        "libc_id": f"{libc_name or 'unknown'} {libc_version or 'unknown'}",
        "compiler_id": str(args.compiler_id),
        "environment": environment,
        "hhs_present": False,
        "vm81_services_present": False,
        "lane5_present": False,
        "rna_services_present": False,
        "hash72_present": False,
        "hash216_present": False,
        "pqc_present": False,
        "production_accepted": production_accepted,
    }
    result = {
        "schema": CALIBRATION_SCHEMA,
        **body,
        "evidence_sha256": digest(
            "LANE5_RAW_LINUX_SERIAL_ABI_CALIBRATION",
            body,
        ),
        "source_raw_benchmark": raw,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "schema": result["schema"],
        "capacity_unit": result["capacity_unit"],
        "max_serial_abi_bytes": result["max_serial_abi_bytes"],
        "evidence_sha256": result["evidence_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
