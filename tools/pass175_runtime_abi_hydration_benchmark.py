#!/usr/bin/env python3
"""Benchmark the Pass 175 invariant kernel ABI and execute first terminal hydration.

Timing values are host-dependent observations only. Correctness is established by
exact round trips, identity preservation, singleton VM81 admission, Hash216 store
sealing, firmware boot, and deterministic replay checks.
"""
from __future__ import annotations

import argparse
import ctypes
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import tempfile
import time
from typing import Any, Callable

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass175 import (
    EncryptedHash216Store,
    HydratedMicrocodeStore,
    Pass175Runtime,
    SUPPORTED_CORPUS,
    TerminalInstructionRequest,
    TerminalPass175Runtime,
)

ABI_VERSION = 0x00017501
VM81_CELLS = 81
STATE_COUNT = 5184
CONTROL_COUNT = 243
CONTROL_TRITS = 5
BITSET_WORDS = 2
ZERO_SHA256 = "0" * 64


class KernelBitset(ctypes.Structure):
    _fields_ = [("words", ctypes.c_uint64 * BITSET_WORDS)]


class KernelAddress(ctypes.Structure):
    _fields_ = [
        ("state", ctypes.c_uint32),
        ("cell", ctypes.c_uint16),
        ("operation", ctypes.c_uint8),
        ("phase", ctypes.c_uint8),
    ]


class CandidateInput(ctypes.Structure):
    _fields_ = [
        ("epoch", ctypes.c_uint64),
        ("sequence", ctypes.c_uint32),
        ("thread_id", ctypes.c_uint16),
        ("control", ctypes.c_uint16),
        ("state", ctypes.c_uint32),
        ("write_cell", ctypes.c_uint16),
        ("write_value", ctypes.c_int8),
        ("reserved", ctypes.c_uint8),
        ("read_set", KernelBitset),
        ("write_set", KernelBitset),
        ("instruction_identity", ctypes.c_uint64),
    ]


class Candidate(ctypes.Structure):
    _fields_ = [
        ("input", CandidateInput),
        ("projected_address", ctypes.c_uint32),
        ("phase", ctypes.c_uint8),
        ("control_trits", ctypes.c_uint8 * CONTROL_TRITS),
        ("reserved", ctypes.c_uint16),
        ("candidate_identity", ctypes.c_uint64),
    ]


class KernelState(ctypes.Structure):
    _fields_ = [
        ("cells", ctypes.c_int8 * VM81_CELLS),
        ("epoch", ctypes.c_uint64),
        ("ordered_commit_root", ctypes.c_uint64),
        ("admitted_candidates", ctypes.c_uint64),
        ("rejected_candidates", ctypes.c_uint64),
    ]


AdmitCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(Candidate),
    ctypes.c_size_t,
    ctypes.POINTER(KernelState),
    ctypes.POINTER(KernelState),
    ctypes.POINTER(ctypes.c_uint64),
)


