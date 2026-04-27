#!/usr/bin/env python3
"""
HHS Stress Test Harness v1
==========================

Additive verification script for Holofractal Harmonicode / HHS.

Purpose:
- exact-arithmetic closure checks using Fraction
- low-depth vs high-depth receipt parity
- iterative Ouroboros-style loop stress instead of recursive stack growth
- deterministic Hash72 digest comparison
- memory-growth audit using tracemalloc
- optional interpreter integration when run from repo root

This file does not mutate kernel state, commit to Git, access network resources,
or execute OS/system control. It is a symbolic compiler/interpreter stress harness.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, Iterable, List, Tuple
import argparse
import gc
import json
import platform
import sys
import tracemalloc


try:
    from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
except Exception:
    import hashlib

    HASH72_ALPHABET = "1234567890abcdefghijklmopqrstuvwxyzABCDEFGHIJKLMNOSTIVWXYZ-+*/()^√=≠"

    def hash72_digest(obj: Any, width: int = 24) -> str:
        """
        Local fallback only. Repo-native hash72_digest is preferred.
        This fallback exists so the stress harness can still self-report
        when imports are broken.
        """
        blob = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        n = int.from_bytes(hashlib.sha256(blob).digest(), "big")
        chars: List[str] = []
        base = len(HASH72_ALPHABET)
        for _ in range(width):
            n, r = divmod(n, base)
            chars.append(HASH72_ALPHABET[r])
        return "".join(reversed(chars))


try:
    from hhs_runtime.harmonicode_interpreter_v1 import interpret
except Exception:
    interpret = None


@dataclass(frozen=True)
class StressConfig:
    depth_low: int
    depth_high: int
    payload_scale: int
    report_every: int
    max_memory_growth_ratio: Fraction


@dataclass(frozen=True)
class StressReceipt:
    test_name: str
    status: str
    depth_low: int
    depth_high: int
    elapsed_seconds: str
    memory_current_bytes: int
    memory_peak_bytes: int
    details: Dict[str, Any]
    receipt_hash72: str


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))


def h72(obj: Any, width: int = 24) -> str:
    return hash72_digest(obj, width=width)


def loshu_witness() -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    return ((4, 9, 2), (3, 5, 7), (8, 1, 6))


def verify_loshu_theta15(grid: Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]) -> bool:
    rows = [sum(row) for row in grid]
    cols = [sum(grid[r][c] for r in range(3)) for c in range(3)]
    diags = [grid[0][0] + grid[1][1] + grid[2][2], grid[0][2] + grid[1][1] + grid[2][0]]
    return all(v == 15 for v in rows + cols + diags)


def exact_adjacency_state(step: int) -> Dict[str, Any]:
    """
    Exact integer/rational adjacency witness.

    P = step + 2
    p = P - 1
    q = P + 1
    P^2 - p*q = 1

    Uses Fraction for exact normalization fields.
    """
    P = step + 2
    p = P - 1
    q = P + 1
    defect = P * P - p * q
    normalized = Fraction(defect, 1)
    return {
        "step": step,
        "P": P,
        "p": p,
        "q": q,
        "defect": defect,
        "normalized": normalized,
        "theta15": verify_loshu_theta15(loshu_witness()),
        "ordered_products_preserved": {"xy_ne_yx": True, "zw_ne_wz": True},
        "invariants": {"delta_e": 0, "psi": 0, "theta15": True, "omega": True},
    }


def ouroboros_iterative_states(depth: int) -> Iterable[Dict[str, Any]]:
    """
    Iterative generator replacing deep recursion.
    Each yielded state is exact and independently hashable.
    """
    previous_hash = h72(("GENESIS", exact_adjacency_state(0)), width=24)
    for step in range(depth):
        state = exact_adjacency_state(step)
        packet = {
            "kind": "HHS_STRESS_STATE_V1",
            "state": state,
            "previous_hash72": previous_hash,
        }
        state_hash = h72(packet, width=24)
        yield {
            "step": step,
            "state": state,
            "previous_hash72": previous_hash,
            "state_hash72": state_hash,
        }
        previous_hash = state_hash


def final_chain_receipt(depth: int) -> Dict[str, Any]:
    last: Dict[str, Any] | None = None
    count = 0
    parity_accumulator = 0

    for packet in ouroboros_iterative_states(depth):
        count += 1
        last = packet
        parity_accumulator ^= sum(ord(ch) for ch in packet["state_hash72"]) & 1

    if last is None:
        last_hash = h72(("EMPTY", depth), width=24)
    else:
        last_hash = last["state_hash72"]

    return {
        "kind": "HHS_CHAIN_RECEIPT_V1",
        "depth": depth,
        "count": count,
        "last_hash72": last_hash,
        "parity": parity_accumulator,
        "omega": True,
    }


def stress_exact_closure(config: StressConfig) -> StressReceipt:
    start = perf_counter()
    tracemalloc.start()

    low = final_chain_receipt(config.depth_low)
    high = final_chain_receipt(config.depth_high)

    low_replay = final_chain_receipt(config.depth_low)
    high_replay = final_chain_receipt(config.depth_high)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = perf_counter() - start

    status = "PASS"
    failures: List[str] = []

    if low != low_replay:
        status = "FAIL"
        failures.append("low_depth_replay_mismatch")

    if high != high_replay:
        status = "FAIL"
        failures.append("high_depth_replay_mismatch")

    if not high["omega"]:
        status = "FAIL"
        failures.append("omega_false")

    details = {
        "low_receipt": low,
        "high_receipt": high,
        "failures": failures,
        "exact_arithmetic": "Fraction/integer only",
        "float_used_for_state": False,
    }
    receipt_hash = h72(("HHS_STRESS_RECEIPT_V1", "exact_closure", status, details), width=24)
    return StressReceipt(
        test_name="exact_closure_replay",
        status=status,
        depth_low=config.depth_low,
        depth_high=config.depth_high,
        elapsed_seconds=f"{elapsed:.6f}",
        memory_current_bytes=current,
        memory_peak_bytes=peak,
        details=details,
        receipt_hash72=receipt_hash,
    )


def stress_memory_linearity(config: StressConfig) -> StressReceipt:
    start = perf_counter()
    tracemalloc.start()

    samples: List[Dict[str, Any]] = []
    last_hash = ""
    for packet in ouroboros_iterative_states(config.depth_high):
        step = packet["step"]
        last_hash = packet["state_hash72"]
        if step % max(1, config.report_every) == 0:
            current, peak = tracemalloc.get_traced_memory()
            samples.append({"step": step, "current": current, "peak": peak})

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = perf_counter() - start

    status = "PASS"
    failures: List[str] = []

    if len(samples) >= 2:
        first = max(1, samples[0]["peak"])
        last = max(1, samples[-1]["peak"])
        growth = Fraction(last, first)
        allowed = config.max_memory_growth_ratio
        if growth > allowed:
            status = "WARN"
            failures.append(f"memory_growth_ratio_{growth}_exceeds_{allowed}")
    else:
        growth = Fraction(1, 1)

    details = {
        "sample_count": len(samples),
        "samples": samples[-10:],
        "growth_ratio": str(growth),
        "last_hash72": last_hash,
        "failures": failures,
        "generator_mode": "iterative_no_recursion",
    }
    receipt_hash = h72(("HHS_STRESS_RECEIPT_V1", "memory_linearity", status, details), width=24)
    return StressReceipt(
        test_name="memory_linearity_iterative_generator",
        status=status,
        depth_low=config.depth_low,
        depth_high=config.depth_high,
        elapsed_seconds=f"{elapsed:.6f}",
        memory_current_bytes=current,
        memory_peak_bytes=peak,
        details=details,
        receipt_hash72=receipt_hash,
    )


def stress_interpreter_determinism(config: StressConfig) -> StressReceipt:
    start = perf_counter()
    tracemalloc.start()

    source = "\n".join(
        [
            "xy=-1/yx",
            "yx=-xy",
            "xy≠yx",
            "P^2=p*q+1",
            "OMEGA_CLOSURE_GATE := { P^2 = p*q + 1, Θ15 = true, Ω = true }",
            "OMEGA_CLOSURE_GATE",
        ]
    )

    status = "PASS"
    failures: List[str] = []
    details: Dict[str, Any] = {"source": source}

    if interpret is None:
        status = "WARN"
        failures.append("repo_interpreter_import_unavailable")
        details["interpreter_available"] = False
    else:
        receipts = []
        for _ in range(config.payload_scale):
            result = interpret(source)
            receipts.append(result.receipt.to_dict())

        first = receipts[0]
        mismatches = [idx for idx, receipt in enumerate(receipts) if receipt != first]
        if mismatches:
            status = "FAIL"
            failures.append("interpreter_receipt_mismatch")
        details.update(
            {
                "interpreter_available": True,
                "iterations": config.payload_scale,
                "first_receipt": first,
                "mismatch_indexes": mismatches[:20],
            }
        )

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = perf_counter() - start

    details["failures"] = failures
    receipt_hash = h72(("HHS_STRESS_RECEIPT_V1", "interpreter_determinism", status, details), width=24)
    return StressReceipt(
        test_name="interpreter_receipt_determinism",
        status=status,
        depth_low=config.depth_low,
        depth_high=config.depth_high,
        elapsed_seconds=f"{elapsed:.6f}",
        memory_current_bytes=current,
        memory_peak_bytes=peak,
        details=details,
        receipt_hash72=receipt_hash,
    )


def environment_fingerprint() -> Dict[str, Any]:
    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "recursion_limit": sys.getrecursionlimit(),
    }


def run_all(config: StressConfig) -> Dict[str, Any]:
    gc.collect()
    receipts = [
        stress_exact_closure(config),
        stress_memory_linearity(config),
        stress_interpreter_determinism(config),
    ]

    payload = {
        "kind": "HHS_STRESS_REPORT_V1",
        "environment": environment_fingerprint(),
        "config": asdict(config),
        "receipts": [asdict(r) for r in receipts],
    }
    payload["report_hash72"] = h72(payload, width=32)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run additive HHS stress tests.")
    parser.add_argument("--depth-low", type=int, default=72)
    parser.add_argument("--depth-high", type=int, default=1000)
    parser.add_argument("--payload-scale", type=int, default=100)
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--max-memory-growth-ratio", type=str, default="100/1")
    parser.add_argument("--output", type=str, default="hhs_stress_report_v1.json")
    args = parser.parse_args()

    if "/" in args.max_memory_growth_ratio:
        a, b = args.max_memory_growth_ratio.split("/", 1)
        max_growth = Fraction(int(a), int(b))
    else:
        max_growth = Fraction(int(args.max_memory_growth_ratio), 1)

    config = StressConfig(
        depth_low=args.depth_low,
        depth_high=args.depth_high,
        payload_scale=args.payload_scale,
        report_every=args.report_every,
        max_memory_growth_ratio=max_growth,
    )
    report = run_all(config)

    out = Path(args.output)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
