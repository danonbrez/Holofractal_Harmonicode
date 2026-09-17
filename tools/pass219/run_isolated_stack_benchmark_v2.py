#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys


def run_arm(exe: str, dataset: str, sample: dict) -> dict:
    proc = subprocess.run(
        [
            exe,
            dataset,
            str(sample["offset_records"]),
            str(sample["count"]),
            str(sample["phase_slot"]),
            str(sample["inverse_phase_slot"]),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError(f"expected one JSON line from {exe}, got {len(lines)}: {proc.stdout!r}")
    row = json.loads(lines[0])
    if row.get("schema") != "HHS_PASS219_ISOLATED_STACK_BENCHMARK_V2":
        raise RuntimeError(f"unexpected schema from {exe}: {row}")
    return row


def main() -> int:
    if len(sys.argv) != 7:
        raise SystemExit(
            f"usage: {sys.argv[0]} MANIFEST DATASET A_EXE B_EXE C_EXE OUT_JSONL"
        )
    manifest_path = pathlib.Path(sys.argv[1])
    dataset_path = pathlib.Path(sys.argv[2])
    exe = {"A": sys.argv[3], "B": sys.argv[4], "C": sys.argv[5]}
    out_path = pathlib.Path(sys.argv[6])

    manifest = json.loads(manifest_path.read_text())
    payload_sha = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    if payload_sha != manifest["sha256"]:
        raise RuntimeError("dataset SHA-256 does not match manifest")
    if manifest["record_bytes"] != 648 or manifest["record_count"] <= 0:
        raise RuntimeError("invalid neutral dataset manifest")

    rotations = [("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B")]
    rows: list[dict] = []
    meta = {
        "type": "meta",
        "schema": "HHS_PASS219_ISOLATED_STACK_BENCHMARK_V2",
        "dataset_sha256": payload_sha,
        "dataset_record_bytes": manifest["record_bytes"],
        "dataset_record_count": manifest["record_count"],
        "same_dataset_file_for_all_arms": True,
        "timed_regions_exclude_dataset_generation_and_file_load": True,
        "arm_A": "full_aggregate_abi_lane5_h36_hash216_m_stack",
        "arm_B": "immutable_exact_v1_1_base_abi_only",
        "arm_C": "plain_x86_64_ubuntu_libc_no_hhs",
        "order_rotation": "ABC/BCA/CAB",
    }
    rows.append(meta)

    for sample_index, sample in enumerate(manifest["samples"]):
        order = rotations[sample_index % len(rotations)]
        measured: dict[str, dict] = {}
        for order_position, arm in enumerate(order):
            row = run_arm(exe[arm], str(dataset_path), sample)
            if row.get("arm") != arm:
                raise RuntimeError(f"arm identity mismatch: expected {arm}, got {row}")
            row.update(
                {
                    "type": "arm",
                    "sample_id": sample["sample_id"],
                    "rank": sample["rank"],
                    "gradient": sample["gradient"],
                    "phase_index": sample["phase_index"],
                    "phase": sample["phase"],
                    "order": "".join(order),
                    "order_position": order_position,
                    "target_count": sample["count"],
                }
            )
            if row["completed"] != sample["count"]:
                raise RuntimeError(f"incomplete sample: {row}")
            measured[arm] = row
            rows.append(row)

        digests = {measured[a]["payload_digest"] for a in ("A", "B", "C")}
        inputs = {measured[a]["input_digest"] for a in ("A", "B", "C")}
        if len(digests) != 1 or len(inputs) != 1 or digests != inputs:
            raise RuntimeError(f"payload identity failure for {sample['sample_id']}")

    result = {
        "type": "result",
        "schema": "HHS_PASS219_ISOLATED_STACK_BENCHMARK_V2",
        "triplet_samples": len(manifest["samples"]),
        "same_dataset_verified": True,
        "result": "PASS",
    }
    rows.append(result)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
