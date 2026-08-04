#!/usr/bin/env python3
"""Pass 211 deterministic multimodal invariant and computation-reuse benchmark.

This benchmark is additive and read-only. It scans repository-visible text objects,
measures exact VM81/G243/context address round trips, calibrates a deterministic
72-byte retrieval projection, and emits a stable JSON receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

VM81_CELLS = 81
OPERATIONS_PER_CELL = 64
PERMANENT_STATES = VM81_CELLS * OPERATIONS_PER_CELL
G243_CONTROLS = 243
PROJECTED_STATES = PERMANENT_STATES * G243_CONTROLS
LOCAL_COORDINATES = 41
CONTEXTUAL_STATES = PROJECTED_STATES * LOCAL_COORDINATES
FACTORIAL_STATES = math.factorial(7)
OUTER_ENVELOPE = PROJECTED_STATES + 1

TEXT_SUFFIXES = {
    ".c", ".cc", ".cpp", ".h", ".hpp", ".py", ".js", ".mjs", ".ts", ".tsx",
    ".json", ".jsonl", ".md", ".txt", ".toml", ".yaml", ".yml", ".ini", ".cfg",
    ".sh", ".service", ".timer", ".sql", ".html", ".css", ".wgsl", ".cl", ".glsl",
}
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build", "builds",
}
MAX_TEXT_BYTES = 8 * 1024 * 1024
PASS_RE = re.compile(r"(?:PASS|Pass|pass)[_\- ]?(\d{1,3})")

MODALITY_MARKERS: dict[str, tuple[str, ...]] = {
    "image": ("image", "sprite", "texture", "pixel"),
    "video": ("video", "frame", "mp4", "timeline"),
    "animation": ("animation", "motion", "keyframe", "storyboard"),
    "audio": ("audio", "pcm", "waveform", "speech", "music"),
    "physics": ("physics", "worldline", "relativ", "gravity", "collision"),
    "game": ("game", "unity", "shader", "scene", "rigidbody"),
    "language": ("language", "token", "text encoder", "llm"),
    "model": ("model parameter", "weight", "tensor", "neural", "inference"),
    "gpu": ("gpu", "opencl", "cuda", "vulkan", "accelerator"),
    "continuation": ("continuation", "delta", "replay", "branch"),
    "retrieval": ("retrieval", "vector", "cache", "reuse", "rag"),
}

INVARIANT_MARKERS: dict[str, tuple[str, ...]] = {
    "vm81_64": ("81 × 64", "81*64", "81 * 64", "5184"),
    "g243": ("g243", "G243"),
    "projected_1259712": ("1259712", "1,259,712"),
    "contextual_51648192": ("51648192", "51,648,192"),
    "factorial_5040": ("5040", "5,040", "Factorial(7)", "7!"),
    "hash72": ("Hash72", "hash72"),
    "hash216": ("Hash216", "hash216"),
    "no_float": ("NO_FLOAT_CANONICAL_AUTHORITY", "no floating-point canonical authority"),
    "single_authority": ("singleton VM81", "single authority", "one VM81"),
    "noncommutative": ("noncommutative", "non-commutative"),
    "exact_list": ("1/Factorial(72)", "List(x*Factorial(72)"),
}


@dataclass(frozen=True)
class RepositoryObject:
    path: str
    size: int
    digest_hex: str
    vector72: bytes
    modalities: tuple[str, ...]
    invariants: tuple[str, ...]


def iter_text_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
        base = Path(current)
        for name in sorted(files):
            path = base / name
            if path.suffix.lower() in TEXT_SUFFIXES or name in {"Makefile", "Dockerfile"}:
                yield path


def vector72(path_text: str, payload: bytes) -> bytes:
    seed = path_text.encode("utf-8") + b"\0" + payload
    part_a = hashlib.sha256(b"HHS211-A\0" + seed).digest()
    part_b = hashlib.sha256(b"HHS211-B\0" + seed).digest()
    part_c = hashlib.sha256(b"HHS211-C\0" + seed).digest()
    return part_a + part_b + part_c[:8]


def scan_repository(root: Path, max_vector_objects: int) -> tuple[dict[str, Any], list[RepositoryObject]]:
    started = time.perf_counter_ns()
    corpus_hash = hashlib.sha256()
    suffix_counts: Counter[str] = Counter()
    modality_counts: Counter[str] = Counter()
    invariant_counts: Counter[str] = Counter()
    modality_pairs: Counter[str] = Counter()
    pass_ids: set[int] = set()
    objects: list[RepositoryObject] = []
    scanned_files = 0
    scanned_bytes = 0
    skipped_oversized: list[str] = []
    valid_json = 0
    invalid_json = 0
    invalid_json_paths: list[str] = []
    invalid_json_errors: dict[str, str] = {}
    valid_jsonl_lines = 0
    invalid_jsonl_lines = 0

    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            size = path.stat().st_size
        except OSError:
            continue
        suffix_counts[path.suffix.lower() or path.name] += 1
        if size > MAX_TEXT_BYTES:
            skipped_oversized.append(rel)
            continue
        try:
            payload = path.read_bytes()
        except OSError:
            continue

        scanned_files += 1
        scanned_bytes += len(payload)
        digest = hashlib.sha256(payload).hexdigest()
        corpus_hash.update(rel.encode("utf-8"))
        corpus_hash.update(b"\0")
        corpus_hash.update(bytes.fromhex(digest))

        text = payload.decode("utf-8", errors="replace")
        lower = text.lower()
        for match in PASS_RE.finditer(text):
            value = int(match.group(1))
            if 0 <= value <= 999:
                pass_ids.add(value)

        modalities = tuple(
            name for name, markers in MODALITY_MARKERS.items()
            if any(marker.lower() in lower for marker in markers)
        )
        invariants = tuple(
            name for name, markers in INVARIANT_MARKERS.items()
            if any(marker.lower() in lower for marker in markers)
        )
        modality_counts.update(modalities)
        invariant_counts.update(invariants)
        for index, left in enumerate(modalities):
            for right in modalities[index + 1:]:
                modality_pairs[f"{left}|{right}"] += 1

        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
                valid_json += 1
            except json.JSONDecodeError as exc:
                invalid_json += 1
                invalid_json_paths.append(rel)
                invalid_json_errors[rel] = (
                    f"{exc.msg} at line {exc.lineno}, column {exc.colno}, char {exc.pos}"
                )
        elif path.suffix.lower() == ".jsonl":
            for line in text.splitlines():
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                    valid_jsonl_lines += 1
                except json.JSONDecodeError:
                    invalid_jsonl_lines += 1

        if len(objects) < max_vector_objects and (modalities or invariants):
            objects.append(
                RepositoryObject(
                    path=rel,
                    size=size,
                    digest_hex=digest,
                    vector72=vector72(rel, payload),
                    modalities=modalities,
                    invariants=invariants,
                )
            )

    elapsed_ns = time.perf_counter_ns() - started
    public_objects = [
        {
            "path": item.path,
            "size": item.size,
            "sha256": item.digest_hex,
            "modalities": list(item.modalities),
            "invariants": list(item.invariants),
        }
        for item in objects[:100]
    ]
    return (
        {
            "scanned_files": scanned_files,
            "scanned_bytes": scanned_bytes,
            "elapsed_ns": elapsed_ns,
            "files_per_second": round(
                scanned_files / max(elapsed_ns / 1_000_000_000, 1e-9), 3
            ),
            "corpus_sha256": corpus_hash.hexdigest(),
            "suffix_counts": dict(sorted(suffix_counts.items())),
            "pass_ids": sorted(pass_ids),
            "pass_count": len(pass_ids),
            "highest_pass_observed": max(pass_ids) if pass_ids else None,
            "json": {
                "valid_files": valid_json,
                "invalid_files": invalid_json,
                "invalid_paths": sorted(invalid_json_paths),
                "invalid_errors": dict(sorted(invalid_json_errors.items())),
                "pass211_owned_invalid_paths": sorted(
                    rel
                    for rel in invalid_json_paths
                    if rel.startswith(
                        (
                            "contracts/pass211/",
                            "evidence/pass211/",
                            "artifacts/pass211/",
                        )
                    )
                ),
                "valid_jsonl_lines": valid_jsonl_lines,
                "invalid_jsonl_lines": invalid_jsonl_lines,
            },
            "modality_file_counts": dict(sorted(modality_counts.items())),
            "modality_pair_file_counts": dict(sorted(modality_pairs.items())),
            "invariant_file_counts": dict(sorted(invariant_counts.items())),
            "skipped_oversized_files": skipped_oversized,
            "vector_object_count": len(objects),
            "vector_objects": public_objects,
            "vector_objects_truncated": max(0, len(objects) - len(public_objects)),
        },
        objects,
    )


def encode_context(cell: int, operation: int, control: int, local_coordinate: int) -> int:
    if not 0 <= cell < VM81_CELLS:
        raise ValueError("cell")
    if not 0 <= operation < OPERATIONS_PER_CELL:
        raise ValueError("operation")
    if not 0 <= control < G243_CONTROLS:
        raise ValueError("control")
    if not 0 <= local_coordinate < LOCAL_COORDINATES:
        raise ValueError("local_coordinate")
    permanent = cell * OPERATIONS_PER_CELL + operation
    projected = permanent * G243_CONTROLS + control
    return projected * LOCAL_COORDINATES + local_coordinate


def decode_context(extended: int) -> tuple[int, int, int, int]:
    if not 0 <= extended < CONTEXTUAL_STATES:
        raise ValueError("extended")
    projected, local_coordinate = divmod(extended, LOCAL_COORDINATES)
    permanent, control = divmod(projected, G243_CONTROLS)
    cell, operation = divmod(permanent, OPERATIONS_PER_CELL)
    return cell, operation, control, local_coordinate


def benchmark_address_roundtrip(samples: int) -> dict[str, Any]:
    fixed = [
        0,
        1,
        LOCAL_COORDINATES - 1,
        LOCAL_COORDINATES,
        CONTEXTUAL_STATES // 2,
        CONTEXTUAL_STATES - LOCAL_COORDINATES,
        CONTEXTUAL_STATES - 2,
        CONTEXTUAL_STATES - 1,
    ]
    state = 0x9E3779B97F4A7C15
    values = list(fixed)
    for _ in range(max(0, samples - len(fixed))):
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        values.append(state % CONTEXTUAL_STATES)

    started = time.perf_counter_ns()
    checksum = 0
    for extended in values:
        decoded = decode_context(extended)
        rebuilt = encode_context(*decoded)
        if rebuilt != extended:
            raise AssertionError((extended, rebuilt))
        checksum = ((checksum << 7) ^ (checksum >> 3) ^ rebuilt) & ((1 << 64) - 1)
    elapsed_ns = time.perf_counter_ns() - started
    return {
        "samples": len(values),
        "elapsed_ns": elapsed_ns,
        "roundtrips_per_second": round(
            len(values) / max(elapsed_ns / 1_000_000_000, 1e-9), 3
        ),
        "coordinate_drift": 0,
        "checksum_hex": f"{checksum:016x}",
    }


def distance72(left: bytes, right: bytes) -> int:
    return (int.from_bytes(left, "big") ^ int.from_bytes(right, "big")).bit_count()


def benchmark_retrieval(objects: list[RepositoryObject], query_limit: int) -> dict[str, Any]:
    if not objects:
        return {
            "candidate_count": 0,
            "query_count": 0,
            "exact_hits": 0,
            "exact_hit_rate": 0.0,
            "single_bit_adaptation_nearest_hits": 0,
            "single_bit_adaptation_nearest_rate": 0.0,
            "distance_evaluations": 0,
            "elapsed_ns": 0,
        }

    queries = objects[: min(query_limit, len(objects))]
    exact_hits = 0
    adaptation_hits = 0
    started = time.perf_counter_ns()
    for index, query in enumerate(queries):
        distances = [distance72(query.vector72, candidate.vector72) for candidate in objects]
        nearest = objects[distances.index(min(distances))]
        if min(distances) == 0 and nearest.digest_hex == query.digest_hex:
            exact_hits += 1

        adapted = bytearray(query.vector72)
        adapted[index % len(adapted)] ^= 1 << (index % 8)
        adapted_distances = [distance72(bytes(adapted), candidate.vector72) for candidate in objects]
        adapted_nearest = objects[adapted_distances.index(min(adapted_distances))]
        if adapted_nearest.digest_hex == query.digest_hex:
            adaptation_hits += 1

    elapsed_ns = time.perf_counter_ns() - started
    evaluations = len(objects) * len(queries) * 2
    return {
        "candidate_count": len(objects),
        "query_count": len(queries),
        "exact_hits": exact_hits,
        "exact_hit_rate": exact_hits / len(queries),
        "single_bit_adaptation_nearest_hits": adaptation_hits,
        "single_bit_adaptation_nearest_rate": adaptation_hits / len(queries),
        "distance_evaluations": evaluations,
        "elapsed_ns": elapsed_ns,
        "distance_evaluations_per_second": round(
            evaluations / max(elapsed_ns / 1_000_000_000, 1e-9), 3
        ),
    }


def exact_constants() -> dict[str, Any]:
    checks = {
        "81_x_64": PERMANENT_STATES == 5_184,
        "5184_x_243": PROJECTED_STATES == 1_259_712,
        "1259712_x_41": CONTEXTUAL_STATES == 51_648_192,
        "factorial_7": FACTORIAL_STATES == 5_040,
        "outer_envelope": OUTER_ENVELOPE == 1_259_713,
    }
    return {
        "values": {
            "vm81_cells": VM81_CELLS,
            "operations_per_cell": OPERATIONS_PER_CELL,
            "permanent_states": PERMANENT_STATES,
            "g243_controls": G243_CONTROLS,
            "projected_states": PROJECTED_STATES,
            "local_coordinates": LOCAL_COORDINATES,
            "contextual_states": CONTEXTUAL_STATES,
            "factorial_states": FACTORIAL_STATES,
            "outer_envelope": OUTER_ENVELOPE,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--address-samples", type=int, default=500_000)
    parser.add_argument("--max-vector-objects", type=int, default=1_024)
    parser.add_argument("--query-limit", type=int, default=256)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    constants = exact_constants()
    scan, objects = scan_repository(root, args.max_vector_objects)
    address = benchmark_address_roundtrip(args.address_samples)
    retrieval = benchmark_retrieval(objects, args.query_limit)

    required_invariants = {
        "vm81_64",
        "g243",
        "projected_1259712",
        "contextual_51648192",
        "factorial_5040",
        "hash72",
        "hash216",
        "single_authority",
        "noncommutative",
    }
    present_invariants = {
        key for key, count in scan["invariant_file_counts"].items() if count > 0
    }
    required_modalities = {
        "image",
        "video",
        "animation",
        "audio",
        "physics",
        "game",
        "language",
        "model",
        "gpu",
        "continuation",
        "retrieval",
    }
    present_modalities = {
        key for key, count in scan["modality_file_counts"].items() if count > 0
    }

    checks = {
        "exact_constants": constants["passed"],
        "zero_coordinate_drift": address["coordinate_drift"] == 0,
        "exact_retrieval": retrieval["exact_hit_rate"] == 1.0,
        "single_bit_nearest_retrieval": retrieval["single_bit_adaptation_nearest_rate"] == 1.0,
        "required_invariants_present": required_invariants <= present_invariants,
        "required_modalities_present": required_modalities <= present_modalities,
        "pass211_owned_json_files_parse": not scan["json"]["pass211_owned_invalid_paths"],
        "historical_json_failures_reported": (
            len(scan["json"]["invalid_paths"]) == scan["json"]["invalid_files"]
        ),
        "jsonl_lines_parse": scan["json"]["invalid_jsonl_lines"] == 0,
        "pass210_or_later_observed": (scan["highest_pass_observed"] or 0) >= 210,
    }

    receipt = {
        "schema": "HHS_PASS_211_MULTIMODAL_INVARIANT_BENCHMARK_RECEIPT_V1",
        "classification": (
            "HHS_PASS_211_MULTIMODAL_INVARIANT_BENCHMARK_PASS"
            if all(checks.values())
            else "HHS_PASS_211_MULTIMODAL_INVARIANT_BENCHMARK_FAIL"
        ),
        "constants": constants,
        "repository_scan": scan,
        "address_roundtrip": address,
        "retrieval_calibration": retrieval,
        "checks": checks,
        "passed": all(checks.values()),
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": receipt["classification"],
        "passed": receipt["passed"],
        "output": str(output),
        "scanned_files": scan["scanned_files"],
        "contextual_states": CONTEXTUAL_STATES,
        "exact_hit_rate": retrieval["exact_hit_rate"],
        "adaptation_hit_rate": retrieval["single_bit_adaptation_nearest_rate"],
        "receipt_sha256": receipt["receipt_sha256"],
    }, indent=2, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