class FakeAuthority:
    """Deterministic singleton VM81 authority for an isolated hydration benchmark."""

    def __init__(self) -> None:
        self.epoch = 0
        self.state_hash72 = hash72_digest({"schema": "P175_FIRST_HYDRATION_GENESIS"}, b"")
        self.calls: list[dict[str, Any]] = []

    def status(self) -> dict[str, Any]:
        return {
            "classification": "P175_FIRST_HYDRATION_AUTHORITY",
            "vmrc": {
                "epoch": self.epoch,
                "state_hash72": self.state_hash72,
                "kernel_authorities": 1,
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        predecessor = self.state_hash72
        self.calls.append(dict(kwargs))
        self.epoch += 1
        self.state_hash72 = hash72_digest(
            {"schema": "P175_FIRST_HYDRATION_COMMIT", "epoch": self.epoch, "kwargs": kwargs},
            predecessor.encode("ascii"),
        )
        receipt = {
            "sequence": self.epoch,
            "input_hash72": predecessor,
            "output_hash72": self.state_hash72,
        }
        receipt["receipt_sha256"] = sha256(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return {"classification": "P175_FIRST_HYDRATION_VM81_COMMIT", "receipt": receipt}

    def replay(self) -> dict[str, Any]:
        return {
            "classification": "P175_FIRST_HYDRATION_AUTHORITY_REPLAY",
            "epoch": self.epoch,
            "state_hash72": self.state_hash72,
            "deterministic_replay": True,
        }


@dataclass(frozen=True)
class TimedResult:
    elapsed_ns: int
    value: Any


def timed(fn: Callable[[], Any]) -> TimedResult:
    started = time.perf_counter_ns()
    value = fn()
    return TimedResult(time.perf_counter_ns() - started, value)


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    if not ordered:
        return 0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return int(ordered[index])


def rate(count: int, elapsed_ns: int) -> float:
    return 0.0 if elapsed_ns <= 0 else count * 1_000_000_000.0 / elapsed_ns


def load_kernel(path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(path.resolve()))
    library.hhs175_kernel_abi_version.argtypes = []
    library.hhs175_kernel_abi_version.restype = ctypes.c_uint32
    library.hhs175_kernel_scalar_lo.argtypes = [ctypes.POINTER(ctypes.c_size_t)]
    library.hhs175_kernel_scalar_lo.restype = ctypes.POINTER(ctypes.c_uint8)
    library.hhs175_kernel_scalar_hi.argtypes = [ctypes.POINTER(ctypes.c_size_t)]
    library.hhs175_kernel_scalar_hi.restype = ctypes.POINTER(ctypes.c_uint8)
    library.hhs175_kernel_address_encode.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)
    ]
    library.hhs175_kernel_address_encode.restype = ctypes.c_int
    library.hhs175_kernel_address_decode.argtypes = [
        ctypes.c_uint32, ctypes.POINTER(KernelAddress)
    ]
    library.hhs175_kernel_address_decode.restype = ctypes.c_int
    library.hhs175_kernel_projected_encode.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)
    ]
    library.hhs175_kernel_projected_encode.restype = ctypes.c_int
    library.hhs175_kernel_projected_decode.argtypes = [
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)
    ]
    library.hhs175_kernel_projected_decode.restype = ctypes.c_int
    library.hhs175_kernel_control_encode.argtypes = [
        ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint16)
    ]
    library.hhs175_kernel_control_encode.restype = ctypes.c_int
    library.hhs175_kernel_control_decode.argtypes = [
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)
    ]
    library.hhs175_kernel_control_decode.restype = ctypes.c_int
    library.hhs175_kernel_bitset_clear.argtypes = [ctypes.POINTER(KernelBitset)]
    library.hhs175_kernel_bitset_clear.restype = None
    library.hhs175_kernel_bitset_add.argtypes = [ctypes.POINTER(KernelBitset), ctypes.c_uint32]
    library.hhs175_kernel_bitset_add.restype = ctypes.c_int
    library.hhs175_kernel_prepare_candidates.argtypes = [
        ctypes.POINTER(CandidateInput), ctypes.c_size_t, ctypes.POINTER(Candidate)
    ]
    library.hhs175_kernel_prepare_candidates.restype = ctypes.c_int
    library.hhs175_kernel_sort_candidates.argtypes = [ctypes.POINTER(Candidate), ctypes.c_size_t]
    library.hhs175_kernel_sort_candidates.restype = ctypes.c_int
    library.hhs175_kernel_state_reset.argtypes = [ctypes.POINTER(KernelState)]
    library.hhs175_kernel_state_reset.restype = None
    library.hhs175_kernel_commit_candidates.argtypes = [
        ctypes.POINTER(Candidate),
        ctypes.c_size_t,
        ctypes.POINTER(KernelState),
        AdmitCallback,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint64),
    ]
    library.hhs175_kernel_commit_candidates.restype = ctypes.c_int
    return library


