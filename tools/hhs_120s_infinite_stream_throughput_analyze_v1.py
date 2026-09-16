#!/usr/bin/env python3
from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import math
import os
from pathlib import Path
import platform
import subprocess
from typing import Any

getcontext().prec = 80
SCHEMA = "HHS_120S_INFINITE_STREAM_THROUGHPUT_V1_EVIDENCE"


def _cpu_model() -> str:
    p = Path("/proc/cpuinfo")
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _memory_kib() -> int | None:
    p = Path("/proc/meminfo")
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    return None


def _cc_version() -> str:
    try:
        return subprocess.run(["cc", "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    except Exception:
        return "unknown"


def load_records(path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    meta = hhs = classical = verification = None
    terminal = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        if rec.get("type") == "meta":
            meta = rec
        elif rec.get("type") == "engine" and rec.get("engine") == "hhs":
            hhs = rec
        elif rec.get("type") == "engine" and rec.get("engine") == "classical":
            classical = rec
        elif rec.get("type") == "verification":
            verification = rec
        elif rec.get("type") == "result":
            terminal = rec.get("result") == "PASS"
    if not terminal or meta is None or hhs is None or classical is None or verification is None:
        raise ValueError("stream benchmark evidence is incomplete")
    return meta, hhs, classical, verification


def _rate(value: int, elapsed_ns: int) -> Decimal:
    return Decimal(value) * Decimal(1_000_000_000) / Decimal(elapsed_ns)


def analyze(meta: dict[str, Any], hhs: dict[str, Any], classical: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    window = int(meta["window_ns"])
    if window <= 0:
        raise ValueError("invalid window")
    if int(meta.get("active_threads_per_epoch", 0)) != 1 or not bool(meta.get("epochs_sequential")):
        raise ValueError("benchmark must use sequential one-thread epochs")

    he = int(hhs["elapsed_ns"])
    ce = int(classical["elapsed_ns"])
    tolerance = max(1_000_000_000, window // 100)
    for name, elapsed in (("hhs", he), ("classical", ce)):
        if elapsed < window:
            raise ValueError(f"{name} stopped before its window")
        if elapsed > window + tolerance:
            raise ValueError(f"{name} exceeded window tolerance")

    hq = int(hhs["completed_queries"])
    cq = int(classical["completed_queries"])
    if hq <= 0 or cq <= 0:
        raise ValueError("each engine must complete at least one query")
    if int(hhs.get("lane5_admissions", -1)) != hq:
        raise ValueError("every HHS completion must pass Lane 5 admission")
    if int(hhs.get("materialized_intermediate_states", -1)) != 0:
        raise ValueError("HHS materialized represented intermediates")
    if not verification.get("exact"):
        raise ValueError("classical prefix verification failed")
    if int(verification["classical_prefix_queries"]) != cq:
        raise ValueError("verification prefix length mismatch")
    if int(verification["classical_prefix_digest"]) != int(verification["hhs_replay_digest"]):
        raise ValueError("classical/HHS prefix digest disagreement")
    if int(verification["classical_prefix_digest"]) != int(classical["endpoint_digest"]):
        raise ValueError("classical digest mismatch")

    h_trans = int(hhs["represented_transitions"])
    c_complete_trans = int(classical["represented_completed_transitions"])
    c_steps = int(classical["executed_transition_steps"])
    if h_trans <= 0 or c_steps <= 0 or c_complete_trans <= 0:
        raise ValueError("invalid transition counts")
    if c_steps < c_complete_trans:
        raise ValueError("classical executed work below completed represented work")
    partial = int(classical["partial_steps"])
    partial_k = int(classical["partial_query_k"])
    if partial < 0 or partial > partial_k:
        raise ValueError("invalid partial classical query")

    h_comp = int(hhs["affine_compositions"])
    h_verify = int(hhs["matrix_multiplications"])
    h_admit = int(hhs["lane5_admissions"])
    if min(h_comp, h_verify, h_admit) <= 0:
        raise ValueError("invalid HHS counted work")

    modulus = int(meta["modulus"])
    state_width = modulus.bit_length()
    state_space_bits = Decimal(str(math.log2(modulus)))

    h_jump_bits = int(hhs["jump_descriptor_bits"])
    c_jump_bits = int(classical["jump_descriptor_bits"])
    h_descriptor_bits = hq * state_width + h_jump_bits
    c_started = cq + (1 if partial > 0 else 0)
    c_descriptor_bits = c_started * state_width + c_jump_bits + (partial_k.bit_length() if partial > 0 else 0)

    h_qps = _rate(hq, he)
    c_qps = _rate(cq, ce)
    h_endpoint_info_rate = state_space_bits * h_qps
    c_endpoint_info_rate = state_space_bits * c_qps
    h_path_rate = _rate(h_trans, he)
    c_step_rate = _rate(c_steps, ce)
    h_descriptor_rate = _rate(h_descriptor_bits, he)
    c_descriptor_rate = _rate(c_descriptor_bits, ce)
    q_ratio = h_qps / c_qps
    endpoint_info_ratio = h_endpoint_info_rate / c_endpoint_info_rate
    path_to_step_rate_ratio = h_path_rate / c_step_rate
    total_hhs_counted = h_comp + h_verify + h_admit

    return {
        "schema": SCHEMA,
        "result": "PASS",
        "claim_scope": {
            "workload": "same deterministic non-terminating affine-query stream",
            "window_seconds_each": str(Decimal(window) / Decimal(1_000_000_000)),
            "epochs": "sequential, same runner, one active benchmark thread per epoch",
            "information_term": "state-space and exact descriptor bits-equivalent; not an entropy claim",
            "universal_classical_supremacy_claim": False,
        },
        "runner": {
            "cpu_model": _cpu_model(),
            "logical_cpu_count": os.cpu_count(),
            "memory_kib": _memory_kib(),
            "platform": platform.platform(),
            "kernel_release": platform.release(),
            "runner_os_env": os.getenv("RUNNER_OS"),
            "runner_arch_env": os.getenv("RUNNER_ARCH"),
            "image_os_env": os.getenv("ImageOS"),
            "image_version_env": os.getenv("ImageVersion"),
            "cc_version": _cc_version(),
        },
        "workload": {
            "stream_seed": int(meta["stream_seed"]),
            "modulus": modulus,
            "endpoint_state_width_bits": state_width,
            "endpoint_state_space_bits_equivalent": str(state_space_bits),
            "k_min": int(meta["k_min"]),
            "k_span": int(meta["k_span"]),
        },
        "hhs": {
            "elapsed_ns": he,
            "completed_queries": hq,
            "queries_per_second": str(h_qps),
            "represented_transitions_resolved": h_trans,
            "represented_transitions_per_second": str(h_path_rate),
            "endpoint_state_information_bits_equivalent_per_second": str(h_endpoint_info_rate),
            "exact_descriptor_bits_processed": h_descriptor_bits,
            "exact_descriptor_bits_per_second": str(h_descriptor_rate),
            "affine_compositions": h_comp,
            "matrix_verifier_multiplications": h_verify,
            "lane5_admissions": h_admit,
            "counted_hhs_control_operations": total_hhs_counted,
            "represented_transitions_per_counted_hhs_control_operation": str(Decimal(h_trans) / Decimal(total_hhs_counted)),
            "materialized_intermediate_states": 0,
        },
        "classical": {
            "elapsed_ns": ce,
            "completed_queries": cq,
            "queries_per_second": str(c_qps),
            "represented_completed_transitions": c_complete_trans,
            "executed_transition_steps": c_steps,
            "executed_transition_steps_per_second": str(c_step_rate),
            "partial_query_steps": partial,
            "partial_query_k": partial_k,
            "endpoint_state_information_bits_equivalent_per_second": str(c_endpoint_info_rate),
            "exact_descriptor_bits_started": c_descriptor_bits,
            "exact_descriptor_bits_per_second": str(c_descriptor_rate),
        },
        "same_stream_exactness": {
            "verified_prefix_queries": int(verification["classical_prefix_queries"]),
            "classical_prefix_digest": int(verification["classical_prefix_digest"]),
            "hhs_replay_digest": int(verification["hhs_replay_digest"]),
            "hhs_replay_compositions": int(verification["hhs_replay_compositions"]),
            "exact": True,
        },
        "ratios": {
            "completed_query_rate_hhs_over_classical": str(q_ratio),
            "endpoint_information_rate_hhs_over_classical": str(endpoint_info_ratio),
            "represented_path_resolution_rate_hhs_over_classical_executed_step_rate": str(path_to_step_rate_ratio),
            "descriptor_bit_rate_hhs_over_classical": str(h_descriptor_rate / c_descriptor_rate),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("stream_ndjson", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    meta, hhs, classical, verification = load_records(args.stream_ndjson)
    evidence = analyze(meta, hhs, classical, verification)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_120S_INFINITE_STREAM_THROUGHPUT_V1_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
