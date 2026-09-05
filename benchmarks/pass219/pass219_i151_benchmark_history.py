#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

PASS = 219
ITERATION = "I151"
RESOLUTION_BASE = 5184
RESOLUTION_EXPONENT = 21
RESOLUTION_DECIMAL = "1018508951079768942856287659839033239780646340393381046433745481643146696720384"
RESOLUTION_EQUIVALENT = "72^42"

LANES = (
    "RAW5184_X86_64",
    "VM81_HASH72_HASH216",
    "OCTONION_DUAL_STEREO_TERNARY",
    "HARMONIC36_144X36",
)

BENCHMARK_ROOTS = (Path("benchmarks/pass219"), Path("benchmarks/pass219b"))
ALLOWED_SUFFIXES = {".py", ".cpp", ".c", ".h", ".hpp", ".html", ".json"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixed_resolution() -> dict[str, object]:
    value = RESOLUTION_BASE ** RESOLUTION_EXPONENT
    assert value == 72 ** 42
    assert str(value) == RESOLUTION_DECIMAL
    return {
        "base": RESOLUTION_BASE,
        "exponent": RESOLUTION_EXPONENT,
        "exact_cardinality_decimal": str(value),
        "equivalent": RESOLUTION_EQUIVALENT,
        "fixed": True,
        "exhaustive_enumeration_claim": False,
    }


def classify(path: Path) -> str:
    name = path.name.lower()
    if path.suffix.lower() == ".json":
        return "MEASURED_OR_EVIDENCE_RECEIPT"
    if "benchmark" in name:
        return "BENCHMARK_SOURCE"
    if name.startswith("analyze_"):
        return "BENCHMARK_ANALYZER"
    if path.suffix.lower() == ".html":
        return "INTERACTIVE_BENCHMARK_HARNESS"
    return "BENCHMARK_SUPPORT"


def discover_inventory(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rel_root in BENCHMARK_ROOTS:
        absolute = root / rel_root
        if not absolute.is_dir():
            continue
        for path in sorted(p for p in absolute.rglob("*") if p.is_file()):
            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            data = path.read_bytes()
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "kind": classify(path),
                    "bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    return rows


def inventory_root(rows: Iterable[dict[str, object]]) -> str:
    payload = bytearray()
    for row in rows:
        payload.extend(str(row["path"]).encode("utf-8"))
        payload.extend(b"\0")
        payload.extend(str(row["sha256"]).encode("ascii"))
        payload.extend(b"\0")
        payload.extend(str(row["bytes"]).encode("ascii"))
        payload.extend(b"\n")
    return sha256_bytes(bytes(payload))


def load_receipt(path: Path, root: Path) -> dict[str, object]:
    raw = path.read_bytes()
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"receipt must be a JSON object: {path}")
    result = parsed.get("result", parsed.get("conclusion", "UNSPECIFIED"))
    return {
        "path": path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path),
        "sha256": sha256_bytes(raw),
        "schema": parsed.get("schema", "UNSPECIFIED"),
        "result": result,
        "timing_is_canonical": bool(parsed.get("timing_is_canonical", False)),
    }


def build_entry(
    root: Path,
    repository_sha: str,
    run_id: str,
    observed_at: str,
    receipt_paths: list[Path],
    previous_line_sha256: str | None,
) -> dict[str, object]:
    rows = discover_inventory(root)
    return {
        "schema": "HHS_PASS219_I151_BENCHMARK_HISTORY_ENTRY_V1",
        "pass": PASS,
        "iteration": ITERATION,
        "repository_sha": repository_sha,
        "run_id": run_id,
        "observed_at": observed_at,
        "resolution": fixed_resolution(),
        "integrated_lanes": list(LANES),
        "inventory": {
            "count": len(rows),
            "sha256_root": inventory_root(rows),
        },
        "receipts": [load_receipt(p, root) for p in receipt_paths],
        "previous_line_sha256": previous_line_sha256,
        "authority": {
            "canonical_vm81_mutation": False,
            "canonical_hash72_mint": False,
            "canonical_hash216_persistence": False,
        },
    }


def read_history_lines(history: Path) -> list[bytes]:
    if not history.exists():
        return []
    data = history.read_bytes()
    if not data:
        return []
    return data.splitlines(keepends=True)


def validate_history(lines: list[bytes]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    previous: bytes | None = None
    for line in lines:
        parsed = json.loads(line.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("history line must be a JSON object")
        if parsed.get("schema") == "HHS_PASS219_I151_BENCHMARK_HISTORY_ENTRY_V1":
            resolution = parsed["resolution"]
            if resolution["exact_cardinality_decimal"] != RESOLUTION_DECIMAL:
                raise ValueError("history resolution drift")
            if tuple(parsed["integrated_lanes"]) != LANES:
                raise ValueError("history lane drift")
            expected_previous = sha256_bytes(previous.rstrip(b"\n")) if previous is not None else None
            if parsed.get("previous_line_sha256") != expected_previous:
                raise ValueError("history chain mismatch")
            key = (str(parsed["repository_sha"]), str(parsed["run_id"]))
            if key in keys:
                raise ValueError("duplicate benchmark run key")
            keys.add(key)
        previous = line
    return keys


def append_entry(history: Path, entry: dict[str, object]) -> None:
    history.parent.mkdir(parents=True, exist_ok=True)
    original = history.read_bytes() if history.exists() else b""
    lines = read_history_lines(history)
    keys = validate_history(lines)
    key = (str(entry["repository_sha"]), str(entry["run_id"]))
    if key in keys:
        raise ValueError("duplicate benchmark run key")
    encoded = (json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    with history.open("ab") as handle:
        handle.write(encoded)
    after = history.read_bytes()
    if not after.startswith(original):
        raise RuntimeError("append-only history prefix changed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--repository-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--history", required=True)
    parser.add_argument("--registry-output", required=True)
    parser.add_argument("--receipt", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    history = (root / args.history).resolve()
    registry_output = (root / args.registry_output).resolve()
    receipts = [(root / item).resolve() for item in args.receipt]

    rows = discover_inventory(root)
    registry = {
        "schema": "HHS_PASS219_I151_BENCHMARK_INVENTORY_V1",
        "pass": PASS,
        "iteration": ITERATION,
        "resolution": fixed_resolution(),
        "integrated_lanes": list(LANES),
        "inventory_sha256_root": inventory_root(rows),
        "surfaces": rows,
    }
    registry_output.parent.mkdir(parents=True, exist_ok=True)
    registry_output.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = read_history_lines(history)
    previous = lines[-1].rstrip(b"\n") if lines else None
    previous_hash = sha256_bytes(previous) if previous is not None else None
    entry = build_entry(
        root=root,
        repository_sha=args.repository_sha,
        run_id=args.run_id,
        observed_at=args.observed_at,
        receipt_paths=receipts,
        previous_line_sha256=previous_hash,
    )
    append_entry(history, entry)
    print(history)
    print(registry_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