def native_abi_benchmark(library_path: Path, iterations: int, batch_size: int) -> dict[str, Any]:
    lib = load_kernel(library_path)
    checks: dict[str, bool] = {}

    checks["abi_version"] = lib.hhs175_kernel_abi_version() == ABI_VERSION

    length = ctypes.c_size_t()
    lo_pointer = lib.hhs175_kernel_scalar_lo(ctypes.byref(length))
    lo = bytes(lo_pointer[index] for index in range(length.value))
    hi_pointer = lib.hhs175_kernel_scalar_hi(ctypes.byref(length))
    hi = bytes(hi_pointer[index] for index in range(length.value))
    checks["scalar_lo_exact"] = lo == bytes((0, 1, 0, 1, 10, 11, 1, 0))
    checks["scalar_hi_exact"] = hi == bytes((1, 0, 11, 10, 1, 0, 0, 111))

    state_out = ctypes.c_uint32()
    address = KernelAddress()
    address_samples: list[int] = []
    for repeat in range(5):
        started = time.perf_counter_ns()
        for index in range(iterations):
            cell = index % VM81_CELLS
            operation = (index * 17) % 64
            expected_state = cell * 64 + operation
            if lib.hhs175_kernel_address_encode(cell, operation, ctypes.byref(state_out)) != 0:
                raise RuntimeError("address encode failed")
            if state_out.value != expected_state:
                raise RuntimeError("address encode mismatch")
            if lib.hhs175_kernel_address_decode(state_out.value, ctypes.byref(address)) != 0:
                raise RuntimeError("address decode failed")
            if address.cell != cell or address.operation != operation:
                raise RuntimeError("address round-trip mismatch")
        address_samples.append(time.perf_counter_ns() - started)
    checks["address_roundtrip"] = True

    projected = ctypes.c_uint32()
    decoded_state = ctypes.c_uint32()
    decoded_control = ctypes.c_uint32()
    projected_samples: list[int] = []
    for repeat in range(5):
        started = time.perf_counter_ns()
        for index in range(iterations):
            state = (index * 67) % STATE_COUNT
            control = (index * 29) % CONTROL_COUNT
            expected = state * CONTROL_COUNT + control
            if lib.hhs175_kernel_projected_encode(state, control, ctypes.byref(projected)) != 0:
                raise RuntimeError("projected encode failed")
            if projected.value != expected:
                raise RuntimeError("projected address mismatch")
            if lib.hhs175_kernel_projected_decode(
                projected.value, ctypes.byref(decoded_state), ctypes.byref(decoded_control)
            ) != 0:
                raise RuntimeError("projected decode failed")
            if decoded_state.value != state or decoded_control.value != control:
                raise RuntimeError("projected round-trip mismatch")
        projected_samples.append(time.perf_counter_ns() - started)
    checks["projected_roundtrip"] = True

    trits = (ctypes.c_uint8 * CONTROL_TRITS)()
    encoded = ctypes.c_uint16()
    for control in range(CONTROL_COUNT):
        if lib.hhs175_kernel_control_decode(control, trits) != 0:
            raise RuntimeError("control decode failed")
        if lib.hhs175_kernel_control_encode(trits, ctypes.byref(encoded)) != 0:
            raise RuntimeError("control encode failed")
        if encoded.value != control:
            raise RuntimeError("control round-trip mismatch")
    checks["control_roundtrip_all_243"] = True

    effective_batch = max(1, min(batch_size, VM81_CELLS))
    inputs = (CandidateInput * effective_batch)()
    candidates = (Candidate * effective_batch)()
    for index in range(effective_batch):
        lib.hhs175_kernel_bitset_clear(ctypes.byref(inputs[index].read_set))
        lib.hhs175_kernel_bitset_clear(ctypes.byref(inputs[index].write_set))
        if lib.hhs175_kernel_bitset_add(ctypes.byref(inputs[index].write_set), index) != 0:
            raise RuntimeError("bitset add failed")
        inputs[index].epoch = 0
        inputs[index].sequence = effective_batch - index - 1
        inputs[index].thread_id = index
        inputs[index].control = (index * 7) % CONTROL_COUNT
        inputs[index].state = (index * 64 + index) % STATE_COUNT
        inputs[index].write_cell = index
        inputs[index].write_value = 1 if index % 2 == 0 else -1
        inputs[index].instruction_identity = index + 1

    @AdmitCallback
    def admit(
        context: int,
        ordered: ctypes.POINTER(Candidate),
        count: int,
        predecessor: ctypes.POINTER(KernelState),
        successor: ctypes.POINTER(KernelState),
        receipt: ctypes.POINTER(ctypes.c_uint64),
    ) -> int:
        del context
        ctypes.memmove(successor, predecessor, ctypes.sizeof(KernelState))
        token = receipt[0]
        for item_index in range(count):
            item = ordered[item_index]
            successor.contents.cells[item.input.write_cell] = item.input.write_value
            token ^= item.candidate_identity
        receipt[0] = token ^ 0x483732
        return 0

    state = KernelState()
    receipt = ctypes.c_uint64()
    pipeline_samples: list[int] = []
    pipeline_iterations = max(1, iterations // 100)
    for repeat in range(5):
        started = time.perf_counter_ns()
        for _ in range(pipeline_iterations):
            lib.hhs175_kernel_state_reset(ctypes.byref(state))
            receipt.value = 0
            if lib.hhs175_kernel_prepare_candidates(inputs, effective_batch, candidates) != 0:
                raise RuntimeError("candidate prepare failed")
            if lib.hhs175_kernel_sort_candidates(candidates, effective_batch) != 0:
                raise RuntimeError("candidate sort failed")
            if lib.hhs175_kernel_commit_candidates(
                candidates,
                effective_batch,
                ctypes.byref(state),
                admit,
                None,
                ctypes.byref(receipt),
            ) != 0:
                raise RuntimeError("candidate commit failed")
            if state.epoch != 1 or state.admitted_candidates != effective_batch or receipt.value == 0:
                raise RuntimeError("singleton VM81 admission mismatch")
        pipeline_samples.append(time.perf_counter_ns() - started)
    checks["singleton_vm81_candidate_commit"] = True

    if not all(checks.values()):
        raise RuntimeError(f"native ABI checks failed: {checks}")

    address_median = int(statistics.median(address_samples))
    projected_median = int(statistics.median(projected_samples))
    pipeline_median = int(statistics.median(pipeline_samples))
    return {
        "library": str(library_path),
        "abi_version": f"0x{ABI_VERSION:08x}",
        "checks": checks,
        "timings_nonauthoritative": {
            "address_roundtrip": {
                "iterations_per_sample": iterations,
                "sample_count": len(address_samples),
                "median_ns": address_median,
                "p95_ns": percentile(address_samples, 0.95),
                "roundtrips_per_second_median": rate(iterations, address_median),
            },
            "projected_roundtrip": {
                "iterations_per_sample": iterations,
                "sample_count": len(projected_samples),
                "median_ns": projected_median,
                "p95_ns": percentile(projected_samples, 0.95),
                "roundtrips_per_second_median": rate(iterations, projected_median),
            },
            "candidate_prepare_sort_commit": {
                "batch_size": effective_batch,
                "iterations_per_sample": pipeline_iterations,
                "sample_count": len(pipeline_samples),
                "median_ns": pipeline_median,
                "p95_ns": percentile(pipeline_samples, 0.95),
                "candidates_per_second_median": rate(
                    effective_batch * pipeline_iterations, pipeline_median
                ),
            },
        },
    }


def hydration_benchmark(repository_root: Path) -> dict[str, Any]:
    authority = FakeAuthority()
    with tempfile.TemporaryDirectory(prefix="hhs-p175-hydration-") as temporary:
        root = Path(temporary)
        init = timed(
            lambda: Pass175Runtime(
                authority=authority,
                microcode_store=HydratedMicrocodeStore(root / "base_microcode.jsonl"),
            )
        )
        secure_store = EncryptedHash216Store(
            root / "secure_microcode.sqlite3",
            key_path=root / "secure_microcode.key",
        )
        terminal = TerminalPass175Runtime(
            base_runtime=init.value,
            secure_store=secure_store,
            repository_root=repository_root,
        )

        hydration = timed(lambda: terminal.cold_hydrate_terminal(seal=True))
        hydration_payload = hydration.value
        if hydration_payload["supported_instruction_forms"] != len(SUPPORTED_CORPUS):
            raise RuntimeError("supported hydration corpus count mismatch")
        if hydration_payload["secure_store"]["sealed"] is not True:
            raise RuntimeError("Hash216 hydration store was not sealed")

        boot = timed(terminal.boot_firmware)
        boot_payload = boot.value
        if boot_payload["ready"] is not True or len(boot_payload["stages"]) != 18:
            raise RuntimeError("canonical firmware boot did not close")

        requests = [
            TerminalInstructionRequest(b"\x0f\xa2", sequence=0, thread_id=0, explicit_delta=((1, -1),)),
            TerminalInstructionRequest(b"\x31\xc0", sequence=1, thread_id=1, explicit_delta=((2, 1),)),
            TerminalInstructionRequest(b"\x90", sequence=2, thread_id=2, explicit_delta=((3, 1),)),
        ]
        execution = timed(lambda: terminal.execute_batch(requests, max_workers=8))
        execution_payload = execution.value
        if execution_payload["parallel_state_authority"] is not False:
            raise RuntimeError("parallel state authority was incorrectly enabled")
        if execution_payload["singleton_vm81_commit_authority"] is not True:
            raise RuntimeError("singleton VM81 commit authority missing")
        if execution_payload["hash72_commit_streams"] != 1:
            raise RuntimeError("Hash72 commit stream is not singular")

        replay = timed(terminal.replay)
        replay_payload = replay.value
        if replay_payload["deterministic_replay"] is not True:
            raise RuntimeError("terminal replay failed")

        status = terminal.status()
        secure_verification = secure_store.verify()
        secure_root = secure_store.root_sha256
        secure_store.close()

    expected_authority_calls = 20  # hydration seal + 18 firmware stages + one candidate wave
    checks = {
        "permanent_instruction_count_5184": status["permanent_instruction_count"] == STATE_COUNT,
        "permanent_identity_count_5184": status["permanent_identity_count"] == STATE_COUNT,
        "controls_per_instruction_243": status["controls_per_instruction"] == CONTROL_COUNT,
        "projected_address_count_1259712": status["projected_address_count"] == STATE_COUNT * CONTROL_COUNT,
        "supported_corpus_hydrated": hydration_payload["supported_instruction_forms"] == len(SUPPORTED_CORPUS),
        "hash216_store_sealed": hydration_payload["secure_store"]["sealed"] is True,
        "hash216_positional_indexes": secure_verification["positional_index_count"] >= 216,
        "firmware_ready": boot_payload["ready"] is True,
        "firmware_stage_count_18": len(boot_payload["stages"]) == 18,
        "singleton_vm81_authority": execution_payload["singleton_vm81_commit_authority"] is True,
        "single_hash72_commit_stream": execution_payload["hash72_commit_streams"] == 1,
        "deterministic_replay": replay_payload["deterministic_replay"] is True,
        "authority_call_count": len(authority.calls) == expected_authority_calls,
    }
    if not all(checks.values()):
        raise RuntimeError(f"first hydration checks failed: {checks}")

    return {
        "checks": checks,
        "authority": {
            "calls": len(authority.calls),
            "epoch": authority.epoch,
            "state_hash72": authority.state_hash72,
            "kernel_authorities": 1,
        },
        "hydration": {
            "supported_instruction_forms": hydration_payload["supported_instruction_forms"],
            "secure_store_root_sha256": secure_root,
            "sealed": hydration_payload["secure_store"]["sealed"],
            "classification": hydration_payload["classification"],
        },
        "firmware": {
            "ready": boot_payload["ready"],
            "stage_count": len(boot_payload["stages"]),
            "classification": boot_payload["classification"],
        },
        "execution": {
            "candidate_count": execution_payload["candidate_count"],
            "wave_count": execution_payload["wave_count"],
            "parallel_candidates": execution_payload["parallel_candidates"],
            "parallel_state_authority": execution_payload["parallel_state_authority"],
            "singleton_vm81_commit_authority": execution_payload["singleton_vm81_commit_authority"],
            "hash72_commit_streams": execution_payload["hash72_commit_streams"],
        },
        "replay": {
            "deterministic_replay": replay_payload["deterministic_replay"],
            "commit_chain_root_sha256": replay_payload["commit_chain_root_sha256"],
        },
        "timings_nonauthoritative": {
            "runtime_initialization_ns": init.elapsed_ns,
            "cold_hydration_and_seal_ns": hydration.elapsed_ns,
            "firmware_boot_ns": boot.elapsed_ns,
            "three_candidate_execution_ns": execution.elapsed_ns,
            "replay_ns": replay.elapsed_ns,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--abi-library", required=True, type=Path)
    parser.add_argument("--repository-root", default=Path.cwd(), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=50_000)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    if args.iterations < 100:
        parser.error("--iterations must be at least 100")
    if not args.abi_library.is_file():
        parser.error(f"ABI library not found: {args.abi_library}")

    started = time.time_ns()
    native = native_abi_benchmark(args.abi_library, args.iterations, args.batch_size)
    hydration = hydration_benchmark(args.repository_root.resolve())
    report = {
        "schema": "HHS_PASS_175_RUNTIME_ABI_FIRST_HYDRATION_BENCHMARK_V1",
        "classification": "HHS_PASS_175_RUNTIME_KERNEL_ABI_AND_FIRST_HYDRATION_VERIFIED",
        "contract": "HHS-P175-H216-VM5184-G243-VIP-PCW-SVA-H72-X64IE",
        "repository": "danonbrez/Holofractal_Harmonicode",
        "baseline_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNSPECIFIED"),
        "generated_unix_ns": time.time_ns(),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "processor": platform.processor(),
        },
        "timing_authority": "NONAUTHORITATIVE_HOST_OBSERVATION",
        "native_abi": native,
        "first_hydration": hydration,
        "total_elapsed_ns_nonauthoritative": time.time_ns() - started,
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    report["report_sha256"] = sha256(canonical).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": report["classification"],
        "report_sha256": report["report_sha256"],
        "output": str(args.output),
        "native_checks": native["checks"],
        "hydration_checks": hydration["checks"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
