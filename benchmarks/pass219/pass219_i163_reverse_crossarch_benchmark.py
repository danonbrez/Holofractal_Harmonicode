from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import time

SCHEMA = "HHS_PASS219_I163_REVERSE_CROSSARCH_BENCHMARK_V1"
EXPECTED_STDOUT = "PASS219 I163 Pass169 reverse runtime: PASS"


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reverse_executable")
    parser.add_argument("combined_source")
    parser.add_argument("crossarch_parity")
    parser.add_argument("output")
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    if args.repeats < 3 or args.repeats > 64:
        raise SystemExit("repeats must be in [3,64]")

    parity = json.loads(Path(args.crossarch_parity).read_text(encoding="utf-8"))
    if parity.get("schema") != "HHS_PASS219_I163_CROSSARCH_PARITY_EVIDENCE_V1":
        raise SystemExit("wrong cross-architecture evidence schema")
    if parity.get("result") != "PASS" or parity.get("records_identical") is not True:
        raise SystemExit("cross-architecture parity is not green")

    timings: list[int] = []
    stdout_rows: list[str] = []
    for _ in range(args.repeats):
        started = time.perf_counter_ns()
        proc = subprocess.run(
            [args.reverse_executable, args.combined_source],
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed = time.perf_counter_ns() - started
        if proc.returncode != 0:
            raise SystemExit(
                f"reverse executable failed: rc={proc.returncode} stderr={proc.stderr.strip()}"
            )
        stdout = proc.stdout.strip()
        if stdout != EXPECTED_STDOUT:
            raise SystemExit(f"unexpected reverse stdout: {stdout!r}")
        timings.append(elapsed)
        stdout_rows.append(stdout)

    deterministic_reverse_result = len(set(stdout_rows)) == 1
    core = {
        "schema": SCHEMA,
        "result": "PASS" if deterministic_reverse_result else "FAIL",
        "repeats": args.repeats,
        "timing_clock": "perf_counter_ns",
        "timing_values_are_integer_nanoseconds": True,
        "min_ns": min(timings),
        "median_ns": int(statistics.median(timings)),
        "max_ns": max(timings),
        "deterministic_reverse_result": deterministic_reverse_result,
        "native_reverse_runtime_verified": deterministic_reverse_result,
        "cross_architecture_records_identical": parity["records_identical"],
        "cross_architecture_canonical_record_sha256": parity["canonical_record_sha256"],
        "architectures": parity["architectures"],
        "bindings": parity["bindings"],
        "floating_point_authority": False,
        "canonical_mutation_authority": False,
        "hash216_persistence_authority": False,
        "pass169_terminal_contract_verified": False,
        "fixed_resolution": "72^42=5184^21",
    }
    core["benchmark_receipt_sha256"] = canonical_sha256(core)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(core, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(core, sort_keys=True))

    if args.enforce and core["result"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
