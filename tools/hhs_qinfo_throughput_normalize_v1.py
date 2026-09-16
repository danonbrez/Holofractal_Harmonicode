#!/usr/bin/env python3
"""Normalize Lane 5 benchmark evidence into quantum-information-equivalent metrics.

This tool is observational. It does not grant canonical VM81/Hash72/Hash216 authority.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
from typing import Any

getcontext().prec = 80

QUDIT_DIMENSION = 72
QUDIT_COUNT = 72
VM5184_BLOCK_COUNT = 36
ROUTE_ADDRESS_SLOTS = 4
LOGICAL_DIMENSION = QUDIT_DIMENSION ** QUDIT_COUNT
BINARY_EMBEDDING_BITS = LOGICAL_DIMENSION.bit_length()
PROVIDER_DECLARED_VCPU = 4
PROVIDER_DECLARED_RAM_GB = 16
PROVIDER_DECLARED_STORAGE_GB = 14
RUNNER_LABEL = "ubuntu-24.04"
RUNNER_ARCH = "x64"


def dlog2_integer(value: int) -> Decimal:
    if value <= 0:
        raise ValueError("log2 domain requires a positive integer")
    return Decimal(value).ln() / Decimal(2).ln()


QUBIT_EQUIVALENT_ADDRESS_BITS = dlog2_integer(LOGICAL_DIMENSION)


def _read_first_matching_line(path: Path, prefix: str) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith(prefix):
                return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


def _first_line(command: list[str]) -> str | None:
    try:
        out = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError):
        return None
    lines = out.splitlines()
    return lines[0] if lines else None


def observed_hardware() -> dict[str, Any]:
    mem_kib = None
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                mem_kib = int(line.split()[1])
                break
    except OSError:
        pass

    disk = shutil.disk_usage(Path.cwd())
    cpu_model = _read_first_matching_line(Path("/proc/cpuinfo"), "model name")
    if cpu_model is None:
        cpu_model = _read_first_matching_line(Path("/proc/cpuinfo"), "Hardware")

    return {
        "provider": "GitHub Actions",
        "runner_label": RUNNER_LABEL,
        "provider_declared_architecture": RUNNER_ARCH,
        "provider_declared_vcpu": PROVIDER_DECLARED_VCPU,
        "provider_declared_ram_gb": PROVIDER_DECLARED_RAM_GB,
        "provider_declared_storage_gb": PROVIDER_DECLARED_STORAGE_GB,
        "observed_machine": platform.machine(),
        "observed_logical_cpu_count": os.cpu_count(),
        "observed_cpu_model": cpu_model,
        "observed_memory_kib": mem_kib,
        "observed_filesystem_total_bytes": disk.total,
        "observed_filesystem_free_bytes": disk.free,
        "kernel_release": platform.release(),
        "platform": platform.platform(),
        "runner_os_env": os.environ.get("RUNNER_OS"),
        "runner_arch_env": os.environ.get("RUNNER_ARCH"),
        "image_os_env": os.environ.get("ImageOS"),
        "image_version_env": os.environ.get("ImageVersion"),
        "cc_version": _first_line(["cc", "--version"]),
        "active_benchmark_threads": 1,
    }


def normalize(native: dict[str, Any], hardware: dict[str, Any] | None = None) -> dict[str, Any]:
    if native.get("result") != "PASS":
        raise ValueError("native benchmark result must be PASS")
    candidates = int(native["scale_candidates"])
    elapsed_ns = int(native["elapsed_ns"])
    rate_floor = int(native["candidates_per_second_floor"])
    if candidates <= 0 or elapsed_ns <= 0 or rate_floor <= 0:
        raise ValueError("candidate count, elapsed_ns, and rate floor must be positive")
    if int(native["full_manifold_address_bytes"]) != 56:
        raise ValueError("unexpected full-manifold address width")
    if int(native["materialized_intermediate_states"]) != 0:
        raise ValueError("normalization requires zero materialized intermediate states")

    mean_candidate_interval_ns = Decimal(elapsed_ns) / Decimal(candidates)
    basis_rate = QUBIT_EQUIVALENT_ADDRESS_BITS * Decimal(rate_floor)
    route_capacity_bits = QUBIT_EQUIVALENT_ADDRESS_BITS * Decimal(ROUTE_ADDRESS_SLOTS)
    route_capacity_rate = route_capacity_bits * Decimal(rate_floor)
    qudit_coordinate_rate = QUDIT_COUNT * rate_floor
    vm5184_block_rate = VM5184_BLOCK_COUNT * rate_floor
    provider_vcpu = Decimal(PROVIDER_DECLARED_VCPU)

    result: dict[str, Any] = {
        "schema": "HHS_QINFO_THROUGHPUT_NORMALIZATION_V1",
        "result": "PASS",
        "authority": {
            "observational_only": True,
            "physical_quantum_hardware_claim": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        },
        "logical_state_space": {
            "hilbert_space_equivalent_dimension": str(LOGICAL_DIMENSION),
            "qudit_dimension": QUDIT_DIMENSION,
            "qudit_count": QUDIT_COUNT,
            "qubit_equivalent_address_bits": str(QUBIT_EQUIVALENT_ADDRESS_BITS),
            "binary_embedding_bits": BINARY_EMBEDDING_BITS,
            "native_address_bytes": 56,
            "vm5184_block_count": VM5184_BLOCK_COUNT,
            "route_full_manifold_address_slots": ROUTE_ADDRESS_SLOTS,
        },
        "physical_runner_observation": {
            "candidate_count": candidates,
            "elapsed_ns": elapsed_ns,
            "candidate_rate_floor_per_second": rate_floor,
            "mean_candidate_interval_ns": str(mean_candidate_interval_ns),
        },
        "complexity_density": {
            "basis_coordinate_information_rate_bits_equivalent_per_second": str(basis_rate),
            "route_address_capacity_bits_equivalent_per_candidate": str(route_capacity_bits),
            "route_address_capacity_rate_bits_equivalent_per_second": str(route_capacity_rate),
            "qudit_coordinate_symbols_per_second": qudit_coordinate_rate,
            "vm5184_block_coordinates_per_second": vm5184_block_rate,
            "candidate_rate_per_provisioned_vcpu": str(Decimal(rate_floor) / provider_vcpu),
            "basis_information_rate_per_provisioned_vcpu": str(basis_rate / provider_vcpu),
            "route_capacity_rate_per_provisioned_vcpu": str(route_capacity_rate / provider_vcpu),
        },
        "terminology": {
            "deterministic_shot": "one complete candidate-route validation/reduction observation",
            "replay_fidelity": "exact typed deterministic equality; not physical quantum-state fidelity",
            "coherence_equivalent": "named deterministic replay interval only; not physical coherence time",
            "quantum_volume": "reserved unless a compatible quantum-volume protocol is executed",
            "circuit_depth": "reserved until sequential primitive stages are instrumented",
            "gate_rate": "reserved until exact primitive operations are counted",
        },
    }
    result["hardware_normalization"] = hardware if hardware is not None else observed_hardware()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("native_json", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()

    native = json.loads(args.native_json.read_text(encoding="utf-8"))
    result = normalize(native)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("HHS_QINFO_THROUGHPUT_NORMALIZATION_V1_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
