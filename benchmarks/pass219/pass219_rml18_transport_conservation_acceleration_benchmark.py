#!/usr/bin/env python3
"""Pass 219 RML18 frozen-RML17 certificate acceleration benchmark.

Measures the dominant RML17 full address-manifold validation against the
RML18 exact prevalidated certificate reuse path. Timing is observational only.
The benchmark independently requires semantic equality and exact 1.001
admission before reporting a performance result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from hhs_runtime.pass219 import discrete_transport_conservation as rml17
from hhs_runtime.pass219.rml18_transport_conservation_acceleration import (
    FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256,
    accelerated_address_manifold_certificate,
    exact_invariant_1001,
)

PASS = 219
ITERATION = "RML18_TRANSPORT_CONSERVATION_ACCELERATION_BENCHMARK"
SCHEMA = "HHS_PASS219_RML18_TRANSPORT_CONSERVATION_ACCELERATION_BENCHMARK_V1"


def _time(callable_):
    begin = time.perf_counter_ns()
    value = callable_()
    return value, time.perf_counter_ns() - begin


def _median(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--certificate-samples", type=int, default=101)
    args = parser.parse_args()
    if args.certificate_samples < 11 or args.certificate_samples % 2 == 0:
        raise SystemExit("RML18_CERTIFICATE_SAMPLES_MUST_BE_ODD_AND_AT_LEAST_11")

    exhaustive, exhaustive_ns = _time(rml17.audit_transport_address_manifold)
    if (
        exhaustive.get("result") != "PASS"
        or exhaustive.get("visited_address_count") != 1_492_992
        or exhaustive.get("audit_sha256") != FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256
    ):
        raise AssertionError("RML18_BENCHMARK_FROZEN_RML17_BASELINE_MISMATCH")

    certificate_times: list[int] = []
    candidate = None
    for _ in range(args.certificate_samples):
        candidate, elapsed = _time(accelerated_address_manifold_certificate)
        if candidate.get("status") != "ADMITTED" or not exact_invariant_1001(candidate.get("invariant")):
            raise AssertionError("RML18_BENCHMARK_CERTIFICATE_NOT_EXACT_1_001")
        certificate_times.append(elapsed)

    assert candidate is not None
    semantic_equal = (
        exhaustive.get("all_addresses_zero_discrete_divergence") is True
        and exhaustive.get("all_address_edges_reciprocal") is True
        and exhaustive.get("all_address_edge_fluxes_balanced") is True
        and exhaustive.get("all_addresses_encode_decode_bijective") is True
        and candidate.get("zero_discrete_divergence") is True
        and candidate.get("reciprocal_edge_balance") is True
        and candidate.get("admission_preservation") is True
        and candidate.get("zero_canonical_diffusion") is True
        and candidate.get("composed_reverse_closure") is True
        and candidate.get("structural_information_loss_zero") is True
        and candidate.get("frozen_rml17_exhaustive_audit_sha256") == exhaustive.get("audit_sha256")
    )
    if not semantic_equal:
        raise AssertionError("RML18_BENCHMARK_ACCELERATED_SEMANTICS_MISMATCH")

    certificate_median_ns = _median(certificate_times)
    if certificate_median_ns <= 0:
        raise AssertionError("RML18_BENCHMARK_NONPOSITIVE_CERTIFICATE_TIME")
    if certificate_median_ns >= exhaustive_ns:
        raise AssertionError("RML18_BENCHMARK_ACCELERATION_NOT_FASTER")

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "frozen_rml17_audit_sha256": exhaustive["audit_sha256"],
        "address_count": exhaustive["visited_address_count"],
        "exhaustive_rml17_ns": exhaustive_ns,
        "accelerated_certificate_samples": args.certificate_samples,
        "accelerated_certificate_median_ns": certificate_median_ns,
        "speedup_floor_x1000": exhaustive_ns * 1000 // certificate_median_ns,
        "speedup_floor_integer": exhaustive_ns // certificate_median_ns,
        "semantic_equality": True,
        "exact_1001_invariant": True,
        "null_undefined_on_mismatch": True,
        "exhaustive_runtime_scan_in_accelerated_path": False,
        "timing_is_canonical": False,
        "latency_participates_in_viscosity_definition": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "result": "PASS",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
