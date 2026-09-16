#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass165.ingestion import MultimodalLearningService
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger

SCHEMA = "HHS_PASS219_LANE5_REAL_WORLD_WORKLOAD_BENCHMARK_1_47"
AUTH_SCOPE = "PASS219_REAL_WORLD_WORKLOAD_BENCHMARK_1_47"
MAX_FILE_BYTES = 262_144

CLASSIFIERS = {
    "documentation": {
        "suffixes": {".md", ".txt"},
        "prefixes": ("docs/", "contracts/"),
        "media_type": "TEXT",
    },
    "python_runtime": {
        "suffixes": {".py"},
        "prefixes": ("hhs_backend/", "hhs_runtime/"),
        "media_type": "SOURCE_CODE",
    },
    "native_runtime": {
        "suffixes": {".c", ".cc", ".cpp", ".h", ".hpp"},
        "prefixes": ("hhs_runtime/", "native_projects/"),
        "media_type": "SOURCE_CODE",
    },
    "structured_contracts": {
        "suffixes": {".json", ".yml", ".yaml"},
        "prefixes": ("contracts/", ".github/"),
        "media_type": "JSON_OR_TEXT",
    },
}

EXCLUDED_PARTS = {
    ".git",
    "node_modules",
    "artifacts",
    "build",
    "builds",
    "dist",
    ".venv",
    "__pycache__",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def percentile(values: list[int], numerator: int, denominator: int) -> int:
    ordered = sorted(values)
    index = min(len(ordered) - 1, ((len(ordered) - 1) * numerator + denominator - 1) // denominator)
    return ordered[index]


def media_type_for(path: Path, declared: str) -> str:
    if declared != "JSON_OR_TEXT":
        return declared
    return "JSON" if path.suffix.lower() == ".json" else "TEXT"


def candidate_files(class_name: str, limit: int) -> list[Path]:
    spec = CLASSIFIERS[class_name]
    rows: list[tuple[int, str, Path]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if rel.endswith("pass219_lane5_real_world_workload_benchmark_1_47.py"):
            continue
        if path.suffix.lower() not in spec["suffixes"]:
            continue
        if not rel.startswith(spec["prefixes"]):
            continue
        size = path.stat().st_size
        if size <= 0 or size > MAX_FILE_BYTES:
            continue
        rows.append((-size, rel, path))
    rows.sort()
    selected = [row[2] for row in rows[:limit]]
    if len(selected) < limit:
        raise RuntimeError(f"PASS219_REAL_WORLD_INSUFFICIENT_FILES:{class_name}:{len(selected)}<{limit}")
    return selected


def cross_process_projection(path: Path, media_type: str, provenance: str) -> tuple[int, dict[str, Any]]:
    program = r'''
import json, pathlib, sys
from hhs_runtime.pass165.ingestion import MultimodalLearningService
path = pathlib.Path(sys.argv[1])
media_type = sys.argv[2]
provenance = sys.argv[3]
payload = path.read_bytes()
result = MultimodalLearningService().analyze(
    payload,
    declared_media_type=media_type,
    provenance=provenance,
    authorization_scope="PASS219_REAL_WORLD_WORKLOAD_BENCHMARK_1_47",
)
print(json.dumps({"source_hash": result.source.source_hash, "projection_hash72": result.projection_hash72}, sort_keys=True))
'''
    started = time.perf_counter_ns()
    completed = subprocess.run(
        [sys.executable, "-c", program, str(path), media_type, provenance],
        cwd=ROOT,
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed = time.perf_counter_ns() - started
    if completed.returncode != 0:
        raise RuntimeError(f"PASS219_REAL_WORLD_CROSS_PROCESS_FAILED:{path}:{completed.stderr[-400:]}")
    return elapsed, json.loads(completed.stdout.strip().splitlines()[-1])


def benchmark_file(path: Path, class_name: str, media_type: str) -> dict[str, Any]:
    rel = path.relative_to(ROOT).as_posix()
    payload = path.read_bytes()
    expected_hash = sha256(payload).hexdigest()
    provenance = f"pass219-real-world:{rel}"

    cold_service = MultimodalLearningService()
    started = time.perf_counter_ns()
    cold = cold_service.analyze(
        payload,
        declared_media_type=media_type,
        provenance=provenance,
        authorization_scope=AUTH_SCOPE,
    )
    cold_ns = time.perf_counter_ns() - started
    if cold.source.source_bytes != payload or cold.source.source_hash != expected_hash:
        raise RuntimeError(f"PASS219_REAL_WORLD_SOURCE_MISMATCH:{rel}")

    repeat_service = MultimodalLearningService()
    started = time.perf_counter_ns()
    repeat = repeat_service.analyze(
        payload,
        declared_media_type=media_type,
        provenance=provenance,
        authorization_scope=AUTH_SCOPE,
    )
    repeat_ns = time.perf_counter_ns() - started
    if repeat.source.source_hash != expected_hash or repeat.projection_hash72 != cold.projection_hash72:
        raise RuntimeError(f"PASS219_REAL_WORLD_REPEAT_DRIFT:{rel}")

    warm_service = MultimodalLearningService()
    warm_service.ingest_source(
        payload,
        declared_media_type=media_type,
        provenance=provenance,
        authorization_scope=AUTH_SCOPE,
    )
    started = time.perf_counter_ns()
    warm = warm_service.ingest_source(
        payload,
        declared_media_type=media_type,
        provenance=provenance,
        authorization_scope=AUTH_SCOPE,
    )
    warm_ns = time.perf_counter_ns() - started
    if warm["source"]["source_hash"] != expected_hash or warm["receipt"]["reused"] is not True:
        raise RuntimeError(f"PASS219_REAL_WORLD_WARM_REUSE_FAILED:{rel}")
    replay = warm_service.replay_ingestion()
    if replay.get("deterministic_replay") is not True:
        raise RuntimeError(f"PASS219_REAL_WORLD_REPLAY_FAILED:{rel}")

    cross_ns, child = cross_process_projection(path, media_type, provenance)
    if child["source_hash"] != expected_hash or child["projection_hash72"] != cold.projection_hash72:
        raise RuntimeError(f"PASS219_REAL_WORLD_CROSS_PROCESS_DRIFT:{rel}")

    return {
        "class": class_name,
        "path": rel,
        "media_type": media_type,
        "bytes": len(payload),
        "source_sha256": expected_hash,
        "projection_hash72": cold.projection_hash72,
        "token_count": len(cold.tokens),
        "chunk_count": len(cold.chunks),
        "graph_edge_count": len(cold.graph_edges),
        "projection_bytes": len(cold.projection_bytes),
        "cold_ns": cold_ns,
        "repeat_ns": repeat_ns,
        "warm_reuse_ns": warm_ns,
        "cross_process_ns": cross_ns,
        "warm_reused": True,
        "replay_deterministic": True,
        "cross_process_equal": True,
    }


def benchmark_repository(files_per_class: int) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    selected: dict[str, list[str]] = {}
    for class_name, spec in CLASSIFIERS.items():
        paths = candidate_files(class_name, files_per_class)
        selected[class_name] = [path.relative_to(ROOT).as_posix() for path in paths]
        for path in paths:
            records.append(
                benchmark_file(path, class_name, media_type_for(path, spec["media_type"]))
            )

    cold = [int(row["cold_ns"]) for row in records]
    warm = [int(row["warm_reuse_ns"]) for row in records]
    repeat = [int(row["repeat_ns"]) for row in records]
    cross = [int(row["cross_process_ns"]) for row in records]
    total_bytes = sum(int(row["bytes"]) for row in records)
    total_cold_ns = sum(cold)
    return {
        "selected": selected,
        "record_count": len(records),
        "total_source_bytes": total_bytes,
        "all_source_hashes_exact": all(len(row["source_sha256"]) == 64 for row in records),
        "all_projection_hash72_present": all(len(row["projection_hash72"]) == 72 for row in records),
        "all_warm_reused": all(row["warm_reused"] is True for row in records),
        "all_replay_deterministic": all(row["replay_deterministic"] is True for row in records),
        "all_cross_process_equal": all(row["cross_process_equal"] is True for row in records),
        "observational": {
            "timing_clock": "perf_counter_ns",
            "timing_is_canonical": False,
            "cold_total_ns": total_cold_ns,
            "cold_median_ns": percentile(cold, 1, 2),
            "cold_p95_ns": percentile(cold, 95, 100),
            "warm_median_ns": percentile(warm, 1, 2),
            "warm_p95_ns": percentile(warm, 95, 100),
            "repeat_median_ns": percentile(repeat, 1, 2),
            "cross_process_median_ns": percentile(cross, 1, 2),
            "cold_bytes_per_second_floor": (total_bytes * 1_000_000_000) // max(1, total_cold_ns),
        },
        "records": records,
    }


def benchmark_ledger(entries: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pass219-real-world-ledger-") as temp:
        ledger = Path(temp) / "ledger.json"
        samples: list[int] = []
        for index in range(entries):
            started = time.perf_counter_ns()
            append_payload(
                "PASS219_REAL_WORLD_WORKLOAD",
                "benchmarks.pass219.pass219_lane5_real_world_workload_benchmark_1_47",
                {"index": index, "lane": 5, "phase": index % 72},
                ledger_path=ledger,
            )
            samples.append(time.perf_counter_ns() - started)
        verification = verify_unified_ledger(ledger)
        if verification.get("ok") is not True:
            raise RuntimeError("PASS219_REAL_WORLD_LEDGER_VERIFICATION_FAILED")
        return {
            "entries": entries,
            "verification_ok": True,
            "timing_is_canonical": False,
            "median_ns": percentile(samples, 1, 2),
            "p95_ns": percentile(samples, 95, 100),
            "max_ns": max(samples),
            "appends_per_second_floor": (entries * 1_000_000_000) // max(1, sum(samples)),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--files-per-class", type=int, default=3)
    parser.add_argument("--ledger-entries", type=int, default=500)
    args = parser.parse_args()
    if args.files_per_class < 1 or args.files_per_class > 8:
        parser.error("--files-per-class must be between 1 and 8")
    if args.ledger_entries < 1 or args.ledger_entries > 5000:
        parser.error("--ledger-entries must be between 1 and 5000")

    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip()
    started = time.perf_counter_ns()
    repository = benchmark_repository(args.files_per_class)
    ledger = benchmark_ledger(args.ledger_entries)
    elapsed_ns = time.perf_counter_ns() - started

    body = {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "authority": {
            "observational_timing_only": True,
            "floating_point_canonical_authority": False,
            "lane5_candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        },
        "repository_workloads": repository,
        "hash72_ledger": ledger,
        "suite_elapsed_ns": elapsed_ns,
        "result": "PASS",
    }
    body["receipt_sha256"] = sha256(canonical_bytes(body)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": body["result"],
        "record_count": repository["record_count"],
        "total_source_bytes": repository["total_source_bytes"],
        "cold_bytes_per_second_floor": repository["observational"]["cold_bytes_per_second_floor"],
        "ledger_entries": ledger["entries"],
        "ledger_appends_per_second_floor": ledger["appends_per_second_floor"],
        "receipt_sha256": body["receipt_sha256"],
    }, sort_keys=True))
    print("PASS219_LANE5_REAL_WORLD_WORKLOAD_BENCHMARK_1_47_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
